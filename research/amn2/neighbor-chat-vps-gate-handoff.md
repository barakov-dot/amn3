# Neighbor Chat Handoff Before VPS Gate

Дата: 2026-06-01.

Назначение: синхронизировать соседние чаты `VPN Ops Lab — KYORESUAS-API` и `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel` перед реальным VPS gate.

## Current blocker

Оба соседних направления ждут evidence по ветке:

```text
codex/remote-operation-vps-gate-prep
head: aca6663 Add VPS gate handoff for remote ops
```

Пока нет real VPS evidence, интеграционные write/API решения в main project не начинать.

## Signal needed from VPS gate

Минимальный сигнал:

- Phase 1 read-only/dry-run прошла;
- `apply-peer --dry-run` и `revoke-peer --dry-run` показывают operation metadata;
- dry-run output не содержит PSK/private key/full config/raw command string;
- no state change confirmed.

Сильный сигнал:

- Phase 2 single test peer apply/revoke прошла;
- existing peers не изменились;
- final sync подтверждает cleanup;
- evidence записана в AMN3 без секретов.

## What KYORESUAS-API may do after signal

После `verified-live`:

- проектировать read-only API route shell;
- использовать scoped token baseline `server:read` / `metrics:read`;
- использовать Local Agent runtime metadata alignment из `research/amn2/local-agent-runtime-metadata-alignment.md`;
- не переносить Node/Fastify implementation;
- не открывать `/clients` write lifecycle.

Если только `dry-run-only-pass`:

- можно продолжать read-only route design по уже подготовленной privacy classification;
- нельзя начинать write lifecycle, config delivery API или controller-to-agent mutation.

## What PRVTPRO-Web-Panel may do after signal

После `verified-live`:

- использовать идеи route taxonomy, operator status UX и dangerous-action language;
- проектировать status/read-only views для существующей `amn2` panel;
- не копировать GPL UI/templates/managers/scripts;
- не переносить install/clear/uninstall/raw config editing flows.

Если только `dry-run-only-pass`:

- можно уточнять UX wording и evidence presentation;
- нельзя включать live manager flows или destructive operations.

## Shared no-go list

До отдельного design/implementation gate не начинать:

- public/self-service config links;
- `config:read` API;
- write scopes;
- backup/import/reboot;
- raw config editing;
- server install/clear/uninstall;
- Docker socket exposure;
- broad client CRUD.

## Recommended next after VPS evidence

Первый безопасный integration slice после `verified-live`:

```text
Read-only aggregate metrics/API route shell
```

Privacy classification уже подготовлена в `research/amn2/read-only-metrics-privacy-classification.md`. Первый slice должен использовать aggregate-only default и не включать per-peer/client labels.
