# AMN2 VPS Update And Smoke Kit ecf8563

Date: 2026-07-11.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `ecf8563 Add plan device quota admin UI`. Package preparation does not
authorize upload, source apply, service restart, quota mutation or Telegram bot
polling.

```text
source_commit=ecf85632216724ff22da48314321d01339f416e9
previous_vps_overlay=1c7fb78
source_zip=amn2-codex-vps-test-prep-ecf8563-source.zip
source_zip_sha256=15AA131EAA1B3B878ADB6D0FB04ED8DF3114D08641966EFC018D6E528D6CE990
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
plan_quota_ui=/plans
plan_quota_write_policy=web.plans.device_quota_update
plan_quota_rows_on_current_vps=0
assignment_policy=dedicated_device_default|owner_shared_admin_only
telegram_bot_runtime=inactive_disabled_not_started
controlled_telegram_smoke=not_authorized_by_package
offline_editable_install=fail_closed_exact_diagnostic_fallback
```

## Boundaries

The source overlay preserves `.env`, `servers.yml`, `data` and `venv`. Both
product-write flags must remain false. No credential issue/rotate/revoke,
plan quota update, peer/config generation or delivery, public exposure,
Telegram API request or live Telegram send/polling is authorized by this
package.

The candidate adds an authenticated `/plans` view and an audited CSRF-protected
plan quota write route. A future live smoke may read the page and verify route
protection. It must not submit a quota change unless a separate exact gate
explicitly authorizes a named plan and value.

The apply tool forces pip into no-index mode. If the VPS venv returns the two
exact previously observed missing-`setuptools>=69` build-isolation diagnostics,
the tool accepts the existing source path only after imports resolve directly
to `/opt/amn2/app/__init__.py`. Any other pip failure or source-path mismatch is
fatal.

## Future Source Overlay Gate

Only after a separate approval:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-ecf8563.zip.sha256.txt
test ! -e /root/amn2-vps-update-and-smoke-kit-ecf8563
mkdir -m 700 /root/amn2-vps-update-and-smoke-kit-ecf8563
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-ecf8563.zip /root/amn2-vps-update-and-smoke-kit-ecf8563
cd /root/amn2-vps-update-and-smoke-kit-ecf8563
sha256sum -c amn2-codex-vps-test-prep-ecf8563-source.zip.sha256.txt
export VPS_APPLY_ENABLED=false
export OPERATOR_DEVICE_CREATE_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-ecf8563/amn2-codex-vps-test-prep-ecf8563-source.zip
export AMN2_EXPECTED_SOURCE_SHA=15AA131EAA1B3B878ADB6D0FB04ED8DF3114D08641966EFC018D6E528D6CE990
export AMN2_EXPECTED_SOURCE_COMMIT=ecf8563
bash ./amn2_apply_source_zip.sh
```

Any upload, source apply, web restart, live quota write or Telegram runtime
action remains a separate named gate. Return only safe summaries; never publish
environment files, tokens, authorization headers, token hashes, administrator
IDs, private keys, PSK, `.conf`, QR or `vpn://` payloads.
