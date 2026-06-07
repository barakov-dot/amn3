# AMN2 Controlled Prod Readiness Runbook

Дата: 2026-06-06. Обновлено: 2026-06-07.

Назначение: зафиксировать безопасный operator-only production-режим для текущей ветки `codex-vps-test-prep` после read-only VPS smoke. Этот runbook не открывает public web/API, `/api/clients` write CRUD, API `config:read`, public/self-service config delivery, Local Agent mutations, backup/import/reboot routes или новые live peer mutations.

## Текущая production-точка

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
latest VPS source overlay head: 42ffa65 Record git checkout smoke status
latest VPS read-only smoke: 42ffa65 pass, checked_routes=6, 2026-06-07 15:09 UTC
previous VPS source overlay head: c8a6363 Add Local Agent runtime summary mapper
local head deployment status: source overlay promoted and smoked
previous VPS read-only smoke: 32d01fd pass, run_id 20260606T185114Z
previous API route smoke: 1a193b9 pass, run_id 20260606T154636Z
current prod decision: controlled-prod-ready for source overlay 42ffa65
web/admin access: HTTPS reverse proxy approved; API 3040 remains loopback-only
Phase 2 live single disposable peer gate: verified-live on stable line
```

Source overlay `42ffa65` прошел safe update на `/opt/amn2` с сохранением `data/`, `.env`, `servers.yml` и `venv/`, затем read-only API smoke на loopback `127.0.0.1:3040`: 6 routes, all 200, forbidden markers empty, smoke token revoked. Web/admin доступ подтвержден как HTTPS reverse proxy, при этом порт API `3040` наружу не выставляется.

## Controlled Prod Mode

Controlled prod означает:

- VPS остается на последнем smoke-passed source overlay, пока новый package не пройдет read-only update/smoke;
- `VPS_APPLY_ENABLED=false` является безопасным состоянием по умолчанию;
- API и web/admin проверки идут через loopback, SSH tunnel, private network или отдельно утвержденный reverse-proxy/TLS/firewall gate;
- существующие operator CLI/bot flows используются только внутри уже подтвержденного behavior contract;
- новые live writes требуют отдельного operator confirmation и отдельной evidence;
- в GitHub, AMN3 и чат не публикуются raw token, Authorization header, token hash, `.env`, `servers.yml`, private key, PSK, `.conf`, QR payload или `vpn://`.

Controlled prod не означает публичный SaaS-режим.

## Allowed Without New Gate

Разрешено без нового live-write gate:

- повторить read-only API loopback smoke;
- выполнить DB-only server config sync, который использует smoke script;
- проверить web/admin read-only/status pages через loopback или SSH tunnel;
- инспектировать только safe evidence summary;
- продолжать уже verified operator flows по существующим runbooks;
- фиксировать safe status/evidence updates.

## Still Blocked

До отдельных gates заблокированы:

- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply` и `revoke-peer --apply`;
- public web/API exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- полные logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR и `vpn://` в evidence.

## Readiness Checklist

Перед статусом `controlled-prod-ready`:

- [ ] Git commit/package checksum записан.
- [ ] VPS source overlay commit совпадает с последним smoke-passed commit или явно superseding smoke-passed commit.
- [ ] Последний read-only smoke safe summary имеет `VPS verdict: pass`.
- [ ] Smoke result показывает только read-only routes и `status: passed`; для head с `/api/local-agent/runtime/summary` ожидается `checked_routes: 6`.
- [ ] `/api/integration/status` сообщает `controlled_prod_ready`, `phase_2=verified_live`, `write_routes_enabled=false`, `write_operations_enabled=false`, `public_api_exposed=false`.
- [ ] Auth checks: missing bearer `401`, wrong scope `403`, revoked token `401`.
- [ ] Listener и audit checks имеют `passed`.
- [ ] Operator shell по умолчанию держит `VPS_APPLY_ENABLED=false`.
- [ ] Web/admin access path не требует public exposure.
- [ ] SSH host key prompt не появился, либо host key проверен out-of-band.
- [ ] Recovery path известен до будущего write gate.
- [ ] Evidence не содержит secret-bearing data.
- [ ] Нет активного chat-exposed API token, либо он явно отозван/истек и это зафиксировано безопасным audit/evidence.

## Operator Verification Commands

Команды безопасны как шаблон, потому что не содержат secret values. Запускать на VPS только при необходимости:

```bash
cd /opt/amn2
source venv/bin/activate

cat .amn2_source_overlay_commit

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
  --name vps-smoke \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Публиковать после smoke только safe summary из вывода `api smoke-cycle`:

```text
status
checked_routes
route status codes
forbidden_markers
revoke.status
```

`api-server.log` не публиковать без ручной redaction.

## Stop Conditions

Остановиться и не переходить к prod decision, если:

- package checksum не совпал;
- source overlay commit не соответствует ожидаемому smoke-passed commit;
- любой smoke status не `passed`;
- любой route сообщает forbidden markers;
- auth checks не возвращают ожидаемые `401/403/401`;
- появился неожиданный SSH host key prompt;
- для проверки требуется public web/API exposure;
- recovery path неясен;
- evidence требует публикации секретов или full logs.
- есть активный chat-exposed API token, который не отозван и не истек.

## Recovery Boundary

Этот readiness runbook read-only и не должен требовать rollback.

Для будущих write gates recovery должен быть описан до запуска и ограничен конкретным объектом. Для peer apply/revoke это значит:

- отдельный disposable test peer;
- private notes для public key/PSK/private key, без публикации в GitHub/чат;
- revoke path проверен до apply;
- final sync подтверждает, что test peer удален или восстановлен в ожидаемое состояние.

## Evidence Template

```text
date/time:
operator:
server alias:
source overlay commit:
package:
package sha256:
read-only smoke run_id:
preflight_status:
server_db_sync_status:
api_ready_status:
api_smoke_status:
auth_status:
listener_status:
audit_status:
checked_routes:
forbidden_markers:
web/admin access path:
VPS_APPLY_ENABLED default:
host key prompt:
recovery path known:
decision:
next action:
```

## Decision Rules

`controlled-prod-ready` разрешен только когда checklist закрыт и stop conditions отсутствуют. Для текущего VPS source overlay это состояние зафиксировано на `42ffa65`. Если следующий read-only head пройдет только git-checkout smoke, он не становится source overlay автоматически до отдельного source overlay promotion/update gate.

`needs-fix` обязателен, если smoke, auth, listener, audit, checksum, host key, access path или evidence hygiene не проходят.

`defer-prod` допустим, если система здорова, но operator recovery/access conditions еще не готовы.

## Next Engineering Slice

После `controlled-prod-ready` следующий инженерный slice должен оставаться read-only. Не переходить сразу к config delivery, public API writes, backup/import или Local Agent mutations. Для следующего среза выбрать read-only controller work или отдельный design/live gate.
