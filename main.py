import os
import sys
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, Depends, HTTPException, Query, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from database import engine, Base, get_db
import models
from schemas import (
    TextListItemSchema,
    TextReadSchema,
    QuestionReadSchema,
    OptionReadSchema,
    SubmitPayloadSchema,
    TextAnalysisSchema,
    QuestionAnalysisSchema,
    OptionAnalysisSchema,
    VocabularyItemSchema,
    StreamCompleteRequest,
    ReportTaskRequest,
)
from app.stream.service import (
    get_or_create_slots,
    complete_task,
    list_solved_texts,
    get_solved_task_details,
    get_default_profile_for_level,
)
from seed import seed_database
from dictionary import lookup_word
from tools.pdf_import.pipeline import run_pdf_import_pipeline
from tools.pdf_import.review import (
    list_staging_drafts,
    get_draft,
    update_draft,
    publish_draft_detailed,
    reject_draft
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists and seed data is present on startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    from tools.migrations.add_stream_tables import migrate
    migrate()
    yield


app = FastAPI(
    title="JLPT Dokkai Master (読解トレーナー)",
    description="Exam-flow Japanese reading comprehension training with anti-cheat and deep analysis.",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Healthcheck endpoint for Render and uptime monitoring."""
    text_count = db.query(models.Text).count()
    return {
        "status": "ok",
        "database": "connected",
        "texts_count": text_count
    }


@app.get("/api/version", tags=["Health"])
def version_info():
    """Version and build metadata endpoint for QA synchronization (no secrets)."""
    commit_sha = os.getenv("RENDER_GIT_COMMIT", "")
    if not commit_sha:
        try:
            import subprocess
            commit_sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                text=True,
                timeout=1
            ).strip()
        except Exception:
            commit_sha = "unknown"

    return {
        "version": "2.0.2",
        "commit": commit_sha,
        "env": os.getenv("ENV", os.getenv("APP_ENV", "development")),
        "database_backend": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgres") else "sqlite"
    }


@app.get("/api/texts", response_model=List[TextListItemSchema], tags=["Catalog"])
def list_texts(
    level: Optional[str] = Query(None, description="JLPT Level: N5, N4, N3, N2, N1"),
    category: Optional[str] = Query(None, description="Category: short, medium, long, info_search, article"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Text)
    if level:
        query = query.filter(models.Text.level == level.upper())
    if category:
        query = query.filter(models.Text.category == category.lower())

    texts = query.all()
    results = []
    for text in texts:
        results.append(
            TextListItemSchema(
                id=text.id,
                title=text.title,
                level=text.level,
                category=text.category,
                source_exam=text.source_exam,
                is_nhk=text.is_nhk,
                recommended_time_min=text.recommended_time_min,
                question_count=len(text.questions)
            )
        )
    return results


@app.get("/api/texts/{text_id}", response_model=TextReadSchema, tags=["Reading (Anti-Cheat)"])
def get_text_for_reading(text_id: int, db: Session = Depends(get_db)):
    """
    STRICT ANTI-CHEAT ENDPOINT:
    Returns ONLY the text, questions, and option texts.
    Does NOT leak answers, explanations, translations, or evidence span IDs.
    """
    text = (
        db.query(models.Text)
        .options(joinedload(models.Text.questions).joinedload(models.Question.options))
        .filter(models.Text.id == text_id)
        .first()
    )
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")

    questions_read = []
    for q in text.questions:
        options_read = [
            OptionReadSchema(
                id=opt.id,
                option_number=opt.option_number,
                option_text=opt.option_text
            )
            for opt in q.options
        ]
        questions_read.append(
            QuestionReadSchema(
                id=q.id,
                question_number=q.question_number,
                question_text=q.question_text,
                options=options_read
            )
        )

    return TextReadSchema(
        id=text.id,
        title=text.title,
        level=text.level,
        category=text.category,
        source_exam=text.source_exam,
        is_nhk=text.is_nhk,
        recommended_time_min=text.recommended_time_min,
        content_html=text.content_html,
        questions=questions_read
    )


@app.get("/api/dictionary/lookup", tags=["Dictionary"])
def dictionary_lookup(q: str = Query(..., min_length=1, max_length=50)):
    """
    Lookup endpoint for Yomichan-style popup dictionary.
    Returns reading, JLPT level, and Russian translation.
    """
    result = lookup_word(q)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return result


@app.post("/api/texts/{text_id}/submit", response_model=TextAnalysisSchema, tags=["Analysis"])
def submit_and_analyze(text_id: int, payload: SubmitPayloadSchema, db: Session = Depends(get_db)):
    """
    POST-SUBMIT EVALUATION ENDPOINT:
    Validates user choices against DB records and unlocks:
    - Correctness status
    - Explanations for all options (distractor breakdown & correct logic)
    - Key evidence span IDs in the text
    - Full Russian translation and vocabulary list
    """
    text = (
        db.query(models.Text)
        .options(joinedload(models.Text.questions).joinedload(models.Question.options))
        .filter(models.Text.id == text_id)
        .first()
    )
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")

    user_answers_map = {ans.question_id: ans.selected_option_id for ans in payload.answers}

    total_questions = len(text.questions)
    correct_count = 0
    questions_analysis = []

    for q in text.questions:
        selected_opt_id = user_answers_map.get(q.id)
        correct_opt = next((opt for opt in q.options if opt.is_correct), None)
        correct_opt_id = correct_opt.id if correct_opt else -1

        is_user_correct = (selected_opt_id is not None and selected_opt_id == correct_opt_id)
        if is_user_correct:
            correct_count += 1

        options_analysis = []
        for opt in q.options:
            was_selected = (selected_opt_id == opt.id)
            options_analysis.append(
                OptionAnalysisSchema(
                    id=opt.id,
                    option_number=opt.option_number,
                    option_text=opt.option_text,
                    is_correct=opt.is_correct,
                    trap_type=opt.trap_type,
                    option_explanation=opt.option_explanation,
                    was_selected=was_selected
                )
            )

        questions_analysis.append(
            QuestionAnalysisSchema(
                id=q.id,
                question_number=q.question_number,
                question_text=q.question_text,
                general_explanation=q.general_explanation,
                evidence_span_id=q.evidence_span_id,
                is_user_correct=is_user_correct,
                selected_option_id=selected_opt_id,
                correct_option_id=correct_opt_id,
                options=options_analysis
            )
        )

    score_percent = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0

    raw_vocab = text.vocabulary_json or []
    vocab_items = [
        VocabularyItemSchema(
            word=item.get("word", ""),
            furigana=item.get("furigana", ""),
            translation=item.get("translation", "")
        )
        for item in raw_vocab
    ]

    return TextAnalysisSchema(
        id=text.id,
        title=text.title,
        level=text.level,
        category=text.category,
        source_exam=text.source_exam,
        is_nhk=text.is_nhk,
        recommended_time_min=text.recommended_time_min,
        content_html=text.content_html,
        translation_ru=text.translation_ru,
        vocabulary=vocab_items,
        total_questions=total_questions,
        correct_count=correct_count,
        score_percent=score_percent,
        time_spent_sec=payload.time_spent_sec,
        questions=questions_analysis
    )


# =============================================================================
# Stream API Endpoints (Two-Column Continuous Flow)
# =============================================================================

@app.get("/api/stream/slots", tags=["Stream"])
def get_stream_slots(
    user_id: str = Query("default-user", description="ID сессии или пользователя"),
    profile_key: Optional[str] = Query(None, description="Ключ профиля сложности, например N5:short:detail:1:XS"),
    level: Optional[str] = Query("N5", description="Уровень JLPT (N5-N1), если profile_key не указан"),
    category: Optional[str] = Query("short", description="Категория (short, medium, long, info_search)"),
    db: Session = Depends(get_db)
):
    """
    Возвращает 3 активных слота заданий для выбранного профиля сложности.
    При нехватке слотов атомарно дозаполняет их новыми непройденными заданиями.
    Anti-Cheat: правильные ответы и объяснения не возвращаются.
    """
    if not profile_key:
        profile_key = get_default_profile_for_level(level or "N5", category or "short")
    slots = get_or_create_slots(db, user_id=user_id, profile_key=profile_key)
    return {
        "profile_key": profile_key,
        "user_id": user_id,
        "slots": slots
    }


@app.post("/api/stream/complete", tags=["Stream"])
def complete_stream_task(
    payload: StreamCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Атомарная фиксация решения задания с поддержкой idempotency_key.
    При успешном завершении задание переходит в «Решённые»,
    а слот немедленно заменяется новым непройденным заданием того же профиля.
    Anti-Cheat: если режим all_correct и есть ошибки, отдаются только ID ошибочных вопросов без ключа.
    """
    try:
        answers_dicts = [ans.model_dump() for ans in payload.answers]
        result = complete_task(
            db=db,
            user_id=payload.user_id,
            text_id=payload.text_id,
            answers=answers_dicts,
            idempotency_key=payload.idempotency_key,
            mode=payload.mode,
            solved_when=payload.solved_when,
            all_correct_max_attempts=payload.all_correct_max_attempts
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка фиксации задания: {str(e)}")


@app.get("/api/stream/solved", tags=["Stream"])
def get_solved_stream_tasks(
    user_id: str = Query("default-user", description="ID сессии или пользователя"),
    level: Optional[str] = Query(None, description="Фильтр по уровню: N5-N1"),
    only_perfect: Optional[bool] = Query(None, description="Только решённые на 100% без ошибок"),
    only_errors: Optional[bool] = Query(None, description="Только с ошибками"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Количество на страницу"),
    db: Session = Depends(get_db)
):
    """
    Возвращает список завершённых заданий пользователя (архив «Решённые») с пагинацией и фильтрами.
    """
    return list_solved_texts(
        db=db,
        user_id=user_id,
        level=level,
        only_perfect=only_perfect,
        only_errors=only_errors,
        page=page,
        page_size=page_size
    )


@app.get("/api/stream/solved/{text_id}", tags=["Stream"])
def get_solved_stream_task_detail(
    text_id: int,
    user_id: str = Query("default-user", description="ID сессии или пользователя"),
    db: Session = Depends(get_db)
):
    """
    Обзор завершённого задания.
    Anti-Cheat: доступ разрешён ТОЛЬКО если данное задание уже решено пользователем.
    """
    user_state = (
        db.query(models.UserTextState)
        .filter(models.UserTextState.user_id == user_id, models.UserTextState.text_id == text_id)
        .first()
    )
    if not user_state or user_state.status != "solved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anti-Cheat: Задание ещё не решено. Разбор ответов недоступен."
        )

    details = get_solved_task_details(
        db=db,
        user_id=user_id,
        text_id=text_id,
        score_percent=user_state.last_score or 0.0,
        perfect=user_state.perfect or False,
        is_retry=False
    )
    return details


@app.post("/api/stream/retry/{text_id}", tags=["Stream"])
def retry_stream_task(
    text_id: int,
    user_id: str = Query("default-user"),
    db: Session = Depends(get_db)
):
    """
    Повторное прохождение решённого задания.
    Anti-Cheat: возвращает структуру текста со скрытыми ответами для повторной тренировки.
    """
    text = (
        db.query(models.Text)
        .options(joinedload(models.Text.questions).joinedload(models.Question.options))
        .filter(models.Text.id == text_id)
        .first()
    )
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено")

    return {
        "text_id": text.id,
        "slug": text.slug,
        "title": text.title,
        "level": text.level,
        "category": text.category,
        "recommended_time_min": text.recommended_time_min,
        "content_html": text.content_html,
        "origin": text.origin,
        "is_retry": True,
        "questions": [
            {
                "id": q.id,
                "question_number": q.question_number,
                "question_text": q.question_text,
                "options": [
                    {
                        "id": opt.id,
                        "option_number": opt.option_number,
                        "option_text": opt.option_text
                    }
                    for opt in sorted(q.options, key=lambda o: o.option_number)
                ]
            }
            for q in sorted(text.questions, key=lambda x: x.question_number)
        ]
    }


@app.post("/api/texts/{text_id}/report", tags=["Quality & Reports"])
def report_task_defect(
    text_id: int,
    payload: ReportTaskRequest,
    db: Session = Depends(get_db)
):
    """
    Подача жалобы на опечатку/дефект в задании.
    Если число жалоб достигает порога (report_threshold: 3),
    задание автоматически деактивируется (is_active = False).
    """
    text = db.query(models.Text).filter(models.Text.id == text_id).first()
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено")

    text.report_count = (text.report_count or 0) + 1
    deactivated = False
    if text.report_count >= 3:
        text.is_active = False
        deactivated = True

    db.commit()

    return {
        "status": "reported",
        "text_id": text_id,
        "report_count": text.report_count,
        "is_active": text.is_active,
        "deactivated": deactivated,
        "message": "Жалоба принята. Спасибо за помощь в улучшении качества!" if not deactivated else "Жалоба принята. Задание автоматически скрыто из-за превышения порога замечаний."
    }


# =============================================================================
# PDF Import & Staging Admin Endpoints
# =============================================================================

@app.post("/api/admin/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    level: str = Form("N3"),
    category: str = Form("short"),
    title_override: Optional[str] = Form(None)
):
    """
    Загружает PDF книгу/материал, запускает процесс извлечения и сегментации,
    и сохраняет распознанные тексты в staging черновики для ревью.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешены только файлы формата PDF (.pdf)"
        )

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        result = run_pdf_import_pipeline(
            file_path=tmp_path,
            level=level,
            category=category,
            title_override=title_override
        )
        return result
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@app.get("/api/admin/drafts")
def get_staging_drafts():
    """Возвращает список всех черновиков в staging."""
    return list_staging_drafts()


@app.get("/api/admin/drafts/{slug}")
def get_single_staging_draft(slug: str):
    """Возвращает полную структуру черновика по slug."""
    draft = get_draft(slug)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Черновик не найден")
    return draft


@app.put("/api/admin/drafts/{slug}")
def update_staging_draft(slug: str, payload: Dict[str, Any]):
    """Обновляет черновик (например, выбор правильного ответа или редактирование текста)."""
    success, errors = update_draft(slug, payload)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return {"success": True, "slug": slug}


@app.post("/api/admin/drafts/{slug}/publish")
def publish_staging_draft(slug: str):
    """Публикует проверенный черновик из staging в боевую базу данных тренажёра."""
    success, errors = publish_draft_detailed(slug)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": errors})
    return {"success": True, "message": f"Черновик {slug} успешно опубликован в каталог!"}


@app.delete("/api/admin/drafts/{slug}")
def delete_staging_draft(slug: str):
    """Удаляет черновик из staging."""
    success = reject_draft(slug)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Черновик не найден")
    return {"success": True, "message": f"Черновик {slug} удален из staging."}


# =============================================================================
# Static Files & Frontend Routing
# =============================================================================

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "JLPT Dokkai API running. Frontend static/index.html not found."}
