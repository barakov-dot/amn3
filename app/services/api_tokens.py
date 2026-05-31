from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Protocol


API_TOKEN_FIRST_SLICE_SCOPES = frozenset({"server:read", "metrics:read"})

ApiTokenAuthReason = Literal[
    "invalid_token",
    "revoked_token",
    "expired_token",
    "missing_scope",
]


class ApiTokenAuthError(ValueError):
    def __init__(self, message: str, *, reason: ApiTokenAuthReason) -> None:
        super().__init__(message)
        self.reason = reason


class ApiTokenStore(Protocol):
    def create_api_token(
        self,
        *,
        token_id: str,
        name: str,
        owner_user_id: int | None,
        owner_label: str,
        token_hash: str,
        scopes: list[str],
        expires_at: str | None,
    ) -> None: ...


@dataclass(frozen=True)
class ApiTokenRecord:
    token_id: str
    token_hash: str
    name: str
    owner_label: str
    scopes: frozenset[str]
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def safe_audit_metadata(self) -> dict[str, object]:
        return {
            "token_id": self.token_id,
            "name": self.name,
            "owner_label": self.owner_label,
            "scopes": sorted(self.scopes),
        }


@dataclass(frozen=True)
class ApiTokenIssue:
    token_id: str
    raw_token: str
    token_hash: str
    name: str
    owner_label: str
    scopes: frozenset[str]
    expires_at: datetime | None

    def safe_metadata(self) -> dict[str, object]:
        return {
            "token_id": self.token_id,
            "name": self.name,
            "owner_label": self.owner_label,
            "scopes": sorted(self.scopes),
            "expires_at": _format_datetime(self.expires_at),
            "raw_token_display": "one-time",
        }


def hash_api_token(raw_token: str) -> str:
    token_digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return f"sha256:{token_digest}"


def create_api_token(
    store: ApiTokenStore,
    *,
    name: str,
    owner_label: str,
    scopes: set[str] | frozenset[str],
    expires_at: datetime | None,
    owner_user_id: int | None = None,
    token_id: str | None = None,
    raw_token: str | None = None,
) -> ApiTokenIssue:
    normalized_scopes = _validate_scope_set(scopes)
    actual_token_id = token_id or f"api_{secrets.token_urlsafe(16)}"
    actual_raw_token = raw_token or secrets.token_urlsafe(32)
    token_hash = hash_api_token(actual_raw_token)

    store.create_api_token(
        token_id=actual_token_id,
        name=name,
        owner_user_id=owner_user_id,
        owner_label=owner_label,
        token_hash=token_hash,
        scopes=sorted(normalized_scopes),
        expires_at=_format_datetime(expires_at),
    )
    return ApiTokenIssue(
        token_id=actual_token_id,
        raw_token=actual_raw_token,
        token_hash=token_hash,
        name=name,
        owner_label=owner_label,
        scopes=normalized_scopes,
        expires_at=expires_at,
    )


def authenticate_api_token(
    raw_token: str,
    *,
    tokens: tuple[ApiTokenRecord, ...],
    required_scope: str,
    now: datetime | None = None,
) -> ApiTokenRecord:
    if not raw_token:
        raise ApiTokenAuthError("Invalid API token", reason="invalid_token")

    raw_token_hash = hash_api_token(raw_token)
    for token in tokens:
        if not secrets.compare_digest(raw_token_hash, token.token_hash):
            continue

        if token.revoked_at is not None:
            raise ApiTokenAuthError("API token is revoked", reason="revoked_token")

        current_time = _as_utc(now or datetime.now(timezone.utc))
        if token.expires_at is not None and _as_utc(token.expires_at) <= current_time:
            raise ApiTokenAuthError("API token is expired", reason="expired_token")

        if required_scope not in token.scopes:
            raise ApiTokenAuthError(
                f"Missing required scope: {required_scope}",
                reason="missing_scope",
            )

        return token

    raise ApiTokenAuthError("Invalid API token", reason="invalid_token")


def _validate_scope_set(scopes: set[str] | frozenset[str]) -> frozenset[str]:
    normalized = frozenset(scope.strip() for scope in scopes if scope.strip())
    unsupported = normalized - API_TOKEN_FIRST_SLICE_SCOPES
    if not normalized or unsupported:
        raise ValueError(
            "unsupported API token scopes: "
            + ", ".join(sorted(unsupported or normalized))
        )
    return normalized


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _as_utc(value).isoformat()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
