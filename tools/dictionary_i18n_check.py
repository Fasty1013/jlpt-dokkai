"""
Checks for the multi-language pop-up dictionary (feat/i18n-switcher, sub-iteration 3).

  python tools/dictionary_i18n_check.py

 1. The manual glossary covers every word of the project dictionary and every vocabulary item of the texts in
    dokkai.db (read-only), with non-empty en and uz.
 2. Russian contract: lookup without lang / lang=ru returns exactly the historical keys.
 3. Language rules: en / uz / ja results, uz -> English fallback flag, ja has no meaning, unknown word -> 404,
    partial matches (本当 -> 本) are NOT used by the non-Russian path, conjugated forms resolve through Janome.
 4. JMdict path with a tiny jmdict-simplified fixture and tools/build_jmdict_index.py (builder + lookup).
 5. Anti-Cheat: the dictionary endpoints never expose answer fields.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from app.services import dictionary_i18n as di  # noqa: E402
from app.services.dictionary_service import JLPT_DICTIONARY  # noqa: E402
from main import app  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(name)


client = TestClient(app)

# 1. coverage of the manual glossary
manual = di._manual()
check("manual glossary has entries", len(manual) >= 300, str(len(manual)))
missing = [d["word"] for d in JLPT_DICTIONARY if d["word"] not in manual]
check("every project dictionary word has en+uz", not missing, str(missing[:5]))
db = ROOT / "dokkai.db"
if db.exists():
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    vocab = set()
    for (v,) in con.execute("select vocabulary_json from texts"):
        for it in (json.loads(v) if isinstance(v, str) else v) or []:
            if it.get("furigana"):
                vocab.add(it["word"])
    miss_v = sorted(w for w in vocab if w not in manual)
    check("every vocabulary item of the texts has en+uz", not miss_v, str(miss_v[:5]))
check("no empty en/uz", all(e["en"] and e["uz"] for e in manual.values()))

# 2. Russian contract unchanged
r = client.get("/api/dictionary/lookup", params={"q": "図書館"})
check("ru (no lang) 200", r.status_code == 200)
check("ru keys exactly word/reading/level/meaning", sorted(r.json()) == ["level", "meaning", "reading", "word"], str(r.json()))
check("ru meaning is Russian", r.json()["meaning"] == "библиотека")
r2 = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "ru"})
check("lang=ru identical to no lang", r2.json() == r.json())
check("ru partial match kept (本当 -> 本)", client.get("/api/dictionary/lookup", params={"q": "本当"}).json().get("word") == "本")

# 3. language rules (JMdict index disabled for this block)
os.environ["DOKKAI_JMDICT_INDEX"] = str(Path(tempfile.gettempdir()) / "does_not_exist_jmdict.json")
di.reload_data()
en = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "en"}).json()
check("en meaning", en["meaning"] == "library" and en["lang"] == "en" and not en["fallback"], str(en))
check("en reading from project dictionary", en["reading"] == "としょかん" and en["level"] == "N5")
uz = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "uz"}).json()
check("uz meaning", uz["meaning"] == "kutubxona" and uz["lang"] == "uz" and not uz["fallback"], str(uz))
ja = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "ja"}).json()
check("ja: reading+level, empty meaning", ja["meaning"] == "" and ja["reading"] == "としょかん" and ja["level"] == "N5", str(ja))
check("unknown word 404 (en)", client.get("/api/dictionary/lookup", params={"q": "猫", "lang": "en"}).status_code == 404)
check("bad lang 422", client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "xx"}).status_code == 422)
check("partial match not used for en (本当)", client.get("/api/dictionary/lookup", params={"q": "本当", "lang": "en"}).status_code == 404)
conj = client.get("/api/dictionary/lookup", params={"q": "食べました", "lang": "uz"}).json()
check("conjugated form resolves via Janome (食べました -> 食べる)", conj["word"] == "食べる" and conj["meaning"] == "yemoq, ovqatlanmoq", str(conj))

# 4. JMdict builder + lookup with a tiny fixture
fixture = {
    "version": "test", "dictDate": "2026-01-01",
    "words": [
        {"id": "1", "kanji": [{"text": "猫", "common": True}], "kana": [{"text": "ねこ", "common": True}],
         "sense": [{"gloss": [{"lang": "eng", "text": "cat"}], "misc": []}]},
        {"id": "2", "kanji": [], "kana": [{"text": "ありがとう", "common": True}],
         "sense": [{"gloss": [{"lang": "eng", "text": "thank you"}], "misc": []}]},
        {"id": "3", "kanji": [{"text": "図書館", "common": True}], "kana": [{"text": "としょかん", "common": True}],
         "sense": [{"gloss": [{"lang": "eng", "text": "LIBRARY-FROM-JMDICT"}], "misc": []}]},
    ],
}
with tempfile.TemporaryDirectory() as tmp:
    src, out = Path(tmp) / "jm.json", Path(tmp) / "jmdict_en.json"
    src.write_text(json.dumps(fixture, ensure_ascii=False), encoding="utf-8")
    res = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build_jmdict_index.py"), str(src), "--out", str(out)],
                         capture_output=True, text=True, encoding="utf-8")
    check("index builder runs", res.returncode == 0, res.stderr[-200:])
    os.environ["DOKKAI_JMDICT_INDEX"] = str(out)
    di.reload_data()
    check("jmdict index loaded", di.jmdict_available())
    cat = client.get("/api/dictionary/lookup", params={"q": "猫", "lang": "en"}).json()
    check("jmdict word outside the project dictionary (猫)", cat["meaning"] == "cat" and cat["reading"] == "ねこ" and cat["source"] == "jmdict", str(cat))
    cat_uz = client.get("/api/dictionary/lookup", params={"q": "猫", "lang": "uz"}).json()
    check("uz falls back to English and says so", cat_uz["fallback"] is True and cat_uz["lang"] == "en" and cat_uz["meaning"] == "cat", str(cat_uz))
    kana = client.get("/api/dictionary/lookup", params={"q": "ありがとう", "lang": "en"}).json()
    check("kana-only entry", kana["meaning"] == "thank you", str(kana))
    lib = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "en"}).json()
    check("en prefers JMdict over manual", lib["meaning"] == "LIBRARY-FROM-JMDICT" and lib["source"] == "jmdict", str(lib))
    lib_uz = client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "uz"}).json()
    check("uz keeps the manual gloss when present", lib_uz["meaning"] == "kutubxona" and lib_uz["source"] == "manual", str(lib_uz))
    ru_after = client.get("/api/dictionary/lookup", params={"q": "図書館"}).json()
    check("ru unaffected by JMdict", ru_after["meaning"] == "библиотека")

# 5. Anti-Cheat
FORBID = {"is_correct", "explanation", "trap_type", "evidence_span_id"}
body = json.dumps(client.get("/api/dictionary/lookup", params={"q": "図書館", "lang": "en"}).json())
check("no answer fields in dictionary responses", not any(k in body for k in FORBID))

os.environ.pop("DOKKAI_JMDICT_INDEX", None)
print("\nALL PASSED" if not fails else f"\n{len(fails)} FAILED: {fails}")
sys.exit(1 if fails else 0)
