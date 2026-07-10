# Phase 10 Telegram admin traffic route completion

Date: 2026-07-10.

Status: `completed-code-tested-pushed-local-only`.

## Product Result

```text
amn2_base=e73343b
amn2_commit=1c7b5b2
branch=codex-vps-test-prep
push=completed
callback=ADMIN_TRAFFIC_CALLBACK
dispatcher_route=registered
authorization=telegram_admin_and_workflow_is_admin
data_source=local_active_device_traffic_snapshots
locale=operator_locale
audit_action=bot_admin_traffic_read
audit_metadata=device_count_and_local_source_only
surface_policy=bot.admin.traffic
```

The existing `Traffic` admin button now reaches a concrete callback handler.
The handler acknowledges the callback first, checks Telegram administrator
authorization before reading data, renders the existing active-device traffic
views in the operator locale and returns the admin navigation keyboard.

The workflow reads only locally stored traffic snapshots. It does not run a
collector, open SSH or poll the VPS. The audit event contains only the number
of displayed devices and the fixed local-source marker; it does not contain
device names, user identity, traffic values or config material.

## Verification

```text
RED=import_error_handle_admin_traffic
focused_initial=128_passed
locale_contract_initial=128_passed_1_expectation_failed
focused_final=129_passed
expanded=228_passed
full=784_passed_1_skipped_1_warning
diff_check=passed
cached_diff_check=passed
progress_harness_tests=12_passed
progress_harness_scope=product_and_docs_passed
```

The skip is the existing POSIX-only permission assertion on Windows. The
warning is the existing FastAPI/Starlette TestClient deprecation warning. The
temporary locale failure corrected the test expectation to the existing
English product copy `No active devices yet.`; no production defect remained.

## Boundary

This slice performed no Telegram bot startup, live Telegram send, VPS/SSH
command, traffic collection, package build/upload, source overlay, service
restart, peer/config action, Android TV action or public exposure. The private
VPS remains on source overlay `6f475e6`; AMN2 commits `e73343b` and `1c7b5b2`
are pushed to Git but are not deployed.

Android TV device `8` remains pending physical import/connect, handshake and
traffic verification.

## Upstream Product Signals

PRVTPRO's admin-bot and multi-instance direction and KYORESUAS's typed API
taxonomy remain independent product inputs only. No upstream GPL code,
templates, styles or credentials were copied.

## Next Product Slice

```text
START_PHASE10_TELEGRAM_ADMIN_SERVER_STATUS_ROUTE_SLICE
```

Expose the existing secret-safe local server summaries and latest stored
health state to authorized Telegram administrators. Keep the route local-only,
audited and free of SSH, live polling and secret-bearing fields.
