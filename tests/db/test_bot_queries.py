from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_get_user_by_telegram_id_returns_existing_user(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )

    user = repo.get_user_by_telegram_id(1001)

    assert user["id"] == user_id
    assert user["username"] == "alice"


def test_list_user_devices_returns_latest_active_devices(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    first_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")
    second_id = _create_device(repo, user_id=user_id, server_id=server_id, name="laptop")

    devices = repo.list_user_devices(user_id)

    assert [row["id"] for row in devices] == [second_id, first_id]


def test_list_pending_orders_includes_user_identity(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    order_id = repo.create_order(
        user_id=user_id,
        plan_id=None,
        payment_mode="free_test",
        requested_config_version="amneziawg_v1_5",
    )

    orders = repo.list_pending_orders()

    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert orders[0]["telegram_id"] == 1001
    assert orders[0]["username"] == "alice"
    assert orders[0]["requested_config_version"] == "amneziawg_v1_5"


def test_list_active_devices_with_users_includes_user_identity(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")

    devices = repo.list_active_devices_with_users()

    assert len(devices) == 1
    assert devices[0]["id"] == device_id
    assert devices[0]["telegram_id"] == 1001
    assert devices[0]["username"] == "alice"


def _repo(tmp_path):
    conn = connect(tmp_path / "bot-queries.sqlite3")
    initialize_schema(conn)
    return Repository(conn)


def _create_device(repo, *, user_id, server_id, name):
    return repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name=name,
        duration_days=30,
        vpn_ip=f"10.8.0.{user_id + len(name)}",
        peer_public_key=f"peer-{name}",
        peer_private_key_encrypted=f"encrypted-private-{name}",
        preshared_key_encrypted=f"encrypted-psk-{name}",
        config_version="amneziawg_v2",
    )
