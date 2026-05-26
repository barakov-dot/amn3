import sqlite3

import pytest

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def test_repository_creates_user_server_order_and_device(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id = repo.upsert_user(
        telegram_id=1001,
        username="alice",
        first_name="Alice",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="iPhone",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="public",
        peer_private_key_encrypted="v1:encrypted",
        preshared_key_encrypted="v1:psk",
        config_version="amneziawg_v2",
    )

    assert repo.count_active_devices(user_id) == 1
    assert repo.get_order(order_id)["status"] == "manual_review"
    assert repo.get_device(device_id)["vpn_ip"] == "10.8.0.2"


def test_invalid_device_status_fails(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id, server_id = _create_user_and_server(repo)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO devices (
                user_id,
                server_id,
                name,
                duration_days,
                status,
                vpn_ip,
                peer_public_key,
                peer_private_key_encrypted,
                preshared_key_encrypted,
                config_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                server_id,
                "invalid",
                7,
                "unknown",
                "10.8.0.20",
                "invalid-public",
                "v1:invalid-private",
                "v1:invalid-psk",
                "amneziawg_v2",
            ),
        )


def test_list_allocated_ips_only_returns_reserved_statuses(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id, server_id = _create_user_and_server(repo)
    for index, status in enumerate(
        ["pending", "active", "revoked", "expired", "failed"],
        start=2,
    ):
        _insert_device(
            conn,
            user_id=user_id,
            server_id=server_id,
            vpn_ip=f"10.8.0.{index}",
            peer_public_key=f"public-{status}",
            status=status,
        )

    assert repo.list_allocated_ips(server_id) == ["10.8.0.2", "10.8.0.3"]


def test_device_ip_can_be_reused_after_revocation(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id, server_id = _create_user_and_server(repo)
    _insert_device(
        conn,
        user_id=user_id,
        server_id=server_id,
        vpn_ip="10.8.0.44",
        peer_public_key="old-public",
        status="revoked",
    )

    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="replacement",
        duration_days=7,
        vpn_ip="10.8.0.44",
        peer_public_key="new-public",
        peer_private_key_encrypted="v1:new-private",
        preshared_key_encrypted="v1:new-psk",
        config_version="amneziawg_v2",
    )

    assert repo.get_device(device_id)["vpn_ip"] == "10.8.0.44"


def test_device_requires_existing_user_and_server(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    with pytest.raises(sqlite3.IntegrityError):
        repo.create_device(
            user_id=999,
            server_id=999,
            name="orphan",
            duration_days=7,
            vpn_ip="10.8.0.50",
            peer_public_key="orphan-public",
            peer_private_key_encrypted="v1:orphan-private",
            preshared_key_encrypted="v1:orphan-psk",
            config_version="amneziawg_v2",
        )


def test_mark_order_fulfilled_rejects_device_owned_by_another_user(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_a_id, server_id = _create_user_and_server(repo)
    user_b_id = repo.upsert_user(
        telegram_id=2002,
        username="carol",
        first_name="Carol",
        last_name=None,
    )
    order_a_id = repo.create_order(
        user_id=user_a_id,
        plan_id=None,
        payment_mode="free_test",
    )
    device_b_id = repo.create_device(
        user_id=user_b_id,
        server_id=server_id,
        name="Carol phone",
        duration_days=7,
        vpn_ip="10.8.0.80",
        peer_public_key="carol-public",
        peer_private_key_encrypted="v1:carol-private",
        preshared_key_encrypted="v1:carol-psk",
        config_version="amneziawg_v2",
    )

    with pytest.raises(ValueError):
        repo.mark_order_fulfilled(order_a_id, device_b_id)

    order = repo.get_order(order_a_id)
    assert order["status"] == "manual_review"
    assert order["device_id"] is None


def test_mark_order_fulfilled_requires_existing_order(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    user_id, server_id = _create_user_and_server(repo)
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="known device",
        duration_days=7,
        vpn_ip="10.8.0.90",
        peer_public_key="known-public",
        peer_private_key_encrypted="v1:known-private",
        preshared_key_encrypted="v1:known-psk",
        config_version="amneziawg_v2",
    )

    with pytest.raises(LookupError):
        repo.mark_order_fulfilled(999, device_id)


def _create_user_and_server(repo: Repository) -> tuple[int, int]:
    user_id = repo.upsert_user(
        telegram_id=2001,
        username="bob",
        first_name="Bob",
        last_name=None,
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    return user_id, server_id


def _insert_device(
    conn: sqlite3.Connection,
    *,
    user_id: int,
    server_id: int,
    vpn_ip: str,
    peer_public_key: str,
    status: str,
) -> None:
    conn.execute(
        """
        INSERT INTO devices (
            user_id,
            server_id,
            name,
            duration_days,
            status,
            vpn_ip,
            peer_public_key,
            peer_private_key_encrypted,
            preshared_key_encrypted,
            config_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            server_id,
            f"{status}-device",
            7,
            status,
            vpn_ip,
            peer_public_key,
            f"v1:{status}-private",
            f"v1:{status}-psk",
            "amneziawg_v2",
        ),
    )
    conn.commit()
