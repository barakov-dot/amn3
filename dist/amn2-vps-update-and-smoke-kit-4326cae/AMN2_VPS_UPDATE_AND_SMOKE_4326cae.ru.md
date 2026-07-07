# AMN2 VPS Update And Smoke Kit 4326cae

Date: 2026-07-07.

Purpose: local-only package-prep for `amn2/codex-vps-test-prep` head
`4326cae Save fresh installer recovery work`. This kit is prepared for a future
read-only source-overlay upload/smoke gate. It is not a live VPS approval by
itself.

```text
package/source overlay commit: 4326cae Save fresh installer recovery work
previous documented VPS-smoked source overlay: f7f6131 Update integration status for c92 manual prelaunch
source zip: amn2-codex-vps-test-prep-4326cae-source.zip
source zip sha256: 7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
expected read-only routes after update: 6
web/admin backend listener: 127.0.0.1:3030
api smoke listener: 127.0.0.1:3040
service deployment: unchanged
```

## Boundaries

Allowed only after a separate exact VPS source-overlay gate:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv`;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run API loopback smoke on `127.0.0.1:3040`;
- keep web/admin access loopback-only or via an already approved private operator path.

Still blocked without separate gates:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web-admin `3030` exposure;
- enabling or changing systemd services, HTTPS reverse proxy, or firewall exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw token, Authorization header, token hash,
  private keys, PSK, `.conf`, QR, `vpn://`, or full logs.

## 1. Unpack Kit

Future VPS gate command block:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-4326cae.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-4326cae
mkdir -p amn2-vps-update-and-smoke-kit-4326cae
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-4326cae.zip amn2-vps-update-and-smoke-kit-4326cae
cd amn2-vps-update-and-smoke-kit-4326cae
sha256sum -c amn2-codex-vps-test-prep-4326cae-source.zip.sha256.txt
```

Expected source SHA:

```text
7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
```

## 2. Apply Source Overlay

Future VPS gate command block:

```bash
cd /root/amn2-vps-update-and-smoke-kit-4326cae
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-4326cae/amn2-codex-vps-test-prep-4326cae-source.zip
export AMN2_EXPECTED_SOURCE_SHA=7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
export AMN2_EXPECTED_SOURCE_COMMIT=4326cae
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=4326cae
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Run API Loopback Smoke

Future VPS gate command block:

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

Expected safe summary:

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

## 4. Safe Evidence To Return

Return only:

```text
source overlay before:
source overlay after:
source_update_status:
api_smoke_status:
checked_routes:
listener_status:
audit_status:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

Do not return full logs, `.env`, `servers.yml`, raw tokens, Authorization
headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, or backup
contents.
