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

## Supplemental Earlier API Bundle

Operator later provided the safe evidence files for an earlier same-day API smoke run. This is recorded as supporting evidence only; the current gate decision remains anchored on the later `20260604T102355Z` run with script version `2026-06-04.2`.

```text
run_id: 20260604T072704Z
script_version: 2026-06-04.1
script_sha256: efc04baa8236664e06656c0b81065eb757f69297e51d09a75a06d016e2f3c8ef
python: Python 3.13.5
vps_apply_enabled: false
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260604T072704Z.tar.gz
```

Safe summary:

```text
VPS verdict: pass
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
```

Route smoke result:

```text
checked_routes: 4
servers: 200
server_summary: 200
metrics_summary: 200
users_summary: 200
forbidden_markers: none
status: passed
```

Auth and audit checks:

```text
missing_bearer_expected=401 actual=401
wrong_scope_expected=403 actual=403
revoked_token_expected=401 actual=401
api_read_rows=5
audit_safe=yes
```

Listener check:

```text
expected_host=127.0.0.1
host=127.0.0.1
pid_match=yes
loopback_only=yes
```

Server DB sync:

```text
server_db_sync=passed
id=1
name=local
status=active
runtime=docker
```

Token lifecycle safe evidence existed for the run: the smoke token and wrong-scope token were issued with one-time raw-token display metadata only, then revoked with reason `smoke-complete`. Raw token values and token hashes were not included.

The operator also provided an `api-server.log` excerpt for this earlier run. It only showed loopback requests and expected HTTP statuses, but full server logs are not stored in this evidence file; future handoffs should continue sending only the safe evidence files unless a log is manually redacted first.

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
