from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.agent.api import create_agent_app
from app.agent.audit import InMemoryAgentAuditSink
from app.agent.auth import AgentToken, hash_agent_token
from app.agent.runtime import (
    FakeLocalRuntimeAdapter,
    ProtocolSnapshot,
    RuntimeSnapshot,
)


RAW_TOKEN = "raw-agent-token"


def _token(scopes: set[str]) -> AgentToken:
    return AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(RAW_TOKEN),
        scopes=frozenset(scopes),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        owner="test-controller",
    )


def _client(scopes: set[str]) -> tuple[TestClient, InMemoryAgentAuditSink]:
    audit = InMemoryAgentAuditSink()
    adapter = FakeLocalRuntimeAdapter(
        RuntimeSnapshot(
            server_name="demo-vps",
            runtime_type="docker",
            status="running",
            protocols=(
                ProtocolSnapshot(
                    name="amneziawg",
                    status="running",
                    runtime_type="docker",
                    capabilities=("detect", "status"),
                    container_name="amnezia-awg",
                    interface="awg0",
                    client_count=2,
                ),
            ),
        )
    )
    app = create_agent_app(
        adapter=adapter,
        tokens=(_token(scopes),),
        audit_sink=audit,
        build_version="test-build",
    )
    return TestClient(app), audit


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {RAW_TOKEN}"}


def test_agent_docs_are_not_public():
    client, audit = _client({"agent:health"})

    response = client.get("/docs")

    assert response.status_code == 404
    assert audit.events == []


def test_health_requires_bearer_token():
    client, audit = _client({"agent:health"})

    response = client.get("/agent/health")

    assert response.status_code == 401
    assert "agent token" in response.json()["detail"].lower()
    assert audit.events == []


def test_health_rejects_invalid_token():
    client, audit = _client({"agent:health"})

    response = client.get(
        "/agent/health",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert audit.events == []


def test_runtime_rejects_insufficient_scope():
    client, audit = _client({"agent:health"})

    response = client.get("/agent/runtime", headers=_auth_headers())

    assert response.status_code == 403
    assert "scope" in response.json()["detail"].lower()
    assert audit.events == []


def test_health_and_version_return_secret_free_metadata():
    client, audit = _client({"agent:health"})

    health_response = client.get("/agent/health", headers=_auth_headers())
    version_response = client.get("/agent/version", headers=_auth_headers())

    assert health_response.status_code == 200
    assert health_response.json() == {
        "status": "ok",
        "service": "local-amnezia-agent",
    }
    assert version_response.status_code == 200
    assert version_response.json() == {
        "api": "local-amnezia-agent",
        "version": "test-build",
        "write_enabled": False,
    }
    assert [event.path for event in audit.events] == [
        "/agent/health",
        "/agent/version",
    ]
    assert all(event.result == "allowed" for event in audit.events)


def test_runtime_endpoint_returns_read_only_runtime_snapshot():
    client, audit = _client({"agent:read"})

    response = client.get("/agent/runtime", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "server_name": "demo-vps",
        "runtime_type": "docker",
        "status": "running",
    }
    assert audit.events[-1].path == "/agent/runtime"
    assert audit.events[-1].scope == "agent:read"


def test_protocols_endpoint_returns_read_only_protocol_snapshot():
    client, audit = _client({"agent:protocols:read"})

    response = client.get("/agent/protocols", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "protocols": [
            {
                "name": "amneziawg",
                "status": "running",
                "runtime_type": "docker",
                "capabilities": ["detect", "status"],
                "container_name": "amnezia-awg",
                "interface": "awg0",
                "client_count": 2,
            }
        ]
    }
    assert audit.events[-1].path == "/agent/protocols"
    assert audit.events[-1].scope == "agent:protocols:read"


def test_first_slice_does_not_expose_secret_or_write_routes():
    client, audit = _client(
        {
            "agent:health",
            "agent:read",
            "agent:protocols:read",
            "agent:configs:read",
            "agent:backup:read",
            "agent:backup:full",
            "agent:backup:restore",
            "agent:clients:write",
            "agent:operations:destructive",
        }
    )

    config_response = client.get("/agent/configs/client-1", headers=_auth_headers())
    clients_response = client.post("/agent/clients", headers=_auth_headers())
    reboot_response = client.post("/agent/reboot", headers=_auth_headers())

    assert config_response.status_code == 404
    assert clients_response.status_code == 404
    assert reboot_response.status_code == 404
    assert audit.events == []


def test_agent_api_responses_do_not_contain_secret_markers():
    client, audit = _client({"agent:health", "agent:read", "agent:protocols:read"})

    responses = [
        client.get("/agent/health", headers=_auth_headers()),
        client.get("/agent/version", headers=_auth_headers()),
        client.get("/agent/runtime", headers=_auth_headers()),
        client.get("/agent/protocols", headers=_auth_headers()),
    ]
    joined_response_text = " ".join(response.text for response in responses).lower()

    for response in responses:
        assert response.status_code == 200
    for sensitive_marker in (
        "privatekey",
        "private_key",
        "preshared",
        "vpn://",
        "token",
        RAW_TOKEN.lower(),
    ):
        assert sensitive_marker not in joined_response_text
    assert len(audit.events) == 4
