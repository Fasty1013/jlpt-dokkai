import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.core.database import get_db

router = APIRouter()


@router.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Healthcheck endpoint for Render and uptime monitoring."""
    text_count = db.query(models.Text).count()
    return {
        "status": "ok",
        "database": "connected",
        "texts_count": text_count
    }


@router.get("/api/version", tags=["Health"])
def version_info():
    """Version and build metadata endpoint for QA synchronization (no secrets)."""
    commit_sha = os.getenv("RENDER_GIT_COMMIT", "")
    if not commit_sha:
        try:
            import subprocess
            commit_sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                text=True,
                timeout=1
            ).strip()
        except Exception:
            commit_sha = "unknown"

    return {
        "version": "2.1.0",
        "commit": commit_sha,
        "env": os.getenv("ENV", os.getenv("APP_ENV", "development")),
        "database_backend": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgres") else "sqlite"
    }
