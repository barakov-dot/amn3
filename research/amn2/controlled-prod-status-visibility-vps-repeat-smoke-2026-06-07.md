# `42ffa65` controlled prod status visibility repeat VPS smoke

Дата: 2026-06-07.

Назначение: зафиксировать безопасный repeat read-only API smoke для уже promoted `/opt/amn2` source overlay `42ffa65 Record git checkout smoke status`. Это не новый promotion и не меняет safety boundary. Позже следующий gate `c92bd1a Bind web admin systemd to loopback` отдельно прошел source-overlay smoke.

Это evidence не содержит секретов, raw token, Authorization header, token hash, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR, `vpn://` или полный `api-server.log`.

## Scope

```text
target: /opt/amn2
source overlay commit before smoke: 42ffa65
api smoke run_id: 20260607T165807Z
package previously applied: /root/amn2-vps-update-and-smoke-kit-42ffa65.zip
VPS_APPLY_ENABLED: false
branch/head: not a git checkout
```

The source overlay update had already passed for `42ffa65`; this run reconfirmed the current source overlay and API smoke route inventory before moving to the next package gate.

## Pre-Smoke Confirmation

```text
.amn2_source_overlay_commit: 42ffa65
app_cli_file: /opt/amn2/app/cli.py
smoke_paths:
- servers
- integration_status
- local_agent_runtime_summary
- server_summary
- metrics_summary
- users_summary
```

## API Smoke Result

```text
VPS verdict: pass
run_id: 20260607T165807Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T165807Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T165807Z.tar.gz
```

Checked routes:

```text
checked_routes=6
servers: 200, forbidden_markers=[]
integration_status: 200, forbidden_markers=[]
local_agent_runtime_summary: 200, forbidden_markers=[]
server_summary: 200, forbidden_markers=[]
metrics_summary: 200, forbidden_markers=[]
users_summary: 200, forbidden_markers=[]
status=passed
```

## Decision

```text
decision: repeat-read-only-smoke-pass-42ffa65
current VPS source overlay: 42ffa65 Record git checkout smoke status
later source-overlay gate: c92bd1a Bind web admin systemd to loopback, read-only-vps-smoke-pass
controlled prod mode: operator-only
public API 3040: blocked; listener remains loopback-only
direct public web/admin 3030: blocked; approved path remains HTTPS reverse proxy
live write expansion: blocked until separate gate
```

This repeat pass preserves the current controlled production coordination state. It does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot routes or new live peer operations.
