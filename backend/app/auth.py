"""
Authentication for FastAPI.

Supports optional MATE_API_KEY and Supabase JWT (Bearer) for user identity.
When callers authenticate with a shared API key, an optional ``X-Client-User-Id``
header (browser UUID from localStorage) scopes jobs per browser session.
"""

from __future__ import annotations

import re

import structlog
from fastapi import HTTPException, Header, Query

from app.config import get_settings

logger = structlog.get_logger()

_CLIENT_USER_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_SHARED_IDENTITIES = frozenset({"", "anonymous", "api-user"})


def _extract_bearer(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return ""


def _looks_like_jwt(token: str) -> bool:
    return token.count(".") == 2 and not token.startswith("mate_")


def _verify_supabase_jwt(token: str) -> str | None:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        return None
    try:
        import jwt

        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        sub = payload.get("sub")
        if sub:
            return str(sub)
    except Exception as e:
        logger.warning("auth_jwt_rejected", error=str(e))
    return None


def _resolve_client_user_id(raw: str | None) -> str | None:
    if not raw:
        return None
    candidate = raw.strip()
    if _CLIENT_USER_RE.match(candidate):
        return candidate
    return None


def _apply_client_scope(user_id: str, client_user_id: str | None) -> str:
    """Map shared-key identity to a per-browser UUID when provided."""
    if user_id == "api-user":
        scoped = _resolve_client_user_id(client_user_id)
        if scoped:
            return scoped
    if user_id == "anonymous" and get_settings().environment != "production":
        scoped = _resolve_client_user_id(client_user_id)
        if scoped:
            return scoped
    return user_id


def _resolve_user_from_token(token: str) -> str | None:
    """Return user id from JWT or API key match."""
    if not token:
        return None
    if _looks_like_jwt(token):
        return _verify_supabase_jwt(token)
    settings = get_settings()
    if settings.mate_api_key and token == settings.mate_api_key:
        return "api-user"
    return None


def resolve_request_user_id(
    *,
    token: str,
    client_user_id: str | None = None,
) -> str | None:
    user_id = _resolve_user_from_token(token)
    if not user_id:
        return None
    return _apply_client_scope(user_id, client_user_id)


def is_shared_identity(user_id: str) -> bool:
    return user_id in _SHARED_IDENTITIES


async def get_current_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
    x_client_user_id: str | None = Header(default=None, alias="X-Client-User-Id"),
) -> str:
    """
    Return user id for the request.

    Priority: X-API-Key / Bearer JWT / Bearer API key, then optional client scope.
    """
    settings = get_settings()
    token = (x_api_key or "").strip() or _extract_bearer(authorization)

    user_id = resolve_request_user_id(token=token, client_user_id=x_client_user_id)
    if user_id:
        return user_id

    if not settings.mate_api_key:
        if settings.environment == "production":
            raise HTTPException(
                status_code=503,
                detail="API key not configured (set MATE_API_KEY in production)",
            )
        return _apply_client_scope("anonymous", x_client_user_id)

    logger.warning("auth_api_key_rejected", has_header=bool(token))
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API key (use X-API-Key or Authorization: Bearer)",
    )


async def get_optional_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
    x_client_user_id: str | None = Header(default=None, alias="X-Client-User-Id"),
) -> str | None:
    """Like get_current_user but returns None when no valid credentials."""
    token = (x_api_key or "").strip() or _extract_bearer(authorization)
    return resolve_request_user_id(token=token, client_user_id=x_client_user_id)


async def require_stream_access(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str = Header(default=""),
    api_key: str | None = Query(
        default=None,
        description="Optional API key for SSE clients that cannot set headers (discouraged; prefer Next.js proxy).",
    ),
    client_user_id: str | None = Query(
        default=None,
        description="Browser-scoped user id for SSE/EventSource (cannot send custom headers).",
    ),
    x_client_user_id: str | None = Header(default=None, alias="X-Client-User-Id"),
) -> str:
    """
    Same rules as get_current_user, but also accepts ``api_key`` and
    ``client_user_id`` query params for EventSource-only clients.
    """
    settings = get_settings()
    token = (
        (x_api_key or "").strip()
        or _extract_bearer(authorization)
        or (api_key or "").strip()
    )
    scoped_client = x_client_user_id or client_user_id

    user_id = resolve_request_user_id(token=token, client_user_id=scoped_client)
    if user_id:
        return user_id

    if not settings.mate_api_key:
        if settings.environment == "production":
            raise HTTPException(
                status_code=503,
                detail="API key not configured (set MATE_API_KEY in production)",
            )
        return _apply_client_scope("anonymous", scoped_client)

    logger.warning("stream_auth_rejected", has_token=bool(token))
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API key for stream (X-API-Key, Bearer, or api_key query)",
    )
