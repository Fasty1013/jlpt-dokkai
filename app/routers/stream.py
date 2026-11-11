from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.core.database import get_db
from app.schemas import StreamCompleteRequest
from app.services.stream_service import (
    get_or_create_slots,
    complete_task,
    list_solved_texts,
    get_solved_task_details,
    get_default_profile_for_level,
    get_attempt_epoch,
    serialize_questions_for_user,
)

router = APIRouter()


@router.get("/api/stream/slots", tags=["Stream"])
def get_stream_slots(
    user_id: str = Query("default-user", description="ID сессии или пользователя"),
    profile_key: Optional[str] = Query(None, description="Ключ профиля сложности, например N5:short:detail:1:XS"),
    level: Optional[str] = Query("N5", description="Уровень JLPT (N5-N1), если profile_key не указан"),
    category: Optional[str] = Query("short", description="Категория (short, medium, long, info_search)"),
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """
    Возвращает 3 активных слота заданий для выбранного профиля сложности.
    При нехватке слотов атомарно дозаполняет их новыми непройденными заданиями.
    Anti-Cheat: правильные ответы и объяснения не возвращаются.
    """
    if isinstance(response, Response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    if not profile_key:
        profile_key = get_default_profile_for_level(level or "N5", category or "short")
    slots = get_or_create_slots(db, user_id=user_id, profile_key=profile_key)
    return {
        "profile_key": profile_key,
        "user_id": user_id,
        "slots": slots
    }


@router.post("/api/stream/complete", tags=["Stream"])
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


@router.get("/api/stream/solved", tags=["Stream"])
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


@router.get("/api/stream/solved/{text_id}", tags=["Stream"])
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


@router.post("/api/stream/retry/{text_id}", tags=["Stream"])
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
        "questions": serialize_questions_for_user(user_id, text, get_attempt_epoch(db, user_id, text.id))
    }
