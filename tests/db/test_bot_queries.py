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


def test_message_template_can_be_read_and_updated_by_key(tmp_path):
    repo = _repo(tmp_path)

    default_text = repo.get_message_template(
        "config_ready",
        default_text="Default text {device_id}",
    )
    repo.set_message_template("config_ready", "Custom text {device_id}")
    updated_text = repo.get_message_template(
        "config_ready",
        default_text="Default text {device_id}",
    )

    assert default_text == "Default text {device_id}"
    assert updated_text == "Custom text {device_id}"


def test_mark_device_connected_records_first_and_last_seen(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")

    repo.mark_device_connected(device_id, connected_at="2026-05-27T12:00:00Z")
    repo.mark_device_connected(device_id, connected_at="2026-05-27T12:30:00Z")

    device = repo.get_device(device_id)
    assert device["first_connected_at"] == "2026-05-27T12:00:00Z"
    assert device["last_connected_at"] == "2026-05-27T12:30:00Z"


def test_get_user_device_requires_matching_owner(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    other_user_id = repo.upsert_user(
        telegram_id=2002,
        username="bob",
        first_name="Bob",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")

    assert repo.get_user_device(user_id=user_id, device_id=device_id)["id"] == device_id
    assert repo.get_user_device(user_id=other_user_id, device_id=device_id) is None


def test_revoke_device_marks_device_revoked_and_frees_allocated_ip(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")

    changed = repo.revoke_device(
        device_id,
        reason="user_requested",
        revoked_at="2026-05-27T12:00:00Z",
    )

    device = repo.get_device(device_id)
    assert changed is True
    assert device["status"] == "revoked"
    assert device["revoked_at"] == "2026-05-27T12:00:00Z"
    assert device["revoke_reason"] == "user_requested"
    assert device["vpn_ip"] not in repo.list_allocated_ips(server_id)


def test_revoke_user_devices_marks_only_owned_active_devices(tmp_path):
    repo = _repo(tmp_path)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    other_user_id = repo.upsert_user(
        telegram_id=2002,
        username="bob",
        first_name="Bob",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    first_id = _create_device(repo, user_id=user_id, server_id=server_id, name="phone")
    second_id = _create_device(repo, user_id=user_id, server_id=server_id, name="laptop")
    other_id = _create_device(
        repo,
        user_id=other_user_id,
        server_id=server_id,
        name="tablet",
    )

    changed = repo.revoke_user_devices(
        user_id,
        reason="user_reset",
        revoked_at="2026-05-27T12:00:00Z",
    )

    assert changed == 2
    assert repo.get_device(first_id)["status"] == "revoked"
    assert repo.get_device(second_id)["status"] == "revoked"
    assert repo.get_device(other_id)["status"] == "active"


def test_set_user_admin_updates_user_role_and_records_audit_action(tmp_path):
    repo = _repo(tmp_path)
    repo.upsert_user(
        telegram_id=9001,
        username="admin",
        first_name="Admin",
        last_name=None,
    )
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )

    changed = repo.set_user_admin(
        telegram_id=1001,
        is_admin=True,
        granted_by_admin_telegram_id=9001,
    )

    user = repo.get_user(user_id)
    assert changed is True
    assert user["is_admin"] == 1
    actions = repo.list_admin_actions_for_target_user(user_id)
    assert actions[0]["action"] == "grant_admin"
    assert actions[0]["target_user_id"] == user_id


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
