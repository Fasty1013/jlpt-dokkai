"""Admin task editor: edit a task in place (title, passage, translation, questions, options,
correct answer, explanations) with a revision history and rollback.

The structure is fixed (same question and option ids), so in-progress attempts, opaque option
tokens and the HMAC shuffle keep working. Passages are edited either as markup with readings in
brackets (図書館《としょかん》, see app/services/passage_markup.py) or, for flyer/table passages,
as sanitized HTML. Admin only (app/core/security.py).
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.core.database import get_db
from app.core.security import require_admin
from app.services import passage_markup as pm

router = APIRouter(dependencies=[Depends(require_admin)], tags=["Admin"])

MAX_TEXT = 20000


class EditOption(BaseModel):
    id: int
    text: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(default="", max_length=4000)
    is_correct: bool


class EditQuestion(BaseModel):
    id: int
    text: str = Field(min_length=1, max_length=4000)
    explanation: str = Field(default="", max_length=8000)
    options: List[EditOption]


class PassagePayload(BaseModel):
    mode: str = Field(pattern="^(markup|html)$")
    markup: Optional[str] = Field(default=None, max_length=MAX_TEXT)
    html: Optional[str] = Field(default=None, max_length=MAX_TEXT * 2)
    frame: Optional[dict] = None


class EditPayload(PassagePayload):
    title: str = Field(min_length=1, max_length=255)
    translation_ru: str = Field(default="", max_length=MAX_TEXT)
    questions: List[EditQuestion]


def _iso(dt):
    return dt.isoformat() + "Z" if dt else None


def _get_text(db: Session, text_id: int) -> models.Text:
    t = db.query(models.Text).filter(models.Text.id == text_id).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return t


def _snapshot(t: models.Text) -> dict:
    return {
        "title": t.title,
        "content_html": t.content_html,
        "translation_ru": t.translation_ru,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "general_explanation": q.general_explanation,
                "options": [
                    {"id": o.id, "option_text": o.option_text, "option_explanation": o.option_explanation,
                     "is_correct": bool(o.is_correct)}
                    for o in q.options
                ],
            }
            for q in t.questions
        ],
    }


def _editor_view(t: models.Text) -> dict:
    mode = pm.passage_mode(t.content_html)
    view = {
        "id": t.id,
        "title": t.title,
        "level": t.level,
        "category": t.category,
        "mode": mode,
        "translation_ru": t.translation_ru or "",
        "evidence_ids": sorted(set(pm.evidence_ids_in_html(t.content_html))),
        "stray_span_closers": pm.stray_span_closers(t.content_html),
        "questions": [
            {
                "id": q.id,
                "number": q.question_number,
                "text": q.question_text,
                "explanation": q.general_explanation or "",
                "evidence_span_id": q.evidence_span_id,
                "options": [
                    {"id": o.id, "number": o.option_number, "text": o.option_text,
                     "explanation": o.option_explanation or "", "is_correct": bool(o.is_correct)}
                    for o in q.options
                ],
            }
            for q in t.questions
        ],
    }
    if mode == "markup":
        markup, frame = pm.html_to_markup(t.content_html)
        view.update({"markup": markup, "frame": frame})
    else:
        view["html"] = t.content_html
    return view


def _render_passage(payload: PassagePayload):
    """Returns (content_html, warnings); 422 with a readable message on invalid input."""
    if payload.mode == "markup":
        if payload.markup is None:
            raise HTTPException(status_code=422, detail="Нет текста задания")
        try:
            return pm.markup_to_html(payload.markup, payload.frame), []
        except pm.MarkupError as e:
            raise HTTPException(status_code=422, detail=str(e))
    html, removed = pm.sanitize_passage_html(payload.html or "")
    if not html:
        raise HTTPException(status_code=422, detail="Текст задания пустой")
    warnings = [f"Удалено небезопасное: {', '.join(sorted(set(removed)))}"] if removed else []
    return html, warnings


def _apply_snapshot(t: models.Text, snap: dict) -> None:
    t.title = snap["title"]
    t.content_html = snap["content_html"]
    t.translation_ru = snap["translation_ru"]
    by_q = {q["id"]: q for q in snap["questions"]}
    for q in t.questions:
        sq = by_q.get(q.id)
        if not sq:
            continue
        q.question_text = sq["question_text"]
        q.general_explanation = sq["general_explanation"]
        by_o = {o["id"]: o for o in sq["options"]}
        for o in q.options:
            so = by_o.get(o.id)
            if so:
                o.option_text = so["option_text"]
                o.option_explanation = so["option_explanation"]
                o.is_correct = so["is_correct"]


def _save_revision(db: Session, t: models.Text, note: str) -> models.TextRevision:
    rev = models.TextRevision(text_id=t.id, snapshot=_snapshot(t), note=note[:200])
    db.add(rev)
    db.flush()
    return rev


@router.get("/api/admin/texts/{text_id}/edit")
def admin_text_edit_view(text_id: int, db: Session = Depends(get_db)):
    return _editor_view(_get_text(db, text_id))


@router.post("/api/admin/passage/preview")
def admin_passage_preview(payload: PassagePayload):
    html, warnings = _render_passage(payload)
    return {"html": html, "warnings": warnings}


@router.post("/api/admin/passage/furigana")
def admin_passage_furigana(payload: PassagePayload):
    """Readings for kanji that have none (janome dictionary readings); existing ones are kept."""
    if payload.mode != "markup" or payload.markup is None:
        raise HTTPException(status_code=422, detail="Автофуригана доступна только для текста с чтениями в скобках")
    markup = pm.add_missing_furigana(payload.markup)
    _render_passage(PassagePayload(mode="markup", markup=markup, frame=payload.frame))  # validate
    return {"markup": markup}


@router.put("/api/admin/texts/{text_id}")
def admin_text_save(text_id: int, payload: EditPayload, db: Session = Depends(get_db)):
    t = _get_text(db, text_id)
    content_html, warnings = _render_passage(payload)

    questions = {q.id: q for q in t.questions}
    if sorted(questions) != sorted(q.id for q in payload.questions):
        raise HTTPException(status_code=422, detail="Состав вопросов изменился — обновите окно и повторите")
    for pq in payload.questions:
        q = questions[pq.id]
        if sorted(o.id for o in q.options) != sorted(o.id for o in pq.options):
            raise HTTPException(status_code=422, detail=f"Вопрос {q.question_number}: состав вариантов изменился")
        if sum(1 for o in pq.options if o.is_correct) != 1:
            raise HTTPException(status_code=422, detail=f"Вопрос {q.question_number}: должен быть ровно один правильный вариант")

    present = set(pm.evidence_ids_in_html(content_html))
    missing = [f"[{q.evidence_span_id}] (вопрос {q.question_number})" for q in t.questions
               if q.evidence_span_id and q.evidence_span_id not in present]
    if missing:
        raise HTTPException(status_code=422, detail="В тексте нет метки доказательства: " + ", ".join(missing))

    rev = _save_revision(db, t, "до правки")
    _apply_snapshot(t, {
        "title": payload.title.strip(),
        "content_html": content_html,
        "translation_ru": payload.translation_ru.strip(),
        "questions": [
            {"id": pq.id, "question_text": pq.text.strip(), "general_explanation": pq.explanation.strip(),
             "options": [{"id": o.id, "option_text": o.text.strip(), "option_explanation": o.explanation.strip(),
                          "is_correct": o.is_correct} for o in pq.options]}
            for pq in payload.questions
        ],
    })
    db.commit()
    db.refresh(t)
    return {"saved": True, "revision_id": rev.id, "warnings": warnings, "text": _editor_view(t)}


@router.get("/api/admin/texts/{text_id}/revisions")
def admin_text_revisions(text_id: int, db: Session = Depends(get_db)):
    _get_text(db, text_id)
    revs = (db.query(models.TextRevision).filter(models.TextRevision.text_id == text_id)
            .order_by(models.TextRevision.created_at.desc(), models.TextRevision.id.desc()).limit(50).all())
    return {"items": [{"id": r.id, "created_at": _iso(r.created_at), "note": r.note,
                       "title": (r.snapshot or {}).get("title")} for r in revs]}


@router.post("/api/admin/texts/{text_id}/revisions/{revision_id}/restore")
def admin_text_restore(text_id: int, revision_id: int, db: Session = Depends(get_db)):
    t = _get_text(db, text_id)
    rev = db.query(models.TextRevision).filter(
        models.TextRevision.id == revision_id, models.TextRevision.text_id == text_id).first()
    if rev is None:
        raise HTTPException(status_code=404, detail="Версия не найдена")
    _save_revision(db, t, f"до отката к версии #{rev.id}")
    _apply_snapshot(t, rev.snapshot)
    db.commit()
    db.refresh(t)
    return {"restored": rev.id, "text": _editor_view(t)}
