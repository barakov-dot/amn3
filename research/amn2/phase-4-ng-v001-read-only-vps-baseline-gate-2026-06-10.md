# Phase 4 NG-V001: read-only VPS baseline gate 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `NG-V001` как named gate для read-only проверки текущего target VPS baseline. Этот документ фиксирует только safe summary evidence. Он не разрешает package apply, service restart/enable/disable, firewall/reverse proxy edits, public exposure, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot, production peer/user mutation или fresh VPS rebuild.

## Gate Identity

```text
gate_name: P4-NG-VPS-READONLY-BASELINE-2026-06-10
gate_date: 2026-06-10
operator_approval: explicit-start-approved
operator_phrase: "приступаем"
target_label: operator_provided_redacted
operation_class: read-only VPS baseline
planned_evidence_file: research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md
gate_status: closed-go
```

## Codex Security Checkpoint

```text
security_checkpoint: Codex Security risk review
security_source: research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md
security_risk_decision: go
security_decision_reason: operator provided target outside repository files; final safe output contains only allowed read-only status summaries, no secret-bearing evidence and no state-changing result
destructive_action_authorized: no
fresh_vps_rebuild_authorized: no
```

`NG-SC001` requires `security_risk_decision: go | no-go | defer` before any live/read-only or destructive gate work. For this gate, the decision is `go` because the final evidence stayed inside the approved read-only scope and did not publish secrets.

## Allowed Actions

These were the only approved action classes for this gate.

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
target_confirmed: yes
host_key_verification_handled_outside_repo: not_recorded_in_evidence
allowed_actions_reviewed: yes
blocked_actions_reviewed: yes
secrets_policy_reviewed: yes
rollback_or_recovery_note_ready: yes
```

Rollback/recovery note: current pass is read-only only, so it must not create remote state. If any check would require write access, restart, apply, config output, public exposure or destructive operation, stop and return `no-go` or create a separate named gate.

## Safe Summary Fields

```text
safe_summary_fields:
gate_status: closed-go
ssh_transport: ok
service_status_summary: amneziya-web active/enabled; amneziya-bot active/enabled
listener_summary: 3030 present loopback-only; 3040 absent; 80 absent; 443 absent
loopback_http_summary: 127.0.0.1:3030/login returned HTTP 200
vps_apply_enabled_false: yes
public_exposure_summary: direct public API 3040 absent; TCP 80 absent; TCP 443 absent; web/admin 3030 loopback-only
write_surface_summary: no write/sync/apply/revoke action performed; VPS_APPLY_ENABLED=false
config_delivery_summary: no config delivery performed
secret_publication_summary: no_secret_evidence_published
preflight_errors_summary: earlier listener command outputs were superseded by final clean listener evidence
recovery_or_rollback_summary: read-only gate; no remote state changes allowed
```

## Gate Result

```text
go_no_go_decision: go
decision_reason: read-only baseline checks passed using safe summary fields; no blocked action was needed; no secret-bearing evidence was published
safe_result: target baseline matches expected service-mode loopback-only boundary
next_action: remove NG-V001 from active P4-NG plan; any fresh VPS rebuild still requires separate VPS-REBUILD-001
```

## Active Plan Effect

`NG-V001` is closed and removed from the active P4-NG plan:

```text
critical: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Fresh VPS reinstall/rebuild remains outside this gate and requires a separate destructive gate `VPS-REBUILD-001`.
