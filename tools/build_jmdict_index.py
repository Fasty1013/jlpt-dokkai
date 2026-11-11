"""
Build the compact JMdict English index used by app/services/dictionary_i18n.py.

Input : a jmdict-simplified JSON file (https://github.com/scriptin/jmdict-simplified, release asset
        jmdict-eng-*.json or jmdict-eng-common-*.json, unzipped).
Output: app/data/jmdict_en.json  ->  {"meta": {...}, "forms": {"<kanji or kana form>": {"r": reading, "g": gloss}}}

JMdict is (c) The Electronic Dictionary Research and Development Group, licensed CC BY-SA 4.0
(https://www.edrdg.org/edrdg/licence.html). The generated file is a derivative work and stays under CC BY-SA 4.0.

Usage:  python tools/build_jmdict_index.py path/to/jmdict-eng-common-3.6.2.json [--out app/data/jmdict_en.json]
Entries with a kanji form are indexed by every kanji form and (only when the entry is usually written in kana,
or has no kanji) by its kana forms. When several entries share a form, `common` ones win, then the first one.
"""
import argparse
import json
import sys
from pathlib import Path

MAX_SENSES = 3
MAX_GLOSSES_PER_SENSE = 3


def entry_gloss(entry):
    parts = []
    for sense in entry.get("sense", [])[:MAX_SENSES]:
        gl = [g["text"] for g in sense.get("gloss", []) if g.get("lang", "eng") == "eng"][:MAX_GLOSSES_PER_SENSE]
        if gl:
            parts.append(", ".join(gl))
    return "; ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "app" / "data" / "jmdict_en.json"))
    args = ap.parse_args()
    data = json.loads(Path(args.src).read_text(encoding="utf-8"))
    forms = {}
    rank = {}  # form -> 0 common, 1 other (lower wins)

    def put(form, reading, gloss, common):
        r = 0 if common else 1
        if form not in forms or r < rank[form]:
            forms[form] = {"r": reading, "g": gloss}
            rank[form] = r

    for e in data["words"]:
        gloss = entry_gloss(e)
        if not gloss or not e.get("kana"):
            continue
        reading = e["kana"][0]["text"]
        common_any = any(k.get("common") for k in e.get("kanji", [])) or any(k.get("common") for k in e["kana"])
        for k in e.get("kanji", []):
            put(k["text"], reading, gloss, bool(k.get("common")))
        usually_kana = any("uk" in s.get("misc", []) for s in e.get("sense", [])) or not e.get("kanji")
        if usually_kana:
            for k in e["kana"]:
                put(k["text"], k["text"], gloss, bool(k.get("common")) or common_any)
    meta = {
        "source": "JMdict (EDRDG), via jmdict-simplified",
        "license": "CC BY-SA 4.0",
        "version": data.get("version"),
        "dictDate": data.get("dictDate"),
        "entries": len(data["words"]),
        "forms": len(forms),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"meta": meta, "forms": forms}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(forms)} forms from {len(data['words'])} entries -> {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
