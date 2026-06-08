# AMN2 Target Server Prep Runbook

Дата: 2026-06-08.

Назначение: подготовить новый целевой VPS для AMN2/API после validation-pass `f7f6131`, не смешивая ручную validation-проверку с будущим service-mode deployment.

## Текущая опора

```text
current AMN2 head: f7f6131 Update integration status for c92 manual prelaunch
current AMN3 package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
current package status: read-only-vps-smoke-pass
latest validation repeat API smoke: 20260607T204300Z
current accepted runtime mode on validation VPS: manual
target server mode before separate approval: manual bootstrap + read-only smoke
VPS_APPLY_ENABLED: false
```

Validation VPS больше не используем для source-overlay экспериментов. Новый VPS рассматриваем как отдельный target-server gate.

## Что нужно от нового VPS

Безопасные требования до установки AMN2:

- чистая Ubuntu/Debian LTS;
- SSH доступ с ключом или временным паролем, который будет заменен;
- известный публичный IP и будущий домен для web/admin HTTPS;
- Docker runtime для AmneziaWG;
- закрытые наружу `3030` и `3040`;
- открыты только SSH, будущий HTTPS и нужные VPN-порты;
- отдельный секретный канал для `.env`, Telegram token, API/admin secrets, SSH password/key material.

В чат не присылать: `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Phase 0. Safe Server Facts

На новом VPS выполнить и прислать только безопасную сводку:

```bash
hostnamectl
cat /etc/os-release
uname -a
date -u
ss -ltnp
command -v docker || true
docker --version 2>/dev/null || true
docker ps --format '{{.Names}}' 2>/dev/null || true
```

Ожидаем:

```text
os: Ubuntu/Debian LTS
time_utc: correct
docker: present-or-to-install
public_3030: no
public_3040: no
```

## Phase 1. Base Hardening

До AMN2:

```bash
apt update
apt install -y curl ca-certificates git unzip python3 python3-venv python3-pip rsync ufw
timedatectl set-ntp true
```

Firewall baseline, пример:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw status verbose
```

VPN-порты добавлять только после подтверждения фактической Amnezia конфигурации.

## Phase 2. AMN2 Runtime Bootstrap

Если `/opt/amn2` еще нет, не использовать старый source-overlay apply как первый шаг. Сначала создать базовый runtime:

```bash
mkdir -p /opt/amn2
cd /opt/amn2
python3 -m venv venv
source venv/bin/activate
```

Дальше выбрать один путь:

```text
preferred: clone/private checkout of barakov-dot/amn2 or controlled source archive
fallback: unpack f7f6131 source zip into /opt/amn2 after checksum verification
```

Runtime-файлы создаются только на VPS:

```text
/opt/amn2/.env
/opt/amn2/servers.yml
/opt/amn2/data/
/opt/amn2/backups/
```

Обязательные guards:

```bash
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
```

## Phase 3. Read-Only Gate

После установки зависимостей и runtime config:

```bash
cd /opt/amn2
source venv/bin/activate

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

Ожидаем:

```text
bot_check_network: ok
server_preflight: ok
server_check_dry_run: ok
peer apply/revoke: dry-run only
traffic: dry-run only
VPS_APPLY_ENABLED: false
```

## Phase 4. API Loopback Smoke

API запускать только на loopback:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Во втором shell:

```bash
cd /opt/amn2
source venv/bin/activate
python -m app.cli api smoke-cycle \
  --db /opt/amn2/data/amneziya.sqlite3 \
  --base-url http://127.0.0.1:3040 \
  --server-name local \
  --name target-server-smoke \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Ожидаем:

```text
status: passed
checked_routes: 6
route_status_codes: 200
forbidden_markers: none
raw_token_display: hidden
revoke_status: revoked
```

## Phase 5. Manual Web/Admin Gate

До отдельного service-mode approval:

```bash
cd /opt/amn2
source venv/bin/activate
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Проверка:

```bash
curl -sS -o /dev/null -w 'web_login_http=%{http_code}\n' http://127.0.0.1:3030/login
ss -ltnp | grep -E ':3030|:3040' || true
```

Ожидаем:

```text
web_login_http: 200
web_listener: 127.0.0.1:3030
api_listener: 127.0.0.1:3040 only during smoke
public_3030: no
public_3040: no
```

## Phase 6. Backup Gate

Перед любым service-mode:

```bash
cd /opt/amn2
source venv/bin/activate

python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
BACKUP_FILE="$(ls -t backups/*.tar.enc | head -n 1)"
printf 'backup_file=%s\n' "$BACKUP_FILE"
python -m app.cli backup verify --file "$BACKUP_FILE"
```

Ожидаем manifest без секретов:

```text
database_kind: sqlite
includes: database, manifest
excludes: app_secret_key, telegram_bot_token, qr_files, plain_configs
```

## Service-Mode Stop Line

Не включать без отдельного подтверждения:

- `systemd` для web/API/bot;
- reverse proxy HTTPS;
- public web/admin;
- live peer apply/revoke;
- public API `3040`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent mutations;
- backup/import/reboot routes.

## Safe Evidence To Return

```text
target_server_label:
os:
docker_status:
amn2_head_or_source_overlay:
VPS_APPLY_ENABLED:
bot_check_network:
server_preflight:
server_check_dry_run:
api_smoke_status:
checked_routes:
auth_status:
listener_status:
audit_status:
web_login_http:
web_listener:
public_3030:
public_3040:
backup_verify:
safe_evidence_dir:
```

## Next Decision

Если все target-server manual gates прошли, следующий выбор:

```text
option A: keep manual runtime and continue read-only/status slices
option B: open separate service-mode gate for systemd + HTTPS reverse proxy on this target server
```
