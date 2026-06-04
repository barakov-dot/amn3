# API VPS Smoke Evidence

Дата: 2026-06-02.

Назначение: зафиксировать только безопасные факты реального VPS smoke для read-only API shell на ветке `codex/read-only-api-route-shell`.

Template policy: Заполнять после реального VPS smoke; historical command marker `python -m app.cli api smoke-check`; historical filled evidence ниже оставляет только safe summary.

Не вставлять raw API token, Authorization header, token hash, `.conf`, QR, `vpn://`, `PrivateKey`, `PresharedKey`, SSH password/private key, `.env`, PSK, полные response bodies или `api-server.log` без ручной redaction.

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
