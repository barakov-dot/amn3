# AMN2 VPS Update And Smoke Kit 1c7fb78

Date: 2026-07-11.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `1c7fb78 Add config assignment policies`. Package preparation does
not authorize upload, source apply, service restart or Telegram bot polling.

```text
source_commit=1c7fb789b1e4de09811f03e008cfad1fe6a7392c
previous_vps_overlay=34b3b43
source_zip=amn2-codex-vps-test-prep-1c7fb78-source.zip
source_zip_sha256=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
android_tv_import_connect=passed_standard_conf_android_tv_ios_windows
assignment_policy=dedicated_device_default|owner_shared_admin_only
production_db_schema_migration=requires_separate_live_gate
device8_assignment_reconciliation=requires_separate_live_gate
telegram_bot_runtime=inactive_disabled_not_started
controlled_telegram_smoke=not_authorized_by_package
```

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false. No credential issue/rotate/revoke,
peer/config generation or delivery, production DB migration/reconciliation,
public exposure, Telegram API request or live Telegram send/polling is
authorized by this package.

The source contains the controlled single-admin `/start` smoke runner, but its
execution still requires a separate named runtime gate after source activation.
The regular bot unit must remain inactive and disabled.

## Future Source Overlay Gate

Only after a separate approval:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-1c7fb78.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-1c7fb78
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-1c7fb78
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-1c7fb78.zip /root/amn2-vps-update-and-smoke-kit-1c7fb78
cd /root/amn2-vps-update-and-smoke-kit-1c7fb78
sha256sum -c amn2-codex-vps-test-prep-1c7fb78-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-1c7fb78/amn2-codex-vps-test-prep-1c7fb78-source.zip
export AMN2_EXPECTED_SOURCE_SHA=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
export AMN2_EXPECTED_SOURCE_COMMIT=1c7fb78
bash ./amn2_apply_source_zip.sh
```

Any source apply, web restart or Telegram runtime action remains a separate
named gate. Return only safe summaries; never publish environment files,
tokens, authorization headers, token hashes, administrator IDs, private keys,
PSK, `.conf`, QR or `vpn://` payloads.
