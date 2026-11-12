"""Admin access: a shared secret in the ADMIN_TOKEN env var, sent as the X-Admin-Token header.

- ADMIN_TOKEN set: the header must match (constant-time compare), otherwise 401.
- ADMIN_TOKEN not set: admin endpoints are open only with DOKKAI_TEST_MODE=1 (local tests and
  parity tools keep working unchanged); in production they are closed (401).
The env is read on every call so tests can switch it without reloading modules.
"""
import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException, status

ADMIN_TOKEN_REQUIRED_DETAIL = "Требуется ключ администратора"


def admin_token_configured() -> bool:
    return bool(os.environ.get("ADMIN_TOKEN"))


def require_admin(x_admin_token: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get("ADMIN_TOKEN", "")
    if expected:
        if x_admin_token and hmac.compare_digest(x_admin_token.encode("utf-8"), expected.encode("utf-8")):
            return
    elif os.environ.get("DOKKAI_TEST_MODE") == "1":
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ADMIN_TOKEN_REQUIRED_DETAIL)
