"""Tests for auth client-user scoping."""

from app.auth import is_shared_identity, resolve_request_user_id


def test_shared_identity_detection():
    assert is_shared_identity("api-user")
    assert is_shared_identity("anonymous")
    assert not is_shared_identity("550e8400-e29b-41d4-a716-446655440000")


def test_api_key_scoped_to_client_uuid():
    uid = resolve_request_user_id(
        token="secret-key",
        client_user_id="550e8400-e29b-41d4-a716-446655440000",
    )
    assert uid is None  # token must match configured key

    from app.config import get_settings

    settings = get_settings()
    if not settings.mate_api_key:
        return
    uid = resolve_request_user_id(
        token=settings.mate_api_key,
        client_user_id="550e8400-e29b-41d4-a716-446655440000",
    )
    assert uid == "550e8400-e29b-41d4-a716-446655440000"


def test_invalid_client_uuid_ignored():
    from app.config import get_settings

    settings = get_settings()
    if not settings.mate_api_key:
        return
    uid = resolve_request_user_id(
        token=settings.mate_api_key,
        client_user_id="not-a-uuid",
    )
    assert uid == "api-user"
