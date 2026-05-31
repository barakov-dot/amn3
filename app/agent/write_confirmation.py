from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256

from app.agent.write_audit import ALLOWED_ACTOR_SURFACES
from app.security.redaction import redact


ALLOWED_PREFLIGHT_RESULT_STATES = ("passed", "blocked", "failed")


class WriteConfirmationContractError(ValueError):
    pass


class WritePreflightRequiredError(WriteConfirmationContractError):
    code = "preflight_required"


@dataclass(frozen=True, repr=False)
class WritePreflightReference:
    preflight_id: str
    operation_id: str
    actor_surface: str
    actor_id: str
    server_alias: str
    client_id: str
    peer_public_key: str
    request_hash: str
    issued_at_epoch: int
    expires_at_epoch: int
    result_state: str
    message: str
    secret_values: tuple[str, ...] = field(default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        for field_name in (
            "preflight_id",
            "operation_id",
            "actor_id",
            "server_alias",
            "client_id",
            "peer_public_key",
            "request_hash",
            "result_state",
            "message",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )

        actor_surface = _require_text(self.actor_surface, "actor_surface")
        if actor_surface not in ALLOWED_ACTOR_SURFACES:
            raise WriteConfirmationContractError(
                f"actor_surface is unsupported: {actor_surface}"
            )
        object.__setattr__(self, "actor_surface", actor_surface)

        if self.result_state not in ALLOWED_PREFLIGHT_RESULT_STATES:
            raise WriteConfirmationContractError(
                f"result_state is unsupported: {self.result_state}"
            )
        if self.expires_at_epoch <= self.issued_at_epoch:
            raise WriteConfirmationContractError("expires_at_epoch must be after issued_at_epoch")

    @property
    def peer_public_key_fingerprint(self) -> str:
        return _fingerprint(self.peer_public_key)

    def is_fresh(self, now_epoch: int) -> bool:
        return self.result_state == "passed" and now_epoch <= self.expires_at_epoch

    def redacted_payload(self) -> dict[str, object]:
        return {
            "preflight_id": self.preflight_id,
            "operation_id": self.operation_id,
            "actor_surface": self.actor_surface,
            "actor_id": self.actor_id,
            "server_alias": self.server_alias,
            "client_id": self.client_id,
            "peer_public_key_fingerprint": self.peer_public_key_fingerprint,
            "request_hash": self.request_hash,
            "issued_at_epoch": self.issued_at_epoch,
            "expires_at_epoch": self.expires_at_epoch,
            "result_state": self.result_state,
            "message": _redact_values(self.message, self.secret_values),
        }

    def __repr__(self) -> str:
        return f"WritePreflightReference({self.redacted_payload()!r})"


@dataclass(frozen=True, repr=False)
class WriteConfirmationChallenge:
    confirmation_id: str
    preflight: WritePreflightReference
    actor_surface: str
    actor_id: str
    confirmation_nonce: str = field(repr=False)
    issued_at_epoch: int = 0
    expires_at_epoch: int = 0
    message: str = ""
    secret_values: tuple[str, ...] = field(default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        for field_name in (
            "confirmation_id",
            "actor_id",
            "confirmation_nonce",
            "message",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )

        actor_surface = _require_text(self.actor_surface, "actor_surface")
        if actor_surface not in ALLOWED_ACTOR_SURFACES:
            raise WriteConfirmationContractError(
                f"actor_surface is unsupported: {actor_surface}"
            )
        object.__setattr__(self, "actor_surface", actor_surface)

        if self.expires_at_epoch <= self.issued_at_epoch:
            raise WriteConfirmationContractError("expires_at_epoch must be after issued_at_epoch")

    @property
    def nonce_fingerprint(self) -> str:
        return _fingerprint(self.confirmation_nonce)

    def is_fresh(self, now_epoch: int) -> bool:
        return now_epoch <= self.expires_at_epoch

    def redacted_payload(self, now_epoch: int) -> dict[str, object]:
        return {
            "confirmation_id": self.confirmation_id,
            "preflight_id": self.preflight.preflight_id,
            "operation_id": self.preflight.operation_id,
            "actor_surface": self.actor_surface,
            "actor_id": self.actor_id,
            "server_alias": self.preflight.server_alias,
            "client_id": self.preflight.client_id,
            "peer_public_key_fingerprint": self.preflight.peer_public_key_fingerprint,
            "nonce_fingerprint": self.nonce_fingerprint,
            "issued_at_epoch": self.issued_at_epoch,
            "expires_at_epoch": self.expires_at_epoch,
            "expires_in_seconds": max(0, self.expires_at_epoch - now_epoch),
            "message": _redact_values(self.message, self.secret_values),
        }

    def __repr__(self) -> str:
        return f"WriteConfirmationChallenge({self.redacted_payload(self.issued_at_epoch)!r})"


def ensure_mutation_allowed(
    *,
    preflight: WritePreflightReference,
    confirmation: WriteConfirmationChallenge,
    operation_id: str,
    actor_surface: str,
    actor_id: str,
    now_epoch: int,
) -> bool:
    if preflight.operation_id != operation_id:
        raise WritePreflightRequiredError("operation_id does not match fresh preflight")
    if confirmation.preflight.preflight_id != preflight.preflight_id:
        raise WritePreflightRequiredError("confirmation does not match preflight")
    if confirmation.actor_surface != actor_surface or preflight.actor_surface != actor_surface:
        raise WritePreflightRequiredError("actor_surface does not match preflight")
    if confirmation.actor_id != actor_id or preflight.actor_id != actor_id:
        raise WritePreflightRequiredError("actor_id does not match preflight")
    if not preflight.is_fresh(now_epoch):
        raise WritePreflightRequiredError("fresh preflight is required before mutation")
    if not confirmation.is_fresh(now_epoch):
        raise WritePreflightRequiredError("fresh confirmation is required before mutation")
    return True


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise WriteConfirmationContractError(f"{field_name} cannot be blank")
    return normalized


def _fingerprint(value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:16]}"


def _redact_values(value: str, secrets: tuple[str, ...]) -> str:
    safe_value = value
    for secret in secrets:
        if secret:
            safe_value = safe_value.replace(secret, "[REDACTED]")
    return redact(safe_value)
