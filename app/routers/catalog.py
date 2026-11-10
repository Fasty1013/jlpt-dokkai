from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.database import get_db
from app.schemas import TextListItemSchema

router = APIRouter()


@router.get("/api/texts", response_model=List[TextListItemSchema], tags=["Catalog"])
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
