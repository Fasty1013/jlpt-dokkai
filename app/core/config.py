"""Application-wide paths and constants (Step 8b)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = os.path.join(str(PROJECT_ROOT), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)


# Step 11d: key for the HMAC that shuffles answer options and issues opaque option tokens.
# MUST be set in production (Render env var SHUFFLE_SECRET); the order is stable only while it is unchanged.
_DEV_SHUFFLE_SECRET = "dokkai-dev-shuffle-secret-do-not-use-in-production"
SHUFFLE_SECRET = os.getenv("SHUFFLE_SECRET") or _DEV_SHUFFLE_SECRET
SHUFFLE_SECRET_IS_DEFAULT = not os.getenv("SHUFFLE_SECRET")
