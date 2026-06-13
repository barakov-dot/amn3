# Следующий чат: AMN2 Phase 6 Productization Planning

Дата: 2026-06-13.

Рабочая папка нового чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Краткое пояснение Phase 6: это planning/security/productization lane после принятого Phase 5 operator-only pilot. Phase 6 не означает автоматический public launch. Public exposure, config delivery, write API, backup/import/reboot, Local Agent write/config routes, destructive rebuild and production peer/user mutation remain separate named gates.

## Источник правды

```text
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 remote: https://github.com/barakov-dot/amn3.git
AMN3 branch: master
AMN3 current checkpoint: verify with `git log -1`; latest completed slice is P6-M004 + P6-X001 + P6-X002 client compatibility/copy boundary

AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 current branch head: b3102db Add client compatibility delivery boundary
AMN2 latest VPS-smoked source-overlay/package head: b3102db Add client compatibility delivery boundary
AMN2 latest VPS-smoked/package status: live-update-smoke-pass for `b3102db`
AMN2 package/smoke evidence for `b3102db`: `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md` and `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md`
```

## Обязательное чтение в начале нового чата

```text
docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
docs/PHASE_5_6_FORWARD_PLAN.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md
research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md
research/amn2/phase-6-production-security-review-gate-2026-06-13.md
research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md
research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md
research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md
research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md
research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md
research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md
research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md
research/amn2/phase-6-project-operating-system-template-2026-06-13.md
research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md
research/amn2/phase-6-ios-amneziawg-field-diagnostic-2026-06-13.md
research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md
research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md
research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md
```

Historical Phase 5 handoff remains available at:

```text
docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md
```

Use it as history and safety context. Do not reopen Phase 5 default work unless new evidence requires it.

## Current Decision

```text
decision: operator-only-pilot-accepted
current_mode: private/operator-only
Phase_5_default_queue: empty
Phase_6_entry: planning-ready only
Phase_6_live_public_self_service: not opened
last_closed: P6-C006 live update/smoke for b3102db
next_recommendation: P6-C002 + P6-I006 as local-only design/implementation for short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary
new_active_idea: P6-I007 interactive fresh-install wizard/bootstrap automation; P6-C007 destructive VPS cleanup/reinstall gate deferred until the operator explicitly decides to assemble/test the clean installer
```

Standing planning rule: if a new useful Phase 6 idea appears during task
execution, add it to the active plan under the existing priority scale and state
which priority bucket it was added to. This rule added `P6-N004` to normal
priority, `P6-M004` to important priority, `P6-C006` to critical
gated/deferred priority, `P6-I007` to very important priority and `P6-C007` to
critical gated/deferred priority.

## Safety Boundary

Allowed by default in Phase 6 planning:

- AMN3 docs/status/backlog/handoff updates;
- AMN2 local-only code/tests/docs/templates;
- security review, threat model and policy work;
- local fake-runner contracts and tests;
- read-only planning and safe summaries;
- GitHub read/write through existing local git workflow.

Not allowed without separate named gate:

- live VPS commands;
- SSH commands against target VPS;
- package apply/rebuild on VPS;
- service restart/deploy;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS/domain public cutover;
- config delivery, `.conf`, QR, `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS actions;
- Telegram token use, live bot send or profile mutation;
- copying GPL/upstream code.

Keep `VPS_APPLY_ENABLED=false` until a named gate explicitly changes it.

## Phase 6 Active Plan

### Критичные

No active default critical tasks after `P6-C005`.

Critical gated/deferred, not executed:

- `P6-C001` Public exposure gate.
- `P6-C002` Config delivery gate. This also includes short one-tap tokenized
  config links if product wants Telegram copy UX that always works for long
  configs.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `P6-C007` Destructive cleanup/reinstall gate for the current working VPS:
  carried from Phase 6 operator proposal, deferred until the operator
  explicitly decides to assemble/test the clean installer. It may only run
  after a separate named destructive gate, explicit retention decision, stop
  criteria and operator acceptance of data loss. Target server currently in
  use: operator-provided `89.185.80.166`.
- `VPS-REBUILD-001` destructive rebuild.
- Local Agent write/config routes.
- Production peer/user mutation.

### Очень важные

- `P6-I007` Interactive fresh-install wizard/bootstrap automation: local-only
  code/docs/tests to design a question-and-answer installer for a clean future
  deployment. It must support operator-provided secrets, safe defaults,
  preflight validation, dry-run output and no destructive/live execution by
  default.

Proposed, not active until accepted:

- `P6-I006` Commercial entitlement/audit boundary before any payment provider integration.

### Важные

No active important tasks after `P6-M004`.

### Нормальные

- `P6-N001` Public docs/API taxonomy if public docs are approved.
- `P4-PRVTPRO-REFRESH-003-LIVE` live probes/actions: carried from Phase 4, still gated, not executed.

### Простые

No active simple tasks after `P6-S003` and `P6-S002`.

### Косметические

No active cosmetic tasks after `P6-X001` and `P6-X002`.

## Сообщение Для Нового Чата

```text
Продолжаем AMN2 проект в новом этапе:

Phase 6 — Productization Planning.

Рабочая папка:
C:\Users\SooL\Documents\VPS-OPS-LAB

Источник правды:
- AMN3 repo: barakov-dot/amn3, branch master
- AMN2 repo: barakov-dot/amn2, branch codex-vps-test-prep
- AMN2 current head: b3102db Add client compatibility delivery boundary
- AMN2 latest VPS-smoked/package head: b3102db Add client compatibility delivery boundary
- AMN2 package/smoke status for b3102db: live-update-smoke-pass; evidence research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md
- AMN3 current checkpoint: verify with git log -1; latest completed slice is P6-M004 + P6-X001 + P6-X002 client compatibility/copy boundary

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md
- docs/PHASE_5_6_FORWARD_PLAN.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- research/amn2/transfer-backlog.md
- research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md
- research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md
- research/amn2/phase-6-production-security-review-gate-2026-06-13.md
- research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md
- research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md
- research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md
- research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md
- research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md
- research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md
- research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md
- research/amn2/phase-6-project-operating-system-template-2026-06-13.md
- research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md
- research/amn2/phase-6-ios-amneziawg-field-diagnostic-2026-06-13.md
- research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md
- research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md
- research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md

Границы Phase 6:
- это planning/security/productization lane, не автоматический public launch;
- по умолчанию только local-only/docs/tests/security review;
- live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation, destructive VPS actions и Telegram identity mutations запрещены без отдельного named gate;
- VPS_APPLY_ENABLED=false;
- код GPL/upstream не копируем.

Следующая рекомендация:
P6-C002 + P6-I006 как local-only design/implementation: short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary, без открытия config delivery/public/write/payment/live gates.

Постоянное правило:
если в ходе выполнения задач появляется новая полезная мысль, добавлять ее в план по текущей шкале приоритетов и сразу сообщать, в какой раздел она добавлена.

После закрытия каждой задачи:
- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать следующую рекомендацию.
```
