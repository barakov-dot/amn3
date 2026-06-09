# Phase 4 P4-X002 API/Status/Gate Naming Cleanup - 2026-06-09

Статус: completed as AMN3 docs-only/local-only terminology cleanup.

AMN3 baseline before this cleanup:

```text
df628e3 Polish Phase 4 operator docs in Russian
```

## Решение

```text
candidate_id: P4-X002
priority: cosmetic
gate: local-only
status: completed-docs-only
AMN2 code changes: none
live VPS commands: none
```

`P4-X002` закрепляет единый словарь для API/status/gate терминов в активных Phase 4 operator docs. Цель - уменьшить путаницу между `service-mode`, `loopback-only`, `SSH tunnel`, `local-only`, `read-only`, `requires VPS gate`, `blocked` и `deferred`.

## Термины

Использовать эти значения в активных handoff/status docs:

- `service-mode`: web/bot работают как сервисы, но это не означает public exposure.
- `loopback-only`: listener доступен только на `127.0.0.1`.
- `SSH tunnel`: единственный operator access path к private web/admin.
- `local-only`: разрешены только локальные docs/tests/templates/code changes без live VPS commands и без runtime mutation.
- `read-only`: разрешено только чтение/навигация/aggregate/status evidence; POST/write/config/sync/apply/revoke не входят.
- `requires VPS gate`: нужен отдельный named gate даже для read-only live sampling.
- `blocked until separate write/config/public gate`: нельзя выполнять в Phase 4 default mode.
- `deferred`: не выбран сейчас; может быть пересмотрен позже, но не дает permission.
- `public exposure`: public API `3040`, direct public web/admin `3030`, domain/Caddy/HTTPS cutover, public docs/metrics exposure.
- `config delivery`: `.conf`, QR, `vpn://`, generated config archives, share/download links and any secret-bearing config output.

## Область

Обновлены AMN3 operator-facing документы:

- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`
- `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- `research/amn2/transfer-backlog.md`

This cleanup preserves technical identifiers, routes, branch names, candidate IDs, gate names and file paths. It does not rename AMN2 API response keys or route names.

## Non-actions

No AMN2 code was changed.

No live VPS command was run.

No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was authorized.

No upstream PRVTPRO/KYORESUAS code, UI, templates, scripts, command strings, Dockerfiles or manager implementations were copied.

## Verification

```text
git diff --check: passed; CRLF normalization warnings only
active next-step stale scan for P4-X002: no matches
unsafe enabled-marker scan on changed files: no matches
terminology/next-slice scan confirms P4-X001 as next default
```

## Результат

`P4-X002` closes API/status/gate terminology cleanup. The next safest local-only item is `P4-X001` OpenAPI/docs grouping polish for the existing read-only routes, unless `P4-I001` is needed first for another private-panel read-only UX evidence pass.
