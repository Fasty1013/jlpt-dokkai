"""
API snapshot / parity tool for backend refactoring (Step 8).

Runs the FastAPI app in-process (TestClient) against a TEMPORARY COPY of dokkai.db
and records status code, selected headers and body of every public endpoint.

  python tools/api_snapshot.py --capture      # write tools/snapshots/api_snapshot.main.json
  python tools/api_snapshot.py                # compare current code with the stored golden snapshot

Comparison modes per request:
  exact - body must be byte-identical after masking volatile values (timestamps, git commit)
  shape - body structure only (keys, types, list lengths); used where the server picks
          content with SQL random() (stream slots) so values legitimately differ per run.
  loose - like shape, but list lengths are ignored too (the script answers options[0]; since
          Step 11d the correct option position is shuffled, so error lists vary per run).

Also asserts the Anti-Cheat protocol: pre-submit endpoints never expose is_correct,
explanation, trap_type or evidence_span_id.
"""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / "tools" / "snapshots" / "api_snapshot.main.json"
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

TMP = tempfile.mkdtemp(prefix="dokkai_snap_")
shutil.copy(os.environ.get("DOKKAI_SNAPSHOT_DB") or (ROOT / "dokkai.db"), Path(TMP) / "snap.db")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TMP) / "snap.db").replace("\\", "/")
os.environ["DOKKAI_TEST_MODE"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

HEADERS = ["content-type", "cache-control", "pragma", "expires", "service-worker-allowed"]
FORBIDDEN_PRE_SUBMIT = {"is_correct", "explanation", "trap_type", "evidence_span_id",
                        "option_explanation", "general_explanation", "correct_option_id"}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def mask_url(u):
    return re.sub(r"/(solved|retry)/(?!999999)[0-9]+", lambda m: "/" + m.group(1) + "/<TID>", u)


def mask(v, key=None):
    if isinstance(v, dict):
        return {k: mask(x, k) for k, x in v.items()}
    if isinstance(v, list):
        return [mask(x) for x in v]
    if isinstance(v, str) and TS_RE.match(v):
        return "<TS>"
    if key == "commit":
        return "<COMMIT>"
    return v


def shape(v, loose=False):
    if isinstance(v, dict):
        return {k: shape(x, loose) for k, x in sorted(v.items())}
    if isinstance(v, list):
        if loose:  # list length / emptiness depends on the random slot text and shuffled options
            return {"__list__": "*"}
        return {"__list__": len(v), "item": shape(v[0]) if v else None}
    return type(v).__name__ if v is not None else "null"


def walk_keys(v, acc):
    if isinstance(v, dict):
        for k, x in v.items():
            acc.add(k)
            walk_keys(x, acc)
    elif isinstance(v, list):
        for x in v:
            walk_keys(x, acc)
    return acc


def main():
    capture = "--capture" in sys.argv
    out, leaks = {}, []

    with TestClient(app) as c:
        def rec(name, method, url, mode="exact", anticheat=False, raw=False, **kw):
            r = c.request(method, url, **kw)
            entry = {"method": method, "url": mask_url(url), "status": r.status_code,
                     "headers": {h: r.headers.get(h) for h in HEADERS}}
            if raw:
                entry["mode"] = "headers-only"
            else:
                try:
                    body = r.json()
                except Exception:
                    body = {"__text__": r.text[:2000]}
                if anticheat:
                    bad = walk_keys(body, set()) & FORBIDDEN_PRE_SUBMIT
                    if bad:
                        leaks.append((name, sorted(bad)))
                entry["mode"] = mode
                entry["body"] = mask(body) if mode == "exact" else shape(body, loose=(mode == "loose"))
            out[name] = entry
            return r

        rec("health", "GET", "/api/health")
        rec("version", "GET", "/api/version")
        rec("openapi", "GET", "/openapi.json")
        rec("index_headers", "GET", "/", raw=True)
        rec("sw_headers", "GET", "/sw.js", raw=True)
        rec("sw_version_override", "GET", "/sw.js?version=9.9.9", raw=True)
        rec("texts_all", "GET", "/api/texts")
        rec("texts_n5_short", "GET", "/api/texts?level=n5&category=short")
        rec("texts_no_match", "GET", "/api/texts?level=ZZ")

        r = rec("text_1", "GET", "/api/texts/1", anticheat=True)
        rec("text_missing", "GET", "/api/texts/999999")
        rec("text_bad_id", "GET", "/api/texts/abc")

        text = r.json()
        answers = [{"question_id": q["id"], "selected_option_id": q["options"][0]["id"]}
                   for q in text["questions"]]
        rec("submit_text_1", "POST", "/api/texts/1/submit",
            json={"answers": answers, "time_spent_sec": 42})
        rec("submit_empty", "POST", "/api/texts/1/submit", json={"answers": []})
        rec("submit_invalid", "POST", "/api/texts/1/submit", json={"nope": 1})
        rec("submit_missing_text", "POST", "/api/texts/999999/submit", json={"answers": answers})

        rec("dict_lookup", "GET", "/api/dictionary/lookup?q=%E6%97%A5%E6%9C%AC")
        rec("dict_lookup_empty", "GET", "/api/dictionary/lookup?q=")
        rec("dict_lookup_unknown", "GET", "/api/dictionary/lookup?q=zzzqqq")

        user = "snap-user"
        rec("slots_n5_short", "GET", f"/api/stream/slots?user_id={user}&level=N5&category=short",
            mode="shape", anticheat=True)
        s = c.get(f"/api/stream/slots?user_id={user}&level=N5&category=short").json()
        t = s["slots"][0]["text"]
        tid = t["id"]
        ans = [{"question_id": q["id"], "selected_option_id": q["options"][0]["id"]} for q in t["questions"]]
        body = {"user_id": user, "text_id": tid, "answers": ans, "idempotency_key": "snap-key-1"}
        rec("complete_first", "POST", "/api/stream/complete", mode="loose", json=body)
        rec("complete_idempotent", "POST", "/api/stream/complete", mode="loose", json=body)
        rec("complete_missing_text", "POST", "/api/stream/complete", mode="shape",
            json={**body, "text_id": 999999, "idempotency_key": "snap-key-2"})
        rec("complete_invalid", "POST", "/api/stream/complete", json={"user_id": user})
        rec("solved_list", "GET", f"/api/stream/solved?user_id={user}", mode="shape")
        rec("solved_list_filters", "GET", f"/api/stream/solved?user_id={user}&level=N5&only_perfect=true&page=1&page_size=5", mode="loose")
        rec("solved_bad_page", "GET", "/api/stream/solved?page=0")
        rec("solved_detail", "GET", f"/api/stream/solved/{tid}?user_id={user}", mode="loose")
        rec("solved_detail_missing", "GET", f"/api/stream/solved/999999?user_id={user}", mode="shape")
        rec("retry", "POST", f"/api/stream/retry/{tid}?user_id={user}", mode="shape")
        rec("retry_missing", "POST", f"/api/stream/retry/999999?user_id={user}", mode="shape")
        rec("report", "POST", "/api/texts/1/report", mode="shape",
            json={"reason": "snapshot", "details": "api snapshot", "user_id": user})
        rec("report_invalid", "POST", "/api/texts/1/report", json={})
        rec("report_missing_text", "POST", "/api/texts/999999/report", mode="shape", json={"reason": "x"})

        rec("admin_drafts", "GET", "/api/admin/drafts", mode="shape")
        rec("admin_draft_missing", "GET", "/api/admin/drafts/does-not-exist", mode="shape")
        rec("unknown_route", "GET", "/api/nope")
        rec("static_missing", "GET", "/static/nope.txt", raw=True)

    shutil.rmtree(TMP, ignore_errors=True)

    if leaks:
        print("ANTI-CHEAT LEAKS:", leaks)
        sys.exit(2)

    if capture:
        SNAP.parent.mkdir(parents=True, exist_ok=True)
        SNAP.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print(f"captured {len(out)} requests -> {SNAP.relative_to(ROOT)}")
        return

    gold = json.loads(SNAP.read_text(encoding="utf-8"))
    cur = json.loads(json.dumps(out, ensure_ascii=False, sort_keys=True))
    bad = 0
    for name in sorted(set(gold) | set(cur)):
        if gold.get(name) == cur.get(name):
            print(f"  PASS  {name}")
        else:
            bad += 1
            print(f"  FAIL  {name}")
            g, n = gold.get(name), cur.get(name)
            if g and n:
                for k in g:
                    if g[k] != n.get(k):
                        print(f"        differs in '{k}'")
    print(f"\n{len(cur) - bad}/{len(cur)} identical")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
