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

<a id="runtime40-stage-ready-2026-09-24"></a>

## Runtime40 stage: подготовка пакета — 24.09 (исторический снимок)

Состояние перед запуском: **STAGE_READY_NOT_EXECUTED / MAINTENANCE_BLOCKED**.
Обновление: approval использован один раз; [результат исполнения](#runtime40-stage-execution-001-2026-09-24)
— **UNKNOWN_NO_RETRY**, прежняя команда не подлежит повторному запуску.

История подготовки: Продолжение по «ПРОДОЛЖАЙ»
после exact push b28749a: remote branch подтвердил b28749a, оба changelog hooks
PASS. Новый scope этого пакета — только подготовка отдельного runtime40 вне
downtime. Bot identity/token/env, действующие bot/web, shared DB и AWG2 сохраняются.

Реализованы [local gate](../../scripts/phase16_bot_runtime40_stage_gate.py) и
[remote stage executor](../../scripts/vps/phase16_bot_runtime40_stage_remote.py).
[Exact target manifest](phase16-bot-runtime40-stage-manifest-2026-09-24.json)
связывает новый rendered script, frozen helper/transport/target-loader sources,
старый подтверждённый target binding, bundle/source/runtime lock и точные пути.
Исторические scripts используются только как проверенные primitives; их main/
execute и прежние approvals не вызываются, frozen файлы не менялись.

### Объём одного предлагаемого действия

После **нового точного разрешения**, один SSH запускает:

1. Проверку immutable bundle, Linux/Python3.12/x86_64/glibc2.39/root, ownership
   родителей, отсутствия destination, свободного места512MiB и unshare --net.
   Precheck failure → STOP до создания stage. Отсутствующий parent также STOP.
2. Создание только нового каталога
   `/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260924-6e68235-001`,
   private root0700 и одноразового claim. Старый candidate/test-venv48 не меняется.
3. Раскладку159 source entries и41 payload file (runtime lock +40 wheels).
   Новое `runtime-venv` создаётся `/usr/bin/python3 -m venv`; pip устанавливает
   только runtime lock с no-index/no-deps/require-hashes/only-binary. Все children
   работают через отдельный `unshare --net`, HOME/TMPDIR внутри нового scratch.
   Установочные bootstrap distributions pip/setuptools учитываются отдельно от40.
4. pip check; metadata child с `-I -S -B`, без исполнения .pth; проверку40 pins,
   лишних/повторных distributions, их origin, venv config, отсутствия .pth.
   `PathFinder` проверяет origin app/app.main **без импорта приложения**.
5. Повторное сравнение всех разложенных source/payload bytes; sanitized result.
   Успех — `RUNTIME40_STAGED_NOT_ACTIVATED`, а не bot integration PASS.

Ограничения: work280s, outer remote300s, local transport330s, attempts1,
child output256KiB, transport output64KiB. Плановое исполнение — до5мин remote,
до5.5мин с transport; затем разбор receipt. Это не оценка закрытия Phase16.
Любой отказ после claim сохраняет stage и `STOP_RETAINED_NO_RETRY`; потеря
receipt означает UNKNOWN_NO_RETRY. Удаление/перезапись старого или failed stage,
повтор, unit commands и DB operations в этот scope не входят.

### Проверка локально и точные bindings

[Receipt](phase16-bot-runtime40-stage-local-verification-2026-09-24.json):
**15 PASS / 0 FAIL / 0 SKIP**,0.765s, Windows/Python3.12.14; Linux process calls
заменены injected executor. Exact metadata child действительно выполнен на
synthetic local source, где импорт app/__init__ и app/main аварийно завершается;
child PASS доказал отсутствие такого импорта в проверяемом пути.

Negative controls: runtime48/неизвестный scope/duplicate, ошибка каждого из пяти
child calls, metadata/source origin/pth drift, approval/hash/target mismatch,
ложный PASS/лишние receipt fields, stale claim и raw-error redaction. RED/GREEN
исправил Windows `str(Path)` в wire destination на POSIX `.as_posix()` до SSH.
Self-review выполнен; независимый review не проводился. Старые39 maintenance,
125 readback и завершённые Linux lifecycle tests не повторялись.

Настоящий immutable bundle прошёл offline preview и CLI default без `--execute`:
159 source entries,126 app Python files,40 pins; runtime wheels не содержат
.pth/sitecustomize/usercustomize (0). Ничего не распаковывалось на VPS, venv/pip
на рабочем ПК не запускались; target loader/SSH в preview не вызываются.

- Rendered remote SHA256: `cfa62d3767a14904b8330f1688c7424449fab1dffa7709ed875c41ff8f10f1ae`.
- Target manifest SHA256: `e5f6d4d7dc447ca5c933230e0b857377471928dc0daa9b41208d690d5cea607c`.
- Bundle SHA256: `e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7`.
- Source: `6e682356ed14a62d636ee58039fd3a389e794809`.
- Future local evidence: `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-runtime40-stage-20260924/execution-001`.
- Approval marker: `PHASE16_BOT_RUNTIME40_STAGE_20260924_001` — **GRANTED_AND_CONSUMED_ONCE**; исходный manifest сохранён без изменений.

Историческая спецификация уже выполненной команды (не повторять): указанный bundle,
`--execute --approve PHASE16_BOT_RUNTIME40_STAGE_20260924_001`, а также оба
`--approved-remote-sha256` и `--approved-manifest-sha256` из списка выше.
Entry point — `scripts/phase16_bot_runtime40_stage_gate.py`; Python invocation
`-I -S -B`. Evidence path фиксирован внутри gate, разрешения прошлых gates не подходят.
По умолчанию CLI выполняет только offline preview. Push имеет отдельный exact SHA scope.

### Maintenance остаётся отдельной границей

Manifest содержит конкретные proposed source/interpreter/old-runtime/DB/unit
paths, но **не утверждает их live acceptance**. Writer inventory, service User/
Group, effective flags, startup budget, drain и pending operations — UNKNOWN.
Private stage root0700 ещё не доказывает доступность будущему service user.
Нет callback wiring для production migration/stop/start: stage этого не требует
и не разрешает. Не ставить inventory_complete=True по metadata011 или snapshot
одного holder. Следующее решение после stage — закрыть эти prerequisites и
собрать maintenance approval; общая issuance остаётся disabled.

Итог этого локального хода: SSH0, remote stage0, service actions0, DB reads/writes0,
activation0; AWG2_UNTOUCHED, package016 и AMN2 source immutable. Новый пакет stage
готов к рассмотрению, готовность maintenance/Phase16 acceptance не заявляется.

<a id="runtime40-stage-execution-001-2026-09-24"></a>

## Runtime40 stage001: транспорт оборвался, повтор запрещён — 24.09

**UNKNOWN_NO_RETRY / MAINTENANCE_BLOCKED.** По двум точным разрешениям оператора:

1. Push `68df5b9b7d36cd97ad94b7bcab058b10252586b6` выполнен в origin / ветку
   `codex/phase16-awg3-family-3-1-spain-pilot-016` с EXPECTED_OLD `b28749a`.
   URL/ref/ancestor проверены; NO_FORCE/NO_TAGS, hook PASS для одного commit,
   последующий remote readback подтвердил полный новый SHA.
2. Единственная SSH-попытка stage001 завершилась без remote receipt.
   [Normalized execution record](phase16-bot-runtime40-stage-execution-001-2026-09-24.json)
   сохраняет exact claim/result, их hashes, transport metadata и границы вывода.
   Local claim → result file заняло около 33 секунд; это не измерение remote work.

В stdin локального SSH записано 3 702 784 из 30 513 539 bytes; `stdin_complete=false`,
SSH returncode 255, failure_stage=`stdin_write`, stdout 0 bytes. Выходные pipes
закрылись (`output_complete=true`), но это не означает успешную передачу или
полученный серверный результат. stderr 49 bytes классифицирован как
`UNCLASSIFIED_STDERR`; raw bytes существовали только в памяти завершённого runner,
на диске сохранены лишь размер и hash. Точная причина разрыва **UNKNOWN**;
не объявлять причиной сеть, SSH settings, pip или runtime без evidence.

Локальный source trace: remote main сначала читает bundle, `execute()` вызывает
`validate_bundle()` до precheck/claim/write/venv. Frozen validator требует точный
размер 30 485 208 и SHA всего архива. При этой неполной передаче bound code не может
дойти до создания stage. Это вывод по коду и transport counters, **не server
readback**: отсутствие remote destination или состояние работающих сервисов не
проверялось. `RUNTIME40_STAGED_NOT_ACTIVATED` не получен; stage/install не приняты.

Повтор SSH, cleanup, service commands, DB operations и activation не выполнялись.
AWG2/package016/AMN2 source не менялись, general issuance не включалась. Approval 001
и local evidence directory использованы; старые scripts/manifests/receipt сохранены
без изменений. Maintenance prerequisites из manifest остаются UNKNOWN/BLOCKED.

Следующее разрешённое локальное действие: подготовить bounded transport diagnostic
с безопасной классификацией ошибок и offline partial-frame controls, сохраняя
frozen stage001. Не менять timeout/keepalive и не предлагать исправление причины
без доказательства. До любого нового SSH нужны конкретный reviewable artifact и
новое точное разрешение; этот результат не разрешает retry, probe или очистку.
Docs-only фиксация: claim/result/hash/source-order readback, ссылки и diff/whitespace;
завершённые 15/39/125 suites не повторялись. Новая запись результата фиксируется
локально; push этого нового commit требует собственного exact SHA approval.

<a id="transport-diagnostic-local-2026-09-24"></a>

## Локальная диагностика транспорта после stage001 — 24.09

**LOCAL_PASS_NOT_WIRED_TO_LIVE_GATE.** По следующему «продолжай» подготовлен
[отдельный transport module](../../scripts/phase16_bot_transport_diagnostics.py),
сохраняющий process/pipe limits frozen transport из66bbc8a. Stage001, его helpers,
manifest и использованное разрешение не менялись. Новый модуль не содержит CLI,
target loader, SSH settings, remote command, сохранения raw logs или retry.
К действующему gate он не подключён; нового разрешения SSH этот commit не создаёт.

Дополнительные данные — elapsed_seconds, last_stdin_progress_seconds,
termination_action и несколько фиксированных stderr hints вместо одной категории.
Allowlist распознаёт в том числе server-alive timeout, send-disconnect/reset/abort,
отказ подключения и Python traceback; выводит только постоянные labels, без адреса,
пути или текста ошибки. Hints не устанавливают root cause и не меняют exit status.
Unknown stderr остаётся UNCLASSIFIED, raw bytes не сохраняются; произвольную новую
ошибку по-прежнему нельзя восстановить из receipt. Output cap общий для stdout и
stderr, его срабатывание отдельно отмечается в диагностике.

[11 целевых локальных тестов](../../tests/test_phase16_bot_transport_diagnostics.py)
прошли без ошибок/пропусков за0.454s; [verification receipt](phase16-bot-transport-diagnostic-local-verification-2026-09-24.json).
Реальные Windows/Python children проверили early exit255 с неполным stdin,
несколько hints и redaction, unknown/invalid UTF8, timeout/cleanup, combined cap,
start failure, invalid limits, отсутствие retry и независимость hints от exit code.
RED подтвердил отсутствие нового модуля; при разработке исправлены quoting теста
и fixture: чтение одного byte не гарантирует завершённую запись chunk32768.
`stdin_bytes_accepted` и last-progress относятся к завершённым локальным writes,
а не к количеству bytes, полученному VPS.

Точный rendered bootstrap stage001 исполнен **локально** с synthetic partial frame
длиной3 702 784 bytes: rc3, `bundle_binding`, steps пусты, local scratch пуст.
Подмена byte в script дала rc70 до remote main. Это подтверждает validate-before-
stage для этих inputs; не воспроизводит сетевую причину, Linux install или actual
remote directory state. Production bundle/target/config/token для controls не нужны.

Попытка сопоставить сохранённый stderr hash с18 фиксированными распространёнными
сообщениями и окончаниями строк совпадений не дала. Protected target не читался;
никаких предположений о фактическом тексте/причине из этого не делается.
Stage001 остаётся UNKNOWN_NO_RETRY. Self-review выполнен; independent review не
проводился. Предыдущие suites не повторялись; frozen manifest сверён и совпал.

Следующий локальный этап — подготовить конкретный checksum-bound диагностический
SSH packet с этим модулем, собственными evidence path/approval и строгим output
validator. Он ещё **NOT_PREPARED**: этот module не является готовой live-командой
и не разрешает повтор stage001. До отдельного exact approval: SSH0, remote stage0,
install0, service/DB actions0, activation0, push0. AWG2/package016 не изменены,
general issuance не включалась. Maintenance и Phase16 acceptance остаются открыты.

<a id="transfer-diagnostic-ready-2026-09-27"></a>

## Подготовка transfer packet — 27.09 (исторический снимок)

На момент подготовки: **READY_NOT_EXECUTED**. Обновление: approval использован
один раз; [результат исполнения](#transfer-diagnostic-executed-2026-09-27) —
**UNKNOWN_NO_RETRY**, подтверждено5MiB, SSH server-alive timeout hint.

После подтверждённого push9086bc3 продолжена разрешённая
локальная подготовка. Конкретный вопрос: проходит ли одноразовая передача объёма
stage001 по прежним SSH settings, и какая последняя подтверждённая отметка/ошибка
остаётся при отказе? Это новый диагностический scope, не retry stage001.

Артефакты: [gate](../../scripts/phase16_bot_transfer_probe_gate.py),
[receiver](../../scripts/vps/phase16_bot_transfer_probe_remote.py),
[exact manifest](phase16-bot-transfer-probe-manifest-2026-09-27.json),
[verification receipt](phase16-bot-transfer-probe-local-verification-2026-09-27.json).

- Payload:30 485 208 synthetic bytes0xA5, создаётся только в памяти; объём равен
  размеру immutable bundle, но архив/source/wheels/данные приложения не передаются.
  Frame:30 487 313 bytes, включая hash-bound script и8-byte length header.
- Remote: `/usr/bin/python3 -I -S -B`, RAM-only hash/count, READY, checkpoints
  каждый1MiB и terminal COMPLETE/STOP. Нет remote file writes, application/config
  reads, subprocess, service/DB/stage/install/activation commands или outbound
  network. Штатные SSH authentication/audit side effects не считаются file writes
  скрипта и остаются обычным свойством SSH-сеанса.
- Лимиты: remote alarm90s, local transport110s, общий stdout+stderr64KiB,
  одна попытка. Cleanup локального transport может добавить до6s; лимит90s
  начинается внутри receiver после получения/проверки script, не в начале SSH.
- SSH host/key/known_hosts binding прежний, проверяется непосредственно перед
  новой попыткой; StrictHostKeyChecking=yes, BatchMode, connection attempts1,
  ConnectTimeout10, ServerAliveInterval5/CountMax1. Keepalive не перенастраивался.
- Локальный evidence directory новый и одноразовый:
  `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-transfer-probe-20260927/execution-001`.
  На этапе подготовки отсутствует. Claim сохраняется до SSH; повтор даже после
  неудачи запрещён. Frozen stage001/evidence не меняются и не очищаются.

### Выводы и stop conditions

`TRANSFER_OBSERVED_NOT_STAGE_ACCEPTANCE` возможен только при rc0, полной записи
stdin, полном output и строгом COMPLETE с ожидаемыми bytes/hash и всей очередью
progress. Это доказательство этой synthetic передачи, не исправления stage001.
Новый небольшой receiver и progress output отличаются от прежнего silent upload;
из успеха нельзя выводить причину прежнего разрыва, работоспособность pip/runtime
или отсутствие stage001 directory. Compression/traffic acceptance не проверяются.

При обрыве observer нового diagnostic transport передаёт только ограниченный
stdout prefix строгому parser до выброса transport error. Сохраняются лишь
валидные JSON events: fixed schema/approval/seq/byte checkpoints, без произвольных
полей. Незавершённая последняя строка отбрасывается с явным trailing_fragment;
искажённые/повторные/переставленные события дают INVALID и никогда PASS.
`confirmed_bytes` означает bytes, заявленные проверенным receiver event, а не
локальным pipe counter. Бounded stderr hints остаются подсказками, не root cause.

Remote STOP, incomplete transfer/output, неверный receipt, timeout или отсутствие
READY → stop/no retry; UNKNOWN не превращается в успешную установку. Никакого
автоматического следующего SSH, stage, cleanup или восстановления. Разбор этого
единственного результата определяет следующий шаг; новая бесконечная серия gates
здесь не планируется и не разрешается.

### Проверка и точное разрешение

25 PASS/0FAIL/0SKIP,1.234s включая preview/binding checks (unittest1.095s).
Реальные локальные Windows children передали весь30.5MB frame без файлов;
negative controls: truncated/extra/corrupt payload, timeout path, false COMPLETE,
extra/duplicate fields, boolean types, event order, partial JSON, wrong approval/
hash/target, stale evidence и no retry. RED: отсутствующий gate/observer API.
Windows text stdout CRLF в fixture заменён явной byte write. Linux SIGALRM здесь
не исполнялся; timeout path проверен injected stream, не Linux wall-time proof.
Новый затронутый transport suite выполнен; frozen runtime/maintenance suites не
повторялись. Default CLI preview exit0, SSH0; stage001 manifest по-прежнему MATCH.
Self-review без делегирования; независимый review не проводился.

Approval: `PHASE16_SSH_TRANSFER_DIAGNOSTIC_20260927_001` — **GRANTED_AND_CONSUMED_ONCE**. Frozen manifest сохранён.

- Rendered remote SHA256: `5329105df7461fd2e65e5b294568e1e2d6c036a794a51a74a293fc4627609b68`.
- Manifest SHA256 (canonical LF): `b497b652a794a28886ddea0be8cbad8ecd35395fd216df89b325d32be5675ee5`.
- Synthetic payload SHA256: `2be558efdf53a6a0be148ffec0535e3d2a5de583ba365ef6e570a2b7a0de0fd1`.

Историческая команда выполненной попытки ниже — **не повторять**:

```powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -S -B 'C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB/scripts/phase16_bot_transfer_probe_gate.py' --execute --approve PHASE16_SSH_TRANSFER_DIAGNOSTIC_20260927_001 --approved-remote-sha256 5329105df7461fd2e65e5b294568e1e2d6c036a794a51a74a293fc4627609b68 --approved-manifest-sha256 b497b652a794a28886ddea0be8cbad8ecd35395fd216df89b325d32be5675ee5
```

Локальные задачи этой части завершены: receiver/strict validator, one-shot gate/
manifest/evidence binding, observer, targeted verification и review. Решение по
scope: отдельная synthetic передача с progress вместо повторной попытки install;
цена ограничения — PASS не закрывает stage001 и не устанавливает причину сбоя.
Настройки SSH и frozen001 не менялись. Server/root runtime state остаётся прежним
UNKNOWN по датированному evidence; AWG2/package016 сохранены, issuance не включалась.
SSH/live reads/service/DB/stage/install/activation/push в этом ходе0.

<a id="transfer-diagnostic-executed-2026-09-27"></a>

## Transfer001 исполнен: 5MiB подтверждены, SSH server-alive timeout — 27.09

**UNKNOWN_NO_RETRY / TRANSFER_PARTIAL.** Exact push7e7d64a0 выполнен с
EXPECTED_OLD9086bc3; hook PASS, remote branch readback MATCH, NO_FORCE/NO_TAGS.
Затем единственный разрешённый `PHASE16_SSH_TRANSFER_DIAGNOSTIC_20260927_001`
завершился за34.313s с SSH rc255. [Normalized execution record](phase16-bot-transfer-probe-execution-001-2026-09-27.json)
содержит exact claim/result, hashes внешних evidence и проверенные выводы.

Получены READY и пять последовательных PROGRESS: receiver подтвердил
5 242 880 bytes (5MiB). COMPLETE/STOP не получены, stdout содержит921 bytes,
validated prefix полностью восстановлен из events и совпал по SHA с transport.
Локальный pipe принял7 897 088 из30 487 313 bytes; последняя завершённая запись
на24.625s. Это не счётчик доставки на сервер. `stdin_complete=false`,
`output_complete=true`, failure_stage=stdin_write, termination_action=NONE:
локальный timeout110s и kill не сработали. Завершение remote process не доказано.

stderr49 bytes: `SSH_SERVER_ALIVE_TIMEOUT_HINT`, raw text не сохранялся и не
выводился. Размер и SHA полностью совпали с прежним stage001. Это связывает
оба отказа одним stderr fingerprint; прежний immutable receipt не переписан.
Новое наблюдение локализует отказ до install: он повторился на synthetic receiver
без venv/pip/application. Полная причина отсутствия ответа **UNKNOWN**; ни VPN,
ни сеть провайдера, ни загрузка VPS, ни дефект SSH не объявляются доказанными.

[OpenSSH ServerAliveCountMax/Interval](https://man.openbsd.org/ssh_config#ServerAliveCountMax)
описывает разрыв при отсутствии ответов на server-alive проверки через SSH.
[Upstream server_alive_check](https://raw.githubusercontent.com/openssh/openssh-portable/master/clientloop.c)
связывает соответствующий шаблон сообщения с exit255. Это проверка смысла hint,
а не трассировка exact установленного Windows binary. В этой попытке
ServerAliveInterval5/CountMax1 не менялись. Увеличение общего gate timeout не
устраняет установленный механизм раннего выхода клиента само по себе.

### Следующий локальный шаг без очередного bulk transfer probe

[Исторический PASS22.09](phase16-bot-linux-execution-v2-2026-09-22.json) подтверждает
retained candidate `/opt/amn2-spain/bot-candidates/phase16-bot-candidate-20260921-6e68235-001`.
Frozen Linux executor сохранял туда payload/source, в том числе runtime lock и40
runtime wheels. Нынешнее наличие/целостность **не проверялись** этим transfer probe.

Подготовить локально вариант runtime40 stage из retained payload: передавать
малый проверяемый script/manifest вместо30MB архива; перед первым использованием
на сервере обязательно сверять каждый используемый файл с внешними immutable
hash/size bindings, paths/owners/no links и provenance. Проверенные bytes копировать
в **новый** private release; прежние payload/source/test-venv48 не менять, готовый
test-venv48 не активировать. При missing/drift — STOP до stage, без автоматического
upload fallback или повторов. Остальные offline install/runtime40/no-app-import
и service/DB/activation границы прежнего дизайна сохраняются.

Это локальное направление подготовки, не готовый executor или новое live approval.
Оно убирает известную зависимость stage от повторного большого upload, но не
объявляет сеть исправной. Новый stage требует своих artifacts/manifest и exact
разрешения после проверки; незакрытые maintenance prerequisites сохраняются.
Повтор synthetic transfer, изменение keepalive, cleanup и новый SSH не разрешены.

В текущем ходе SSH1, retry0, remote script file writes0, application reads0,
service/DB/stage/install/activation0. AWG2/package016 сохранены, general issuance
не включалась; health bot/web заново не опрашивался. Проверены claim/result,
manifest/script hashes, строгий event parser/stdout hash, stderr comparison,
исторический candidate receipt, docs links/diff/whitespace; неизменные suites
не повторялись. Push результата требует нового exact SHA approval.


<a id="retained-runtime40-stage-ready-2026-09-29"></a>

## Runtime40 из сохранённого candidate: пакет готов локально — 29.09

**Исторический пакет подготовки; исполнен один раз, результат UNKNOWN_NO_RETRY.**
[Фактический результат29.09](#retained-runtime40-stage-executed-2026-09-29) имеет приоритет
над первоначальным preview ниже. По «продолжай» реализован локальный шаг
после transfer001; результат transfer001 опубликован в `8800fc6733120977ca1d007babc0f98454dc3869`.
[Новый gate](../../scripts/phase16_bot_retained_stage_gate.py),
[remote executor](../../scripts/vps/phase16_bot_retained_stage_remote.py),
[manifest](phase16-bot-retained-stage-manifest-2026-09-29.json),
[local verification](phase16-bot-retained-stage-local-verification-2026-09-29.json).
Approval этого пакета **GRANTED_AND_CONSUMED_ONCE**. Manifest и исполнявшиеся scripts заморожены.

### Что сделает одна разрешённая попытка

Передаётся только bound Python script: **41 104 bytes всего frame**, bundle upload0.
Retained payload:
`/opt/amn2-spain/bot-candidates/phase16-bot-candidate-20260921-6e68235-001/payload`.
Новая единственная write destination:
`/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001`.
Старый test-venv48 и неизвестный stage001 от24.09 не используются и не удаляются.

1. Проверить Linux/Python3.12/x86_64/glibc2.39/root, права родителей, отсутствие
   нового destination, free space512MiB и наличие unshare.
2. Через закреплённые descriptors от `/` прочитать ровно43 используемых файла:
   manifest, source.tar, runtime lock,40 runtime wheels. Ancestors: root-owned,
   no group/world write; open с O_DIRECTORY/O_NOFOLLOW. Файлы: O_NOFOLLOW и
   O_NONBLOCK, regular/root-owned/nlink1, без group/world write. Повторная сверка
   inode/метаданных открытого descriptor и имени; все descriptors закрываются.
3. Manifest74676 bytes должен совпасть с внешним immutable SHA6792cb2c…;
   его source commit/artifact id, hashes/sizes каждого используемого файла и
   каждого source entry проверяются до первого stage write. Чтение ограничено
   trusted size+1 и total128MiB. Полезные данные30 159 388 bytes читаются **на VPS**.
   Локально исходный ZIP30485208 bytes/e19abc5c… прошёл full validation;
   выбран41 payload file +159 source files (126 app Python), только40 runtime pins.
4. Проверенные bytes держать в памяти и копировать только в новый private0700
   каталог. Выполнить unshare-net probe до claim, затем создать venv и установить
   wheels offline: no-index/no-deps/require-hashes/only-binary. Child env очищен.
   Pip check и metadata: exact40 pins, допускаются только bootstrap pip/setuptools,
   pth0, source origins проверяются PathFinder под -S без import приложения.
5. Readback новой source/payload, sanitized receipt. Missing/hash drift/unsafe path
   дают STOP до stage. Ошибка после claim оставляет каталог с STOP_RETAINED_NO_RETRY.
   Повтор, cleanup, fallback upload и автоматический следующий SSH отсутствуют.

Limits: remote300s/work280s, SSH transport330s (плюс ограниченное закрытие локальных
pipes), child output256KiB, transport output64KiB, attempts1. SSH settings прежние:
ConnectTimeout10, ConnectionAttempts1, ServerAliveInterval5/CountMax1,
strict known_hosts и pinned target binding. Прежний network root cause UNKNOWN;
малый frame убирает зависимость от большого upload, но не доказывает исправление сети.
При потере SSH результат UNKNOWN_NO_RETRY; завершение remote install не угадывать.

Состояние server files сейчас не наблюдалось. Linux descriptor syscalls, SIGALRM,
unshare, venv и pip **не исполнялись** в Windows-проверке; syscalls моделировались,
install children заменялись fixture executor. Реальные local children проверили
exact bootstrap, partial/corrupt frame, extra input и wrong approval. Это local
readiness, не Linux stage PASS. Полный stage — один следующий gate, не новая серия
transfer diagnostics. Service/DB/Telegram/app activation остаются вне scope.

### Проверки и фиксация

[23 PASS/0FAIL/0SKIP,0.846s](phase16-bot-retained-stage-local-verification-2026-09-29.json).
RED отсутствующего executor; дополнительный RED показал слабую границу STOP
receipt, исправлено: before-stage count0/steps0, retained STOP count43/claim step,
после failed step продолжения нет. Проверены tamper/missing/truncation, links,
owner/mode/type, inode/ancestor replacement, source inventory, failure каждого child,
metadata pin/origin/pth, false success, duplicate/extra fields, incomplete transport,
redaction, stale claim и wrong approval/hash/target/path. Default CLI preview exit0.
Frozen stage001 и transfer001 manifests по всем bound files MATCH; старые suites
не повторялись. Self-review; независимого review и делегирования не было.

Local scope: SSH0, remote reads/writes0, stage/install0, service/DB/activation0,
push0. AWG2_UNTOUCHED, package016 immutable, general issuance disabled.
Чужое изменение `ideas/candidates-for-amn2.md` сохранено вне нашего commit.
Maintenance prerequisites (writer inventory, service user/group, effective flags,
drain/startup/pending) остаются UNKNOWN/BLOCKED; stage не подменяет их.

### Точные bindings для будущего разрешения

- Approval: `PHASE16_BOT_RUNTIME40_RETAINED_STAGE_20260929_001` — **GRANTED_AND_CONSUMED_ONCE**.
- Remote SHA256: `d5197bb13e9548de82060ba3e17d6a0d20673cb378fff8c33014b31329b83a26`.
- Manifest SHA256 (canonical LF): `c8635ea3f2b01bc8b57cda0ee6b273864121289f72d7b91c21811e2dab112051`.
- Evidence: `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-retained-stage-20260929/execution-001`.
- Target binding: `87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6`.

Подготовленный порядок push/readback → единственный stage исполнен29.09.
Команда ниже — историческая команда использованного approval, **НЕ ПОВТОРЯТЬ**:

```powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -S -B 'C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB/scripts/phase16_bot_retained_stage_gate.py' --execute --approve PHASE16_BOT_RUNTIME40_RETAINED_STAGE_20260929_001 --approved-remote-sha256 d5197bb13e9548de82060ba3e17d6a0d20673cb378fff8c33014b31329b83a26 --approved-manifest-sha256 c8635ea3f2b01bc8b57cda0ee6b273864121289f72d7b91c21811e2dab112051
```

После отдельного разрешения: до6min на ограниченный запуск, ориентир5–10min на
разбор/фиксацию результата; это не оценка закрытия всего Phase16. При STOP/UNKNOWN
сначала анализ единственного receipt, без автоматического повторного approval chain.
P2 локальная подготовка этого этапа завершена; P1 integration/maintenance/recovery
зависят от stage и новых exact разрешений; P1 Windows и P0 quality/A-B остаются
отдельными незакрытыми задачами, quality отложен оператором.
CURRENT_MODEL/CURRENT_EFFORT: недоступны. RECOMMENDED_MODEL_NEXT=gpt-6-astra,
RECOMMENDED_EFFORT_NEXT=high: анализ install/evidence и recovery границ; это
рекомендация из текущего workflow, не live authority.


<a id="retained-runtime40-stage-executed-2026-09-29"></a>

## Retained-stage исполнен: малый frame, тот же SSH timeout — 29.09

**UNKNOWN_NO_RETRY.** Exact push `0574462dded68e2430fca93886f20d702765c3d0`
выполнен при EXPECTED_OLD `8800fc6733120977ca1d007babc0f98454dc3869`;
pre-push CHANGELOG hook PASS, origin/ref readback MATCH, NO_FORCE/NO_TAGS.
Затем один разрешённый `PHASE16_BOT_RUNTIME40_RETAINED_STAGE_20260929_001`.
[Normalized execution record](phase16-bot-retained-stage-execution-001-2026-09-29.json)
сохраняет exact claim/result, hashes внешних evidence, bindings и сравнение отказов.

SSH завершился с rc255 за **12.297s**. Локальный pipe принял все41 104 bytes к2.578s,
`stdin_complete=true`, `output_complete=true`, pipe failures отсутствуют,
`failure_stage=null`, termination_action=NONE. Local330s timeout/kill не сработал.
stdout0, remote receipt отсутствует. stderr49 bytes с тем же SHA
`f267ca96307a9b773efb5f398fdf3a0d69bb89c6b184cff55d60474855b39d10` и hint
`SSH_SERVER_ALIVE_TIMEOUT_HINT`. Raw stderr не сохранялся/не восстанавливался.

| Попытка | Input в локальный pipe | Remote stdout | SSH |
| --- | --- | --- | --- |
| Stage00124.09 | 3 702 784 /30 513 539, incomplete | 0 | 255, stderr49/same SHA |
| Transfer00127.09 | 7 897 088 /30 487 313, incomplete | 921 bytes; подтверждено5MiB | 255, stderr49/same SHA |
| Retained-stage29.09 | 41 104 /41 104, complete | 0 | 255, stderr49/same SHA |

Это уже не ошибка неполной записи stdin. Малый frame не предотвратил наблюдаемый
SSH disconnect. Причина потери ответов остаётся UNKNOWN; дефект сети/провайдера, Windows VPN,
нагрузка VPS или сбой приложения/pip не установлены. Полная запись в
локальный pipe **не подтверждает** доставку/запуск script на VPS. Wrapper reason
`transport_json` означает decode пустого stdout после rc255; это не доказательство
дефекта remote JSON/validator и не основание для очередного validator gate.

В отличие от неполного stage001 frame, здесь нельзя выводить «stage не достигнут».
Каталог `/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001`
мог быть создан; retained-file verification, stage, offline install и завершение
remote process **UNKNOWN / NOT ACCEPTED**. Код ограничен этим новым каталогом,
но фактические записи не наблюдались. Remote300s cap не считается evidence его
срабатывания. Старый candidate/test-venv48 и stage00124.09 не переиспользовались
исполняемым кодом; receipt не доказывает текущее health bot/web.

### Следующая работа и границы

Повтор stage, новый bulk-transfer probe, cleanup или новая установка сейчас
**не являются следующим шагом**. Следующий локальный scope — review SSH transport
и подготовка bounded readback **уже существующего/возможного** stage directory.
Он должен различить absent/incomplete/complete, проверить сохранённый result и
реальное содержимое перед любым решением об install/activation. Учитывать текущий
SSH timeout при проектировании transport; настройки не менять попутно или наугад.
На момент execution receipt readback executor/manifest ещё не были подготовлены.
Теперь [локальный пакет готов](#stage-readback-ready-2026-09-29); новый SSH требует
точного разрешения. Автоматической цепочки probes и повторов нет.

Текущий approval **использован один раз**. Frozen manifest/scripts и исторические
receipts не изменены. Проверены local claim/result и hashes, script/manifest/target/
destination bindings, предыдущие fingerprints, docs readback/links/diff/whitespace.
Неизменные23 local PASS и прежние suites сохранены без повторного запуска.
Результат записывается отдельным локальным commit с CHANGELOG; его push требует
нового exact SHA approval, разрешение на0574462 уже выполнено.

Фактический scope: push0574462 выполнен, SSH1, retry0, cleanup0;
remote retained reads/stage/install UNKNOWN. Service/DB/Telegram/activation
команд в bound script0; AWG2_UNTOUCHED, package016 immutable, general issuance
не включалась. Maintenance writer/user/flags/drain/startup/pending prerequisites
по-прежнему UNKNOWN/BLOCKED. Чужой `ideas/candidates-for-amn2.md` сохранён.
P0 quality/A-B отложен; P1 integration теперь зависит от transport/readback и
maintenance, Windows остаётся отдельным открытым P1; P2 фиксация этого run завершена.
CURRENT_MODEL/CURRENT_EFFORT: недоступны. RECOMMENDED_MODEL_NEXT=gpt-6-astra,
RECOMMENDED_EFFORT_NEXT=high — анализ transport и неопределённого stage state;
рекомендация модели не разрешает новый live шаг.


<a id="transport-readback-design-2026-09-29"></a>

## Локальный transport review и предложенный readback — 29.09

[Review receipt](phase16-bot-transport-local-review-2026-09-29.json).
**Локальный разбор завершён; дизайн впоследствии подтверждён оператором и
[реализован локально](#stage-readback-ready-2026-09-29).**
Нового SSH/установки/push0. Результат stage по-прежнему UNKNOWN.

Сверены успешный Linux gate22.09 (remote47.487s, полный30.5MB input, rc0),
исторический local transport source66bbc8a/72757328 и текущий frozen transport.
ServerAliveInterval5/CountMax1 и явное закрытие stdin были и в успешном запуске.
Изменения этих настроек, объясняющего нынешний отказ, не найдено. Успешное длительное
выполнение также не поддерживает объяснение «любая пауза stdout приводит к timeout».
Installed ssh.exe сейчас OpenSSH_for_Windows_9.5p2 / LibreSSL3.8.2,
SHA256 `0b8b5653141c6e02e8afc043d1703dcd6410f1606422ff3ba5eb52dc56a5cce9`;
исторического SHA binary нет, сравнение версий прошлого запуска не доказано.

Точный41104-byte frame с правильным marker пропущен через реальный локальный
Python child и тот же diagnostic transport. Получены stdin/output complete,
нет pipe errors/stderr, elapsed0.110s; программа дошла до ожидаемого
`platform_python` STOP на Windows. Локальный temp остался пустым. Это проверяет
EOF у нашего Python transport; не воспроизводит Windows SSH channel и Linux.
Повторять весь неизменный suite не требовалось; frozen scripts не менялись.

[OpenSSH ssh_config](https://man.openbsd.org/ssh_config#ServerAliveCountMax)
описывает отключение при превышении допуска отсутствующих ответов; эти сообщения
идут внутри шифрованного SSH-канала. В [upstream clientloop.c](https://raw.githubusercontent.com/openssh/openssh-portable/master/clientloop.c)
server_alive_check соответствует найденным message/exit255. Это объясняет границу
отказа, а не причину отсутствия ответа и не является трассировкой Windows binary.
Root cause всё ещё UNKNOWN; оснований объявлять исправление pip/бота/сети нет.

### Согласованный bounded design (история предложения)

Цель — узнать состояние уже возможного stage29.09 за одну read-only попытку,
сразу пригодную для решения о дальнейшей интеграции. Подтверждать live readiness
или запускать очередную установку эта проверка не должна.

- Единственный read scope: stage29.09, его ancestors, claim/result, source/payload,
  pyvenv.cfg и статические distribution metadata. Исходный candidate22.09, прежний
  runtime, stage24.09, /proc, БД, env/token и service units не читать.
- Внешние immutable hashes получают offline из прежнего ZIP:159 source files,
  41 payload file,40 runtime pins,29 936 839 content bytes. Inventory JSON24938 bytes,
  compressed/base6414996 bytes. Проверить exact file sets, root-owned/no writable
  parents, no traversal/links/race для content; специальные venv interpreter links
  проверять статически по разрешённой цепочке, не запускать их.
- Saved receipt должен пройти прежний exact validator; затем текущие hashes,
  pyvenv config/no pth и metadata40+допустимый bootstrap. Не импортировать приложение
  или его зависимости, не выполнять candidate interpreter/pip. Это не полный
  аудит каждого установленного binary и не maintenance/activation acceptance.
- Код+inventory передать проверяемым compressed argument; SSH -n/без stdin.
  Проверить полный Windows command-line length локально до claim/target call.
  Если лимит не выдержан — local STOP, без автоматического transport fallback.
- Proposed per-command ServerAliveInterval5/CountMax6, remote45s/transport60s,
  output64KiB, одна попытка. Глобальные SSH configs, target/key/known_hosts bindings
  не менять. READY/progress/terminal — только фиксированные поля; raw logs/configs
  не возвращать. Сохранять validated prefix при transport failure.
- ABSENT означает отсутствие нужного каталога при безопасных ancestors;
  INCOMPLETE — неполный/неприемлемый stage; VERIFIED — receipt+содержимое+metadata
  соответствуют контракту без activation; UNKNOWN — transport/неполное наблюдение.
  Каждый исход завершает попытку, автоматических install/retry/cleanup нет.

Передача без stdin и CountMax6 предложены для получения наблюдения после
неопределённого stage, **не как доказанный fix/root-cause эксперимент**: одновременно
меняются две характеристики transport, поэтому их отдельный эффект не атрибутируется.
Дизайн был запрошен через async question и подтверждён ответом оператора
«подтверждаю». Локальная реализация/проверки приведены ниже. Первоначальное
ожидание соответствовало [Brainstorming skill](C:/Users/SooL/.codex/plugins/cache/openai-curated-remote/superpowers/6.4.2/skills/brainstorming/SKILL.md):
“the human partner approves the short in-chat design”. Повторного design approval
не требуется. Только будущие exact push/SSH остаются за отдельным разрешением
по AGENTS; исторические markers не переиспользовать.


<a id="stage-readback-ready-2026-09-29"></a>

## Readback stage29.09: локальный пакет готов — 29.09

**LOCAL_READY_NOT_EXECUTED.** Оператор подтвердил предложенный дизайн.
[Executor](../../scripts/phase16_bot_stage_readback_gate.py),
[remote reader](../../scripts/vps/phase16_bot_stage_readback_remote.py),
[inventory](phase16-bot-stage-readback-inventory-2026-09-29.json),
[manifest](phase16-bot-stage-readback-manifest-2026-09-29.json),
[28 local PASS](phase16-bot-stage-readback-local-verification-2026-09-29.json).
База подготовки a4190c26787df604ac686fbe88a36c259b52dcb3; последняя серверная
попытка была из0574462. Текущий фактический stage/install остаётся UNKNOWN.

Вопрос единственной будущей попытки: существует ли stage29.09 и подтверждаются ли
сохранённый успешный receipt, текущие200 source/payload files и static runtime40
metadata? Читается только `/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001`
и безопасные ancestors. App/dependencies/candidate interpreter не исполняются;
БД, service units, env/token, прежние candidates и /proc вне scope. Нет remote
writes/children/install/activation. Immutable ZIP и package016 не менялись.

Проверяются saved claim с точным stage marker/bundle и result прежним frozen
validator; descriptor-relative no-follow/root-owned/no-writable-path/regular-file/
single-link checks; exact159 source +41 payload inventory/size/SHA256; неизменность
наблюдавшихся файлов/директорий до завершения чтения. Статически проверяются
pyvenv.cfg без system-site, разрешённые symlink chains трёх interpreter names,
40 точных distribution pins и только pip/setuptools как возможный bootstrap.
.pth, startup customization и egg-info отвергаются. Установленные binaries целиком
не хешируются, system interpreter target не исполняется и не аудируется.

| Исход | Смысл и stop-condition |
| --- | --- |
| ABSENT_NO_INSTALL | Нужный каталог отсутствует при безопасно прочитанном parent; установка не начинается. |
| INCOMPLETE_NO_RETRY | Каталог наблюдался, receipt/содержимое/metadata неполны или не соответствуют; без исправления/cleanup. |
| VERIFIED_NOT_ACTIVATED | Saved-stage success + нынешние hashes/static metadata соответствуют; это не maintenance readiness и не разрешение activation. |
| UNKNOWN_NO_RETRY | Transport, права, изменение во время чтения или неполное наблюдение; вывод о состоянии не делается. |

### Transport и проверки

Bound script46 706 bytes передаётся compressed/base64 argument с проверкой hashes
до исполнения; stdin0/SSH -n. Preview command с резервом2048UTF-16 units занимает
27 237units; полный argv проверяется против30 000 до claim/SSH. SSH per-command
ServerAliveInterval5/CountMax6, ConnectTimeout10/Attempts1, pinned target/key/
known_hosts, StrictHostKeyChecking; глобальные configs не меняются. Remote45s,
local60s, output64KiB, одна попытка. Сохраняется валидный event prefix при обрыве;
успех требует complete pipes, terminal receipt и согласованный exit code. Готовые
решения не повторяют stage и не переключаются на другой транспорт автоматически.
Изменения argv/keepalive не являются экспериментом для установления root cause.

[Test source](../../tests/test_phase16_bot_stage_readback.py):28 PASS/0FAIL/0SKIP,
0.658s. Начальный RED — executor отсутствовал. Дополнительный RED исправил
классификацию отсутствующего parent: UNKNOWN, а не INCOMPLETE/ABSENT. Negative
controls: missing/drift/extra source, saved claim/result, metadata/config/link
cycles, paths/owners/modes/hardlinks, changed snapshots, malformed/false receipts,
partial pipes, cap, marker/hash/manifest/target drift, single claim/no retries.
Реальный Windows child исполнил exact compressed argv с DEVNULL stdin: READY,
ожидаемый platform_python UNKNOWN/rc3/stderr0; corrupt digest — rc70 до script.
Default preview exit0. Descriptor checks проверены на моделях системных вызовов;
реальные Linux openat/O_NOFOLLOW/listdir(fd) и SIGALRM **не исполнялись**. SSH,
текущий VPS, приложение и установка не проверялись.
Self-review; independent review/subagents0. Frozen manifests24/27/29.09 MATCH;
неизменные suites не повторялись. Docs readback/links/diff/whitespace проверены.

### Bindings и следующий шаг

- Approval: `PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001` — **NOT_GRANTED**.
- Remote SHA256: `f72f312f1cb5007586820b09761879a08f65b886ea8ddc92e8a15f36c8701bc0`.
- Manifest SHA256 (canonical LF): `6402188734e50485418ed39feba7a1be5d0e1a03676e08d5054cc5134191e857`.
- Inventory SHA256 (canonical LF): `647a32f7a538028a8debbe8169ade373ea08b5d1c1b0467a36a9253380852aec`.
- Target binding: `87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6`.
- Evidence: `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-stage-readback-20260929/execution-001` — отсутствует, не claimed.

Сначала отдельный exact push нового HEAD в origin branch при EXPECTED_OLD
`0574462dded68e2430fca93886f20d702765c3d0`, NO_FORCE/NO_TAGS и remote readback;
затем отдельное разрешение marker выше и одна команда. Последний origin read-only
check29.09 подтвердил0574462; перед push проверить снова. Два предыдущих локальных
commits43dd9b1/a4190c2 ещё не опубликованы, войдут в тот же разрешённый диапазон.
Команда ниже подготовлена, **НЕ ИСПОЛНЕНА И ПОКА НЕ РАЗРЕШЕНА**:

```powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -S -B 'C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB/scripts/phase16_bot_stage_readback_gate.py' --execute --approve PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001 --approved-remote-sha256 f72f312f1cb5007586820b09761879a08f65b886ea8ddc92e8a15f36c8701bc0 --approved-manifest-sha256 6402188734e50485418ed39feba7a1be5d0e1a03676e08d5054cc5134191e857
```

Ориентир после разрешения: одна попытка максимум60s плюс5–10min на разбор и фиксацию.
Это не срок закрытия Phase16. После результата определить интеграционный шаг;
не создавать автоматически очередную цепочку probes. Maintenance writer inventory,
service user/group, effective flags, drain/startup/pending остаются UNKNOWN/BLOCKED.
P1 integration зависит от readback/maintenance; Windows — отдельная незакрытая
задача. P0 quality/A-B отложен оператором. P2 локальная подготовка readback завершена.

За этот этап SSH/push/remote read/write/stage/install/DB/service/activation0.
AWG2_UNTOUCHED, package016 immutable, general issuance disabled. Чужой
`ideas/candidates-for-amn2.md` не менялся и не включён в наш commit.
CURRENT_MODEL/CURRENT_EFFORT: недоступны. RECOMMENDED_MODEL_NEXT=gpt-6-astra,
RECOMMENDED_EFFORT_NEXT=high — сложный разбор evidence/recovery; не live authority.
