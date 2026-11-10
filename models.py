"""Compatibility shim (Step 8b); removed in Step 9. Real module lives under app/."""
from app.models import *  # noqa: F401,F403
