# AMN2 VPS Update And Smoke Kit 34b3b43

Date: 2026-07-10.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `34b3b43 Add Telegram integration status`. Package preparation does not
authorize upload, source apply, service restart or Telegram bot activation.

```text
source_commit=34b3b43a87fb673cb966a578d3d5e48533b541fa
previous_vps_overlay=6f475e6
source_zip=amn2-codex-vps-test-prep-34b3b43-source.zip
source_zip_sha256=97D7676B9C349877A8A51C971599C0C886616E9BBB6472749C0C695209BE5179
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
android_tv_import_connect=pending_physical_device
telegram_bot_runtime=not_started
```

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false. No credential issue/rotate/revoke,
peer/config action, Android TV action, public exposure or live Telegram send is
authorized by this package.

## Future Source Overlay Gate

Only after a separate approval:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-34b3b43.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-34b3b43
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-34b3b43
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-34b3b43.zip /root/amn2-vps-update-and-smoke-kit-34b3b43
cd /root/amn2-vps-update-and-smoke-kit-34b3b43
sha256sum -c amn2-codex-vps-test-prep-34b3b43-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-34b3b43/amn2-codex-vps-test-prep-34b3b43-source.zip
export AMN2_EXPECTED_SOURCE_SHA=97D7676B9C349877A8A51C971599C0C886616E9BBB6472749C0C695209BE5179
export AMN2_EXPECTED_SOURCE_COMMIT=34b3b43
bash ./amn2_apply_source_zip.sh
```

Any bot runtime activation, live Telegram check or VPS source apply remains a
separate named gate. Return only safe summaries; never publish environment
files, tokens, authorization headers, token hashes, private keys, PSK, `.conf`,
QR or `vpn://` payloads.
