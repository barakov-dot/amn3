# Phase 10 Telegram admin server status route

Date: 2026-07-10.

Status: `completed-code-tested-pushed-local-only`.

## Product Result

```text
amn2_base=1c7b5b2
amn2_commit=4cf93f8
branch=codex-vps-test-prep
push=completed
callback=ADMIN_SERVERS_CALLBACK
dispatcher_route=registered
authorization=telegram_admin_and_workflow_is_admin
data_source=list_api_server_summaries
typed_allowlist=operator_server_status_view
stored_fields=name|status|runtime|device_counts|health_status|latency|checked_at|ssh_awg_udp_probe_results
excluded_fields=host|ssh_port|endpoint|server_public_key|health_error
audit_action=bot_admin_servers_read
audit_metadata=server_count_and_local_source_only
surface_policy=bot.admin.servers
```

The Telegram admin menu now exposes `Servers`. The route returns typed local
server summaries and the latest already stored health state in the operator
locale. Missing health data is shown as unknown.

The typed service explicitly copies only the API-safe fields. Tests inject
`endpoint_host` and `server_public_key` into a source row and prove that neither
field exists on the Telegram view. The workflow audit contains only the server
count and a fixed local-source marker.

## Verification

```text
RED=missing_operator_server_status_service|missing_handler|missing_callback
focused_initial=130_passed_4_navigation_expectations_failed
focused_final=135_passed
expanded=217_passed_1_warning
full=790_passed_1_skipped_1_warning
diff_check=passed
cached_diff_check=passed
progress_harness_tests=12_passed
progress_harness_scope=product_and_docs_passed
```

The four intermediate failures were exact admin-navigation expectations that
did not yet include the new `Servers` row. The skip is the existing POSIX-only
permission assertion on Windows. The warning is the existing FastAPI/Starlette
TestClient deprecation warning.

## Boundary

This slice performed no live health check, SSH command, VPS polling, Telegram
bot startup, live Telegram send, package build/upload, source overlay, service
restart, peer/config action, Android TV action or public exposure. The private
VPS remains on source overlay `6f475e6`; later Telegram commits through
`4cf93f8` are pushed to Git only and are not deployed.

Android TV device `8` remains pending physical import/connect, handshake and
traffic verification. That pending config/device work does not block this
local-only product lane.

## Upstream Product Signals

The route independently applies PRVTPRO's admin-bot/multi-instance product
signals and KYORESUAS's typed API taxonomy. No upstream GPL code, templates,
styles or credentials were copied.

## Next Product Slice

```text
START_PHASE10_TELEGRAM_ADMIN_INTEGRATION_CREDENTIAL_STATUS_ROUTE_SLICE
```

Expose the existing hash-free integration credential registry as an
authorized, read-only Telegram lifecycle view. Keep issue/rotate/revoke, raw
tokens, token hashes and live bot activation outside that slice.
