# Production VPS Checklist

Short path before the first live VPS test.

## 1. Get the Code

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 2. Prepare Python Environment

On a new VPS:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

If the project was already cloned and needs fresh changes:

```bash
git pull
source venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

## 3. Prepare `.env`

```bash
cp .env.example .env
```

Fill the minimum required values:

```env
TELEGRAM_BOT_TOKEN=CHANGE_ME_TOKEN_FROM_BOTFATHER
TELEGRAM_PROXY_URL=
APP_SECRET_KEY=CHANGE_ME_GENERATED_RANDOM_SECRET_32_PLUS_CHARS
ADMIN_TELEGRAM_IDS=CHANGE_ME_ADMIN_TELEGRAM_IDS
VPS_APPLY_ENABLED=false
SERVER_CONFIG_PATH=servers.yml
SERVER_NAME=debian-vps-1
```

If the VPS cannot reach `https://api.telegram.org` directly, set a SOCKS5 proxy:

```env
TELEGRAM_PROXY_URL=socks5://127.0.0.1:1080
```

Before starting the bot, check access through the same proxy:

```bash
curl --socks5-hostname 127.0.0.1:1080 -I https://api.telegram.org
python -m app.cli bot check-network
```

Store `APP_SECRET_KEY` separately. Losing it means losing access to encrypted
peer secrets.

### Web Admin Panel

The web panel is disabled by default for the first VPS run. When enabling it,
fill the separate values:

```env
WEB_ADMIN_ENABLED=false
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PORT=3030
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=replace-with-password-hash
WEB_ADMIN_SESSION_SECRET=replace-with-generated-random-secret-32-plus-chars
WEB_ADMIN_SESSION_COOKIE_SECURE=true
```

Generate `WEB_ADMIN_PASSWORD_HASH` on the VPS without putting the raw password
into shell history:

```bash
python -m app.cli web hash-password
```

For automation in a trusted shell, the command also accepts `--password`, but the
interactive prompt is safer for the first setup. Generate
`WEB_ADMIN_SESSION_SECRET` with any strong random 32+ character value, for
example from your password manager.

Start the panel with:

```bash
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

If `--host` or `--port` are omitted, the command uses `WEB_ADMIN_HOST` and
`WEB_ADMIN_PORT` from `.env`.

`WEB_ADMIN_SESSION_COOKIE_SECURE=true` requires HTTPS, a TLS reverse proxy, or an
SSH tunnel to the panel. For a short plain-HTTP check on `:3030`, temporarily set
`WEB_ADMIN_SESSION_COOKIE_SECURE=false`, but do not leave an internet-facing
admin panel open that way.

## 4. Config Templates And Delivery

Current user config delivery options:

- Telegram message rendered from the `config_ready` template;
- attached `.conf` file;
- QR code;
- user-triggered resend from their devices;
- admin-triggered resend;
- emergency raw config text delivery if file/QR delivery fails after device creation.

The web-panel work adds a separate client `.conf` template per version,
`amneziawg_v1_5` and `amneziawg_v2`, plus an import link in the form `vpn://...`.
After implementation, keep VPS template edits in an external directory:

```env
CLIENT_CONFIG_TEMPLATE_DIR=config_templates
```

Override files use these exact names:

- `amneziawg_v1_5.conf.tpl`
- `amneziawg_v2.conf.tpl`

The template contains stable config lines and placeholders for user/device
variables. The `.conf` file remains the canonical delivery path until `vpn://`
import is verified with a real AmneziaVPN client.

If the user provides an email address, the web admin panel can send a
verification email, then send the device config or a one-time recovery code to
that verified address. Keep this channel disabled for the first live run until
SMTP is configured and tested:

```env
EMAIL_DELIVERY_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
EMAIL_REQUIRE_VERIFICATION=true
EMAIL_RECOVERY_TOKEN_TTL_MINUTES=30
EMAIL_CONFIG_ATTACHMENTS_ENABLED=true
```

With `EMAIL_REQUIRE_VERIFICATION=true`, config and recovery emails are sent only
after the address is verified. Verification/recovery codes are one-time tokens
stored in the database as SHA-256 hashes and expire after
`EMAIL_RECOVERY_TOKEN_TTL_MINUTES`. Config emails include setup text and the
`vpn://` import link; the `.conf` attachment is controlled by
`EMAIL_CONFIG_ATTACHMENTS_ENABLED`.

SMTP passwords, raw verification/recovery tokens, and full config text must not
be written to logs or admin-action metadata.

## 5. Prepare `servers.yml`

Do not commit this file. Required values:

```yaml
ssh.host: VPS IP or domain
ssh.user: root or another user
ssh.auth.type: key or password
vpn.endpoint_host: public IP or domain
vpn.port: fixed UDP port, for example 30001
vpn.network_cidr: 10.8.0.0/24
vpn.server_address: 10.8.0.1/24
vpn.server_public_key: AmneziaWG server public key
```

## 6. Local Check

```bash
python -m pytest tests
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## 7. Safe VPS Dry-Runs

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --preshared-key PEER_PSK --vpn-ip 10.8.0.2 --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
```

## 8. First Live Test

Run the read-only check first:

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1
```

If the check succeeds, manually test `apply-peer --apply` with a test peer. Only
after that enable:

```env
VPS_APPLY_ENABLED=true
```

## 9. Backup

```bash
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Before moving to another server, store `.env`, `servers.yml`, and the backup
file outside the repository.
