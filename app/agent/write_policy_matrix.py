from __future__ import annotations

from dataclasses import dataclass

from app.agent.policy import AgentRiskClass


@dataclass(frozen=True)
class PlannedWriteOperation:
    operation_id: str
    method: str
    path: str
    scope: str
    risk_class: AgentRiskClass
    audit_required: bool
    dry_run: bool
    confirmation_required: bool
    vps_smoke_required: bool
    request_contract: str
    response_fields: tuple[str, ...]


@dataclass(frozen=True)
class WriteErrorContract:
    code: str
    http_status: int
    retryable: bool
    redact_secrets: bool
    public_message: str


WRITE_POLICY_MATRIX: tuple[PlannedWriteOperation, ...] = (
    PlannedWriteOperation(
        operation_id="local_agent.clients.apply.dry_run",
        method="POST",
        path="/agent/clients/dry-run",
        scope="agent:clients:write",
        risk_class="state-write",
        audit_required=True,
        dry_run=True,
        confirmation_required=False,
        vps_smoke_required=True,
        request_contract="AgentPeerApplyRequest",
        response_fields=(
            "operation_id",
            "status",
            "dry_run",
            "risk_class",
            "consistency_status",
            "message",
            "planned_commands",
        ),
    ),
    PlannedWriteOperation(
        operation_id="local_agent.clients.apply",
        method="POST",
        path="/agent/clients",
        scope="agent:clients:write",
        risk_class="state-write",
        audit_required=True,
        dry_run=False,
        confirmation_required=True,
        vps_smoke_required=True,
        request_contract="AgentPeerApplyRequest",
        response_fields=(
            "operation_id",
            "status",
            "dry_run",
            "risk_class",
            "consistency_status",
            "message",
            "planned_commands",
        ),
    ),
    PlannedWriteOperation(
        operation_id="local_agent.clients.revoke",
        method="DELETE",
        path="/agent/clients/{id}",
        scope="agent:clients:write",
        risk_class="state-write",
        audit_required=True,
        dry_run=False,
        confirmation_required=True,
        vps_smoke_required=True,
        request_contract="AgentPeerRevokeRequest",
        response_fields=(
            "operation_id",
            "status",
            "dry_run",
            "risk_class",
            "consistency_status",
            "message",
            "planned_commands",
        ),
    ),
)


WRITE_ERROR_CONTRACTS: tuple[WriteErrorContract, ...] = (
    WriteErrorContract(
        code="validation_failed",
        http_status=400,
        retryable=False,
        redact_secrets=True,
        public_message="Request fields are invalid or incomplete.",
    ),
    WriteErrorContract(
        code="missing_or_invalid_token",
        http_status=401,
        retryable=False,
        redact_secrets=True,
        public_message="Agent token is missing or invalid.",
    ),
    WriteErrorContract(
        code="missing_scope",
        http_status=403,
        retryable=False,
        redact_secrets=True,
        public_message="Agent token does not include the required write scope.",
    ),
    WriteErrorContract(
        code="preflight_required",
        http_status=409,
        retryable=True,
        redact_secrets=True,
        public_message="Dry-run preflight must pass before mutation.",
    ),
    WriteErrorContract(
        code="runtime_degraded",
        http_status=409,
        retryable=True,
        redact_secrets=True,
        public_message="Runtime is degraded; inspect Local Agent diagnostics before retry.",
    ),
    WriteErrorContract(
        code="mutation_failed",
        http_status=502,
        retryable=True,
        redact_secrets=True,
        public_message="Local peer mutation failed; inspect redacted diagnostics and rollback state.",
    ),
)


def planned_write_operation(operation_id: str) -> PlannedWriteOperation:
    for operation in WRITE_POLICY_MATRIX:
        if operation.operation_id == operation_id:
            return operation
    raise KeyError(f"Unknown Local Agent write operation: {operation_id}")
