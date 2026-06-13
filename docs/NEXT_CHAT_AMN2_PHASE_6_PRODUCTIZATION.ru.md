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
AMN3 current checkpoint: verify with `git log -1`; latest completed slice is P6-M001 + P6-N003 capability/status alignment

AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 current branch head: 3118b43 Make integration status source head dynamic
AMN2 latest VPS-smoked source-overlay/package head: 2215761 Polish operator web admin UX
AMN2 latest VPS-smoked/package status: live-update-smoke-pass for `2215761`
AMN2 package/smoke status for `3118b43`: not package-rebuilt, not VPS-smoked
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
last_closed: P6-M001 + P6-N003 Capability registry and integration status alignment
next_recommendation: P6-I003 Payments/manual approval boundary if commercial access is enabled
```

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
- `P6-C002` Config delivery gate.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `VPS-REBUILD-001` destructive rebuild.
- Local Agent write/config routes.
- Production peer/user mutation.

### Очень важные

- `P6-I003` Payments/manual approval boundary if commercial access is enabled.
- `P6-I004` Support bot and news bot production split with separate tokens/scopes.
- `P6-I005` Telegram bot profile/icon apply gates for access/support/news bots.

### Важные

- `P6-M002` Health/status polling scheduler with aggregate-only privacy boundary.
- `P6-M003` Attach-existing-server reconciliation beyond read-only report mode.

### Нормальные

- `P6-N001` Public docs/API taxonomy if public docs are approved.
- `P6-N002` Admin analytics without per-peer/user leakage.
- `P4-PRVTPRO-REFRESH-003-LIVE` live probes/actions: carried from Phase 4, still gated, not executed.

### Простые

- `P6-S001` Release checklist and changelog.
- `P6-S002` Recurring upstream refresh incorporation.

### Косметические

- `P6-X001` Public product copy polish.
- `P6-X002` Brand/media consistency across bots, panel and docs.

## Сообщение Для Нового Чата

```text
Продолжаем AMN2 проект в новом этапе:

Phase 6 — Productization Planning.

Рабочая папка:
C:\Users\SooL\Documents\VPS-OPS-LAB

Источник правды:
- AMN3 repo: barakov-dot/amn3, branch master
- AMN2 repo: barakov-dot/amn2, branch codex-vps-test-prep
- AMN2 current head: 3118b43 Make integration status source head dynamic
- AMN2 latest VPS-smoked/package head: 2215761 Polish operator web admin UX
- AMN2 package/smoke status for 3118b43: not package-rebuilt, not VPS-smoked
- AMN3 current checkpoint: verify with git log -1; latest completed slice is P6-M001 + P6-N003 capability/status alignment

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

Границы Phase 6:
- это planning/security/productization lane, не автоматический public launch;
- по умолчанию только local-only/docs/tests/security review;
- live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation, destructive VPS actions и Telegram identity mutations запрещены без отдельного named gate;
- VPS_APPLY_ENABLED=false;
- код GPL/upstream не копируем.

Следующая рекомендация:
P6-I003 Payments/manual approval boundary if commercial access is enabled.

После закрытия каждой задачи:
- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать следующую рекомендацию.
```
