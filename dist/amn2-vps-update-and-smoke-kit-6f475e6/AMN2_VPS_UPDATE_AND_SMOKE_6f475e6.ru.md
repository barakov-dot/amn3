# AMN2 VPS Update And Smoke Kit 6f475e6

Date: 2026-07-10.

Purpose: private source-overlay package for `amn2/codex-vps-test-prep`
commit `6f475e6 Add integration credential registry`. The approved live scope is
limited to checksum verification, source overlay, read-only loopback smoke and
private loopback web activation. It does not authorize credential issuance,
peer/config actions or public exposure.

```text
source_commit=6f475e6ef3c3610be9de971ef7f18c5e9d6d19ee
previous_vps_overlay=3ed20ab
source_zip=amn2-codex-vps-test-prep-6f475e6-source.zip
source_zip_sha256=BEDFDBE04CA40DA21A51B1ACAB4C0C21BD7F5EC408A77D1223664EAAAF673FFF
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
android_tv_import_connect=pending_physical_device
```

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false. The web service stays bound to
`127.0.0.1:3030`.

Still blocked:

- API token issuance, rotation or revoke during deployment;
- peer/user creation, revoke or config generation/delivery;
- `VPS_APPLY_ENABLED=true` or `OPERATOR_DEVICE_CREATE_ENABLED=true`;
- Android TV import/connect and device `8` acceptance;
- public API/web exposure, firewall, reverse proxy or TLS changes;
- backup/import/reboot, live Telegram actions or secret publication.

## Source Overlay

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-6f475e6.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-6f475e6
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-6f475e6
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-6f475e6.zip /root/amn2-vps-update-and-smoke-kit-6f475e6
cd /root/amn2-vps-update-and-smoke-kit-6f475e6
sha256sum -c amn2-codex-vps-test-prep-6f475e6-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-6f475e6/amn2-codex-vps-test-prep-6f475e6-source.zip
export AMN2_EXPECTED_SOURCE_SHA=BEDFDBE04CA40DA21A51B1ACAB4C0C21BD7F5EC408A77D1223664EAAAF673FFF
export AMN2_EXPECTED_SOURCE_COMMIT=6f475e6
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

## Read-Only Smoke

```bash
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
export AMN2_EXPECTED_COMMIT=6f475e6
bash ./amn2_api_loopback_smoke.sh
```

Return only safe summary fields. Do not return full logs, environment files,
tokens, authorization headers, token hashes, private keys, PSK, `.conf`, QR or
`vpn://`.
