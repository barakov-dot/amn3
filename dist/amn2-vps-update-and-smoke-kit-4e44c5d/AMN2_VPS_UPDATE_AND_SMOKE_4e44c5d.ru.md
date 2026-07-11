# AMN2 VPS Update And Smoke Kit 4e44c5d

Date: 2026-07-11.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `4e44c5d Add controlled Telegram start smoke`. Package preparation does
not authorize upload, source apply, service restart or Telegram bot polling.

```text
source_commit=4e44c5d36f64d01f2d1afae5c6fd72e37c3dc22d
previous_vps_overlay=34b3b43
source_zip=amn2-codex-vps-test-prep-4e44c5d-source.zip
source_zip_sha256=4E34EB736775749467BDD5E0DA20758F46B8F10224871091C96778E960A040FA
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
android_tv_import_connect=pending_physical_device
telegram_bot_runtime=inactive_disabled_not_started
controlled_telegram_smoke=not_authorized_by_package
```

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false. No credential issue/rotate/revoke,
peer/config action, Android TV action, public exposure, Telegram API request or
live Telegram send/polling is authorized by this package.

The source contains the controlled single-admin `/start` smoke runner, but its
execution still requires a separate named runtime gate after source activation.
The regular bot unit must remain inactive and disabled.

## Future Source Overlay Gate

Only after a separate approval:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-4e44c5d.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-4e44c5d
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-4e44c5d
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-4e44c5d.zip /root/amn2-vps-update-and-smoke-kit-4e44c5d
cd /root/amn2-vps-update-and-smoke-kit-4e44c5d
sha256sum -c amn2-codex-vps-test-prep-4e44c5d-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-4e44c5d/amn2-codex-vps-test-prep-4e44c5d-source.zip
export AMN2_EXPECTED_SOURCE_SHA=4E34EB736775749467BDD5E0DA20758F46B8F10224871091C96778E960A040FA
export AMN2_EXPECTED_SOURCE_COMMIT=4e44c5d
bash ./amn2_apply_source_zip.sh
```

Any source apply, web restart or Telegram runtime action remains a separate
named gate. Return only safe summaries; never publish environment files,
tokens, authorization headers, token hashes, administrator IDs, private keys,
PSK, `.conf`, QR or `vpn://` payloads.
