# `amn2` Transfer Backlog

Дата: 2026-05-31.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| Local Amnezia Agent first slice | `pushed-needs-pr` | `amn2` | `codex/local-agent-first-slice`, commits `3119ee6`, `ac2baa8` | Открыть stacked PR в `codex-vps-test-prep` |
| Local Agent production wiring | `implementation-plan-ready` | `amn2` | `docs/superpowers/plans/2026-05-31-amn2-local-agent-production-wiring.md` | После PR/review выполнить plan task-by-task |
| VPS retest bundle | `implemented-needs-live-retest` | `amn2` | commit `573c368` | Проверить на live VPS после Local Agent PR |
| Config defaults from `.env` | `implemented-needs-live-retest` | `amn2` | commit `8ecb0b4` | Проверить выдаваемые configs и preview на live VPS |
| Docker runtime peer apply/revoke | `implemented-needs-live-retest` | `amn2` | текущий `codex-vps-test-prep` | Подтвердить disable/enable и selective revoke |
| Verified config delivery | `implemented-needs-regression-watch` | `amn2` | current web/email flows | Держать policy: config, QR и `vpn://` являются `secret-read` |
| Public/self-service config delivery | `lab-only-until-policy` | AMN3 -> `amn2` later | `research/amn2/config-delivery-inventory.md` | Сначала route/config delivery policy, затем отдельный plan |

## Local Agent Decision

Решение: переносить как собственную реализацию `amn2`, без копирования внешнего `kyoresuas/amnezia-api`.

Причина:

- задача совпадает с целевым продуктом: API-first управление пользователями Amnezia;
- текущий first slice уже защищен route policy, hash-only token auth, typed auth errors и no-write boundary;
- ближайший production gain - получить opt-in local runtime adapter на сервере, который controller сможет опрашивать безопасно.

Следующий artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-local-agent-production-wiring.md
```

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

1. Открыть/смержить Local Agent first slice PR.
2. Выполнить Local Agent production wiring plan.
3. Обновить AMN3 status with commits, tests and PR URL.
4. Вернуться к live VPS retest on latest `codex-vps-test-prep`.
5. После live retest выбирать следующий slice: runtime write operations или config delivery policy.
