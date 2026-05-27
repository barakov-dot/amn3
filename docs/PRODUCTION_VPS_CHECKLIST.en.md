# Production VPS Checklist

Short path before the first live VPS test.

## 1. Get the Code

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 2. Prepare `.env`

```bash
cp .env.example .env
```

Fill the minimum required values:

```env
TELEGRAM_BOT_TOKEN=...
APP_SECRET_KEY=...
ADMIN_TELEGRAM_IDS=...
VPS_APPLY_ENABLED=false
SERVER_CONFIG_PATH=servers.yml
SERVER_NAME=debian-vps-1
```

Store `APP_SECRET_KEY` separately. Losing it means losing access to encrypted
peer secrets.

## 3. Prepare `servers.yml`

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

## 4. Local Check

```bash
python -m pytest tests
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## 5. Safe VPS Dry-Runs

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --preshared-key PEER_PSK --vpn-ip 10.8.0.2 --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key PEER_PUBLIC_KEY --dry-run
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
```

## 6. First Live Test

Run the read-only check first:

```bash
python -m app.cli server check --config servers.yml --server debian-vps-1
```

If the check succeeds, manually test `apply-peer --apply` with a test peer. Only
after that enable:

```env
VPS_APPLY_ENABLED=true
```

## 7. Backup

```bash
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
```

Before moving to another server, store `.env`, `servers.yml`, and the backup
file outside the repository.
