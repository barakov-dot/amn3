from app.bot.workflows import BotWorkflow
from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.services.access import AccessService

SECRET = "bot-workflow-secret-value-with-more-than-32-chars"

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


def test_approve_order_creates_device_with_selected_config_version(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(
        user_id=user_id,
        plan_id=None,
        payment_mode="free_test",
        requested_config_version="amneziawg_v2",
    )
    workflow = BotWorkflow(
        repo=repo,
        admin_telegram_ids={9001},
        access_service=AccessService(
            repo=repo,
            secret_box=SecretBox.from_app_secret(SECRET),
            max_devices_per_user=5,
            duration_days=7,
        ),
        default_server_id=server_id,
    )

    result = workflow.approve_order(
        admin_telegram_id=9001,
        order_id=order_id,
        config_version="amneziawg_v1_5",
    )

    device = repo.get_device(result.device_id)
    assert device["config_version"] == "amneziawg_v1_5"
    assert result.user_telegram_id == 1001
    assert "Access request #1 approved" in result.admin_text
    assert "[Interface]" in result.config_text
    assert result.delivery.config_filename == f"amneziya-device-{result.device_id}.conf"
    assert result.delivery.qr_png_bytes.startswith(b"\x89PNG")
    assert "DefaultVPN" in result.delivery.message_text


def test_approve_order_rejects_non_admin_without_creating_device(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(
        user_id=user_id,
        plan_id=None,
        payment_mode="free_test",
        requested_config_version="amneziawg_v2",
    )
    workflow = BotWorkflow(
        repo=repo,
        admin_telegram_ids={9001},
        access_service=AccessService(
            repo=repo,
            secret_box=SecretBox.from_app_secret(SECRET),
            max_devices_per_user=5,
            duration_days=7,
        ),
        default_server_id=server_id,
    )

    result = workflow.approve_order(
        admin_telegram_id=1001,
        order_id=order_id,
        config_version="amneziawg_v1_5",
    )

    assert result is None
    assert repo.count_active_devices(user_id) == 0


def _repo(tmp_path):
    conn = connect(tmp_path / "bot-workflows.sqlite3")
    initialize_schema(conn)
    return Repository(conn)
