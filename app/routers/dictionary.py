from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services.dictionary_i18n import lookup_word_i18n
from app.services.dictionary_service import lookup_word

router = APIRouter()


@router.get("/api/dictionary/lookup", tags=["Dictionary"])
def dictionary_lookup(
    q: str = Query(..., min_length=1, max_length=50),
    lang: Optional[str] = Query(
        None,
        pattern="^(ru|uz|en|ja)$",
        description="Gloss language. Omitted or ru: Russian meaning (unchanged contract). "
        "en: JMdict / manual gloss. uz: manual gloss, English fallback (fallback=true). "
        "ja: reading and level only (no Japanese-definition source).",
    ),
):
    """
    Lookup endpoint for Yomichan-style popup dictionary.
    Returns reading, JLPT level, and the meaning in the requested language (Russian by default).
    """
    if lang in (None, "ru"):
        result = lookup_word(q)
    else:
        result = lookup_word_i18n(q, lang)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return result
