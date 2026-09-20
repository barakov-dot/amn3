# Журнал изменений AMN3 / VPS-OPS-LAB

Ведётся с 2026-09-13. Предыдущие записи ниже восстановлены по указанным receipts
и Git, это не полная история проекта. Даты — даты действий/подтверждений;
записи не означают deployment или новую выдачу. Текущая очередь — в
[плане Phase16](docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).

## 2026-09-20

- По подтверждённому [плану bot worker](docs/superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md)
  выполнены четыре этапа inline: one-thread SQLite ownership, bounded FIFO/async facade,
  handler lifetime и persistent runtime/delivery integration. Source AMN2 commits
  614dfd8, b9f5d4e, 28a4e43, 8bc8496 и review fix 1bd7f62 включают свой CHANGELOG
  и отправлены обычным push в codex/phase16-web-health-event-loop; remote SHA сверены.
  Baseline 278 PASS; итог 312 PASS без warnings. Независимый read-only review выявил
  две гонки до dispatch (queued cancellation и factory после close); обе воспроизведены
  RED и исправлены. [Полное evidence и ограничения](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-worker-реализация-и-проверки--2026-09-20).
  Docs проверены readback, локальными ссылками и diff/whitespace; source и docs
  фиксируются раздельно. Нет live/VPS/Telegram/реальной выдачи, package/stage/install,
  dependency/schema changes или deployment. Phase16 gates, AWG2 и package016 сохранены.

- Оператор подтвердил [письменный bot worker design](docs/superpowers/specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md)
  после commit b277154; статус DESIGN_APPROVED_NOT_IMPLEMENTED_NOT_DEPLOYED.
  Подготовлен [технический implementation plan](docs/superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md):
  четыре части с явными API, RED/GREEN, factory cleanup, queue/cancel/context,
  handler ownership и runtime/delivery integration; затем независимый review.
  План ожидает review и выбора метода; рекомендуется inline, subagents не запускались.
  Выполнены self-review покрытия design, readback, ссылки и diff/whitespace.
  Код AMN2 и runtime tests не менялись/не запускались; live/package/выдача вне scope.

- Подготовлен [design последовательного bot workflow worker](docs/superpowers/specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md)
  на baseline AMN2 2069e41: SQLite принадлежит одному потоку, ограниченная очередь
  на 8 outstanding jobs, async facade и явное владение lifetime handlers.
  Отмена до dispatch исключает job, после dispatch операция завершается; shutdown
  дожидается уже принятых handlers, включая delivery record, до закрытия БД/сессии.
  Учтены partial failure и отсутствие гарантии быстрого меню/жёсткого drain timeout.
  Статус DESIGN_DRAFT_READY_FOR_REVIEW: документ ещё не утверждён, код не реализован.
  Выполнены source/self-review, readback, проверка ссылок и diff/whitespace;
  bot/runtime tests, VPS/Telegram, package/stage/install не запускались.

- [DefaultVPN: получен ответ поддержки](research/amn2/phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md#ответ-поддержки-предоставленный-оператором--2026-09-20),
  предоставленный оператором. Восстановлен порядок русского письма из истории
  задачи; он отличается от английского черновика. Поддержка отрицает возможность
  имени при .conf и полное сохранение MTU/AWG через vpn://, без уточнения полей.
  Точные параметры, шаги экспорта и привязка source остаются неподтверждёнными;
  native delivery не включается. WAITING_REPLY заменён на CLARIFICATION_NEEDED,
  узкое уточнение подготовлено, не отправлено. Проверены readback, ссылки,
  согласованность и diff/whitespace. Source/tests/live/профили не менялись,
  повторных GitHub lookup, phone tests или отправок сообщений не было.

- [Bot SSH/SQLite: завершён source review](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-sqlite-и-границы-переноса--2026-09-20)
  на AMN2 2069e41: 41 прямой вызов 30 методов в handlers, общий SQLite,
  partial remote/local failure и запись доставки после Telegram send.
  Сравнены последовательный worker и разделение prepare/remote/finalize;
  рекомендован первый, выбор/design/реализация ещё не согласованы.
  Зафиксированы ограничения очереди, отмены, shutdown и необходимые synthetic
  проверки. Source/readback, ссылки и diff/whitespace проверены; pytest не
  запускался, AMN2 source/VPS/AWG2/package016/выдача не менялись.

- [Локальный web health fix AMN2](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#локальная-реализация-после-согласования--2026-09-20):
  после согласования оператора SSH-ожидание вынесено из event loop одного handler.
  Baseline 28 PASS; RED 2 ожидаемых FAIL + 3 guards PASS; GREEN 33 PASS.
  SQLite/auth/CSRF/summary/audit сохранены; новое CHANGELOG в source checkout.
  Source 2069e41 pushed в AMN2/codex/phase16-web-health-event-loop; remote SHA
  подтверждён. Независимый review без замечаний. Существующий warning httpx
  сохранён; общий suite и live действия не запускались. Документация проверена
  readback/links/diff, source checkout и пакет сохранены.

- DefaultVPN: оператор сообщил об отправке письма на support@dfvpn.com;
  статус SENT_OPERATOR_REPORTED / WAITING_REPLY, направление отложено как несрочное.
  Доставка и ответ независимо не проверены; исходный черновик сохранён.
- [Panel #174: применимость к AMN2](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md):
  source review подтвердил синхронный SSH в async web health и условном bot revoke.
  Уточнена существующая карточка, предложен локальный fix только web health;
  bot SQLite и retry/cooldown требуют отдельного решения. Проверены официальный
  PR/diff, локальные source/tests, дубли в четырёх ideas-файлах и ссылки/whitespace.
  Код/тесты AMN2 и VPS не запускались и не менялись; weekly cursor не продвинут.

- [DefaultVPN: зафиксирована следующая граница](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#следующая-граница-после-name_fail-и-остановки--2026-09-20):
  оператор остановил переподключение и подтвердил отсутствие просмотра/экспорта
  одного профиля. Read-only AMN2 source check отделил готовый native exporter от
  двух legacy delivery call sites; source/tests/выдача не менялись.
- Точный source cb7ea0c не найден через commit lookup в двух официальных repositories;
  source/build binding и сохранность параметров остаются UNKNOWN. Подготовлен
  [запрос разработчикам](research/amn2/phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md)
  на support@dfvpn.com, не отправлен. GitHub issues отключены; PR #23 меняет
  заголовок настроек и не является исправлением импорта .conf. Проверки: source/API readback, пользовательские ответы, ссылки и diff;
  повторных runtime tests/import/connect, изменений VPS/AWG2/package016 нет.

- Уточнена версия [DefaultVPN с .conf NAME_FAIL](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#результат-conf--скриншот-получен-2026-09-20):
  UI показывает 2.0.1.1 (Aug 22 2026, cb7ea0c). Второй скриншот под тем же
  локальным именем отделён по SHA256 от первого. Версия iOS, параметры, restart
  и остановка переподключения не подтверждены. Проверка: оба изображения и hashes,
  readback/ссылки/diff; это docs-only, без повторного импорта, подключения или code fix.

- Зафиксирован [DefaultVPN .conf NAME_FAIL](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#результат-conf--скриншот-получен-2026-09-20):
  пользовательский скриншот после инструкции импорта показывает Server 1 вместо
  Neobyatnaya.NET и Reconnecting…. Предложено остановить попытку; её причина,
  остановка, build и сохранение параметров пока UNKNOWN. Native vpn:// NAME_PASS
  от 16.09 остаётся отдельным результатом. Проверка: изображение, SHA256, согласованность
  записи, ссылки и diff; код, runtime-тесты, выдача и серверы не менялись/не запускались.

- Завершён независимый review локальных recovery observations (b8bb1c8..86e4adc):
  Critical/Important/Minor замечаний нет. [План и границы](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md)
  переведены в LOCAL_IMPLEMENTED_TESTED_REVIEWED_NOT_LIVE_APPROVAL; очередь Phase16
  согласована с локальным результатом. Сохранено evidence 164 targeted PASS,
  проверены 53 локальные ссылки, diff и changelog; docs-only завершение без повторных тестов.
  Ручные Snapshot в обход parser, достоверность источника и live recovery не проверены;
  остальные подсистемы не объявлены прошедшими regression. VPS/AWG2/package016 неизменны.

- Добавлено [сравнение recovery snapshots](scripts/vps/phase16_recovery_observation.py):
  проверка контекста/порядка, отдельные исходы смены идентичности, появления,
  отсутствия в scope и UNKNOWN при query failure. Эти исходы не разрешают cleanup.
  RED: 39 проверок отсутствующей функции; GREEN: 164 PASS (137 новых + 27 metadata).
  [План](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md)
  и очередь обновлены; заключительный review пока ожидается. I/O/collector,
  live stage/install, AWG2, package016 и выдача остаются вне изменений.

- Реализован [локальный parser recovery observations](scripts/vps/phase16_recovery_observation.py):
  строгий canonical JSON до 64 KiB, проверка bindings/host/query/scope и пяти видов
  идентификаторов, неизменяемые снимки и фиксированная ошибка без исходного ввода.
  [План и evidence](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md):
  98 ожидаемых RED до появления модуля → 98 PASS. Сравнение ещё не реализовано;
  I/O/collector, ownership/quiescence GO, VPS, выдача и package016 не добавлялись/не менялись.

- Подготовлен [локальный recovery-план](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md):
  строгие наблюдения и сравнение идентификаторов вместо принятия имён/PID за
  доказательство владения. По source записаны недостающие creation/process bindings,
  критерии будущего ownership/quiescence evidence и 2 локальные задачи с тестами.
  Реализация/collector/cleanup не выполнялись; metadata не разрешает live действия.
- План связан с единственной очередью Phase16. Проверка: адресный source readback,
  официальный контракт /proc/cgroup/inspect, самопроверка плана, ссылки и diff;
  runtime tests, SSH, stage/install и повтор старых diagnostics не запускались.

- Выполнена [сверка AWG Go](research/amn2/phase16-awg-go-pinned-runtime-review-2026-09-20.md):
  declared source старее двух fixes; отдельно обнаружен пробел image/source binding.
  SHA256 публичных manifest/config/layer проверены, бинарник прочитан в памяти без
  запуска; exact source не подтверждён. Применимость ограничена настройками шаблона.
  Добавлен один P2 candidate; weekly cursor, runtime, package016 и выдача не изменены.
- [Первый GitHub CI](docs/CHANGELOG_GATE.ru.md#первый-github-run--подтверждено-2026-09-20)
  для 3eb18f6 подтверждён SUCCESS по run/job/steps. Документирована граница между
  успешным workflow и отдельно настраиваемыми required checks. Локальные тесты
  повторно не запускались; проверки этого пакета — source/readback, ссылки и diff.

- Добавлен [автоматический changelog gate](docs/CHANGELOG_GATE.ru.md): проверка
  index перед commit и каждого нового commit перед push; поздняя общая запись
  не закрывает пропуски. Учтены датированные записи, формальные исключения с
  причиной, старая история и остановка при недостаточных Git-данных.
- Подготовлены версионируемые hooks и GitHub workflow с read-only token,
  полным checkout и закреплённым action SHA. Обновлены AGENTS и навигация.
  26 integration tests PASS, включая реальные hooks и push во временный
  локальный bare repository; исправлен относительный путь из вложенной папки.
  По review исправлены трактовка буквальных # строк после trailer и неявный
  lazy fetch Git: оба дефекта воспроизведены RED, добавлены regression tests.
  Hooks подключены только в активном worktree, config readback выполнен;
  2 markdown-hygiene tests и диапазон двух предыдущих commits PASS.
  Смысловое review остаётся обязательным. CI/required checks ещё не подтверждены;
  серверы, VPN, выдача и package016 не изменены.
- Синхронизирован DefaultVPN: NAME_PASS через vpn:// подтверждён скриншотом
  16.09, .conf и параметры остаются открытыми. В [чеклисте](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md)
  подготовлен короткий вечерний сценарий без повторения paste/Windows проверок
  и без изменения рабочего профиля «Испания».
- Старый .conf в Temp отсутствовал; синтетическая fixture восстановлена в
  отдельной папке Downloads из ранее проверенного native ключа, 417 bytes,
  SHA256/readback и параметры проверены. В Git payload/ключи не добавлены.
- Read-only upstream на 20.09 14:40 MSK: #3043 без новых ответов, #3113 открыт
  и не слит. Ссылки/diff документации проверены; code/тесты повторно не запускались.

- Выполнен шаг 2 [format_version review](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md):
  NO_CHANGE_REQUIRED для текущего exporter. Записана матрица missing/0/1/future
  и malformed типов, source/build границы DefaultVPN. Целевые 52 offline tests
  PASS; exporter/legacy/delivery не менялись. Новый importer/restore не создаётся.


- По запросу оператора оформлены [реестр upstream](docs/UPSTREAM_INTAKE.ru.md)
  и [план format_version](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md),
  добавлены переходы из AGENTS/START_HERE и существующей P3-карточки.
  Уточнено: native exporter уже существует, missing version upstream принимает
  как 0; несовместимость не доказана. Первым идёт проверка применимости.
- Исправлены границы выводов weekly: неполные issues/PR/AWG coverage и 161-commit
  диапазон Panel не считаются полностью проверенными; IPv6 DNS не приравнивается
  к двух-IPv4 fix, а pooled SSH не является основанием отклонять event-loop isolation.
- Проверка пакета: адресный readback, локальные ссылки, diff/whitespace;
  runtime/code/tests, Phase16 gates, package016 и общая выдача не изменяются.
  Запись документации выполняется штатным apply_patch с одобренным повышением
  доступа; неисправность sandbox ACL этим не объявляется устранённой.

- В [кандидаты AMN2](ideas/candidates-for-amn2.md) добавлен отдельный P3 design
  candidate по upstream PR #3184: версионирование собственного JSON/envelope,
  отказ до side effects, import/restore tests и redaction. GitHub merge SHA и
  diff проверены. Это planning-only, не реализация или изменение Phase16.
- Проверка: readback и diff/whitespace; существующие профили, форматы, выдача
  и серверы не изменены. DefaultVPN .conf test остаётся незавершённым.

## 2026-09-13

### Правила и документация

- Создан этот журнал, добавлена навигация из START_HERE. В AGENTS.md введено
  обязательное обновление changelog в том же commit для существенных изменений
  кода, настроек, правил, инструкций и результатов проверок. Исключение для
  правок без изменения смысла требует явного обоснования в commit body.
- Проверка: readback, staged diff/whitespace и локальные ссылки. Изменения
  только документационные; автоматический commit/CI gate не установлен.

## 2026-09-12 — ретроспективно

### Проверено: импорт Windows

- AmneziaVPN local 5.0.1.5 + PR #3113: имя Neobyatnaya.NET и metadata MTU1280
  сохраняются; в backup двух профилей совпали 45 ожидаемых полей каждого.
  Повторный импорт создаёт одноимённый дубль.
- AmneziaWG official 3.1.0 x64: имя и MTU1280 сохраняются после полного выхода;
  UI-параметры проверены, одноимённый повторный импорт отклоняется. Пропуск
  PersistentKeepalive=0 объяснён официальным serializer, исправление не требуется.
- DefaultVPN остаётся NOT_RUN на iOS. Windows import PASS не закрывает Windows
  traffic FAIL/quality FAIL и не переключает delivery. AWG2_UNTOUCHED.
- По просьбе оператора в тестовом .wsb включён clipboard и добавлена guest-only
  настройка EN/RU Alt+Shift. Статические проверки PASS; фактическая работа обоих
  механизмов отдельно не подтверждена.
- Evidence: [receipt](research/amn2/phase16-windows-import-acceptance-2026-09-12.md),
  commit `4447dc4`; push в согласованную ветку подтверждён readback SHA в задаче.

## 2026-09-11 — ретроспективно

### Проверено: начальный импорт в Sandbox

- Исправленная сборка AmneziaVPN запущена в offline Sandbox; правильное имя
  сохранилось после полного открытия, отдельный MTU1280 подтверждён в preview.
  Полная проверка backup выполнена позже, см. 2026-09-12.
- Evidence: [build/import receipt](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commit `78e8815`.

## 2026-09-09 — ретроспективно

### Подготовлено: локальная сборка

- Собрана AmneziaVPN 5.0.1.5 с upstream MTU fix PR #3113. Одна попытка сборки,
  0 циклов исправлений; ZIP CRC и SHA проверены. Build Tools/SDK установлены
  по разрешению, Qt/Conan/Python изолированы по каталогам.
- Подготовлен offline Sandbox launcher. Рабочий VPN не заменён; service installer
  candidate на хосте не запускался. Сам build PASS не означал import/traffic PASS.
- Evidence: [receipt и SHA](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commits `fe31852`, `5560e5d`.
