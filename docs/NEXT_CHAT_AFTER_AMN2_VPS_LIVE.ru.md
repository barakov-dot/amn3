# Переезд в VPS Ops Lab после verified amn2 VPS live cycle

Дата: 2026-05-31.

Этот документ нужен как стартовая карта для нового чата в `VPS-OPS-LAB`. Цель переезда: не продолжать длинный VPS-чат, а перейти в lab-режим, где мы проектируем следующий API/ops слой от уже проверенного production baseline.

## Роли репозиториев

`amn2` остается production-репозиторием:

```text
C:\Users\SooL\Documents\Amneziya
https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
```

`VPS-OPS-LAB` / AMN3 остается coordination, research, design и transfer-gate репозиторием:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
https://github.com/barakov-dot/amn3.git
branch: master
```

В новом lab-чате production-код не меняем, пока отдельно не принято решение о переносе конкретного slice в `amn2`.

## Текущая точка правды `amn2`

Актуальный production baseline:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
handoff: docs/NEXT_CHAT_HANDOFF.ru.md
```

Последняя проверка локального `amn2`:

```text
git status: ## codex-vps-test-prep...origin/codex-vps-test-prep
tests: 508 passed, 1 warning
```

Тег `vps-live-cycle-verified` фиксирует последнюю точку, где базовый живой VPS-цикл был подтвержден.

## Что уже проверено на живом VPS

Проверенный цикл:

- Telegram approve создает peer на Docker AmneziaWG runtime.
- Сгенерированный config работает у клиента.
- `Working configs on server` показывает approved config сразу после approve.
- `Run peer sync` подтверждает `confirmed live`.
- Peer, созданные в приложении Amnezia, не удаляются и показываются отдельно как `Созданы в Amnezia`.
- `Disable VPN` и `Enable VPN` работают как реальные apply/revoke операции.
- Выборочное удаление устройства работает как описано в чате.
- При `VPS_APPLY_ENABLED=false` локальные операции не должны пытаться трогать VPS.
- Client config defaults и template override доведены до рабочего AmneziaWG 2.0 формата.

Этот baseline не надо заново доказывать в lab-чате. Его можно считать contract для следующего проектирования, пока production-код `amn2` не менялся.

## Что продолжаем в VPS-OPS-LAB

Рекомендуемое имя нового чата:

```text
VPS Ops Lab - API Readiness after amn2 live baseline
```

Задача первого lab-этапа:

```text
Сделать API-readiness audit и выбрать первый безопасный API / Local Agent / operations slice на основе verified amn2 live baseline.
```

Ожидаемый результат нового lab-чата:

- документ с API-readiness audit;
- решение, какой первый API/ops slice переносить в `amn2`;
- boundaries: actors, auth, secrets, audit, idempotency, dry-run/apply, rollback;
- только после этого отдельный implementation plan для `amn2`.

## Что не делаем первым шагом

Не начинаем с кода API.

Не копируем код из upstream-проектов.

Не трогаем live VPS из lab-чата.

Не открываем новую большую feature-ветку в `amn2`, пока не описан API contract и transfer gate.

Не возвращаемся к full live retest как к открытой задаче: verified cycle уже зафиксирован. Новый retest нужен только если меняется apply/revoke/config/sync логика.

## Что прочитать в новом чате

В `VPS-OPS-LAB`:

```text
docs/PROJECT_STATUS_CURRENT.ru.md
docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
docs/NEXT_CHAT_KYORESUAS_API.ru.md
docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
research/amn2/README.md
research/amn2/transfer-backlog.md
research/amn2/remote-operations-inventory.md
research/amn2/config-delivery-inventory.md
research/upstreams/kyoresuas-amnezia-api.md
```

В `amn2`:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
docs/VPS_RETEST_PROTOCOL.ru.md
docs/SERVER_CONFIG_TEMPLATE.ru.md
docs/WEB_PANEL_AND_BOT_SETUP.ru.md
```

## Первые проверки в новом чате

В `VPS-OPS-LAB`:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate
```

В `amn2`:

```powershell
cd C:\Users\SooL\Documents\Amneziya
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate
& 'C:\Program Files\Git\cmd\git.exe' tag --points-at d6eda20
```

Ожидаем для `amn2`:

```text
branch: codex-vps-test-prep
latest: 91aeb3e Document VPS verified tag
tag: vps-live-cycle-verified
```

## Стартовый текст для нового чата

```text
Работаем в VPS-OPS-LAB после завершения live VPS этапа amn2.

Локальная папка lab: C:\Users\SooL\Documents\VPS-OPS-LAB
Lab repo: https://github.com/barakov-dot/amn3.git
Lab branch: master

Production repo amn2: C:\Users\SooL\Documents\Amneziya
amn2 branch: codex-vps-test-prep
amn2 latest: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle

Сначала прочитай:
- docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/NEXT_CHAT_KYORESUAS_API.ru.md
- docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
- research/amn2/transfer-backlog.md

Проверь git status/log в lab и amn2.

Задача: сделать API-readiness audit и определить первый безопасный API/Local-Agent/operations slice на основе verified amn2 live baseline. Production-код не менять, upstream code не копировать, live VPS не трогать.
```

## Критерий готовности переезда

Переезд готов, если новый чат может без истории текущего чата понять:

- что `amn2` уже стабилен на live VPS в базовом цикле;
- какой commit/tag считать проверенной точкой;
- почему следующий этап лучше вести в lab, а не добивать случайные мелочи в production;
- какие документы читать первыми;
- какой первый результат требуется от lab-чата.
