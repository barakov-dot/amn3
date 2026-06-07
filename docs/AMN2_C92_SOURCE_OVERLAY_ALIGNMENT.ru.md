# AMN2 c92bd1a Source Overlay Alignment

Дата: 2026-06-07.

Назначение: безопасно выровнять production source overlay `/opt/amn2` с текущим target `c92bd1a Bind web admin systemd to loopback`, потому что последний operator launch evidence подтвердил working runtime на `42ffa65`, а не финальный `c92bd1a` gate.

Этот runbook не включает broad write API, не включает public API exposure и не требует `VPS_APPLY_ENABLED=true`.

## 1. Артефакты

Локально в lab repo:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\dist\amn2-vps-update-and-smoke-kit-c92bd1a.zip
C:\Users\SooL\Documents\VPS-OPS-LAB\dist\amn2-vps-update-and-smoke-kit-c92bd1a.zip.sha256.txt
```

Checksums:

```text
kit_sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source_zip_sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
expected_source_overlay: c92bd1a
```

## 2. Загрузка На VPS

Можно загрузить любым безопасным способом. Если доступен `scp` с локального Windows host:

```powershell
scp C:\Users\SooL\Documents\VPS-OPS-LAB\dist\amn2-vps-update-and-smoke-kit-c92bd1a.zip root@mirror:/root/
scp C:\Users\SooL\Documents\VPS-OPS-LAB\dist\amn2-vps-update-and-smoke-kit-c92bd1a.zip.sha256.txt root@mirror:/root/
```

Если `mirror` не резолвится с Windows, использовать реальный SSH host из своего окружения. Секреты, `.env`, DB и private keys не копировать через чат.

## 3. Распаковка И Checksum На VPS

```bash
cd /root

sha256sum -c amn2-vps-update-and-smoke-kit-c92bd1a.zip.sha256.txt

rm -rf amn2-vps-update-and-smoke-kit-c92bd1a
mkdir -p amn2-vps-update-and-smoke-kit-c92bd1a

python3 -m zipfile -e \
  amn2-vps-update-and-smoke-kit-c92bd1a.zip \
  amn2-vps-update-and-smoke-kit-c92bd1a

cd /root/amn2-vps-update-and-smoke-kit-c92bd1a
sha256sum -c amn2-codex-vps-test-prep-c92bd1a-source.zip.sha256.txt
```

Ожидаем:

```text
amn2-vps-update-and-smoke-kit-c92bd1a.zip: OK
amn2-codex-vps-test-prep-c92bd1a-source.zip: OK
```

## 4. Применение Source Overlay

```bash
cd /root/amn2-vps-update-and-smoke-kit-c92bd1a

export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2

bash ./amn2_apply_source_zip.sh
```

Ожидаем:

```text
source_update_status=passed
target=/opt/amn2
source_commit=c92bd1a
```

Проверить target:

```bash
cd /opt/amn2
cat .amn2_source_overlay_commit

test -d data && echo "data_dir=present" || echo "data_dir=missing"
test -f .env && echo "env_file=present" || echo "env_file=missing"
test -f servers.yml && echo "servers_yml=present" || echo "servers_yml=missing"
test -d venv && echo "venv=present" || echo "venv=missing"

export VPS_APPLY_ENABLED=false
printf 'VPS_APPLY_ENABLED=%s\n' "$VPS_APPLY_ENABLED"
```

Ожидаем:

```text
c92bd1a
data_dir=present
env_file=present
servers_yml=present
venv=present
VPS_APPLY_ENABLED=false
```

## 5. Backup После Alignment

```bash
cd /opt/amn2
source venv/bin/activate

export APP_SECRET_KEY="$(
  python -c 'from dotenv import dotenv_values; print(dotenv_values(".env").get("APP_SECRET_KEY", ""))'
)"

test -n "${APP_SECRET_KEY:-}" && echo "APP_SECRET_KEY=present" || echo "APP_SECRET_KEY=missing"

python -m app.cli backup create --db data/amneziya.sqlite3 --output backups

BACKUP_FILE="$(ls -t backups/*.tar.enc | head -n 1)"
printf 'backup_file=%s\n' "$BACKUP_FILE"

python -m app.cli backup verify --file "$BACKUP_FILE"
```

Не публиковать `APP_SECRET_KEY`, backup content, `.env` или DB.

## 6. Safe Preflight

```bash
cd /opt/amn2
source venv/bin/activate

export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local

python -m app.cli bot check-network

python -m app.cli server preflight \
  --config servers.yml \
  --server "$AMN2_SERVER_NAME" \
  --db data/amneziya.sqlite3

python -m app.cli server check \
  --config servers.yml \
  --server "$AMN2_SERVER_NAME" \
  --dry-run
```

## 7. API Smoke Только На Loopback

В первом SSH-окне:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false

python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Во втором SSH-окне:

```bash
cd /opt/amn2
source venv/bin/activate

python -m app.cli api smoke-cycle \
  --db /opt/amn2/data/amneziya.sqlite3 \
  --base-url http://127.0.0.1:3040 \
  --server-name local \
  --name c92-align-smoke \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Ожидаем:

```text
status: passed
checked_routes: 6
route status codes: 200
forbidden_markers: []
token.raw_token_display: hidden
revoke.status: revoked
```

## 8. Web/Admin Loopback Systemd

`c92bd1a` нужен, чтобы web-admin service template держал backend на loopback.

```bash
cd /opt/amn2

grep -F 'web serve --host 127.0.0.1 --port 3030' deploy/systemd/amneziya-web.service.example

sudo cp deploy/systemd/amneziya-web.service.example /etc/systemd/system/amneziya-web.service
sudo systemctl daemon-reload
sudo systemctl restart amneziya-web
sudo systemctl status amneziya-web --no-pager

curl -sS -o /dev/null -w 'web_login_http=%{http_code}\n' http://127.0.0.1:3030/login
ss -ltnp | grep -E ':3030|:3040' || true
```

Ожидаем:

```text
web_login_http=200
web listener: 127.0.0.1:3030
api listener: 127.0.0.1:3040 only while smoke server is running
```

## 9. Safe Evidence Для Чата

Прислать только:

```text
source_update_status: passed
source_overlay_commit: c92bd1a
runtime_preserved: data/.env/servers.yml/venv present
VPS_APPLY_ENABLED: false
APP_SECRET_KEY: present
backup_create: passed
backup_file: backups/<filename>.tar.enc
backup_verify: passed
bot_check_network: ok
server_preflight: ok
server_check_dry_run: ok
api_smoke_status: passed
api_checked_routes: 6
api_route_status_codes: 200
api_forbidden_markers: []
api_token_lifecycle: issued-hidden-and-revoked
web_login_http: 200
web_listener: 127.0.0.1:3030
api_listener: 127.0.0.1:3040
```

Не присылать raw API token, Authorization header, token hash, `.env`, full `servers.yml`, PrivateKey, PresharedKey, QR, `vpn://`, full config, full logs or backup content.

## 10. Решение После Alignment

Если все пункты прошли, `c92bd1a` можно закрывать как current production source overlay gate. Следующий шаг после этого: не broad write API, а отдельный operator-approved live-write window для одной контролируемой user/peer операции или следующий read-only controller slice.
