import sqlite3

import pytest

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


def _repo(tmp_path):
    conn = connect(tmp_path / "traffic.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="traffic_user",
        first_name="Traffic",
        last_name="User",
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="known-peer",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )
    return repo, server_id, device_id


def test_record_and_get_latest_device_traffic(tmp_path):
    repo, server_id, device_id = _repo(tmp_path)

    repo.record_device_traffic_snapshot(
        device_id=device_id,
        server_id=server_id,
        peer_public_key="known-peer",
        rx_bytes=1024,
        tx_bytes=2048,
        source="fake",
        collected_at="2026-05-27T10:00:00Z",
    )
    latest_id = repo.record_device_traffic_snapshot(
        device_id=device_id,
        server_id=server_id,
        peer_public_key="known-peer",
        rx_bytes=4096,
        tx_bytes=8192,
        source="fake",
        collected_at="2026-05-27T11:00:00Z",
    )

    latest = repo.get_latest_device_traffic(device_id)

    assert latest is not None
    assert latest["id"] == latest_id
    assert latest["rx_bytes"] == 4096
    assert latest["tx_bytes"] == 8192


def test_traffic_snapshot_rejects_negative_counters(tmp_path):
    repo, server_id, device_id = _repo(tmp_path)

    with pytest.raises(sqlite3.IntegrityError):
        repo.record_device_traffic_snapshot(
            device_id=device_id,
            server_id=server_id,
            peer_public_key="known-peer",
            rx_bytes=-1,
            tx_bytes=0,
            source="fake",
            collected_at="2026-05-27T10:00:00Z",
        )


def test_get_device_by_server_peer_public_key(tmp_path):
    repo, server_id, device_id = _repo(tmp_path)

    device = repo.get_device_by_server_peer_public_key(server_id, "known-peer")
    missing = repo.get_device_by_server_peer_public_key(server_id, "unknown-peer")

    assert device is not None
    assert device["id"] == device_id
    assert missing is None
