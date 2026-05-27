# MVP Data Model

## Principle

User storage must be a separate application layer. Telegram users and VPN configs must not be mixed with temporary requests, payments, and logs.

One user can have multiple devices. Each device gets a separate VPN config, separate IP address, and separate peer on the server.

## Tables

### `users`

Telegram user.

Fields:

- `id` - internal ID;
- `telegram_id` - Telegram user ID;
- `username`;
- `first_name`;
- `last_name`;
- `created_at`;
- `updated_at`;
- `status` - `active`, `blocked`, `deleted`;
- `is_admin` - MVP shortcut, later replaceable with roles.

### `devices`

User device. One device equals one VPN config.

Fields:

- `id`;
- `user_id`;
- `server_id`;
- `name`, for example `iPhone`, `Windows PC`, `Android`;
- `created_at`;
- `activated_at`;
- `expires_at`;
- `duration_days`;
- `status` - `active`, `expired`, `revoked`, `pending`;
- `vpn_ip`;
- `peer_public_key`;
- `peer_private_key_encrypted`;
- `preshared_key_encrypted`;
- `config_version`, for example `amneziawg_v2`;
- `last_config_sent_at`;
- `revoked_at`;
- `revoke_reason`.

### `servers`

VPN servers.

Fields:

- `id`;
- `name`;
- `host`;
- `ssh_port`;
- `endpoint_host`;
- `vpn_port`;
- `vpn_network_cidr`;
- `vpn_network_version`;
- `runtime` - `host_systemd`, later possibly `docker`;
- `firewall`, for example `ufw`;
- `status` - `active`, `degraded`, `disabled`;
- `max_devices`;
- `current_devices`;
- `created_at`;
- `updated_at`.

### `server_ports`

Allocated UDP ports. The MVP may keep the port in `servers.vpn_port`, but a separate table helps when several interfaces or protocols appear on one VPS.

Fields: `id`, `server_id`, `protocol`, `port`, `purpose`, `opened_in_firewall`, `created_at`.

### `plans`

Access plans.

Fields: `id`, `name`, `duration_days`, `price`, `currency`, `is_free`, `is_active`, `created_at`.

### `orders`

Request for creating or extending access.

Fields: `id`, `user_id`, `device_id`, `plan_id`, `status`, `payment_mode`, `created_at`, `approved_at`, `fulfilled_at`.

Order statuses: `draft`, `payment_pending`, `manual_review`, `approved`, `rejected`, `fulfilled`.

### `payments`

Future payment layer.

Fields: `id`, `order_id`, `provider`, `external_payment_id`, `amount`, `currency`, `status`, `created_at`, `paid_at`.

### `admin_actions`

Administrator audit log.

Fields: `id`, `admin_telegram_id`, `action`, `target_user_id`, `target_device_id`, `metadata_json`, `created_at`.

## Mode Settings

Minimum `.env` settings:

```env
ACCESS_MODE=free_test
PAYMENT_PROVIDER=none
DEFAULT_PLAN_DAYS=7
ADMIN_TELEGRAM_IDS=123456789
VPN_PORT_MIN=30001
VPN_PORT_MAX=65535
DEFAULT_VPN_NETWORK_CIDR=10.8.0.0/24
EXPIRATION_NOTICE_DAYS=7,5,3,1
VPN_SERVER_RUNTIME=host_systemd
CLIENT_DNS=1.1.1.1
CLIENT_ALLOWED_IPS=0.0.0.0/0
MAX_DEVICES_PER_USER=5
FREE_TEST_REQUIRES_APPROVAL=true
```

`ACCESS_MODE` values:

- `free_test`;
- `manual`;
- `payment`.

## Key Storage

For config resend, the system must either store the private key or store an encrypted complete config. For the MVP, prefer storing `peer_private_key_encrypted` and regenerating `.conf` from database and server parameters.
