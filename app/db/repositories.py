import ipaddress
import json
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any

DEFAULT_PLAN_DAYS = (3, 7, 10, 14, 30, 60, 90, 180)
USER_STATUSES = {"active", "blocked", "deleted"}
SERVER_STATUSES = {"active", "degraded", "disabled"}


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

    def get_user_by_telegram_id(self, telegram_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()

    def get_user(self, user_id: int) -> sqlite3.Row:
        return self._fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    def update_user_email(self, user_id: int, email: str | None) -> None:
        user = self.get_user(user_id)
        email_verified_at = user["email_verified_at"]
        if user["email"] != email:
            email_verified_at = None

        self._conn.execute(
            """
            UPDATE users
            SET email = ?,
                email_verified_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (email, email_verified_at, user_id),
        )
        self._commit()

    def create_user_for_admin(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        status: str,
        is_admin: bool,
    ) -> int:
        _validate_user_status(status)
        if self.get_user_by_telegram_id(telegram_id) is not None:
            raise ValueError("telegram_id already exists")

        cursor = self._conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name,
                last_name,
                email,
                status,
                is_admin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                username,
                first_name,
                last_name,
                email,
                status,
                int(is_admin),
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def update_user_for_admin(
        self,
        *,
        user_id: int,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        status: str,
        is_admin: bool,
    ) -> None:
        _validate_user_status(status)
        user = self.get_user(user_id)
        email_verified_at = user["email_verified_at"]
        if user["email"] != email:
            email_verified_at = None

        self._conn.execute(
            """
            UPDATE users
            SET telegram_id = ?,
                username = ?,
                first_name = ?,
                last_name = ?,
                email = ?,
                email_verified_at = ?,
                status = ?,
                is_admin = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                telegram_id,
                username,
                first_name,
                last_name,
                email,
                email_verified_at,
                status,
                int(is_admin),
                user_id,
            ),
        )
        self._commit()

    def set_user_status_for_admin(self, user_id: int, status: str) -> None:
        _validate_user_status(status)
        self._conn.execute(
            """
            UPDATE users
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, user_id),
        )
        self._commit()

    def mark_user_email_verified(self, user_id: int, verified_at: str) -> None:
        self._conn.execute(
            """
            UPDATE users
            SET email_verified_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (verified_at, user_id),
        )
        self._commit()

    def set_user_admin(
        self,
        *,
        telegram_id: int,
        is_admin: bool,
        granted_by_admin_telegram_id: int,
    ) -> bool:
        user = self.get_user_by_telegram_id(telegram_id)
        if user is None:
            return False
        self._conn.execute(
            """
            UPDATE users
            SET is_admin = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = ?
            """,
            (int(is_admin), telegram_id),
        )
        self.record_admin_action(
            admin_telegram_id=granted_by_admin_telegram_id,
            action="grant_admin" if is_admin else "revoke_admin",
            target_user_id=int(user["id"]),
            metadata={"target_telegram_id": telegram_id},
        )
        self._commit()
        return True

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

    def upsert_server_config(
        self,
        *,
        name: str,
        host: str,
        ssh_port: int,
        endpoint_host: str,
        vpn_port: int,
        vpn_network_cidr: str,
        server_address: str,
        server_public_key: str,
        runtime: str,
        firewall: str,
        max_devices: int,
    ) -> int:
        normalized_server_address = _host_address(server_address)
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
            ON CONFLICT(name) DO UPDATE SET
                host = excluded.host,
                ssh_port = excluded.ssh_port,
                endpoint_host = excluded.endpoint_host,
                vpn_port = excluded.vpn_port,
                vpn_network_cidr = excluded.vpn_network_cidr,
                server_address = excluded.server_address,
                server_public_key = excluded.server_public_key,
                runtime = excluded.runtime,
                firewall = excluded.firewall,
                max_devices = excluded.max_devices,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                name,
                host,
                ssh_port,
                endpoint_host,
                vpn_port,
                vpn_network_cidr,
                normalized_server_address,
                server_public_key,
                runtime,
                firewall,
                max_devices,
            ),
        )
        self._commit()
        row = self._conn.execute(
            "SELECT id FROM servers WHERE name = ?",
            (name,),
        ).fetchone()
        return int(row["id"])

    def create_server_for_admin(
        self,
        *,
        name: str,
        host: str,
        ssh_port: int,
        endpoint_host: str,
        vpn_port: int,
        vpn_network_cidr: str,
        server_address: str,
        server_public_key: str,
        runtime: str,
        firewall: str,
        status: str,
        max_devices: int,
    ) -> int:
        _validate_server_status(status)
        _validate_server_fields(
            name=name,
            host=host,
            ssh_port=ssh_port,
            endpoint_host=endpoint_host,
            vpn_port=vpn_port,
            vpn_network_cidr=vpn_network_cidr,
            server_address=server_address,
            runtime=runtime,
            firewall=firewall,
            max_devices=max_devices,
        )
        cursor = self._conn.execute(
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
                status,
                max_devices
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                host,
                ssh_port,
                endpoint_host,
                vpn_port,
                vpn_network_cidr,
                _host_address(server_address),
                server_public_key,
                runtime,
                firewall,
                status,
                max_devices,
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def update_server_for_admin(
        self,
        *,
        server_id: int,
        name: str,
        host: str,
        ssh_port: int,
        endpoint_host: str,
        vpn_port: int,
        vpn_network_cidr: str,
        server_address: str,
        server_public_key: str,
        runtime: str,
        firewall: str,
        status: str,
        max_devices: int,
    ) -> None:
        self.get_server(server_id)
        _validate_server_status(status)
        _validate_server_fields(
            name=name,
            host=host,
            ssh_port=ssh_port,
            endpoint_host=endpoint_host,
            vpn_port=vpn_port,
            vpn_network_cidr=vpn_network_cidr,
            server_address=server_address,
            runtime=runtime,
            firewall=firewall,
            max_devices=max_devices,
        )
        self._conn.execute(
            """
            UPDATE servers
            SET name = ?,
                host = ?,
                ssh_port = ?,
                endpoint_host = ?,
                vpn_port = ?,
                vpn_network_cidr = ?,
                server_address = ?,
                server_public_key = ?,
                runtime = ?,
                firewall = ?,
                status = ?,
                max_devices = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                host,
                ssh_port,
                endpoint_host,
                vpn_port,
                vpn_network_cidr,
                _host_address(server_address),
                server_public_key,
                runtime,
                firewall,
                status,
                max_devices,
                server_id,
            ),
        )
        self._commit()

    def set_server_status_for_admin(self, server_id: int, status: str) -> None:
        self.get_server(server_id)
        _validate_server_status(status)
        self._conn.execute(
            """
            UPDATE servers
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, server_id),
        )
        self._commit()

    def seed_default_plans(self) -> None:
        for duration_days in DEFAULT_PLAN_DAYS:
            self.upsert_plan(
                plan_id=f"days_{duration_days}",
                name=f"{duration_days} days",
                duration_days=duration_days,
                price=0,
                currency="RUB",
                is_free=True,
                is_active=True,
            )

    def upsert_plan(
        self,
        *,
        plan_id: str,
        name: str,
        duration_days: int,
        price: int = 0,
        currency: str = "RUB",
        is_free: bool = True,
        is_active: bool = True,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO plans (
                id,
                name,
                duration_days,
                price,
                currency,
                is_free,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                duration_days = excluded.duration_days,
                price = excluded.price,
                currency = excluded.currency,
                is_free = excluded.is_free,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                plan_id,
                name,
                duration_days,
                price,
                currency,
                int(is_free),
                int(is_active),
            ),
        )
        self._commit()

    def get_plan(self, plan_id: str) -> sqlite3.Row:
        return self._fetch_one("SELECT * FROM plans WHERE id = ?", (plan_id,))

    def list_active_plans(self) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT *
            FROM plans
            WHERE is_active = 1
            ORDER BY duration_days ASC
            """
        ).fetchall()

    def create_order(
        self,
        *,
        user_id: int,
        plan_id: str | None,
        payment_mode: str,
        requested_config_version: str = "amneziawg_v2",
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO orders (
                user_id,
                plan_id,
                payment_mode,
                requested_config_version
            )
            VALUES (?, ?, ?, ?)
            """,
            (user_id, plan_id, payment_mode, requested_config_version),
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

    def get_user_device(self, *, user_id: int, device_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            """
            SELECT *
            FROM devices
            WHERE id = ?
              AND user_id = ?
            """,
            (device_id, user_id),
        ).fetchone()

    def list_user_devices(
        self,
        user_id: int,
        *,
        statuses: tuple[str, ...] = ("active",),
        limit: int = 20,
    ) -> list[sqlite3.Row]:
        if not statuses:
            return []
        placeholders = ", ".join("?" for _ in statuses)
        return self._conn.execute(
            f"""
            SELECT *
            FROM devices
            WHERE user_id = ?
              AND status IN ({placeholders})
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, *statuses, limit),
        ).fetchall()

    def revoke_device(
        self,
        device_id: int,
        *,
        reason: str,
        revoked_at: str,
    ) -> bool:
        cursor = self._conn.execute(
            """
            UPDATE devices
            SET status = 'revoked',
                revoked_at = ?,
                revoke_reason = ?
            WHERE id = ?
              AND status IN ('pending', 'active')
            """,
            (revoked_at, reason, device_id),
        )
        self._commit()
        return cursor.rowcount > 0

    def revoke_user_devices(
        self,
        user_id: int,
        *,
        reason: str,
        revoked_at: str,
    ) -> int:
        cursor = self._conn.execute(
            """
            UPDATE devices
            SET status = 'revoked',
                revoked_at = ?,
                revoke_reason = ?
            WHERE user_id = ?
              AND status IN ('pending', 'active')
            """,
            (revoked_at, reason, user_id),
        )
        self._commit()
        return int(cursor.rowcount)

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

    def record_server_health(
        self,
        *,
        server_id: int,
        status: str,
        latency_ms: int | None,
        ssh_ok: bool,
        awg_ok: bool,
        udp_port_ok: bool,
        error: str | None,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO server_health_checks (
                server_id,
                status,
                latency_ms,
                ssh_ok,
                awg_ok,
                udp_port_ok,
                error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                server_id,
                status,
                latency_ms,
                int(ssh_ok),
                int(awg_ok),
                int(udp_port_ok),
                error,
            ),
        )
        self._commit()
        return int(cursor.lastrowid)

    def get_latest_server_health(self, server_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            """
            SELECT *
            FROM server_health_checks
            WHERE server_id = ?
            ORDER BY checked_at DESC, id DESC
            LIMIT 1
            """,
            (server_id,),
        ).fetchone()

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

    def list_admin_actions_for_target_user(self, target_user_id: int):
        return self._conn.execute(
            """
            SELECT *
            FROM admin_actions
            WHERE target_user_id = ?
            ORDER BY id DESC
            """,
            (target_user_id,),
        ).fetchall()

    def get_user_for_admin(self, user_id: int) -> sqlite3.Row:
        return self._fetch_one(
            """
            SELECT
                users.*,
                COUNT(devices.id) AS total_device_count,
                COALESCE(
                    SUM(CASE WHEN devices.status = 'active' THEN 1 ELSE 0 END),
                    0
                ) AS active_device_count
            FROM users
            LEFT JOIN devices ON devices.user_id = users.id
            WHERE users.id = ?
            GROUP BY users.id
            """,
            (user_id,),
        )

    def list_users_for_admin(self, *, limit: int = 50) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                users.*,
                COUNT(devices.id) AS total_device_count,
                COALESCE(
                    SUM(CASE WHEN devices.status = 'active' THEN 1 ELSE 0 END),
                    0
                ) AS active_device_count
            FROM users
            LEFT JOIN devices ON devices.user_id = users.id
            GROUP BY users.id
            ORDER BY users.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def list_user_devices_for_admin(
        self,
        user_id: int,
        *,
        limit: int = 50,
    ) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                devices.id,
                devices.name,
                devices.status,
                devices.vpn_ip,
                servers.name AS server_name
            FROM devices
            JOIN servers ON servers.id = devices.server_id
            WHERE devices.user_id = ?
            ORDER BY devices.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    def list_user_orders_for_admin(
        self,
        user_id: int,
        *,
        limit: int = 50,
    ) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                orders.*,
                plans.name AS plan_name,
                devices.name AS device_name
            FROM orders
            LEFT JOIN plans ON plans.id = orders.plan_id
            LEFT JOIN devices ON devices.id = orders.device_id
            WHERE orders.user_id = ?
            ORDER BY orders.created_at DESC, orders.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    def list_servers_for_admin(self, *, limit: int = 100) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                servers.*,
                COUNT(devices.id) AS total_device_count,
                COALESCE(
                    SUM(CASE WHEN devices.status = 'active' THEN 1 ELSE 0 END),
                    0
                ) AS active_device_count,
                latest_health.status AS health_status,
                latest_health.latency_ms AS health_latency_ms,
                latest_health.checked_at AS health_checked_at,
                latest_health.error AS health_error
            FROM servers
            LEFT JOIN devices ON devices.server_id = servers.id
            LEFT JOIN server_health_checks AS latest_health
                ON latest_health.id = (
                    SELECT id
                    FROM server_health_checks
                    WHERE server_id = servers.id
                    ORDER BY checked_at DESC, id DESC
                    LIMIT 1
                )
            GROUP BY servers.id
            ORDER BY servers.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def get_server_for_admin(self, server_id: int) -> sqlite3.Row:
        return self._fetch_one(
            """
            SELECT
                servers.*,
                COUNT(devices.id) AS total_device_count,
                COALESCE(
                    SUM(CASE WHEN devices.status = 'active' THEN 1 ELSE 0 END),
                    0
                ) AS active_device_count,
                latest_health.status AS health_status,
                latest_health.latency_ms AS health_latency_ms,
                latest_health.checked_at AS health_checked_at,
                latest_health.error AS health_error
            FROM servers
            LEFT JOIN devices ON devices.server_id = servers.id
            LEFT JOIN server_health_checks AS latest_health
                ON latest_health.id = (
                    SELECT id
                    FROM server_health_checks
                    WHERE server_id = servers.id
                    ORDER BY checked_at DESC, id DESC
                    LIMIT 1
                )
            WHERE servers.id = ?
            GROUP BY servers.id
            """,
            (server_id,),
        )

    def list_orders_for_admin(self, *, limit: int = 100) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                orders.*,
                users.telegram_id,
                users.username,
                users.first_name,
                users.last_name
            FROM orders
            JOIN users ON users.id = orders.user_id
            ORDER BY orders.created_at DESC, orders.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def list_pending_orders(self, *, limit: int = 20) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                orders.*,
                users.telegram_id,
                users.username,
                users.first_name,
                users.last_name
            FROM orders
            JOIN users ON users.id = orders.user_id
            WHERE orders.status IN ('manual_review', 'approved')
              AND orders.device_id IS NULL
            ORDER BY orders.created_at ASC, orders.id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def list_active_devices_with_users(self, *, limit: int = 50) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT
                devices.id,
                devices.name,
                devices.config_version,
                devices.status,
                devices.expires_at,
                devices.first_connected_at,
                devices.last_connected_at,
                devices.vpn_ip,
                users.telegram_id,
                users.username,
                users.first_name,
                users.last_name
            FROM devices
            JOIN users ON users.id = devices.user_id
            WHERE devices.status = 'active'
            ORDER BY devices.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

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

    def mark_device_connected(self, device_id: int, *, connected_at: str) -> None:
        self._conn.execute(
            """
            UPDATE devices
            SET first_connected_at = COALESCE(first_connected_at, ?),
                last_connected_at = ?
            WHERE id = ?
            """,
            (connected_at, connected_at, device_id),
        )
        self._commit()

    def get_message_template(self, key: str, *, default_text: str) -> str:
        row = self._conn.execute(
            "SELECT text FROM message_templates WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return default_text
        return str(row["text"])

    def set_message_template(self, key: str, text: str) -> None:
        self._conn.execute(
            """
            INSERT INTO message_templates (key, text)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                text = excluded.text,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, text),
        )
        self._commit()

    def create_email_recovery_token(
        self,
        *,
        user_id: int,
        email: str,
        token_hash: str,
        purpose: str,
        expires_at: str,
        device_id: int | None = None,
    ) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO email_recovery_tokens (
                user_id,
                email,
                token_hash,
                purpose,
                device_id,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, token_hash, purpose, device_id, expires_at),
        )
        self._commit()
        return int(cursor.lastrowid)

    def get_valid_email_recovery_token(
        self,
        *,
        token_hash: str,
        purpose: str,
        now: str,
    ) -> sqlite3.Row | None:
        return self._conn.execute(
            """
            SELECT *
            FROM email_recovery_tokens
            WHERE token_hash = ?
              AND purpose = ?
              AND used_at IS NULL
              AND expires_at > ?
            """,
            (token_hash, purpose, now),
        ).fetchone()

    def mark_email_recovery_token_used(self, token_id: int, used_at: str) -> bool:
        cursor = self._conn.execute(
            """
            UPDATE email_recovery_tokens
            SET used_at = ?
            WHERE id = ?
              AND used_at IS NULL
            """,
            (used_at, token_id),
        )
        self._commit()
        return cursor.rowcount > 0

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


def _host_address(value: str) -> str:
    try:
        return str(ipaddress.ip_interface(value).ip)
    except ValueError:
        return str(ipaddress.ip_address(value))


def _validate_user_status(status: str) -> None:
    if status not in USER_STATUSES:
        raise ValueError(f"unsupported user status: {status}")


def _validate_server_status(status: str) -> None:
    if status not in SERVER_STATUSES:
        raise ValueError(f"unsupported server status: {status}")


def _validate_server_fields(
    *,
    name: str,
    host: str,
    ssh_port: int,
    endpoint_host: str,
    vpn_port: int,
    vpn_network_cidr: str,
    server_address: str,
    runtime: str,
    firewall: str,
    max_devices: int,
) -> None:
    for field_name, value in {
        "name": name,
        "host": host,
        "endpoint_host": endpoint_host,
        "vpn_network_cidr": vpn_network_cidr,
        "server_address": server_address,
        "runtime": runtime,
        "firewall": firewall,
    }.items():
        if not value.strip():
            raise ValueError(f"{field_name} is required")
    _validate_port("ssh_port", ssh_port)
    _validate_port("vpn_port", vpn_port)
    if max_devices < 0:
        raise ValueError("max_devices must be non-negative")
    ipaddress.ip_network(vpn_network_cidr, strict=False)
    _host_address(server_address)


def _validate_port(field_name: str, value: int) -> None:
    if not 1 <= value <= 65535:
        raise ValueError(f"{field_name} must be in 1..65535")
