# База знаний для будущего единого VPN-проекта — снимок 2026-09-23

Адресат: разработчик/модель нового проекта с общей админкой и ботом для нескольких
VPN-протоколов. Это **передача знаний уже сейчас**, а не перенос кода, данных или
полномочий. На23.09 оператор выбрал сначала завершить Phase16 на текущем сервере,
затем собрать окончательный пакет передачи. Уточнение03.10 заменило этот порядок:
завершить проект и перенести его на другой сервер/сервис; см. дополнение ниже.
Новый проект по сведениям23.09 находится на начальной
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

<a id="transfer-baseline-2026-10-03"></a>

## Дополнение03.10: переносимая основа и оставшиеся зависимости

Текущая цель — завершить проект и перенести его на другой сервер/сервис.
[Единственная очередь M0–M5](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md#transfer-priority-2026-10-03)
заменяет прежний порядок завершения на Spain. Этот раздел — материал передачи,
а не второй execution plan. Уточнение адресата уже запрошено: другой VPS либо
новый проект с общей админкой/ботом, точное место ещё не известно.

Локальная Git-сверка03.10: AMN2 checkout
`C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop`,
ветка `codex/phase16-web-health-event-loop`, HEAD
`6e682356ed14a62d636ee58039fd3a389e794809`, `git status --short` пустой.
AMN3 после preparation: `0421da7c2202c6d55a8c2bdf0d117d38b765ed1b`;
это local source commit, не deployment или доказательство publication.
Исторический Git remote/source push не проверялся повторно.

| Материал | Как использовать при переносе | Существенная граница |
| --- | --- | --- |
| AMN2 production source6e68235 | Основа приложения web/bot/DB и AWG version capabilities; exact source/tests привязаны в прежних receipts | Целевой runtime/data integration ещё не приняты; общая поддержка других протоколов не реализована этим SHA |
| Immutable source/runtime40 bundle | Сохранённые bytes/pins и offline provenance; ссылки в [runbook](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md) | Runtime wheels требуют проверки совместимости нового OS/architecture/Python; bundle не переносит live БД, токен или peers |
| AMN3 maintenance tools0421da7 | Проверки content/settings/writers/pending/access, one-shot sequence и manager-owned coordinator; [461 local PASS](../research/amn2/phase16-bot-maintenance-packet-local-verification-2026-10-03.json) | Конкретный packet связан с Spain boot/paths/UID/service/old schema и target digest; локальные tests не являются target acceptance |
| Решения и client evidence | Source/design links, naming/MTU/import ограничения, historical Android/iPhone connectivity и Windows/quality FAIL | Результаты Spain не принимают новую endpoint/network/runtime; перенести также открытые дефекты |

`PHASE16_BOT_MAINTENANCE_20261003_001` не выполнен и снят с текущей очереди;
не применять его на Spain или другом сервере как готовый migration package.
Изменение host/boot/hash без новой целевой проверки нарушает его контракт.
На новом VPS потребуется отдельный installation/migration контракт, а в новом
проекте — сначала сопоставление ownership/data/capability contracts с его кодом.

Для продолжения нужны точная цель и решение о переносимом состоянии: только
код/знания либо также согласованные БД, server bindings, users/subscriptions и
peers. Не трактовать этот перечень как разрешение открыть/export/copy live state.
Секреты передаются отдельно по [протоколу](AMN2_SECRET_HANDOFF_PROTOCOL.ru.md);
набор для Git не включает `.env`, keys/PSK/tokens, raw конфиги/логи и строки БД.
Если сохраняется Telegram identity, переключение должно исключать одновременный
polling старой и новой копий; local token reset не подразумевается.

Передача основы подготовлена; фактический перенос, target acceptance и закрытие
Phase16 ещё не выполнены. Это сохраняет completed checks без объявления всего
проекта принятым. SSH/live writes/install/activation/push в дополнении03.10:0.

### Позднее exact исполнение03.10 после уточнения переноса

Оператор отдельно разрешил ранее подготовленный Spain packet и push0421da7;
owner statement принят для45min окна. [Запуск](../research/amn2/phase16-bot-maintenance-execution-001-2026-10-03.json)
завершился за22.937s/SSH3, полный transport, bound STOP_OR_UNKNOWN_NO_RETRY.
Push0421da7 подтверждён Git readback. Candidate installation/activation и DB/service
state этим ответом не приняты: UNKNOWN, repeat/restore/replay запрещены.
Текущую безопасную границу M0a — отдельный read-only retained-state readback —
смотреть в единственном плане. Цель переноса и вопрос о точном месте сохраняются;
этот запуск не является фактическим переездом или закрытием Phase16.

### Подтверждённое состояние после readback03.10

[Readback execution](../research/amn2/phase16-bot-maintenance-readback-execution-001-2026-10-03.json):
один exact SSH0/4.031s, READBACK_COLLECTED_NOT_RECOVERY, writes/DB/service actions0.
Bot/web active/stable; access/coordinator/sequence claims и fences отсутствуют,
coordinator not-found. По bound source ordering permission/maintenance sequence
не начинались этим packet; точный original exception не сохранён. Current
candidate probe STOP/candidate_collection_failed, inner cause не установлена;
это переносимое открытое ограничение, не target admission. Оба approvals consumed.
AMN3 source5acb675 опубликован и подтверждён exact ref readback; приложение на VPS
этим Git push не развёрнуто. M0a завершён, далее M1–M5 в единственном плане.

<a id="forming-admin-2026-10-03"></a>

### Будущая общая админка ещё формируется — уточнение03.10

Оператор подтвердил стадию формирования общей админки. Сейчас передаём основу
знаний и сохраняем проверяемые source/package/evidence и открытые ограничения.
Точный адрес/репозиторий нужен при реальном сопоставлении ownership/data/runtime
контрактов; его отсутствие не останавливает локальную подготовку текущего проекта.
Код новой админки здесь не проверялся, её реализация в этот scope не входит.

До появления адресата разработчику доступны ссылки выше на AMN2 source6e68235,
immutable runtime40, bot worker lifecycle, web/DB ownership, AWG capability limits
и client evidence. Current candidate collector STOP остаётся открытым; отдельный
[component diagnostic](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-component-diagnostic-2026-10-03)
подготовлен локально для inner reason, без live исполнения. Это не новый runtime
или новая универсальная protocol model. Phase16 acceptance/closeout остаются
открытыми; дальнейшее состояние брать только из единственного плана.

<a id="candidate-ancestor-precondition-2026-10-03"></a>

### Current ancestor precondition — переносимое ограничение03.10

[Actual component diagnostic](../research/amn2/phase16-bot-candidate-diagnostic-execution-001-2026-10-03.json)
установил current access_plan/ancestor_access, один SSH0/4.218s, без mutations.
Settings/bootstrap/identity/expected wheels/venv PASS относятся к достигнутым
этапам; full installed runtime verification ещё не достигнут. Original unsaved
exception не доказан. Bot/web/retained markers прежние; push e0bdf39 подтверждён.

Для разработчика целевого размещения: selected service должен проходить по всей
parent chain; private stage/payload/receipts остаются изолированы. Старый access
plan намеренно не меняет shared ancestors. Нельзя переносить его как готовый
универсальный chmod/import рецепт или удалять traversal precondition ради PASS.
[Actual ancestor facts](../research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json)
выполнены один раз: SSH0/2.938s, без writes/permissions. Exact parent
`/opt/amn2-spain/bot-candidates` root:root0700, dev64770/ino262273; selected
service UID/GID61212. Другие три parents traversable; stage-root root:root0700
ожидаемо приватен. Bot/web unchanged; approval consumed, push6be4149 MATCH.
[Parent repair04.10](../research/amn2/phase16-bot-ancestor-repair-execution-001-2026-10-04.json)
выполнен один раз: SSH3/7.125s, STOP_NO_REMOTE_CHANGE/sibling_inventory, audit false,
operation null; permission/DB/app/services/candidate scan0. Approval consumed,
push2410dea MATCH. Local name whitelist пропускал исторический readback-guard22.09;
live состав не сообщён. Для разработчика: безопасность execute-only parent требует
private top-level дочерних объектов, а имена каталогов не служат доказательством
приватности. Подготовлен отдельный [v2](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-ancestor-repair-v2-2026-10-04):
каждый непосредственный sibling root:root0700 directory/no links/no ACL, max16,
retained root exact; unknown names только SHA256 keys в private audit. Desired
parent root:61212/0710 и other guards/proof scope прежние; новый live NOT_EXECUTED,
checksum approval необходим. Frozen v1 сохраняется, no replay. Child access plan не применяется; original57
artifacts/consumed operations неизменны. Это целевой host-specific fix, а не
универсальная инструкция для нового VPS. Group traverse не даёт listing/write;
root-private дочерние stage остаются недоступны сервису до отдельного access apply.
При новом target нужны проверенные layout/ownership/rollback и один poller; данные
Spain и local PASS не принимают новую общую админку. Phase16 остаётся открытой.
