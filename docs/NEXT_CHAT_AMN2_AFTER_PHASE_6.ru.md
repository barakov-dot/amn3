# Следующий чат: AMN2 after Phase 6

Дата: 2026-06-13.

Рабочая папка:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Source Of Truth

```text
AMN3 repo: barakov-dot/amn3
AMN3 branch: master
AMN3 checkpoint: verify with git log -1; latest completed slice is FI-M001 + FI-M002 + FI-M003 fresh installer readiness planning

AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 current head: 7416fb0 Add fresh installer readiness planning
AMN2 latest VPS-smoked/package head: c46f664 Add public taxonomy cleanup checklist
AMN2 package/smoke status: live-update-smoke-pass for c46f664
AMN2 local-only after-smoke head: 7416fb0, not package-rebuilt/VPS-smoked
```

## Read First

```text
docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
docs/PHASE_5_6_FORWARD_PLAN.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-plan-renderer-2026-06-13.md
research/amn2/after-phase-6-fresh-installer-readiness-planning-2026-06-13.md
research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md
research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md
```

## Current Decision

```text
decision: Phase 6 default lane closed
current_mode: private/operator-only
public_self_service_launch: not opened
latest_vps_smoked_head: c46f664
default_local_queue: empty
next_recommendation: FI-N001 + FI-N002 + FI-S001 as local-only docs/test evidence readiness, or P6-C001 + P6-C002 as docs-only gate decision refresh
```

Phase 6 produced planning/security/productization boundaries and confirmed the
current disposable VPS source overlay at `c46f664` through read-only loopback
smoke. It did not open public launch, config delivery, write API, destructive
rebuild, backup/import/reboot, Local Agent mutations, production peer/user
mutation or Telegram identity mutation.

After Phase 6, `FI-I001 + FI-I002 + FI-I003` were completed in AMN2 commit
`de635a0 Add fresh installer plan renderer` as local-only code/tests/docs. This
added versioned installer question/answer schemas, a rendered plan, secret
handoff protocol binding and the canonical `scripts/test.ps1` Windows/Codex
test wrapper. This head is not package-rebuilt or VPS-smoked.

After that, `FI-M001 + FI-M002 + FI-M003` were completed in AMN2 commit
`7416fb0 Add fresh installer readiness planning` as local-only code/tests/docs.
This added `fresh-install-readiness.v1`, target preflight matrix, runtime mode
decision and package hygiene checklist. This head is not package-rebuilt or
VPS-smoked.

## Safety Boundary

Allowed by default:

- AMN3 docs/status/backlog/handoff updates;
- AMN2 local-only code/tests/docs/templates;
- local fake-runner contracts;
- security review and policy work;
- package planning and local hygiene checks without altering sealed evidence
  packages.

Not allowed without separate named gate:

- live VPS commands or SSH;
- package upload/apply on VPS;
- service restart/deploy;
- public API `3040`, direct public web/admin `3030`, domain/HTTPS/reverse
  proxy/firewall changes;
- config delivery, `.conf`, QR, `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or profile/identity mutation;
- upstream/GPL implementation copy.

Keep `VPS_APPLY_ENABLED=false` unless a future named gate explicitly changes it.

## Remaining Plan

### Critical gated/deferred

- `P6-C001` Public exposure gate.
- `P6-C002` Config delivery gate.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `P6-C007` Destructive cleanup/reinstall gate.
- `VPS-REBUILD-001`, carried from earlier phases, gated/deferred.
- Local Agent write/config routes.
- Production peer/user mutation.

### Normal gated/deferred

- `P4-PRVTPRO-REFRESH-003-LIVE`, carried from Phase 4, live probes/actions
  still gated.

### Fresh installer candidates

Use `docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md`. Candidates are not active by
default. Completed after Phase 6:

```text
FI-I001 Installer question model hardening
FI-I002 Install plan renderer
FI-I003 Secret handoff checklist binding
FI-M001 Target OS/runtime preflight matrix
FI-M002 Runtime mode decision
FI-M003 Package hygiene integration
```

The recommended local-only next bundle is:

```text
FI-N001 Smoke/evidence template
FI-N002 Existing-server reconciliation input
FI-S001 Installer docs index
```

## Suggested Next Steps

Recommended triple:

```text
FI-N001 + FI-N002 + FI-S001 as local-only docs/test evidence readiness for the clean installer path.
```

Pair alternative:

```text
P6-C001 + P6-C002 decision checklist refresh as docs-only, without opening public exposure or config delivery.
```

Single alternative:

```text
FI-N001 smoke/evidence template as local-only docs/tests/code.
```

Do not run live/destructive work unless the operator gives a separate exact
named gate phrase.
