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
    "inactive_owner",
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
        rotated_from_token_id: str | None = None,
    ) -> None: ...

    def revoke_api_token(
        self,
        token_id: str,
        revoked_at: str,
        reason: str | None = None,
    ) -> bool: ...


@dataclass(frozen=True)
class ApiTokenRecord:
    token_id: str
    token_hash: str
    name: str
    owner_label: str
    scopes: frozenset[str]
    owner_user_id: int | None = None
    owner_status: str | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def safe_audit_metadata(self) -> dict[str, object]:
        return {
            "token_id": self.token_id,
            "name": self.name,
            "owner_label": self.owner_label,
            "owner_user_id": self.owner_user_id,
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


@dataclass(frozen=True)
class ApiTokenLifecycleEvent:
    action: str
    token_id: str
    status: str
    reason: str | None = None
    revoked_at: datetime | None = None
    rotated_from_token_id: str | None = None

    def safe_metadata(self) -> dict[str, object]:
        return {
            "action": self.action,
            "token_id": self.token_id,
            "status": self.status,
            "reason": self.reason,
            "revoked_at": _format_datetime(self.revoked_at),
            "rotated_from_token_id": self.rotated_from_token_id,
        }


@dataclass(frozen=True)
class ApiTokenRotationIssue:
    issue: ApiTokenIssue
    revoked: ApiTokenLifecycleEvent
    old_token_id: str
    owner_user_id: int | None

    def safe_metadata(self) -> dict[str, object]:
        return {
            "action": "api_token.rotated",
            "status": "rotated",
            "old_token_id": self.old_token_id,
            "new_token_id": self.issue.token_id,
            "owner_label": self.issue.owner_label,
            "owner_user_id": self.owner_user_id,
            "scopes": sorted(self.issue.scopes),
            "expires_at": _format_datetime(self.issue.expires_at),
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
    return _create_api_token_with_rotation(
        store,
        token_id=token_id,
        raw_token=raw_token,
        name=name,
        owner_user_id=owner_user_id,
        owner_label=owner_label,
        scopes=scopes,
        expires_at=expires_at,
        rotated_from_token_id=None,
    )


def create_route_api_token(
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
    if expires_at is None:
        raise ValueError("expires_at is required for route-connected API tokens")
    return create_api_token(
        store,
        name=name,
        owner_label=owner_label,
        scopes=scopes,
        expires_at=expires_at,
        owner_user_id=owner_user_id,
        token_id=token_id,
        raw_token=raw_token,
    )


def revoke_api_token(
    store: ApiTokenStore,
    *,
    token_id: str,
    revoked_at: datetime,
    reason: str,
) -> ApiTokenLifecycleEvent:
    revoked = store.revoke_api_token(
        token_id,
        _format_datetime(revoked_at) or "",
        reason=reason,
    )
    return ApiTokenLifecycleEvent(
        action="api_token.revoked",
        token_id=token_id,
        status="revoked" if revoked else "already-revoked-or-missing",
        reason=reason,
        revoked_at=revoked_at,
    )


def rotate_api_token(
    store: ApiTokenStore,
    previous: ApiTokenRecord,
    *,
    expires_at: datetime,
    rotated_at: datetime,
    new_token_id: str | None = None,
    raw_token: str | None = None,
) -> ApiTokenRotationIssue:
    issue = _create_api_token_with_rotation(
        store,
        token_id=new_token_id,
        raw_token=raw_token,
        name=previous.name,
        owner_user_id=previous.owner_user_id,
        owner_label=previous.owner_label,
        scopes=previous.scopes,
        expires_at=expires_at,
        rotated_from_token_id=previous.token_id,
    )
    revoked = revoke_api_token(
        store,
        token_id=previous.token_id,
        revoked_at=rotated_at,
        reason="rotated",
    )
    return ApiTokenRotationIssue(
        issue=issue,
        revoked=revoked,
        old_token_id=previous.token_id,
        owner_user_id=previous.owner_user_id,
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

        if token.owner_user_id is not None and token.owner_status != "active":
            raise ApiTokenAuthError("API token owner is inactive", reason="inactive_owner")

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


def _create_api_token_with_rotation(
    store: ApiTokenStore,
    *,
    name: str,
    owner_label: str,
    scopes: set[str] | frozenset[str],
    expires_at: datetime | None,
    owner_user_id: int | None,
    rotated_from_token_id: str | None,
    token_id: str | None,
    raw_token: str | None,
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
        rotated_from_token_id=rotated_from_token_id,
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


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _as_utc(value).isoformat()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
