#!/usr/bin/env python3
"""Checks for texts from open sources (I34/I35). Runs on a temporary copy of the DB.

  python tools/open_content_check.py [path/to/source.db]   (default: dokkai.db)

1. build_open_content --check passes; every record has attribution with license and url.
2. import_open_content is insert-only and idempotent (second run inserts 0).
3. pick_next serves open-source texts only after the main pool of the category is used up.
4. GET /api/texts/{id}: open texts carry `attribution`, others have no such key; no answer leaks.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src_db = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dokkai.db"
tmp = Path(tempfile.mkdtemp(prefix="open_check_"))
db_copy = tmp / "check.db"
shutil.copy(src_db, db_copy)
os.environ["DATABASE_URL"] = "sqlite:///" + db_copy.as_posix()
os.environ["DOKKAI_TEST_MODE"] = "1"
sys.path.insert(0, str(ROOT))

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


# 1. build
r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_open_content.py"), "--check"],
                   capture_output=True, text=True, encoding="utf-8")
check("build_open_content --check", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:])
records = []
for p in sorted((ROOT / "content" / "open").glob("n*.json")):
    records += json.loads(p.read_text(encoding="utf-8"))
bad_attr = [x["slug"] for x in records if not (x.get("attribution") or {}).get("license") or not x["attribution"].get("url", "").startswith("https://")]
check("attribution: license + https url for every record", not bad_attr, ", ".join(bad_attr))

# 2. import (idempotent)
from tools.import_open_content import import_open_content  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models import Text  # noqa: E402

first = import_open_content()
second = import_open_content()
check("import is idempotent", len(second["inserted"]) == 0 and len(second["skipped"]) == len(records),
      f"first +{len(first['inserted'])}, second +{len(second['inserted'])}")
from tools.migrations.add_stream_tables import migrate  # noqa: E402
import contextlib, io  # noqa: E401,E402
with contextlib.redirect_stdout(io.StringIO()):
    migrate()

# 3. pick_next order
from app.services.stream_service import pick_next, get_default_profile_for_level  # noqa: E402

db = SessionLocal()
order_ok, detail = True, []
for rec in records:
    lvl, cat = rec["level"], rec["category"]
    profile = get_default_profile_for_level(lvl, cat)
    old_ids = {i for (i,) in db.query(Text.id).filter(Text.level == lvl, Text.category == cat,
                                                       Text.origin != "open_source").all()}
    open_ids = {i for (i,) in db.query(Text.id).filter(Text.level == lvl, Text.category == cat,
                                                        Text.origin == "open_source", Text.is_active == True).all()}
    picks = [pick_next(db, f"open-check-{i}", profile, allow_generate=False) for i in range(30)]
    if any(p is not None and p.origin == "open_source" for p in picks):
        order_ok = False
        detail.append(f"{rec['slug']}: open text picked while main pool has texts")
    last = pick_next(db, "open-check-x", profile, exclude_text_ids=old_ids, allow_generate=False)
    if last is None or last.id not in open_ids:
        order_ok = False
        detail.append(f"{rec['slug']}: not picked after main pool is used up")
check("pick_next: open texts only after the main pool", order_ok, "; ".join(sorted(set(detail))))

# 4. API
from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

LEAK_KEYS = ("is_correct", "trap_type", "evidence_span_id", "option_explanation", "explanation", "translation_ru")
with contextlib.redirect_stdout(io.StringIO()), TestClient(app) as client:
    open_rows = db.query(Text.id, Text.slug).filter(Text.origin == "open_source").all()
    api_ok, leaks = True, []
    for tid, slug in open_rows:
        body = client.get(f"/api/texts/{tid}?user_id=open-check").json()
        attr = body.get("attribution") or {}
        if attr.get("url") is None or attr.get("license") is None:
            api_ok = False
        raw = json.dumps(body)
        leaks += [f"{slug}:{k}" for k in LEAK_KEYS if f'"{k}"' in raw]
    old_id = db.query(Text.id).filter(Text.origin != "open_source").order_by(Text.id).first()[0]
    old_body = client.get(f"/api/texts/{old_id}?user_id=open-check").json()
check("API: attribution on every open text", api_ok and len(open_rows) == len(records), f"{len(open_rows)} texts")
check("API: no `attribution` key on other texts", "attribution" not in old_body, f"text {old_id}")
check("API: no answer leaks", not leaks, ", ".join(leaks))
db.close()

shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASSED" if all(results) else f"FAILED: {results.count(False)} of {len(results)}")
sys.exit(0 if all(results) else 1)
