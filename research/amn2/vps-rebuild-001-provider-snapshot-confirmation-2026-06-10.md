# VPS-REBUILD-001: provider snapshot confirmation 2026-06-10

Дата: 2026-06-10.

Назначение: открыть безопасный confirmation step для provider snapshot перед возможным `VPS-REBUILD-001` fresh VPS rebuild. Этот документ не подтверждает наличие snapshot сам по себе и не разрешает VPS commands, SSH commands, wipe, reinstall, package apply, service changes, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
confirmation_id: VPS-REBUILD-001-PROVIDER-SNAPSHOT-CONFIRMATION-2026-06-10
gate_name: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
confirmation_scope: provider backup/snapshot existence and recoverability, safe summary only
result: backup-plan-enabled-recovery-copy-not-confirmed
snapshot_required: yes
snapshot_confirmation: defer
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
destructive_action_authorized: no
reinstall_authorized: no
package_apply_authorized: no
secret_publication: none
go_no_go_decision: defer
```

## Why This Step Exists

`VPS-REBUILD-001` is a destructive gate. The novice-safe mode selected earlier requires a provider snapshot before any wipe/reinstall decision. A snapshot gives the operator a recovery point if a fresh rebuild exposes an unexpected installer, runtime, secret or networking issue.

## Current Safe Summary

The operator enabled the monthly backup plan in the provider panel. A created/restorable backup or snapshot is not confirmed yet, and no deletion is planned.

```text
provider_snapshot_exists: no
provider_backup_plan_enabled: yes
backup_frequency: monthly
backup_created_now: unknown
backup_restorable: yes_after_backup_created
snapshot_created_at_utc: unknown
snapshot_label_redacted: not_applicable
snapshot_target_label: operator_provided_redacted
snapshot_delete_planned: no
backup_delete_planned: no
delete_actions_planned: no
provider_snapshot_confirmation: defer
```

## Required Operator Confirmation

If a real snapshot or backup becomes visible later, return only this safe summary after checking it in the provider panel:

```text
provider_snapshot_exists: yes | no
snapshot_created_at_utc: YYYY-MM-DDTHH:MM:SSZ | unknown
snapshot_label_redacted: safe label only, no IP/account/provider ids
snapshot_target_label: operator_provided_redacted
snapshot_restorable: yes | unknown | no
snapshot_delete_planned: no
backup_delete_planned: no
delete_actions_planned: no
provider_snapshot_confirmation: confirmed | blocked | defer
```

Do not paste:

- VPS IP/host;
- provider account id;
- invoice/customer ids;
- console URLs with tokens;
- screenshots that reveal IP/account details, tokens, keys or passwords;
- full provider logs;
- `.env`, `servers.yml`, raw tokens, private keys, PSK, `.conf`, QR, `vpn://` or backup contents.

## Allowed Now

- Operator may create or verify a provider snapshot in the provider panel.
- Operator may return only the safe summary fields above.
- AMN3 may update docs/evidence with the safe summary result.

## Blocked Now

- Running any command on the VPS.
- Rebooting, rebuilding, wiping or reinstalling the VPS.
- Applying `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`.
- Deleting snapshots or backups.
- Changing firewall, reverse proxy, listeners, public `3030`, public API `3040`, TCP `80/443`, Caddy/nginx/HTTPS or domain settings.
- Config delivery, `.conf`, QR, `vpn://`, share/download links or secret-bearing output.
- Write API, `/api/clients` CRUD, peer/user mutation, Local Agent mutation, backup/import/reboot.

## Close Conditions

This confirmation can close as `confirmed` only if:

```text
provider_snapshot_exists: yes
snapshot_restorable: yes | unknown
snapshot_delete_planned: no
secret_publication: none
```

If `provider_snapshot_exists=no` or the operator is unsure whether a backup/snapshot has already been created and can be restored, keep this step `defer`.

## Current Result

```text
provider_snapshot_confirmation: defer
provider_backup_plan_enabled: yes
backup_created_now: unknown
delete_actions_planned: no
next_required_operator_action: ask provider where to see created backups or whether an immediate backup can be created
remaining_after_confirmation: stop-criteria review before any final destructive phrase
go_no_go_decision: defer
```
