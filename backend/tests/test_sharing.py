"""
Tests for sharing and collaboration — access control, password, expiry, school scoping.
"""

import pytest
from datetime import datetime, timedelta

from app.sharing.router import (
    ShareRequest,
    _hash_password,
    _check_link_valid,
    _shared_links,
    _shared_resources,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clean_stores():
    """Clear in-memory stores before each test."""
    _shared_links.clear()
    _shared_resources.clear()
    yield
    _shared_links.clear()
    _shared_resources.clear()


# ---------------------------------------------------------------------------
# Tests: Password hashing
# ---------------------------------------------------------------------------
class TestPasswordHashing:
    def test_consistent_hashing(self):
        h1 = _hash_password("test123")
        h2 = _hash_password("test123")
        assert h1 == h2

    def test_different_passwords_different_hash(self):
        h1 = _hash_password("test123")
        h2 = _hash_password("test456")
        assert h1 != h2


# ---------------------------------------------------------------------------
# Tests: Link validation
# ---------------------------------------------------------------------------
class TestLinkValidation:
    def test_valid_link(self):
        link = {"expires_at": None, "max_views": None, "view_count": 0}
        valid, error = _check_link_valid(link)
        assert valid is True
        assert error == ""

    def test_expired_link(self):
        link = {
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "max_views": None,
            "view_count": 0,
        }
        valid, error = _check_link_valid(link)
        assert valid is False
        assert "expired" in error.lower()

    def test_future_expiry_valid(self):
        link = {
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "max_views": None,
            "view_count": 0,
        }
        valid, error = _check_link_valid(link)
        assert valid is True

    def test_max_views_exceeded(self):
        link = {
            "expires_at": None,
            "max_views": 5,
            "view_count": 5,
        }
        valid, error = _check_link_valid(link)
        assert valid is False
        assert "views" in error.lower()

    def test_max_views_not_exceeded(self):
        link = {
            "expires_at": None,
            "max_views": 5,
            "view_count": 3,
        }
        valid, error = _check_link_valid(link)
        assert valid is True

    def test_no_limits(self):
        link = {
            "expires_at": None,
            "max_views": None,
            "view_count": 1000,
        }
        valid, error = _check_link_valid(link)
        assert valid is True


# ---------------------------------------------------------------------------
# Tests: ShareRequest validation
# ---------------------------------------------------------------------------
class TestShareRequest:
    def test_valid_request(self):
        req = ShareRequest(
            resource_type="generation",
            resource_id="abc123",
        )
        assert req.resource_type == "generation"

    def test_with_password(self):
        req = ShareRequest(
            resource_type="generation",
            resource_id="abc123",
            password="secret",
            expires_hours=168,
        )
        assert req.password == "secret"
        assert req.expires_hours == 168

    def test_with_max_views(self):
        req = ShareRequest(
            resource_type="exercise_set",
            resource_id="xyz789",
            max_views=10,
        )
        assert req.max_views == 10


# ---------------------------------------------------------------------------
# Integration tests (would use TestClient in production)
# ---------------------------------------------------------------------------
class TestSharingIntegration:
    """These tests validate the logic without running the full API server."""

    def test_create_and_validate_link(self):
        import secrets

        token = secrets.token_urlsafe(24)
        link = {
            "token": token,
            "resource_type": "generation",
            "resource_id": "gen-001",
            "password_hash": None,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "max_views": 100,
            "view_count": 0,
            "allow_download": True,
            "allow_clone": True,
        }
        _shared_links[token] = link

        valid, _ = _check_link_valid(link)
        assert valid is True

        # Simulate views
        link["view_count"] = 100
        valid, error = _check_link_valid(link)
        assert valid is False

    def test_password_protected_link(self):
        link = {
            "password_hash": _hash_password("mypassword"),
            "expires_at": None,
            "max_views": None,
            "view_count": 0,
        }

        # Correct password
        assert _hash_password("mypassword") == link["password_hash"]

        # Wrong password
        assert _hash_password("wrongpassword") != link["password_hash"]
