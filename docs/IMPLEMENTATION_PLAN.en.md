# Implementation Plan

## Stage 0. Decisions Before Code

- Choose the first VPS OS: Debian is recommended and accepted.
- Choose MVP payment scenario: manual approval or a concrete provider.
- Decide where the bot runs: locally, on the same VPS, or on a separate VPS.
- Confirm the import-link format for AmneziaVPN.

## Stage 1. Project Scaffold

- Create Python package.
- Add `pyproject.toml`.
- Add Dockerfile and Docker Compose later when deployment needs them.
- Configure `.env.example`.
- Add basic logging configuration.
- Connect SQLite for MVP.

## Stage 2. Telegram Bot

- Configure aiogram.
- Implement `/start`.
- Implement user menu.
- Implement admin menu.
- Add admin allowlist.
- Add access requests.

## Stage 3. Data Model

- Describe tables.
- Add migrations when needed.
- Implement repositories.
- Add admin audit log.

## Stage 4. AmneziaWG Manager

- Generate keypairs.
- Allocate IP addresses.
- Render AmneziaWG 2.0 `.conf`.
- Generate QR code.
- Add peer to server.
- Revoke peer.

## Stage 5. VPS Provisioning

- Check OS/kernel; first target is Debian.
- Read `servers.yml`.
- Add interactive mode for missing VPS data.
- Install dependencies and AmneziaWG.
- Generate UDP port above `30000` when not manually set.
- Open selected UDP port in `ufw`.
- Configure network forwarding.
- Configure firewall/NAT.
- Create systemd service.
- Run health check.

## Stage 6. Periods and Automation

- Add scheduler.
- Disable expired access.
- Send expiration warnings 7, 5, 3, and 1 day before expiration.
- Create backups.
- Record server health status.

## Stage 7. Payments

- Start with manual approval.
- Add the selected payment provider later.
- Add webhook or polling for payment status.
- Link order, payment, and peer.

## Stage 8. Multi-Server Support

- Add several servers.
- Add location selection.
- Add capacity and health checks.
- Add failover strategy by issuing a new config.

## Proposed Code Structure

```text
.
├── app/
│   ├── bot/
│   ├── config/
│   ├── db/
│   ├── payments/
│   ├── scheduler/
│   ├── vpn/
│   └── main.py
├── scripts/
├── tests/
├── docs/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## First Working Increment

1. Start an empty Telegram bot.
2. Register a user.
3. Add `ACCESS_MODE=free_test`.
4. Create a user device.
5. Generate a test `.conf` without writing to the server.
6. Generate QR code.
7. Add admin approval for manual mode.
8. Connect real peer creation on a test VPS.

## Refined MVP

- First provisioning target: Debian VPS.
- Bot runs separately from VPN server.
- One user can have several devices.
- Each device gets a separate peer, IP, keys, expiration, and config.
- Maximum devices per user: 5.
- Client DNS: `1.1.1.1`.
- Routing mode: full tunnel.
- VPN port is generated above `30000` and opened in `ufw`.
- Base VPN pool: `10.8.0.0/24`, with IPAM ready for larger pools or multiple servers.
- Main AmneziaWG runtime: host systemd with `awg`/`awg-quick`, without Docker.
- Several future servers are managed from one Telegram bot.
- Test mode: free access through `ACCESS_MODE=free_test` with required admin approval.
- Default test period: 7 days.
- Manual approval and future payment provider share the `orders/payments` layer.
