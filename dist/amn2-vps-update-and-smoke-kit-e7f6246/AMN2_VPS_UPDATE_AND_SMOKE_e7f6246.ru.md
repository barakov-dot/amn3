# AMN2 VPS Update And Smoke Kit e7f6246

Date: 2026-07-10.

Purpose: local-only package preparation for `amn2/codex-vps-test-prep`
commit `e7f6246 Harden operator single device creation`. This kit is an input
for a future separately approved read-only source-overlay upload/smoke gate. It
does not authorize VPS access, upload or apply by itself.

```text
source_commit=e7f62461af69ceaef175093242349f4aa3496239
source_commit_short=e7f6246
current_live_vps_overlay=4326cae
source_zip=amn2-codex-vps-test-prep-e7f6246-source.zip
source_zip_sha256=FE980BDBC209ED339B33231BCABD42000E2DA6910791DAA8ABA85620A099B0EE
expected_read_only_routes=6
web_admin_listener=127.0.0.1:3030
api_smoke_listener=127.0.0.1:3040
service_deployment=unchanged
android_tv_import_connect=pending_physical_device
```

## Boundaries

Allowed only after a separate exact VPS source-overlay gate:

- verify both package and source checksums;
- preserve `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data` and
  `/opt/amn2/venv`;
- apply only the tracked source archive in this kit;
- keep `VPS_APPLY_ENABLED=false`;
- run the API smoke on loopback `127.0.0.1:3040`;
- retain operator-only web/admin access through the already approved private
  path.

Still blocked without separate exact gates:

- `VPS_APPLY_ENABLED=true`;
- peer creation/revoke or config generation/delivery;
- Android TV import/connect and device `8` acceptance;
- public API or direct public web/admin exposure;
- service enable/restart, reverse-proxy or firewall changes;
- broad write API, self-service config delivery, backup/import/reboot;
- Telegram token use, bot send or identity mutation;
- publication of `.env`, `servers.yml`, raw tokens, authorization headers,
  token hashes, private keys, PSK, `.conf`, QR, `vpn://` or full logs.

## 1. Unpack Kit

Future exact-gate commands:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-e7f6246.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-e7f6246
mkdir -p amn2-vps-update-and-smoke-kit-e7f6246
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-e7f6246.zip amn2-vps-update-and-smoke-kit-e7f6246
cd amn2-vps-update-and-smoke-kit-e7f6246
sha256sum -c amn2-codex-vps-test-prep-e7f6246-source.zip.sha256.txt
```

## 2. Apply Source Overlay

Future exact-gate commands:

```bash
cd /root/amn2-vps-update-and-smoke-kit-e7f6246
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-e7f6246/amn2-codex-vps-test-prep-e7f6246-source.zip
export AMN2_EXPECTED_SOURCE_SHA=FE980BDBC209ED339B33231BCABD42000E2DA6910791DAA8ABA85620A099B0EE
export AMN2_EXPECTED_SOURCE_COMMIT=e7f6246
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected result:

```text
source_update_status=passed
source_commit=e7f6246
next=run ./amn2_api_loopback_smoke.sh from /opt/amn2
```

## 3. Run Read-Only API Smoke

Future exact-gate commands:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
export AMN2_EXPECTED_COMMIT=e7f6246
bash ./amn2_api_loopback_smoke.sh
```

Expected safe summary:

```text
VPS verdict: pass
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

## 4. Safe Evidence

Return only source overlay before/after, source update status, API smoke status,
checked route count, listener/audit status, `VPS_APPLY_ENABLED` and the safe
evidence directory. Do not return secret-bearing source or full logs.
