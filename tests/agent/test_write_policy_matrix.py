import pytest

from app.agent.policy import AgentPolicyError, get_policy
from app.agent.write_policy_matrix import (
    WRITE_ERROR_CONTRACTS,
    WRITE_POLICY_MATRIX,
    planned_write_operation,
)


def test_write_policy_matrix_lists_only_vps_gated_client_operations():
    assert {
        (operation.operation_id, operation.method, operation.path)
        for operation in WRITE_POLICY_MATRIX
    } == {
        ("local_agent.clients.apply.dry_run", "POST", "/agent/clients/dry-run"),
        ("local_agent.clients.apply", "POST", "/agent/clients"),
        ("local_agent.clients.revoke", "DELETE", "/agent/clients/{id}"),
    }

    assert all(operation.scope == "agent:clients:write" for operation in WRITE_POLICY_MATRIX)
    assert all(operation.risk_class == "state-write" for operation in WRITE_POLICY_MATRIX)
    assert all(operation.audit_required is True for operation in WRITE_POLICY_MATRIX)
    assert all(operation.vps_smoke_required is True for operation in WRITE_POLICY_MATRIX)


def test_write_policy_matrix_marks_confirmation_and_dry_run_requirements():
    dry_run = planned_write_operation("local_agent.clients.apply.dry_run")
    apply = planned_write_operation("local_agent.clients.apply")
    revoke = planned_write_operation("local_agent.clients.revoke")

    assert dry_run.dry_run is True
    assert dry_run.confirmation_required is False
    assert apply.dry_run is False
    assert apply.confirmation_required is True
    assert revoke.confirmation_required is True
    assert "preshared_key" not in apply.response_fields
    assert "private_key" not in apply.response_fields
    assert "qr" not in apply.response_fields
    assert "vpn_url" not in apply.response_fields


def test_write_policy_matrix_is_not_active_before_vps_smoke():
    for operation in WRITE_POLICY_MATRIX:
        with pytest.raises(AgentPolicyError, match="No agent route policy"):
            get_policy(operation.method, operation.path)


def test_write_error_contracts_are_typed_redacted_and_non_destructive():
    assert {
        contract.code: contract.http_status
        for contract in WRITE_ERROR_CONTRACTS
    } == {
        "validation_failed": 400,
        "missing_or_invalid_token": 401,
        "missing_scope": 403,
        "preflight_required": 409,
        "runtime_degraded": 409,
        "mutation_failed": 502,
    }

    assert all(contract.redact_secrets is True for contract in WRITE_ERROR_CONTRACTS)
    assert all("raw token" not in contract.public_message.lower() for contract in WRITE_ERROR_CONTRACTS)
    assert all("private key" not in contract.public_message.lower() for contract in WRITE_ERROR_CONTRACTS)
