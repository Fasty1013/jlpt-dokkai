#!/usr/bin/env python3
"""Build content/open/n*.json from authoring drafts in content/open/src/*.json.

Drafts hold the passage as editor markup (`body_markup`: paragraphs separated by a
blank line, [ev-qN]…[/ev-qN] evidence marks, optional 漢字《かな》 readings). Furigana for
every kanji without an explicit reading comes from the janome tokenizer
(app.services.passage_markup.add_missing_furigana) — never from a language model.

Output records follow content/schema.md plus:
  source_type  = "open_adapted"
  source_note  = short attribution line shown in the exercise badge
  attribution  = {source, work, author, url, revision, license, license_url, changes}

Usage:  python tools/build_open_content.py [--check]
  --check  build in memory and validate, do not write files
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.services.passage_markup import add_missing_furigana, markup_to_html  # noqa: E402
from validate_content import validate_text_record  # noqa: E402

SRC_DIR = ROOT / "content" / "open" / "src"
OUT_DIR = ROOT / "content" / "open"
LEVELS = ["N5", "N4", "N3", "N2", "N1"]
REQUIRED_ATTR = ["source", "work", "author", "url", "license", "license_url", "changes"]
SOURCE_LABEL = {"wikipedia_ja": "Wikipedia日本語版", "aozora": "青空文庫"}


def source_note(attr: dict) -> str:
    label = SOURCE_LABEL.get(attr["source"], attr["source"])
    lic = "パブリックドメイン" if attr["license"].lower().startswith("public domain") else attr["license"]
    if attr["source"] == "aozora":
        return f"出典：{attr['author'].split('（')[0]}「{attr['work']}」（{label}・{lic}・改変）"
    return f"出典：{label}「{attr['work']}」（{lic}・改変）"


def build_record(draft: dict) -> dict:
    attr = draft["attribution"]
    missing = [k for k in REQUIRED_ATTR if not attr.get(k)]
    if missing:
        raise ValueError(f"[{draft['slug']}] attribution: нет полей {missing}")
    body_html = markup_to_html(add_missing_furigana(draft["body_markup"]))
    rec = {
        "slug": draft["slug"],
        "level": draft["level"],
        "category": draft["category"],
        "title": draft["title"],
        "source_type": "open_adapted",
        "source_note": source_note(attr),
        "recommended_time_min": draft["recommended_time_min"],
        "body_html": body_html,
        "translation_ru": draft["translation_ru"],
        "vocabulary": draft.get("vocabulary", []),
        "needs_manual_review": draft.get("needs_manual_review", []),
        "attribution": attr,
        "questions": draft["questions"],
    }
    return rec


def main() -> int:
    check_only = "--check" in sys.argv
    drafts = []
    for p in sorted(SRC_DIR.glob("*.json")):
        drafts.extend(json.loads(p.read_text(encoding="utf-8")))
    by_level = {lv: [] for lv in LEVELS}
    seen, errors = set(), []
    for d in drafts:
        if "-open-" not in d["slug"]:
            errors.append(f"[{d['slug']}] slug должен содержать '-open-'")
        try:
            rec = build_record(d)
        except Exception as e:  # markup / attribution errors
            errors.append(f"[{d.get('slug')}] {e}")
            continue
        errors.extend(validate_text_record(rec, "content/open", seen))
        by_level[rec["level"]].append(rec)
    if errors:
        print("ОШИБКИ:")
        for e in errors:
            print("  •", e)
        return 1
    for lv in LEVELS:
        recs = sorted(by_level[lv], key=lambda r: r["slug"])
        print(f"{lv}: {len(recs)} текстов, {sum(len(r['questions']) for r in recs)} вопросов")
        if not check_only:
            (OUT_DIR / f"{lv.lower()}.json").write_text(
                json.dumps(recs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("OK" + (" (только проверка)" if check_only else f" → {OUT_DIR.relative_to(ROOT)}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
