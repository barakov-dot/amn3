# Phase 5 Web/Admin Header Asset Boundary 2026-06-11

Дата: 2026-06-11.

## Итог

`P5-M004` закрыт как AMN3 docs-only/local-only design-boundary slice.

Русское название задачи:

```text
P5-M004 Граница ассета шапки веб-панели
```

Created boundary doc:

```text
docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md
```

## Что зафиксировано

- `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` belongs to the web/admin product surface,
  not to current access bot, future support/news bot or Telegram profile icon.
- Current Phase 5 web/admin mode remains operator-only: loopback
  `127.0.0.1:3030`, SSH local port forward, no direct public `3030`, no public
  API `3040`, no public domain/Caddy/HTTPS cutover by default.
- The admin-panel asset filename is a planning input. The actual file source,
  license, SHA-256 and operator intent must be confirmed before any AMN2 copy.
- Future implementation should choose one first placement only: login header,
  admin navigation brand or dashboard header.
- The asset must stay public-safe if shown on the unauthenticated login page and
  must not contain endpoints, QR codes, `.conf`, `vpn://`, private keys, PSK,
  server config, operational state or user identifiers.
- Russian-first task naming is now preferred in active Russian plans while
  technical IDs remain stable.

## Safety

No AMN2 runtime code was changed. No asset was copied into AMN2. No upload
handler, static route, template change, web/admin runtime change, public
exposure, live VPS command, SSH command, service restart, deploy, package
apply/rebuild on VPS, production peer/user mutation, `/api/clients` CRUD,
config delivery, Local Agent mutation, backup/import/reboot, destructive
provider action or upstream/GPL code copy was performed.

This slice does not authorize a web/admin UI implementation. It only defines
where the planning asset belongs and what must be checked before any local
implementation.

## Active Plan Update

Removed from active Phase 5 plan:

```text
P5-M004 Граница ассета шапки веб-панели
```

Remaining gated items stay gated:

```text
P5-C001 Гейт пересборки пакета от текущего AMN2 head
P5-C002 Решение по VPS retention
P5-C003 Named gate live rollout
P5-C004 Протокол передачи секретов
VPS-REBUILD-001 destructive gate remains defer
```

## Следующая рекомендация

The original follow-up, `P5-M002` QA клиентских инструкций доставки
конфигурации, was completed later in
`research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md`.

Current next safe local-only recommendation: `P5-M006` Одно нажатие для
копирования import-ссылки в Telegram.

Rationale: after bot/admin media planning assets are scoped, the remaining
important local-only task is to review Android/iOS/Desktop client guidance text
and screenshots without publishing real secrets.
