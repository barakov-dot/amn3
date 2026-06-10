# Phase 4 NG: named gate evidence template

Дата: 2026-06-10.

Назначение: reusable safe evidence template for `P4-NG` gates. Заполнять только после явного approval конкретного gate. Этот шаблон сам по себе не разрешает SSH, VPS sampling, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production peer/user mutation.

## Gate Identity

```text
gate_name:
gate_date:
operator_approval:
target_label:
operation_class:
planned_evidence_file:
```

`operator_approval` must be `explicit`. If approval is absent or ambiguous, stop and record `go_no_go_decision: no-go`.

## Allowed Actions

List only actions approved for this gate:

```text
allowed_actions:
- <approved read-only action>
```

If an action is not listed here, it is blocked for this gate.

## Blocked Actions

Default blocked actions:

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
- secret-bearing evidence publication
```

## Secrets Policy

Evidence may contain only boolean/status summaries and safe aggregate counts.

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

If a command output contains or may contain any forbidden field, do not paste it. Replace it with a safe summary such as `present`, `absent`, `passed`, `failed`, count-only, or `redacted`.

## Safe Summary Fields

```text
safe_summary_fields:
gate_status:
ssh_transport:
service_status_summary:
listener_summary:
loopback_http_summary:
vps_apply_enabled_false:
public_exposure_summary:
write_surface_summary:
config_delivery_summary:
secret_publication_summary:
preflight_errors_summary:
recovery_or_rollback_summary:
```

Use `not_checked` for any field outside the approved gate scope.

## Preflight

```text
preflight:
approval_confirmed:
target_confirmed:
host_key_verification_handled_outside_repo:
allowed_actions_reviewed:
blocked_actions_reviewed:
secrets_policy_reviewed:
rollback_or_recovery_note_ready:
```

Any `no` in preflight means `go_no_go_decision: no-go` or `defer`.

## Gate Result

Allowed decisions:

```text
go_no_go_decision: go | no-go | defer
decision_reason:
safe_result:
next_action:
```

Decision rules:

- `go`: all approved checks passed, no blocked action was performed, no secret-bearing evidence was published.
- `no-go`: approval is absent/ambiguous, preflight fails, a blocked action would be needed, or a secret-safe summary cannot be produced.
- `defer`: target/context is missing, operator intentionally postpones, or more design work is needed before the gate can run.

`go` authorizes only the completed gate result. It does not authorize adjacent VPS/live/public/write/config work.
