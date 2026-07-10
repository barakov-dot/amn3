# AMN2 VPS Update And Smoke Kit 3ed20ab

Date: 2026-07-10.

Purpose: local-only package preparation for `amn2/codex-vps-test-prep`
commit `3ed20ab Assert operator route security policy`, containing product commit
`466e0bc Add operator device web workflow`. This kit does not authorize VPS
access, upload, source overlay, service restart or product apply by itself.

```text
source_commit=3ed20abfaa24d7ad2d3b72ff0c0a92dd10b823ab
product_commit=466e0bc
previous_vps_overlay=e7f6246
source_zip=amn2-codex-vps-test-prep-3ed20ab-source.zip
source_zip_sha256=F2F6AC74FD9311E72B9098DD2472841DFB8CAE804D5901A3DDD0F38CB3DE1066
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
android_tv_import_connect=pending_physical_device
```

## Boundaries

A future exact source-overlay gate may verify checksums, preserve `.env`,
`servers.yml`, `data` and `venv`, apply tracked source, keep both product-write
flags false and run loopback smoke. Web service restart/activation is a separate
gate because it changes the running process.

Still blocked:

- peer/user creation, revoke or config generation/delivery;
- `VPS_APPLY_ENABLED=true` or `OPERATOR_DEVICE_CREATE_ENABLED=true`;
- Android TV import/connect and device `8` acceptance;
- public API/web exposure, firewall, reverse proxy or TLS changes;
- backup/import/reboot, Telegram actions or secret publication.

## Future Source Overlay

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-3ed20ab.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-3ed20ab
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-3ed20ab
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-3ed20ab.zip /root/amn2-vps-update-and-smoke-kit-3ed20ab
cd /root/amn2-vps-update-and-smoke-kit-3ed20ab
sha256sum -c amn2-codex-vps-test-prep-3ed20ab-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-3ed20ab/amn2-codex-vps-test-prep-3ed20ab-source.zip
export AMN2_EXPECTED_SOURCE_SHA=F2F6AC74FD9311E72B9098DD2472841DFB8CAE804D5901A3DDD0F38CB3DE1066
export AMN2_EXPECTED_SOURCE_COMMIT=3ed20ab
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

## Future Read-Only Smoke

```bash
cd /opt/amn2
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
export AMN2_EXPECTED_COMMIT=3ed20ab
bash ./amn2_api_loopback_smoke.sh
```

Return only safe summary fields. Do not return full logs, environment files,
tokens, authorization headers, private keys, PSK, `.conf`, QR or `vpn://`.
