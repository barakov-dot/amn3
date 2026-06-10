# VPS-REBUILD-001: fresh VPS rebuild gate 2026-06-10

Дата: 2026-06-10.

Назначение: открыть отдельный destructive named gate для подготовки fresh VPS reinstall/rebuild под текущую AMN2/AMN3 задачу. Этот документ является только preflight/evidence gate. Он не разрешает wipe, reinstall, package apply, service stop/restart, firewall change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
gate_name: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
source_baseline: NG-V001 closed-go
target_label: operator_provided_redacted
operator_intent: try fresh rebuild under a destructive named gate
operation_class: destructive + remote-exec + secret-read + state-write
gate_status: opened-defer-awaiting-final-destructive-approval
preflight_mode: novice-safe snapshot-first
security_checkpoint: Codex Security threat-model required
security_risk_decision: defer
go_no_go_decision: defer
destructive_action_authorized: no
reinstall_authorized: no
live_commands_run: no
ssh_commands_run: no
AMN2_code_changed: no
public_exposure: no
config_delivery: no
write_api_implementation: no
secret_publication: none
```

## Why This Gate Exists

`NG-V001` proved the current target baseline as read-only safe summary: SSH transport ok, `amneziya-web` and `amneziya-bot` active/enabled, loopback `/login` HTTP 200, listener `3030` loopback-only, public API `3040` absent, TCP `80/443` absent, `VPS_APPLY_ENABLED=false`, and no secret-bearing evidence publication.

Fresh VPS reinstall/rebuild is intentionally outside `NG-V001`. It can destroy current runtime state, files, secrets, service definitions, firewall state and peer/config material. Therefore it needs a separate explicit gate, a data-retention decision and a final destructive approval phrase before any live action.

## Protected Assets

- Current service-mode baseline proven by `NG-V001`.
- `amneziya-web` and `amneziya-bot` runtime/service state.
- Web/admin loopback-only access path on `127.0.0.1:3030`.
- `.env`, `servers.yml`, admin/session secrets, Telegram bot token and API tokens.
- AmneziaWG runtime state, private keys, PSKs, peer configs, QR payloads and `vpn://` payloads.
- Approved test-peer lifecycle evidence.
- AMN2/AMN3 git heads, install packages, runtime docs and evidence files.
- Operator trust boundary: no target IP/host, secret, token, key or full command output is stored in repo evidence.

## Required Decisions Before Go

```text
data_retention_decision: preserve_snapshot_required
allowed_values: wipe_all_allowed | preserve_snapshot_required | export_safe_summary_only

snapshot_or_backup_decision: provider_snapshot_required
allowed_values: not_required_by_operator | provider_snapshot_required | encrypted_backup_required | safe_summary_only

install_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
allowed_values: explicit AMN2 commit or package hash only

install_package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
install_package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
source_zip: dist/amn2-codex-vps-test-prep-1508e3c-source.zip
source_zip_sha256: 0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E

secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
allowed_values: operator_local_channel_only | regenerate_on_target | restore_from_approved_secret_store

final_destructive_phrase: not_sent
required_exact_phrase: GO VPS-REBUILD-001 WIPE TARGET
```

Snapshot-first mode is selected because the current `NG-V001` baseline is known-good and should remain recoverable for a novice-safe rebuild path. Local source precheck selected AMN2 commit `1508e3c4a100b76815b29f91757290f1266f813d`; local package build/hygiene produced `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip` as `package-ready-not-vps-smoked`. Until the operator chooses a retention path, stop-criteria review and the exact final destructive phrase are complete, this gate stays `defer`.

## Source Precheck Result

Evidence: `research/amn2/vps-rebuild-001-source-package-precheck-2026-06-10.md`.

```text
source_precheck_status: passed
AMN2_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
focused_local_tests: 30 passed, 1 warning
package_precheck_status: blocked_until_1508e3c_package_build
neighboring_branch_policy: mine ideas explicitly, do not auto-merge into first rebuild package
```

## Package Build/Hygiene Result

Evidence: `research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md`.

```text
package_status: package-ready-not-vps-smoked
package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
source_zip: dist/amn2-codex-vps-test-prep-1508e3c-source.zip
source_zip_sha256: 0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E
package_entries: 5
source_entries: 302
forbidden_source_entries: 0
test_extract: passed
```

## Provider Snapshot Confirmation

Evidence: `research/amn2/vps-rebuild-001-provider-snapshot-confirmation-2026-06-10.md`.

```text
provider_snapshot_confirmation: defer
snapshot_required: yes
provider_snapshot_exists: no
provider_backup_plan_enabled: yes
backup_frequency: monthly
backup_created_now: unknown
backup_restorable: yes_after_backup_created
snapshot_delete_planned: no
backup_delete_planned: no
delete_actions_planned: no
operator_provider_panel_action_required: yes
provider_portal_action_by_codex: no
live_commands_run: no
ssh_commands_run: no
secret_publication: none
```

## Fresh Deploy Readiness Clarification

Evidence: `research/amn2/vps-fresh-deploy-001-readiness-checklist-2026-06-10.md`.

```text
fresh_deploy_readiness: documented
fresh_deploy_possible_from_repo_package: yes-with-operator-provided-secrets
bare_os_deploy_smoked: no
current_vps_disposable_decision: not-set
data_loss_acceptance_required_before_wipe: yes
provider_backup_required_for_readiness_docs: no
delete_actions_planned: no
destructive_action_authorized: no
```

This clarification answers the operator question about rebuilding from zero: source/package readiness can continue without waiting for the provider backup. It does not change the current destructive gate result. Before any wipe/reinstall, the operator must still choose a retention path: wait for provider backup, explicitly accept the current VPS as disposable, or keep this gate deferred.

## Allowed Now

- Update AMN3 docs/evidence for `VPS-REBUILD-001`.
- Prepare local-only command checklist and post-install acceptance checklist.
- Select candidate AMN2 source commit/package locally.
- Prepare local source/package precheck before any live action.
- Define safe summary fields for future evidence.
- Define stop criteria and rollback/recovery note.
- Optionally prepare a read-only pre-rebuild status checklist, but do not run it without separate explicit approval.

## Blocked Now

- VPS reinstall/rebuild, wipe, provider rebuild, destructive filesystem changes or package apply.
- `apt`, Docker, service, firewall, reverse proxy, Caddy/nginx or listener changes.
- `systemctl stop/start/restart/enable/disable`.
- Changing public exposure for `3030`, `3040`, `80`, `443` or domain/HTTPS.
- Config delivery, `.conf`, QR, `vpn://`, share/download links or secret-bearing output.
- `/api/clients` write CRUD, peer apply/revoke/sync write, Local Agent mutations.
- Backup/import/reboot.
- Production peer/user mutation.
- Copying GPL/upstream code, templates, UI, manager implementations or workflows.

## Stop Criteria

The gate must stop and return `no-go` or `defer` if:

- the target identity is ambiguous or evidence would reveal target secrets;
- any required decision remains pending;
- the selected source commit/package is not explicit;
- the plan requires public exposure, config delivery, write API or production mutation as part of rebuild;
- a required preflight cannot be summarized without secrets;
- the operator has not sent the exact final destructive phrase.

## Post-Install Acceptance Checklist

The rebuild can be considered acceptable only after a future approved live run produces secret-free safe summary evidence for:

- `ssh_transport=ok`;
- `amneziya-web` active/enabled;
- `amneziya-bot` active/enabled;
- web/admin loopback `/login` returns HTTP `200`;
- listener `3030` is loopback-only;
- public API `3040` is absent/closed;
- TCP `80/443` are absent unless a separate public gate explicitly changes that;
- `VPS_APPLY_ENABLED=false`;
- no config delivery occurred;
- no write API routes were opened;
- no production peer/user mutation occurred;
- no secret-bearing evidence was published.

## Current Gate Result

```text
gate_status: opened-defer-awaiting-final-destructive-approval
security_risk_decision: defer
go_no_go_decision: defer
preflight_mode: novice-safe snapshot-first
data_retention_decision: preserve_snapshot_required
snapshot_or_backup_decision: provider_snapshot_required
secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
install_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
install_package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
install_package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
provider_snapshot_confirmation: defer
provider_backup_plan_enabled: yes
backup_created_now: unknown
delete_actions_planned: no
fresh_deploy_readiness: documented
fresh_deploy_possible_from_repo_package: yes-with-operator-provided-secrets
current_vps_disposable_decision: not-set
next_required_operator_decision: choose retention path before any wipe: wait for provider backup, explicitly accept disposable target, or keep gate deferred; then stop-criteria review and exact final destructive phrase only if the operator still chooses wipe
```
