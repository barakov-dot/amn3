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

### Критичные

- `P5-C001` Current-head package rebuild gate: пересобрать package от выбранного AMN2 head, rerun source/package precheck, записать sha256 и stop criteria.
- `P5-C002` VPS retention decision: snapshot/backup/reinstall path должен быть выбран до любого wipe/package apply.
- `P5-C003` Live rollout named gate: отдельный go/no-go для deploy/restart/smoke, без public API/panel.
- `P5-C004` Secret handoff protocol: операторский локальный канал для Telegram token, web secret, server config and bootstrap values.

### Очень важные

- `P5-I002` External-only backfill rehearsal on local DB copy: проверить импорт старых test configs without config material resurrection.
- `P5-I004` Operator-only smoke checklist: web/admin loopback, bot dry/local behavior, read-only API routes, no public exposure.

### Важные

- `P5-M001` Support/news bot asset inventory: собрать тексты, команды and ownership boundary для будущих отдельных ботов; supplied planning assets are `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png` and `NEOBYATNAYA-AMNZ-NEWS-BOT.png`.
- `P5-M002` Client guidance QA: проверить Telegram delivery text on Android/iOS/Desktop screenshots without publishing real secrets.
- `P5-M003` AMN3 evidence discipline: каждый live/local step получает evidence file, status/backlog update and active-plan cleanup.
- `P5-M004` Admin panel header asset boundary: рассмотреть `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` только как отдельный web/admin design slice, не как asset текущего access bot.

### Нормальные

- `P5-N001` Operator docs cleanup after pilot.
- `P5-N002` Web panel copy polish for service-mode and external-only devices.
- `P5-N003` Client/platform compatibility refresh after next Amnezia upstream watcher run.

### Простые

- `P5-S001` Keep next-chat handoff current.
- `P5-S002` Remove stale recommendations after every closed slice.

### Косметические

- `P5-X001` Russian-first microcopy polish.
- `P5-X002` Bot button labels and captions consistency.

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
