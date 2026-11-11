from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.core.database import get_db
from app.schemas import TextReadSchema, QuestionReadSchema, OptionReadSchema
from app.services.option_shuffle import present_options
from app.services.stream_service import get_attempt_epoch

router = APIRouter()


@router.get("/api/texts/{text_id}", response_model=TextReadSchema, tags=["Reading (Anti-Cheat)"])
def get_text_for_reading(
    text_id: int,
    user_id: str = Query("default-user", description="ID сессии или пользователя (для перемешивания вариантов)"),
    db: Session = Depends(get_db),
    response: Response = Response()
):
    """
    STRICT ANTI-CHEAT ENDPOINT:
    Returns ONLY the text, questions, and option texts.
    Does NOT leak answers, explanations, translations, or evidence span IDs.
    """
    # Prevent browser from caching texts to avoid stale exercises
    if isinstance(response, Response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    text = (
        db.query(models.Text)
        .options(joinedload(models.Text.questions).joinedload(models.Question.options))
        .filter(models.Text.id == text_id)
        .first()
    )
    if not text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")

    epoch = get_attempt_epoch(db, user_id, text.id)
    questions_read = []
    for q in text.questions:
        options_read = [
            OptionReadSchema(
                id=v["token"],
                option_number=v["number"],
                option_text=v["opt"].option_text
            )
            for v in present_options(user_id, text.id, epoch, q)
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
