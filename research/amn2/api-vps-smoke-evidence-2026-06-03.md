# AMN2 VPS API Smoke Evidence - 2026-06-03

Дата: 2026-06-03.

Назначение: зафиксировать безопасный итог реального VPS loopback API-only smoke после заполнения `.env`/`servers.yml` и DB-only синхронизации server row в SQLite. Секреты, `.env`, `servers.yml`, raw API token, token hash, Authorization header, private keys, PSK, config contents и `api-server.log` не публиковались.

## Source

Операторский запуск на VPS:

```text
workspace: /opt/amn2
server name: local
api bind: http://127.0.0.1:3040
script version: 2026-06-02.3
script sha256: b348f493de107a93f45b6dfb89848e3370556701c24ef5e84eea774d16e1c144
safe evidence dir: /opt/amn2/vps-smoke/api-loopback-20260603T112418Z
```

Перед smoke оператор выполнил DB-only sync из `servers.yml` в `data/amneziya.sqlite3`.
Безопасный вывод:

```text
server_synced: (1, 'local', 'active', 'docker')
```

`/opt/amn2` reported `not a git checkout` because the VPS install used the source-overlay/update kit path rather than a live git checkout.

## Result

```text
VPS verdict: pass
run_id: 20260603T112418Z
preflight_status: skipped
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260603T112418Z.tar.gz
```

## Decision

The read-only API baseline is confirmed on real VPS with API-only smoke after DB-only server config sync. The follow-up packaging fix is to make `amn2_api_loopback_smoke.sh` perform that DB-only sync automatically before route smoke, without entering `server preflight`, SSH, Docker or live apply gates.

Still blocked until separate controlled VPS gates:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- SSH/sync/config/runtime-changing routes.
