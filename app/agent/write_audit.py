from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Literal

from app.security.redaction import redact


ActorSurface = Literal["web_admin", "telegram_bot", "cli"]
AuditResultState = Literal[
    "dry_run_planned",
    "mutation_applied",
    "mutation_revoked",
    "mutation_failed",
    "rollback_planned",
    "rollback_applied",
]

ALLOWED_ACTOR_SURFACES: tuple[ActorSurface, ...] = ("web_admin", "telegram_bot", "cli")
ALLOWED_RESULT_STATES: tuple[AuditResultState, ...] = (
    "dry_run_planned",
    "mutation_applied",
    "mutation_revoked",
    "mutation_failed",
    "rollback_planned",
    "rollback_applied",
)


class WriteAuditContractError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class WriteAuditEvent:
    audit_id: str
    operation_id: str
    actor_surface: str
    actor_id: str
    server_alias: str
    client_id: str
    peer_public_key: str
    dry_run_reference: str
    result_state: str
    rollback_reference: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    secret_values: tuple[str, ...] = field(default_factory=tuple, repr=False)
    risk_class: str = "state-write"

    def __post_init__(self) -> None:
        for field_name in (
            "audit_id",
            "operation_id",
            "actor_id",
            "server_alias",
            "client_id",
            "peer_public_key",
            "dry_run_reference",
            "rollback_reference",
            "message",
            "risk_class",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )

        actor_surface = _require_text(self.actor_surface, "actor_surface")
        if actor_surface not in ALLOWED_ACTOR_SURFACES:
            raise WriteAuditContractError(f"actor_surface is unsupported: {actor_surface}")
        object.__setattr__(self, "actor_surface", actor_surface)

        result_state = _require_text(self.result_state, "result_state")
        if result_state not in ALLOWED_RESULT_STATES:
            raise WriteAuditContractError(f"result_state is unsupported: {result_state}")
        object.__setattr__(self, "result_state", result_state)

        object.__setattr__(self, "details", dict(self.details))

    @property
    def peer_public_key_fingerprint(self) -> str:
        digest = sha256(self.peer_public_key.encode("utf-8")).hexdigest()
        return f"sha256:{digest[:16]}"

    def redacted_record(self) -> dict[str, object]:
        return {
            "audit_id": self.audit_id,
            "operation_id": self.operation_id,
            "actor_surface": self.actor_surface,
            "actor_id": self.actor_id,
            "server_alias": self.server_alias,
            "client_id": self.client_id,
            "peer_public_key_fingerprint": self.peer_public_key_fingerprint,
            "dry_run_reference": self.dry_run_reference,
            "result_state": self.result_state,
            "risk_class": self.risk_class,
            "rollback_reference": self.rollback_reference,
            "message": self._redact_text(self.message),
            "details": self._redact_object(self.details),
        }

    def __repr__(self) -> str:
        return f"WriteAuditEvent({self.redacted_record()!r})"

    def _redact_object(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key): self._redact_object(nested_value)
                for key, nested_value in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [self._redact_object(nested_value) for nested_value in value]
        if isinstance(value, str):
            return self._redact_text(value)
        return value

    def _redact_text(self, value: str) -> str:
        safe_value = value
        for secret in self.secret_values:
            if secret:
                safe_value = safe_value.replace(secret, "[REDACTED]")
        return redact(safe_value)


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise WriteAuditContractError(f"{field_name} cannot be blank")
    return normalized
