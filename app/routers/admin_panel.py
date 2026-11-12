"""Admin panel API (/admin page): stats, user reports, task moderation, recent activity.

Every endpoint requires the admin key (app/core/security.py). Correct answers are returned
only by the admin task preview, never by public endpoints (Anti-Cheat protocol unchanged).
"""
import csv
import io
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.core.database import get_db
from app.core.security import require_admin

router = APIRouter(dependencies=[Depends(require_admin)], tags=["Admin"])

REPORT_STATUSES = ("new", "resolved")


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() + "Z" if dt else None


def _text_brief(text: Optional[models.Text]) -> Optional[dict]:
    if text is None:
        return None
    return {
        "id": text.id,
        "slug": text.slug,
        "title": text.title,
        "level": text.level,
        "category": text.category,
        "origin": text.origin,
        "report_count": text.report_count or 0,
        "is_active": bool(text.is_active),
    }


def _report_dict(r: models.DefectReport) -> dict:
    return {
        "id": r.id,
        "text_id": r.text_id,
        "reason": r.reason,
        "details": r.details,
        "user_id": r.user_id,
        "status": r.status,
        "created_at": _iso(r.created_at),
        "resolved_at": _iso(r.resolved_at),
        "text": _text_brief(r.text),
    }


def _get_or_404(db: Session, model, obj_id: int, what: str):
    obj = db.query(model).filter(model.id == obj_id).first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{what} не найден(о)")
    return obj


@router.get("/api/admin/check")
def admin_check():
    """Lets the /admin page validate the stored key."""
    return {"ok": True}


@router.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    by_level = {}
    for level, active, count in (
        db.query(models.Text.level, models.Text.is_active, func.count(models.Text.id))
        .group_by(models.Text.level, models.Text.is_active).all()
    ):
        row = by_level.setdefault(level, {"active": 0, "hidden": 0})
        row["active" if active else "hidden"] += count

    attempts_total = db.query(func.count(models.Attempt.id)).scalar() or 0
    attempts_week = db.query(func.count(models.Attempt.id)).filter(models.Attempt.created_at >= week_ago).scalar() or 0
    users_total = db.query(func.count(func.distinct(models.Attempt.user_id))).scalar() or 0
    users_week = (
        db.query(func.count(func.distinct(models.Attempt.user_id)))
        .filter(models.Attempt.created_at >= week_ago).scalar() or 0
    )
    avg_score = db.query(func.avg(models.Attempt.score)).scalar()

    reports = dict(
        db.query(models.DefectReport.status, func.count(models.DefectReport.id))
        .group_by(models.DefectReport.status).all()
    )

    return {
        "texts": {
            "total": sum(v["active"] + v["hidden"] for v in by_level.values()),
            "active": sum(v["active"] for v in by_level.values()),
            "hidden": sum(v["hidden"] for v in by_level.values()),
            "by_level": dict(sorted(by_level.items())),
        },
        "attempts": {"total": attempts_total, "last_7_days": attempts_week,
                     "avg_score": round(float(avg_score), 1) if avg_score is not None else None},
        "users": {"total": users_total, "last_7_days": users_week},
        "reports": {"new": reports.get("new", 0), "resolved": reports.get("resolved", 0)},
        "generated_at": _iso(now),
    }


# ---------------------------------------------------------------- reports

@router.get("/api/admin/reports")
def admin_reports(
    status_filter: str = Query("new", alias="status", pattern="^(new|resolved|all)$"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.DefectReport)
    if status_filter != "all":
        query = query.filter(models.DefectReport.status == status_filter)
    items = query.order_by(models.DefectReport.created_at.desc(), models.DefectReport.id.desc()).limit(limit).all()
    return {"items": [_report_dict(r) for r in items]}


@router.get("/api/admin/reports.csv")
def admin_reports_csv(db: Session = Depends(get_db)):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "created_at", "status", "text_id", "title", "level", "reason", "details", "user_id"])
    for r in db.query(models.DefectReport).order_by(models.DefectReport.created_at.desc()).all():
        t = r.text
        writer.writerow([r.id, _iso(r.created_at), r.status, r.text_id, t.title if t else "",
                         t.level if t else "", r.reason, r.details or "", r.user_id or ""])
    # BOM so that Excel opens UTF-8 (Cyrillic, Japanese) correctly
    return Response(
        content="﻿" + buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="dokkai_reports.csv"'},
    )


@router.post("/api/admin/reports/{report_id}/resolve")
def admin_resolve_report(report_id: int, db: Session = Depends(get_db)):
    r = _get_or_404(db, models.DefectReport, report_id, "Сообщение")
    r.status = "resolved"
    r.resolved_at = datetime.utcnow()
    db.commit()
    return _report_dict(r)


@router.post("/api/admin/reports/{report_id}/reopen")
def admin_reopen_report(report_id: int, db: Session = Depends(get_db)):
    r = _get_or_404(db, models.DefectReport, report_id, "Сообщение")
    r.status = "new"
    r.resolved_at = None
    db.commit()
    return _report_dict(r)


@router.delete("/api/admin/reports/{report_id}")
def admin_delete_report(report_id: int, db: Session = Depends(get_db)):
    r = _get_or_404(db, models.DefectReport, report_id, "Сообщение")
    db.delete(r)
    db.commit()
    return {"deleted": report_id}


# ---------------------------------------------------------------- texts (tasks)

@router.get("/api/admin/texts")
def admin_texts(
    q: Optional[str] = Query(None, max_length=100),
    level: Optional[str] = Query(None, pattern="^N[1-5]$"),
    category: Optional[str] = Query(None, max_length=50),
    active: Optional[str] = Query(None, pattern="^(active|hidden)$"),
    reported: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Text)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((models.Text.title.ilike(like)) | (models.Text.slug.ilike(like)))
    if level:
        query = query.filter(models.Text.level == level)
    if category:
        query = query.filter(models.Text.category == category)
    if active == "active":
        query = query.filter(models.Text.is_active.is_(True))
    elif active == "hidden":
        query = query.filter(models.Text.is_active.is_(False))
    if reported:
        query = query.filter(models.Text.report_count > 0)
    total = query.count()
    rows = query.order_by(models.Text.id).offset(offset).limit(limit).all()
    return {"total": total, "items": [_text_brief(t) for t in rows]}


@router.get("/api/admin/texts/{text_id}")
def admin_text_detail(text_id: int, db: Session = Depends(get_db)):
    """Full task for moderation, including correct answers (admin only)."""
    t = _get_or_404(db, models.Text, text_id, "Задание")
    return {
        **_text_brief(t),
        "source_exam": t.source_exam,
        "recommended_time_min": t.recommended_time_min,
        "content_html": t.content_html,
        "translation_ru": t.translation_ru,
        "questions": [
            {
                "number": q.question_number,
                "text": q.question_text,
                "explanation": q.general_explanation,
                "options": [
                    {"number": o.option_number, "text": o.option_text, "is_correct": bool(o.is_correct)}
                    for o in q.options
                ],
            }
            for q in t.questions
        ],
        "reports": [
            _report_dict(r) for r in
            db.query(models.DefectReport).filter(models.DefectReport.text_id == t.id)
            .order_by(models.DefectReport.created_at.desc()).all()
        ],
    }


@router.post("/api/admin/texts/{text_id}/hide")
def admin_hide_text(text_id: int, db: Session = Depends(get_db)):
    t = _get_or_404(db, models.Text, text_id, "Задание")
    t.is_active = False
    db.commit()
    return _text_brief(t)


@router.post("/api/admin/texts/{text_id}/show")
def admin_show_text(text_id: int, reset_reports: bool = True, db: Session = Depends(get_db)):
    """Return a task to the stream; by default also resets the counter so that it is not
    auto-hidden again by the next report (threshold 3)."""
    t = _get_or_404(db, models.Text, text_id, "Задание")
    t.is_active = True
    if reset_reports:
        t.report_count = 0
    db.commit()
    return _text_brief(t)


# ---------------------------------------------------------------- activity

@router.get("/api/admin/activity")
def admin_activity(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    rows = (
        db.query(models.Attempt, models.Text)
        .join(models.Text, models.Text.id == models.Attempt.text_id)
        .order_by(models.Attempt.created_at.desc(), models.Attempt.id.desc())
        .limit(limit).all()
    )
    return {"items": [
        {
            "id": a.id,
            "user_id": a.user_id,
            "text": {"id": t.id, "title": t.title, "level": t.level},
            "score": round(float(a.score), 1),
            "mode": a.mode,
            "created_at": _iso(a.created_at),
        }
        for a, t in rows
    ]}
