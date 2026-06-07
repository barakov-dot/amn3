# AMN2 VPS Update And Smoke Kit c92bd1a

Date: 2026-06-07.

Purpose: update existing `/opt/amn2` source overlay from `42ffa65` to `amn2/codex-vps-test-prep` head `c92bd1a Bind web admin systemd to loopback` and repeat the read-only smoke gate. This package is a safety follow-up for the controlled production launch: web/admin systemd now binds backend service to `127.0.0.1:3030` by default for the approved HTTPS reverse proxy mode.

Important distinction:

```text
package/source overlay commit: c92bd1a Bind web admin systemd to loopback
previous source overlay: 42ffa65 Record git checkout smoke status
previous source-overlay smoke: 20260607T165625Z, pass
expected read-only routes after update: 6
web/admin backend listener: 127.0.0.1:3030
api smoke listener: 127.0.0.1:3040
```

## Boundaries

Allowed:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv`;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run API loopback smoke on `127.0.0.1:3040`;
- enable/check web-admin only through loopback backend plus approved HTTPS reverse proxy.

Still blocked without a separate gate:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web-admin `3030` exposure;
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
sha256sum -c amn2-vps-update-and-smoke-kit-c92bd1a.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-c92bd1a
mkdir -p amn2-vps-update-and-smoke-kit-c92bd1a
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-c92bd1a.zip amn2-vps-update-and-smoke-kit-c92bd1a
cd amn2-vps-update-and-smoke-kit-c92bd1a
sha256sum -c amn2-codex-vps-test-prep-c92bd1a-source.zip.sha256.txt
```

Expected source SHA:

```text
272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
```

## 2. Apply Source Overlay

```bash
cd /root/amn2-vps-update-and-smoke-kit-c92bd1a
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=c92bd1a
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

## 4. Controlled Production Launch Check

After the source overlay smoke passes, proceed with the production launch gate but keep web-admin backend on loopback:

```bash
cd /opt/amn2
grep -F 'web serve --host 127.0.0.1 --port 3030' deploy/systemd/amneziya-web.service.example
```

If any installed unit still contains `--host 0.0.0.0`, stop and replace it with `--host 127.0.0.1` before enabling/restarting:

```bash
sudo systemctl cat amneziya-web 2>/dev/null || true
```

Expected listener shape after web service starts:

```text
web backend: 127.0.0.1:3030
api smoke: 127.0.0.1:3040 only during smoke
public API 3040: no
direct public 3030: no
HTTPS reverse proxy: yes
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
web_unit_loopback_template:
web_listener:
api_3040_public:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

Do not return full logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, or backup contents.
