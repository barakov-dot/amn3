# Phase 11 review: 3c91601 private Telegram single-admin transient smoke gate

Date: 2026-07-14.

Trigger:

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```

## Decision

```text
production_overlay_3c91601_live_smoke=STOP
local_hardening_801f8c3=PASSED-PUSHED
live_polling_performed=false
persistent_bot_activation=false
```

Review of the production-overlay implementation found one backlog-preservation
race. The runner requested only message updates, then acknowledged the accepted
administrator `/start` with `offset=update_id+1`. A callback or other filtered
update arriving after the initial zero-backlog preflight but before the selected
message could have a lower update ID. The offset acknowledgement could then
discard that unseen update, while the post-ack zero-backlog check would no
longer detect it.

The finding blocks a live approval phrase for overlay `3c91601`. No Telegram
API call, polling, VPS/SSH action, service change, database write or public
exposure occurred during this review.

## Source hardening

AMN2 commit `801f8c3` adds a fail-closed pre-ack guard:

1. The existing preflight still requires the configured bot identity, no
   webhook and zero pending updates.
2. The runner still accepts only exact `/start` from one selected ID already
   present in `ADMIN_TELEGRAM_IDS`.
3. It still calls `handle_start` directly against a private SQLite clone and
   never creates the full dispatcher or callback routes.
4. After the response succeeds but before any offset acknowledgement, it
   requires the webhook to remain absent and the pending count to be exactly
   one: the accepted, not-yet-acknowledged `/start`.
5. Any additional pending update stops the run without an offset call, so the
   backlog remains available to a later regular bot runtime.
6. Only then does it acknowledge the accepted update and require the final
   pending count to be zero.

The internal deadline remains at most 120 seconds. Both write gates must remain
false. The production SQLite logical digest is still checked before and after;
the supported workflow receives only the clone path. Output remains limited to
redacted identity/status/count booleans.

## Watchdog and rollback boundary

The future live gate must retain the established transient service contract:

```text
RuntimeMaxSec=180
Restart=no
TimeoutStopSec=15
KillMode=control-group
regular_bot_unit=inactive_disabled_before_and_after
```

The transient unit must be stopped and absent before its private mode `0700`
run directory and mode `0600` clone are removed. Production DB digest/counts,
web loopback health, private listeners, write gates and regular bot state must
be verified before and after. AWG must not be stopped or restarted.

## Verification

```text
focused_controlled_smoke_and_bootstrap=21_passed
bot_and_settings_regression=184_passed
python_compile=passed
git_diff_check=passed
semantic_security_review=passed
source_branch=codex-vps-test-prep
source_commit=801f8c3
source_push=completed
```

The added regression models an extra pending update before acknowledgement and
proves that no offset acknowledgement is sent in that state.

The first harness invocation used `--require-product-step` with the mandatory
risk-review command and correctly rejected it as not being a product slice;
the focused tests still ran and passed. The Phase 11 review command is a named
risk gate, so final harness verification uses the command without the
product-diff requirement.

## Runtime and automation

The last verified production baseline remains overlay `3c91601`, web active on
loopback, AWG running with restart count zero and 12 peers, and the regular bot
inactive/disabled. This task did not refresh that baseline through SSH because
the Phase 11 live stop-line remains false.

`amn2-upstream-orchestrator` was retargeted from the legacy automation task to
the current Phase 11 task while preserving its ACTIVE read-only prompt and
weekly schedule. The PRVTPRO, KYORESUAS and Amnezia legacy heartbeat chain
remains PAUSED.

## Next command

The hardened source must be packaged and reviewed for a separate exact private
overlay gate before a live transient smoke phrase can be issued:

```text
GPT-5.6 SOL -> PREPARE_PHASE11_801F8C3_PRIVATE_TELEGRAM_SMOKE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

That future overlay gate must not repeat the Phase 10 schema rollout or client
acceptance. It is limited to the two-file source delta, checksum/snapshot/
rollback preparation, regular-bot-disabled proof and AWG continuity. The live
Telegram transient smoke remains a later, separately approved action after the
production overlay contains `801f8c3`.
