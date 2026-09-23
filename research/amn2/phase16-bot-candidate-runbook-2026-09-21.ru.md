# Отдельный bot candidate — 2026-09-21

Статус: LOCAL_CANDIDATE_NOT_DEPLOYED.
[Конкретный startup/fence/backup/recovery дизайн](#startup-fence-backup-design-2026-09-23)
подготовлен локально; новые live scopes ожидают согласования. Это локальная подготовка по разрешению
оператора, не разрешение upload/install/activation. Единственная очередь работ —
канонический план Phase16 в AMN3. Package016 не входит в этот пакет.

Источник: AMN2 6e682356ed14a62d636ee58039fd3a389e794809.
Цель зависимостей: CPython 3.12, Linux x86_64, glibc 2.39.

## Состав и проверка

- source.tar: README.md, весь app (159 файлов всего с locks/helper), два
  неизменённых lock-файла, scripts/phase15_dependency_lock.py. Полный app нужен
  из-за общих импортов; это не установка/активация web/API/agent.
- test-support.tar: tests и pyproject.toml, отдельно от runtime source.
- wheelhouse/runtime: 40 wheels из runtime lock.
- wheelhouse/test-only: 8 дополнительных wheels; test lock включает все 48.
  Production environment должен получать только runtime lock/40 wheels.
- requirements: точные копии двух locks из Git archive.
- manifest.json: SHA256 всех payload files и архивных entries. Сам manifest
  связан внешним SHA256 в receipt; содержимое архива не является новым trust root.
- verify_candidate.py: только проверка файлов/архивов/хешей, без extraction,
  импорта приложения, установки, сети или чтения environment/DB.

Перед любым будущим применением сначала проверить внешний SHA256 bundle,
затем manifest SHA256 из AMN3 receipt, затем выполнить:

~~~text
python3 -I -B verify_candidate.py
~~~

Пакет не содержит .env, servers.yml, runtime.env, DB, токена, service units,
live configs или Windows venv. Существующие deployment scripts не включены.
Все source/locks взяты git archive exact commit; pip download использовал
require-hashes, binary-only, официальный https://pypi.org/simple, без установки.

## Исторический дизайн Linux-проверки — исполнен отдельно 22.09

Последующий [isolated Linux gate завершён PASS](phase16-bot-linux-isolated-gate-2026-09-21.md#isolated-linux-pass-2026-09-22):
offline test48/pip metadata, negative control и 6 signal tests без SKIP.
Ниже сохранён исходный дизайн 21.09, а не команда повторного запуска.
Retained test-venv содержит 48 pins и не годится как production runtime40.
Статус NOT_RUN внутри immutable manifest относится к моменту создания;
не менять manifest и не пересобирать candidate ради обновления статуса.

Отдельный будущий scope: один retained каталог
/opt/amn2-spain/bot-candidates/phase16-bot-candidate-20260921-6e68235-001;
если он существует — STOP, не перезаписывать. Лимиты: bundle <=64 MiB,
unpacked payload <=128 MiB; общий gate <=300s, тесты <=120s/256KiB,
signals только собственным disposable child, 10s/child.
Создать test venv без system-site-packages только если уже имеющиеся
/usr/bin/python3 venv/ensurepip пригодны; если нет — STOP, без apt/pip bootstrap
из сети. Сеть для dependency install не нужна: no-index/require-hashes.

Предлагаемый порядок внутри нового каталога после отдельного разрешения:

1. Проверка binding/платформы/доступного диска и внешних SHA256; безопасная
   распаковка проверенных tar в новый source, без links/path traversal.
2. Отдельная test-venv, offline установка requirements/phase15-test-py312.lock
   с --no-index --require-hashes --only-binary=:all: и find-links двух wheel dirs.
   pip check и сверка installed metadata против всех 48 pins.
3. Чистый environment: не загружать /etc/amn2-spain/runtime.env, .env,
   bot token, DB или service EnvironmentFile. VPS_APPLY_ENABLED=false,
   AWG3_BOOTSTRAP_ENABLED=false; cwd — новый пустой test scratch.
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1; -I -B; явный sys.path только candidate source.
4. Один test-only negative control с пропущенной pending delivery по Task3
   lifecycle plan: ожидаем trace assertion failure. Только disposable копия
   helper, production source неизменён; штатные hashes перепроверить перед GREEN.
5. Один штатный запуск tests/bot/test_lifecycle_signals.py: ожидаются 6 PASS,
   0 SKIP, 0 FAIL. Сохранить JUnit/normalized result. Реальные bot/web units
   не останавливать/не сигналить; app.main main() и polling не запускать.
6. На любом отклонении STOP с evidence. Автоматический повтор/cleanup запрещён.
   Новая папка/venv остаются retained, службы и общий source/DB неизменны.

Эти шаги ещё не являются готовым remote runner. Перед исполнением нужен
checksum-bound single-attempt runner с проверкой внешнего bundle SHA, owner
child cleanup/caps и доверенного SSH target. Разрешение на этот gate не
равно разрешению activation либо установке runtime venv для production.

## БД и совместная работа с web

create_workflow вызывает initialize_schema, seed_default_plans и
ensure_default_server/_sync_server_config. Даже VPS_APPLY_ENABLED=false
не делает startup read-only. Две синтетические DB из схем 55dc243/910539e
проверены отдельно: старые columns/5 fixture rows сохранены, повторный
initializer идемпотентен, старый initializer не удалил новые columns,
старый Repository прочитал данные и записал синтетического пользователя.
Это не тест всех бизнес-таблиц, concurrent writers или живой DB.

Выявленные ограничения:

- seed_default_plans перезаписывает name/price/is_free/is_active стандартного
  days_30 (max_devices сохраняется); это существующее поведение, не новая
  регрессия lifecycle fix. Факт наличия кастомных тарифов в live DB неизвестен.
- Поздняя ошибка partial Phase15 schema не отменяет ранее созданные таблицы.
  initialize_schema целиком не является атомарной миграцией.
- [Сверка 23.09](phase16-bot-integration-readback-contract-2026-09-22.ru.md#source-history-reconciliation-2026-09-23)
  установила совпадение всех 102 наблюдаемых Python-файлов с 55dc243.
  Позднее011 собрал static dependencies и полную scoped schema metadata (см. readiness ниже);
  exact deployed release, effective runtime binding и semantic DB compatibility UNKNOWN.

Readback011 закрыл сбор scoped schema metadata без пользовательских строк.
До activation остаются полный old release/effective binding, согласованный
writer fence для всех писателей общей БД, пределы offline совместимости
старого кода и миграции, startup seed policy и failure recovery. Текущий запрет менять web не снимается
молча: если миграция требует остановки web, это новый scope/решение оператора.
Нельзя запускать candidate на shared DB для проверки того, что получится.

## Будущий switch и rollback — дизайн, НЕ КОМАНДА К ИСПОЛНЕНИЮ

Сохранить старые /opt/amn2-spain/runtime/source и runtime/site-packages;
существующую bot identity/token, /etc/amn2-spain/runtime.env и shared DB.
Новый production source/venv — отдельный release directory. Поменять только
amn2-spain-bot.service через один checksum-bound drop-in с WorkingDirectory,
ExecStart и проверенным PYTHONPATH binding; общий web unit не менять.
Не подставлять пример unit и не менять Restart/no, Timeouts или limits попутно.

Перед switch: подтверждённый exact old unit/source/dependency revert target,
отсутствие посторонних pollers, backup со своей provenance и schema gate.
Старый poller должен завершиться до любого нового. Kill/timeout/drain UNKNOWN
блокирует автоматический restart/rollback. READY отдельно от menu /start и
от quality acceptance. Реальная выдача/peer creation остаются выключены.

Возврат до первого запуска candidate: убрать только свой новый drop-in,
перечитать units и вернуть прежний bot entrypoint, сохранив остальные файлы.
После запуска candidate: возврат старого кода разрешён только при доказанной
совместимости изменённой DB и отсутствии незавершённых операций. Если этого
нет — STOP/recovery; не восстанавливать DB поверх продолжающих писать web/
других клиентов. Backup сам по себе не разрешает DB restore.
Старый release, package016 и новые evidence не удалять.

<a id="switch-readiness-2026-09-23"></a>

## Готовность bot-only switch — 2026-09-23

Это уточнение прежнего дизайна и prerequisites, не исполняемый gate.
Новая сборка и повтор завершённых isolated Linux/worker проверок не нужны.

По exact approval [readback011 завершён полностью](phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-011-complete-2026-09-23).
Собранная metadata18 таблиц совпадает с old55dc243; зависимости прежние27/13/0/3,
1pth. В bounded scan один holder — bot; это не полный перечень writers.
Bot/web active/running, PID/startticks стабильны, stop timeout90s у обоих;
bot start40s/Restart=no, web start90s/Restart=on-failure. Scope readback закрыт,
новый collector gate для этих уже полученных фактов не нужен. SQL bodies/rows,
effective runtime binding, writer quiescence и startup policy не доказаны.

| Условие | Что уже доказано | Что нужно до переключения |
| --- | --- | --- |
| Candidate source/runtime | Exact source 6e68235, immutable ZIP/manifest; isolated test48 включает runtime40 | Отдельный production venv только runtime40; checksum/readback его source, interpreter, installed metadata и unit binding в будущем stage |
| Старый release для возврата | Python source снимка009 совпал с 55dc243; unit snapshot имеет ожидаемые entrypoint/cwd | Подтвердить полный сохраняемый старый release, dependency identity и эффективный unit/env binding; Python match не заменяет это |
| Shared DB | Metadata18 таблиц011 совпала с old55dc243; synthetic переход и старый repository проверены ранее в ограниченном scope | Закрепить пределы совместимости: SQL/default/CHECK/rows не наблюдались; candidate добавляет11 таблиц/4 triggers и меняет3 таблицы; startup неатомарный |
| Startup writes | Известны schema/seed/server-sync writes и неатомарный startup | Явная policy для days_30 и server sync на фактическом состоянии; не трактовать «нулевой бот» как пустую DB |
| Writer fence и backup | В011 один observed holder bot; coverage scan полная в его границах, writer completeness UNKNOWN; lock не покрывает web/API/CLI/agent | Полный список writers и способ их quiescence, согласованный с scope; проверяемый backup/restore target и provenance при этом fence |
| Stop/start/recovery | Linux signal tests PASS;011 подтвердил bot start40s/stop90s, web start90s/stop90s, стабильные PID и KillMode control-group | Эти unit budgets не доказывают фактический drain; отсутствие второго poller, подтверждённое завершение старого до запуска нового; UNKNOWN ведёт в STOP/recovery |

Порядок допуска после011: offline закрепить startup policy/rollback и writer
fence, используя собранную old metadata и прежние ограниченные synthetic
проверки совместимости. Новые live evidence запрашивать только под конкретный
оставшийся prerequisite, не повторять завершённый readback. Только после этого готовить
exact stage/switch approval с реальными hashes, unit values и stop-conditions.
Не подменять отсутствующие факты типовым unit или выдуманным timeout.
Если writer fence требует остановки web, это изменение scope для решения
оператора до подготовки live-команды. Ни один из этих пунктов не разрешает
автоматическую остановку, запуск poller, восстановление DB или выдачу.

Local readiness остаётся неполной по effective runtime binding, startup policy,
writer fence/backup и recovery; сбор scoped DB metadata завершён;
Task3B, Windows traffic и Task4.5 не закрыты. Их приоритет и очередь сохраняет
канонический план Phase16, а эта таблица не вводит параллельный execution plan.


<a id="startup-fence-backup-design-2026-09-23"></a>

## Startup, writer fence, backup и recovery — проект решения 23.09

**DESIGN_APPROVED / LOCAL_CORE_IMPLEMENTED / LIVE_EXECUTOR_NOT_READY.**
Оператор согласовал локальную реализацию после design commit0928ca0.
[Результат реализации и оставшиеся границы](#maintenance-local-core-2026-09-23) ниже.
Основание: операторское «приступай» к локальной подготовке после публикации
9cb5706. Scope этой работы — чтение exact source и конкретизация существующего
runbook; не новый execution plan. AMN3 HEAD9cb570646f3f22df8c2c4ff70a062707c1a7508f,
AMN2 HEAD6e682356ed14a62d636ee58039fd3a389e794809 чистые при проверке.
Readback011 завершён; повторять его ради подготовки решения не нужно.

### Выбранный вариант и существенные альтернативы

Предлагается короткое обслуживание **bot и web**, без обновления кода web,
с сохранением bot identity/token, shared DB и старого release. Перед первым
production запуском candidate — backup на том же VPS и закрытая rehearsal
на отдельной копии; разрешены только ожидаемые schema additions/backfills,
стандартные недостающие seed rows и служебные timestamps по policy ниже.

Оставить web работающим пока не подходит: его exact old source55dc243
`app/web/app.py:2195–2201`, `_open_repository`, вызывает initialize_schema
при открытии repository. Один observed bot holder011 не исключает последующее
открытие БД web/API/CLI/agent. Одного bot lock или краткого пустого FD scan мало.
Создавать пустую БД/новую bot identity для обхода миграции не предлагается:
это не сохраняет текущие данные и не закрывает задачу интеграции.

### Проверенные записи при startup и предлагаемая policy

Source references ниже относятся к exact6e68235, если не указан55dc243.
Это чтение кода, не запуск приложения и не новые runtime tests.

| Место | Наблюдаемое поведение | Допуск перед production startup |
| --- | --- | --- |
| `app/main.py:410–414` | connect → initialize_schema → Repository → seed_default_plans | Проверить полный этот путь на копии; не считать отключение VPS_APPLY_ENABLED read-only режимом |
| `app/db/repositories.py:15,2485–2545` | Восемь seed plans: days_3/7/10/14/30/60/90/180. Upsert меняет name, duration_days, price, currency, is_free, is_active, updated_at; max_devices сохраняется при None | Существующие business values сохранять: перед seed проверить совпадение со штатными значениями. Несовпадение → STOP без исправления; отсутствие стандартного плана допускает штатное создание после согласования policy. Изменение updated_at явно допускается |
| `app/main.py:416–427` | При VPS_APPLY_ENABLED=false ensure_default_server(name=local); при true _sync_server_config | Предлагается candidate VPS_APPLY_ENABLED=false и AWG3_BOOTSTRAP_ENABLED=false с фиксацией в scoped bot drop-in. Если это расходится с утверждённой функцией текущего bot — STOP/решение оператора, не молчаливое изменение общей конфигурации |
| `app/db/repositories.py:405–443` | local server INSERT ON CONFLICT(name) DO NOTHING | Существующую запись не менять. Отсутствующую стандартную local запись разрешить создать только в рамках этой policy; она не означает создание VPN peer/контейнера |
| `app/main.py:493–510`, repository `2273–2337` | При включённом apply upsert server меняет host/ssh_port/endpoint/vpn_port/network/address/public_key/runtime/firewall/max_devices и updated_at | Этот путь исключён выбранной policy. Не читать/переписывать servers.yml или server rows ради включения apply; для этого потребуется отдельное решение |
| `app/services/phase15_bootstrap.py:451–487` | Bootstrap loader вызывается при enabled; при false он не вызывается | Проверить effective flag=false. Constructors Awg3ControlService и TelegramCallbackStateService только сохраняют параметры; это не разрешение выдачи |
| Exact55dc243 `app/web/app.py:2195–2201` | Старый web вызывает старый initializer при открытии repository | В rehearsal после candidate schema применить старый initializer и проверить сохранность новой схемы/старых данных; проверить repository smoke без сетевых вызовов |

Не считать custom plans отсутствующими потому, что бот назывался «нулевым».
Policy проверяется по фактической копии; её данные не выводятся. Если seed
меняет существующие business values, текущий immutable candidate к switch
не допускается. Решение: отдельно согласовать изменение данных либо bounded
source fix и новый candidate; не monkeypatch startup и не редактировать bundle.

### Политика данных и проверка на копии

Предлагаемое будущее разрешение должно явно включать server-local чтение
данных для проверки/backup: прежний readback011 разрешал только metadata.
Backup и rehearsal содержат конфиденциальные строки; хранить исключительно
на VPS в новых каталогах с минимальными правами, без Git/выгрузки в чат/на ПК.
В report — PASS/STOP, counts, file hashes и фиксированные причины, без значений
строк, raw SQL ошибок, ключей, env contents и Telegram identifiers.

1. Сохранять source archive/locks/unit drop-in fingerprints и полный старый
   runtime revert target; проверить dependency/source/interpreter binding.
   Не заменять старый source/site-packages, не использовать test-venv48 как runtime40.
   Эффективные настройки проверять на сервере только сравнением с allowlist;
   секреты не выводить и не менять. Нужен доказанный единственный poller.
2. После writer fence создать новый backup через
   [SQLite Backup API](https://www.sqlite.org/backup.html), завершить/закрыть
   соединения, хешировать конечный artifact, проверить integrity и separately
   [foreign_key_check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check).
   Backup API даёт согласованный snapshot, но сам не запрещает последующие
   записи — fence нужен независимо от него. Не копировать только main file
   при возможных WAL/sidecars и не удалять sidecars для обхода отказа.
3. Из проверенного backup создать отдельную disposable rehearsal DB. Network
   и bot token ей недоступны; app.main/polling не запускать. Helper вызывает
   только exact schema/repository startup operations с явно заданными параметрами,
   не общий application bootstrap. Закрыть source connections до сравнения.
4. Сравнить все старые таблицы/columns/PK и данные на сервере по устойчивым ключам,
   отдельно разрешить документированные migration backfills (например,
   passport/generation связи), новые tables/triggers и seed policy выше.
   Полный delta allowlist ещё должен быть выведен из exact migration source
   при реализации helper: пример backfill не разрешает любые изменения.
   Удаление старых rows, неожиданные replacements/изменения значений или
   constraints/integrity failures → STOP. Не выдавать raw rows/row hashes наружу.
5. После повторного initializer и old web/repository path проверить повторяемость,
   ожидаемую candidate shape, старые данные, integrity/FK. Smoke writes только
   на disposable clone, с фиксированными synthetic identifiers; backup immutable.
   До baseline PASS не переходить к production DB. Сохранить normalized result
   и hashes. Это новый data-specific rehearsal, а не повтор прежних synthetic tests.

### Writer fence и окно обслуживания

Дополнительный scope на будущее: остановка/возобновление обоих units bot/web,
временное блокирование их автоматического старта, пауза всех известных иных
writers/schedulers и ручных CLI операций на время изменения БД. Это **ещё не
разрешено**. Код/config web и VPN/AWG2 units не менять. Bot drop-in меняет
только его release/interpreter/cwd/import binding и два согласованных флага.

Перед первым stop подготовить exact writer inventory и способ удержания
fence для каждого владельца: units, socket/timer/agent/cron/manual entrypoints,
включая возможный внешний poller. Из source известно наличие классов writers,
их фактическая конфигурация на VPS неизвестна. Нет закрытого inventory или
возможности блокировать новый start → STOP до обслуживания, без угадывания.
Не заменять это advisory SQLite lock, chmod общей БД или обещанием «FD сейчас нет».

Maintenance runner должен сохранять исходное active/enabled/masked состояние,
различать свои временные изменения и чужие; не unmask/enable чужие units.
Конкретный механизм runtime start inhibition и recovery после потери SSH
должен быть реализован и проверен локально до exact live approval. Root/operator
обходы исключаются согласованным maintenance ownership, не недоказанной
абсолютной защитой. Не выполнять произвольные cron/unit остановки по поиску.

Последовательность: закрыть admission/start writers → остановить bot с drain
и web → подтвердить завершение старых PID/cgroups и сохранение fence → backup
и rehearsal → ограниченный production schema/seed helper без сети → baseline
после migration → один candidate bot start → проверка READY/локальных receipts
→ запуск прежнего web и проверка → снять только свои временные ограничения.
Возобновление других writers — только по сохранённому manifest и результату.
Общая issuance остаётся disabled; operator /start и delivery — отдельный scope.

Фактические budgets011: bot start40s/stop90s, web start90s/stop90s; KillMode
control-group, signals15/9. Их не менять попутно. Timeouts, forced kill,
неполный drain, неизвестные in-flight операции или процесс вне cgroup → STOP,
без автоматического нового poller/restore. Telegram admission setting допускает
1..120s в source, actual значение ещё не прочитано; проверить совместимость
с bot start40s, не молча увеличивать timeout.

### Recovery: граница до и после polling

`app/main.py:149–157` создаёт workflow до polling; `170–190` запускает polling
до уведомления READY. **Отсутствие READY не доказывает отсутствие обработанных
сообщений.** Recovery не может использовать READY как границу безопасного restore.

| Фаза отказа | Допустимый маршрут после будущего точного разрешения |
| --- | --- |
| Stage вне shared DB/до stop | Оставить действующие units; сохранить failed stage, не переиспользовать каталог |
| Writers остановлены, production DB ещё не менялась | После проверки исходной DB/файлов вернуть прежние units и снять только свой fence; неизвестный drain → удерживать STOP |
| Production migration началась, candidate процесс ещё ни разу не запускался | При доказанном непрерывном fence восстановить проверенный backup через staged replacement с сохранением failed DB/sidecars, owner/mode и validation. Затем прежние units. Потерян fence → автоматический restore запрещён |
| Candidate start уже запрошен, независимо от READY | Считать, что polling/записи могли начаться. Сохранить текущую DB, остановить/дренировать только разрешённые процессы; автоматический restore старого backup запрещён. Отдельно решить code-only revert на текущей DB после совместимости либо data recovery с учётом принятых событий |
| Пропала связь, runner завершён/состояние неизвестно | Не повторять gate и не возвращать старый poller вслепую. Read persisted operation state; неизвестная фаза означает STOP/ручное восстановление |

Runner должен иметь persistent phase journal без секретов и выделенный запас
на recovery; timeout не означает автоматическое снятие fence или unmask.
Revert старого кода после новой схемы требует доказательства по clone и
проверки текущих pending operations; прежних5 synthetic rows для общего
автоматического разрешения недостаточно. Backup хранить до принятого closeout;
его удаление и restore поверх активных writers не входят в этот проект.

### Объём следующей реализации и согласования

1. Согласовать этот вариант и scope **на подготовку**, включая проект краткой
   остановки web, закрытые server-local backup/data checks и policy seed.
   Это не live approval и не разрешение Telegram сообщений.
2. Локально подготовить один согласованный набор runner/receipts с фазами
   stage → fence/rehearsal/migration → start/recovery; derive exact mutation
   allowlist из source, negative controls для failures до/после polling,
   таймаутов, потерянного fence, неверного backup/bindings и восстановления.
   Не расширять старый readback collector и не запускать серию012/013.
3. Перед исполнением представить конкретные artifact hashes, writer inventory,
   paths, recovery procedure, limits и exact scopes. Stage можно делать до
   downtime только по отдельному live approval; maintenance включает заранее
   согласованные внутренние проверки, а не новое разрешение на каждый PRAGMA.

Рабочая оценка после согласования дизайна:60–90мин локальные runner/tests;
дальнейшее live stage ориентировочно до5мин, maintenance целевое окно10–15мин
при отсутствии STOP и наличии всех prerequisite. Это плановые пределы,
**не обещание общего времени закрытия Phase16** и не готовые timeout constants.
Точное окно и recovery reserve закрепить по реализованному runner до approval.
Windows/quality/A-B остаются самостоятельными условиями acceptance.

В этом ходе: source-only review, official SQLite docs, docs readback/links/
diff/secret review; тесты/backup/SSH/stage/install/activation0, AMN2/package
не менялись. Новые runner и migration allowlist пока не реализованы.

<a id="maintenance-local-core-2026-09-23"></a>

## Локальное ядро maintenance — результат 23.09

**LOCAL_CORE_PASS / LIVE_EXECUTOR_NOT_READY / NO_LIVE_AUTHORIZATION.**
По «приступай» реализованы два модуля и их offline tests. Это материальная
подготовка согласованного дизайна, не новый collector012 и не live gate.
[Машинный receipt](phase16-bot-maintenance-local-verification-2026-09-23.json):
**39 PASS / 0 FAIL / 0 SKIP, 11.468s**, Windows/Python3.12.14/SQLite3.53.1.
Self-review выполнен; независимый review не проводился, делегирование не было
разрешено. Readback011, bundle/package016 и source AMN2 не изменялись.

### Реализовано и чем проверено

- [DB helper](../../scripts/phase16_bot_db_rehearsal.py): pinned schema snapshots
  и AST-selected exact repository methods из55dc243/6e68235; без импорта app.main,
  env/token/polling. Backup API в новый файл0600, integrity и FK separately,
  hash закрытого backup, отдельный disposable clone, strict schema/data delta,
  повторный initializer и старый initializer/repository read/write smoke на clone.
  WAL snapshot проверен с открытым synthetic writer и неперенесёнными строками:
  только новая копия переводится штатным SQLite PRAGMA в DELETE для автономного
  artifact. Исходный journal mode/sidecars не меняются и не удаляются helper.
- [Maintenance core](../../scripts/phase16_bot_maintenance.py): точный ordered
  coordinator fence → stop → backup → rehearsal → migrate → candidate start →
  web start → release; intent fsync до каждой операции, manifest/unit baseline,
  chained event files, exclusive execution claim. Повтор/продолжение незавершённого
  intent запрещены. Ошибка любого этапа прекращает последующие действия, без
  automatic cleanup/unmask/restart/restore. Stage snapshot verifier использует
  существующий pinned manifest126 source files/runtime40; test-venv48 отклоняется.
- Конкретный fence adapter создаёт только свой persistent drop-in с
  `ConditionPathExists=/run/phase16/<operation>/<unit>.allow`. По умолчанию permit
  отсутствует; созданный до start permit удаляется после вызова, в том числе
  при обычном timeout exception. Crash оставляет intent/lock и может оставить
  permit: **STOP/manual recovery**, не доказанный запрет любого будущего start.
  При reboot `/run` очищается, persistent condition остаётся; boot identity
  должна перепроверяться. Чужие unit/drop-in/masked/enabled настройки не меняются.
  Механизм основан на [systemd unit conditions/drop-ins](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.unit.xml).
  Linux/systemd execution не проводилось; commands проверены injected executor.
- Explicit restore разрешён кодом только до candidate-start intent, при
  подтверждённых fence/drain/same boot и проверенном backup. Он сохраняет failed
  main/WAL/SHM/journal в новый archive, готовит проверенный replacement, сохраняет
  mode и на POSIX owner/group, записывает recovery claim. Повтор и движение вперёд
  блокируются; процессы не запускаются. Partial filesystem failure требует
  отдельного разбора сохранённых файлов/журнала, автоматического resume нет.
  Ни одна такая операция на VPS в этом ходе не выполнялась.

[DB tests](../../tests/test_phase16_bot_db_rehearsal.py) используют synthetic rows
во **всех18 старых таблицах**, включая BLOB, ссылки passport/device/receipts,
custom max_devices и timestamps. Проверены row deletion/change/addition,
нештатные seeds, schema drift, FK violation, source/backup tamper, WAL, deadline
и redacted errors. [Maintenance tests](../../tests/test_phase16_bot_maintenance.py)
покрывают все8 failure phases, persisted start intent, timeout, stale writer,
crash claim, восстановление до/после polling boundary, foreign/changed drop-ins,
effective condition/reload/alias mismatch и неполный manifest.

Во время RED/GREEN исправлены Windows fsync/read-only handle и незакрытые
fixture connections; self-review закрыл WAL backup mode, mutation без intent,
restore/forward race и SQL LIKE `sqlite_%`, который пропускал `sqliteX...`.
Это исправления новых локальных модулей; прежние readback suites не повторялись.

### Точный data delta для наблюдённого old55dc

Произвольных passport/generation backfills **нет** в разрешённом переходе.
Старые строки/ключи/значения сохраняются с учётом SQLite types и multiplicity.

| Объект | Допустимое изменение |
| --- | --- |
| devices и device_passports | Четыре новые колонки protocol_version/runtime_instance_id/client_identity_evidence_status/compatibility_evidence_id, все NULL у старых rows |
| admin_config_issuance_receipts | Новые config_version/protocol_version/runtime_instance_id/compatibility_evidence_id/client_application/client_platform/client_version/client_build, все NULL |
| plans | Восемь стандартных days_N; existing business values обязаны совпадать до записи. Только updated_at может измениться; existing max_devices/created_at сохраняются. Отсутствующие стандартные rows создаются по exact defaults |
| servers | Existing rows полностью неизменны. Только отсутствующий local может добавиться с exact defaults и явно заданной network_cidr |
| sqlite_sequence | Только servers: ровно +1 к max(old sequence, old maximum id), включая ON CONFLICT DO NOTHING. Другие sequence entries не меняются |
| awg3_control_state | Ровно singleton1 с false/0 для acceptance/issuance/suspension, NULL actor/reason/receipt и штатным timestamp |
| Остальные десять новых таблиц | Пустые после startup schema/seed |
| Новая schema, indexes, triggers | Точное соответствие результату pinned old → candidate initializer; не только число объектов |

### Что ещё требуется до исполнимого live пакета

Этот commit **не содержит готового SSH/live executor**. Нет CLI, принимающего
production paths и запускающего systemctl автоматически. Callback operations
coordinator, systemctl executor и typed target observations пока не привязаны
к реальным VPS paths/hashes/config; проверки с `lambda: True` существуют только
в synthetic tests и не являются допустимой live реализацией.

Дальнейшая локальная сборка того же пакета должна связать эти модули с:

1. Exact stage/revert targets, runtime40 interpreter/source/import origins и
   artifact manifests; stage verifier сам ничего не устанавливает/не собирает.
2. Фактическим writer inventory и maintenance ownership. Текущий validator
   допускает только bot+web и доказанное отсутствие cron/agent/socket/timer/
   external poller/manual CLI. Это **не установленные факты** о VPS. Если иной
   writer найден — STOP до stop; понадобится адресная реализация его fence,
   а не установка inventory_complete=True. Effective settings/admission budget
   также ещё UNKNOWN; admission<40 — необходимая, не достаточная startup bound.
3. Проверкой effective conditions, PID/cgroup/drain/forced-kill, startup READY
   и локальных receipts, original runtime rollback evidence, pending operations.
4. Linux process wall deadline, network isolation DB helper, private parent
   directories, same-filesystem restore paths, recovery reserve и устойчивым
   запуском/наблюдением runner. In-process SQLite deadline120s/row cap200000
   не заменяют общий OS timeout и не обещают maintenance SLA.

До этих привязок нельзя выдавать `READY_TO_EXECUTE`, готовое live approval или
автоматический data rollback. Live server-local чтение строк/backup/rehearsal,
production migration, bot/web stop/start, stage и Telegram operator actions
по-прежнему требуют соответствующего точного разрешения. Локальную сборку
можно продолжать в уже согласованном scope; нового согласования дизайна не нужно.

В этом ходе SSH/live DB reads/writes/stage/install/service actions/activation=0.
AWG2_UNTOUCHED, package016 immutable, general issuance disabled. Локальные
synthetic backup/restore artifacts находились только в temporary test directories.
Production rows, env, token и protected configs не читались и не копировались.
