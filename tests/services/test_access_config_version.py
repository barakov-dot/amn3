import pytest

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.services.access import AccessService
from app.vpn.config_versions import ConfigVersionError


SECRET = "config-version-secret-value-with-more-than-32-chars"


def _service(tmp_path):
    conn = connect(tmp_path / "access-version.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(
        telegram_id=2001,
        username="version_user",
        first_name="Version",
        last_name="User",
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    service = AccessService(
        repo=repo,
        secret_box=SecretBox.from_app_secret(SECRET),
        max_devices_per_user=5,
        duration_days=7,
    )
    return repo, service, order_id, server_id


def test_approve_order_stores_selected_config_version(tmp_path):
    repo, service, order_id, server_id = _service(tmp_path)

    result = service.approve_order(
        order_id,
        server_id,
        "laptop",
        admin_telegram_id=1,
        config_version="amneziawg_v1_5",
    )

    device = repo.get_device(result.device_id)
    assert "[Interface]" in result.config_text
    assert "[Peer]" in result.config_text
    assert device["config_version"] == "amneziawg_v1_5"


def test_approve_order_uses_requested_order_config_version_by_default(tmp_path):
    conn = connect(tmp_path / "access-requested-version.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(
        telegram_id=2001,
        username="version_user",
        first_name="Version",
        last_name="User",
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(
        user_id=user_id,
        plan_id=None,
        payment_mode="free_test",
        requested_config_version="amneziawg_v1_5",
    )
    service = AccessService(
        repo=repo,
        secret_box=SecretBox.from_app_secret(SECRET),
        max_devices_per_user=5,
        duration_days=7,
    )

    result = service.approve_order(
        order_id,
        server_id,
        "phone",
        admin_telegram_id=1,
    )

    device = repo.get_device(result.device_id)
    assert device["config_version"] == "amneziawg_v1_5"


def test_approve_order_rejects_unknown_config_version_without_creating_device(tmp_path):
    repo, service, order_id, server_id = _service(tmp_path)

    with pytest.raises(ConfigVersionError):
        service.approve_order(
            order_id,
            server_id,
            "laptop",
            admin_telegram_id=1,
            config_version="wireguard",
        )

    assert repo.count_active_devices(repo.get_order(order_id)["user_id"]) == 0
