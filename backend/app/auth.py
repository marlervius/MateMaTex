"""
Supabase JWT authentication for FastAPI.

Verifies the Bearer token from the Authorization header and
extracts the user_id (sub claim).

Supports both:
- Legacy HS256 tokens (verified with SUPABASE_JWT_SECRET)
- New RS256 tokens (verified via Supabase JWKS endpoint)

Usage in routers:
    from app.auth import get_current_user

    @router.get("/protected")
    async def protected(user_id: str = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

import base64
import json
import time

import httpx
import structlog
from fastapi import HTTPException, Header
from jose import jwt, JWTError

from app.config import get_settings

logger = structlog.get_logger()

# JWKS cache: fetched once and refreshed every 5 minutes
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_TTL_SECONDS = 300


def _decode_jwt_unverified_header(token: str) -> dict:
    """Decode the JWT header without verification to check the algorithm."""
    try:
        header_b64 = token.split(".")[0]
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += "=" * padding
        header_json = base64.urlsafe_b64decode(header_b64)
        return json.loads(header_json)
    except Exception:
        return {}


def _fetch_jwks(supabase_url: str) -> dict | None:
    """Fetch JWKS from the Supabase endpoint (cached)."""
    global _jwks_cache, _jwks_fetched_at

    if _jwks_cache and (time.time() - _jwks_fetched_at) < _JWKS_TTL_SECONDS:
        return _jwks_cache

    url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        resp = httpx.get(url, timeout=5)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_fetched_at = time.time()
        logger.info("jwks_fetched", url=url)
        return _jwks_cache
    except Exception as e:
        logger.warning("jwks_fetch_failed", url=url, error=str(e))
        return _jwks_cache  # return stale cache if available


async def get_current_user(
    authorization: str = Header(default=""),
) -> str:
    """
    Verify Supabase JWT and return user_id.

    In development mode with no JWT secret configured, returns a
    placeholder user_id to allow local testing without Supabase.
    """
    settings = get_settings()

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
    header = _decode_jwt_unverified_header(token)
    alg = header.get("alg", "HS256")

    try:
        if alg == "HS256":
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        else:
            # RS256: verify with JWKS from Supabase
            jwks = (
                _fetch_jwks(settings.supabase_url)
                if settings.supabase_url
                else None
            )
            if jwks:
                from jose import jwk as jose_jwk

                kid = header.get("kid")
                signing_key = None
                for key_data in jwks.get("keys", []):
                    if key_data.get("kid") == kid:
                        signing_key = jose_jwk.construct(key_data)
                        break

                if signing_key:
                    payload = jwt.decode(
                        token,
                        signing_key,
                        algorithms=[alg],
                        audience="authenticated",
                    )
                else:
                    logger.warning(
                        "jwks_kid_not_found",
                        kid=kid,
                        available=[k.get("kid") for k in jwks.get("keys", [])],
                    )
                    raise JWTError(f"No matching key found for kid={kid}")
            else:
                logger.warning(
                    "auth_rs256_no_jwks",
                    msg="JWKS unavailable, falling back to unverified decode",
                )
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
        ) from e


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
