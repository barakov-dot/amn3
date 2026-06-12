# Phase 5 P5-C002 VPS retention decision

Date: 2026-06-12.

Status: `completed-amn3-docs-only`.

## Operator Decision

The operator clarified that the current target server is a disposable test VPS:

- it does not work properly enough to be treated as a stable production system;
- it has no important data that must be preserved;
- it was created for testing together with Codex and for project completion work;
- breaking the current server state is acceptable within an explicitly opened named gate.

## Retention Decision

`P5-C002` is closed with this retention posture:

```text
target_server_role: disposable_test_vps
project_critical_data_on_server: no
backup_or_snapshot_required_before_package_apply: no
backup_or_snapshot_required_before_wipe/reinstall: no, if the operator opens the matching destructive named gate
operator_accepts_current_server_state_loss: yes
secret_transfer_policy: operator local channel only
```

This replaces the previous default blocker that required provider snapshot/backup confirmation before any live rollout or destructive rebuild on this test VPS.

## Still Not Authorized By This Decision

This decision does not by itself authorize:

- live VPS commands;
- SSH commands;
- package apply/rebuild on the VPS;
- service restart/deploy;
- wipe/reinstall;
- public exposure;
- real config delivery;
- write API / `/api/clients` CRUD;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation.

Those actions still require a separate named gate with explicit scope, stop criteria and allowed command class.

## Safe Next Step

The next safe progression is `P5-C001` as a named package-rebuild gate from current AMN2 head `de25576`.

`P5-C001` can rebuild and verify a current package locally without touching the server. After that, a separate `P5-C003` live rollout gate can decide whether to apply/restart/smoke on the disposable test VPS.

## Safety Boundary

No live VPS command, SSH command, service restart, deploy, package apply/rebuild on VPS, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed while recording this decision.

## Verification

AMN3-only documentation update:

```text
git diff --check
result: passed
```

AMN2 state remained unchanged:

```text
branch: codex-vps-test-prep
head: de25576 Polish Russian-first microcopy
```

## Decision

`P5-C002` is closed as an AMN3 docs-only VPS retention decision for the current disposable test server.

Next recommendation: open `P5-C001` as a named local package-rebuild gate from AMN2 head `de25576`.
