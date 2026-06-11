# VPS-FRESH-DEPLOY-002: clean Ubuntu runbook 2026-06-11

Дата: 2026-06-11.

Назначение: закрыть следующий docs-only preparation slice после `VPS-FRESH-DEPLOY-001`: оформить простой fresh deploy runbook для будущего чистого Ubuntu target, текущего AMN2 package/source `1508e3c` и no-domain service-mode boundary. Этот документ не разрешает live VPS commands, SSH commands, wipe, reinstall, provider rebuild, package apply, service stop/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
task_id: VPS-FRESH-DEPLOY-002-CLEAN-UBUNTU-RUNBOOK-2026-06-11
linked_readiness: VPS-FRESH-DEPLOY-001-CLEAN-SERVER-READINESS-2026-06-10
linked_destructive_gate: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
result: completed-docs-only
runbook: docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md
plan: docs/superpowers/plans/2026-06-11-vps-fresh-deploy-002-clean-ubuntu-runbook.md
source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
live_commands_run: no
ssh_commands_run: no
destructive_action_authorized: no
reinstall_authorized: no
package_apply_authorized: no
public_exposure: no
config_delivery: no
write_api_implementation: no
secret_publication: none
go_no_go_decision: defer
```

## What Was Added

Created `docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md` with a future-approved-run checklist:

- current `1508e3c` package/source baseline and checksums;
- what can and cannot be recreated from repo/package;
- stop line before any live execution;
- local package staging checks;
- fresh OS baseline checks;
- base package install list;
- `amneziya` service user and `/opt/amn2` directory layout;
- private package upload and checksum verification;
- source install into `/opt/amn2`;
- private `.env` / `servers.yml` handling and safe defaults;
- read-only import and smoke;
- service-mode loopback acceptance;
- SSH tunnel operator access;
- final safe evidence acceptance criteria.

## Boundary Clarification

The runbook intentionally does not claim that the AMN2 package recreates every live runtime object. It separates:

```text
rebuildable_from_repo_package: AMN2 app source, venv, web/bot service-mode, loopback web/admin, safe smoke docs
operator_required_inputs: .env, servers.yml, bot/admin/session/API secrets, desired seed state
separate_gate_required: Amnezia runtime install/attach, production peers/users, config delivery, write API, public exposure
```

## Safety Result

```text
runbook_live_execution_authorized: no
wipe_reinstall_authorized: no
package_apply_authorized: no
delete_actions_planned: no
retention_path_decision_required: yes
stop_criteria_review_required: yes
exact_final_destructive_phrase_required: yes_if_operator_chooses_wipe
```

## Current Result

```text
status: completed-docs-only
active_plan_remove_task: VPS-FRESH-DEPLOY-002
remaining_active_task: VPS-REBUILD-001 retention path + stop criteria + final destructive phrase if wipe is chosen
recommendation: use the runbook for review now; do not run it live until retention path and destructive approval are explicit
```
