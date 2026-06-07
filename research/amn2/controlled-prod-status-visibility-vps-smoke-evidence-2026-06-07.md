# `42ffa65` controlled prod status visibility VPS smoke evidence

Дата: 2026-06-07.

Назначение: зафиксировать safe summary фактического promotion `/opt/amn2` до source overlay `42ffa65 Record git checkout smoke status` и повторного read-only API smoke уже на production source-overlay path.

Это evidence не содержит секретов, raw token, Authorization header, token hash, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR, `vpn://` или полный `api-server.log`.

## Scope

```text
target: /opt/amn2
source overlay before: c8a6363
source overlay after: 42ffa65
source update run_id: 20260607T165559Z
api smoke run_id: 20260607T165625Z
package: /root/amn2-vps-update-and-smoke-kit-42ffa65.zip
package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source zip: /root/amn2-vps-update-and-smoke-kit-42ffa65/amn2-codex-vps-test-prep-42ffa65-source.zip
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
expected commit: 42ffa65
VPS_APPLY_ENABLED: false
```

## Source Update Result

```text
source_update_status=passed
target=/opt/amn2
source_commit=42ffa65
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260607T165559Z
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
python=Python 3.13.5
```

`/opt/amn2` is still a source-overlay install, not a git checkout. `branch/head: not a git checkout` is expected for this deployment path.

## API Smoke Result

```text
VPS verdict: pass
run_id: 20260607T165625Z
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T165625Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T165625Z.tar.gz
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
```

Auth checks:

```text
missing_bearer_expected=401
missing_bearer_actual=401
wrong_scope_expected=403
wrong_scope_actual=403
revoked_token_expected=401
revoked_token_actual=401
```

Listener and audit:

```text
expected_host=127.0.0.1
host=127.0.0.1
loopback_only=yes
api_read_rows=5
audit_safe=yes
server_db_sync=passed
server id=1
server name=local
server status=active
server runtime=docker
```

## Decision

```text
decision: source-overlay-smoke-pass-42ffa65
current VPS source overlay: 42ffa65 Record git checkout smoke status
previous VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
controlled prod mode: operator-only
public API 3040: blocked; listener remains loopback-only
web/admin access: through approved HTTPS reverse proxy
live write expansion: blocked until separate gate
```

This promotes the read-only status visibility line from git-checkout smoke evidence to production source-overlay smoke evidence. It does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot routes or new live peer operations.

## Repeat Smoke

A later safe repeat read-only smoke for the same `42ffa65` source overlay passed with `run_id=20260607T165807Z`, `checked_routes=6`, all route status codes `200`, auth checks `401/403/401`, listener passed, and audit passed. Evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

## Next Safe Gate

Use this evidence as the current AMN3 truth for `amn2` controlled production coordination. The next safe local step is either:

- use the later `c92bd1a` smoke evidence as the current source-overlay truth and complete the controlled production launch checklist for web/admin and bot runtime;
- or continue with another read-only controller/status/observability slice.

Any live write, config delivery, backup/import or Local Agent mutation surface still needs its own design, tests, runbook and real VPS gate.
