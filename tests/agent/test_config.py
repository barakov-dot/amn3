from datetime import datetime, timezone

import pytest

from app.agent.auth import AgentToken
from app.agent.config import (
    build_agent_tokens,
    parse_agent_expiry,
    parse_agent_scopes,
    require_agent_enabled,
)
from app.config.settings import Settings


TOKEN_HASH = (
    "sha256:"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)


def _settings(**overrides):
    values = {
        "_env_file": None,
        "telegram_bot_token": "TEST_TOKEN",
        "app_secret_key": "test-secret",
        "local_agent_enabled": True,
        "local_agent_token_hash": TOKEN_HASH,
        "local_agent_token_id": "agent-token-1",
        "local_agent_token_owner": "controller",
        "local_agent_token_scopes": "agent:health,agent:read",
    }
    values.update(overrides)
    return Settings(**values)


def test_parse_agent_scopes_strips_empty_parts():
    assert parse_agent_scopes("agent:health, agent:read,") == frozenset(
        {"agent:health", "agent:read"}
    )


def test_parse_agent_expiry_accepts_blank_value():
    assert parse_agent_expiry("") is None
    assert parse_agent_expiry("   ") is None


def test_parse_agent_expiry_accepts_z_suffix():
    assert parse_agent_expiry("2030-01-02T03:04:05Z") == datetime(
        2030,
        1,
        2,
        3,
        4,
        5,
        tzinfo=timezone.utc,
    )


def test_build_agent_tokens_returns_hash_only_token():
    token = build_agent_tokens(_settings())[0]

    assert token == AgentToken(
        token_id="agent-token-1",
        token_hash=TOKEN_HASH,
        scopes=frozenset({"agent:health", "agent:read"}),
        expires_at=None,
        owner="controller",
    )


def test_build_agent_tokens_rejects_disabled_agent():
    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        build_agent_tokens(
            _settings(local_agent_enabled=False, local_agent_token_hash="")
        )


def test_require_agent_enabled_rejects_disabled_agent():
    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        require_agent_enabled(
            _settings(local_agent_enabled=False, local_agent_token_hash="")
        )
