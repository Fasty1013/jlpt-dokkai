from fastapi import APIRouter, HTTPException, Query, status

from app.services.dictionary_service import lookup_word

router = APIRouter()


@router.get("/api/dictionary/lookup", tags=["Dictionary"])
def dictionary_lookup(q: str = Query(..., min_length=1, max_length=50)):
    """
    Lookup endpoint for Yomichan-style popup dictionary.
    Returns reading, JLPT level, and Russian translation.
    """
    result = lookup_word(q)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return result
