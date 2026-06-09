# Unified prod gate handoff 2026-06-08

Дата: 2026-06-08.

Назначение: зафиксировать docs-only/read-only coordination slice для объединенного production-чата после Phase 2 live gate и Phase 3 target VPS service-mode evidence.

## Baseline

```text
AMN2 current head: f7f6131 Update integration status for c92 manual prelaunch
AMN3 current package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
validation VPS source overlay status: read-only-vps-smoke-pass
latest_repeat_api_smoke_run_id: 20260607T204300Z
target VPS prep gate: completed
target VPS Phase 3 service mode: enabled-loopback-web-bot
operator access: SSH tunnel only
public API 3040: absent/closed
direct public web 3030: closed by loopback bind
TCP 80/443: absent
domain/Caddy/HTTPS public cutover: deferred indefinitely
live_peer_count: 2
remaining_test_peers: Neobyatnaya-AMNZ-1, Neobyatnaya-AMNZ-2
revoked_test_peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
```

## Scope

This slice:

- records that Phase 2 and Phase 3 safe summaries are available;
- keeps one live-command owner per future named gate;
- keeps this chat as AMN2/API integration dispatcher;
- keeps PRVTPRO/Web Panel chat as candidate source;
- defines the unified chat boundary after service-mode loopback evidence;
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
decision: phase3-service-mode-loopback-ssh-tunnel-recorded
live_command_owner: one owner per future explicit gate
integration_dispatcher: AMN2/API coordination chat
candidate_source: PRVTPRO-Amnezia-Web-Panel chat
unified_chat_status: ready-with-phase3-service-mode-handoff
```

## Still Blocked

- multiple chats issuing live commands to the same VPS without a named gate owner;
- validation VPS source-overlay changes after `f7f6131` pass;
- `VPS_APPLY_ENABLED=true` without a live gate;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode expansion beyond loopback web/bot and any reverse proxy/public cutover without separate approval;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config routes;
- backup/import/reboot routes;
- raw tokens, Authorization headers, token hashes, `.env`, `servers.yml`, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Current Safe Evidence Packet

```text
phase3_service_mode_status: passed-loopback-ssh-tunnel
AMN3_commit: bc00b77 Record Phase 3 service mode evidence
AMN2_source_overlay: f7f6131
VPS_APPLY_ENABLED: false
web_bot_systemd: enabled-active
web_admin_listener: 127.0.0.1:3030
operator_access: SSH tunnel only
public_3030: no
public_api_3040: no
tcp_80_443: absent
live_peer_count: 2
approved_test_peers: Neobyatnaya-AMNZ-1, Neobyatnaya-AMNZ-2
revoked_test_peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
web_panel_unauth_smoke: passed
web_panel_authenticated_read_only_smoke: passed
write_actions: none
next_recommendation: local read-only/status/UX slices only until a separate gate is opened
```
