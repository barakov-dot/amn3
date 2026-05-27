from app.bot.workflows import BotWorkflow
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_request_access_creates_order_with_selected_config_version(tmp_path):
    repo = _repo(tmp_path)
    workflow = BotWorkflow(repo=repo, admin_telegram_ids={9001})

    result = workflow.request_access(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
        config_version="amneziawg_v1_5",
    )

    order = repo.get_order(result.order_id)
    assert order["requested_config_version"] == "amneziawg_v1_5"
    assert "AmneziaWG 1.5" in result.text


def test_build_user_traffic_views_reads_user_devices_and_latest_stats(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=30,
        vpn_ip="10.8.0.2",
        peer_public_key="peer-phone",
        peer_private_key_encrypted="encrypted-private-phone",
        preshared_key_encrypted="encrypted-psk-phone",
        config_version="amneziawg_v2",
    )
    repo.record_device_traffic_snapshot(
        device_id=device_id,
        server_id=server_id,
        peer_public_key="peer-phone",
        rx_bytes=1024,
        tx_bytes=2048,
        source="test",
        collected_at="2026-05-27T12:00:00Z",
    )
    workflow = BotWorkflow(repo=repo, admin_telegram_ids={9001})

    views = workflow.build_user_traffic_views(
        telegram_id=1001,
        now="2026-05-27T12:30:00Z",
    )

    assert len(views) == 1
    assert views[0].device_name == "phone"
    assert views[0].total == "3.0 KiB"


def test_build_admin_traffic_views_requires_admin(tmp_path):
    repo = _repo(tmp_path)
    workflow = BotWorkflow(repo=repo, admin_telegram_ids={9001})

    assert workflow.build_admin_traffic_views(
        admin_telegram_id=1001,
        now="2026-05-27T12:30:00Z",
    ) == []


def _repo(tmp_path):
    conn = connect(tmp_path / "bot-workflows.sqlite3")
    initialize_schema(conn)
    return Repository(conn)
