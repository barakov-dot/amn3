# Traffic Statistics and Config Version Selection

## Goal

Add two related capabilities to the project:

- collect and display traffic statistics for VPN devices;
- allow selecting the AmneziaWG config version: `amneziawg_v1_5` or `amneziawg_v2`.

The functionality must be available both to users in the Telegram bot account area and to administrators when manually creating or managing accounts.

## Current State

Already exists:

- `devices.config_version`;
- `amneziawg_v2` client config generator;
- users/devices/orders/admin_actions model;
- encrypted peer secret storage;
- safe `server check` scaffold.

Missing:

- `amneziawg_v1_5` generator;
- explicit supported config version list;
- user-side config version selection;
- admin-side config version selection;
- traffic snapshot tables;
- service mapping peer public keys to traffic counters;
- Telegram UI for traffic statistics.

## Scope

Included:

- define supported config formats:
  - `amneziawg_v1_5`;
  - `amneziawg_v2`;
- add a version-based renderer selection layer;
- add a minimal `amneziawg_v1_5` renderer;
- extend device creation workflow so callers can pass the selected version;
- add a traffic snapshot table;
- add repository/service methods for writing and reading latest traffic stats;
- prepare DTO/text formatting for user and admin display;
- add a fake-friendly server traffic collection interface;
- cover the new logic with tests.

Excluded from this increment:

- real SSH traffic collection from a production VPS;
- traffic limits and auto-disable by limit;
- traffic-based paid plans;
- complete Telegram inline-button UI if the DB/service foundation is not ready;
- production migration framework.

## Terms

`config_version` is the client VPN config format version.

`traffic snapshot` is a point-in-time snapshot of peer traffic counters.

`rx_bytes` is received traffic for a peer.

`tx_bytes` is transmitted traffic for a peer.

`total_bytes` is `rx_bytes + tx_bytes`.

## Data Model

Add `device_traffic_snapshots`:

```sql
CREATE TABLE IF NOT EXISTS device_traffic_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    server_id INTEGER NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    peer_public_key TEXT NOT NULL,
    rx_bytes INTEGER NOT NULL CHECK (rx_bytes >= 0),
    tx_bytes INTEGER NOT NULL CHECK (tx_bytes >= 0),
    source TEXT NOT NULL,
    collected_at TEXT NOT NULL
);
```

Indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_device_traffic_device_collected
    ON device_traffic_snapshots(device_id, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_device_traffic_server_collected
    ON device_traffic_snapshots(server_id, collected_at DESC);
```

`devices.config_version` already exists. Supported values must be enforced at service level:

- `amneziawg_v1_5`;
- `amneziawg_v2`.

If a migration system is introduced later, allowed values can move to a DB constraint or lookup table.

## Config Generation

Add a common interface:

```text
render_client_config_for_version(input, config_version) -> str
```

Rules:

- `amneziawg_v2` uses the current renderer;
- `amneziawg_v1_5` uses a separate renderer;
- unknown versions return a clear error;
- the version is stored in `devices.config_version`;
- config resend uses the version stored on the device.

## User Flow

In the Telegram bot account area, the user should see:

- list of own devices;
- config version of each device;
- expiration;
- received traffic;
- transmitted traffic;
- total traffic;
- last statistics update time.

When creating a new request, the user selects:

1. device name;
2. AmneziaWG version:
   - AmneziaWG 1.5;
   - AmneziaWG 2.0.

The selected version enters the order/device workflow.

## Admin Flow

When manually creating access, the administrator selects:

1. user;
2. device or new device name;
3. access period;
4. config version:
   - AmneziaWG 1.5;
   - AmneziaWG 2.0.

Admin views should show:

- user;
- device;
- config version;
- status;
- expiration;
- latest traffic stats;
- last stats collection time.

## Traffic Collection

This increment needs a VPS-independent interface:

```text
TrafficCollector.collect(server) -> list[PeerTraffic]
```

`PeerTraffic`:

- `peer_public_key`;
- `rx_bytes`;
- `tx_bytes`;
- `collected_at`;
- `source`.

A real backend can later read `awg show` or another AmneziaWG-compatible output. For this increment, a fake collector is enough for tests, plus a service that maps `peer_public_key` to devices.

## Errors and Security

- Traffic collection must not log private keys, PSKs, or full configs.
- If a peer from server output is not found in the DB, no snapshot is written, but the event may be returned in a report as `unknown_peer`.
- Negative counters are forbidden.
- Stale snapshots must be displayed as stale.
- Traffic collection failure must not break config delivery for existing devices.

## Testing

Required tests:

- supported config version list;
- unknown config version rejected;
- `amneziawg_v2` path remains compatible;
- `amneziawg_v1_5` renderer returns a valid config shape;
- access service stores selected config version;
- traffic snapshot insert rejects negative counters;
- latest traffic for device returns newest snapshot;
- collector service stores stats only for known peers;
- user/admin display DTO formats bytes safely;
- backup/restore remains green after schema update.

## Acceptance Criteria

- User and admin workflows can pass the selected config version.
- Device stores the selected `config_version`.
- There are two renderer paths: `amneziawg_v1_5` and `amneziawg_v2`.
- Traffic snapshot table and repository exist.
- Latest device traffic is available for bot display.
- Fake collector is covered by tests.
- Full test suite passes.
- Documentation exists in Russian and English.
