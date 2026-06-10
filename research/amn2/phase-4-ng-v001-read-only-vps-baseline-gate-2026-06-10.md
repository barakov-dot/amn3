# Phase 4 NG-V001: read-only VPS baseline gate 2026-06-10

Дата: 2026-06-10.

Назначение: открыть `NG-V001` как named gate для будущей read-only проверки текущего target VPS baseline. Этот документ фиксирует preflight и safe evidence boundary. Он не разрешает package apply, service restart/enable/disable, firewall/reverse proxy edits, public exposure, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot, production peer/user mutation или fresh VPS rebuild.

## Gate Identity

```text
gate_name: P4-NG-VPS-READONLY-BASELINE-2026-06-10
gate_date: 2026-06-10
operator_approval: explicit-start-approved
operator_phrase: "приступаем"
target_label: pending_operator_provided_ssh_alias_or_host
operation_class: read-only VPS baseline
planned_evidence_file: research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md
gate_status: opened-defer-awaiting-target
```

## Codex Security Checkpoint

```text
security_checkpoint: Codex Security risk review
security_source: research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md
security_risk_decision: defer
security_decision_reason: target SSH alias/host is not yet operator-provided in this gate turn, so live read-only SSH cannot start safely
destructive_action_authorized: no
fresh_vps_rebuild_authorized: no
```

`NG-SC001` requires `security_risk_decision: go | no-go | defer` before any live/read-only or destructive gate work. For this opening pass, the decision is `defer` because the target is not confirmed yet. No SSH/VPS command was run.

## Allowed Actions After Target Confirmation

These actions are allowed only after the operator provides the target SSH alias/host outside repository secrets and the security checkpoint is updated to `security_risk_decision: go`.

```text
allowed_actions:
- verify SSH transport to the operator-provided target
- read-only service status summary for amneziya-web and amneziya-bot
- read-only loopback /login check on 127.0.0.1:3030
- read-only listener checks for 3030, 3040, 80 and 443
- boolean-only proof that VPS_APPLY_ENABLED=false exists, without printing .env
```

## Blocked Actions

```text
blocked_actions:
- package apply
- service restart/enable/disable
- firewall/reverse proxy edits
- public API 3040 exposure
- direct public web/admin 3030 exposure
- Caddy/nginx/HTTPS/domain cutover
- VPS_APPLY_ENABLED=true
- peer apply/revoke/sync
- config delivery, .conf, QR, vpn://
- /api/clients write CRUD
- API config:read
- token issue/revoke/rotate API routes
- Local Agent write/config mutations
- backup/import/reboot
- production peer/user mutation
- fresh VPS reinstall/rebuild
- secret-bearing evidence publication
```

Fresh VPS reinstall/rebuild is explicitly outside `NG-V001`. If selected later, it requires separate destructive gate `VPS-REBUILD-001`.

## Secrets Policy

Safe evidence may contain only boolean/status summaries and safe aggregate counts.

Never publish:

```text
forbidden_evidence_fields:
- .env values or raw .env
- raw servers.yml
- raw tokens
- Authorization headers
- token hashes
- web password hash
- session secret
- private keys
- PSK
- peer public keys
- client .conf
- QR payloads or QR images
- vpn:// links
- backup contents
- public endpoint values
- session cookies
- full logs
- secret-bearing command output
```

## Preflight

```text
preflight:
approval_confirmed: yes
target_confirmed: no
host_key_verification_handled_outside_repo: pending
allowed_actions_reviewed: yes
blocked_actions_reviewed: yes
secrets_policy_reviewed: yes
rollback_or_recovery_note_ready: yes
```

Rollback/recovery note: current pass is read-only only, so it must not create remote state. If any check would require write access, restart, apply, config output, public exposure or destructive operation, stop and return `no-go` or create a separate named gate.

## Safe Summary Fields

```text
safe_summary_fields:
gate_status: opened-defer-awaiting-target
ssh_transport: not_checked
service_status_summary: not_checked
listener_summary: not_checked
loopback_http_summary: not_checked
vps_apply_enabled_false: not_checked
public_exposure_summary: not_checked
write_surface_summary: not_checked
config_delivery_summary: not_checked
secret_publication_summary: no_secret_evidence_published
preflight_errors_summary: target SSH alias/host not yet provided
recovery_or_rollback_summary: read-only gate; no remote state changes allowed
```

## Gate Result

```text
go_no_go_decision: defer
decision_reason: explicit start approval is present, but target SSH alias/host is not yet confirmed outside repo secrets; security_risk_decision remains defer
safe_result: no live command was run; no secret-bearing evidence was published; no state changed
next_action: operator provides target SSH alias/host outside repository secrets, then rerun NG-V001 live read-only checks with security_risk_decision: go
```

## Active Plan Effect

`NG-V001` is open but not closed. It remains the only active P4-NG task:

```text
critical: none
very_important: NG-V001 read-only VPS baseline gate, opened-defer-awaiting-target
important: none
normal: none
simple: none
cosmetic: none
```

Do not remove `NG-V001` from the active plan until the read-only VPS baseline evidence is completed with `go`, `no-go` or an operator decision to stop the gate.
