# VPN Server Management

## General Idea

The Telegram bot runs separately from VPN servers and manages them centrally.

For each VPN server, the bot stores:

- SSH host/port;
- client endpoint;
- VPN UDP port;
- VPN address pool;
- runtime;
- availability status;
- active device count.

The first stage has one server. Future versions may have several, but the management interface remains one Telegram bot.

New server connection must be possible through:

- a prepared `servers.yml`;
- an interactive wizard that asks for VPS data and creates/updates `servers.yml`.

## Runtime

MVP runtime:

- Debian VPS;
- AmneziaWG 2.0 installed on host;
- management through `systemd`;
- interface started with `awg-quick`;
- peers applied through `awg`.

This avoids dependency on a constantly restarted Docker container, allows adding and revoking peers without stopping the VPN interface, and persists the final state to server config after successful application.

Docker can be added later as an alternative backend.

## Adding a Peer

Recommended order:

1. Create `device` record in DB with `pending` status.
2. Allocate a free IP from the server pool.
3. Generate keys.
4. Build peer data.
5. Apply peer to the running interface through `awg`.
6. Save peer to persistent server config.
7. Back up the changed config.
8. Move device to `active`.
9. Send `.conf`, QR, and confirmed link/key format to the user.

If server application fails, the record stays `pending` or moves to `failed`, and the IP is released.

## Revoking a Peer

Recommended order:

1. Find the user device.
2. Remove peer from the running interface.
3. Remove or comment peer in persistent server config.
4. Create backup.
5. Update device status to `revoked` or `expired`.
6. Save revoke reason.

## Ports

If the administrator did not set a port:

- generate a random UDP port in `30001-65535`;
- check that it is not used on the server;
- open it in `ufw`;
- save it in `servers.vpn_port`;
- use it in client endpoints.

## Address Pools

First server base pool: `10.8.0.0/24`.

This is enough for about 253-254 client IPs after excluding network, broadcast, and server address.

For more devices:

- expand the pool, for example to `10.8.0.0/16`;
- add new servers with separate pools, for example `10.9.0.0/24`, `10.10.0.0/24`.

The code needs an IPAM layer that understands each server CIDR, avoids occupied IPs, avoids the server IP, scales to several servers, and blocks race conditions when several configs are issued concurrently.

## Multi-Server Support

All servers are managed from one bot.

Selection strategies:

- `manual`;
- `least_loaded`;
- `failover`.

Failover does not move an active tunnel instantly. The user receives a new config for another server.

## Health Check

Each server should be checked for:

- SSH availability;
- systemd service status;
- interface status;
- UDP port visibility;
- peer count;
- free IPs in the pool;
- available disk space.
