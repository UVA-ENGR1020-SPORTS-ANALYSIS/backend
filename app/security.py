import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException


def require_admin_key(x_admin_key: Optional[str] = Header(default=None)) -> None:
    expected_key = os.getenv("ADMIN_API_KEY")
    if not expected_key:
        raise HTTPException(status_code=503, detail="Admin authorization is not configured")

    if not x_admin_key or not secrets.compare_digest(expected_key, x_admin_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
