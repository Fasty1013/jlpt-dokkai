import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

from app.core.config import STATIC_DIR

router = APIRouter()


@router.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "JLPT Dokkai API running. Frontend static/index.html not found."}


@router.get("/admin", include_in_schema=False)
def serve_admin():
    """Admin panel page (data comes from /api/admin/*, protected by ADMIN_TOKEN)."""
    admin_path = os.path.join(STATIC_DIR, "admin", "index.html")
    if not os.path.exists(admin_path):
        raise HTTPException(status_code=404, detail="Admin page not found")
    return FileResponse(admin_path, headers={
        "Cache-Control": "no-cache, must-revalidate",
        "X-Robots-Tag": "noindex, nofollow",
    })


@router.get("/sw.js")
def serve_service_worker(request: Request, version: Optional[str] = None):
    sw_path = os.path.join(STATIC_DIR, "sw.js")
    if not os.path.exists(sw_path):
        raise HTTPException(status_code=404, detail="Service worker not found")

    # In production and normal operation, version query override is strictly disabled.
    # It is ONLY permitted during automated tests when DOKKAI_TEST_MODE=1 is explicitly set.
    is_test_mode = os.environ.get("DOKKAI_TEST_MODE") == "1"

    if version and is_test_mode:
        import re
        safe_version = re.sub(r"[^a-zA-Z0-9.-]", "", version)[:30]
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r"const CACHE_VERSION = '[^']+';", f"const CACHE_VERSION = '{safe_version}';", content)
        return Response(
            content=content,
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Service-Worker-Allowed": "/"
            }
        )

    return FileResponse(
        sw_path,
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Service-Worker-Allowed": "/"
        }
    )
