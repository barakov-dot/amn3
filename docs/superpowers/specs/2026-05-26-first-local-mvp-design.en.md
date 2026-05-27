# First Local MVP Design

## Goal

Build the first working local increment for Amneziya: a Python application that can register a Telegram user, accept an access request, let an administrator approve it, create a device, allocate a VPN IP, generate an AmneziaWG 2.0 client config, and produce a QR code.

This increment does not apply peers to a real VPS. Server provisioning and live `awg`/`awg-quick` integration are deferred to the next increment. The purpose is to prove the application core safely before touching a production VPN server.

Data protection requirements for this increment are defined in [2026-05-26-data-protection-addendum.md](2026-05-26-data-protection-addendum.md) and are part of the implementation scope.

Backup and restore requirements are defined in [2026-05-26-backup-and-recovery-addendum.md](2026-05-26-backup-and-recovery-addendum.md) and are part of the first scaffold.

## Scope

Included:

- Python project scaffold with package layout, dependency metadata, and environment example.
- Runtime configuration loaded from environment variables.
- SQLite storage for local MVP development.
- Data model for users, servers, devices, plans, orders, and admin actions.
- IP allocation from a configurable CIDR.
- AmneziaWG 2.0 client config generation.
- QR generation from the full config text.
- Encrypted local backup, verification, and restore CLI for application state.
- Minimal Telegram bot flow with `/start`, access request, and admin approval.
- Service layer for the request-to-device lifecycle.
- Tests for IPAM, config generation, and the core approval flow.

Excluded:

- Real SSH provisioning.
- Installing AmneziaWG on Debian VPS.
- Applying or revoking live peers on a running interface.
- Real payment provider integration.
- Multi-server selection beyond data model readiness.
- Import-link format until confirmed against a real AmneziaVPN client.

## Architecture

The application should use a small layered structure:

```text
app/
  bot/
    handlers/
    keyboards/
  config/
  db/
    migrations/
    repositories/
  services/
  backup/
  vpn/
    amneziawg_v2/
    ipam.py
  cli.py
  main.py
tests/
```

`bot` handles Telegram input and output only. It should not directly allocate IP addresses, create keys, or write VPN config records.

`services` owns user workflows: request access, approve request, create device, generate config payload, and record admin actions.

`db` owns persistence and repository interfaces. SQLite is the MVP backend, but repository boundaries should avoid spreading SQL through bot handlers.

`vpn.ipam` owns CIDR-aware IP allocation and must avoid issuing the server address, network address, broadcast address, or already allocated addresses.

`vpn.amneziawg_v2` owns key generation and config rendering. The generator should include a config format version such as `amneziawg_v2` so future protocol changes can be added without rewriting old records.

`backup` owns backup manifest generation, encrypted archive creation, verification, and guarded restore. Backup code should not depend on Telegram handlers or VPN config rendering.

## Data Flow

1. A Telegram user sends `/start`.
2. The bot creates or updates a `users` record.
3. The user requests access.
4. The app creates an `orders` record with status `manual_review` in the default MVP mode.
5. An admin approves the order.
6. The service creates a `devices` record in `pending` status.
7. IPAM allocates the next available address from the selected server CIDR.
8. The VPN generator creates keys and renders an AmneziaWG 2.0 `.conf`.
9. The service stores peer secret fields encrypted with an application secret from the environment.
10. The device becomes `active`.
11. The bot sends the `.conf` file and QR code to the user.

For this first increment, the selected server is a local logical server record. No remote host is modified.

## Configuration

The MVP should support these environment values:

```env
ACCESS_MODE=free_test
FREE_TEST_REQUIRES_APPROVAL=true
DEFAULT_PLAN_DAYS=7
MAX_DEVICES_PER_USER=5
CLIENT_DNS=1.1.1.1
CLIENT_ALLOWED_IPS=0.0.0.0/0
EXPIRATION_NOTICE_DAYS=7,5,3,1
VPN_PORT_MIN=30001
VPN_PORT_MAX=65535
VPN_SERVER_RUNTIME=host_systemd
DEFAULT_VPN_NETWORK_CIDR=10.8.0.0/24
```

Secrets such as `TELEGRAM_BOT_TOKEN`, encryption keys, and admin Telegram IDs belong in `.env` or deployment secret storage, not in committed files.

## Error Handling

The service layer should treat device creation as a workflow with explicit states.

If config generation fails, the order remains unfulfilled and the device should stay `pending` or move to `failed`.

If IP allocation fails because the pool is exhausted, the admin should receive a clear error and no active device should be created.

If sending the config to Telegram fails after the device is created, the device remains active and `last_config_sent_at` stays empty. The user or admin can retry delivery later.

No logs should include private keys, preshared keys, full config text, or Telegram bot tokens.

Backup restore must refuse to overwrite an existing database unless forced, verify checksums before restore, and require the same `APP_SECRET_KEY` needed to decrypt peer secrets.

## Testing

The first test set should cover:

- IPAM does not allocate reserved addresses.
- IPAM does not allocate an IP already used by an active or pending device.
- IPAM reports pool exhaustion clearly.
- Config generation includes the expected interface, peer, endpoint, DNS, allowed IPs, and AmneziaWG 2.0 fields.
- The approval service creates a user device with status `active`, an expiry date, a VPN IP, and generated key data.
- The max-devices-per-user limit is enforced.
- Backup creation includes database state and a manifest without plaintext secrets.
- Backup verification fails on checksum mismatch.
- Restore requires `APP_SECRET_KEY` and refuses overwrite without an explicit force option.

Telegram handler tests can be lighter in the first increment. The highest-risk behavior is the domain workflow, not button rendering.

## Implementation Order

1. Create the Python package scaffold and dependency metadata.
2. Add config loading and `.env.example`.
3. Add SQLite schema and repository layer.
4. Add IPAM with tests.
5. Add AmneziaWG 2.0 config generator with tests.
6. Add backup manifest, encrypted archive, verify, and restore commands with tests.
7. Add service workflow for request approval with tests.
8. Add minimal aiogram bot handlers.
9. Add QR generation and Telegram file delivery.
10. Add a local run command and README instructions.

## Open Decisions

- Confirm the exact AmneziaWG 2.0 parameters used for generated configs before real user rollout.
- Confirm import-link compatibility separately on a real AmneziaVPN client before making it part of MVP completion.
