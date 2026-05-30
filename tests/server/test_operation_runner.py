import pytest

from app.server.operations import (
    CommandStep,
    OperationValidationError,
    RemoteOperation,
    validate_operation,
)


def test_validate_operation_allows_read_only_remote_steps():
    operation = RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id="debian-vps-1",
        actor_id="web-admin",
        actor_auth_method="session",
        inputs={"server_name": "debian-vps-1"},
        secret_refs=(),
        local_side_effects=("server_health_checks", "admin_actions"),
        remote_side_effects=(),
        command_policy="read-only",
        steps=(
            CommandStep(
                id="os-release",
                command="cat /etc/os-release",
                command_policy_class="read-only",
                expected_remote_effect="none",
                allowed_exit_codes=(0,),
                timeout_seconds=20,
                output_policy="internal-only",
            ),
        ),
        consistency_policy="read-only",
        audit_summary="Run read-only server health check",
        rollback_note="No rollback is needed for read-only health checks.",
        confirmation_required=False,
    )

    validate_operation(operation)


@pytest.mark.parametrize(
    "key",
    ["password", "private_key", "token", "preshared_key", "client_config"],
)
def test_validate_operation_rejects_secret_like_inputs(key):
    operation = RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id="debian-vps-1",
        actor_id="cli",
        actor_auth_method="cli",
        inputs={key: "secret-value"},
        secret_refs=(),
        local_side_effects=(),
        remote_side_effects=(),
        command_policy="read-only",
        steps=(),
        consistency_policy="read-only",
        audit_summary="Run read-only server health check",
        rollback_note="No rollback is needed for read-only health checks.",
        confirmation_required=False,
    )

    with pytest.raises(OperationValidationError, match="secret-like input"):
        validate_operation(operation)
