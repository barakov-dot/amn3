from dataclasses import replace

import pytest

from app.agent.write_confirmation import (
    WriteConfirmationChallenge,
    WriteConfirmationContractError,
    WritePreflightReference,
    WritePreflightRequiredError,
    ensure_mutation_allowed,
)


def test_preflight_reference_redacts_secrets_and_exposes_safe_fingerprint():
    preflight = WritePreflightReference(
        preflight_id="preflight-001",
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="admin-42",
        server_alias="debian-vps-1",
        client_id="alice-phone",
        peer_public_key="peer-public-key-abcdef1234567890",
        request_hash="sha256:request-hash",
        issued_at_epoch=1_000,
        expires_at_epoch=1_300,
        result_state="passed",
        message="Dry-run passed without raw-token-secret or psk-secret leakage",
        secret_values=("raw-token-secret", "psk-secret"),
    )

    payload = preflight.redacted_payload()

    assert preflight.is_fresh(now_epoch=1_200) is True
    assert preflight.is_fresh(now_epoch=1_301) is False
    assert payload["preflight_id"] == "preflight-001"
    assert payload["operation_id"] == "local_agent.clients.apply"
    assert payload["peer_public_key_fingerprint"].startswith("sha256:")
    assert "peer_public_key" not in payload

    serialized = f"{payload!r} {preflight!r}"
    assert "peer-public-key-abcdef1234567890" not in serialized
    assert "raw-token-secret" not in serialized
    assert "psk-secret" not in serialized
    assert "[REDACTED]" in serialized


def test_confirmation_challenge_uses_nonce_fingerprint_and_redacted_payload():
    preflight = _fresh_preflight()
    confirmation = WriteConfirmationChallenge(
        confirmation_id="confirm-001",
        preflight=preflight,
        actor_surface="telegram_bot",
        actor_id="admin-42",
        confirmation_nonce="nonce-secret",
        issued_at_epoch=1_050,
        expires_at_epoch=1_110,
        message="Confirm apply with nonce-secret and psk-secret",
        secret_values=("nonce-secret", "psk-secret"),
    )

    payload = confirmation.redacted_payload(now_epoch=1_070)

    assert confirmation.is_fresh(now_epoch=1_070) is True
    assert confirmation.is_fresh(now_epoch=1_111) is False
    assert payload["confirmation_id"] == "confirm-001"
    assert payload["preflight_id"] == "preflight-001"
    assert payload["operation_id"] == "local_agent.clients.apply"
    assert payload["expires_in_seconds"] == 40
    assert payload["nonce_fingerprint"].startswith("sha256:")
    assert "confirmation_nonce" not in payload

    serialized = f"{payload!r} {confirmation!r}"
    assert "nonce-secret" not in serialized
    assert "psk-secret" not in serialized
    assert "[REDACTED]" in serialized


def test_ensure_mutation_allowed_requires_fresh_matching_preflight_and_confirmation():
    preflight = _fresh_preflight()
    confirmation = WriteConfirmationChallenge(
        confirmation_id="confirm-001",
        preflight=preflight,
        actor_surface="web_admin",
        actor_id="admin-42",
        confirmation_nonce="nonce-secret",
        issued_at_epoch=1_050,
        expires_at_epoch=1_110,
        message="Confirm apply",
    )

    assert ensure_mutation_allowed(
        preflight=preflight,
        confirmation=confirmation,
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="admin-42",
        now_epoch=1_070,
    ) is True

    expired_preflight = replace(preflight, expires_at_epoch=1_060)
    with pytest.raises(WritePreflightRequiredError) as exc_info:
        ensure_mutation_allowed(
            preflight=expired_preflight,
            confirmation=confirmation,
            operation_id="local_agent.clients.apply",
            actor_surface="web_admin",
            actor_id="admin-42",
            now_epoch=1_070,
        )
    assert exc_info.value.code == "preflight_required"

    with pytest.raises(WritePreflightRequiredError, match="operation_id"):
        ensure_mutation_allowed(
            preflight=preflight,
            confirmation=confirmation,
            operation_id="local_agent.clients.revoke",
            actor_surface="web_admin",
            actor_id="admin-42",
            now_epoch=1_070,
        )


def test_confirmation_contract_rejects_blank_or_invalid_fields():
    with pytest.raises(WriteConfirmationContractError, match="actor_surface"):
        WritePreflightReference(
            preflight_id="preflight-001",
            operation_id="local_agent.clients.apply",
            actor_surface="public_api",
            actor_id="admin-42",
            server_alias="debian-vps-1",
            client_id="alice-phone",
            peer_public_key="peer-public-key",
            request_hash="sha256:request-hash",
            issued_at_epoch=1_000,
            expires_at_epoch=1_300,
            result_state="passed",
            message="Dry-run passed",
        )

    with pytest.raises(WriteConfirmationContractError, match="preflight_id"):
        WritePreflightReference(
            preflight_id=" ",
            operation_id="local_agent.clients.apply",
            actor_surface="cli",
            actor_id="admin-42",
            server_alias="debian-vps-1",
            client_id="alice-phone",
            peer_public_key="peer-public-key",
            request_hash="sha256:request-hash",
            issued_at_epoch=1_000,
            expires_at_epoch=1_300,
            result_state="passed",
            message="Dry-run passed",
        )


def _fresh_preflight() -> WritePreflightReference:
    return WritePreflightReference(
        preflight_id="preflight-001",
        operation_id="local_agent.clients.apply",
        actor_surface="web_admin",
        actor_id="admin-42",
        server_alias="debian-vps-1",
        client_id="alice-phone",
        peer_public_key="peer-public-key-abcdef1234567890",
        request_hash="sha256:request-hash",
        issued_at_epoch=1_000,
        expires_at_epoch=1_300,
        result_state="passed",
        message="Dry-run passed",
    )
