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
AMN3 current checkpoint: verify with `git log -1`; latest completed slice is P5-C010 live update/smoke for AMN2 2215761

AMN2 remote: https://github.com/barakov-dot/amn2.git
AMN2 branch: codex-vps-test-prep
AMN2 current branch head: 2215761 Polish operator web admin UX
AMN2 latest VPS-smoked source-overlay/package head: 2215761 Polish operator web admin UX
AMN2 latest current-head package status: live-update-smoke-pass for `2215761`
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
- `P4-PRVTPRO-REFRESH-003`: read-only server status/latency UX, carried from Phase 4 and closed in Phase 5. AMN3 design boundary evidence `research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md`; safe local cached display implemented by `P5-L001`; live probes/actions remain gated.
- `P5-C006`: current-head package rebuild for AMN2 `dd0dd44`, package-ready-not-vps-smoked after full local AMN2 suite and package hygiene/test-extract; evidence `research/amn2/phase-5-current-head-package-rebuild-dd0dd44-2026-06-12.md`. Superseded as current-head package evidence by AMN2 `9bff807`; rebuild requirement was satisfied by `P5-C008` and the live path was completed by `P5-C007`.
- `P5-L002`: bot media local registry/upload for start/header assets, AMN2 commit `9bff807`, local-only CLI validation/stage/select/manifest for access/support/news bot media; no Telegram API/token/profile mutation/live send/public upload; evidence `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`.
- `P5-L001`: read-only status/latency display, AMN2 commit `9bff807`, private web/admin `Read-only server summary` from cached DB health data only; no live probe, SSH, health/sync action, config/user/device/peer secret output or public exposure; evidence `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`.
- `P5-C008`: current-head package rebuild for AMN2 `9bff807`, package-ready-not-vps-smoked after CPython 3.12.13 toolchain check, full AMN2 suite and package hygiene/test-extract; evidence `research/amn2/phase-5-current-head-package-rebuild-9bff807-2026-06-12.md`.
- `P5-S003`: carried-items active-plan cleanup, refreshed AMN3 docs so closed carried items remain visible with phase/gate labels but are not listed as active pending work; evidence `research/amn2/phase-5-carried-items-active-plan-cleanup-2026-06-12.md`.
- `P5-C007`: live update/smoke for AMN2 `9bff807`, source overlay on the disposable test VPS passed, read-only API smoke passed with run_id `20260612T184701Z`, web/bot are active after restart, and remote listeners remained loopback/closed as expected; evidence `research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md`.
- `P5-O001`: operator-only post-update UI smoke for AMN2 `9bff807`, authenticated GET navigation through the operator SSH local port forward loaded the checked web/admin routes, but decision is `needs-fix` because create/write/config/token controls remain visible during operator-only smoke; evidence `research/amn2/phase-5-operator-post-update-ui-smoke-9bff807-2026-06-12.md`.
- `P5-O002`: web-admin gated-action and Russian-first UX cleanup, AMN2 commit `2215761`, local-only implementation/test slice that makes the sampled web/admin UI use `AmneziyaDA`, Russian-first headings/navigation, centered two-line dashboard counts and disabled named-gate create/token/template write affordances; evidence `research/amn2/phase-5-web-admin-gated-action-russian-ux-2026-06-12.md`.
- `P5-C009`: current-head package rebuild for AMN2 `2215761`, package-ready-not-vps-smoked after CPython 3.12.13 toolchain check, full AMN2 suite and package hygiene/test-extract; evidence `research/amn2/phase-5-current-head-package-rebuild-2215761-2026-06-13.md`.
- `P5-C010`: live update/smoke for AMN2 `2215761`, source overlay on the disposable test VPS passed, read-only API smoke passed with run_id `20260613T045107Z`, web/bot are active after restart, and remote listeners remained loopback/closed as expected; evidence `research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md`.

Latest AMN2 verification:

```text
focused P5-O002 suite: 4 passed, 1 warning
expanded web regression at 2215761: 90 passed, 1 warning
full AMN2 suite at 2215761: 675 passed, 1 warning
git diff --check: passed
package: dist/amn2-vps-update-and-smoke-kit-2215761.zip
package sha256: 6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44
source zip: dist/amn2-codex-vps-test-prep-2215761-source.zip
source sha256: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
package status: live-update-smoke-pass
latest VPS-smoked source: 2215761, live-update-smoke-pass
```

Latest AMN3 `P5-C009` verification:

```text
initial system python toolchain check: failed on Python 3.14.3 as expected
AMN2 CPython 3.12.13 toolchain check: passed
AMN2 full pytest: 675 passed, 1 warning
AMN2 git diff --check: passed
package hygiene/test-extract: passed
package entries: 5
source files: 275
forbidden source entries: absent
shell scripts LF/no BOM: passed
commit bindings: present
```

Latest AMN3 `P5-C010` verification:

```text
package upload/checksum/extract: passed
source overlay update: passed, run_id 20260613T045004Z
read-only API smoke: passed, run_id 20260613T045107Z
web/bot services after restart: active
loopback /login: 200
remote listener snapshot: 127.0.0.1:3030 only; 3040/80/443 absent
VPS_APPLY_ENABLED: false
```

Latest AMN3 `P5-C008` verification:

```text
initial system python toolchain check: failed on Python 3.14.3 as expected
AMN2 CPython 3.12.13 toolchain check: passed
AMN2 full pytest: 671 passed, 1 warning
AMN2 git diff --check: passed
package hygiene/test-extract: passed
package entries: 5
source files: 274
forbidden source entries: absent
shell scripts LF/no BOM: passed
commit bindings: present
```

Latest AMN3 `P5-C006` verification:

```text
AMN2 toolchain check: passed
AMN2 full pytest: 664 passed, 1 warning
AMN2 git diff --check: passed
package hygiene/test-extract: passed
package entries: 5
source files: 271
forbidden source entries: absent
shell scripts LF/no BOM: passed
commit bindings: present
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

Historical AMN2 `P5-L002`/`P5-L001` verification:

```text
RED P5-L002: missing app.services.bot_media / CLI entrypoints failed as expected
RED P5-L001: server detail lacked Read-only server summary as expected
focused final: 71 passed, 1 warning
full final: 671 passed, 1 warning
AMN2 remote head: 9bff807 Add local bot media and status summaries
```

Latest AMN3 `P4-PRVTPRO-REFRESH-003` verification:

```text
design_boundary_doc_created: yes
upstream_code_copied: no
stale active P4-PRVTPRO-REFRESH-003 scan: passed
git diff --check: passed
```

## Phase 4 Items Carried Into Phase 5

These are not active Phase 4 tasks anymore. They are carried into Phase 5 with explicit priority and gate labels.

### Очень важные

- `P5-I004` Operator-only smoke checklist: carried from Phase 4 and closed as Phase 5 docs-only checklist; evidence `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.

### Нормальные

- `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX: carried from Phase 4; design boundary closed, and local-only cached status display was implemented by `P5-L001` in AMN2 `9bff807`. Live probes/actions remain gated.

### Критичные, gated

- `VPS-REBUILD-001`: destructive VPS rebuild gate remains `defer`. Do not run VPS commands, wipe, reinstall or package apply until retention path, stop criteria and exact final destructive phrase are accepted.
- `P5-C001` Current-head package rebuild gate: closed for AMN2 `de25576` as `package-ready-not-vps-smoked`; live apply still requires `P5-C003`.
- `P5-C002` VPS retention decision: closed for current disposable test VPS; no important project data must be preserved, but live/destructive actions still require separate named gate.
- `P5-C003` Live rollout named gate: closed for AMN2 `de25576` on disposable test VPS; read-only API smoke passed, web/bot active, no public exposure.
- `P5-C004` Secret handoff protocol: closed as docs-only protocol; operator local channel only for tokens/secrets/server config.
- `P5-C005` Source-overlay permission preservation fix: closed as local package tooling/test follow-up; future package apply must use a rebuilt kit with the corrected script.
- `P5-C006` Current-head package rebuild: closed for AMN2 `dd0dd44` as `package-ready-not-vps-smoked`, then superseded as current-head package evidence by AMN2 `9bff807`; the rebuild requirement was satisfied by `P5-C008`.
- `P5-C008` Current-head package rebuild: closed for AMN2 `9bff807` as `package-ready-not-vps-smoked`; its live update/smoke recommendation was completed by `P5-C007`.
- `P5-C007` Named live update/smoke: closed for AMN2 `9bff807` as `live-update-smoke-pass`; no config delivery, write API, public exposure change, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive provider action was performed.
- `P5-C010` Named live update/smoke: closed for AMN2 `2215761` as `live-update-smoke-pass`; no config delivery, write API, public exposure change, Local Agent mutation, backup/import/reboot, production peer/user mutation or destructive provider action was performed.

### Blocked Until Separate Gate

- write API / `/api/clients` CRUD;
- config delivery and public/self-service config routes;
- public API/panel/domain/HTTPS exposure;
- backup/import/reboot;
- Local Agent write/config routes;
- production peer/user mutation.

## Действующий Phase 5 План

### Критичные

Сейчас нет активных default critical задач после закрытия `P5-C004`, `P5-C005`, `P5-C006`, `P5-L002`, `P5-L001`, `P5-C008`, `P5-S003`, `P5-C007`, `P5-O001`, `P5-O002`, `P5-C009` и `P5-C010`.

Критичные deferred/gated, не исполнены:

- `VPS-REBUILD-001`: destructive rebuild, not executed, defer.
- Write API / `/api/clients` CRUD: not executed, deferred.
- Config delivery: not executed, deferred.
- Public exposure: not executed, deferred.

### Очень важные

- Сейчас нет активных задач в этой группе после закрытия `P5-I004`.

### Важные

Сейчас нет активных задач в этой группе после закрытия `P5-O002`.

### Нормальные

Сейчас нет активных default normal задач после закрытия `P5-L002`, `P5-L001` и safe part of carried-from-Phase-4 `P4-PRVTPRO-REFRESH-003`.

Нормальные deferred/gated, не исполнены:

- `P4-PRVTPRO-REFRESH-003-LIVE`: live probes/actions not executed; safe design boundary and local cached display are closed.

### Простые

Сейчас нет активных задач в этой группе после закрытия `P5-S002` и `P5-S003`.

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
- AMN2 current head: 2215761 Polish operator web admin UX
- AMN2 latest VPS-smoked/package head: 2215761 Polish operator web admin UX
- AMN3 current checkpoint: verify with git log -1; latest completed slice is P5-C010 live update/smoke for AMN2 2215761

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

Следующая рекомендация после закрытия `P5-C010`:
`P5-D001` Operator-only pilot acceptance and Phase 6 entry decision.

После закрытия каждой задачи:
- удалять ее из активного плана;
- выводить полный оставшийся план без нее;
- давать следующую рекомендацию.
```
