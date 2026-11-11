"""
Multi-language gloss lookup for the pop-up dictionary (feat/i18n-switcher, sub-iteration 3).

Sources, in the order they are used:
  * app/data/dictionary_manual.txt   - glosses written by the project (word|en|uz). NOT third-party data.
                                       Needs review by a native speaker / @jlpt-expert.
  * app/data/jmdict_en.json          - optional compact index built by tools/build_jmdict_index.py from
                                       JMdict (EDRDG, CC BY-SA 4.0). English only. Absent until generated.
Readings come from the project dictionary (JLPT_DICTIONARY) or from JMdict, never invented.
Machine translation is NOT used anywhere.

Language rules (requested `lang`):
  en : JMdict gloss, else manual en.
  uz : manual uz, else English gloss flagged as fallback (`fallback: true`, `lang: "en"`).
  ja : there is no Japanese-definition source; reading and JLPT level only (`meaning: ""`).
The Russian request path (no `lang` / lang=ru) is untouched and lives in dictionary_service.lookup_word.
"""
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from app.services.dictionary_service import lookup_word

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MANUAL_PATH = DATA_DIR / "dictionary_manual.txt"
JMDICT_PATH = Path(os.getenv("DOKKAI_JMDICT_INDEX") or (DATA_DIR / "jmdict_en.json"))

SUPPORTED_LANGS = ("ru", "uz", "en", "ja")
JMDICT_ATTRIBUTION = (
    "Dictionary data from JMdict, copyright The Electronic Dictionary Research and Development Group, "
    "licensed under CC BY-SA 4.0: https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project"
)


@lru_cache(maxsize=1)
def _manual() -> Dict[str, Dict[str, str]]:
    entries: Dict[str, Dict[str, str]] = {}
    if not MANUAL_PATH.exists():
        return entries
    for line in MANUAL_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 3:
            continue
        word, en, uz = (p.strip() for p in parts)
        entries[word] = {"en": en, "uz": uz}
    return entries


@lru_cache(maxsize=1)
def _jmdict() -> Dict[str, Dict[str, str]]:
    """form (kanji or kana) -> {"r": reading, "g": english gloss}. Empty when the index is not generated."""
    if not JMDICT_PATH.exists():
        return {}
    try:
        data = json.loads(JMDICT_PATH.read_text(encoding="utf-8"))
        return data.get("forms", {})
    except (OSError, ValueError):
        return {}


def reload_data() -> None:
    """Drop the caches (tests swap DOKKAI_JMDICT_INDEX / data files)."""
    _manual.cache_clear()
    _jmdict.cache_clear()
    global JMDICT_PATH
    JMDICT_PATH = Path(os.getenv("DOKKAI_JMDICT_INDEX") or (DATA_DIR / "jmdict_en.json"))


@lru_cache(maxsize=1)
def _tokenizer():
    from janome.tokenizer import Tokenizer  # heavy import: only when a conjugated form must be resolved
    return Tokenizer()


def _candidates(query: str) -> List[str]:
    """The selection itself, then the dictionary form of its first token (食べました -> 食べる)."""
    out = [query]
    try:
        tokens = list(_tokenizer().tokenize(query))
        if tokens:
            base = tokens[0].base_form
            if base and base != "*" and base not in out:
                out.append(base)
    except Exception:  # tokenizer problems must never break a lookup
        pass
    return out


def jmdict_available() -> bool:
    return bool(_jmdict())


def lookup_word_i18n(query: str, lang: str) -> Optional[Dict[str, object]]:
    """Entry for the pop-up in `lang` (en / uz / ja), or None when nothing is known about the word."""
    if lang not in ("en", "uz", "ja"):
        return None
    q = (query or "").strip()
    if not q:
        return None

    base = lookup_word(q)  # project dictionary entry (authentic reading, level)
    if base and q not in (base["word"], base["reading"]):
        # lookup_word also returns *partial* matches (本当 -> 本, 学 -> 学生). The Russian path keeps that
        # historical behaviour (API contract); here a partial match would attach a wrong gloss, so it is dropped.
        base = None
    manual, jm = _manual(), _jmdict()

    def find(table, keys):
        for k in keys:
            if k in table:
                return k, table[k]
        return None, None

    keys = [q] + ([base["word"]] if base and base["word"] != q else [])
    mkey, mentry = find(manual, keys)
    jkey, jentry = find(jm, keys)
    if mentry is None and jentry is None:
        # not an exact hit: try the dictionary form of a conjugated selection
        extra = [c for c in _candidates(q) if c not in keys]
        mkey, mentry = find(manual, extra)
        jkey, jentry = find(jm, extra)

    matched = jkey or mkey
    if matched and (not base or base["word"] != matched):
        exact = lookup_word(matched)
        if exact and exact["word"] == matched:
            base = exact
    if base and (matched is None or matched == base["word"]):
        word, reading, level = base["word"], base["reading"], base["level"]
    else:
        word = matched or q
        reading = jentry["r"] if jentry else ""
        level = ""

    en = (jentry["g"] if jentry else None) or (mentry["en"] if mentry else None)
    en_source = "jmdict" if jentry else "manual"

    if lang == "ja":
        if not (base or jentry or mentry):
            return None
        return {"word": word, "reading": reading, "level": level, "meaning": "", "lang": "ja", "source": "none", "fallback": False}

    if lang == "uz":
        if mentry:
            return {"word": word, "reading": reading, "level": level, "meaning": mentry["uz"], "lang": "uz", "source": "manual", "fallback": False}
        if en:
            return {"word": word, "reading": reading, "level": level, "meaning": en, "lang": "en", "source": en_source, "fallback": True}
        return None

    if en:  # lang == "en"
        return {"word": word, "reading": reading, "level": level, "meaning": en, "lang": "en", "source": en_source, "fallback": False}
    return None
