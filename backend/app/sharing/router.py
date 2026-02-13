"""
Sharing API — create and resolve shareable links.

Supports: password protection, expiry dates, view limits, cloning.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user, get_optional_user

logger = structlog.get_logger()

router = APIRouter(prefix="/sharing", tags=["sharing"])


# ---------------------------------------------------------------------------
# In-memory store (replace with PostgreSQL in production)
# ---------------------------------------------------------------------------
_shared_links: dict[str, dict] = {}
_shared_resources: dict[str, dict] = {}  # resource_id → resource data


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ShareRequest(BaseModel):
    resource_type: str = Field(
        ...,
        description="'generation', 'exercise_set', or 'folder'",
    )
    resource_id: str = Field(..., description="ID of the resource to share")
    password: str | None = Field(None, description="Optional password protection")
    expires_hours: int | None = Field(
        None,
        ge=1,
        le=8760,
        description="Hours until expiry (max 1 year)",
    )
    max_views: int | None = Field(
        None,
        ge=1,
        description="Maximum number of views",
    )
    allow_download: bool = True
    allow_clone: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "resource_type": "generation",
                "resource_id": "abc123",
                "password": "hemmelighet",
                "expires_hours": 168,
            }
        }


class ShareResponse(BaseModel):
    success: bool
    token: str = ""
    share_url: str = ""
    expires_at: str | None = None
    error: str = ""


class SharedResourceResponse(BaseModel):
    success: bool
    resource_type: str = ""
    resource_id: str = ""
    content: dict = {}
    allow_download: bool = True
    allow_clone: bool = True
    error: str = ""


class CloneResponse(BaseModel):
    success: bool
    new_resource_id: str = ""
    error: str = ""


class VerifyPasswordRequest(BaseModel):
    password: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _check_link_valid(link: dict) -> tuple[bool, str]:
    """Check if a shared link is still valid. Returns (valid, error_message)."""
    # Check expiry
    if link.get("expires_at"):
        expires = datetime.fromisoformat(link["expires_at"])
        if datetime.now() > expires:
            return False, "Link has expired"

    # Check view limit
    if link.get("max_views") is not None:
        if link["view_count"] >= link["max_views"]:
            return False, "Maximum views reached"

    return True, ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=ShareResponse,
    summary="Create a shareable link for a resource",
)
async def create_share(req: ShareRequest, user_id: str = Depends(get_current_user)) -> ShareResponse:
    """
    Create a shareable link with optional password, expiry, and view limits.
    """
    token = secrets.token_urlsafe(24)

    link_data = {
        "id": uuid.uuid4().hex,
        "token": token,
        "resource_type": req.resource_type,
        "resource_id": req.resource_id,
        "password_hash": _hash_password(req.password) if req.password else None,
        "expires_at": (
            (datetime.now() + timedelta(hours=req.expires_hours)).isoformat()
            if req.expires_hours
            else None
        ),
        "max_views": req.max_views,
        "view_count": 0,
        "allow_download": req.allow_download,
        "allow_clone": req.allow_clone,
        "created_at": datetime.now().isoformat(),
    }

    _shared_links[token] = link_data

    logger.info(
        "share_created",
        token=token[:8] + "...",
        resource_type=req.resource_type,
        has_password=req.password is not None,
        expires_hours=req.expires_hours,
    )

    return ShareResponse(
        success=True,
        token=token,
        share_url=f"/shared/{token}",
        expires_at=link_data["expires_at"],
    )


@router.get(
    "/{token}",
    response_model=SharedResourceResponse,
    summary="Access a shared resource by token",
)
async def get_shared(token: str, password: str | None = None) -> SharedResourceResponse:
    """
    Access a shared resource. Checks password and expiry.
    """
    link = _shared_links.get(token)
    if not link:
        raise HTTPException(404, "Shared link not found")

    # Validate
    valid, error = _check_link_valid(link)
    if not valid:
        raise HTTPException(410, error)

    # Check password
    if link["password_hash"]:
        if not password:
            raise HTTPException(401, "Password required")
        if _hash_password(password) != link["password_hash"]:
            raise HTTPException(403, "Incorrect password")

    # Increment view count
    link["view_count"] += 1

    # Get resource (in production, fetch from database)
    resource = _shared_resources.get(link["resource_id"], {})

    return SharedResourceResponse(
        success=True,
        resource_type=link["resource_type"],
        resource_id=link["resource_id"],
        content=resource,
        allow_download=link["allow_download"],
        allow_clone=link["allow_clone"],
    )


@router.post(
    "/{token}/clone",
    response_model=CloneResponse,
    summary="Clone a shared resource to own account",
)
async def clone_shared(token: str, user_id: str = Depends(get_current_user)) -> CloneResponse:
    """Clone a shared resource to the authenticated user's account."""
    link = _shared_links.get(token)
    if not link:
        raise HTTPException(404, "Shared link not found")

    if not link.get("allow_clone", True):
        raise HTTPException(403, "Cloning not allowed for this shared resource")

    valid, error = _check_link_valid(link)
    if not valid:
        raise HTTPException(410, error)

    # In production: deep-copy the resource and assign to current user
    new_id = uuid.uuid4().hex
    original = _shared_resources.get(link["resource_id"], {})
    _shared_resources[new_id] = {**original, "id": new_id, "cloned_from": link["resource_id"]}

    logger.info("resource_cloned", original=link["resource_id"], new_id=new_id)

    return CloneResponse(success=True, new_resource_id=new_id)
