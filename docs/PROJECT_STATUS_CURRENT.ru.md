# Текущее состояние проекта

Дата: 2026-05-31.

Этот snapshot фиксирует переезд из длинного `amn2` VPS-чата в `VPS-OPS-LAB` после подтвержденного live VPS cycle.

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

Коммит lab перед этим migration update:

```text
42dea7a Update Local Agent production wiring status
```

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

Следующий безопасный этап в lab:

```text
API-readiness audit after amn2 live baseline
```

Нужно определить первый API / Local Agent / operations slice, который можно будет отдельно перенести в `amn2`.

Ожидаемые вопросы audit:

- кто actor: web admin, Telegram admin, Local Agent, future API client;
- какая auth model допустима;
- какие routes являются read-only, secret-read, state-write, remote-write;
- где нужны dry-run, apply, idempotency, rollback/recovery;
- какие события должны попадать в audit;
- как не раскрывать private key, PSK, config, QR, `vpn://`;
- какие tests нужны до production branch.

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

## Local Agent branches still relevant

Local Agent first slice:

```text
branch: codex/local-agent-first-slice
commits: 3119ee6, ac2baa8
manual PR: https://github.com/barakov-dot/amn2/compare/codex-vps-test-prep...codex/local-agent-first-slice?expand=1
```

Local Agent production wiring:

```text
branch: codex/local-agent-production-wiring
head: 8697b60 Document Local Agent production wiring
manual PR: https://github.com/barakov-dot/amn2/compare/codex/local-agent-first-slice...codex/local-agent-production-wiring?expand=1
```

Эти ветки не являются обязательным первым действием нового lab-чата. Их нужно учитывать как уже подготовленные slices при выборе API-readiness направления.

## Рекомендуемый порядок

1. Открыть новый чат в `VPS-OPS-LAB` по `docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md`.
2. Проверить git status/log в lab и `amn2`.
3. Сделать API-readiness audit по текущему verified `amn2` behavior.
4. Выбрать первый безопасный slice.
5. Только потом писать implementation plan для `amn2`.
