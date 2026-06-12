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
AMN3 current checkpoint: verify with `git log -1`; latest completed slice is P5-N003 client/platform compatibility refresh

AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 current branch head: dd0dd44 Refresh client platform guidance
AMN2 latest VPS-smoked source-overlay/package head: de25576 Polish Russian-first microcopy
AMN2 latest package status: live-rollout-pass-with-permission-repair on disposable test VPS; AMN2 branch has advanced to `dd0dd44` after that package, so rebuild a new kit with the corrected apply script before any future source apply
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
- `P5-M005`: bot media asset upload/apply boundary, `docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md`.
- `P5-M004`: граница ассета шапки веб-панели, `docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md`.
- `P5-M002`: QA клиентских инструкций доставки конфигурации, `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`.
- `P5-M006`: Telegram import link copy affordance, AMN2 commit `ad6aa1b`, evidence `research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md`.
- `P5-N002`: web-panel service-mode/external-only copy polish, AMN2 commit `17454e9`, evidence `research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md`.
- `P5-X002`: bot labels and captions polish, AMN2 commit `fed832c`, evidence `research/amn2/phase-5-bot-labels-captions-2026-06-11.md`.
- `P5-X001`: Russian-first microtexts polish, AMN2 commit `de25576`, evidence `research/amn2/phase-5-russian-first-microtexts-2026-06-11.md`.
- `P5-S002`: active-plan stale recommendation cleanup, evidence `research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md`.
- `P5-C002`: VPS retention decision, current server recorded as disposable test VPS, evidence `research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md`.
- `P5-C001`: current-head package rebuild from AMN2 `de25576`, package-ready-not-vps-smoked, evidence `research/amn2/phase-5-current-head-package-rebuild-2026-06-12.md`.
- `P5-C003`: live rollout for AMN2 `de25576` on disposable test VPS, source overlay and read-only API smoke passed, web/bot active after permission repair, evidence `research/amn2/phase-5-live-rollout-de25576-2026-06-12.md`.
- `P5-C004`: secret handoff protocol, created `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md` with operator-local channel policy, safe summaries and stop lines, evidence `research/amn2/phase-5-secret-handoff-protocol-2026-06-12.md`.
- `P5-C005`: source-overlay permission preservation fix, corrected `scripts/vps/amn2_apply_source_zip.sh`, added local regression tests and documented future package rebuild requirement, evidence `research/amn2/phase-5-source-overlay-permission-preservation-2026-06-12.md`.
- `P5-N001`: operator docs cleanup, removed stale active references to already closed gate slices and refreshed the Phase 5 handoff/status/context/backlog plan; evidence `research/amn2/phase-5-operator-docs-cleanup-2026-06-12.md`.
- `P5-N003`: client/platform compatibility refresh, AMN2 commit `dd0dd44` updates AmneziaVPN Linux platform guidance after the 2026-06-12 upstream watcher check; evidence `research/amn2/phase-5-client-platform-compatibility-refresh-2026-06-12.md`.

Latest AMN2 verification:

```text
tests -q
result: 664 passed, 1 warning
package: dist/amn2-vps-update-and-smoke-kit-de25576.zip
package sha256: B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87
source sha256: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
VPS source update run_id: 20260612T054750Z
VPS API smoke run_id: 20260612T054913Z
VPS result: pass, with permission repair after source overlay
```

Latest AMN3 `P5-C005` verification:

```text
python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v
result: 2 passed
scope: local fake target through Git Bash, no VPS contact
```

Latest AMN3 `P5-C004` verification:

```text
secret_doc_created: yes
raw_secret_values_recorded: no
git diff --check: passed
```

Latest AMN3 `P5-N001` verification:

```text
stale active P5-N001 recommendation scan: passed
closed-gate active wording scan: passed
git diff --check: passed
```

Latest AMN2 `P5-N003` verification:

```text
RED tests/vpn/test_client_compatibility.py: 2 failed, 3 passed
focused tests/vpn/test_client_compatibility.py tests/bot/test_delivery.py: 13 passed
git diff --check: passed
git diff --cached --check: passed
AMN2 remote head: dd0dd442f0f25c1113accdc625dd16a96059eba4
```

## Phase 4 Items Carried Into Phase 5

These are not active Phase 4 tasks anymore. They are carried into Phase 5 with explicit priority and gate labels.

### Очень важные

- `P5-I004` Operator-only smoke checklist: carried from Phase 4 and closed as Phase 5 docs-only checklist; evidence `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.

### Нормальные

- `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX: only after a separate design boundary; no implementation yet.

### Критичные, gated

- `VPS-REBUILD-001`: destructive VPS rebuild gate remains `defer`. Do not run VPS commands, wipe, reinstall or package apply until retention path, stop criteria and exact final destructive phrase are accepted.
- `P5-C001` Current-head package rebuild gate: closed for AMN2 `de25576` as `package-ready-not-vps-smoked`; live apply still requires `P5-C003`.
- `P5-C002` VPS retention decision: closed for current disposable test VPS; no important project data must be preserved, but live/destructive actions still require separate named gate.
- `P5-C003` Live rollout named gate: closed for AMN2 `de25576` on disposable test VPS; read-only API smoke passed, web/bot active, no public exposure.
- `P5-C004` Secret handoff protocol: closed as docs-only protocol; operator local channel only for tokens/secrets/server config.
- `P5-C005` Source-overlay permission preservation fix: closed as local package tooling/test follow-up; future package apply must use a rebuilt kit with the corrected script.

### Blocked Until Separate Gate

- write API / `/api/clients` CRUD;
- config delivery and public/self-service config routes;
- public API/panel/domain/HTTPS exposure;
- backup/import/reboot;
- Local Agent write/config routes;
- production peer/user mutation.

## Действующий Phase 5 План

### Критичные

Сейчас нет активных default critical задач после закрытия `P5-C004` и `P5-C005`. Остаются только carried/gated directions: `VPS-REBUILD-001`, write API/config delivery/public exposure and other separate named gates.

### Очень важные

- Сейчас нет активных задач в этой группе после закрытия `P5-I004`.

### Важные

- Сейчас нет активных задач в этой группе после закрытия `P5-M006`.

### Нормальные

- `P4-PRVTPRO-REFRESH-003` Граница read-only UX server status/latency.

### Простые

Сейчас нет активных задач в этой группе после закрытия `P5-S002`.

### Косметические

Сейчас нет активных задач в этой группе после закрытия `P5-X001` и `P5-X002`.

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
- AMN2 current head: dd0dd44 Refresh client platform guidance
- AMN3 current checkpoint: verify with git log -1; latest completed slice is P5-N003 client/platform compatibility refresh

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

Следующая рекомендация после закрытия `P5-N003`:
P4-PRVTPRO-REFRESH-003 read-only server status/latency UX boundary as docs/design-only first.

После закрытия каждой задачи:
- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать следующую рекомендацию.
```
