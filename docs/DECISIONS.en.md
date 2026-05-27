# Accepted Decisions

## MVP Baseline

- First VPN server: own VPS.
- VPS already exists and SSH access is available.
- First VPS OS: Debian.
- VPN protocol: AmneziaWG 2.0.
- Telegram bot runs separately from the VPN server.
- First stage supports one VPN server.
- Future versions may support several servers, but all of them must be managed from one Telegram bot.
- The architecture must support future servers, location selection, and failover by issuing a new config.

## Network

- The VPN port is generated automatically from a range above `30000`.
- During provisioning, the selected UDP port must be opened in `ufw`.
- First server VPN pool: `10.8.0.0/24`.
- The address pool must be configurable.
- If more than 255 devices/peers are expected on one server, use a larger pool such as `10.8.0.0/16` or distribute addresses across several servers.
- Address management must go through an IPAM layer, not manual string scanning in config files.
- Client DNS: `1.1.1.1`.
- Routing mode: full tunnel, `AllowedIPs = 0.0.0.0/0`.

## AmneziaWG Runtime

- MVP path: install AmneziaWG 2.0 directly on Debian host without Docker.
- Peer management must work without restarting Docker containers.
- Preferred runtime: `systemd` plus `awg`/`awg-quick`.
- Add, revoke, and update peer operations must be applied dynamically to a running interface and then persisted to the server config.
- Docker may remain a future alternative backend, but not the base dependency for peer management.

## Access and Devices

- One Telegram user may have several active configs.
- Each config maps to a separate device.
- Maximum devices per user in MVP: 5.
- Every device gets a separate peer, VPN IP, and keys.
- The user database must store user identity, creation date, and the list of configs.
- Each config stores creation date, duration, expiration date, IP, and peer key data.

## Payments

- In test mode, all access is free.
- The MVP must have a simple payment-mode switch.
- First working mode: free test access through manual admin approval.
- Payment provider will be selected later.
- The payment layer must be abstract so a provider can be added without rewriting Telegram bot and VPN logic.

## Periods

Fixed periods:

- 3 days;
- 7 days;
- 10 days;
- 14 days;
- 30 days;
- 60 days;
- 90 days;
- 180 days.

The administrator must also be able to set a custom duration.

Default test period: 7 days.

## Notifications

Warn users before device expiration:

- 7 days;
- 5 days;
- 3 days;
- 1 day.

## Deployment

- Scripts must deploy AmneziaWG 2.0 to a clean Debian VPS.
- Provisioning must be idempotent.
- A backup is required before changing server VPN config.
- Server configuration supports two modes:
  - non-interactive: values are already filled in `servers.yml`;
  - interactive: the wizard asks for missing data and creates/updates `servers.yml`.
- A new VPS can be connected by replacing config values or by running the interactive wizard.
