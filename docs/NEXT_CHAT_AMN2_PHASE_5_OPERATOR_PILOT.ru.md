# Следующий чат: AMN2 Phase 5 Operator-Only Pilot

Дата: 2026-06-11.

Рабочая папка нового чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Краткое пояснение Phase 5: это controlled operator-only pilot после Phase 4 Unified Product Gate. Цель - подготовить и провести безопасный операторский контур запуска AMN2 без public exposure, без write/config/public действий по умолчанию и без live VPS операций вне named gate.

## Источник правды

```text
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
AMN3 remote: https://github.com/barakov-dot/amn3.git
AMN3 branch: master
AMN3 current checkpoint: verify with `git log -1`; latest completed slice is P5-M001 Support/news bot asset inventory

AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 current branch head: 23f18ef Add external-only backfill rehearsal
AMN2 latest VPS-smoked source-overlay/package head remains historical: f7f6131 Update integration status for c92 manual prelaunch
```

GitHub access note:

- local git push to `barakov-dot/amn3` and `barakov-dot/amn2` worked in the previous slice;
- GitHub connector can read both repos, but connector permissions reported `pull=true`, `push=false`;
- `gh` CLI is not installed in this environment, so use local git remotes or GitHub connector depending on task.

## Обязательное чтение в начале нового чата

```text
docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md
docs/PHASE_5_6_FORWARD_PLAN.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md
research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md
research/amn2/phase-4-candidate-registry-2026-06-09.md
```

Historical Phase 4 handoff remains available at:

```text
docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md
```

Use it as history only. Do not reopen Phase 4 default queue unless new evidence requires it.

## Safety Boundary

Allowed by default in Phase 5:

- AMN3 docs/status/backlog/handoff updates;
- AMN2 local-only code/tests/docs/templates;
- local DB-copy rehearsal;
- operator checklist preparation;
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
- copying GPL/upstream code.

Keep `VPS_APPLY_ENABLED=false` until a named gate explicitly changes it.

## Закрыто перед Phase 5

- `P4-DEVICE-SEQUENCE-EXTERNAL-IMPORT`: bot/admin device sequence and local external-only visibility.
- `P4-AMNEZIA-REFRESH-002`: client import compatibility matrix.
- `P4-BOT-ONBOARDING-001`: bot onboarding language/header.
- `P5-I003`: runtime/toolchain standardization, CPython 3.12.x local runtime.
- `P5-I002`: external-only backfill rehearsal on local DB copy.
- `P5-I004`: operator-only smoke checklist, `docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md`.
- `P5-M003`: AMN3 evidence discipline, `docs/AMN3_PHASE5_EVIDENCE_DISCIPLINE.ru.md`.
- `P5-M001`: support/news bot asset inventory, `docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md`.

Latest AMN2 verification:

```text
tests -q
result: 662 passed, 1 warning
```

## Phase 4 Items Carried Into Phase 5

These are not active Phase 4 tasks anymore. They are carried into Phase 5 with explicit priority and gate labels.

### Очень важные

- `P5-I004` Operator-only smoke checklist: carried from Phase 4 and closed as Phase 5 docs-only checklist; evidence `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.

### Нормальные

- `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX: only after a separate design boundary; no implementation yet.

### Критичные, gated

- `VPS-REBUILD-001`: destructive VPS rebuild gate remains `defer`. Do not run VPS commands, wipe, reinstall or package apply until retention path, stop criteria and exact final destructive phrase are accepted.
- `P5-C001` Current-head package rebuild gate: if live/package direction is selected, rebuild from selected current AMN2 head `23f18ef`, rerun source/package precheck, then enter a named gate.
- `P5-C002` VPS retention decision: provider snapshot/backup/retention path must be explicit before destructive action.
- `P5-C003` Live rollout named gate: deploy/restart/smoke only after go/no-go.
- `P5-C004` Secret handoff protocol: operator local channel only for tokens/secrets/server config.

### Blocked Until Separate Gate

- write API / `/api/clients` CRUD;
- config delivery and public/self-service config routes;
- public API/panel/domain/HTTPS exposure;
- backup/import/reboot;
- Local Agent write/config routes;
- production peer/user mutation.

## Действующий Phase 5 План

### Критичные

- `P5-C001` Current-head package rebuild gate.
- `P5-C002` VPS retention decision.
- `P5-C003` Live rollout named gate.
- `P5-C004` Secret handoff protocol.

### Очень важные

- Сейчас нет активных задач в этой группе после закрытия `P5-I004`.

### Важные

- `P5-M002` Client guidance QA.
- `P5-M004` Admin panel header asset boundary.
- `P5-M005` Bot media asset upload/apply boundary.

### Нормальные

- `P5-N001` Operator docs cleanup after pilot.
- `P5-N002` Web panel copy polish for service-mode and external-only devices.
- `P5-N003` Client/platform compatibility refresh after next Amnezia upstream watcher run.
- `P4-PRVTPRO-REFRESH-003` Read-only server status/latency UX design boundary.

### Простые

- `P5-S002` Remove stale recommendations after every closed slice.

### Косметические

- `P5-X001` Russian-first microcopy polish.
- `P5-X002` Bot button labels and captions consistency.

## Automations

Existing heartbeat automations were updated for Phase 5 prompts without creating new automations:

- `amnezia-weekly-upstream-refresh`;
- `prvtpro-weekly-upstream-refresh`;
- `weekly-kyoresuas-upstream-refresh`.

Schedule remains Sunday 10:00. Prompts now reference Phase 5 docs and keep the same negative controls.

Important: because these are heartbeat/thread automations, the Phase 5 chat retargeted `amnezia-weekly-upstream-refresh` to the current thread. The app rejected attaching a second active heartbeat to the same thread, so `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` keep their existing thread bindings unless the operator chooses a separate consolidation policy. Do not create duplicates or cron workarounds by default.

## Сообщение Для Нового Чата

```text
Продолжаем AMN2 проект в новом этапе:

Phase 5 — Operator-Only Pilot.

Рабочая папка:
C:\Users\SooL\Documents\VPS-OPS-LAB

Источник правды:
- AMN3 repo: barakov-dot/amn3, branch master
- AMN2 repo: barakov-dot/amn2, branch codex-vps-test-prep
- AMN2 current head: 23f18ef Add external-only backfill rehearsal
- AMN3 current checkpoint: verify with git log -1; latest completed slice is P5-M001 Support/news bot asset inventory

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md
- docs/PHASE_5_6_FORWARD_PLAN.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- research/amn2/transfer-backlog.md
- research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md
- research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md
- research/amn2/phase-4-candidate-registry-2026-06-09.md

Границы Phase 5:
- это controlled operator-only pilot;
- по умолчанию только local-only/docs/tests/checklists;
- live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation и destructive VPS actions запрещены без отдельного named gate;
- VPS_APPLY_ENABLED=false;
- код GPL/upstream не копируем.

В начале нового чата:
1. Проверь доступ к локальным git remotes AMN3/AMN2 и GitHub connector read access.
2. Проверь существующие automations: amnezia-weekly-upstream-refresh, prvtpro-weekly-upstream-refresh, weekly-kyoresuas-upstream-refresh. Если они все еще привязаны к старому Phase 4 thread, обнови эти же automation IDs на текущий Phase 5 thread, не создавая новые.
3. Выведи действующий план с градацией: критичные, очень важные, важные, нормальные, простые, косметические.
4. То, что пришло из Phase 4, пометь как carried from Phase 4 и укажи важность/gate.

Следующая рекомендация после закрытия `P5-M001`:
P5-M005 Bot media asset upload/apply boundary.

После закрытия каждой задачи:
- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать следующую рекомендацию.
```
