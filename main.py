import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
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
)
from seed import seed_database
from dictionary import lookup_word


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists and seed data is present on startup
    Base.metadata.create_all(bind=engine)
    seed_database()
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
