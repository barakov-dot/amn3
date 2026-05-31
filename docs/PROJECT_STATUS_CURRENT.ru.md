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
