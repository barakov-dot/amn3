from __future__ import annotations

import ipaddress
import sqlite3
from dataclasses import dataclass

from app.db.repositories import Repository
from app.security.crypto import SecretBox
from app.vpn.amneziawg_v2.config import ClientConfigInput
from app.vpn.amneziawg_v2.keys import generate_key, generate_keypair
from app.vpn.config_versions import render_client_config_for_version, validate_config_version


IP_ALLOCATION_ATTEMPTS = 3


class MaxDevicesReached(ValueError):
    pass


class OrderAlreadyFulfilled(ValueError):
    pass


class OrderNotApprovable(ValueError):
    pass


class IpAllocationConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class AccessApprovalResult:
    device_id: int
    config_text: str


class AccessService:
    def __init__(
        self,
        *,
        repo: Repository,
        secret_box: SecretBox,
        max_devices_per_user: int = 5,
        duration_days: int = 30,
    ) -> None:
        self._repo = repo
        self._secret_box = secret_box
        self._max_devices_per_user = max_devices_per_user
        self._duration_days = duration_days

    def approve_order(
        self,
        order_id: int,
        server_id: int,
        device_name: str,
        *,
        admin_telegram_id: int,
        config_version: str | None = None,
    ) -> AccessApprovalResult:
        with self._repo.transaction():
            return self._approve_order(
                order_id=order_id,
                server_id=server_id,
                device_name=device_name,
                admin_telegram_id=admin_telegram_id,
                config_version=config_version,
            )

    def _approve_order(
        self,
        *,
        order_id: int,
        server_id: int,
        device_name: str,
        admin_telegram_id: int,
        config_version: str | None,
    ) -> AccessApprovalResult:
        order = self._repo.get_order(order_id)
        config_version = validate_config_version(
            config_version or str(order["requested_config_version"])
        )
        user_id = int(order["user_id"])
        if order["status"] == "fulfilled" or order["device_id"] is not None:
            raise OrderAlreadyFulfilled("Order has already been fulfilled")
        if order["status"] not in {"manual_review", "approved"}:
            raise OrderNotApprovable(
                f"Order {order_id} cannot be approved from status {order['status']}"
            )

        if self._repo.count_active_devices(user_id) >= self._max_devices_per_user:
            raise MaxDevicesReached("User has reached the maximum number of active devices")

        server = self._repo.get_server(server_id)
        keypair = generate_keypair()
        preshared_key = generate_key()

        device_id, config_text = self._create_device_with_allocated_ip(
            user_id=user_id,
            server_id=server_id,
            device_name=device_name,
            server=server,
            private_key=keypair.private_key,
            public_key=keypair.public_key,
            preshared_key=preshared_key,
            config_version=config_version,
        )
        self._repo.mark_order_fulfilled(order_id, device_id)
        self._repo.record_admin_action(
            admin_telegram_id=admin_telegram_id,
            action="access.approve_order",
            target_user_id=user_id,
            target_device_id=device_id,
            metadata={"order_id": order_id, "server_id": server_id},
        )

        return AccessApprovalResult(device_id=device_id, config_text=config_text)

    def _create_device_with_allocated_ip(
        self,
        *,
        user_id: int,
        server_id: int,
        device_name: str,
        server,
        private_key: str,
        public_key: str,
        preshared_key: str,
        config_version: str,
    ) -> tuple[int, str]:
        last_error: sqlite3.IntegrityError | None = None

        for _ in range(IP_ALLOCATION_ATTEMPTS):
            try:
                vpn_ip = _allocate_vpn_ip(
                    network_cidr=str(server["vpn_network_cidr"]),
                    server_address=server["server_address"],
                    allocated_ips=self._repo.list_allocated_ips(server_id),
                )
            except RuntimeError as exc:
                raise IpAllocationConflict("Could not allocate a unique VPN IP address") from exc
            config_text = render_client_config_for_version(
                ClientConfigInput(
                    private_key=private_key,
                    address=f"{vpn_ip}/32",
                    dns="1.1.1.1",
                    server_public_key=str(server["server_public_key"]),
                    preshared_key=preshared_key,
                    endpoint=f"{server['endpoint_host']}:{server['vpn_port']}",
                    allowed_ips="0.0.0.0/0",
                    persistent_keepalive=25,
                    jc=4,
                    jmin=40,
                    jmax=70,
                    s1=0,
                    s2=0,
                    h1=1,
                    h2=2,
                    h3=3,
                    h4=4,
                ),
                config_version,
            )

            try:
                device_id = self._repo.create_device(
                    user_id=user_id,
                    server_id=server_id,
                    name=device_name,
                    duration_days=self._duration_days,
                    vpn_ip=vpn_ip,
                    peer_public_key=public_key,
                    peer_private_key_encrypted=self._secret_box.encrypt_text(private_key),
                    preshared_key_encrypted=self._secret_box.encrypt_text(preshared_key),
                    config_version=config_version,
                )
            except sqlite3.IntegrityError as exc:
                if not _is_duplicate_ip_integrity_error(exc):
                    raise
                last_error = exc
            else:
                return device_id, config_text

        raise IpAllocationConflict("Could not allocate a unique VPN IP address") from last_error


def _allocate_vpn_ip(
    *,
    network_cidr: str,
    server_address: str | None,
    allocated_ips: list[str],
) -> str:
    network = ipaddress.ip_network(network_cidr, strict=False)
    reserved = {ipaddress.ip_address(ip) for ip in allocated_ips}
    if server_address is not None:
        reserved.add(ipaddress.ip_address(server_address))

    for ip_address in network.hosts():
        if ip_address not in reserved:
            return str(ip_address)

    raise RuntimeError("No available VPN IP addresses")


def _is_duplicate_ip_integrity_error(exc: sqlite3.IntegrityError) -> bool:
    message = str(exc)
    return (
        "vpn_ip" in message
        or "idx_devices_reserved_ip_unique" in message
    ) and "UNIQUE constraint failed" in message
