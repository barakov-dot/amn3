# AMN2 VPS API Smoke Evidence - 2026-06-02

Дата: 2026-06-02.

Назначение: зафиксировать безопасный итог реального VPS loopback smoke для ветки `amn2/codex/read-only-api-route-shell` без публикации SSH-доступа, `.env`, токенов, ключей, PSK, config contents или `api-server.log`.

## Source

Операторский запуск на VPS:

```text
workspace: /opt/amn2
server name: local
api bind: http://127.0.0.1:3040
script version: 2026-06-02.2
script sha256: 6ebe5c50d634541dd1a8fb1bac269e2593deae335e3d75f40a4d589a48a33743
safe evidence dir: /opt/amn2/vps-smoke/api-loopback-20260602T171639Z
```

`/opt/amn2` reported `not a git checkout` because the VPS install used the source-overlay/update kit path rather than a live git checkout.

## Result

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
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260602T171639Z.tar.gz
```

## Security Boundary

- Raw bearer tokens, token hashes, headers, `.env`, private keys, PSK and config bodies were not recorded in AMN3.
- `api-server.log` remains excluded unless manually redacted.
- `VPS_APPLY_ENABLED=false` remained the required smoke boundary.
- The first API lane remains read-only and aggregate-only.

## Decision

The read-only API route shell passed the real VPS loopback smoke gate. The next step is not another local-only API implementation slice, but a PR/merge decision for `amn2/codex/read-only-api-route-shell` back into stable `codex-vps-test-prep`.

Still blocked until separate controlled VPS gates:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- SSH/sync/config/runtime-changing routes.
