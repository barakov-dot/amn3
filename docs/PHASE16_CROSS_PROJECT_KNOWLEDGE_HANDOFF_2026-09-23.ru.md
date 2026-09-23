# База знаний для будущего единого VPN-проекта — снимок 2026-09-23

Адресат: разработчик/модель нового проекта с общей админкой и ботом для нескольких
VPN-протоколов. Это **передача знаний уже сейчас**, а не перенос кода, данных или
полномочий. Оператор выбрал сначала завершить Phase16 на текущем сервере, затем
собрать окончательный пакет передачи. Новый проект пока находится на начальной
стадии у другой модели; его код здесь не проверялся. Этот снимок не является
вторым execution plan и не объявляет Phase16 принятой.

## Источники правды и порядок чтения

1. [START_HERE](START_HERE.ru.md) и [AGENTS](../AGENTS.md) — границы текущего
   репозитория, разрешения и защита секретов.
2. [Паспорт](PROJECT_PASSPORT.ru.md) — AMN3 как research/evidence/control plane,
   AMN2 как отдельный production source, VPS и клиенты как отдельное live state.
3. [Текущий план Phase16](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md)
   — единственная очередь исполнения; это главный источник изменяющегося статуса.
4. [Дизайн интеграции](superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#integration-readiness-web-bot),
   [bot candidate runbook](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md),
   [readback `_009`](../research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-009-stop-2026-09-22)
   — проверенное и неизвестное в Task 3B.
5. [Критерии приёмки v1](PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md) и
   [обязательное сравнение A/B](../research/amn2/phase16-spain-transport-quality-ab-gate-2026-08-26.md)
   — требования к клиентскому результату, не подтверждение PASS.

Старые handoff/GO и датированные receipts объясняют прошлые действия; они не
разрешают запуск команд. Перед работой проверять Git и свежий статус, а не
считать SHA в этом снимке вечным указателем на HEAD или deployed revision.

## Что уже есть в исходниках

Проверенный локальный AMN2 source candidate — commit
[`6e682356ed14a62d636ee58039fd3a389e794809`](https://github.com/barakov-dot/amn2/commit/6e682356ed14a62d636ee58039fd3a389e794809)
в ветке `codex/phase16-web-health-event-loop`. На момент этого снимка локальный
checkout был чистым. Это **не** SHA приложения, работающего на VPS.

| Область | Передаваемое знание | Граница |
| --- | --- | --- |
| Web/admin, Telegram bot, SQLite repository | Рабочие entrypoints и бизнес-потоки находятся в `app/web/`, `app/bot/`, `app/services/`, `app/db/`; bot worker сериализует свои принятые операции и имеет lifecycle tests. [Bot evidence](../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-implementation-m4-2026-09-21) | Bot lock не ограждает web/API/agent/CLI writers общей БД; production startup/drain/rollback не принят. |
| AWG2/AWG3.1 | Есть модели версий, runtime/admission, конфиги и запреты выдачи. `app/vpn/protocol_versions.py` и SQLite schema ограничены AWG2/AWG3; это предмет адаптации, а не готовая универсальная модель. | WireGuard/Xray и иные новые protocol managers не объявлять реализованными из-за их упоминания в документации. |
| Артефакты выдачи и безопасность | [Transfer checklist](superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md) описывает ownership, secret-read, audit, тесты и rollback. [Manager export candidate](../ideas/candidates-for-amn2.md#manager-config-export-contract) уже имеет узкий local-only adapter slice. | Новые форматы импорта и общий интерфейс протоколов требуют проверки capabilities каждого протокола и нового проектного решения. |
| Bot candidate для Linux | Отдельный immutable source `6e68235`, 40 runtime и 8 test-only wheels. [Изолированный Linux gate](../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#isolated-linux-pass-2026-09-22) прошёл negative control и 6 signal tests. | Test-venv с 48 pins и retained test directory не являются production release/venv или разрешением activation. |

AMN3 хранит решения, планы, проверки и операторские инструменты; AMN2 хранит
production-код. [Ранее согласованная схема двух репозиториев](superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md)
не означает автоматическое объединение Git histories. GPL-3.0 upstream из
исследовательских карточек остаётся `research-only`: идеи и требования можно
формулировать самостоятельно, upstream code/UI/scripts не копировать.

## Состояние Phase16 на дату снимка

- Task 0/1/2 и 3A завершены по соответствующим историческим evidence; package016
  immutable, AWG2_UNTOUCHED, общая AWG3 выдача выключена.
- Task 3B открыт. [Execution `_009`](../research/amn2/phase16-bot-integration-readback-execution-009-2026-09-22.json)
  завершился `STOP_NO_RETRY`: один SSH, валидный частичный receipt; deployed
  source отличается от candidate (102/126 ожидаемых `.py` присутствуют,
  24 отсутствуют, 24 отличаются). Dependency result/DB stage не получены,
  точная deployed revision и причина remote exception неизвестны. Не повторять
  `_009` и не выдавать наличие тестового candidate на VPS за установку.
- Task 4B/4C имеют connectivity/reconnect evidence, но не performance acceptance.
  Task 4A Windows traffic FAIL, Task 4.5 quality FAIL и строгое сравнение AWG2/
  AWG3.1 не завершено. Task 5 acceptance и Task 6 closeout заблокированы.
- Порядок завершения: клиентское quality A/B и Windows evidence; затем отдельно
  разрешённая bot/application integration с реальной schema identity, полным
  writer fence, startup seed policy, точным revert target и recovery; затем
  acceptance/closeout. Текущий порядок и scope всегда брать из плана Phase16.

## Что передавать новому проекту после закрытия Phase16

Финальный handoff должен назвать: exact AMN2 source/release SHA и соответствующие
тесты; AMN3 commit и ссылки на решения/receipts; реально подтверждённые клиентские
и server outcomes; capability map по протоколам; выбранные границы адаптации
web/bot/DB; известные дефекты и исключения. Каждый статус помечать как local,
package, deployed или accepted. Решение «выбор протокола пользователем либо доступ
ко всем» остаётся продуктовым вопросом нового проекта и не меняет Phase16.

Не включать в передачу `.env`, ключи, PSK, токены, raw конфиги/логи, строки живой
БД или незащищённые backup. Передача знаний не разрешает новый SSH, установку,
выдачу, перенос состояния или изменение другого репозитория. После появления
доступа к новому проекту сначала сравнить его код и модель данных с этим снимком;
не копировать AMN2 целиком без решения о владении данными и capabilities.

## Старт для другой модели

«Прочитай этот датированный снимок и связанные канонические документы AMN3.
Проверь текущие Git HEAD/статус AMN3, AMN2 и своего проекта. Раздели verified
source, package, deployed и accepted. Составь карту пересечений для будущей общей
админки/бота и протокольных capabilities; решения о пользовательском выборе
протокола оставь открытыми. Не запускай исторические GO, не переноси секреты,
не меняй live VPS и не объявляй Phase16 закрытой без новых receipts».
