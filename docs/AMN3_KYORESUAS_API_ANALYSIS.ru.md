# AMN3: анализ kyoresuas/amnezia-api

Дата среза: 2026-05-31.

Источник: `https://github.com/kyoresuas/amnezia-api`.

Код не копируем. Этот документ фиксирует только продуктовые идеи, архитектурные
решения, риски и кандидатов для AMN3. Все реализации в AMN3 должны быть
собственными, с нашими tests, policy gates, redaction и production runbooks.

## Проверенные источники

- Repository: `https://github.com/kyoresuas/amnezia-api`
- README EN: `https://github.com/kyoresuas/amnezia-api/blob/main/README_EN.md`
- License: `https://github.com/kyoresuas/amnezia-api/blob/main/LICENSE`
- Clients controller: `https://github.com/kyoresuas/amnezia-api/blob/main/src/controllers/clients.controllers.ts`
- Client handlers: `https://github.com/kyoresuas/amnezia-api/tree/main/src/handlers/clients`
- Client schemas: `https://github.com/kyoresuas/amnezia-api/tree/main/src/schemas/clients`
- Services: `https://github.com/kyoresuas/amnezia-api/tree/main/src/services`
- Server handlers: `https://github.com/kyoresuas/amnezia-api/tree/main/src/handlers/server`

## Короткий вывод

`kyoresuas/amnezia-api` полезен как компактный пример API-first управления
Amnezia-сервером: клиенты, статусы, expiry, QR, server load, backup/import,
reboot и multi-protocol слой. Для AMN3 это хороший источник UX/API идей, но
его не переносим как есть:

- у нас Local Agent должен оставаться localhost-only и gated by VPS smoke;
- write API включается только после read-only smoke;
- `x-api-key` как единый глобальный ключ для нас слишком грубый механизм;
- backup/import/reboot относятся к отдельному high-risk контуру, не к первому
  user/device API slice;
- выдача config/QR должна быть строго отделена от runtime mutation API.

## Лицензия

В репозитории указана MIT license. Это разрешительная лицензия, но в рамках
AMN3 правило жестче: Код не копируем. Разрешено брать идеи, namespacing,
контрактные паттерны и UX-уроки, но реализация, тесты и документация должны
быть нашими.

## Архитектура, которую стоит учесть

Полезная форма разбиения:

- `controllers` описывают HTTP surface;
- `handlers` держат конкретные use cases;
- `services` инкапсулируют работу с AmneziaWG, AmneziaWG 2.0, Xray и server;
- `schemas` задают request/response contracts;
- `types` отделяют доменные модели от transport layer;
- DI container и Fastify setup отделены от бизнес-логики.

Для AMN3 это подтверждает наш текущий курс:

- keep `app.agent.write_contracts` отдельным contract layer;
- не смешивать Local Agent runtime commands с web admin UI;
- держать policy/scopes/audit отдельно от transport handlers;
- расширять protocol registry постепенно: AmneziaWG -> AmneziaWG 2.0 -> Xray.

## Функциональная поверхность

В README и структуре controllers/handlers виден такой публичный API:

- `GET /clients` - список клиентов;
- `POST /clients` - создание клиента;
- `PATCH /clients` - обновление клиента;
- `DELETE /clients` - удаление клиента;
- `GET /server` - информация о сервере;
- `GET /server/load` - нагрузка/метрики;
- backup/import/reboot - отдельные server operations.

Также в дереве есть QR-related handlers/schemas. Для AMN3 это важно разделить:

- mutation API: apply/revoke/disable/enable peer;
- delivery API/UI: config, QR, `vpn://`, email, Telegram;
- diagnostics API: health/runtime/protocols/load;
- destructive/admin API: backup/import/reboot, только в будущий privileged
  contour.

## Auth и security

В README используется `x-api-key`. Для AMN3 это не подходит как финальная модель,
потому что нам нужны:

- отдельные scopes: `agent:health`, `agent:read`, `agent:protocols:read`,
  будущий `agent:clients:write`;
- token owner и token id для audit;
- rotation и revoke;
- запрет raw token в `.env`, logs, docs, issue и chat;
- разные keys для read-only controller и будущего write controller.

Вывод: `x-api-key` можно считать UX-простым примером, но в AMN3 оставляем
hash-only bearer tokens и explicit scopes.

## UX/API идеи для AMN3

Кандидаты, которые стоит адаптировать:

- единая client lifecycle модель: created, active, paused/disabled, expired,
  deleted/revoked;
- explicit expiry date при создании/обновлении клиента;
- status field в ответах, понятный web admin и bot;
- server load endpoint как отдельная diagnostics surface;
- cleanup expired clients как scheduler-задача;
- schemas-first API: каждый endpoint имеет request/response contract;
- Swagger/OpenAPI полезен для controller API, но не для Local Agent public docs
  в production.

## Что берем в AMN3

Критически важные кандидаты:

- normalized Client API vocabulary: `client_id`, `peer_public_key`,
  `expires_at`, `status`, `protocol`;
- future write contracts для `agent:clients:write`;
- dry-run before mutation как обязательный первый шаг;
- server load/metrics как read-only diagnostics после Local Agent smoke;
- lifecycle actions: create/apply, disable, enable, revoke/delete.

Важные кандидаты:

- schema-driven docs for API consumers;
- separate protocol services for AmneziaWG, AmneziaWG 2.0, Xray;
- scheduler cleanup for expired clients;
- typed error responses with safe human-readable details;
- localized/admin-friendly status wording.

Менее важные кандидаты:

- QR endpoint as separate delivery action;
- backup redacted endpoint;
- import/export helpers;
- deploy scripts as operational helpers.

Не переносим как есть:

- single `x-api-key` as full admin auth;
- public backup/import/reboot in the same API contour as users;
- direct public exposure of Local Agent;
- returning full config/QR from mutation endpoints;
- write-enabled defaults.

## Mapping к текущему AMN3 состоянию

Уже сделано локально:

- `app/agent/write_contracts.py` содержит future contracts без FastAPI routes;
- `tests/agent/test_write_contracts.py` проверяет validation, `allowed_ips` и
  redaction PSK;
- `tests/agent/test_policy.py` подтверждает, что `/agent/clients*` write routes
  остаются недоступны до VPS smoke.

Следующий локальный слой без VPS:

- расширить contract docs для typed error response;
- подготовить enum статусов клиента без включения endpoints;
- описать controller-side UX flow: dry-run -> confirmation -> mutation;
- добавить smoke result template, чтобы после VPS было видно go/no-go для
  `agent:clients:write`.

Только после VPS smoke:

- активировать первый write policy slice;
- включать `agent:clients:write` только отдельным token/scope set;
- подключать web admin к dry-run и confirmation;
- проверять rollback и logs на реальном сервере.

## Решение для ближайшего AMN3 write API

Первый write API должен быть уже, чем `kyoresuas/amnezia-api`:

1. `dry-run apply peer` - возвращает redacted plan, не меняет сервер.
2. `apply peer` - только после confirmation и только при `LOCAL_AGENT_WRITE_ENABLED=true`.
3. `revoke peer` - только по known local device/peer, с audit и rollback notes.

Не добавлять backup/import/reboot в первый write slice. Эти операции требуют
отдельного security design и не должны смешиваться с user lifecycle.
