"""Admin panel and report storage checks (in-process TestClient on a TEMPORARY copy of dokkai.db).

Usage: python tools/admin_check.py
Covers: report text is stored and the public report response is unchanged; admin key rules
(test mode without key = open, key set = header required, production without key = closed);
stats, reports list/resolve/reopen/delete/CSV, task hide/show/detail, activity; /admin page.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TMP = tempfile.mkdtemp(prefix="dokkai_admin_")
shutil.copy(os.environ.get("DOKKAI_SNAPSHOT_DB") or (ROOT / "dokkai.db"), Path(TMP) / "admin.db")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TMP) / "admin.db").replace("\\", "/")
os.environ["DOKKAI_TEST_MODE"] = "1"
os.environ.pop("ADMIN_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

failed = []


def check(name, ok, info=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"   {info}" if info and not ok else ""))
    if not ok:
        failed.append(name)


with TestClient(main.app) as c:
    text_id = c.get("/api/texts?level=N5").json()[0]["id"]

    # --- report storage, public contract unchanged
    marker = "admin-check <img src=x onerror=alert(1)> 改行\nвторая строка"
    r = c.post(f"/api/texts/{text_id}/report", json={"reason": "Опечатка в тексте или вопросе", "details": marker, "user_id": "user-admin-check"})
    check("report: 200", r.status_code == 200, r.text)
    check("report: response keys unchanged",
          sorted(r.json()) == ["deactivated", "is_active", "message", "report_count", "status", "text_id"], r.text)
    r2 = c.post(f"/api/texts/{text_id}/report", json={"reason": "Другая ошибка"})
    check("report without details/user: 200", r2.status_code == 200, r2.text)

    # --- test mode, no ADMIN_TOKEN: open (parity tools/tests)
    check("test mode, no key: /api/admin/check 200", c.get("/api/admin/check").status_code == 200)
    check("test mode, no key: /api/admin/drafts 200", c.get("/api/admin/drafts").status_code == 200)

    reports = c.get("/api/admin/reports?status=new").json()["items"]
    mine = [x for x in reports if x["details"] == marker]
    check("reports: stored with full details text", len(mine) == 1, str(reports[:2]))
    rep = mine[0] if mine else {}
    check("reports: reason/user/text attached",
          rep.get("reason") == "Опечатка в тексте или вопросе" and rep.get("user_id") == "user-admin-check"
          and rep.get("text", {}).get("id") == text_id, str(rep))
    check("reports: empty details stored as null",
          any(x["reason"] == "Другая ошибка" and x["details"] is None and x["user_id"] is None for x in reports))

    rid = rep.get("id")
    r = c.post(f"/api/admin/reports/{rid}/resolve")
    check("resolve: status resolved + resolved_at", r.status_code == 200 and r.json()["status"] == "resolved" and r.json()["resolved_at"])
    check("resolve: gone from 'new'", all(x["id"] != rid for x in c.get("/api/admin/reports?status=new").json()["items"]))
    check("resolve: in 'resolved'", any(x["id"] == rid for x in c.get("/api/admin/reports?status=resolved").json()["items"]))
    r = c.post(f"/api/admin/reports/{rid}/reopen")
    check("reopen: back to new", r.status_code == 200 and r.json()["status"] == "new" and r.json()["resolved_at"] is None)
    check("reports: bad status rejected", c.get("/api/admin/reports?status=zzz").status_code == 422)

    csv_resp = c.get("/api/admin/reports.csv")
    check("csv: 200 text/csv with BOM and the report",
          csv_resp.status_code == 200 and csv_resp.headers["content-type"].startswith("text/csv")
          and csv_resp.content.startswith("﻿".encode("utf-8")) and "admin-check" in csv_resp.text)

    stats = c.get("/api/admin/stats").json()
    check("stats: shape", {"texts", "attempts", "users", "reports"} <= set(stats) and stats["reports"]["new"] >= 2, str(stats))

    # --- tasks
    lst = c.get("/api/admin/texts?level=N5&limit=5").json()
    check("texts: list with total", lst["total"] > 0 and len(lst["items"]) <= 5)
    check("texts: reported filter", any(t["id"] == text_id for t in c.get("/api/admin/texts?reported=true&limit=200").json()["items"]))
    detail = c.get(f"/api/admin/texts/{text_id}").json()
    check("text detail: admin sees correct answers",
          all(any(o["is_correct"] for o in q["options"]) for q in detail["questions"]) and detail["reports"], str(detail.get("questions", [])[:1]))
    c.post(f"/api/admin/texts/{text_id}/hide")
    check("hide: inactive", c.get(f"/api/admin/texts/{text_id}").json()["is_active"] is False)
    shown = c.post(f"/api/admin/texts/{text_id}/show").json()
    check("show: active and report_count reset", shown["is_active"] is True and shown["report_count"] == 0, str(shown))
    check("text detail: 404 for unknown", c.get("/api/admin/texts/99999999").status_code == 404)

    act = c.get("/api/admin/activity?limit=5")
    check("activity: 200 list", act.status_code == 200 and isinstance(act.json()["items"], list))

    r = c.delete(f"/api/admin/reports/{rid}")
    check("delete: removed", r.status_code == 200 and all(x["id"] != rid for x in c.get("/api/admin/reports?status=all").json()["items"]))

    # --- public endpoints never expose answers (Anti-Cheat) and do not expose reports
    pub = c.get(f"/api/texts/{text_id}?user_id=admin-check").text
    check("public text: no answer keys", not any(k in pub for k in ('"is_correct"', '"explanation"', '"trap_type"', '"evidence_span_id"')))

    # --- /admin page
    page = c.get("/admin")
    check("/admin page: 200 html noindex", page.status_code == 200 and "Админ-панель" in page.text
          and page.headers.get("x-robots-tag") == "noindex, nofollow")
    check("/admin not in OpenAPI", "/admin\"" not in c.get("/openapi.json").text)

    # --- key set: header required
    os.environ["ADMIN_TOKEN"] = "s3cret-admin-check"
    for path in ("/api/admin/check", "/api/admin/reports", "/api/admin/stats", "/api/admin/drafts"):
        check(f"key set, no header: {path} 401", c.get(path).status_code == 401)
    check("key set, wrong header: 401", c.get("/api/admin/check", headers={"X-Admin-Token": "nope"}).status_code == 401)
    check("key set, right header: 200", c.get("/api/admin/check", headers={"X-Admin-Token": "s3cret-admin-check"}).status_code == 200)
    check("key set: upload-pdf 401 without header", c.post("/api/admin/upload-pdf").status_code == 401)
    check("401 detail is the localized server message",
          c.get("/api/admin/check").json().get("detail") == "Требуется ключ администратора")

    # --- production (no test mode), no key: closed
    os.environ.pop("ADMIN_TOKEN", None)
    os.environ["DOKKAI_TEST_MODE"] = "0"
    check("prod, no key configured: admin closed", c.get("/api/admin/check").status_code == 401)
    check("prod, no key configured: drafts closed", c.get("/api/admin/drafts").status_code == 401)
    check("prod: report still works", c.post(f"/api/texts/{text_id}/report", json={"reason": "Другая ошибка"}).status_code == 200)
    os.environ["DOKKAI_TEST_MODE"] = "1"

shutil.rmtree(TMP, ignore_errors=True)
print("\nALL PASSED" if not failed else f"\n{len(failed)} FAILED")
sys.exit(1 if failed else 0)
