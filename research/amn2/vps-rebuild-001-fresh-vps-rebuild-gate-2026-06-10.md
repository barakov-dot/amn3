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
data_retention_decision: pending
allowed_values: wipe_all_allowed | preserve_snapshot_required | export_safe_summary_only

snapshot_or_backup_decision: pending
allowed_values: not_required_by_operator | provider_snapshot_required | encrypted_backup_required | safe_summary_only

install_source_commit: pending
allowed_values: explicit AMN2 commit or package hash only

secret_transfer_policy: pending
allowed_values: operator_local_channel_only | regenerate_on_target | restore_from_approved_secret_store

final_destructive_phrase: pending
required_exact_phrase: GO VPS-REBUILD-001 WIPE TARGET
```

Until all decisions above are filled and the exact final destructive phrase is sent by the operator, this gate stays `defer`.

## Allowed Now

- Update AMN3 docs/evidence for `VPS-REBUILD-001`.
- Prepare local-only command checklist and post-install acceptance checklist.
- Select candidate AMN2 source commit/package locally.
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
next_required_operator_decision: data retention mode, snapshot/backup mode, install source commit/package, secret transfer policy, then exact final destructive phrase
```
