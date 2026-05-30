import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.web.app import create_web_app
from app.web.auth import create_password_hash


def test_servers_redirects_when_unauthenticated(tmp_path: Path):
    client = _client(settings=_settings(tmp_path))

    response = client.get("/servers", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_servers_lists_latest_health_latency_errors_and_device_counts(tmp_path: Path):
    settings = _settings(tmp_path)
    with _repo(Path(settings.database_path)) as repo:
        user_id = _seed_user(repo)
        server_id = _seed_server(repo, name="debian-vps-1")
        _seed_device(repo, user_id=user_id, server_id=server_id, status="active")
        _seed_device(
            repo,
            user_id=user_id,
            server_id=server_id,
            status="revoked",
            vpn_ip="10.44.0.3",
            peer_public_key="revoked-public",
        )
        repo.record_server_health(
            server_id=server_id,
            status="degraded",
            latency_ms=118,
            ssh_ok=True,
            awg_ok=False,
            udp_port_ok=True,
            error="awg service down",
        )
    client = _authenticated_client(settings)

    response = client.get("/servers")

    assert response.status_code == 200
    assert "debian-vps-1" in response.text
    assert "degraded" in response.text
    assert "118 ms" in response.text
    assert "awg service down" in response.text
    assert "1 / 2" in response.text


def test_create_server_from_web_stores_fields_redirects_and_records_action(
    tmp_path: Path,
):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    client = _authenticated_client(settings)
    form = client.get("/servers/new")
    assert form.status_code == 200

    response = client.post(
        "/servers/new",
        data=_server_form(
            _csrf_token(form.text),
            name="edge-1",
            host="203.0.113.20",
            ssh_port="2222",
            endpoint_host="vpn.example.com",
            vpn_port="31000",
            vpn_network_cidr="10.44.0.0/24",
            server_address="10.44.0.1/24",
            server_public_key="server-public-key",
            runtime="host_systemd",
            firewall="ufw",
            status="active",
            max_devices="128",
        ),
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert re.fullmatch(r"/servers/\d+", response.headers["location"])
    server_id = int(response.headers["location"].rsplit("/", 1)[1])
    with _repo(Path(settings.database_path)) as repo:
        server = repo.get_server(server_id)
        assert server["name"] == "edge-1"
        assert server["host"] == "203.0.113.20"
        assert server["ssh_port"] == 2222
        assert server["endpoint_host"] == "vpn.example.com"
        assert server["vpn_port"] == 31000
        assert server["vpn_network_cidr"] == "10.44.0.0/24"
        assert server["server_address"] == "10.44.0.1"
        assert server["server_public_key"] == "server-public-key"
        assert server["runtime"] == "host_systemd"
        assert server["firewall"] == "ufw"
        assert server["status"] == "active"
        assert server["max_devices"] == 128
        action = _latest_admin_action(repo)
        assert action["admin_telegram_id"] == 9001
        assert action["action"] == "web_server_create"
        assert json.loads(action["metadata_json"])["server_id"] == server_id


def test_create_server_rejects_invalid_port_status_without_mutating(tmp_path: Path):
    settings = _settings(tmp_path)
    client = _authenticated_client(settings)
    form = client.get("/servers/new")

    response = client.post(
        "/servers/new",
        data=_server_form(
            _csrf_token(form.text),
            name="invalid-server",
            ssh_port="70000",
            status="retired",
        ),
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert "ssh_port must be in 1..65535" in response.text
    with _repo(Path(settings.database_path)) as repo:
        assert _server_by_name(repo, "invalid-server") is None
        assert _latest_admin_action(repo) is None


def test_server_detail_shows_config_health_and_actions(tmp_path: Path):
    settings = _settings(tmp_path)
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="detail-vps")
        repo.record_server_health(
            server_id=server_id,
            status="online",
            latency_ms=45,
            ssh_ok=True,
            awg_ok=True,
            udp_port_ok=True,
            error=None,
        )
    client = _authenticated_client(settings)

    response = client.get(f"/servers/{server_id}")

    assert response.status_code == 200
    assert "detail-vps" in response.text
    assert "203.0.113.10" in response.text
    assert "10.44.0.1" in response.text
    assert "server-public-key" in response.text
    assert "online" in response.text
    assert "45 ms" in response.text
    assert f"/servers/{server_id}/health/run" in response.text


def test_edit_server_updates_fields_and_records_action(tmp_path: Path):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="edit-vps")
    client = _authenticated_client(settings)
    form = client.get(f"/servers/{server_id}/edit")
    assert form.status_code == 200

    response = client.post(
        f"/servers/{server_id}/edit",
        data=_server_form(
            _csrf_token(form.text),
            name="edit-vps-renamed",
            host="203.0.113.99",
            ssh_port="2200",
            endpoint_host="vpn-renamed.example.com",
            vpn_port="32000",
            vpn_network_cidr="10.55.0.0/24",
            server_address="10.55.0.1/24",
            server_public_key="server-public-updated",
            runtime="docker",
            firewall="nftables",
            status="degraded",
            max_devices="64",
        ),
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/servers/{server_id}"
    with _repo(Path(settings.database_path)) as repo:
        server = repo.get_server(server_id)
        assert server["name"] == "edit-vps-renamed"
        assert server["host"] == "203.0.113.99"
        assert server["ssh_port"] == 2200
        assert server["endpoint_host"] == "vpn-renamed.example.com"
        assert server["vpn_port"] == 32000
        assert server["vpn_network_cidr"] == "10.55.0.0/24"
        assert server["server_address"] == "10.55.0.1"
        assert server["server_public_key"] == "server-public-updated"
        assert server["runtime"] == "docker"
        assert server["firewall"] == "nftables"
        assert server["status"] == "degraded"
        assert server["max_devices"] == 64
        assert _latest_admin_action(repo)["action"] == "web_server_update"


def test_disable_server_marks_status_disabled_without_deleting_row(tmp_path: Path):
    settings = _settings(tmp_path, admin_telegram_ids="9001")
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="disable-vps")
    client = _authenticated_client(settings)
    detail = client.get(f"/servers/{server_id}")
    assert detail.status_code == 200

    response = client.post(
        f"/servers/{server_id}/disable",
        data={"csrf_token": _csrf_token(detail.text)},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/servers/{server_id}"
    with _repo(Path(settings.database_path)) as repo:
        server = repo.get_server(server_id)
        assert server["name"] == "disable-vps"
        assert server["status"] == "disabled"
        assert _latest_admin_action(repo)["action"] == "web_server_disable"


def test_server_health_page_shows_latest_health(tmp_path: Path):
    settings = _settings(tmp_path)
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="health-vps")
        repo.record_server_health(
            server_id=server_id,
            status="offline",
            latency_ms=250,
            ssh_ok=False,
            awg_ok=False,
            udp_port_ok=False,
            error="SSH connection timed out",
        )
    client = _authenticated_client(settings)

    response = client.get(f"/servers/{server_id}/health")

    assert response.status_code == 200
    assert "health-vps" in response.text
    assert "offline" in response.text
    assert "250 ms" in response.text
    assert "SSH connection timed out" in response.text
    assert "ssh: failed" in response.text
    assert "awg: failed" in response.text
    assert "udp port: failed" in response.text


def test_health_run_stores_unknown_when_server_config_is_unavailable(tmp_path: Path):
    settings = _settings(
        tmp_path,
        admin_telegram_ids="9001",
        server_config_path=tmp_path / "missing-servers.yml",
    )
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="not-in-config")
    client = _authenticated_client(settings)
    page = client.get(f"/servers/{server_id}/health")
    assert page.status_code == 200

    response = client.post(
        f"/servers/{server_id}/health/run",
        data={"csrf_token": _csrf_token(page.text)},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/servers/{server_id}/health"
    with _repo(Path(settings.database_path)) as repo:
        latest = repo.get_latest_server_health(server_id)
        assert latest is not None
        assert latest["status"] == "unknown"
        assert latest["latency_ms"] is None
        assert latest["ssh_ok"] == 0
        assert latest["awg_ok"] == 0
        assert latest["udp_port_ok"] == 0
        assert "Add server 'not-in-config' to" in latest["error"]
        action = _latest_admin_action(repo)
        assert action["action"] == "web_server_health_run"
        metadata = json.loads(action["metadata_json"])
        assert metadata["operation_id"] == "server.health.check"
        assert metadata["risk_class"] == "read-only-remote"
        assert metadata["consistency_status"] == "read-only"
        assert metadata["status"] == "unknown"


def test_invalid_csrf_does_not_create_edit_disable_or_run_health(tmp_path: Path):
    settings = _settings(tmp_path)
    with _repo(Path(settings.database_path)) as repo:
        server_id = _seed_server(repo, name="csrf-vps")
    client = _authenticated_client(settings)

    create_response = client.post(
        "/servers/new",
        data=_server_form("missing"),
        follow_redirects=False,
    )
    edit_response = client.post(
        f"/servers/{server_id}/edit",
        data=_server_form(
            "bad-token",
            name="mutated",
            host="203.0.113.200",
            status="disabled",
        ),
        follow_redirects=False,
    )
    disable_response = client.post(
        f"/servers/{server_id}/disable",
        data={"csrf_token": "bad-token"},
        follow_redirects=False,
    )
    run_response = client.post(
        f"/servers/{server_id}/health/run",
        data={"csrf_token": "bad-token"},
        follow_redirects=False,
    )

    assert create_response.status_code == 403
    assert edit_response.status_code == 403
    assert disable_response.status_code == 403
    assert run_response.status_code == 403
    with _repo(Path(settings.database_path)) as repo:
        assert _server_by_name(repo, "default-vps") is None
        server = repo.get_server(server_id)
        assert server["name"] == "csrf-vps"
        assert server["host"] == "203.0.113.10"
        assert server["status"] == "active"
        assert repo.get_latest_server_health(server_id) is None
        assert _latest_admin_action(repo) is None


def _settings(
    tmp_path: Path,
    *,
    admin_telegram_ids: str = "",
    server_config_path: Path | None = None,
) -> Settings:
    return Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        database_path=str(tmp_path / "amneziya.sqlite3"),
        admin_telegram_ids=admin_telegram_ids,
        server_config_path=str(server_config_path or (tmp_path / "servers.yml")),
        web_admin_username="root",
        web_admin_password_hash=create_password_hash(
            "correct-password",
            salt="test-salt",
        ),
        web_admin_session_secret="s" * 32,
        web_admin_session_cookie_secure=True,
    )


def _client(*, settings: Settings) -> TestClient:
    return TestClient(create_web_app(settings), base_url="https://testserver")


def _authenticated_client(settings: Settings) -> TestClient:
    client = _client(settings=settings)
    login_page = client.get("/login")
    response = client.post(
        "/login",
        data={
            "username": "root",
            "password": "correct-password",
            "csrf_token": _csrf_token(login_page.text),
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return client


def _csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


class _repo:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._conn = None

    def __enter__(self) -> Repository:
        self._conn = connect(self._database_path)
        initialize_schema(self._conn)
        return Repository(self._conn)

    def __exit__(self, *args) -> None:
        assert self._conn is not None
        self._conn.close()


def _seed_user(repo: Repository) -> int:
    return repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )


def _seed_server(repo: Repository, *, name: str) -> int:
    return repo.upsert_server_config(
        name=name,
        host="203.0.113.10",
        ssh_port=22,
        endpoint_host="vpn.example.test",
        vpn_port=30001,
        vpn_network_cidr="10.44.0.0/24",
        server_address="10.44.0.1/24",
        server_public_key="server-public-key",
        runtime="host_systemd",
        firewall="ufw",
        max_devices=254,
    )


def _seed_device(
    repo: Repository,
    *,
    user_id: int,
    server_id: int,
    status: str,
    vpn_ip: str = "10.44.0.2",
    peer_public_key: str = "active-public",
) -> int:
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name=f"{status}-device",
        duration_days=7,
        vpn_ip=vpn_ip,
        peer_public_key=peer_public_key,
        peer_private_key_encrypted=f"v1:{status}-private",
        preshared_key_encrypted=f"v1:{status}-psk",
        config_version="amneziawg_v2",
    )
    if status == "revoked":
        repo.revoke_device(
            device_id,
            reason="test",
            revoked_at="2026-05-29T10:00:00Z",
        )
    return device_id


def _server_form(csrf_token: str, **overrides: str) -> dict[str, str]:
    payload = {
        "name": "default-vps",
        "host": "203.0.113.20",
        "ssh_port": "22",
        "endpoint_host": "vpn.example.com",
        "vpn_port": "30001",
        "vpn_network_cidr": "10.44.0.0/24",
        "server_address": "10.44.0.1/24",
        "server_public_key": "server-public-key",
        "runtime": "host_systemd",
        "firewall": "ufw",
        "status": "active",
        "max_devices": "254",
        "csrf_token": csrf_token,
    }
    payload.update(overrides)
    return payload


def _server_by_name(repo: Repository, name: str):
    return repo._conn.execute("SELECT * FROM servers WHERE name = ?", (name,)).fetchone()


def _latest_admin_action(repo: Repository):
    return repo._conn.execute(
        "SELECT * FROM admin_actions ORDER BY id DESC LIMIT 1"
    ).fetchone()
