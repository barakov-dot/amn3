# Technical Specification

## 1. Purpose

The system must automate issuing and managing AmneziaWG 2.0 VPN access on a privately owned VPS through a Telegram bot.

The first stage supports one VPS. The architecture must remain extensible for multiple servers with manual location selection or automated failover when the primary server is unavailable.

## 2. Sources and Technical Constraints

AmneziaWG 2.0 differs from classic WireGuard and older AmneziaWG versions:

- supported in AmneziaVPN 4.8.12.9 and newer;
- requires new configs and keys; legacy configs are not upgraded directly;
- adds `S3` and `S4`;
- `H1-H4` parameters support ranges that must not overlap;
- uses `I1-I5`;
- `j1-j3` and `itime` are no longer used.

Reference materials:

- https://amneziavpn.org/documentation/instructions/new-amneziawg-selfhosted/
- https://amneziavpn.org/documentation/amnezia-wg/
- https://amneziavpn.org/documentation/supported-linux-os-for-vps/
- https://github.com/amnezia-vpn/amneziawg-go
- https://github.com/amnezia-vpn/amneziawg-linux-kernel-module

## 3. Roles

### Administrator

Can install/check the VPS, view users, create configs manually, approve requests, issue custom access periods, extend and revoke access, view server status, manage plans, and add future servers.

### User

Can submit a request, pay or wait for manual approval, receive a config, check the expiration date, request config resend, extend access, and receive setup instructions.

MVP limit: no more than 5 active devices per user.

## 4. Access Periods

The system must support fixed periods: 3, 7, 10, 14, 30, 60, 90, and 180 days.

The administrator must also be able to set a custom duration in days or an explicit expiration date.

Default test period: 7 days.

## 5. Telegram Bot

User commands:

- `/start` - registration and main menu;
- `Get access` - start a request or payment flow;
- `My VPN` - access status;
- `Send config again` - resend files;
- `Extend` - renew access;
- `Help` - short instructions.

Admin commands:

- `/admin` - admin panel;
- `/users` - user list;
- `/approve <user_id> <days>` - approve access;
- `/revoke <user_id>` - revoke access;
- `/extend <user_id> <days>` - extend access;
- `/server_status` - VPS and AmneziaWG status;
- `/plans` - manage periods/plans.

The final UI should use inline buttons, while commands remain as a fast fallback.

## 6. Payments and Approval

The MVP must support two modes:

1. Free test mode with manual approval.
2. Payment stub: the bot records the selected plan and moves the request to `payment_pending`.

After the MVP, possible providers include YooKassa, CryptoBot, Telegram Stars, manual bank-transfer approval, or another provider.

The payment layer must be isolated so the bot and VPN logic do not need to be rewritten when the provider changes.

## 7. Config Generation

Each user device gets a separate peer:

- private key;
- public key;
- preshared key if PSK mode is enabled;
- VPN IP from the allocated pool;
- allowed IPs;
- DNS;
- endpoint;
- persistent keepalive;
- AmneziaWG 2.0 parameters `I1-I5`, `S1-S4`, `Jc`, `Jmin`, `Jmax`, `H1-H4`.

Users and administrators must be able to select the config format version:

- `amneziawg_v1_5`;
- `amneziawg_v2`.

The selected version is stored on the device and used when the config is resent.

MVP client settings:

- DNS: `1.1.1.1`;
- full tunnel: `AllowedIPs = 0.0.0.0/0`.

The generator must be a separate versioned module, for example `amneziawg_v2`, so future protocol changes can be added without breaking old configs.

## 8. Output Formats

The bot must provide:

- `.conf` file;
- QR code;
- text copy of the config on request;
- import link/key if compatibility with AmneziaVPN clients is confirmed.

The QR code is generated from the full `.conf` content.

## 9. VPS Provisioning

The initial provisioning script must:

- run in non-interactive mode from a prepared `servers.yml`;
- run interactively when config is missing or incomplete;
- ask for missing VPS data and create/update `servers.yml`;
- check OS and kernel;
- support Debian as the first target distribution;
- install dependencies and AmneziaWG;
- generate a UDP port above `30000` if no port is set;
- open the selected UDP port in `ufw`;
- enable forwarding;
- configure firewall/NAT;
- create the server keypair and base interface;
- verify service startup;
- save server metadata in the DB or project config.

The MVP runtime is host-level AmneziaWG on Debian, managed through `systemd`, `awg`, and `awg-quick`. Docker may be added later as an alternative backend.

## 10. Storage

Minimal entities:

- `users`;
- `servers`;
- `peers` or `devices`;
- `plans`;
- `orders`;
- `payments`;
- `admin_actions`;
- `server_health_checks`.

SQLite is acceptable for MVP. PostgreSQL is preferred for production.

The detailed MVP data model is described in [DATA_MODEL.en.md](DATA_MODEL.en.md).

## 11. Background Jobs

Required background tasks:

- disable expired peers;
- warn users 7, 5, 3, and 1 day before expiration;
- check VPS availability;
- back up the database and server configs;
- collect server health/status.
- collect peer traffic statistics and show them to users and administrators.

## 12. Security

Required controls:

- Telegram admin allowlist;
- secrets only in `.env` or secret storage;
- never log private keys or full configs;
- restrict the provisioning SSH key;
- back up before server config changes;
- use idempotent deployment scripts;
- validate durations and Telegram IDs;
- rate-limit user actions.

## 13. Multi-Server Support

The first stage has one server, but the architecture must include:

- `servers` table;
- server status: `active`, `degraded`, `disabled`;
- per-server IP pool, default `10.8.0.0/24`;
- capacity limit;
- selection strategy: `manual`, `least_loaded`, `failover`.

Failover does not instantly move an active tunnel. The realistic strategy is to issue a new config on a reserve server and mark the old peer as problematic.

All servers are managed by one Telegram bot.

## 14. MVP Completion

The MVP is complete when:

- the bot starts locally;
- an admin can register a VPS;
- provisioning deploys AmneziaWG 2.0;
- an admin can issue access for a chosen period;
- the user receives `.conf` and QR;
- expired access is disabled automatically;
- basic logs and backups exist.
