# Unified prod gate handoff 2026-06-08

Дата: 2026-06-08.

Назначение: зафиксировать docs-only/read-only coordination slice для будущего объединенного production-чата после запуска Phase 2 live gate на реальном VPS.

## Baseline

```text
AMN2 current head: f7f6131 Update integration status for c92 manual prelaunch
AMN3 current package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
validation VPS source overlay status: read-only-vps-smoke-pass
latest_repeat_api_smoke_run_id: 20260607T204300Z
target VPS prep gate: prepared
service mode: separate gate required
```

## Scope

This slice:

- defines chat ownership for live VPS commands;
- keeps Phase 2 live gate chat as active live-command owner;
- keeps this chat as AMN2/API integration dispatcher;
- keeps PRVTPRO/Web Panel chat as candidate source;
- defines when to open the future unified chat;
- defines safe evidence packet and stop lines.

Production code changes: none.

AMN2 source changes: none.

## Artifacts

```text
handoff: docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
target server gate: docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
target server runbook: docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
target server evidence template: research/amn2/target-server-prep-evidence-template-2026-06-08.md
```

## Decision

```text
decision: prepare-unified-chat-after-phase2-safe-summary
live_command_owner: Phase 2 live gate chat
integration_dispatcher: AMN2/API coordination chat
candidate_source: PRVTPRO-Amnezia-Web-Panel chat
unified_chat_status: pending-first-phase2-safe-summary
```

## Still Blocked

- multiple chats issuing live commands to the same VPS;
- validation VPS source-overlay changes after `f7f6131` pass;
- `VPS_APPLY_ENABLED=true` without a live gate;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse proxy on target VPS without separate approval;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config routes;
- backup/import/reboot routes;
- raw tokens, Authorization headers, token hashes, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Evidence Expected

```text
phase2_gate_status:
server_label:
AMN2_head_or_runtime:
VPS_APPLY_ENABLED:
operation_class:
live_write_performed:
preflight_status:
api_smoke_status:
checked_routes:
auth_status:
listener_status:
audit_status:
rollback_status:
safe_evidence_dir:
next_recommendation:
```
