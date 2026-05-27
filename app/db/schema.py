import sqlite3


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'blocked', 'deleted')),
            is_admin INTEGER NOT NULL DEFAULT 0
                CHECK (is_admin IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            host TEXT,
            ssh_port INTEGER CHECK (ssh_port BETWEEN 1 AND 65535),
            endpoint_host TEXT,
            vpn_port INTEGER CHECK (vpn_port BETWEEN 1 AND 65535),
            vpn_network_cidr TEXT NOT NULL,
            server_address TEXT,
            server_public_key TEXT,
            runtime TEXT,
            firewall TEXT,
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'degraded', 'disabled')),
            max_devices INTEGER CHECK (max_devices >= 0),
            current_devices INTEGER NOT NULL DEFAULT 0
                CHECK (current_devices >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            server_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            activated_at TEXT,
            expires_at TEXT,
            duration_days INTEGER NOT NULL CHECK (duration_days > 0),
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('pending', 'active', 'expired', 'revoked', 'failed')),
            vpn_ip TEXT NOT NULL,
            peer_public_key TEXT NOT NULL,
            peer_private_key_encrypted TEXT NOT NULL,
            preshared_key_encrypted TEXT NOT NULL,
            config_version TEXT NOT NULL,
            last_config_sent_at TEXT,
            revoked_at TEXT,
            revoke_reason TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (server_id) REFERENCES servers(id),
            UNIQUE (server_id, peer_public_key)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device_id INTEGER,
            plan_id TEXT,
            requested_config_version TEXT NOT NULL DEFAULT 'amneziawg_v2',
            status TEXT NOT NULL DEFAULT 'manual_review'
                CHECK (
                    status IN (
                        'draft',
                        'payment_pending',
                        'manual_review',
                        'approved',
                        'rejected',
                        'fulfilled'
                    )
                ),
            payment_mode TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            fulfilled_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );

        CREATE TABLE IF NOT EXISTS admin_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_telegram_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_user_id INTEGER,
            target_device_id INTEGER,
            metadata_json TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_user_id) REFERENCES users(id),
            FOREIGN KEY (target_device_id) REFERENCES devices(id)
        );

        CREATE TABLE IF NOT EXISTS device_traffic_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            server_id INTEGER NOT NULL,
            peer_public_key TEXT NOT NULL,
            rx_bytes INTEGER NOT NULL CHECK (rx_bytes >= 0),
            tx_bytes INTEGER NOT NULL CHECK (tx_bytes >= 0),
            source TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_devices_user_status
            ON devices(user_id, status);
        CREATE INDEX IF NOT EXISTS idx_devices_server_status
            ON devices(server_id, status);
        CREATE INDEX IF NOT EXISTS idx_orders_user_status
            ON orders(user_id, status);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_reserved_ip_unique
            ON devices(server_id, vpn_ip)
            WHERE status IN ('pending', 'active');
        CREATE INDEX IF NOT EXISTS idx_device_traffic_device_collected
            ON device_traffic_snapshots(device_id, collected_at DESC);
        CREATE INDEX IF NOT EXISTS idx_device_traffic_server_collected
            ON device_traffic_snapshots(server_id, collected_at DESC);
        """
    )
    _ensure_column(
        conn,
        "orders",
        "requested_config_version",
        "TEXT NOT NULL DEFAULT 'amneziawg_v2'",
    )
    conn.commit()


def _ensure_column(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = {
        row["name"] if isinstance(row, sqlite3.Row) else row[1]
        for row in conn.execute(f"PRAGMA table_info({table_name})")
    }
    if column_name not in columns:
        conn.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )
