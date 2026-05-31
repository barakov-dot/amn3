from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agent.auth import hash_agent_token
from app.cli import build_parser, run_agent_server, run_agent_token_hash
from app.config.settings import Settings
from app.db.connection import connect
from app.db.schema import initialize_schema


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


def test_run_agent_token_hash_outputs_hash_only_value():
    result = run_agent_token_hash("raw-agent-token")

    assert result == TOKEN_HASH
    assert "raw-agent-token" not in result


def test_run_agent_token_hash_rejects_blank_token():
    with pytest.raises(ValueError, match="token cannot be blank"):
        run_agent_token_hash("   ")


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
    server_config = _write_server_config(tmp_path)
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


def test_run_agent_server_records_allowed_read_audit_in_database(tmp_path: Path):
    server_config = _write_server_config(tmp_path)
    db_path = tmp_path / "amneziya.sqlite3"
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(db_path),
        server_config_path=str(server_config),
        server_name="debian-vps-1",
        local_agent_enabled=True,
        local_agent_token_hash=TOKEN_HASH,
    )

    def fake_uvicorn_run(app, *, host: str, port: int) -> None:
        response = TestClient(app).get(
            "/agent/health",
            headers={"Authorization": "Bearer raw-agent-token"},
        )
        assert response.status_code == 200

    run_agent_server(
        host=None,
        port=None,
        settings=settings,
        uvicorn_run=fake_uvicorn_run,
    )

    conn = connect(db_path)
    try:
        initialize_schema(conn)
        row = conn.execute(
            "SELECT action, metadata_json FROM admin_actions ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row["action"] == "local_agent_read"
    assert "raw-agent-token" not in row["metadata_json"]
    assert '"path": "/agent/health"' in row["metadata_json"]
    assert '"scope": "agent:health"' in row["metadata_json"]
    assert '"token_id": "local-controller"' in row["metadata_json"]


def _write_server_config(tmp_path: Path) -> Path:
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
    return server_config
