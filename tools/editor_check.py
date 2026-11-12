"""Admin task editor checks (in-process TestClient on a TEMPORARY copy of dokkai.db).

Usage: python tools/editor_check.py
- every passage converts to the editor format and back without loss (prose: identical except
  stray </span> closers; flyers: sanitizer keeps them identical);
- saving edits title/passage/questions/options/correct answer/translation in place, the public
  API shows the change and still hides answers; option ids/tokens are unchanged;
- validation: one correct option, evidence markers, broken markup, changed structure;
- revisions are stored and restore works; HTML mode strips unsafe markup; furigana endpoint;
- admin key required when ADMIN_TOKEN is set.
"""
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TMP = tempfile.mkdtemp(prefix="dokkai_editor_")
shutil.copy(os.environ.get("DOKKAI_SNAPSHOT_DB") or (ROOT / "dokkai.db"), Path(TMP) / "editor.db")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TMP) / "editor.db").replace("\\", "/")
os.environ["DOKKAI_TEST_MODE"] = "1"
os.environ.pop("ADMIN_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
from app import models  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.services import passage_markup as pm  # noqa: E402

failed = []


def check(name, ok, info=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"   {info}" if info and not ok else ""))
    if not ok:
        failed.append(name)


def strip_stray(h):
    out, depth, pos = [], 0, 0
    for m in re.finditer(r"<span\b[^>]*>|</span>", h):
        out.append(h[pos:m.start()])
        pos = m.end()
        if m.group(0) == "</span>":
            if depth:
                depth -= 1
                out.append(m.group(0))
        else:
            depth += 1
            out.append(m.group(0))
    out.append(h[pos:])
    return "".join(out)


# ------------------------------------------------------------------ lossless conversion
db = SessionLocal()
exact = stray = html_ok = bad = 0
for t in db.query(models.Text).all():
    if pm.passage_mode(t.content_html) == "markup":
        mk, fr = pm.html_to_markup(t.content_html)
        back = pm.markup_to_html(mk, fr)
        if back == t.content_html:
            exact += 1
        elif back == strip_stray(t.content_html) and pm.stray_span_closers(t.content_html):
            stray += 1
        else:
            bad += 1
    else:
        s, removed = pm.sanitize_passage_html(t.content_html)
        html_ok += int(s == t.content_html.strip() and not removed)
        bad += int(not (s == t.content_html.strip() and not removed))
db.close()
check(f"convert: all passages lossless (prose exact {exact}, prose minus stray </span> {stray}, html {html_ok})", bad == 0, f"bad={bad}")

# ------------------------------------------------------------------ markup unit checks
check("markup: ruby + bar + evidence", pm.markup_to_html("[ev-q1]図書館《としょかん》で｜お願《ねが》い[/ev-q1]", {"head": "", "wrapped": False})
      == '<p><span id="ev-q1" data-evidence="ev-q1"><ruby>図書館<rt>としょかん</rt></ruby>で<ruby>お願<rt>ねが</rt></ruby>い</span></p>')
check("markup: text is escaped", "&lt;script&gt;" in pm.markup_to_html("<script>alert(1)</script>"))
for bad_markup, label in [("《よみ》だけ", "reading without kanji"), ("[ev-q1]開いたまま", "unclosed evidence"),
                          ("図書館《としょかん", "unbalanced bracket"), ("[/ev-q1]", "closing without opening")]:
    try:
        pm.markup_to_html(bad_markup)
        check(f"markup error: {label}", False, "no error")
    except pm.MarkupError:
        check(f"markup error: {label}", True)
fur = pm.add_missing_furigana("日本語学校の大会《たいかい》です。お願いします。")
check("furigana: tokenizer readings, existing kept, okurigana outside",
      fur == "日本語《にほんご》学校《がっこう》の大会《たいかい》です。お願《ねが》いします。", fur)
san, removed = pm.sanitize_passage_html('<div class="x" onclick="evil()"><script>alert(1)</script><p>ok</p><a href="javascript:x">l</a><img src=x onerror=y></div>')
check("sanitize: script/handlers/links/images removed", san == '<div class="x"><p>ok</p>l</div>' and removed, san)

with TestClient(main.app) as c:
    # pick a prose task with evidence and a flyer task
    texts = c.get("/api/admin/texts?limit=200").json()["items"]
    prose = flyer = None
    for t in texts:
        v = c.get(f"/api/admin/texts/{t['id']}/edit").json()
        if v["mode"] == "markup" and v["evidence_ids"] and not prose:
            prose = v
        if v["mode"] == "html" and not flyer:
            flyer = v
        if prose and flyer:
            break
    check("edit view: prose task in markup mode", prose is not None)
    tid = prose["id"]
    public_before = c.get(f"/api/texts/{tid}?user_id=editor-check").json()
    tokens_before = sorted(o["id"] for q in public_before["questions"] for o in q["options"])

    # --- validation errors
    def payload(v, **over):
        p = {"title": v["title"], "mode": v["mode"], "translation_ru": v["translation_ru"],
             "questions": [{"id": q["id"], "text": q["text"], "explanation": q["explanation"],
                            "options": [{"id": o["id"], "text": o["text"], "explanation": o["explanation"],
                                         "is_correct": o["is_correct"]} for o in q["options"]]} for q in v["questions"]]}
        if v["mode"] == "markup":
            p.update({"markup": v["markup"], "frame": v["frame"]})
        else:
            p["html"] = v["html"]
        p.update(over)
        return p

    two = payload(prose)
    for o in two["questions"][0]["options"]:
        o["is_correct"] = True
    r = c.put(f"/api/admin/texts/{tid}", json=two)
    check("validation: two correct options -> 422", r.status_code == 422 and "ровно один" in r.json()["detail"], r.text)
    ev = prose["evidence_ids"][0]
    r = c.put(f"/api/admin/texts/{tid}", json=payload(prose, markup=prose["markup"].replace(f"[{ev}]", "").replace(f"[/{ev}]", "")))
    check("validation: removed evidence marker -> 422", r.status_code == 422 and ev in r.json()["detail"], r.text)
    r = c.put(f"/api/admin/texts/{tid}", json=payload(prose, markup=prose["markup"] + "\n\n《よみ》"))
    check("validation: broken markup -> 422 with paragraph", r.status_code == 422 and "Абзац" in r.json()["detail"], r.text)
    struct = payload(prose)
    struct["questions"] = struct["questions"][1:] if len(struct["questions"]) > 1 else []
    r = c.put(f"/api/admin/texts/{tid}", json=struct)
    check("validation: changed question set -> 422", r.status_code == 422, r.text)
    check("validation: nothing saved by failed requests", c.get(f"/api/admin/texts/{tid}/revisions").json()["items"] == [])

    # --- successful edit
    new = payload(prose, title=prose["title"] + " (испр.)",
                  markup=prose["markup"].replace("。", "。", 1) + "\n\n編集《へんしゅう》テスト",
                  translation_ru=prose["translation_ru"] + " [правка]")
    q0 = new["questions"][0]
    q0["text"] = q0["text"] + "（改）"
    old_correct = next(o["id"] for o in q0["options"] if o["is_correct"])
    other = next(o for o in q0["options"] if not o["is_correct"])
    for o in q0["options"]:
        o["is_correct"] = o["id"] == other["id"]
    other["text"] = other["text"] + "！"
    r = c.put(f"/api/admin/texts/{tid}", json=new)
    check("save: 200", r.status_code == 200 and r.json()["saved"], r.text[:300])
    after = c.get(f"/api/admin/texts/{tid}/edit").json()
    check("save: title, passage, translation stored", after["title"].endswith("(испр.)") and "編集《へんしゅう》テスト" in after["markup"]
          and after["translation_ru"].endswith("[правка]"))
    q_after = after["questions"][0]
    check("save: question text and correct answer changed",
          q_after["text"].endswith("（改）") and next(o for o in q_after["options"] if o["id"] == other["id"])["is_correct"]
          and not next(o for o in q_after["options"] if o["id"] == old_correct)["is_correct"])

    public = c.get(f"/api/texts/{tid}?user_id=editor-check")
    pj = public.json()
    check("public: shows edited title and passage", pj["title"].endswith("(испр.)") and "<ruby>編集<rt>へんしゅう</rt></ruby>テスト" in pj["content_html"])
    check("public: still no answer keys", not any(k in public.text for k in ('"is_correct"', '"explanation"', '"trap_type"', '"evidence_span_id"')))
    check("public: option tokens unchanged (same ids, same user)",
          sorted(o["id"] for q in pj["questions"] for o in q["options"]) == tokens_before)

    revs = c.get(f"/api/admin/texts/{tid}/revisions").json()["items"]
    check("revisions: one 'до правки' entry", len(revs) == 1 and revs[0]["note"] == "до правки" and revs[0]["title"] == prose["title"])
    r = c.post(f"/api/admin/texts/{tid}/revisions/{revs[0]['id']}/restore")
    check("restore: 200", r.status_code == 200, r.text[:200])
    restored = c.get(f"/api/admin/texts/{tid}/edit").json()
    check("restore: task back to original (title, passage, correct answer)",
          restored["title"] == prose["title"] and restored["markup"] == prose["markup"]
          and [o["is_correct"] for o in restored["questions"][0]["options"]] == [o["is_correct"] for o in prose["questions"][0]["options"]])
    check("restore: current version saved too", len(c.get(f"/api/admin/texts/{tid}/revisions").json()["items"]) == 2)
    check("restore: unknown revision -> 404", c.post(f"/api/admin/texts/{tid}/revisions/999999/restore").status_code == 404)

    # --- preview & furigana endpoints
    r = c.post("/api/admin/passage/preview", json={"mode": "markup", "markup": "新しい本《ほん》", "frame": {"head": "", "wrapped": True}})
    check("preview: markup -> html", r.status_code == 200 and "<ruby>本<rt>ほん</rt></ruby>" in r.json()["html"])
    r = c.post("/api/admin/passage/furigana", json={"mode": "markup", "markup": "新しい本です"})
    check("furigana endpoint: readings added", r.status_code == 200 and "新《あたら》しい本《ほん》" in r.json()["markup"], r.text)
    r = c.post("/api/admin/passage/preview", json={"mode": "html", "html": "<p onclick='x()'>a</p><script>b</script>"})
    check("preview: html sanitized with warning", r.status_code == 200 and r.json()["html"] == "<p>a</p>" and r.json()["warnings"])

    # --- flyer (html mode) save keeps content when unchanged
    if flyer:
        r = c.put(f"/api/admin/texts/{flyer['id']}", json=payload(flyer))
        check("html mode: unchanged save keeps passage identical",
              r.status_code == 200 and c.get(f"/api/admin/texts/{flyer['id']}/edit").json()["html"] == flyer["html"], r.text[:200])

    # --- admin key
    os.environ["ADMIN_TOKEN"] = "editor-key"
    check("key set: edit view 401 without header", c.get(f"/api/admin/texts/{tid}/edit").status_code == 401)
    check("key set: save 401 without header", c.put(f"/api/admin/texts/{tid}", json=payload(prose)).status_code == 401)
    check("key set: furigana 401 without header", c.post("/api/admin/passage/furigana", json={"mode": "markup", "markup": "本"}).status_code == 401)
    check("key set: with header 200", c.get(f"/api/admin/texts/{tid}/edit", headers={"X-Admin-Token": "editor-key"}).status_code == 200)
    os.environ.pop("ADMIN_TOKEN", None)

shutil.rmtree(TMP, ignore_errors=True)
print("\nALL PASSED" if not failed else f"\n{len(failed)} FAILED")
sys.exit(1 if failed else 0)
