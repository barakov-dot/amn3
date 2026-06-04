# AMN2 API/Web Panel VPS Evidence - 2026-06-04

Дата: 2026-06-04.

Назначение: зафиксировать безопасный итог реального VPS gate для stable production head `294803e Add API readiness and token web pages`: API loopback smoke и первичная web-admin проверка новых API/web-panel страниц. Секреты, `.env`, `servers.yml`, raw API token, Authorization header, token hash, private keys, PSK, config contents, QR, `vpn://` и полный `api-server.log` не публиковались.

## Source

Операторский запуск на VPS:

```text
workspace: /opt/amn2
server name: local
api bind: http://127.0.0.1:3040
script version: 2026-06-04.2
script sha256: 2506968a20aa282f78741f739c15401414682c513a9aebed6d199683aaedca77
safe evidence dir: /opt/amn2/vps-smoke/api-loopback-20260604T102355Z
```

`/opt/amn2` reported `not a git checkout` because the VPS install used the source-overlay/update kit path rather than a live git checkout.

## API Loopback Result

```text
VPS verdict: pass
run_id: 20260604T102355Z
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260604T102355Z.tar.gz
```

## Web Panel Observation

Web server booted successfully:

```text
python -m app.cli web serve --host 127.0.0.1 --port 3030
Uvicorn running on http://127.0.0.1:3030
```

Operator also temporarily ran the web server on `0.0.0.0:3030` and accessed it from a private LAN client. This confirms route rendering but should not become the default exposure model. Future operator checks should prefer `127.0.0.1` plus SSH tunnel, or a separately approved firewall/TLS/reverse-proxy gate.

Safe web routes observed as HTTP 200:

```text
GET /
GET /servers
GET /servers/1
GET /api-readiness
GET /api-tokens
GET /users
GET /orders
GET /config-templates
GET /logs
GET /settings
```

Screenshot evidence in the chat showed `API readiness` rendering with:

- allowed read scopes: `metrics:read`, `server:read`;
- aggregate state: `Servers=1`, `Users=0`, `Devices=0`;
- blocked slice entries for `/api/clients` write CRUD, API `config:read`, public config delivery and live peer apply/revoke.

## Remote-Read Note

The web log included:

```text
POST /servers/1/sync/run -> 303 See Other
```

In the current policy matrix this route is `web.servers.sync_run`, operation class `remote-read`, not state-write. It reads live VPS peer inventory and updates the local sync view. This observation is useful but must remain separate from the API/web-panel gate: it is not approval for live peer apply/revoke, config delivery, write API routes, Docker restart or runtime-changing operations.

## Decision

Stable `codex-vps-test-prep` at `294803e` is confirmed on the real VPS for:

- API loopback smoke with DB-only server config sync;
- web-admin startup;
- `API readiness` page rendering;
- `API tokens` page route availability;
- read-only API boundary display.

Still blocked until separate controlled gates:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- live peer apply/revoke;
- SSH/sync/config/runtime-changing routes;
- public web/API exposure without explicit TLS/reverse-proxy/firewall decision.
