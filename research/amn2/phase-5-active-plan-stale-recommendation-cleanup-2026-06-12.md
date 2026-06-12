# Phase 5 P5-S002 active-plan stale recommendation cleanup

Date: 2026-06-12.

Status: `completed-amn3-docs-only`.

## Summary

`P5-S002` was completed as an AMN3 docs-only housekeeping slice after `P5-X002` and `P5-X001`.

The cleanup removes the stale active recommendation to start `P5-S002`, records `P5-S002` as closed, and keeps the active Phase 5 plan honest:

- critical work remains gated and is not started by default;
- normal work remains conditional on pilot completion, upstream watcher output, or a separate design boundary;
- simple and cosmetic groups now have no active default tasks.

## Scope

Changed AMN3 coordination/evidence files only:

- `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md`
- `docs/PHASE_5_6_FORWARD_PLAN.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `ideas/candidates-for-amn2.md`
- `research/amn2/transfer-backlog.md`
- `research/amn2/phase-5-russian-first-microtexts-2026-06-11.md`

No AMN2 runtime, tests, templates, bot delivery code, web panel code, database or package artifact was changed.

## Safety Boundary

No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed.

## Verification

Stale recommendation scan before cleanup found the expected active references:

```text
P5-S002 in active simple plan
P5-S002 as next recommendation after P5-X001
```

Verification after cleanup:

```text
rg stale-current-head/recommendation patterns
result: no matches

git diff --check
result: passed
```

AMN2 state was checked and remained unchanged:

```text
branch: codex-vps-test-prep
head: de25576 Polish Russian-first microcopy
working tree: clean
remote: amn2/codex-vps-test-prep at de25576
```

## Decision

`P5-S002` is closed as an AMN3 docs-only active-plan cleanup checkpoint.

Next recommendation: no automatic default local-only continuation remains. The operator should explicitly choose one of the remaining conditional paths:

- open `P5-C001` only as a named package-rebuild gate from current AMN2 head `de25576`;
- run/finish the operator-only pilot first, then close `P5-N001`;
- wait for the next upstream watcher output, then consider `P5-N003`;
- open a separate design boundary before `P4-PRVTPRO-REFRESH-003`.
