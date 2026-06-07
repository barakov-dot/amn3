# Web-admin loopback systemd VPS smoke evidence

Дата: 2026-06-07.

Назначение: зафиксировать safe evidence после source-overlay promotion AMN2 head `c92bd1a Bind web admin systemd to loopback` на `/opt/amn2`. Этот срез нужен перед controlled production launch, чтобы web/admin backend по systemd template слушал только `127.0.0.1:3030` и работал через утвержденный HTTPS reverse proxy.

## Scope

```text
AMN2 branch: codex-vps-test-prep
AMN2 commit: c92bd1a Bind web admin systemd to loopback
target: /opt/amn2
previous source overlay: 42ffa65 Record git checkout smoke status
source overlay after: c92bd1a
VPS_APPLY_ENABLED: false
```

Это read-only/source-overlay smoke. Он не включает live peer apply/revoke, не открывает public API `3040`, не открывает direct public web/admin `3030` и не расширяет API/config/backup/Local Agent surfaces.

## Package

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source zip: dist/amn2-codex-vps-test-prep-c92bd1a-source.zip
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
operator doc: dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
package evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
```

VPS download and checksum:

```text
amn2-vps-update-and-smoke-kit-c92bd1a.zip: OK
amn2-codex-vps-test-prep-c92bd1a-source.zip: OK
```

## Source Update Evidence

```text
source_update_status: passed
run_id: 20260607T182118Z
target: /opt/amn2
source_commit: c92bd1a
source_sha: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260607T182118Z
runtime preservation: .env/data/venv/servers.yml not present in source zip and preserved
```

Operator confirmation after smoke:

```text
source overlay after: c92bd1a
```

## Read-only API Smoke Evidence

```text
VPS verdict: pass
run_id: 20260607T182131Z
workspace: /opt/amn2
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T182131Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T182131Z.tar.gz
```

Route-level result:

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

## Web/Admin Loopback Template Evidence

VPS command output confirmed the systemd template command:

```text
ExecStart=/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
```

This matches the approved reverse-proxy boundary: web/admin backend stays on loopback, while public access, if enabled, must be through HTTPS reverse proxy.

## Decision

```text
decision: read-only-vps-smoke-pass-c92bd1a
current VPS source overlay: c92bd1a
checked_routes: 6
web/admin backend template: loopback-only 127.0.0.1:3030
API listener policy: 127.0.0.1:3040 loopback-only
controlled production next gate: operator-only web/admin and bot launch checklist
```

Still blocked until separate gates:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web/admin `3030` exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links or full logs.
