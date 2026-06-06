# API VPS Smoke Evidence

Дата: 2026-06-02. Обновлено: 2026-06-06.

Назначение: зафиксировать только безопасные факты реального VPS smoke для read-only API shell на ветке `codex/read-only-api-route-shell`.

Template policy: Заполнять после реального VPS smoke; current command marker `python -m app.cli api smoke-cycle`; historical filled evidence ниже оставляет только safe summary.

Не вставлять raw API token, Authorization header, token hash, `.conf`, QR, `vpn://`, `PrivateKey`, `PresharedKey`, SSH password/private key, `.env`, PSK, полные response bodies или `api-server.log` без ручной redaction.

## Controlled Prod Update: 2026-06-07 / c8a6363 source overlay

Назначение: зафиксировать safe summary фактического VPS состояния после source overlay update и loopback API smoke на `/opt/amn2`.

```text
source overlay commit: c8a6363
source update run_id: 20260606T202012Z
source_update_status: passed
api loopback smoke run_id: 20260606T202040Z
workspace: /opt/amn2
VPS checkout state: not a git checkout; source-overlay/update kit path
API bind: http://127.0.0.1:3040
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
server name: local
runtime: docker
```

Read-only route evidence:

```text
checked_routes: 5
status: passed

servers: 200, forbidden_markers=[]
integration_status: 200, forbidden_markers=[]
server_summary: 200, forbidden_markers=[]
metrics_summary: 200, forbidden_markers=[]
users_summary: 200, forbidden_markers=[]
```

Auth/listener/audit evidence:

```text
auth_status: passed
missing_bearer_actual: 401
wrong_scope_actual: 403
revoked_token_actual: 401
listener_status: passed
api_listener: 127.0.0.1:3040 loopback-only
audit_status: passed
api_read_rows: 5
audit_safe: yes
server_db_sync: passed
```

Access and recovery boundary:

```text
web/admin access: HTTPS reverse proxy approved by operator
public API 3040 exposure: blocked
data/: preserved
.env: preserved
servers.yml: preserved
recovery kits: 32d01fd and c8a6363 present with sha files and extracted dirs
controlled_prod_decision: controlled-prod-ready for source overlay c8a6363
next local head before VPS overlay update: 465444a requires fresh VPS smoke
```

## 0. Актуальный Smoke: 2026-06-06 / 64a6750

Назначение: зафиксировать безопасный факт read-only API smoke на git-managed checkout `/opt/amn2-git` после перехода с source overlay `/opt/amn2`.

```text
Дата и время проверки: 2026-06-06, около 20:48 UTC
VPS alias: mirror / local
Workspace: /opt/amn2-git
Branch: codex-vps-test-prep
Target app-code commit: 64a6750 Document controlled prod readiness
API bind: http://127.0.0.1:3040
VPS_APPLY_ENABLED: false
Server name: local
```

Preflight evidence:

```text
Telegram API: ok
Bot identity: ok
Proxy: enabled
server config: ok
database sync: ok
server check dry-run: ok
peer apply dry-run: ok
peer revoke dry-run: ok
traffic dry-run: ok
backup target: ok
```

Read-only route evidence:

```text
checked_routes: 5
status: passed

servers: 200, forbidden_markers=[]
integration_status: 200, forbidden_markers=[]
server_summary: 200, forbidden_markers=[]
metrics_summary: 200, forbidden_markers=[]
users_summary: 200, forbidden_markers=[]
```

Token evidence:

```text
new smoke token status: revoked
new smoke token revoke reason: smoke-complete
raw token/header/hash evidence: not published
previous chat-exposed token: not revoked by operator decision
previous chat-exposed token expiry reported by CLI: 2026-06-13T20:37:39+00:00
```

VPS verdict:

```text
api_smoke_status: passed
forbidden_markers: none
listener_scope: loopback-only
write_routes_enabled: false
write_operations_enabled: false
controlled_prod_decision: defer-prod
defer reason: previous chat-exposed token remains a token-hygiene exception until revoked or expired
```

This run confirms the read-only API route shell on the current app-code baseline. It does not grant public exposure, write API routes, `config:read`, Local Agent mutations, backup/import/reboot routes or broad live peer mutation permission.

Follow-up local route after this evidence:

```text
route: GET /api/local-agent/runtime/summary
scope: server:read
status: local-ready, not included in the 2026-06-06 VPS smoke above
next VPS smoke expectation: checked_routes=6
next VPS smoke command: python -m app.cli api smoke-cycle
secret boundary: no Local Agent host/port/token id/token hash/container/interface/config path
```

## 1. Контекст

```text
Дата и время проверки: 2026-06-02, run_id=20260602T171639Z
VPS alias: mirror / local
Workspace: /opt/amn2
Branch: codex/read-only-api-route-shell
Commit: 2010d60 Add API VPS smoke evidence template
VPS checkout state: not a git checkout; source-overlay/update kit path
API bind: http://127.0.0.1:3040
Smoke script version: 2026-06-02.2
Smoke script sha256: 6ebe5c50d634541dd1a8fb1bac269e2593deae335e3d75f40a4d589a48a33743
VPS_APPLY_ENABLED: false
Safe evidence dir: /opt/amn2/vps-smoke/api-loopback-20260602T171639Z
Safe bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260602T171639Z.tar.gz
```

## 2. Route Evidence

Фактические aggregate counts и response bodies не копировались в чат/документ, чтобы не расширять evidence beyond safe summary. Smoke script выполнил route-level read-only проверку через scoped token.

```text
api_ready_status: passed
api_smoke_status: passed
```

Read-only API shell scope:

```text
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/metrics/summary
GET /api/users/summary
```

Forbidden data boundary:

```text
raw token/header/hash/config/key/PSK evidence: not published
full response bodies: not published
```

## 3. Auth And Scope Evidence

```text
auth_status: passed

Missing bearer token:
  expected HTTP: 401
  actual HTTP: 401

Wrong scope:
  expected HTTP: 403
  actual HTTP: 403

Revoked token after smoke:
  expected HTTP: 401
  actual HTTP: 401
```

## 4. Audit Evidence

```text
audit_status: passed
api_read rows present: verified by smoke script
metadata secret boundary: raw token/header/hash/config/key/PSK not published
```

`api-server.log` was not copied into AMN3 and must not be shared unless manually redacted.

## 5. Network Exposure Evidence

```text
API bind: http://127.0.0.1:3040
listener_status: passed
```

API остается loopback-only (`127.0.0.1`) до отдельного решения о reverse proxy, TLS, rate-limit и production auth boundary.

## 6. VPS Verdict

```text
VPS verdict: pass
run_id: 20260602T171639Z
preflight_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
```

Next local action:

```text
PR/merge decision for codex/read-only-api-route-shell back into codex-vps-test-prep.
```

Next VPS action:

```text
No additional VPS action for this read-only aggregate API shell unless a merge/retest policy explicitly requires it.
```

## 7. Still Blocked Until Separate Gates

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- SSH/sync/config/runtime-changing routes;
- public unauthenticated `/docs` or `/metrics`.
