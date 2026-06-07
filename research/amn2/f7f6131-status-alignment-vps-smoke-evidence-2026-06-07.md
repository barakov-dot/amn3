# f7f6131 status alignment VPS smoke evidence

Дата: 2026-06-07.

Назначение: зафиксировать safe evidence фактического source-overlay update/read-only smoke для AMN2 `f7f6131 Update integration status for c92 manual prelaunch`.

## Result

```text
decision: read-only-vps-smoke-pass-f7f6131
source_overlay_commit: f7f6131
previous_proven_source_overlay: c92bd1a
source_update_run_id: 20260607T203721Z
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z
runtime_mode: manual
systemd_web: not-used
systemd_bot: not-used
VPS_APPLY_ENABLED: false
```

## Source Overlay Update

```text
run_id: 20260607T203721Z
target: /opt/amn2
source_zip: /root/amn2-vps-update-and-smoke-kit-f7f6131/amn2-codex-vps-test-prep-f7f6131-source.zip
source_sha: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
expected_commit: f7f6131
python: Python 3.13.5
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
source_update_status: passed
source_commit: f7f6131
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260607T203721Z
```

## API Loopback Smoke

```text
run_id: 20260607T203730Z
branch/head: not a git checkout
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T203730Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T203730Z.tar.gz
```

## Latest Repeat API Loopback Smoke

```text
run_id: 20260607T204300Z
branch/head: not a git checkout
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T204300Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T204300Z.tar.gz
note: api-server.log was not published and must not be sent unless manually redacted.
```

## Route Evidence

```text
checked_routes: 6
status: passed
servers: 200, forbidden_markers=[]
integration_status: 200, forbidden_markers=[]
local_agent_runtime_summary: 200, forbidden_markers=[]
server_summary: 200, forbidden_markers=[]
metrics_summary: 200, forbidden_markers=[]
users_summary: 200, forbidden_markers=[]
```

## Listener, Audit And Sync

```text
listener_rows: 1
expected_host: 127.0.0.1
host: 127.0.0.1
loopback_only: yes
api_read_rows: 5
audit_safe: yes
server_db_sync: passed
server_name: local
runtime: docker
source overlay after: f7f6131
VPS_APPLY_ENABLED: false
```

## Boundary

This evidence does not authorize:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web/admin `3030` exposure;
- service-mode `systemd`/reverse-proxy deployment without a separate gate;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links, backup contents or full logs.
