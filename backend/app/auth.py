"""
Supabase JWT authentication for FastAPI.

Verifies the Bearer token from the Authorization header and
extracts the user_id (sub claim).

Usage in routers:
    from app.auth import get_current_user

    @router.get("/protected")
    async def protected(user_id: str = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

from app.config import get_settings


async def get_current_user(
    authorization: str = Header(default=""),
) -> str:
    """
    Verify Supabase JWT and return user_id.

    In development mode with no JWT secret configured, returns a
    placeholder user_id to allow local testing without Supabase.
    """
    import structlog
    logger = structlog.get_logger()

    settings = get_settings()

    # Development fallback: skip auth if no JWT secret configured
    if not settings.supabase_jwt_secret and settings.environment == "development":
        return "dev-user-00000000"

    if not settings.supabase_jwt_secret:
        logger.error("auth_no_jwt_secret", environment=settings.environment)
        raise HTTPException(
            status_code=401,
            detail="Server misconfiguration: JWT secret not set",
        )

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("auth_missing_header", has_auth=bool(authorization), starts_with_bearer=authorization[:10] if authorization else "")
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub claim")
        logger.info("auth_success", user_id=user_id)
        return user_id
    except JWTError as e:
        logger.error("auth_jwt_error", error=str(e), token_length=len(token), secret_length=len(settings.supabase_jwt_secret))
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {e}",
        )


async def get_optional_user(
    authorization: str = Header(default=""),
) -> str | None:
    """
    Like get_current_user but returns None instead of raising
    for unauthenticated requests (useful for public endpoints).
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
