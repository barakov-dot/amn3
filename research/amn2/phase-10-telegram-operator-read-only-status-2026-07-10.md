# Phase 10 Telegram operator read-only status

Date: 2026-07-10.

Status: `completed-code-tested-pushed-local-only`.

## Product Result

```text
amn2_base=6f475e6
amn2_commit=e73343b
branch=codex-vps-test-prep
push=completed
operator_status=authorized_aggregate_local_database_view
locale=russian_or_english_admin_locale
audit_action=bot_operator_status_read
vps_write_state=actual_runtime_gate
public_config_delivery=false
public_exposure=false
```

The Telegram admin menu now exposes `Status`. The workflow reports aggregate
counts for users, servers, devices, pending orders and integration credential
lifecycle state. It does not expose names, identifiers, addresses, raw tokens,
token hashes or config material.

The status path is bound to the Telegram admin policy, checks authorization
before reading the summary and records safe audit metadata. Its repository
query is local and aggregate-only; it performs no SSH command and no live VPS
polling.

## Verification

```text
RED=missing_operator_status_service_and_bot_route_imports
scoped=116_passed
expanded=197_passed
full=780_passed_1_skipped_1_warning
diff_check=passed
cached_diff_check=passed
progress_harness_tests=12_passed
post_commit_amn3_product_diff_guard=expected_fail_docs_only_after_amn2_e73343b
```

The skip is the existing POSIX-only permission assertion on Windows. The
warning is the existing FastAPI/Starlette TestClient deprecation warning.
The harness guard intentionally rejected the later AMN3-only evidence sync;
the product diff had already been reviewed, committed and pushed in the
separate AMN2 repository.

## Boundary

This slice performed no Telegram bot startup, live Telegram send, VPS/SSH
command, package build/upload, source overlay, service restart, peer/config
action, Android TV action or public exposure. The private VPS remains on the
previously smoked `6f475e6` source overlay; `e73343b` is pushed to Git only.

Android TV device `8` remains pending physical import/connect, handshake and
traffic verification.

## Next Product Slice

```text
START_PHASE10_TELEGRAM_ADMIN_TRAFFIC_ROUTE_COMPLETION_SLICE
```

Complete the existing `admin:traffic` button path with an authorized,
read-only handler and scoped tests. The callback is currently rendered by the
admin keyboard but has no registered route. Keep the implementation local,
secret-safe and free of VPS/Telegram live actions.
