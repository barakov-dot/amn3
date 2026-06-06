# AMN2 VPS Smoke Runbook: 62ff184

Дата: 2026-06-07.

Назначение: безопасно проверить read-only app-code срез `62ff184 Update controlled prod status visibility` на VPS перед обновлением source overlay. Этот runbook не включает `VPS_APPLY_ENABLED=true`, не открывает public API `3040`, не добавляет write routes и не требует публикации секретов.

Если этот документ читается из более нового documentation-only commit, перед запуском брать фактический expected commit из `git log -1 --oneline` и package manifest. `62ff184` остается app-code срезом, ради которого подготовлен этот smoke.

## Стартовая Точка

```text
production repo: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
app-code slice to test: 62ff184 Update controlled prod status visibility
expected package commit: use git log -1 / package manifest before VPS update
current VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
last VPS smoke: 20260606T202040Z, pass
current prod decision: controlled-prod-ready for source overlay c8a6363
next decision after this run: keep c8a6363 or promote 62ff184 after source overlay update/smoke
```

`62ff184` меняет только read-only status visibility: `/api/integration/status`, страницу `/integration-status`, runbook/evidence/handoff. Он не включает live peer mutations, config delivery, public API, Local Agent mutations, backup/import/reboot routes или `config:read`.

## Фактический Результат Git-Checkout Smoke

Оператор выполнил read-only smoke на git-managed checkout `/opt/amn2-git` через `python -m app.cli api smoke-cycle`.

```text
Дата и время проверки: 2026-06-06 21:41 UTC
workspace: /opt/amn2-git
server: local
api_smoke_status: passed
checked_routes: 6
servers: 200
integration_status: 200
local_agent_runtime_summary: 200
server_summary: 200
metrics_summary: 200
users_summary: 200
forbidden_markers: []
smoke_token_status: revoked
raw_token_display: hidden
```

Decision для этого прогона:

```text
decision: 62ff184 read-only git-checkout VPS smoke passed
source_overlay_promotion: not claimed by this smoke; promote /opt/amn2 separately if needed
```

## Локальная Подготовка

Перед передачей на VPS убедиться, что локальная ветка синхронизирована:

```powershell
cd C:\Users\SooL\Documents\Amneziya
git status --short --branch
git log -3 --oneline --decorate
git remote -v
```

Ожидаемо:

```text
branch: codex-vps-test-prep
HEAD/package commit: matches the package prepared for this VPS update
production remote: amn2 -> https://github.com/barakov-dot/amn2.git
working tree: clean
```

## Что Выполнить На VPS

Работать в `/opt/amn2`, где используется source overlay/update kit path. До отдельного live-write решения держать `VPS_APPLY_ENABLED=false`.

```bash
cd /opt/amn2
source venv/bin/activate

echo "current source overlay:"
cat .amn2_source_overlay_commit

echo "runtime preservation:"
test -d data && echo "data_dir=present" || echo "data_dir=missing"
test -f .env && echo "env_file=present" || echo "env_file=missing"
test -f servers.yml && echo "servers_yml=present" || echo "servers_yml=missing"

echo "safe default:"
export VPS_APPLY_ENABLED=false
printf 'shell VPS_APPLY_ENABLED=%s\n' "${VPS_APPLY_ENABLED:-unset}"
```

Если для этого среза уже подготовлен update kit, применить его только через существующий safe source-overlay update flow, который сохраняет `.env`, `data/`, `venv/` и `servers.yml`. После применения проверить:

```bash
cat .amn2_source_overlay_commit
```

Ожидаемо после успешного update:

```text
expected package commit from manifest
```

Если update kit еще не подготовлен, не собирать его вручную на VPS и не копировать файлы частями. Вернуться в локальный чат за package/update kit.

## Read-only API Smoke

API должен слушать только loopback:

```bash
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
```

Terminal A:

```bash
python -m app.cli api serve --host 127.0.0.1 --port 3040
```

Terminal B:

```bash
python -m app.cli api smoke-cycle \
  --db data/amneziya.sqlite3 \
  --base-url http://127.0.0.1:3040 \
  --server-name "$AMN2_SERVER_NAME" \
  --name vps-smoke-62ff184 \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Ожидаемый safe result:

```text
status: passed
checked_routes: 6
servers: 200
integration_status: 200
local_agent_runtime_summary: 200
server_summary: 200
metrics_summary: 200
users_summary: 200
forbidden_markers: []
revoke.status: revoked
```

## Listener/Auth/Audit Evidence

После smoke проверить только safe facts:

```bash
ss -ltnp | grep ':3040' || true
```

Ожидаемо:

```text
127.0.0.1:3040
```

Если smoke-cycle выводит auth/listener/audit summary, вернуть только:

```text
auth_status:
missing_bearer_actual:
wrong_scope_actual:
revoked_token_actual:
listener_status:
loopback_only:
audit_status:
api_read_rows:
audit_safe:
server_db_sync:
```

## Web/Admin Boundary

Web/admin открывается через утвержденный HTTPS reverse proxy. API `3040` наружу не выставлять.

Проверка loopback web без публикации наружу:

```bash
python -m app.cli web serve --host 127.0.0.1 --port 3030
curl -sS -o /dev/null -w 'login_http=%{http_code}\n' http://127.0.0.1:3030/login
```

Ожидаемо:

```text
login_http=200
```

Если `3030` уже занят работающим процессом, не убивать его без причины. Достаточно вернуть `ss -ltnp | grep ':3030'` и `login_http=200`.

## Что Вернуть В Чат

Вернуть только safe summary:

```text
source overlay before:
source overlay after:
source_update_status:
api_smoke_status:
checked_routes:
route status codes:
forbidden_markers:
auth_status:
missing_bearer_actual:
wrong_scope_actual:
revoked_token_actual:
listener_status:
loopback_only:
audit_status:
api_read_rows:
server_db_sync:
web_login_http:
VPS_APPLY_ENABLED shell:
VPS_APPLY_ENABLED .env:
decision:
```

Не присылать:

- raw API token;
- Authorization header;
- token hash;
- `.env`;
- `servers.yml`;
- private key;
- PSK / `PresharedKey`;
- `.conf`, QR payload или `vpn://`;
- полный `api-server.log` без ручной redaction.

## Stop Conditions

Остановиться и не считать `62ff184` promoted, если:

- source overlay commit не стал expected package commit после update;
- checksum package/update kit не совпал;
- smoke status не `passed`;
- `checked_routes` не `6`;
- любой route вернул forbidden markers;
- auth checks не дают ожидаемые `401/403/401`;
- listener не loopback-only;
- audit небезопасен или содержит secret-bearing data;
- `VPS_APPLY_ENABLED` оказался `true`;
- для проверки требуется открыть API `3040` наружу.

## Decision

Если проверки прошли на git-managed checkout `/opt/amn2-git`, можно фиксировать:

```text
decision: 62ff184 read-only git-checkout VPS smoke passed; source overlay promotion remains separate
```

Если отдельно выполнен source overlay update flow и после него `/opt/amn2/.amn2_source_overlay_commit` показывает `62ff184`, можно фиксировать:

```text
decision: 62ff184 source overlay update/smoke passed; source overlay can be treated as promoted
```

Если часть проверок не выполнена:

```text
decision: keep controlled-prod-ready source overlay c8a6363; 62ff184 source overlay promotion requires fix or rerun
```
