#!/usr/bin/env python3
"""Insert-only import of open-licensed texts (content/open/n*.json) into the database.

Unlike content_loader.load_content() this never updates or deletes anything:
a text whose slug already exists is skipped as is (its questions, option ids,
attempts and admin-editor revisions stay untouched). Safe to run repeatedly.

New texts get origin="open_source", verification_status="unverified" (until the
@jlpt-expert review is recorded) and source_exam = the attribution line.
profile_key / content_hash are filled by tools/migrations/add_stream_tables.migrate(),
which also runs on every server start.

Usage:
  python tools/import_open_content.py --dry-run   # show what would be inserted
  python tools/import_open_content.py             # insert into DATABASE_URL (default: local SQLite)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Option, Question, Text  # noqa: E402
from validate_content import validate_text_record  # noqa: E402

OPEN_DIR = ROOT / "content" / "open"
ORIGIN = "open_source"


def load_records():
    records, errors, seen = [], [], set()
    for p in sorted(OPEN_DIR.glob("n*.json")):
        for rec in json.loads(p.read_text(encoding="utf-8")):
            errs = validate_text_record(rec, p.name, seen)
            if rec.get("source_type") != "open_adapted":
                errs.append(f"[{rec.get('slug')}] source_type должен быть open_adapted")
            if not (rec.get("attribution") or {}).get("license"):
                errs.append(f"[{rec.get('slug')}] нет attribution.license")
            errors.extend(errs)
            records.append(rec)
    return records, errors


def import_open_content(dry_run: bool = False) -> dict:
    records, errors = load_records()
    if errors:
        raise SystemExit("Контент не прошёл проверку:\n  • " + "\n  • ".join(errors))
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted, skipped = [], []
    try:
        existing = {s for (s,) in db.query(Text.slug).filter(Text.slug.in_([r["slug"] for r in records])).all()}
        for rec in records:
            if rec["slug"] in existing:
                skipped.append(rec["slug"])
                continue
            inserted.append(rec["slug"])
            if dry_run:
                continue
            text = Text(
                slug=rec["slug"], title=rec["title"], level=rec["level"], category=rec["category"],
                source_exam=rec["source_note"], is_nhk=False,
                recommended_time_min=rec.get("recommended_time_min", 4),
                content_html=rec["body_html"], translation_ru=rec["translation_ru"],
                vocabulary_json=rec.get("vocabulary", []),
                origin=ORIGIN, verification_status="unverified", is_active=True,
            )
            db.add(text)
            db.flush()
            for q in rec["questions"]:
                qo = Question(text_id=text.id, question_number=q["question_number"], question_text=q["prompt"],
                              general_explanation=q.get("general_explanation", ""),
                              evidence_span_id=q.get("evidence_span_id"))
                db.add(qo)
                db.flush()
                for o in q["options"]:
                    db.add(Option(question_id=qo.id, option_number=o["option_number"], option_text=o["text"],
                                  is_correct=o["is_correct"], trap_type=o.get("trap_type"),
                                  option_explanation=o["explanation_ru"]))
        if dry_run:
            db.rollback()
        else:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return {"inserted": inserted, "skipped": skipped}


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    res = import_open_content(dry_run=dry)
    print(("[dry-run] " if dry else "") + f"добавлено: {len(res['inserted'])}, уже были: {len(res['skipped'])}")
    for s in res["inserted"]:
        print("  +", s)
    if not dry and res["inserted"]:
        from tools.migrations.add_stream_tables import migrate
        migrate()
        print("profile_key/content_hash заполнены (migrate)")
