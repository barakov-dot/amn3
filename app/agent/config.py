from __future__ import annotations

from datetime import datetime, timezone

from app.agent.auth import AgentToken
from app.config.settings import Settings


def require_agent_enabled(settings: Settings) -> None:
    if not settings.local_agent_enabled:
        raise ValueError("LOCAL_AGENT_ENABLED must be true to start the Local Agent")


def parse_agent_scopes(value: str) -> frozenset[str]:
    return frozenset(part.strip() for part in value.split(",") if part.strip())


def parse_agent_expiry(value: str) -> datetime | None:
    stripped = value.strip()
    if not stripped:
        return None
    normalized = stripped[:-1] + "+00:00" if stripped.endswith("Z") else stripped
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_agent_tokens(settings: Settings) -> tuple[AgentToken, ...]:
    require_agent_enabled(settings)
    return (
        AgentToken(
            token_id=settings.local_agent_token_id.strip(),
            token_hash=settings.local_agent_token_hash.strip(),
            scopes=parse_agent_scopes(settings.local_agent_token_scopes),
            expires_at=parse_agent_expiry(settings.local_agent_token_expires_at),
            owner=settings.local_agent_token_owner.strip(),
        ),
    )
