from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import hashlib
import secrets


@dataclass(frozen=True)
class EmailToken:
    raw_token: str
    token_hash: str
    expires_at: str


def create_email_token(*, ttl_minutes: int, now: datetime | None = None) -> EmailToken:
    if ttl_minutes <= 0:
        raise ValueError("email token ttl must be positive")
    raw_token = secrets.token_urlsafe(32)
    issued_at = now or datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=ttl_minutes)
    return EmailToken(
        raw_token=raw_token,
        token_hash=hash_email_token(raw_token),
        expires_at=_utc_iso(expires_at),
    )


def hash_email_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return _utc_iso(datetime.now(timezone.utc))


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
