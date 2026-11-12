from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core.database import get_db
from app.schemas import ReportTaskRequest

router = APIRouter()


@router.post("/api/texts/{text_id}/report", tags=["Quality & Reports"])
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

    # Keep the message for the admin panel (response contract unchanged).
    db.add(models.DefectReport(
        text_id=text.id,
        reason=(payload.reason or "")[:200],
        details=(payload.details or "")[:2000] or None,
        user_id=(payload.user_id or "")[:100] or None,
    ))

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
