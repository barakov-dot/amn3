# Emergency Restore Checklist

Short emergency service migration path for a new server.

## What Must Be Saved in Advance

- `.env` with the same `APP_SECRET_KEY`;
- `servers.yml` or a new file for the replacement VPS;
- the latest backup file from `backups/`;
- access to the GitHub repository;
- access to the Telegram bot token.

Without the original `APP_SECRET_KEY`, encrypted peer private keys and PSKs
cannot be decrypted.

## 1. Prepare a New VPS

Install Python 3.12+, Git, and AmneziaWG system dependencies. Keep
`VPS_APPLY_ENABLED=false` until checks pass.

## 2. Get the Project

```bash
git clone -b codex-vps-test-prep https://github.com/barakov-dot/amn2.git
cd amn2
```

## 3. Restore Local Files

```bash
cp /secure-copy/.env .env
cp /secure-copy/servers.yml servers.yml
```

Check:

```env
APP_SECRET_KEY=CHANGE_ME_SAME_KEY_USED_WHEN_BACKUP_WAS_CREATED
TELEGRAM_BOT_TOKEN=CHANGE_ME_BOT_TOKEN
ADMIN_TELEGRAM_IDS=CHANGE_ME_ADMIN_TELEGRAM_IDS
VPS_APPLY_ENABLED=false
```

## 4. Restore the Database

```bash
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
python -m app.cli backup restore --file backups/<backup-file>.tar.enc --target-db data/amneziya.sqlite3 --force
```

## 5. Check the Server

```bash
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server check --config servers.yml --server debian-vps-1
```

## 6. Restore Config Issuing

After live check and test `apply-peer --dry-run` pass, enable:

```env
VPS_APPLY_ENABLED=true
```

Then restart the bot.

## 7. Check Clients

- create a test request;
- approve it as admin;
- import the config into a client;
- verify connection;
- run `collect-traffic`;
- verify traffic in the bot.
