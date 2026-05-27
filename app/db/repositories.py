import ipaddress
import json
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._transaction_depth = 0

    @contextmanager
    def transaction(self) -> Iterator[None]:
        is_outermost = self._transaction_depth == 0
        if is_outermost:
            self._conn.execute("BEGIN")

        self._transaction_depth += 1
        try:
            yield
        except Exception:
            self._transaction_depth -= 1
            if is_outermost:
                self._conn.rollback()
            raise
        else:
            self._transaction_depth -= 1
            if is_outermost:
                self._conn.commit()

    def upsert_user(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> int:
        self._conn.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                updated_at = CURRENT_TIMESTAMP
            """,
            (telegram_id, username, first_name, last_name),
        )
        self._commit()
        row = self._conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()
        return int(row["id"])

    def ensure_default_server(self, *, name: str, network_cidr: str) -> int:
        self._conn.execute(
            """
            INSERT INTO servers (
                name,
                host,
                ssh_port,
                endpoint_host,
                vpn_port,
                vpn_network_cidr,
                server_address,
                server_public_key,
                runtime,
                firewall,
                max_devices
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO NOTHING
            """,
            (
                name,
                "local",
                22,
                "127.0.0.1",
                30001,
                network_cidr,
                _first_host_address(network_cidr),
                "local-server-public-key",
                "host_systemd",
                "ufw",
                254,
            ),
        )
        self._commit()
        row = self._conn.execute(
            "SELECT id FROM servers WHERE name = ?",
            (name,),
        ).fetchone()
        return int(row["id"])

    def create_order(
        self,
        *,
        user_id: int,
        plan_id: str | None,
        payment_mode: str,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO orders (user_id, plan_id, payment_mode)
            VALUES (?, ?, ?)
            """,
            (user_id, plan_id, payment_mode),
        )
        self._commit()
        return int(cursor.lastrowid)

    def get_order(self, order_id: int) -> sqlite3.Row:
        return self._fetch_one("SELECT * FROM orders WHERE id = ?", (order_id,))

    def create_device(
        self,
        *,
        user_id: int,
        server_id: int,
        name: str,
        duration_days: int,
        vpn_ip: str,
        peer_public_key: str,
        peer_private_key_encrypted: str,
        preshared_key_encrypted: str,
        config_version: str,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO devices (
                user_id,
                server_id,
                name,
                activated_at,
                expires_at,
                duration_days,
                vpn_ip,
                peer_public_key,
                peer_private_key_encrypted,
                preshared_key_encrypted,
                config_version
            )
            VALUES (
                ?,
                ?,
                ?,
                CURRENT_TIMESTAMP,
                datetime(CURRENT_TIMESTAMP, ?),
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                user_id,
                server_id,
                name,
                f"+{duration_days} days",
                duration_days,
                vpn_ip,
                peer_public_key,
                peer_private_key_encrypted,
                preshared_key_encrypted,
                config_version,
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def get_device(self, device_id: int) -> sqlite3.Row:
        return self._fetch_one("SELECT * FROM devices WHERE id = ?", (device_id,))

    def get_device_by_server_peer_public_key(
        self,
        server_id: int,
        peer_public_key: str,
    ) -> sqlite3.Row | None:
        return self._conn.execute(
            """
            SELECT *
            FROM devices
            WHERE server_id = ?
              AND peer_public_key = ?
            """,
            (server_id, peer_public_key),
        ).fetchone()

    def count_active_devices(self, user_id: int) -> int:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS device_count
            FROM devices
            WHERE user_id = ?
              AND status = 'active'
            """,
            (user_id,),
        ).fetchone()
        return int(row["device_count"])

    def list_allocated_ips(self, server_id: int) -> list[str]:
        rows = self._conn.execute(
            """
            SELECT vpn_ip
            FROM devices
            WHERE server_id = ?
              AND status IN ('pending', 'active')
            ORDER BY id
            """,
            (server_id,),
        ).fetchall()
        return [str(row["vpn_ip"]) for row in rows]

    def get_server(self, server_id: int) -> sqlite3.Row:
        return self._fetch_one("SELECT * FROM servers WHERE id = ?", (server_id,))

    def mark_order_fulfilled(self, order_id: int, device_id: int) -> None:
        order = self.get_order(order_id)
        device = self.get_device(device_id)
        if order["user_id"] != device["user_id"]:
            raise ValueError("Order and device must belong to the same user")

        self._conn.execute(
            """
            UPDATE orders
            SET device_id = ?,
                status = 'fulfilled',
                fulfilled_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (device_id, order_id),
        )
        self._commit()

    def record_admin_action(
        self,
        *,
        admin_telegram_id: int,
        action: str,
        target_user_id: int | None = None,
        target_device_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO admin_actions (
                admin_telegram_id,
                action,
                target_user_id,
                target_device_id,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                admin_telegram_id,
                action,
                target_user_id,
                target_device_id,
                json.dumps(metadata, sort_keys=True) if metadata is not None else None,
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def record_device_traffic_snapshot(
        self,
        *,
        device_id: int,
        server_id: int,
        peer_public_key: str,
        rx_bytes: int,
        tx_bytes: int,
        source: str,
        collected_at: str,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO device_traffic_snapshots (
                device_id,
                server_id,
                peer_public_key,
                rx_bytes,
                tx_bytes,
                source,
                collected_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device_id,
                server_id,
                peer_public_key,
                rx_bytes,
                tx_bytes,
                source,
                collected_at,
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def get_latest_device_traffic(self, device_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            """
            SELECT *
            FROM device_traffic_snapshots
            WHERE device_id = ?
            ORDER BY collected_at DESC, id DESC
            LIMIT 1
            """,
            (device_id,),
        ).fetchone()

    def _commit(self) -> None:
        if self._transaction_depth == 0:
            self._conn.commit()

    def _fetch_one(self, query: str, params: tuple[Any, ...]) -> sqlite3.Row:
        row = self._conn.execute(query, params).fetchone()
        if row is None:
            raise LookupError("record not found")
        return row


def _first_host_address(network_cidr: str) -> str:
    network = ipaddress.ip_network(network_cidr, strict=False)
    return str(next(network.hosts(), network.network_address))
