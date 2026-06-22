# Phase 8 private/operator RC ready hold

Date: 2026-06-22.

Status: `active-private-operator-rc-ready-hold-docs-only`.

Scope: AMN2 held at private/operator RC
`launch-ready-with-explicit-limitations` using existing Phase 8 evidence only.
No live VPS/SSH command, destructive action, package upload/apply, service
restart, public exposure, config delivery, Telegram live send, bot polling,
Telegram profile/media mutation, backup restore/import/reboot, provider
mutation, production peer/user mutation or secret-bearing output was performed.

## Produced Artifact

```text
docs/AMN2_PRIVATE_OPERATOR_RC_READY_HOLD.ru.md
```

## Held Status

```text
ready_hold_status=active-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

## Heads at Hold Start

```text
amn3_evidence_head_before_ready_hold=92ddaca Record private operator RC closeout
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

## Hold Rules

```text
live_vps_ssh_allowed=false
destructive_action_allowed=false
package_apply_allowed=false
service_restart_allowed=false
public_exposure_allowed=false
config_delivery_allowed=false
telegram_live_send_allowed=false
bot_polling_allowed=false
restore_import_allowed=false
provider_rebuild_allowed=false
production_rollout_allowed=false
secret_payload_output_allowed=false
```

## Exit Conditions

Hold may be exited only by a fresh exact named gate, such as:

```text
PRIVATE-RC-OPERATOR-RUN-GATE
CONFIG-DELIVERY-GATE
TELEGRAM-LIVE-DELIVERY-GATE
PUBLIC-EXPOSURE-GATE
RESTORE-IMPORT-DR-GATE
PROVIDER-REBUILD-GATE
PRODUCTION-ROLLOUT-GATE
FRESH-ANDROID-PHONE-POST-RC-RECHECK-GATE
```

## Recommended Next State

```text
current_recommendation=hold
next_action=wait_for_explicit_exact_named_gate
```
