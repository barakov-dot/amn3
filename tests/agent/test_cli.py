from pathlib import Path

import pytest

from app.agent.auth import hash_agent_token
from app.agent.client import AgentHealth, AgentProtocol, AgentRuntime
from app.cli import build_parser, run_agent_probe, run_agent_server, run_agent_token_hash
from app.config.settings import Settings


TOKEN_HASH = hash_agent_token("raw-agent-token")


def test_cli_accepts_agent_hash_token_argument():
    parser = build_parser()

    args = parser.parse_args(["agent", "hash-token", "--token", "raw-agent-token"])

    assert args.command == "agent"
    assert args.agent_command == "hash-token"
    assert args.token == "raw-agent-token"


def test_cli_accepts_agent_serve_arguments():
    parser = build_parser()

    args = parser.parse_args(["agent", "serve", "--host", "127.0.0.1", "--port", "3041"])

    assert args.command == "agent"
    assert args.agent_command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 3041


def test_cli_accepts_agent_probe_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "agent",
            "probe",
            "--base-url",
            "http://127.0.0.1:3031",
            "--token",
            "raw-agent-token",
        ]
    )

    assert args.command == "agent"
    assert args.agent_command == "probe"
    assert args.base_url == "http://127.0.0.1:3031"
    assert args.token == "raw-agent-token"


def test_run_agent_token_hash_outputs_hash_only_value():
    result = run_agent_token_hash("raw-agent-token")

    assert result == TOKEN_HASH
    assert "raw-agent-token" not in result


def test_run_agent_token_hash_rejects_blank_token():
    with pytest.raises(ValueError, match="token cannot be blank"):
        run_agent_token_hash("   ")


def test_run_agent_probe_returns_read_only_summary_without_raw_token():
    calls = []

    class FakeClient:
        def __init__(self, *, base_url: str, bearer_token: str):
            calls.append(("init", base_url, bearer_token))

        def health(self) -> AgentHealth:
            calls.append(("health",))
            return AgentHealth(status="ok", service="local-amnezia-agent")

        def runtime(self) -> AgentRuntime:
            calls.append(("runtime",))
            return AgentRuntime(
                server_name="demo-vps",
                runtime_type="docker",
                status="running",
            )

        def protocols(self) -> tuple[AgentProtocol, ...]:
            calls.append(("protocols",))
            return (
                AgentProtocol(
                    name="amneziawg",
                    status="running",
                    runtime_type="docker",
                    capabilities=("detect", "status"),
                    container_name="amnezia-awg",
                    interface="awg0",
                    client_count=2,
                ),
            )

    result = run_agent_probe(
        base_url="http://127.0.0.1:3031/",
        raw_token="raw-agent-token",
        client_factory=FakeClient,
    )

    assert calls == [
        ("init", "http://127.0.0.1:3031/", "raw-agent-token"),
        ("health",),
        ("runtime",),
        ("protocols",),
    ]
    assert "health: ok (local-amnezia-agent)" in result
    assert "runtime: demo-vps docker running" in result
    assert "protocol: amneziawg docker running interface=awg0 container=amnezia-awg clients=2 capabilities=detect,status" in result
    assert "raw-agent-token" not in result
    assert "create" not in result.lower()
    assert "delete" not in result.lower()


def test_run_agent_server_requires_enabled_agent(tmp_path: Path):
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        local_agent_enabled=False,
    )

    with pytest.raises(ValueError, match="LOCAL_AGENT_ENABLED"):
        run_agent_server(host=None, port=None, settings=settings)


def test_run_agent_server_invokes_uvicorn_with_selected_host_and_port(tmp_path: Path):
    server_config = tmp_path / "servers.yml"
    server_config.write_text(
        """
servers:
  - name: debian-vps-1
    enabled: true
    location: default
    ssh:
      host: 127.0.0.1
      port: 22
      user: root
      auth:
        type: key
    vpn:
      endpoint_host: 127.0.0.1
      port: 30001
      interface: awg0
      network_cidr: 10.8.1.0/24
      server_address: 10.8.1.1/24
      dns: 1.1.1.1
      allowed_ips: 0.0.0.0/0
      max_devices: 254
      server_public_key: server-public-key
    firewall:
      provider: ufw
      open_vpn_port: true
    runtime:
      type: docker
      container_name: amnezia-awg2
      config_path: /opt/amnezia/awg/awg0.conf
""",
        encoding="utf-8",
    )
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        server_config_path=str(server_config),
        server_name="debian-vps-1",
        local_agent_enabled=True,
        local_agent_host="127.0.0.1",
        local_agent_port=3031,
        local_agent_token_hash=TOKEN_HASH,
    )
    calls = []

    def fake_uvicorn_run(app, *, host: str, port: int) -> None:
        calls.append({"docs_url": app.docs_url, "host": host, "port": port})

    run_agent_server(
        host="127.0.0.2",
        port=3041,
        settings=settings,
        uvicorn_run=fake_uvicorn_run,
    )

    assert calls == [{"docs_url": None, "host": "127.0.0.2", "port": 3041}]
