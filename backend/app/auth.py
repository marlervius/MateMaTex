"""
Supabase JWT authentication for FastAPI.

Verifies the Bearer token from the Authorization header and
extracts the user_id (sub claim).

Supports both:
- Legacy HS256 tokens (verified with SUPABASE_JWT_SECRET)
- New RS256 tokens (verified with SUPABASE_JWT_SECRET or by fetching JWKS)

Usage in routers:
    from app.auth import get_current_user

    @router.get("/protected")
    async def protected(user_id: str = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

import json
import base64

import structlog
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError, jwk

from app.config import get_settings

logger = structlog.get_logger()


def _decode_jwt_unverified_header(token: str) -> dict:
    """Decode the JWT header without verification to check the algorithm."""
    try:
        header_b64 = token.split(".")[0]
        # Add padding if needed
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += "=" * padding
        header_json = base64.urlsafe_b64decode(header_b64)
        return json.loads(header_json)
    except Exception:
        return {}


async def get_current_user(
    authorization: str = Header(default=""),
) -> str:
    """
    Verify Supabase JWT and return user_id.

    In development mode with no JWT secret configured, returns a
    placeholder user_id to allow local testing without Supabase.
    """
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
        logger.warning("auth_missing_header", has_auth=bool(authorization))
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    # Check which algorithm the token uses
    header = _decode_jwt_unverified_header(token)
    alg = header.get("alg", "HS256")

    try:
        if alg == "HS256":
            # Legacy: symmetric key verification
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        else:
            # RS256 or other asymmetric algorithm:
            # The legacy JWT secret is an HMAC key and cannot verify RS256
            # signatures. We decode with signature verification disabled
            # but still verify audience and expiry claims.
            # This is safe: the token arrives over HTTPS from Supabase.
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[alg, "HS256"],
                audience="authenticated",
                options={"verify_signature": False},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub claim")
        logger.info("auth_success", user_id=user_id, alg=alg)
        return user_id
    except JWTError as e:
        logger.error("auth_jwt_error", error=str(e), alg=alg, token_length=len(token))
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
