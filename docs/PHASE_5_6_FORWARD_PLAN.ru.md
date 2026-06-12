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
- `P5-S001` Keep next-chat handoff current: Phase 5 handoff prepared at `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md`; existing weekly upstream automations were updated to Phase 5 prompts without creating duplicates.

### Перенесено из Phase 4 как условные направления Phase 5

- `P4-PRVTPRO-REFRESH-003` Read-only server status/latency UX: `normal`, only after design boundary.
- Write API / config delivery / public exposure: `critical gated`, blocked until separate named gates.
- `VPS-REBUILD-001`: `critical destructive gate`, remains `defer`; not Phase 5 default work.

### Критичные

- `P5-C004` Протокол передачи секретов: операторский локальный канал для Telegram token, web secret, server config and bootstrap values.
- `P5-C005` Source-overlay permission preservation fix: local package tooling/runbook fix before any future package rebuild/apply.

### Очень важные

- Сейчас нет активных задач в этой группе после закрытия `P5-I004`.

### Важные

- Сейчас нет активных задач в этой группе после закрытия `P5-M006`.

### Нормальные

- `P5-N001` Чистка операторских документов после pilot.
- `P5-N003` Обновление совместимости клиентов/платформ после следующего Amnezia upstream watcher run.

### Простые

Сейчас нет активных задач в этой группе после закрытия `P5-S002`.

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

## Phase 6 задачи

### Критичные

- `P6-C001` Public exposure gate: domain/Caddy/HTTPS/public panel/API решение с threat model.
- `P6-C002` Config delivery gate: public/self-service delivery, tokenized links, TTL, revoke, audit, redaction.
- `P6-C003` Write API production gate: `/api/clients` CRUD, operation queue, idempotency, locking, partial failure and rollback.
- `P6-C004` Production backup/restore/import gate: encrypted backups, restore preview/apply, disaster recovery drill.

### Очень важные

- `P6-I001` Scoped API tokens production implementation.
- `P6-I002` User self-service surface separated from admin surface.
- `P6-I003` Payments/manual approval boundary if commercial access is enabled.
- `P6-I004` Support bot and news bot production split with separate tokens/scopes; current planning assets: `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png`, `NEOBYATNAYA-AMNZ-NEWS-BOT.png`.

### Важные

- `P6-M001` Multi-server/multi-protocol capability registry.
- `P6-M002` Health/status polling scheduler with aggregate-only privacy boundary.
- `P6-M003` Attach-existing-server reconciliation beyond read-only report mode.

### Нормальные

- `P6-N001` Public docs/API taxonomy if public docs are approved.
- `P6-N002` Admin analytics without per-peer/user leakage.

### Простые

- `P6-S001` Release checklist and changelog.
- `P6-S002` Recurring upstream refresh incorporation.

### Косметические

- `P6-X001` Public product copy polish.
- `P6-X002` Brand/media consistency across bots, panel and docs.
