# VPS-FRESH-DEPLOY-001: clean server readiness checklist 2026-06-10

Дата: 2026-06-10.

Назначение: ответить на operator question, можем ли мы развернуть AMN2 с нуля на чистом VPS из GitHub/source/package, не ожидая provider backup как блокер для всей работы. Этот документ является AMN3 docs-only readiness evidence. Он не разрешает wipe, reinstall, provider rebuild, package apply, service stop/restart, firewall change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
gate_name: VPS-FRESH-DEPLOY-001-CLEAN-SERVER-READINESS-2026-06-10
linked_destructive_gate: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
operation_class: docs-only readiness for a future destructive clean deploy
result: readiness-documented
fresh_deploy_possible_from_repo_package: yes-with-operator-provided-secrets
bare_os_deploy_smoked: no
current_vps_disposable_decision: not-set
data_loss_acceptance_required_before_wipe: yes
provider_backup_required_for_readiness_docs: no
provider_backup_required_for_novice_safe_rollback: recommended-or-operator-overridden
destructive_action_authorized: no
reinstall_authorized: no
delete_actions_planned: no
live_commands_run: no
ssh_commands_run: no
provider_portal_action_by_codex: no
public_exposure: no
config_delivery: no
write_api_implementation: no
secret_publication: none
go_no_go_decision: defer
```

## Short Answer

Да, AMN2 можно готовить к развертыванию с нуля на чистом сервере, потому что source/package baseline уже выбран и локально проверен. Это не значит, что текущая VPS должна быть стерта сейчас. До wipe/reinstall нужно отдельно принять data-retention decision: ждать provider backup, считать текущую VPS disposable test target, или выбрать другой recovery path.

## Rebuildable From Repo / Package

Эти части можно восстановить из GitHub/source/package и operator runbook, без сохранения текущего runtime state:

- AMN2 source commit `1508e3c4a100b76815b29f91757290f1266f813d`.
- AMN3 package `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`.
- Package checksum `03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3`.
- Source zip `dist/amn2-codex-vps-test-prep-1508e3c-source.zip`.
- Source zip checksum `0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E`.
- Web/admin intended boundary: loopback-only `127.0.0.1:3030`.
- Operator access model: SSH tunnel only.
- Public API `3040`: absent/closed by default for this stage.
- TCP `80/443`: absent unless a separate public gate later changes that.
- `VPS_APPLY_ENABLED=false` as the default safe runtime boundary.
- Existing AMN3 evidence, runbooks and post-install acceptance checklist.

## Not Rebuildable Without Operator Input

Эти данные нельзя считать восстановимыми из repo/package alone. Перед wipe/reinstall operator must either preserve them, recreate them manually, or accept loss:

- `.env` values, bot token, web/admin secret, session secret and API/token material.
- Raw `servers.yml` or target-specific server inventory secrets.
- Current local SQLite DB contents, users/devices/orders/logs if not exported through an approved safe path.
- Live Amnezia runtime state, private keys, PSKs and peer config material.
- Existing test peer/client configs, QR payloads and `vpn://` payloads.
- Provider-side backup/snapshot availability and restore history.
- Any manually edited service/firewall/provider settings not represented in repo/runbook.

## Required Operator Decisions Before Any Wipe

```text
target_identity_confirmed_out_of_repo: required
data_retention_decision: required
allowed_values: preserve_snapshot_required | wipe_all_allowed | export_safe_summary_only
current_vps_disposable_decision: required_if_no_snapshot
external_secret_channel: operator-local-only
desired_seed_state_after_clean_deploy: required
final_destructive_phrase: required_only_if_operator_chooses_wipe
```

The current `VPS-REBUILD-001` selected novice-safe value remains `preserve_snapshot_required` until explicitly changed. This readiness note only records that a clean deploy is technically plausible from source/package plus operator-provided secrets.

## Readiness Checklist

```text
source_commit_selected: yes
source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
focused_local_tests_passed: yes
focused_local_tests_result: 30 passed, 1 warning
package_built: yes
package_hygiene_passed: yes
package_status: package-ready-not-vps-smoked
provider_backup_plan_enabled: yes
created_restorable_backup_confirmed: no
bare_os_bootstrap_runbook_finalized: partial
bare_os_deploy_smoked: no
post_install_acceptance_checklist_exists: yes
secret_transfer_policy_defined: yes
secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
public_cutover_required_for_clean_deploy: no
write_api_required_for_clean_deploy: no
config_delivery_required_for_clean_deploy: no
```

## Safe Interpretation

Backup is not a blocker for docs/source/package readiness. Backup is a rollback and recovery control for the current VPS state. If the operator decides that the current VPS is disposable, that decision must be recorded before destructive action, but the package/readiness work can continue without waiting for the provider to create the monthly backup.

## Still Blocked

- Wipe/reinstall/provider rebuild.
- Package apply to target VPS.
- Service stop/start/restart/enable/disable.
- Firewall/reverse proxy/public listener changes.
- Public API `3040`, direct public web/admin `3030`, TCP `80/443` exposure or Caddy/HTTPS/domain cutover.
- Config delivery, `.conf`, QR, `vpn://`, share/download links or secret-bearing output.
- `/api/clients` write CRUD, live peer apply/revoke/sync, Local Agent mutation.
- Backup/import/reboot routes or actions.
- Production peer/user mutation.
- Secret-bearing evidence publication.

## Current Result

```text
readiness_result: documented
fresh_deploy_possible_from_repo_package: yes-with-operator-provided-secrets
current_vps_disposable_decision: not-set
delete_actions_planned: no
destructive_action_authorized: no
next_required_decision: choose retention path before any wipe: wait for provider backup, explicitly accept disposable target, or keep VPS-REBUILD-001 deferred
recommendation: continue local/non-destructive readiness work; do not run wipe/reinstall until retention path and exact final destructive phrase are recorded
```
