# `amn2` Transfer Backlog

Дата: 2026-05-31.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Verified Production Baseline

Актуальный `amn2` baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Live VPS cycle подтвержден на Docker AmneziaWG runtime:

- approve создает рабочий peer;
- config работает;
- `Working configs on server` обновляется сразу;
- `Run peer sync` подтверждает `confirmed live`;
- внешние Amnezia-created peer не удаляются;
- missing local device можно добавить на сервер;
- disable/enable работают;
- выборочное удаление устройства работает.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| API readiness after verified live baseline | `active-lab-design` | AMN3 -> `amn2` later | `docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md` | Сделать audit и выбрать первый safe API/ops slice |
| Local Amnezia Agent first slice | `pushed-needs-pr` | `amn2` | `codex/local-agent-first-slice`, commits `3119ee6`, `ac2baa8` | Учитывать при API-readiness; PR открывать отдельно при готовности |
| Local Agent production wiring | `pushed-needs-stacked-pr` | `amn2` | `codex/local-agent-production-wiring`, head `8697b60` | Учитывать как candidate для API/ops boundary |
| VPS retest bundle | `verified-live-baseline` | `amn2` | commit `573c368` | Не трогать без изменения VPS apply/sync логики |
| Config defaults from `.env` | `verified-live-baseline` | `amn2` | commit `8ecb0b4` и последующие fixes | Использовать как текущий config contract |
| Docker runtime peer apply/revoke | `verified-live-baseline` | `amn2` | `codex-vps-test-prep`, tag `vps-live-cycle-verified` | Использовать как behavior contract |
| Verified config delivery | `implemented-needs-regression-watch` | `amn2` | current web/email/bot flows | Держать policy: config, QR и `vpn://` являются `secret-read` |
| Public/self-service config delivery | `lab-only-until-policy` | AMN3 -> `amn2` later | `research/amn2/config-delivery-inventory.md` | После API-readiness решить route/config delivery policy |

## Local Agent Decision

Решение: переносить как собственную реализацию `amn2`, без копирования внешнего `kyoresuas/amnezia-api`.

Причина:

- задача совпадает с целевым продуктом: API-first управление пользователями Amnezia;
- текущий first slice уже защищен route policy, hash-only token auth, typed auth errors и no-write boundary;
- ближайший production gain - получить opt-in local runtime adapter на сервере, который controller сможет опрашивать безопасно;
- verified VPS baseline теперь дает реальный behavior contract для будущих write операций.

## Transfer Gates

Любая новая функция из AMN3 переходит в `amn2` только если есть:

- source/license verdict;
- current `amn2` inventory;
- risk class;
- route/auth policy;
- secret and audit decision;
- tests;
- rollback/recovery note for state-write or remote operations;
- AMN3 return note after branch/commit/PR.

## Current Priority Order

1. Открыть новый lab-чат по `docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md`.
2. Сделать API-readiness audit на основе verified `amn2` live behavior.
3. Выбрать первый safe API/ops slice: read-only Local Agent, controlled write operation, config delivery policy или иной узкий slice.
4. После выбора написать отдельный implementation plan для `amn2`.
5. Только потом переходить в production branch/worktree.

## Когда нужен новый live retest

Новый live retest обязателен, если меняется хотя бы одно из:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.
