import base64
import sqlite3

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.security.crypto import SecretBox
from app.services.access import (
    AccessService,
    IpAllocationConflict,
    MaxDevicesReached,
    OrderAlreadyFulfilled,
    OrderNotApprovable,
)


def test_approve_order_creates_active_device_with_encrypted_secrets(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    secret_box = SecretBox.from_app_secret("test-secret-for-access-service-1234567890")
    service = AccessService(repo=repo, secret_box=secret_box)
    result = service.approve_order(order_id=order_id, server_id=server_id, device_name="iPhone", admin_telegram_id=999)

    device = repo.get_device(result.device_id)
    assert device["status"] == "active"
    assert device["vpn_ip"] == "10.8.0.2"
    assert device["peer_private_key_encrypted"].startswith("v1:")
    assert "PrivateKey =" in result.config_text
    private_key = secret_box.decrypt_text(device["peer_private_key_encrypted"])
    derived_public_key = base64.b64encode(
        x25519.X25519PrivateKey.from_private_bytes(base64.b64decode(private_key))
        .public_key()
        .public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    ).decode("ascii")
    assert device["peer_public_key"] == derived_public_key


def test_approve_order_enforces_max_devices(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"), max_devices_per_user=1)
    first_order = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    second_order = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    service.approve_order(first_order, server_id, "iPhone", admin_telegram_id=999)

    with pytest.raises(MaxDevicesReached):
        service.approve_order(second_order, server_id, "Laptop", admin_telegram_id=999)


def test_approve_order_rejects_already_fulfilled_order_without_creating_device(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))
    first_result = service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    with pytest.raises(OrderAlreadyFulfilled):
        service.approve_order(order_id, server_id, "Laptop", admin_telegram_id=999)

    order = repo.get_order(order_id)
    assert repo.count_active_devices(user_id) == 1
    assert order["device_id"] == first_result.device_id


@pytest.mark.parametrize("status", ["payment_pending", "rejected"])
def test_approve_order_rejects_non_approvable_order_without_creating_device(tmp_path, status):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    original_order = dict(repo.get_order(order_id))

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))

    with pytest.raises(OrderNotApprovable, match=status):
        service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    assert repo.count_active_devices(user_id) == 0
    assert dict(repo.get_order(order_id)) == original_order


def test_approve_order_rolls_back_device_and_order_when_admin_audit_fails(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = FailingAdminActionRepository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))

    with pytest.raises(RuntimeError, match="audit failed"):
        service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    order = repo.get_order(order_id)
    assert repo.count_active_devices(user_id) == 0
    assert order["status"] == "manual_review"
    assert order["device_id"] is None


def test_approve_order_retries_ip_allocation_after_duplicate_ip_race(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = DuplicateIpRaceRepository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))
    result = service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    assert repo.get_device(result.device_id)["vpn_ip"] == "10.8.0.3"


def test_approve_order_raises_clear_error_after_duplicate_ip_retries_are_exhausted(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = AlwaysDuplicateIpRepository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))

    with pytest.raises(IpAllocationConflict):
        service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    order = repo.get_order(order_id)
    assert repo.count_active_devices(user_id) == 0
    assert order["status"] == "manual_review"
    assert order["device_id"] is None


def test_approve_order_raises_clear_error_when_retry_refresh_exhausts_ips(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = LastFreeIpConsumedRepository(conn)
    user_id = repo.upsert_user(telegram_id=1001, username="alice", first_name="Alice", last_name=None)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/30")
    order_id = repo.create_order(user_id=user_id, plan_id=None, payment_mode="free_test")

    service = AccessService(repo=repo, secret_box=SecretBox.from_app_secret("test-secret-for-access-service-1234567890"))

    with pytest.raises(IpAllocationConflict):
        service.approve_order(order_id, server_id, "iPhone", admin_telegram_id=999)

    order = repo.get_order(order_id)
    assert repo.count_active_devices(user_id) == 0
    assert order["status"] == "manual_review"
    assert order["device_id"] is None


class FailingAdminActionRepository(Repository):
    def record_admin_action(self, **kwargs):
        raise RuntimeError("audit failed")


class DuplicateIpRaceRepository(Repository):
    def __init__(self, conn):
        super().__init__(conn)
        self._duplicate_seen = False

    def list_allocated_ips(self, server_id: int) -> list[str]:
        allocated_ips = super().list_allocated_ips(server_id)
        if self._duplicate_seen and "10.8.0.2" not in allocated_ips:
            allocated_ips.append("10.8.0.2")
        return allocated_ips

    def create_device(self, **kwargs):
        if kwargs["vpn_ip"] == "10.8.0.2" and not self._duplicate_seen:
            self._duplicate_seen = True
            raise sqlite3.IntegrityError("UNIQUE constraint failed: devices.server_id, devices.vpn_ip")
        return super().create_device(**kwargs)


class AlwaysDuplicateIpRepository(Repository):
    def create_device(self, **kwargs):
        raise sqlite3.IntegrityError("UNIQUE constraint failed: devices.server_id, devices.vpn_ip")


class LastFreeIpConsumedRepository(Repository):
    def __init__(self, conn):
        super().__init__(conn)
        self._duplicate_seen = False

    def list_allocated_ips(self, server_id: int) -> list[str]:
        allocated_ips = super().list_allocated_ips(server_id)
        if self._duplicate_seen and "10.8.0.2" not in allocated_ips:
            allocated_ips.append("10.8.0.2")
        return allocated_ips

    def create_device(self, **kwargs):
        self._duplicate_seen = True
        raise sqlite3.IntegrityError("UNIQUE constraint failed: devices.server_id, devices.vpn_ip")
