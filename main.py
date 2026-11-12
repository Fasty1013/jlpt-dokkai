"""JLPT Dokkai Master - ASGI entry point (`uvicorn main:app`).

Thin composition root (Step 8b): application object, lifespan, middleware and routers.
Business logic lives in app/services, HTTP endpoints in app/routers.
"""
import logging
import os
import sys
from contextlib import asynccontextmanager

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.core.config import STATIC_DIR, SHUFFLE_SECRET_IS_DEFAULT
from app.core.database import engine, Base
from app.routers import (
    health, catalog, reading, dictionary, analysis, stream, reports, admin, admin_panel, pages,
)
from seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists and seed data is present on startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    from tools.migrations.add_stream_tables import migrate
    migrate()
    if SHUFFLE_SECRET_IS_DEFAULT:
        # The fallback key is public (repository source): anyone could undo the option shuffle.
        logging.getLogger("uvicorn.error").warning(
            "SHUFFLE_SECRET is not set: using the public development key. "
            "Set SHUFFLE_SECRET in production (Render > Environment)."
        )
    if not os.environ.get("ADMIN_TOKEN") and os.environ.get("DOKKAI_TEST_MODE") != "1":
        logging.getLogger("uvicorn.error").warning(
            "ADMIN_TOKEN is not set: the admin panel (/admin) and PDF import API are closed. "
            "Set ADMIN_TOKEN in Render > Environment to use them."
        )
    yield


app = FastAPI(
    title="JLPT Dokkai Master (読解トレーナー)",
    description="Exam-flow Japanese reading comprehension training with anti-cheat and deep analysis.",
    version="2.3.1",
    lifespan=lifespan
)


@app.middleware("http")
async def add_static_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/static/") or path in ("/", "/sw.js"):
        if "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


# Registration order is part of the public OpenAPI contract: keep it stable.
for _module in (health, catalog, reading, dictionary, analysis, stream, reports, admin, admin_panel):
    app.include_router(_module.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(pages.router)

# Backward-compatible re-exports (test_api.py and tools import endpoint functions from main)
from app.routers.catalog import list_texts  # noqa: E402,F401
from app.routers.reading import get_text_for_reading  # noqa: E402,F401
from app.routers.analysis import submit_and_analyze  # noqa: E402,F401
from app.routers.dictionary import dictionary_lookup  # noqa: E402,F401
