# `amn2` Transfer Backlog

Дата: 2026-05-31.

Назначение: единая очередь переноса AMNEZIYA-наработок и upstream-идей из AMN3 в production repo `amn2`.

Правило: AMN3 хранит статус, решение, plan, branch/commit/PR links и test evidence. Production-код остается в `C:\Users\SooL\Documents\Amneziya` / `barakov-dot/amn2`.

## Active Items

| Item | Статус | Target repo | Текущий artifact | Следующий шаг |
| --- | --- | --- | --- | --- |
| Local Amnezia Agent first slice | `pushed-needs-pr` | `amn2` | `codex/local-agent-first-slice`, commits `3119ee6`, `ac2baa8` | Открыть stacked PR в `codex-vps-test-prep` |
| Local Agent production wiring | `pushed-needs-stacked-pr` | `amn2` | `codex/local-agent-production-wiring`, head `8697b60` | Открыть stacked PR в `codex/local-agent-first-slice` |
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
codex/local-agent-production-wiring
```

Production wiring branch включает:

- disabled-by-default settings;
- strict hash-only `LOCAL_AGENT_TOKEN_HASH`;
- token builder from settings;
- real read-only runtime detection for Docker and host/systemd;
- `python -m app.cli agent hash-token`;
- `python -m app.cli agent serve`;
- production docs.

Verification:

```text
tests/agent tests/config/test_settings.py tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_cli_web.py -v
108 passed, 1 existing Starlette/httpx warning
```

Stacked PR:

```text
base: codex/local-agent-first-slice
head: codex/local-agent-production-wiring
url: https://github.com/barakov-dot/amn2/compare/codex/local-agent-first-slice...codex/local-agent-production-wiring?expand=1
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
2. Открыть production wiring PR как stacked PR поверх `codex/local-agent-first-slice`.
3. После merge first slice retarget/rebase production wiring на свежий `codex-vps-test-prep`.
4. Смержить production wiring после review.
5. Вернуться к live VPS retest on latest `codex-vps-test-prep`.
6. После live retest выбирать следующий slice: runtime write operations или config delivery policy.
