# Текущее состояние проекта

Дата: 2026-05-31.

Этот snapshot фиксирует переезд из длинного `amn2` VPS-чата в `VPS-OPS-LAB` после подтвержденного live VPS cycle.

## Что учтено при обновлении

Проанализированы локальные Codex-сессии проекта с `VPS-OPS-LAB` и `Amneziya`, включая:

- ранний Amneziya planning/provisioning чат;
- `Подготовка запуска на VPS`;
- `VPS-тест Amneziya`;
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`;
- `VPN Ops Lab - KYORESUAS-API`;
- task/review-чаты Local Amnezia Agent first slice;
- task/review-чаты Local Agent production wiring;
- live VPS completion / verified tag / migration-to-lab чаты;
- текущий `MAIN - VPN Ops Lab` coordination chat.

Нерелевантные сессии из других рабочих папок, например `ISP-NEW`, не включались в состояние этого проекта.

## AMN3 / VPS Ops Lab

Локальный checkout:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

GitHub remote:

```text
https://github.com/barakov-dot/amn3.git
```

Текущая ветка:

```text
master
```

Текущий committed head lab:

```text
a0ccfef Expand secret inventory priority gate
```

`master` сейчас ahead of `origin/master` на 2 коммита:

- `3351a46 Add priority backlog`
- `a0ccfef Expand secret inventory priority gate`

Есть незакоммиченные lab-изменения:

- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `research/amn2/transfer-backlog.md`
- `research/amn2/api-readiness-audit-after-live-baseline.md`

AMN3 является coordination/knowledge repo: research, design specs, implementation plans, transfer notes и gate для переноса идей в production.

Production-код остается в `amn2`.

## Production baseline: `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

GitHub remote:

```text
https://github.com/barakov-dot/amn2.git
```

Текущая production-ветка:

```text
codex-vps-test-prep
```

Актуальный head:

```text
91aeb3e Document VPS verified tag
```

Проверенная stable-точка live VPS cycle:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Основной handoff production-репозитория:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
```

Последняя локальная проверка `amn2`:

```text
508 passed, 1 warning
```

Ожидаемое предупреждение: `StarletteDeprecationWarning` от `httpx` / `starlette.testclient`.

## Verified live VPS cycle

На живом VPS подтверждено:

- approve заявки в Telegram создает рабочий peer;
- клиентский config подключается;
- web panel показывает working config сразу после approve;
- `Run peer sync` подтверждает live-состояние;
- внешние peer, созданные в приложении Amnezia, не удаляются и отображаются отдельно;
- missing local device можно добавить в AmneziaWG;
- `Disable VPN` и `Enable VPN` работают;
- выборочное удаление устройства работает;
- Docker runtime apply/revoke прошел живую проверку;
- AmneziaWG 2.0 template/defaults приведены к рабочему формату.

Это закрывает прежний пункт `live VPS retest` как основной риск. Новый retest нужен только после изменений в apply/revoke/config/sync логике.

## Что продолжаем теперь

API-readiness audit выполнен в AMN3:

```text
research/amn2/api-readiness-audit-after-live-baseline.md
```

Основной порядок слияния API, web panel и operations зафиксирован:

```text
docs/AMN2_MAIN_MERGE_ROADMAP.ru.md
```

Первый выбранный safe slice для будущего переноса в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

Смысл slice: не добавлять новый production API сразу, а сначала сделать machine-checkable policy/contract для текущих web, bot, Local Agent и remote-operation surfaces: actors, auth, risk class, secret class, audit, idempotency, dry-run/apply, rollback/recovery и live-retest trigger.

Этот slice должен остаться без live VPS calls, без новых config/API/write endpoints и без копирования upstream code.

Решение по соседним чатам:

- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: широкие research-задачи поставить на паузу; оставить как targeted-input для web-panel UX, config delivery integrity, route taxonomy и dangerous-action patterns.
- `VPN Ops Lab — KYORESUAS-API`: оставить active reference для Local Agent/API architecture; не устанавливать, не копировать и не переносить CRUD/write API до policy/secret/remote-write gates.

## Что не делать первым

Не писать production API сразу.

Не копировать upstream code.

Не трогать live VPS из lab-чата.

Не считать старые заметки `implemented-needs-live-retest` актуальными: они исторические, live baseline уже подтвержден.

## Связанные документы

Главный migration handoff:

```text
docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
```

API/upstream start:

```text
docs/NEXT_CHAT_KYORESUAS_API.ru.md
research/upstreams/kyoresuas-amnezia-api.md
```

`amn2` transfer context:

```text
research/amn2/README.md
research/amn2/transfer-backlog.md
research/amn2/remote-operations-inventory.md
research/amn2/config-delivery-inventory.md
```

Existing unification design:

```text
docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
```

## Local Agent baseline status

Local Agent first slice:

```text
status: merged into codex-vps-test-prep via PR #2
commits: 3119ee6, ac2baa8
```

Local Agent production wiring:

```text
status: merged into codex-vps-test-prep via PR #3
head: 8697b60 Document Local Agent production wiring
```

Локальная проверка показала, что эти commits уже содержатся в актуальном production baseline `91aeb3e`. Поэтому следующий slice не должен повторно добавлять Local Agent foundation; он должен закрепить policy boundary вокруг уже существующего read-only/opt-in agent.

## Рекомендуемый порядок

1. Commit текущий AMN3 audit/roadmap state.
2. Review `docs/AMN2_MAIN_MERGE_ROADMAP.ru.md` и `research/amn2/api-readiness-audit-after-live-baseline.md`.
3. Написать отдельный implementation plan для `Route/Auth/Operation Policy Matrix`.
4. Не включать в первый plan новые API routes, config delivery endpoints, write operations или live VPS calls.
5. Только после принятого plan переходить в production branch/worktree.
6. После production-среза вернуть в AMN3 branch/commit/test evidence.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Новый AMN3 artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md
```

Production branch:

```text
codex-vps-test-prep
```

Production commit:

```text
d1d9690 Add route auth operation policy matrix
```

Создано в `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Проверка:

```text
focused policy/agent/server tests: 46 passed
web/bot smoke tests: 85 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Новые API endpoints не добавлялись. Новые write/config delivery flows не включались.

Обновленный порядок:

1. `amn2` commit `d1d9690` запушен в remote branch `codex-vps-test-prep`.
2. Следующий local-only slice выбран и выполнен: redaction coverage.
3. Следующий рекомендуемый safe slice: config delivery integrity.

## Redaction Coverage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
94ad807 Document secret-bearing delivery artifacts
```

Production commits:

```text
75c235a Expand redaction primitive coverage
fc73929 Add config delivery redaction coverage
f62d5d6 Harden config email audit coverage
eb735e2 Harden remote output redaction coverage
94ad807 Document secret-bearing delivery artifacts
```

Проверка:

```text
focused redaction/security/delivery/remote/docs tests: 61 passed, 1 StarletteDeprecationWarning
full local suite: 528 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет live apply/revoke/config/sync behavior, поэтому VPS gate не нужен.

## Local Gate / Live VPS Gate

Новый порядок проверки разделен на два контура.

Локально можно делать:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot smoke через TestClient;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- remote operation contracts на fake SSH;
- docs/status/backlog updates.

На real VPS проверяем только после локально зеленого slice, если он меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- реальный Local Agent deployment или controller-to-agent calls.

Следующий рекомендуемый local-only шаг: config delivery integrity. Следующий VPS gate пока не запускать, потому что policy matrix и redaction coverage не меняют live behavior.
