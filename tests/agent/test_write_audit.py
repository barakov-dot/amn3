import pytest

from app.agent.write_audit import (
    ALLOWED_ACTOR_SURFACES,
    ALLOWED_RESULT_STATES,
    WriteAuditContractError,
    WriteAuditEvent,
)


def test_write_audit_event_records_safe_fields_and_redacts_secret_values():
    event = WriteAuditEvent(
        audit_id="audit-001",
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="admin-42",
        server_alias="debian-vps-1",
        client_id="alice-phone",
        peer_public_key="peer-public-key-abcdef1234567890",
        dry_run_reference="dry-run-001",
        result_state="mutation_applied",
        rollback_reference="revoke:alice-phone",
        message=(
            "Applied peer with raw-token-secret private-key-secret "
            "psk-secret qr-secret vpn://secret"
        ),
        details={
            "planned_command": "awg set awg0 peer peer-public-key psk-secret",
            "private_key": "private-key-secret",
            "preshared_key": "psk-secret",
            "qr": "qr-secret",
            "vpn_url": "vpn://secret",
            "raw_token": "raw-token-secret",
        },
        secret_values=(
            "raw-token-secret",
            "private-key-secret",
            "psk-secret",
            "qr-secret",
            "vpn://secret",
        ),
    )

    record = event.redacted_record()

    assert record["audit_id"] == "audit-001"
    assert record["operation_id"] == "local_agent.clients.apply"
    assert record["actor_surface"] == "web_admin"
    assert record["actor_id"] == "admin-42"
    assert record["server_alias"] == "debian-vps-1"
    assert record["client_id"] == "alice-phone"
    assert record["peer_public_key_fingerprint"].startswith("sha256:")
    assert record["dry_run_reference"] == "dry-run-001"
    assert record["result_state"] == "mutation_applied"
    assert record["rollback_reference"] == "revoke:alice-phone"

    serialized = f"{record!r} {event!r}"
    for unsafe_value in [
        "raw-token-secret",
        "private-key-secret",
        "psk-secret",
        "qr-secret",
        "vpn://secret",
    ]:
        assert unsafe_value not in serialized
    assert "[REDACTED]" in serialized


def test_write_audit_event_validates_actor_surface_and_result_state():
    assert ALLOWED_ACTOR_SURFACES == ("web_admin", "telegram_bot", "cli")
    assert "mutation_failed" in ALLOWED_RESULT_STATES
    assert "rollback_applied" in ALLOWED_RESULT_STATES

    with pytest.raises(WriteAuditContractError, match="actor_surface"):
        WriteAuditEvent(
            audit_id="audit-001",
            operation_id="local_agent.clients.apply",
            actor_surface="public_api",
            actor_id="admin-42",
            server_alias="debian-vps-1",
            client_id="alice-phone",
            peer_public_key="peer-public-key",
            dry_run_reference="dry-run-001",
            result_state="mutation_applied",
            rollback_reference="revoke:alice-phone",
            message="Applied",
        )

    with pytest.raises(WriteAuditContractError, match="result_state"):
        WriteAuditEvent(
            audit_id="audit-001",
            operation_id="local_agent.clients.apply",
            actor_surface="cli",
            actor_id="admin-42",
            server_alias="debian-vps-1",
            client_id="alice-phone",
            peer_public_key="peer-public-key",
            dry_run_reference="dry-run-001",
            result_state="unknown",
            rollback_reference="revoke:alice-phone",
            message="Applied",
        )


def test_write_audit_event_rejects_blank_required_fields():
    with pytest.raises(WriteAuditContractError, match="client_id"):
        WriteAuditEvent(
            audit_id="audit-001",
            operation_id="local_agent.clients.apply",
            actor_surface="telegram_bot",
            actor_id="admin-42",
            server_alias="debian-vps-1",
            client_id=" ",
            peer_public_key="peer-public-key",
            dry_run_reference="dry-run-001",
            result_state="mutation_applied",
            rollback_reference="revoke:alice-phone",
            message="Applied",
        )
