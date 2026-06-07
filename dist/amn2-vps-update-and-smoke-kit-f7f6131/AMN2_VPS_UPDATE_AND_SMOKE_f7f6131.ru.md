# AMN2 VPS Update And Smoke Kit f7f6131

Date: 2026-06-07.

Purpose: update existing `/opt/amn2` source overlay from `c92bd1a` to `amn2/codex-vps-test-prep` head `f7f6131 Update integration status for c92 manual prelaunch` and repeat the read-only/manual-runtime smoke gate.

This package does not switch the validation VPS to service mode. It only aligns source code so `/api/integration/status` and the web integration status page report the current accepted state: manual runtime passed, `systemd` not used, public `3030/3040` closed, and the next service-mode deployment deferred to a separate gate.

```text
package/source overlay commit: f7f6131 Update integration status for c92 manual prelaunch
previous source overlay: c92bd1a Bind web admin systemd to loopback
source zip sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
expected read-only routes after update: 6
web/admin runtime mode: manual
web/admin backend listener: 127.0.0.1:3030
api smoke listener: 127.0.0.1:3040
service deployment: deferred target server
```

## Boundaries

Allowed:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv`;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run API loopback smoke on `127.0.0.1:3040`;
- keep web/admin and bot in the current operator-started manual runtime mode.

Still blocked without a separate gate:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web-admin `3030` exposure;
- enabling `systemd` services or HTTPS reverse proxy on this validation VPS;
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
sha256sum -c amn2-vps-update-and-smoke-kit-f7f6131.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-f7f6131
mkdir -p amn2-vps-update-and-smoke-kit-f7f6131
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-f7f6131.zip amn2-vps-update-and-smoke-kit-f7f6131
cd amn2-vps-update-and-smoke-kit-f7f6131
sha256sum -c amn2-codex-vps-test-prep-f7f6131-source.zip.sha256.txt
```

Expected source SHA:

```text
720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
```

## 2. Apply Source Overlay

```bash
cd /root/amn2-vps-update-and-smoke-kit-f7f6131
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=f7f6131
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
checked_routes: 6
```

## 4. Optional Manual Status Check

If the API process is already running on loopback:

```bash
python -m app.cli api smoke-cycle \
  --db /opt/amn2/data/amneziya.sqlite3 \
  --base-url http://127.0.0.1:3040 \
  --server-name local \
  --name f7-status-align-smoke \
  --owner-label ops \
  --expires-at "$(date -u -d '+7 days' '+%Y-%m-%dT%H:%M:%S+00:00')" \
  --pretty
```

Expected safe result:

```text
status: passed
checked_routes: 6
route_status_codes: 200
forbidden_markers_count: 0
raw_token_display: hidden
revoke_status: revoked
```

## 5. Safe Evidence To Return

Return only safe summary fields:

```text
source overlay before:
source overlay after:
source_update_status:
api_smoke_status:
checked_routes:
listener_status:
audit_status:
integration_status_current_stable_head:
integration_status_decision:
manual_runtime_mode:
service_deployment:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

Do not return full logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, or backup contents.
