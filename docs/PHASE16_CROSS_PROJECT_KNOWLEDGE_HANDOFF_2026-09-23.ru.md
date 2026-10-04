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
parent root:61212/0710 и other guards/proof scope прежние. [Actual v2 исполнен04.10](../research/amn2/phase16-bot-ancestor-repair-v2-execution-001-2026-10-04.json):
SSH0/12.297s, parent verified/durable, два permission syscalls; installed runtime
PASS_SITE_CONTENT_ONLY4621files/2092bytecode. Candidate access_plan STOP/private_boundary,
exact объект не сообщён. Old selected units/boot/NSS final guard PASS, DB/app/services/
child DAC/install0; approval consumed, push4d57e2d MATCH. Готов [short readonly packet](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-private-boundary-readback-2026-10-04)
для metadata четырёх объектов и pinned durable repair result. [Actual readback04.10](../research/amn2/phase16-bot-private-boundary-readback-execution-001-2026-10-04.json)
исполнен один раз: SSH0/2.578s, claim/result root:root0644 regular/nlink1/ACLclear,
payload/scratch700; parent/stage/repair result/selected units прежние, mutations/DB/
app/services0, approval consumed, pushdce10e0 MATCH. Подготовлен [отдельный seal](../research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-private-seal-2026-10-04):
ровно два JSON fchmod600 после exact witness/durable intent, затем candidate readonly
plan build; access apply/DB/services/install0, [local20 PASS/review](../research/amn2/phase16-bot-private-seal-local-verification-2026-10-04.json),
live NOT_EXECUTED/new approval. Для
разработчика: новые stage receipt files следует создавать явно private0600; implicit
process umask не гарантирует это. Actual umask текущего VPS не измерен. Frozen v1/v2
сохраняются, no replay. Child access plan не применяется; original57
artifacts/consumed operations неизменны. Это целевой host-specific fix, а не
универсальная инструкция для нового VPS. Group traverse не даёт listing/write;
root-private дочерние stage остаются недоступны сервису до отдельного access apply.
При новом target нужны проверенные layout/ownership/rollback и один poller; данные
Spain и local PASS не принимают новую общую админку. Phase16 остаётся открытой.

<a id="upstream-recommendations-2026-10-04"></a>

### Принятые рекомендации upstream04.10 для следующей разработки

Оператор разрешил применить рекомендации; [intake и exact sources](UPSTREAM_INTAKE.ru.md#upstream-intake-2026-10-04)
сохраняют rationale/priority/contracts. Applied здесь означает требования и
передаваемые знания; новая функциональность AMN2/админки не реализована этим шагом.

| Получатель / требование | Следующий допустимый шаг |
| --- | --- |
| Генератор AWG3.1: до рендеринга проверить worst-case MTU budget с учётом S4/padding upper bound и выбранного transport | Существующий P3 после image/source binding и transfer queue; explicit MTU/insufficient budget и boundary tests, без изменения старых профилей |
| Общая multi-server/protocol админка: связать request/response/cache с точным выбранным context; не принимать неполный snapshot за пустой список | Дополнен HYB-AI-001, hybrid-only P2 при проектировании после target contract; delayed/out-of-order и mixed/incomplete snapshot tests |
| AWG3.1 receive-path: H1–H3/RandomTrailers | Существующий отдельный P2; сначала exact runtime/source contract, без переноса неподтверждённого issue-рецепта |

AMN2 source6e68235 проверен clean; renderer/importer budget gap сохраняется,
но параметры deployed peer и причина quality FAIL этим не определены. Код
будущей админки не обследован; нельзя объявлять эти защиты отсутствующими у неё.
При передаче разработчик сопоставляет требования с фактической реализацией и
не копирует GPL-код или secret-bearing payloads. Цель переноса, M0f, отложенные
клиентские проверки, AWG2/package016/general issuance прежние; на момент записи
этих рекомендаций seal не был исполнен, последующее выполнение приведено ниже.

<a id="candidate-ready-transfer-baseline-2026-10-04"></a>

### Проверенная основа переноса после закрытия M0f — 04.10

[Actual seal](../research/amn2/phase16-bot-private-seal-execution-001-2026-10-04.json)
выполнен по exact approval: SSH0/30.000s, два JSON0600 verified/durable;
14 components и candidate PASS, runtime/bootstrap content4621files/2092bytecode
PASS. Access plan5278 objects/SHA c60b69ec8ac6018f58b86049fd20bdeb9c80a63f0302e33924efa8e936e7515e
построен, не применён. AMN3 a93b785 опубликован, exact ref readback MATCH.

Для передачи: AMN2 source6e68235 и immutable source/runtime40, проверенные
candidate content/settings/catalog/identity и план доступа сохранены вместе с
решениями upstream. M0a–M0f закрыты; повторный диагностический цикл по текущему
candidate blocker не требуется. Приёмщик должен различать эту готовность и
реальное startup/data integration: БД не открывалась, доступ сервису не выдавался,
app/services/install/activation0, original maintenance не повторялся.

Следующее — M1/M2 при готовности общей админки/целевого сервера: зафиксировать
target и data ownership, переносимый набор данных и совместимый runtime,
recovery/rollback, один Telegram poller и client acceptance. Старые Spain boot/
paths/UID/claims не переназначаются на новый host. Клиентские проверки отложены;
AWG2/package016/issuance и прочие stages сохранены. Интеграция, перенос и Phase16
ещё не приняты; новая установка на Spain не требуется автоматически.

<a id="source-transfer-contract-2026-10-04"></a>

### Исходная сторона контракта переноса — проверено 04.10

После публикации результата M0f (`373e3a1`, exact remote readback MATCH)
выполнена статическая сверка AMN2 `6e68235`: checkout чистый, 20 исходных файлов
привязаны к Git blobs в [receipt](../research/amn2/phase16-transfer-source-review-2026-10-04.json).
Это подготовка исходной стороны M1/M2. Цель, состав переносимых данных и их
владелец пока не определены; M1/M2 не объявляются завершёнными. Приложение не
импортировалось, БД не открывалась, архивы и новые пакеты не создавались.

#### Что может использовать принимающий разработчик

| Область | Проверенный контракт исходника | Следствие для переноса |
| --- | --- | --- |
| Runtime | `pyproject.toml`: Python `>=3.12,<3.13`; Linux/systemd примеры bot/web, отдельный immutable runtime40 | Проверить OS/архитектуру/ABI адресата. Примеры unit и Spain paths не являются готовой конфигурацией нового host |
| Протоколы | `app/vpn/protocol_versions.py`: AWG2/AWG3; активная ревизия AWG3 — 3.1 | Новый общий protocol manager требует сопоставления capabilities; другие протоколы этим кодом не реализованы |
| Backup | `app/backup/service.py` и `manifest.py`: архив содержит только `database.sqlite3` и `manifest.json` | Не переносит приложение, runtime, файлы сервера, внешние токены и конфигурацию VPN-узла |
| Ключ данных | `app/backup/storage.py`, `app/security/crypto.py`: архив и шифротексты устройств зависят от `APP_SECRET_KEY`; сам ключ исключён из архива | При сохранении шифротекстов нельзя просто заменить ключ новым. Сохранение ключа или отдельная перешифровка определяются целевым контрактом; значения только по secret handoff protocol |
| Согласованность копии | `BackupService.create` сначала считает hash основного файла БД, затем читает его для архива; в этом методе нет SQLite backup API и захвата WAL | Нужна отдельно доказанная согласованная копия с учётом writers/journal. Наличие команды backup этого не доказывает; метод на живой БД не запускался |
| Проверка восстановления | `verify` проверяет архив/manifest/checksum; `restore` дополнительно проверяет выбранные свойства БД | `verify` не заменяет репетицию восстановления. Restore требует `expires_at` у active/pending, хотя схема допускает indefinite с NULL: применимость к выбранным данным требуется проверить отдельно, live-дефект не установлен |
| Мигратор Phase13 | `app/migration/bot_web.py`: merge истории только в `.copy.sqlite3`; импортированные устройства — revoked/external_only, рабочие ключи не переносятся | Нельзя использовать как перенос действующих VPN-подключений или как универсальный импорт новой админки |
| Запуск приложения | Bot `create_workflow` вызывает `initialize_schema`, seed планов и default/server sync; web `_open_repository` тоже вызывает `initialize_schema` | Пробный запуск на целевой БД может её изменить. Нужны копия, выбранная startup policy и проверки результата до переключения |
| Единственный bot owner | `PersistentBotInstanceLock` блокирует локальный файл | Локальный lock не исключает вторую копию на другом host; перед cutover нужны отдельные stop/drain/start и доказательство одного poller |

Старый [backup-policy report](../research/amn2/backup-import-policy-contract-implementation.md)
описывает другую ветку `afb2702`. В проверенном `6e68235` файла
`app/backup/policy.py` нет; фактическая реализация — перечисленные выше modules.
Этот исторический report не является контрактом готового импорта для переноса.

#### Карта данных для сопоставления с новой админкой

Все 29 уникальных таблиц из деклараций `schema.py`, `phase14_dual_protocol.py`
и `phase15_bootstrap.py` распределены ниже; временные таблицы rebuild исключены.
Это карта исходного кода, а не утверждение о схеме или количестве записей живой БД.
Названия и связи проверяются в pinned source из receipt; строки БД сюда не входят.

| Группа | Таблицы | Решение, которое должен закрепить целевой контракт |
| --- | --- | --- |
| Пользователи и бизнес-данные | `users`, `plans`, `orders`, `message_templates` | Сохраняемые сущности, соответствие ID, владельцы, тарифы и сроки |
| Устройства и владельцы | `devices`, `device_passports` | Сохранение привязок owner/server, expiry policy и доступности секретного материала |
| Серверный контекст | `servers`, `server_health_checks`, `vpn_runtime_instances`, `client_compatibility_evidence`, `ignored_remote_peers` | Какие VPN-узлы остаются и какие переезжают; старые paths/endpoint/acceptance не становятся автоматически действительными на новом host |
| История и телеметрия | `admin_actions`, `device_traffic_snapshots`, `device_lifecycle_events` | Объём сохраняемой истории и её происхождение, без принятия старой телеметрии за свежую |
| Повторяемость операций и назначение | `admin_config_issuance_requests`, `admin_config_issuance_receipts`, `access_slot_assignment_requests`, `legacy_migration_records` | Сохранение связей и защиты от повторной выдачи; необработанные операции требуют явного решения |
| Доступ и enrollment | `email_recovery_tokens`, `api_tokens`, `device_enrollment_tickets` | Сохранение либо перевыпуск полномочий; token hashes и пользовательские записи не включать в публичную передачу |
| Состояние протоколов | `awg3_control_state`, `client_build_acceptances`, `device_protocol_profiles`, `protocol_config_events`, `protocol_issuance_attempts`, `protocol_issuance_user_barriers` | Сохранить историю; заново связать admission с целевым runtime, разобрать reserved/recovery_required и barriers до включения выдачи |
| Незавершённые действия Telegram | `telegram_callback_handles`, `protocol_issuance_confirmations` | Сроки, claims и terminal states должны иметь явную политику; не считать их пустыми и не воспроизводить автоматически |

Эта таблица не задаёт автоматический copy/drop для любой группы. При переносе
только кода не нужен доступ к живым данным; при сохранении состояния понадобятся
выбранный набор, защищённый snapshot, совместимая схема и репетиция на копии.
Ни один из этих вариантов пока не выбран за оператора.

Открыты четыре входа M1: граница переноса (включая судьбу Spain VPN-узла), адресат
и его стек, состав сохраняемых данных, единственный владелец bot/web/data после
переключения. Вопрос о границе уже задан; повторного запроса адреса формирующейся
админки нет. После ответа уточняется существующая очередь M1–M5, без нового
Spain diagnostic/install. Клиентский retest остаётся отложенным; AWG2/package016,
общая выдача и предыдущие approvals не меняются.
