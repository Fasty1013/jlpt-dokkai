"""Compatibility shim (Step 8b); removed in Step 9. Real module lives under app/."""
from app.services.dictionary_service import *  # noqa: F401,F403
from app.services.dictionary_service import lookup_word, get_authentic_hiragana  # noqa: F401
