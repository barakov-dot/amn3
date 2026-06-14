# Следующий чат: AMN2 Phase 7 Release Candidate Readiness

Дата: 2026-06-14.

## Phase 7 Name And Status

```text
Phase 7: Release Candidate Readiness / Clean Installer RC
status: pre-release / release-candidate readiness
default_mode: local-only/docs/tests/security/package-preflight
public_launch: not opened
production_mutation: not opened
known_good_vps_head: 0de7a77 Polish fresh installer preflight planning
current_local_amn2_head: b121865 Add multi instance conflict model
```

Phase 7 is not a public launch. It is the pre-release lane for turning the
operator-only AMN2 baseline into a clean, repeatable release-candidate package
and installer path.

## Рабочая папка

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Source Of Truth

```text
AMN3 repo: barakov-dot/amn3
AMN3 branch: master
AMN3 checkpoint: verify with git log -1; Phase 7 transition packet should be latest

AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 current head: b121865 Add multi instance conflict model
AMN2 latest VPS-smoked head: 0de7a77 Polish fresh installer preflight planning
AMN2 latest package-ready head: 0de7a77 Polish fresh installer preflight planning
AMN2 package status: VPS-smoked/pass for 0de7a77
AMN2 smoke status: live-update-smoke-pass for 0de7a77
Current disposable VPS: 89.185.80.166
```

## Read First

```text
docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md
docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md
docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md
research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md
research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md
research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md
docs/AMN2_AUTOMATION_INTAKE_AGGREGATION_PLAN.ru.md
```

## Message To Start The New Chat

```text
Продолжаем AMN2 в Phase 7.

Phase 7 name/status:
- Phase 7: Release Candidate Readiness / Clean Installer RC.
- Status: pre-release / release-candidate readiness.
- Это не public launch и не production mutation lane.
- По умолчанию только local-only/docs/tests/security/package-preflight.

Рабочая папка:
C:\Users\SooL\Documents\VPS-OPS-LAB

Источник правды:
- AMN3 repo: barakov-dot/amn3, branch master.
- AMN2 repo: barakov-dot/amn2, branch codex-vps-test-prep.
- AMN2 current local head: b121865 Add multi instance conflict model.
- AMN2 latest VPS-smoked/package head: 0de7a77 Polish fresh installer preflight planning.
- Current disposable VPS: 89.185.80.166.
- Known-good VPS evidence: research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md
- docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md
- docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
- docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- research/amn2/transfer-backlog.md
- research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md
- research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
- docs/AMN2_AUTOMATION_INTAKE_AGGREGATION_PLAN.ru.md

Границы Phase 7:
- default lane: local-only/docs/tests/security/package-preflight;
- live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation, destructive VPS actions and Telegram identity/profile/media mutations are forbidden without a separate exact named gate;
- VPS_APPLY_ENABLED=false by default;
- do not copy GPL/upstream code, templates, UI, scripts, workflows or manager implementations;
- do not rewrite already-smoked package evidence for 0de7a77;
- b121865 is local-only and not package-rebuilt or VPS-smoked.

Phase 7 goal:
Prepare a release-candidate quality clean installer and package path from current AMN2 work, while preserving the known-good 0de7a77 VPS state.

Access policy:
- No VPS/SSH/PowerShell access is needed for default Phase 7 planning.
- If a live gate is chosen later, ask the operator for an exact named gate phrase and use the existing PowerShell SSH flow for passwords.

Start by verifying:
1. AMN3 git status/log.
2. AMN2 git status/log.
3. GitHub connector read access if needed.
4. Automation prompts are Phase 7 aware:
   - prvtpro-weekly-upstream-refresh
   - weekly-kyoresuas-upstream-refresh
   - amnezia-weekly-upstream-refresh

Then print the Phase 7 plan by priority:
critical gated/deferred, very important, important, normal, simple, cosmetic, watch-only.
Every carried item must include carried-from phase, importance and gate.

Current recommended first step:
P7-I001 + P7-M001 together as local-only package/test readiness:
- build a local package/preflight plan for b121865;
- do not apply to VPS;
- do not restart services;
- keep 0de7a77 as known-good.
```

## Access Request Policy

Default Phase 7 work needs no additional access.

Ask the operator for access only when a task explicitly requires it:

- live package/apply/smoke on VPS `89.185.80.166`;
- SSH/PowerShell password entry;
- provider console action;
- Telegram token/API/profile mutation;
- public DNS/domain/reverse proxy/TLS setup;
- payment provider or production bot credentials.

For live VPS work, require a phrase like:

```text
Открываю P7-C001 live package/apply/smoke gate для <commit> на текущем disposable VPS 89.185.80.166.
```

For destructive clean install/reinstall, require a separate destructive phrase:

```text
Открываю P7-C004 destructive clean installer execution gate для disposable VPS 89.185.80.166.
```

## Remaining Gates Carried Into Phase 7

- `P6-C001` -> `P7-C002` public exposure gate, critical gated, carried from Phase 6.
- `P6-C002` -> `P7-C003` config delivery gate, critical gated, carried from Phase 6.
- `P6-C003` -> `P7-C005` write API/install mutation gate, critical gated, carried from Phase 6.
- `P6-C004` -> `P7-C006` backup/restore/import gate, critical gated, carried from Phase 6.
- `P6-C007` and `VPS-REBUILD-001` -> `P7-C004` destructive clean installer execution gate, critical gated, carried from Phase 6 / earlier phases.
- Local Agent write/config routes -> `P7-C005`, critical gated, carried from Phase 6.
- Production peer/user mutation -> `P7-C005`, critical gated, carried from Phase 6.
- Telegram identity/profile/media mutation -> `P7-C007`, critical gated, carried from Phase 6.

## Default Recommendation Rhythm

After every completed task:

- remove it from the active plan;
- print the full remaining plan without it;
- give next-step options as single, pair and triple bundles;
- include gates and importance;
- immediately propose any new Phase 7 candidate discovered during work, but do
  not add it as active without operator acknowledgement.
