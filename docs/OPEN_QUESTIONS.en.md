# Open Questions

## VPS

1. First VPS OS: decided, Debian.
2. Bot placement: decided, separate from VPN server.
3. VPS/SSH: decided, VPS exists and SSH access is available.
4. Is IPv6 required, or IPv4 only?

## Network

1. UDP port: decided, generate any port above `30000` and open it in `ufw`.
2. Client DNS: decided, `1.1.1.1`.
3. Routing: decided, full tunnel `0.0.0.0/0`.
4. VPN IP pool: base `10.8.0.0/24`, but larger pools must be supported for growth above 255 devices.

## Access

1. Device model: decided, one Telegram user can have several devices, and each device gets a separate config.
2. Device limit: decided, maximum 5 devices per user.
3. Is traffic limiting required?
4. Is speed limiting required?
5. Warnings: decided, 7, 5, 3, and 1 day before expiration.

## Payments

1. MVP: decided, free test mode with a switch to manual approval/payment.
2. Which payment provider should be added first later?
3. Are promo codes required?
4. Is subscription auto-renewal required?

## Administration

1. Are Telegram admin IDs known?
2. Are roles required: owner, admin, support?
3. Should all admin actions be logged to a separate Telegram channel?

## Client Formats

1. Main client: AmneziaVPN, native AmneziaWG, or both?
2. Are separate instructions required for Windows, Android, iOS, and macOS?
3. Should the import-link format be experimentally confirmed in the AmneziaVPN client?

## Storage Policy

1. Store user private keys in the database for config resend?
2. Or store only encrypted `.conf`/secrets?
3. What is the retention period for logs and requests?
