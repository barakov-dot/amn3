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

The template contains stable config lines and placeholders for user/device
variables. The `.conf` file remains the canonical delivery path until `vpn://`
import is verified with a real AmneziaVPN client.

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
