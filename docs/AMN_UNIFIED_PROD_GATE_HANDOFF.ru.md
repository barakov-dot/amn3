# AMN Unified Prod Gate Handoff

Дата: 2026-06-08.

Назначение: подготовить единый handoff для будущего объединенного production-чата, который свяжет:

- AMN2/API line;
- Phase 2 live VPS gate;
- новый target VPS prep;
- PRVTPRO/Amnezia Web Panel candidate line;
- VPN Ops Lab evidence/decision registry.

Этот документ не переносит live-команды в новый чат. Он задает порядок объединения, чтобы не было трех источников команд для одного VPS.

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

validation VPS mode: manual runtime
validation VPS source overlay: do-not-touch-after-f7f6131
target VPS mode before approval: target-server-prep-gate only
service mode: separate gate required
```

## Chat Roles

```text
Phase 2 live gate chat:
  role: owner of real VPS live commands and live evidence
  allowed: run the active approved VPS gate
  returns: safe summary only

This AMN2/API coordination chat:
  role: integration dispatcher, status map, target-server prep, API boundary
  allowed: docs/evidence/handoff, package coordination, read-only planning
  blocked: issuing conflicting live VPS commands while Phase 2 chat is active

PRVTPRO-Amnezia-Web-Panel chat:
  role: UI/web-panel candidate source
  allowed: collect UX/features/architecture ideas
  blocked: direct promotion to production without AMN2 gate and tests

Future unified chat:
  role: single production decision room after first Phase 2 safe evidence summary
  input: this handoff + Phase 2 safe evidence + PRVTPRO candidate summary
```

## Why Not Merge The Chats Immediately

Active VPS connection is already being handled in the Phase 2 chat. Moving live commands into multiple chats can cause:

- duplicate commands against one server;
- conflicting `VPS_APPLY_ENABLED` assumptions;
- mixed validation VPS vs target VPS evidence;
- accidental service-mode enablement;
- secret-bearing output copied into the wrong context.

Therefore, live execution remains in the Phase 2 chat until it returns a safe summary. The new unified chat should start after that summary is available.

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

Target VPS starts as:

```text
runtime_mode: manual bootstrap + read-only smoke
public API 3040: no
direct public web 3030: no
systemd: not enabled
reverse proxy: not production-enabled
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
- target VPS prep is a separate gate;
- service mode requires separate approval;
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
- service-mode `systemd`/reverse proxy on target VPS without a separate gate;
- publishing secret-bearing evidence.

## Next Action

```text
1. Let Phase 2 live gate chat finish or return first safe summary.
2. Keep this chat as integration dispatcher.
3. Prepare target VPS using target-server prep gate.
4. Convert PRVTPRO/Web Panel ideas into candidate rows.
5. Open unified chat only after Phase 2 summary exists.
```
