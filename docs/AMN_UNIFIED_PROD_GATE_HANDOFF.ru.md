# AMN Unified Prod Gate Handoff

Дата: 2026-06-08.

Назначение: подготовить единый handoff для будущего объединенного production-чата, который свяжет:

- AMN2/API line;
- Phase 2 live VPS gate;
- новый target VPS prep;
- PRVTPRO/Amnezia Web Panel candidate line;
- VPN Ops Lab evidence/decision registry.

Этот документ не переносит live-команды в новый чат. Он задает порядок объединения, чтобы не было трех источников команд для одного VPS.

## Current Override 2026-06-09

Phase 2 live gate, target VPS prep and Phase 3 service-mode loopback gates are no longer pending. The new target VPS is now in service-mode for web/bot only, with web/admin bound to `127.0.0.1:3030` and operator access through SSH tunnel only. Use `docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md` as the active Phase 3 handoff.

Still closed: HTTPS reverse proxy/public cutover, any domain/Caddy path, public API `3040`, direct public web/admin `3030`, production peer mutation beyond the two approved test peers, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent write/config mutations and backup/import/reboot routes.

## Текущая Точка Правды

```text
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 branch: codex-vps-test-prep
AMN2 current head: f7f6131 Update integration status for c92 manual prelaunch

AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 GitHub: barakov-dot/amn3
current package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
package status: read-only-vps-smoke-pass
source_update_run_id: 20260607T203721Z
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z

validation VPS mode: manual runtime historical baseline
validation VPS source overlay: do-not-touch-after-f7f6131
target VPS mode: service-mode web/bot active, loopback-only
target VPS operator access: SSH tunnel only
target VPS live peer count: 2 approved test peers
target VPS revoked peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
target VPS public/direct 3030: closed by loopback bind
target VPS public API 3040: absent/closed
target VPS TCP 80/443: absent
target VPS domain/Caddy/HTTPS public cutover: deferred indefinitely
VPS_APPLY_ENABLED in target .env: false
```

## Chat Roles

```text
Phase 2/3 live gate chats:
  role: owners of already completed real VPS gates and safe evidence
  allowed: keep historical context and one-copy live evidence
  returns: safe summary only, no secrets

This AMN2/API coordination chat:
  role: integration dispatcher, status map, API boundary and next-slice planner
  allowed: docs/evidence/handoff, package coordination, read-only planning
  blocked: treating service-mode loopback evidence as approval for route expansion or write APIs

PRVTPRO-Amnezia-Web-Panel chat:
  role: UI/web-panel candidate source
  allowed: collect UX/features/architecture ideas
  blocked: direct promotion to production without AMN2 gate and tests

Future unified chat:
  role: single production decision room after Phase 3 service-mode evidence
  input: this handoff + Phase 3 safe evidence + PRVTPRO candidate summary
```

## Why Not Merge The Chats Immediately

Phase 2/3 live execution has produced the safe summaries, but live authority should still stay single-owner per gate. Moving new live commands into multiple chats can cause:

- duplicate commands against one server;
- conflicting `VPS_APPLY_ENABLED` assumptions;
- mixed validation VPS vs target VPS evidence;
- accidental route/API/write expansion from a read-only/service-mode evidence record;
- secret-bearing output copied into the wrong context.

Therefore, future live execution should open as a named gate with one owner. This document is now the coordination map; it is not a standing authorization to run new live mutations.

## Required Phase 2 Safe Summary

Phase 2 chat should return only:

```text
phase2_gate_status:
server_label:
AMN2_head_or_runtime:
VPS_APPLY_ENABLED:
operation_class:
live_write_performed:
target_peer_or_user_scope:
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

Do not return:

- `.env`;
- `servers.yml`;
- raw token;
- Authorization header;
- token hash;
- private key;
- PSK;
- `.conf`;
- QR;
- `vpn://`;
- backup contents;
- full logs;
- provider console credentials.

## Target VPS Prep Input

The new rented VPS should follow:

```text
gate: docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
runbook: docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
evidence template: research/amn2/target-server-prep-evidence-template-2026-06-08.md
evidence note: research/amn2/target-server-prep-gate-2026-06-08.md
```

Target VPS current safe mode:

```text
runtime_mode: service-mode web/bot, loopback-only
web_admin_bind: 127.0.0.1:3030
operator_access: SSH tunnel only
public API 3040: no
direct public web 3030: no
systemd: enabled/active for web and bot
reverse proxy: not enabled
domain/Caddy/HTTPS public cutover: deferred indefinitely
live_peer_count: 2
approved_test_peers: Neobyatnaya-AMNZ-1, Neobyatnaya-AMNZ-2
revoked_test_peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
web_panel_smoke: unauth redirect passed, authenticated read-only GET passed
write_actions: none
VPS_APPLY_ENABLED: false
```

## PRVTPRO/Web Panel Candidate Intake

PRVTPRO chat output should be converted into candidate rows before touching AMN2:

```text
candidate_id:
source_chat: VPN Ops Lab — VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel
feature_area:
user_value:
AMN2_fit:
risk_class:
secret_surface:
remote_write_surface:
test_plan:
required_gate:
recommendation: accept / defer / reject / research
```

Immediate candidates may be accepted only if they are:

- read-only;
- no public API expansion;
- no secret-bearing output;
- no live remote mutation;
- covered by local tests and later VPS smoke if route/runtime changes.

## Unified Chat Opening Packet

Current active opening packet for Phase 3 lives in:

```text
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
```

Historical packet below remains as broader context.

When opening the future unified chat, paste this packet:

```text
Название: AMN Unified Prod Gate — AMN2 + PRVTPRO + Target VPS

Sources:
- docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
- docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
- docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
- research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
- research/amn2/target-server-prep-gate-2026-06-08.md
- latest safe summary from Phase 2 live gate chat
- candidate summary from PRVTPRO-Amnezia-Web-Panel chat

Decision rules:
- one chat owns live commands at a time;
- validation VPS source overlay remains untouched after f7f6131 pass;
- target VPS service-mode web/bot is loopback-only and tunnel-only;
- public/reverse-proxy/API/write work requires a separate gate;
- PRVTPRO ideas enter as candidates, not direct production changes;
- no secrets in chat or GitHub.
```

## Still Blocked

- `VPS_APPLY_ENABLED=true` without a live gate;
- broad write API;
- public API `3040`;
- direct public web/admin `3030`;
- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- service-mode expansion beyond loopback web/bot and any reverse proxy/public cutover without a separate gate;
- publishing secret-bearing evidence.

## Next Action

```text
1. Treat `bc00b77` Phase 3 evidence/runbooks as the current AMN3 checkpoint.
2. Keep the target VPS in loopback-only service mode with SSH tunnel operator access.
3. Convert PRVTPRO/Web Panel ideas into candidate rows before any AMN2 changes.
4. Prepare the next AMN2/API slice as local/read-only by default.
5. Open a separate gate before public API, config delivery, write CRUD, Local Agent mutation, backup/import/reboot, Caddy/HTTPS or production peer writes.
```
