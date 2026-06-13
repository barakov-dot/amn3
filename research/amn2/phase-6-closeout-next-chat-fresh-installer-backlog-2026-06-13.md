# Phase 6 closeout / next-chat / fresh installer backlog

Date: 2026-06-13.

Status: `closed`.

Scope: AMN3 docs-only closeout and handoff.

## Decision

```text
task_id: P6-S004
priority: simple
scope: Phase 6 closeout packet + next-chat handoff + fresh installer backlog grooming
result: closed
phase_6_default_lane: closed
public_launch: not opened
live_vps_command: no
ssh_command: no
package_apply_on_vps: no
destructive_action: no
```

## Source State

```text
AMN3 branch: master
AMN2 branch: codex-vps-test-prep
AMN2 current head: c46f664 Add public taxonomy cleanup checklist
AMN2 latest VPS-smoked/package head: c46f664 Add public taxonomy cleanup checklist
latest VPS-smoke evidence: research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md
```

## What Closed In Phase 6

Phase 6 closed the default planning/security/productization lane:

- production security review gate;
- scoped API token production policy;
- self-service/admin surface separation;
- capability registry and integration-status current-head alignment;
- commercial/manual approval and support/news bot split boundaries;
- Telegram profile/icon apply gate policy;
- aggregate privacy/status/analytics boundary;
- reconciliation/release boundary;
- reusable project operating-system templates;
- telemetry retention and upstream refresh incorporation;
- iOS/Android client compatibility and public copy/brand alignment;
- live update/smoke gates for `b3102db` and `c46f664`;
- config-link entitlement boundary as local-only design/implementation;
- fresh-install wizard/bootstrap local-only boundary;
- public docs/API taxonomy and destructive cleanup checklist-only boundary;
- package runbook escaping hygiene guardrail.

## New/Updated Documents

```text
docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md
```

Synchronized:

```text
docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
docs/PHASE_5_6_FORWARD_PLAN.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
research/amn2/transfer-backlog.md
```

## Remaining Gates

These remain not executed and not approved by default:

- `P6-C001` Public exposure gate.
- `P6-C002` Config delivery gate.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `P6-C007` Destructive cleanup/reinstall gate.
- `VPS-REBUILD-001`, carried from earlier phases.
- Local Agent write/config routes.
- Production peer/user mutation.
- `P4-PRVTPRO-REFRESH-003-LIVE`, carried from Phase 4, live probes/actions gated.

## Fresh Installer Grooming

Fresh installer work is now organized under
`docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md`.

Recommended first local-only bundle:

```text
FI-I001 Installer question model hardening
FI-I002 Install plan renderer
FI-I003 Secret handoff checklist binding
```

The destructive/live install path is still gated:

```text
FI-C001 / P6-C007 destructive clean install execution gate
```

It requires a separate exact named destructive phrase, target decision,
retention/data-loss acceptance, stop criteria, package choice, rollback story
and second confirmation.

## Boundary

This closeout did not perform:

- live VPS command;
- SSH command;
- package upload/apply on VPS;
- service restart/deploy;
- public exposure, domain, HTTPS, reverse proxy or firewall change;
- config delivery, `.conf`, QR or `vpn://`;
- write API or `/api/clients` CRUD;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Next Recommendation

Recommended triple:

```text
FI-I001 + FI-I002 + FI-I003
```

Scope: local-only code/tests/docs for the clean installer path.

Pair alternative:

```text
P6-C001 + P6-C002
```

Scope: docs-only decision checklist refresh, without opening public exposure or
config delivery.

Single alternative:

```text
FI-I001
```

Scope: local-only installer question model hardening.
