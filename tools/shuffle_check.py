#!/usr/bin/env python3
"""Step 11d: end-to-end checks of the server-side option shuffle (needs a running server + its SQLite file).

Usage:
    DATABASE_URL=sqlite:///./copy.db python -m uvicorn main:app --port 8010
    python tools/shuffle_check.py --base http://localhost:8010 --db ./copy.db [--restart-cmd "..."]

Runs against a COPY of the database: it creates attempts for throw-away users.
"""
import argparse
import collections
import json
import sqlite3
import sys
import urllib.request

FORBIDDEN = {"is_correct", "trap_type", "option_explanation", "general_explanation",
             "evidence_span_id", "correct_option_id", "explanation"}


def call(base, method, path, body=None):
    req = urllib.request.Request(base + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def keys_of(obj, acc=None):
    acc = set() if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(k)
            keys_of(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            keys_of(v, acc)
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8010")
    ap.add_argument("--db", required=True)
    a = ap.parse_args()
    base = a.base
    db = sqlite3.connect(a.db)
    failed = []

    def check(name, ok, info=""):
        print(("PASS  " if ok else "FAIL  ") + name + (f"   {info}" if info and not ok else ""))
        if not ok:
            failed.append(name)

    text_id = db.execute("select id from texts where is_active=1 order by id limit 1").fetchone()[0]
    raw = {}  # question_id -> {option_id: (text, correct)}
    for qid, oid, txt, cor in db.execute(
            "select o.question_id, o.id, o.option_text, o.is_correct from options o join questions q on q.id=o.question_id where q.text_id=?",
            (text_id,)):
        raw.setdefault(qid, {})[oid] = (txt, bool(cor))
    raw_ids = {oid for q in raw.values() for oid in q}

    def view(user):
        return call(base, "GET", f"/api/texts/{text_id}?user_id={user}")

    def order(v):
        return [[o["option_text"] for o in q["options"]] for q in v["questions"]]

    # 1. determinism per (user, text, attempt)
    v1, v2 = view("shuf-A"), view("shuf-A")
    check("same user + same attempt -> identical order and tokens", v1 == v2)

    # 2. tokens are opaque
    tokens = {o["id"] for q in v1["questions"] for o in q["options"]}
    check("no raw database option id is exposed", not (tokens & raw_ids))
    check("tokens fit a JS safe integer", all(0 < t < 2 ** 53 for t in tokens))
    check("option_number is the displayed position 1..n",
          all([o["option_number"] for o in q["options"]] == list(range(1, len(q["options"]) + 1)) for q in v1["questions"]))
    check("anti-cheat: no answer keys in /api/texts", not (keys_of(v1) & FORBIDDEN), str(keys_of(v1) & FORBIDDEN))

    # 3. different users get different orders (at least somewhere)
    others = [order(view(f"shuf-U{i}")) for i in range(8)]
    check("different users get different orders", any(o != order(v1) for o in others))

    # 4. every option is still present exactly once
    check("shuffle is a permutation (same options, none lost)",
          all(sorted(o["option_text"] for o in q["options"]) == sorted(t for t, _ in raw[q["id"]].values())
              for q in v1["questions"]))

    # 5. correct answer by TEXT resolves through tokens -> 100%
    def answers_for(v, pick_correct=True):
        out = []
        for q in v["questions"]:
            txt_correct = next(t for t, c in raw[q["id"]].values() if c)
            wrong = [o for o in q["options"] if o["option_text"] != txt_correct]
            chosen = next(o for o in q["options"] if o["option_text"] == txt_correct) if pick_correct else wrong[0]
            out.append({"question_id": q["id"], "selected_option_id": chosen["id"]})
        return out

    bad = call(base, "POST", "/api/stream/complete", {"user_id": "shuf-W", "text_id": text_id, "idempotency_key": "w1",
               "answers": answers_for(view("shuf-W"), pick_correct=False)})
    check("wrong tokens score 0 correct", bad.get("correct_count") == 0, str(bad.get("correct_count")))

    shown = view("shuf-A")
    res = call(base, "POST", "/api/stream/complete", {"user_id": "shuf-A", "text_id": text_id, "idempotency_key": "a1",
               "answers": answers_for(shown)})
    check("correct answers (by text) via tokens score 100%", res.get("score_percent") == 100.0, str(res.get("score_percent")))

    # 6. review shows the order the user saw during the attempt, with consistent tokens
    seen = order(shown)
    review_order = [[o["option_text"] for o in q["options"]] for q in res["questions"]]
    check("analysis keeps the order shown during the attempt", seen == review_order)
    ok_sel = all(q["selected_option_id"] == q["correct_option_id"] and q["is_user_correct"] for q in res["questions"])
    check("analysis: selected/correct ids are tokens and match", ok_sel)
    check("analysis does not expose raw ids", not ({o["id"] for q in res["questions"] for o in q["options"]} & raw_ids))
    rv = call(base, "GET", f"/api/stream/solved/{text_id}?user_id=shuf-A")
    check("/solved review identical to completion analysis (options order)",
          [[o["option_text"] for o in q["options"]] for q in rv["questions"]] == review_order)

    # 7. raw database ids are not accepted
    raw_answers = [{"question_id": q["id"], "selected_option_id": next(oid for oid, (t, c) in raw[q["id"]].items() if c)}
                   for q in shown["questions"]]
    rr = call(base, "POST", "/api/stream/complete", {"user_id": "shuf-R", "text_id": text_id, "idempotency_key": "r1",
              "answers": raw_answers})
    check("raw (unshuffled) option ids are rejected", rr.get("correct_count") == 0, str(rr.get("correct_count")))

    # 8. new attempt (retry) -> new epoch -> order may change, still consistent
    rt = call(base, "POST", f"/api/stream/retry/{text_id}?user_id=shuf-A")
    check("retry: no answer keys", not (keys_of(rt) & FORBIDDEN), str(keys_of(rt) & FORBIDDEN))
    retry_tokens = {o["id"] for q in rt["questions"] for o in q["options"]}
    check("retry: options use new tokens (epoch changed)", retry_tokens != tokens)
    fresh = view("shuf-A")
    check("retry: /api/texts matches /retry order for the new attempt",
          order(fresh) == [[o["option_text"] for o in q["options"]] for q in rt["questions"]])

    # 9. slots endpoint
    sl = call(base, "GET", "/api/stream/slots?user_id=shuf-S&level=N5&category=short")
    check("slots: no answer keys", not (keys_of(sl) & FORBIDDEN), str(keys_of(sl) & FORBIDDEN))
    slot_tokens = {o["id"] for s in sl["slots"] if s["text"] for q in s["text"]["questions"] for o in q["options"]}
    check("slots: no raw ids", not (slot_tokens & raw_ids) and not slot_tokens & {
        r[0] for r in db.execute("select id from options")})

    # 10. distribution of the correct answer's displayed position (the old DB is 54% position #1)
    texts = [r[0] for r in db.execute("select id from texts where is_active=1 order by id limit 25")]
    all_opts = collections.defaultdict(dict)
    for qid, oid, txt, cor in db.execute("select question_id, id, option_text, is_correct from options"):
        all_opts[qid][txt] = bool(cor)
    pos = collections.Counter()
    for t in texts:
        for u in range(6):
            v = call(base, "GET", f"/api/texts/{t}?user_id=dist-{u}")
            for q in v["questions"]:
                for o in q["options"]:
                    if all_opts[q["id"]].get(o["option_text"]):
                        pos[o["option_number"]] += 1
    total = sum(pos.values())
    print("      correct answer position:", {k: f"{v * 100 // total}%" for k, v in sorted(pos.items())}, f"(n={total})")
    check("correct answer is no longer biased to position 1 (<45%)", pos[1] / total < 0.45)

    print("\n" + ("ALL PASSED" if not failed else f"{len(failed)} FAILED: {failed}"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
