"""Compatibility shim (Step 8b); removed in Step 9. Real module lives under app/."""
from app.core.database import *  # noqa: F401,F403
from app.core.database import DATABASE_URL, engine, SessionLocal, Base, get_db  # noqa: F401
