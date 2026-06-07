# AMN2 VPS Update And Smoke Kit 42ffa65

Date: 2026-06-07.

Purpose: update existing `/opt/amn2` source overlay to `amn2/codex-vps-test-prep` head `42ffa65 Record git checkout smoke status` and run a read-only API/web-admin smoke gate. This package tests promotion of the read-only status line that was already smoke-tested on `/opt/amn2-git`; it does not enable live peer mutations or new write/config/backup/agent surfaces.

Important distinction:

```text
package/source overlay commit: 42ffa65 Record git checkout smoke status
app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
previous source overlay: c8a6363 Add Local Agent runtime summary mapper
previous source-overlay smoke: 20260606T202040Z, pass
expected read-only routes after update: 6
```

## Boundaries

Allowed:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv`;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run API loopback smoke on `127.0.0.1:3040`;
- check web-admin read-only/status pages through loopback or approved reverse proxy.

Still blocked without a separate gate:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw token, Authorization header, token hash, private keys, PSK, `.conf`, QR, `vpn://`, or full logs.

## 1. Unpack Kit

On the VPS:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-42ffa65.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-42ffa65
mkdir -p amn2-vps-update-and-smoke-kit-42ffa65
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-42ffa65.zip amn2-vps-update-and-smoke-kit-42ffa65
cd amn2-vps-update-and-smoke-kit-42ffa65
sha256sum -c amn2-codex-vps-test-prep-42ffa65-source.zip.sha256.txt
```

Expected source SHA:

```text
8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
```

## 2. Apply Source Overlay

```bash
cd /root/amn2-vps-update-and-smoke-kit-42ffa65
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=42ffa65
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Run API Loopback Smoke

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Expected summary:

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

`api-smoke-result.json` should show 6 read-only routes:

```text
servers
integration_status
local_agent_runtime_summary
server_summary
metrics_summary
users_summary
```

For `/api/integration/status`, expected safe state:

```text
status: controlled_prod_ready
api_baseline.write_routes_enabled: false
api_baseline.public_api_exposed: false
controlled_prod_readiness.source_overlay_head: c8a6363
local_read_only_extension.head: 62ff184
local_read_only_extension.status: vps_smoke_passed_git_checkout
next_gate: Promote 62ff184 through source overlay update or choose next read-only slice
```

That `next_gate` text is expected for this package because the code records the prior git-checkout smoke state. If this source-overlay update/smoke passes on `/opt/amn2`, record the safe evidence first; a later read-only status-contract update can then replace the git-checkout wording with source-overlay pass wording.

## 4. Web/Admin Boundary

Web/admin access is operator-only through the approved HTTPS reverse proxy. API `3040` must remain loopback-only.

Optional loopback check:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
python -m app.cli web serve --host 127.0.0.1 --port 3030
curl -sS -o /dev/null -w 'login_http=%{http_code}\n' http://127.0.0.1:3030/login
```

Expected:

```text
login_http=200
```

## 5. Safe Evidence To Return

Return only safe summary fields:

```text
source overlay before:
source overlay after:
source_update_status:
api_smoke_status:
checked_routes:
route status codes:
forbidden_markers:
auth_status:
missing_bearer_actual:
wrong_scope_actual:
revoked_token_actual:
listener_status:
loopback_only:
audit_status:
api_read_rows:
server_db_sync:
web_login_http:
VPS_APPLY_ENABLED shell:
VPS_APPLY_ENABLED .env:
decision:
```

Do not return raw tokens, Authorization headers, token hashes, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR payloads, `vpn://`, or full `api-server.log` without manual redaction.

## Decision

If source overlay update and read-only smoke pass:

```text
decision: 42ffa65 source overlay update/smoke passed; runtime promotion evidence ready for follow-up status-contract update
```

If any stop condition appears:

```text
decision: keep controlled-prod-ready source overlay c8a6363; 42ffa65 promotion requires fix or rerun
```
