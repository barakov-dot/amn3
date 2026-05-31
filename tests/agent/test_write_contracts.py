import pytest

from app.agent.write_contracts import (
    AgentPeerApplyRequest,
    AgentPeerMutationResult,
    AgentPeerRevokeRequest,
    AgentWriteContractError,
)


def test_peer_apply_request_normalizes_allowed_ip_and_redacts_psk():
    request = AgentPeerApplyRequest(
        client_id="device-42",
        peer_public_key="peer-public-key",
        preshared_key="super-secret-psk",
        vpn_ip="10.8.1.42",
    )

    assert request.allowed_ips == "10.8.1.42/32"
    assert request.to_agent_payload() == {
        "client_id": "device-42",
        "protocol": "amneziawg",
        "peer_public_key": "peer-public-key",
        "preshared_key": "super-secret-psk",
        "allowed_ips": "10.8.1.42/32",
    }
    assert request.redacted_payload()["preshared_key"] == "[REDACTED]"
    assert "super-secret-psk" not in repr(request)


def test_peer_apply_request_rejects_blank_or_invalid_fields():
    with pytest.raises(AgentWriteContractError, match="client_id"):
        AgentPeerApplyRequest(
            client_id=" ",
            peer_public_key="peer-public-key",
            preshared_key="super-secret-psk",
            vpn_ip="10.8.1.42",
        )

    with pytest.raises(AgentWriteContractError, match="vpn_ip"):
        AgentPeerApplyRequest(
            client_id="device-42",
            peer_public_key="peer-public-key",
            preshared_key="super-secret-psk",
            vpn_ip="not-an-ip",
        )


def test_peer_revoke_request_validates_and_exposes_no_secret_fields():
    request = AgentPeerRevokeRequest(
        client_id="device-42",
        peer_public_key="peer-public-key",
    )

    assert request.to_agent_payload() == {
        "client_id": "device-42",
        "peer_public_key": "peer-public-key",
    }
    assert request.redacted_payload() == request.to_agent_payload()

    with pytest.raises(AgentWriteContractError, match="peer_public_key"):
        AgentPeerRevokeRequest(client_id="device-42", peer_public_key="")


def test_peer_mutation_result_redacts_secret_values_from_response_payload():
    result = AgentPeerMutationResult(
        operation_id="local_agent.clients.apply",
        status="planned",
        dry_run=True,
        message="Would apply peer with super-secret-psk",
        planned_commands=(
            "awg set awg0 peer peer-public-key preshared-key super-secret-psk",
        ),
        secret_values=("super-secret-psk",),
    )

    payload = result.redacted_payload()

    assert payload["operation_id"] == "local_agent.clients.apply"
    assert payload["status"] == "planned"
    assert payload["dry_run"] is True
    assert payload["risk_class"] == "state-write"
    assert payload["consistency_status"] == "dry-run"
    assert "super-secret-psk" not in repr(result)
    assert "super-secret-psk" not in str(payload)
    assert "[REDACTED]" in str(payload)
