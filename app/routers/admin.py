import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from tools.pdf_import.pipeline import run_pdf_import_pipeline
from tools.pdf_import.review import (
    list_staging_drafts,
    get_draft,
    update_draft,
    publish_draft_detailed,
    reject_draft
)

router = APIRouter()


@router.post("/api/admin/upload-pdf")
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


@router.get("/api/admin/drafts")
def get_staging_drafts():
    """Возвращает список всех черновиков в staging."""
    return list_staging_drafts()


@router.get("/api/admin/drafts/{slug}")
def get_single_staging_draft(slug: str):
    """Возвращает полную структуру черновика по slug."""
    draft = get_draft(slug)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Черновик не найден")
    return draft


@router.put("/api/admin/drafts/{slug}")
def update_staging_draft(slug: str, payload: Dict[str, Any]):
    """Обновляет черновик (например, выбор правильного ответа или редактирование текста)."""
    success, errors = update_draft(slug, payload)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return {"success": True, "slug": slug}


@router.post("/api/admin/drafts/{slug}/publish")
def publish_staging_draft(slug: str):
    """Публикует проверенный черновик из staging в боевую базу данных тренажёра."""
    success, errors = publish_draft_detailed(slug)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": errors})
    return {"success": True, "message": f"Черновик {slug} успешно опубликован в каталог!"}


@router.delete("/api/admin/drafts/{slug}")
def delete_staging_draft(slug: str):
    """Удаляет черновик из staging."""
    success = reject_draft(slug)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Черновик не найден")
    return {"success": True, "message": f"Черновик {slug} удален из staging."}
