import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.core.database import get_db
from app.schemas import SubmitPayloadSchema, TextAnalysisSchema
from app.services.scoring_service import build_text_analysis

router = APIRouter()


def require_test_mode():
    """D5: this endpoint returns correct answers without verifying an attempt, so it is
    reachable only when DOKKAI_TEST_MODE=1 (tests/tools). In production it looks absent."""
    if os.environ.get("DOKKAI_TEST_MODE") != "1":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


@router.post(
    "/api/texts/{text_id}/submit",
    response_model=TextAnalysisSchema,
    tags=["Analysis"],
    dependencies=[Depends(require_test_mode)],
)
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

    return build_text_analysis(text, payload)
