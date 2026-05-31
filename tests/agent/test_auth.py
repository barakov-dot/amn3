from datetime import datetime, timedelta, timezone

import pytest

from app.agent.auth import (
    AgentAuthError,
    AgentToken,
    authenticate_agent_token,
    hash_agent_token,
)


def test_hash_agent_token_is_stable_prefixed_and_does_not_expose_raw_token():
    token_hash = hash_agent_token("raw-agent-token")

    assert token_hash == hash_agent_token("raw-agent-token")
    assert token_hash.startswith("sha256:")
    assert "raw-agent-token" not in token_hash


def test_authenticate_agent_token_accepts_matching_token_with_required_scope():
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
        owner="local-admin",
    )

    authenticated = authenticate_agent_token(
        "raw-agent-token",
        tokens=(agent_token,),
        required_scope="agent:health",
    )

    assert authenticated.token_id == "local-token-1"
    assert authenticated.owner == "local-admin"


def test_authenticate_agent_token_accepts_unexpired_aware_expiry():
    now = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
        expires_at=now + timedelta(minutes=5),
    )

    authenticated = authenticate_agent_token(
        "raw-agent-token",
        tokens=(agent_token,),
        required_scope="agent:health",
        now=now,
    )

    assert authenticated.token_id == "local-token-1"


def test_authenticate_agent_token_treats_naive_expiry_as_utc():
    now = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
        expires_at=datetime(2026, 5, 31, 10, 5),
    )

    authenticated = authenticate_agent_token(
        "raw-agent-token",
        tokens=(agent_token,),
        required_scope="agent:health",
        now=now,
    )

    assert authenticated.token_id == "local-token-1"


@pytest.mark.parametrize("raw_token", ("", "unknown-token"))
def test_authenticate_agent_token_rejects_missing_or_unknown_raw_token(raw_token):
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
    )

    with pytest.raises(AgentAuthError, match="Invalid agent token"):
        authenticate_agent_token(
            raw_token,
            tokens=(agent_token,),
            required_scope="agent:health",
        )


def test_authenticate_agent_token_rejects_insufficient_scope():
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:read"}),
    )

    with pytest.raises(AgentAuthError, match="Missing required scope"):
        authenticate_agent_token(
            "raw-agent-token",
            tokens=(agent_token,),
            required_scope="agent:health",
        )


def test_authenticate_agent_token_rejects_expired_token():
    now = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
        expires_at=now - timedelta(seconds=1),
    )

    with pytest.raises(AgentAuthError, match="expired"):
        authenticate_agent_token(
            "raw-agent-token",
            tokens=(agent_token,),
            required_scope="agent:health",
            now=now,
        )


def test_authenticate_agent_token_rejects_revoked_token():
    now = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
    agent_token = AgentToken(
        token_id="local-token-1",
        token_hash=hash_agent_token("raw-agent-token"),
        scopes=frozenset({"agent:health"}),
        revoked_at=now - timedelta(seconds=1),
    )

    with pytest.raises(AgentAuthError, match="revoked"):
        authenticate_agent_token(
            "raw-agent-token",
            tokens=(agent_token,),
            required_scope="agent:health",
            now=now,
        )
