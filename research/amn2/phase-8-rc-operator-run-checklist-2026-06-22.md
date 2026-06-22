# Phase 8 private/operator RC run checklist

Date: 2026-06-22.

Status: `completed-private-operator-rc-run-checklist-docs-only`.

Scope: operator run checklist prepared from existing Phase 8 evidence only. No
live VPS/SSH command, destructive action, package upload/apply, service restart,
public exposure, config delivery, Telegram live send, bot polling, Telegram
profile/media mutation, backup restore/import/reboot, provider mutation,
production peer/user mutation or secret-bearing output was performed.

## Produced Artifact

```text
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
```

## Checklist Covers

- what to check before operating;
- what is allowed in private/operator RC;
- what is forbidden without a new exact named gate;
- where private handoff artifacts live;
- how to keep public exposure closed;
- Telegram boundaries;
- config delivery boundaries;
- backup/restore boundaries;
- pre-session and post-session operator checks;
- exact future gates for broader action.

## Status Carried Forward

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
operator_run_checklist_status=completed-docs-only
```

## Private Handoff Location

The checklist records the private handoff root without exposing payloads:

```text
C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
```

This path is outside the AMN3 workspace/evidence repository and must remain
outside evidence commits.

## Future Gates Recorded

```text
PUBLIC-EXPOSURE-GATE
TELEGRAM-LIVE-DELIVERY-GATE
CONFIG-DELIVERY-GATE
RESTORE-IMPORT-DR-GATE
PRODUCTION-ROLLOUT-GATE
PROVIDER-REBUILD-GATE
```

## Next Recommended Step

```text
P8-RC-FINAL-PACKAGE
```

Prepare a final private/operator RC package index from existing evidence:
handoff document, run checklist, evidence list, limitations and future exact
gates.
