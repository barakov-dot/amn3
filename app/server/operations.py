from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RiskClass = Literal[
    "read-only",
    "read-only-remote",
    "read-only-remote-telemetry",
    "secret-read",
    "state-write",
    "remote-state-write",
    "remote-exec",
    "destructive-remote",
]
ActorAuthMethod = Literal["session", "telegram-admin", "scoped-token", "cli", "system"]
CommandPolicyClass = Literal["read-only", "telemetry", "state-write"]
OutputPolicy = Literal["internal-only", "discard", "redact-and-store"]
ConsistencyPolicy = Literal[
    "read-only",
    "local-first",
    "remote-first",
    "two-phase-best-effort",
]
ConsistencyStatus = Literal[
    "read-only",
    "consistent",
    "remote-changed-local-failed",
    "local-changed-remote-failed",
    "unknown",
]


class OperationValidationError(ValueError):
    pass


@dataclass(frozen=True)
class CommandStep:
    id: str
    command: str
    command_policy_class: CommandPolicyClass
    expected_remote_effect: str
    allowed_exit_codes: tuple[int, ...]
    timeout_seconds: int
    output_policy: OutputPolicy
    stdin_secret_ref: str | None = None


@dataclass(frozen=True)
class RemoteOperation:
    id: str
    risk_class: RiskClass
    server_id: str
    actor_id: str
    actor_auth_method: ActorAuthMethod
    inputs: dict[str, str]
    secret_refs: tuple[str, ...]
    local_side_effects: tuple[str, ...]
    remote_side_effects: tuple[str, ...]
    command_policy: CommandPolicyClass
    steps: tuple[CommandStep, ...]
    consistency_policy: ConsistencyPolicy
    audit_summary: str
    rollback_note: str
    confirmation_required: bool
    run_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class OperationPlan:
    operation_id: str
    risk_class: RiskClass
    commands: tuple[str, ...]
    audit_summary: str
    rollback_note: str


@dataclass(frozen=True)
class StepExecutionResult:
    step_id: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    status: Literal["succeeded", "failed"]


@dataclass(frozen=True)
class OperationResult:
    operation_id: str
    risk_class: RiskClass
    status: Literal["planned", "completed", "failed", "blocked"]
    consistency_status: ConsistencyStatus
    steps: tuple[StepExecutionResult, ...]
    redacted_stdout_summary: str
    redacted_stderr_summary: str
    recovery_note: str


_SECRET_INPUT_MARKERS = (
    "password",
    "private_key",
    "token",
    "secret",
    "preshared_key",
    "client_config",
)


def validate_operation(operation: RemoteOperation) -> None:
    if not operation.id.strip():
        raise OperationValidationError("operation id cannot be blank")
    if operation.risk_class == "destructive-remote" and not operation.confirmation_required:
        raise OperationValidationError("destructive-remote operation requires confirmation")
    for key in operation.inputs:
        lowered = key.lower()
        if any(marker in lowered for marker in _SECRET_INPUT_MARKERS):
            raise OperationValidationError(f"secret-like input is not allowed: {key}")
    for step in operation.steps:
        if step.command_policy_class != operation.command_policy:
            raise OperationValidationError(
                f"step policy {step.command_policy_class} does not match "
                f"operation policy {operation.command_policy}"
            )
        if step.timeout_seconds < 1:
            raise OperationValidationError(f"step timeout must be positive: {step.id}")
        if not step.allowed_exit_codes:
            raise OperationValidationError(f"allowed exit codes cannot be empty: {step.id}")
