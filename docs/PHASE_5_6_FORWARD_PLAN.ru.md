# AMN2 Phase 5/6 forward plan

Дата: 2026-06-11.

## Когда запускать Phase 5

Phase 5 стоит запускать после закрытия текущих безопасных Phase 4 local-only/product-gate задач и перед любым реальным rollout на VPS.

Минимальные условия входа:

- Phase 4 handoff/status/backlog синхронизированы;
- текущий AMN2 head выбран явно;
- package/source precheck пересобран от выбранного head;
- live/destructive/write/config действия имеют named gate;
- operator retention path для VPS выбран явно;
- секреты передаются только через operator local channel.

Цель Phase 5: controlled pilot / operator-only rollout. Это не публичный продукт и не self-service.

## Phase 5 задачи

### Закрыто до/в начале Phase 5

- `P4-BOT-ONBOARDING-001` Bot onboarding language/header local slice: текущий access bot получил `NEOBYATNAYA-AMNZ-BOT.png`, `/start` language selector, Russian default and English fallback in AMN2 commit `137d471`.
- `P5-I003` Runtime/toolchain standardization: AMN2 commit `578d91e` pins supported local runtime to CPython 3.12.x, adds `python -m app.toolchain check`, documents one `.venv` per worktree and verifies the full local suite with `658 passed, 1 warning`.
- `P5-I002` External-only backfill rehearsal on local DB copy: AMN2 commit `23f18ef` adds `device backfill-external` dry-run/apply-to-copy flow, rejects secret-bearing input fields, keeps imported devices `external_only`, and verifies the full local suite with `662 passed, 1 warning`.
- `P5-I004` Operator-only smoke checklist: created `docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md` with web/admin loopback, bot dry/local, read-only API and no-public-exposure checks; evidence `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.
- `P5-M003` AMN3 evidence discipline: created `docs/AMN3_PHASE5_EVIDENCE_DISCIPLINE.ru.md` with required evidence/status/backlog/active-plan closeout packet; evidence `research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md`.
- `P5-M001` Support/news bot asset inventory: created `docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md` with future support/news bot command, copy, token/runtime, media surface and ownership boundaries; evidence `research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md`.
- `P5-M005` Bot media asset upload/apply boundary: created `docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md` with local upload/registry, profile-icon apply gate, validation, registry and audit boundaries; evidence `research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md`.
- `P5-M004` Граница ассета шапки веб-панели: created `docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md` with web/admin-only placement, public-safe login/header, asset source/license and no-public-exposure boundaries; evidence `research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md`.
- `P5-M002` QA клиентских инструкций доставки конфигурации: created `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md` with safe Telegram `.conf`/QR/`vpn://` Android/iOS/Desktop QA, redacted evidence policy, and the one-tap copy-to-clipboard requirement for the import link; evidence `research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md`.
- `P5-M006` Одно нажатие для копирования import-ссылки в Telegram: AMN2 commit `ad6aa1b` adds a bounded Telegram `Скопировать ссылку` copy button for exact full `vpn://` links that fit Bot API copy-text limits, keeps over-limit raw links on visible-text plus `.conf`/QR fallback, and verifies full local suite with `664 passed, 1 warning`; evidence `research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md`.
- `P5-N002` Полировка текста веб-панели для service-mode и external-only устройств: AMN2 commit `17454e9` clarifies operator-only/service-mode boundary and external-only device wording in web templates, with full local suite `664 passed, 1 warning`; evidence `research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md`.
- `P5-X002` Единообразие bot button labels and captions: AMN2 commit `fed832c` clarifies `.conf`, QR and `vpn://` delivery captions/messages without changing delivery behavior; evidence `research/amn2/phase-5-bot-labels-captions-2026-06-11.md`.
- `P5-X001` Полировка Russian-first микротекстов: AMN2 commit `de25576` makes visible bot/admin and web-panel boundary microtexts Russian-first, with full local suite `664 passed, 1 warning`; evidence `research/amn2/phase-5-russian-first-microtexts-2026-06-11.md`.
- `P5-S002` Удалять устаревшие рекомендации после каждого закрытого slice: AMN3 docs-only cleanup removed stale active-plan/recommendation pointers after `P5-X002`/`P5-X001`; evidence `research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md`.
- `P5-C002` Решение по VPS retention: current server recorded as disposable test VPS with no important project data to preserve; evidence `research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md`.
- `P5-C001` Гейт пересборки пакета от текущего AMN2 head: rebuilt local package/source kit from AMN2 `de25576`, recorded sha256 and hygiene/test-extract as `package-ready-not-vps-smoked`; evidence `research/amn2/phase-5-current-head-package-rebuild-2026-06-12.md`.
- `P5-C003` Named gate live rollout: applied AMN2 `de25576` package to the disposable test VPS, read-only loopback API smoke passed, web/bot services restarted and active after permission repair; evidence `research/amn2/phase-5-live-rollout-de25576-2026-06-12.md`.
- `P5-C004` Secret handoff protocol: created `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md` with operator-local secret transfer policy, safe summary fields, stop lines and related named gates; evidence `research/amn2/phase-5-secret-handoff-protocol-2026-06-12.md`.
- `P5-C005` Source-overlay permission preservation fix: corrected `scripts/vps/amn2_apply_source_zip.sh` so future rebuilt kits preserve target-root metadata and service-readable source permissions; added local regression tests; evidence `research/amn2/phase-5-source-overlay-permission-preservation-2026-06-12.md`.
- `P5-N001` Чистка операторских документов после pilot: removed stale active references to already closed Phase 5 gate slices, refreshed status/context/backlog/next-chat handoff and recorded the remaining plan; evidence `research/amn2/phase-5-operator-docs-cleanup-2026-06-12.md`.
- `P5-N003` Обновление совместимости клиентов/платформ: AMN2 commit `dd0dd44` refreshes AmneziaVPN Linux platform guidance after the 2026-06-12 upstream watcher check; evidence `research/amn2/phase-5-client-platform-compatibility-refresh-2026-06-12.md`.
- `P4-PRVTPRO-REFRESH-003` Read-only server status/latency UX boundary: carried from Phase 4 and closed as AMN3 docs-only design boundary; evidence `research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md`.
- `P5-C006` Current-head package rebuild for AMN2 `dd0dd44`: rebuilt local package/source kit from then-current AMN2 head, tightened operator-kit commit/no-live-apply bindings, verified full AMN2 suite `664 passed, 1 warning`, and recorded package status `package-ready-not-vps-smoked`; evidence `research/amn2/phase-5-current-head-package-rebuild-dd0dd44-2026-06-12.md`. This package is now superseded as current-head package evidence because AMN2 advanced to `9bff807`.
- `P5-L002` Bot media local registry/upload for start/header assets: AMN2 commit `9bff807` adds local-only CLI validation/stage/select/manifest support for access/support/news bot media, with `start_header` runtime selection and `profile_icon` staged-for-operator metadata only; no Telegram API call, token storage, public upload route, live send or profile mutation; evidence `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`.
- `P5-L001` Read-only status/latency display: AMN2 commit `9bff807` adds a private web/admin `Read-only server summary` from cached DB health data only, with secret/user/device/config fields excluded and live checks kept behind a named gate; evidence `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`.
- `P5-C008` Current-head package rebuild for AMN2 `9bff807`: rebuilt local package/source kit from current AMN2 head, verified toolchain on CPython 3.12.13, full AMN2 suite `671 passed, 1 warning`, package hygiene/test-extract and recorded package status `package-ready-not-vps-smoked`; evidence `research/amn2/phase-5-current-head-package-rebuild-9bff807-2026-06-12.md`.
- `P5-S003` Закрытые carried-items без путаницы с активным планом: refreshed AMN3 wording so carried Phase 4 items remain visible as `closed / carried from Phase N / gate remains`, without looking like active pending work; evidence `research/amn2/phase-5-carried-items-active-plan-cleanup-2026-06-12.md`.
- `P5-C007` Named live update/smoke gate for AMN2 `9bff807`: updated the disposable test VPS source overlay from `de25576` to `9bff807`, read-only API smoke passed with run_id `20260612T184701Z`, web/bot services are active after restart and remote listeners remain loopback/closed as expected; evidence `research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md`.
- `P5-O001` Operator-only post-update UI smoke for AMN2 `9bff807`: authenticated GET navigation through the operator SSH local port forward loaded all checked web/admin routes, but decision is `needs-fix` because create/write/config/token controls remain visible during operator-only smoke; evidence `research/amn2/phase-5-operator-post-update-ui-smoke-9bff807-2026-06-12.md`.
- `P5-O002` Web-admin gated-action and Russian-first UX cleanup: AMN2 commit `2215761` makes the operator web/admin brand `AmneziyaDA`, aligns sampled pages Russian-first, centers dashboard count/entity cards and disables create/token/template write affordances with named-gate notes; evidence `research/amn2/phase-5-web-admin-gated-action-russian-ux-2026-06-12.md`.
- `P5-C009` Current-head package rebuild for AMN2 `2215761`: rebuilt local package/source kit from current AMN2 head, verified toolchain on CPython 3.12.13, full AMN2 suite `675 passed, 1 warning`, package hygiene/test-extract and recorded package status `package-ready-not-vps-smoked`; evidence `research/amn2/phase-5-current-head-package-rebuild-2215761-2026-06-13.md`.
- `P5-C010` Named live update/smoke gate for AMN2 `2215761`: updated the disposable test VPS source overlay from `9bff807` to `2215761`, read-only API smoke passed with run_id `20260613T045107Z`, web/bot services are active after restart and remote listeners remain loopback/closed as expected; evidence `research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md`.
- `P5-D001` Operator-only pilot acceptance and Phase 6 entry decision: accepted the current private/operator-only baseline after `P5-C010`, kept Phase 6 as `planning-ready only`, and recorded `P6-C005` Production security review gate as the next recommended local/docs/security step; evidence `research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md`.
- `P5-S001` Keep next-chat handoff current: Phase 5 handoff prepared at `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md`; existing weekly upstream automations were updated to Phase 5 prompts without creating duplicates.

### Неисполненные deferred/gated направления

Эти пункты не выполнены и не считаются частью default work. Их можно исполнять только как отдельные named gates.

- `VPS-REBUILD-001`: `critical destructive`, not executed, defer. Dependencies: explicit destructive phrase, target retention/snapshot decision, stop-criteria review, fresh package choice, secret handoff via operator-local channel, rollback/restore acceptance.
- Write API / `/api/clients` CRUD: `critical gated`, not executed. Dependencies: threat model, scoped write-token policy, fake-runner/local contract, operation queue/idempotency/locking/partial failure model, audit/redaction, rollback semantics, tests, then separate live gate.
- Config delivery: `critical gated`, not executed. Dependencies: secret-bearing artifact policy, tokenized/TTL/revoke model, safe Telegram/self-service UX, redacted evidence, client compatibility QA, explicit delivery gate.
- Public exposure: `critical gated`, not executed. Dependencies: domain/HTTPS/Caddy or reverse-proxy design, auth/session hardening, rate limit, monitoring/log redaction, firewall/listener plan, security review, rollback.
- `P4-PRVTPRO-REFRESH-003` live probes/actions: `normal gated`, carried from Phase 4, not executed. Safe part is closed: AMN3 design boundary and `P5-L001` local cached display. Dependencies for live probes/actions: read-only probe contract, timeout/rate limits, no raw logs/secrets, no sync/apply mutation, separate live probe gate.

### Критичные

Сейчас нет активных default critical задач после закрытия `P5-C004`, `P5-C005`, `P5-C006`, `P5-L002`, `P5-L001`, `P5-C008`, `P5-S003`, `P5-C007`, `P5-O001`, `P5-O002`, `P5-C009`, `P5-C010` и `P5-D001`.

Критичные gated/deferred, не выполнены:

- `VPS-REBUILD-001`: destructive rebuild, deferred.
- Write API / `/api/clients` CRUD: deferred.
- Config delivery: deferred.
- Public exposure: deferred.

### Очень важные

- Сейчас нет активных задач в этой группе после закрытия `P5-I004`.

### Важные

Сейчас нет активных задач в этой группе после закрытия `P5-O002`.

### Нормальные

Сейчас нет активных default normal задач после закрытия `P5-N003`, `P5-L002`, `P5-L001` и safe part of carried-from-Phase-4 `P4-PRVTPRO-REFRESH-003`.

Нормальные gated/deferred, не выполнены:

- `P4-PRVTPRO-REFRESH-003-LIVE` live status/latency probes/actions: separate live probe gate only.

### Простые

Сейчас нет активных задач в этой группе после закрытия `P5-S002` и `P5-S003`.

### Косметические

Сейчас нет активных задач в этой группе после закрытия `P5-X001` и `P5-X002`.

## Когда запускать Phase 6

Phase 6 нужна только если после operator-only pilot мы решаем идти в public/self-service/productization.

Если проект остается private/operator-only через SSH tunnel, Phase 6 можно не открывать.

Минимальные условия входа:

- Phase 5 pilot closed with evidence;
- production peer/user mutation model accepted;
- config delivery policy accepted;
- public exposure decision accepted;
- security review/gate completed;
- rollback and incident plan documented.

## Phase 6 рекомендации

Phase 6 можно открывать только как planning/security/productization lane после закрытого `P5-D001`. Это не открывает public/self-service live work само по себе. Первый шаг Phase 6, `P6-C005` Production security review gate, закрыт как local/docs/security review. Public exposure, config delivery, write API, backup/import/reboot, Local Agent write/config routes and destructive rebuild remain separate named gates.

### Закрыто в Phase 6

- `P6-C005` Production security review gate: completed as AMN3 local/docs/security review with focused AMN2 local security regression suite `98 passed, 1 warning`; evidence `research/amn2/phase-6-production-security-review-gate-2026-06-13.md`. Result: planning can continue, but public/self-service launch remains `no-go` until separate named gates. Follow-up added: `P6-N003` Integration status current-head alignment.
- `P6-I001` Scoped API tokens production implementation: completed as AMN2 local-only code/tests/docs in commit `0b3ac1f Add API token production policy`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md`. Adds a machine-checkable production token policy manifest, keeps allowed scopes to `server:read`/`metrics:read`, records blocked future/config/write/backup/Local Agent scopes, enforces 30-day max TTL for route-connected tokens, aligns the disabled web/admin token form with the same TTL, and updates token policy docs. Verification: focused `18 passed, 1 warning`, expanded `59 passed, 1 warning`, `git diff --check` passed. Latest VPS-smoked/package head remains `2215761`; `0b3ac1f` is not package-rebuilt or VPS-smoked.
- `P6-I002` User self-service surface separated from admin surface: completed as AMN2 local-only code/tests/docs in commit `b676e1b Add self-service surface boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md`. Adds `self-service` as a separate blocked-future surface, records future dashboard/config-delivery/device-revoke policy entries under `/self-service*`, requires separate self-service auth and own-account/device boundaries, and verifies no `/self-service*` route is mounted in the current web/admin app. Verification: RED `4 failed, 23 passed`, focused `27 passed`, expanded `43 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `b676e1b` is not package-rebuilt or VPS-smoked.
- `P6-M001` Multi-server/multi-protocol capability registry + `P6-N003` Integration status current-head alignment: completed together as AMN2 local-only code/tests/docs in commits `4bb7364 Align integration status capability registry` and `3118b43 Make integration status source head dynamic`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md`. Adds a safe capability registry to `/api/integration/status` and web `/integration-status`, records the current implemented capability as single-server operator control for `amneziawg` on Docker, keeps `wireguard` and `xray` protocol managers blocked-future with no upstream/GPL code copy, and separates current branch head from the latest VPS-smoked/package head. Verification: RED `3 failed, 5 passed, 1 warning`, focused `8 passed, 1 warning`, expanded `46 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `3118b43` is not package-rebuilt or VPS-smoked.
- `P6-I003` Payments/manual approval boundary + `P6-I004` Support bot and news bot production split: completed together as AMN2 local-only code/tests/docs in commit `0c6aa7c Add commercial bot productization boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md`. Adds a safe productization manifest, keeps payment processor/webhook/automatic entitlement/config delivery on payment blocked, records manual approval as required, records support/news bots as blocked-future with separate token/runtime requirements, adds blocked-future surface policy entries, and exposes the safe boundary through integration status. Verification: RED `1 error, 1 warning`, focused `29 passed, 1 warning`, expanded `81 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `0c6aa7c` is not package-rebuilt or VPS-smoked.
- `P6-I005` Telegram bot profile/icon apply gates: completed as AMN2 local-only code/tests/docs in commit `19f3422 Add Telegram profile icon gate policy`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md`. Adds a safe profile-icon apply gate manifest for access/support/news bots, keeps Telegram API/profile mutation/live send/token use blocked, adds blocked-future surface policy entries, and exposes the safe gate through integration status. Verification: RED `6 failed, 27 passed, 1 warning`, focused `33 passed, 1 warning`, expanded `83 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `19f3422` is not package-rebuilt or VPS-smoked.
- `P6-M002` Health/status polling scheduler with aggregate-only privacy boundary + `P6-N002` Admin analytics without per-peer/user leakage: completed together as AMN2 local-only code/tests/docs in commit `8f4ac6a Add privacy status analytics boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md`. Adds a machine-checkable aggregate-only health/status and admin analytics boundary, keeps live probes/raw command output/per-peer/per-user details blocked, sanitizes `/api/integration/status` sensitive marker-name lists to counts, adds blocked-future surface policy entries and exposes safe status through web `/integration-status`. Verification: RED `1 error, 1 warning`, focused `33 passed, 1 warning`, expanded `65 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `8f4ac6a` is not package-rebuilt or VPS-smoked.
- `P6-M003` Attach-existing-server reconciliation beyond read-only report mode + `P6-S001` Release checklist and changelog: completed together as AMN2 local-only code/tests/docs in commit `3e1f4cc Add reconciliation release boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md`. Adds a machine-checkable report-only reconciliation/release boundary, keeps live reconciliation, local device creation, peer removal, server config overwrite, package apply/rebuild on VPS, public exposure, config delivery, write API, Local Agent mutation and production peer/user mutation blocked, and exposes safe status through web `/integration-status`. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `81 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `3e1f4cc` is not package-rebuilt or VPS-smoked.
- `P6-S003` Project operating system extraction template: completed as AMN3 docs-only work; evidence `research/amn2/phase-6-project-operating-system-template-2026-06-13.md`. Adds clean reusable templates `docs/templates/PROJECT_OPERATING_SYSTEM_TEMPLATE.ru.md` and `docs/templates/NEXT_PROJECT_BOOTSTRAP.ru.md` so the AMN2/AMN3 project-memory process can be reused for a future project without AMN2-specific details. No AMN2 runtime code changed.
- `P6-N004` Aggregate telemetry retention/redaction policy + `P6-S002` Recurring upstream refresh incorporation: completed together as AMN2 local-only code/tests/docs in commit `a9f53d7 Add telemetry retention refresh policy`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md`. Adds a machine-checkable telemetry retention/redaction and upstream refresh incorporation manifest, keeps raw telemetry export and upstream refresh live actions blocked, records watcher outputs as candidate rows/evidence only, and exposes safe status through web `/integration-status`. Verification: RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `68 passed, 1 warning`, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `2215761`; `a9f53d7` is not package-rebuilt or VPS-smoked.
- `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary + `P6-X001` Public product copy polish + `P6-X002` Brand/media consistency: completed together as AMN2 local-only code/tests/docs in commit `b3102db Add client compatibility delivery boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md`. Adds explicit client roles for iOS DefaultVPN as the primary RF path, iOS AmneziaWG as installed/legacy, and Android AmneziaWG as a separate supported path; aligns Telegram delivery copy, web config-template copy, API/web `/integration-status`, README and setup docs. Verification: RED client/status tests, focused `26 passed, 1 warning`, expanded `290 passed, 1 warning`, `git diff --check` and staged check passed. This head was later package-applied/VPS-smoked by `P6-C006`.
- `P6-C006` Live update/smoke gate for AMN2 `b3102db`: completed as `live-update-smoke-pass`; evidence `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md` and package preflight evidence `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md`. Updated source overlay `/opt/amn2` from `2215761` to `b3102db250da7ca9aef78ca095602187d0efc462`, source update run_id `20260613T154511Z`, read-only API smoke run_id `20260613T154826Z`, web bound to `127.0.0.1:3030`, external probes closed and `VPS_APPLY_ENABLED=false` remained explicit. No config delivery/write/public/destructive/Telegram mutation work was performed.
- `P6-C002-design` short one-tap tokenized config-link boundary + `P6-I006` Commercial entitlement/audit boundary: completed together as AMN2 local-only code/tests/docs in commit `d96112c Add config link entitlement boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-config-link-entitlement-boundary-2026-06-13.md`. Adds tokenized config-link policy with runtime/config delivery disabled, opaque random token, hash-at-rest, one-time 15 minute TTL and Telegram copy constraints; adds entitlement/audit policy with payment provider/write API/automatic activation disabled and manual review required; adds blocked-future route policies for entitlement manual review, config-link issue and public token redeem; updates integration status to latest VPS-smoked head `b3102db` and next local recommendation `P6-I007`. Verification: `37 passed, 1 warning`, `git diff --check` passed. Latest VPS-smoked/package head remains `b3102db`; `d96112c` is local-only and not package-rebuilt/VPS-smoked. `P6-C002` remains critical gated/deferred for real config delivery.
- `P6-I007` Interactive fresh-install wizard/bootstrap automation: completed as AMN2 local-only code/tests/docs in commit `60d2570 Add fresh install wizard boundary`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-fresh-install-wizard-boundary-2026-06-13.md`. Adds a local-only question-and-answer clean installer plan service, `install wizard`/`install plan` CLI commands, docs `docs/FRESH_INSTALL_WIZARD.ru.md` and integration status visibility. Gated `yes` answers become stop-lines for `P6-C001`, `P6-C002`, `P6-C003` and `P6-C007`; no live/destructive action is executed. Verification: RED `2 import errors as expected`, focused `14 passed, 1 warning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `b3102db`; `60d2570` is local-only and not package-rebuilt/VPS-smoked. `P6-C007` remains critical gated/deferred.
- `P6-N001` Public docs/API taxonomy + `P6-C007` checklist-only: completed together as AMN2 local-only code/tests/docs in commit `c46f664 Add public taxonomy cleanup checklist`, pushed to `amn2/codex-vps-test-prep`; evidence `research/amn2/phase-6-public-taxonomy-cleanup-checklist-2026-06-13.md`. Adds a public docs/API taxonomy boundary with publication/public API flags disabled, separates public-safe/operator-only/secret-bearing/write surfaces, adds a destructive cleanup/reinstall checklist with execution flags disabled, and exposes both through API/web integration status. Verification: focused `11 passed, 1 warning`, security/hygiene `26 passed`, toolchain check passed, `git diff --check` and staged check passed. Latest VPS-smoked/package head remains `b3102db`; `c46f664` is local-only and not package-rebuilt/VPS-smoked. `P6-C007` remains critical gated/deferred; only the checklist was completed.
- `P6-C008` Current-head package refresh/preflight for AMN2 `c46f664`: completed as AMN3 local package work with current-head smoke plan and named live gate checklist; evidence `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, package sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`, source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, source sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Verification: package hygiene passed with `kit_entries=5`, `source_entries=337`, `forbidden_source_entries=0`, shell scripts LF/no-BOM and commit bindings present; AMN2 focused suite `11 passed, 1 warning`; AMN2 toolchain check passed; AMN3 apply-script regression `2 tests OK`. Latest VPS-smoked/package head remains `b3102db`; `c46f664` is package-ready locally and not VPS-smoked. Future live update is tracked as `P6-C009` and remains gated/deferred.
- `P6-C009` Live update/smoke gate for AMN2 `c46f664`: completed as `live-update-smoke-pass`; evidence `research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md` and package preflight evidence `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Updated source overlay `/opt/amn2` from `b3102db250da7ca9aef78ca095602187d0efc462` to `c46f664762d7774756b88db8d4e1ebc038b20bb5`, source update run_id `20260613T173232Z`, read-only API smoke run_id `20260613T173738Z`, web bound to `127.0.0.1:3030`, external probes closed and `VPS_APPLY_ENABLED=false` remained explicit. No config delivery/write/public/destructive/Telegram mutation work was performed. Follow-up added: `P6-X003` package runbook escaping hygiene.

### Критичные

- `P6-C001` Public exposure gate: domain/Caddy/HTTPS/public panel/API decision with threat model. Complexity: high. Depends on security review, auth/session hardening, listener/firewall plan, rollback.
- `P6-C002` Config delivery gate: public/self-service delivery, short one-tap tokenized config links, TTL, revoke, audit, redaction. Complexity: high. Depends on secret-bearing artifact policy and client compatibility QA.
- `P6-C003` Write API production gate: `/api/clients` CRUD, operation queue, idempotency, locking, partial failure and rollback. Complexity: very high. Depends on WAPI design tasks and local fake-runner validation.
- `P6-C004` Production backup/restore/import gate: encrypted backups, restore preview/apply, disaster recovery drill. Complexity: high/destructive. Depends on retention policy and restore tests.
- `P6-C007` Destructive cleanup/reinstall gate for current working VPS `89.185.80.166`: checklist-only criteria are documented in `c46f664`; destructive execution remains deferred until the operator explicitly decides to assemble/test the clean installer. Complexity: high/destructive. Depends on separate named destructive gate, explicit retention/data-loss decision, stop criteria and operator acceptance.

Active default critical tasks: none after `P6-C005`. Critical gated/deferred work remains `P6-C001`, `P6-C002`, `P6-C003`, `P6-C004`, `P6-C007`, `VPS-REBUILD-001`, Local Agent write/config routes and production peer/user mutation.

### Очень важные

No active very-important tasks after `P6-I007`.

### Важные

No active important tasks after `P6-M004`.

### Нормальные

No active default normal tasks after `P6-N001`.

### Простые

No active simple tasks after `P6-S003` and `P6-S002`.

### Косметические

- `P6-X003` Package runbook escaping hygiene.
