from datetime import datetime, timedelta, timezone

import pytest

from app.services.api_tokens import (
    API_TOKEN_FIRST_SLICE_SCOPES,
    ApiTokenAuthError,
    ApiTokenRecord,
    authenticate_api_token,
    create_api_token,
    hash_api_token,
)


def test_hash_api_token_is_stable_prefixed_and_does_not_expose_raw_token():
    token_hash = hash_api_token("raw-api-token")

    assert token_hash == hash_api_token("raw-api-token")
    assert token_hash.startswith("sha256:")
    assert "raw-api-token" not in token_hash


def test_create_api_token_stores_hash_and_returns_raw_token_only_in_issue():
    stored: dict[str, object] = {}

    class TokenStore:
        def create_api_token(self, **kwargs):
            stored.update(kwargs)

    issue = create_api_token(
        TokenStore(),
        token_id="api-token-1",
        raw_token="raw-api-token",
        name="Monitoring",
        owner_label="ops",
        scopes={"server:read", "metrics:read"},
        expires_at=datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc),
    )

    assert issue.raw_token == "raw-api-token"
    assert issue.safe_metadata() == {
        "token_id": "api-token-1",
        "name": "Monitoring",
        "owner_label": "ops",
        "scopes": ["metrics:read", "server:read"],
        "expires_at": "2026-06-08T10:00:00+00:00",
        "raw_token_display": "one-time",
    }
    assert stored["token_hash"] == hash_api_token("raw-api-token")
    assert stored["scopes"] == ["metrics:read", "server:read"]
    assert "raw-api-token" not in str(stored)


def test_create_api_token_rejects_secret_read_or_write_scopes():
    class TokenStore:
        def create_api_token(self, **kwargs):  # pragma: no cover - must not be called
            raise AssertionError("token should not be stored")

    assert API_TOKEN_FIRST_SLICE_SCOPES == frozenset({"server:read", "metrics:read"})
    with pytest.raises(ValueError, match="unsupported API token scopes"):
        create_api_token(
            TokenStore(),
            token_id="api-token-1",
            raw_token="raw-api-token",
            name="Config reader",
            owner_label="ops",
            scopes={"config:read"},
            expires_at=None,
        )
    with pytest.raises(ValueError, match="unsupported API token scopes"):
        create_api_token(
            TokenStore(),
            token_id="api-token-2",
            raw_token="raw-api-token-2",
            name="Writer",
            owner_label="ops",
            scopes={"server:write"},
            expires_at=None,
        )


def test_authenticate_api_token_accepts_matching_unexpired_scope():
    now = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
    record = ApiTokenRecord(
        token_id="api-token-1",
        token_hash=hash_api_token("raw-api-token"),
        name="Monitoring",
        owner_label="ops",
        scopes=frozenset({"server:read"}),
        expires_at=now + timedelta(minutes=5),
    )

    authenticated = authenticate_api_token(
        "raw-api-token",
        tokens=(record,),
        required_scope="server:read",
        now=now,
    )

    assert authenticated.token_id == "api-token-1"
    assert authenticated.safe_audit_metadata() == {
        "token_id": "api-token-1",
        "name": "Monitoring",
        "owner_label": "ops",
        "scopes": ["server:read"],
    }


def test_authenticate_api_token_rejects_expired_revoked_and_missing_scope():
    now = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
    expired = ApiTokenRecord(
        token_id="expired",
        token_hash=hash_api_token("expired-token"),
        name="Expired",
        owner_label="ops",
        scopes=frozenset({"server:read"}),
        expires_at=now,
    )
    revoked = ApiTokenRecord(
        token_id="revoked",
        token_hash=hash_api_token("revoked-token"),
        name="Revoked",
        owner_label="ops",
        scopes=frozenset({"server:read"}),
        revoked_at=now - timedelta(minutes=1),
    )
    limited = ApiTokenRecord(
        token_id="limited",
        token_hash=hash_api_token("limited-token"),
        name="Limited",
        owner_label="ops",
        scopes=frozenset({"metrics:read"}),
    )

    with pytest.raises(ApiTokenAuthError) as expired_error:
        authenticate_api_token(
            "expired-token",
            tokens=(expired,),
            required_scope="server:read",
            now=now,
        )
    assert expired_error.value.reason == "expired_token"

    with pytest.raises(ApiTokenAuthError) as revoked_error:
        authenticate_api_token(
            "revoked-token",
            tokens=(revoked,),
            required_scope="server:read",
            now=now,
        )
    assert revoked_error.value.reason == "revoked_token"

    with pytest.raises(ApiTokenAuthError) as scope_error:
        authenticate_api_token(
            "limited-token",
            tokens=(limited,),
            required_scope="server:read",
            now=now,
        )
    assert scope_error.value.reason == "missing_scope"
