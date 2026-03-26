"""
Authentication for FastAPI.

No external auth provider: by default all requests are accepted and a stable
anonymous user id is returned. Optionally set MATE_API_KEY to require
``X-API-Key: <key>`` or ``Authorization: Bearer <key>`` on protected routes.
"""

from __future__ import annotations

import structlog
from fastapi import HTTPException, Header, Query

from app.config import get_settings

logger = structlog.get_logger()


def _extract_bearer(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return ""


async def get_current_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
) -> str:
    """
    Return user id for the request.

    - If MATE_API_KEY is not set: always ``anonymous`` (no headers required).
    - If MATE_API_KEY is set: require matching X-API-Key or Bearer token.
    """
    settings = get_settings()
    if not settings.mate_api_key:
        return "anonymous"

    token = (x_api_key or "").strip() or _extract_bearer(authorization)
    if not token or token != settings.mate_api_key:
        logger.warning("auth_api_key_rejected", has_header=bool(token))
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key (use X-API-Key or Authorization: Bearer)",
        )
    return "api-user"


async def get_optional_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
) -> str | None:
    """
    Like get_current_user but returns None when no valid key is provided
    (only meaningful when MATE_API_KEY is set).
    """
    settings = get_settings()
    if not settings.mate_api_key:
        return None
    token = (x_api_key or "").strip() or _extract_bearer(authorization)
    if token and token == settings.mate_api_key:
        return "api-user"
    return None


async def require_stream_access(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
    api_key: str | None = Query(
        default=None,
        description="Optional API key for SSE clients that cannot set headers (discouraged; prefer Next.js proxy).",
    ),
) -> str:
    """
    Same rules as get_current_user, but also accepts ``api_key`` query param
    for EventSource-only clients. Prefer server-side proxy with X-API-Key.
    """
    settings = get_settings()
    if not settings.mate_api_key:
        return "anonymous"

    token = (
        (x_api_key or "").strip()
        or _extract_bearer(authorization)
        or (api_key or "").strip()
    )
    if not token or token != settings.mate_api_key:
        logger.warning("stream_auth_rejected", has_token=bool(token))
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key for stream (X-API-Key, Bearer, or api_key query)",
        )
    return "api-user"
