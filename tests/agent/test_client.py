import pytest

from app.agent.client import AgentClientError, AgentHttpResponse, LocalAgentClient


RAW_TOKEN = "raw-controller-token"


class FakeAgentTransport:
    def __init__(self, responses: dict[str, AgentHttpResponse]):
        self._responses = responses
        self.calls: list[tuple[str, str, dict[str, str], float]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> AgentHttpResponse:
        self.calls.append((method, url, headers, timeout))
        return self._responses[url]


def test_local_agent_client_reads_health_runtime_and_protocols_with_bearer_token():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/health": AgentHttpResponse(
                status_code=200,
                payload={"status": "ok", "service": "local-amnezia-agent"},
            ),
            "http://127.0.0.1:3031/agent/runtime": AgentHttpResponse(
                status_code=200,
                payload={
                    "server_name": "demo-vps",
                    "runtime_type": "docker",
                    "status": "running",
                },
            ),
            "http://127.0.0.1:3031/agent/protocols": AgentHttpResponse(
                status_code=200,
                payload={
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
                },
            ),
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031/",
        bearer_token=RAW_TOKEN,
        transport=transport,
        timeout=2.5,
    )

    health = client.health()
    runtime = client.runtime()
    protocols = client.protocols()

    assert health.status == "ok"
    assert health.service == "local-amnezia-agent"
    assert runtime.server_name == "demo-vps"
    assert runtime.runtime_type == "docker"
    assert runtime.status == "running"
    assert protocols[0].name == "amneziawg"
    assert protocols[0].capabilities == ("detect", "status")
    assert protocols[0].client_count == 2
    assert [call[0] for call in transport.calls] == ["GET", "GET", "GET"]
    assert [call[1] for call in transport.calls] == [
        "http://127.0.0.1:3031/agent/health",
        "http://127.0.0.1:3031/agent/runtime",
        "http://127.0.0.1:3031/agent/protocols",
    ]
    assert all(
        call[2] == {"Authorization": f"Bearer {RAW_TOKEN}", "Accept": "application/json"}
        for call in transport.calls
    )
    assert all(call[3] == 2.5 for call in transport.calls)


def test_local_agent_client_rejects_write_paths_by_not_exposing_write_methods():
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=FakeAgentTransport({}),
    )

    assert not hasattr(client, "create_client")
    assert not hasattr(client, "delete_client")
    assert not hasattr(client, "backup")
    assert not hasattr(client, "restore")
    assert not hasattr(client, "reboot")


def test_local_agent_client_errors_do_not_expose_bearer_token():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/runtime": AgentHttpResponse(
                status_code=403,
                payload={"detail": "missing scope"},
            ),
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    with pytest.raises(AgentClientError) as exc_info:
        client.runtime()

    message = str(exc_info.value)
    assert "403" in message
    assert "missing scope" in message
    assert RAW_TOKEN not in message
    assert RAW_TOKEN not in repr(client)


def test_local_agent_client_rejects_blank_configuration():
    with pytest.raises(ValueError, match="base_url"):
        LocalAgentClient(base_url=" ", bearer_token=RAW_TOKEN)

    with pytest.raises(ValueError, match="bearer_token"):
        LocalAgentClient(base_url="http://127.0.0.1:3031", bearer_token=" ")
