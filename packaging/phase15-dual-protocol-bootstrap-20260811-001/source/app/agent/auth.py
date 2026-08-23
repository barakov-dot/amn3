from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Sequence


AgentAuthReason = Literal[
    "invalid_token",
    "revoked_token",
    "expired_token",
    "missing_scope",
]


class AgentAuthError(ValueError):
    def __init__(self, message: str, *, reason: AgentAuthReason) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class AgentToken:
    token_id: str
    token_hash: str
    scopes: frozenset[str]
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    owner: str = "local-controller"


def hash_agent_token(raw_token: str) -> str:
    token_digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return f"sha256:{token_digest}"


def authenticate_agent_token(
    raw_token: str,
    *,
    tokens: Sequence[AgentToken],
    required_scope: str,
    now: datetime | None = None,
) -> AgentToken:
    if not raw_token:
        raise AgentAuthError("Invalid agent token", reason="invalid_token")

    raw_token_hash = hash_agent_token(raw_token)
    for token in tokens:
        if not secrets.compare_digest(raw_token_hash, token.token_hash):
            continue

        if token.revoked_at is not None:
            raise AgentAuthError("Agent token is revoked", reason="revoked_token")

        current_time = _as_utc(now or datetime.now(timezone.utc))
        if token.expires_at is not None and _as_utc(token.expires_at) <= current_time:
            raise AgentAuthError("Agent token is expired", reason="expired_token")

        if required_scope not in token.scopes:
            raise AgentAuthError(
                f"Missing required scope: {required_scope}",
                reason="missing_scope",
            )

        return token

    raise AgentAuthError("Invalid agent token", reason="invalid_token")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
