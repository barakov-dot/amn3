# Отдельный bot candidate — 2026-09-21

> **Текущее состояние03.10:** цель переноса сохраняется. После уточнения scope
> оператор отдельным exact approval разрешил прежний Spain packet и push0421da7.
> Один запуск завершился bound STOP_OR_UNKNOWN_NO_RETRY/exit3 за22.937s; input/output
> complete, stderr0. [Readback03.10](#maintenance-readback-executed-2026-10-03): SSH0/4.031s,
> bot/web active/stable, claims/coordinator/fences absent; по bound source ordering
> permission/maintenance sequence не начинались этим packet. Candidate probe STOP,
> inner cause не доказана. Оба approvals consumed/no retry. Общая админка пока
> формируется; текущая local работа — [component diagnostic](#candidate-component-diagnostic-2026-10-03)
> и база передачи, без ожидания exact deployment target.
> Конкретный packet не переносится на иной host заменой hashes.
> [Единственная очередь M0a–M5](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md#transfer-priority-2026-10-03).

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

**LOCAL_READY_NOT_EXECUTED — исторический статус подготовки.** Оператор подтвердил
дизайн, затем отдельно разрешил push/readback; [запуск завершён](#stage-readback-executed-2026-09-29).
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

- Approval: `PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001` — **GRANTED_AND_CONSUMED_ONCE**.
- Remote SHA256: `f72f312f1cb5007586820b09761879a08f65b886ea8ddc92e8a15f36c8701bc0`.
- Manifest SHA256 (canonical LF): `6402188734e50485418ed39feba7a1be5d0e1a03676e08d5054cc5134191e857`.
- Inventory SHA256 (canonical LF): `647a32f7a538028a8debbe8169ade373ea08b5d1c1b0467a36a9253380852aec`.
- Target binding: `87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6`.
- Evidence: `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-stage-readback-20260929/execution-001` — claimed, claim/result сохранены; hashes в execution record ниже.

По отдельным точным разрешениям push07e7769 при EXPECTED_OLD0574462 выполнен,
включая commits43dd9b1/a4190c2; origin/ref readback MATCH, NO_FORCE/NO_TAGS.
Затем один readback marker выше; [результат](#stage-readback-executed-2026-09-29).
Команда ниже — историческая исполненная команда, **НЕ ПОВТОРЯТЬ**:

```powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -S -B 'C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB/scripts/phase16_bot_stage_readback_gate.py' --execute --approve PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001 --approved-remote-sha256 f72f312f1cb5007586820b09761879a08f65b886ea8ddc92e8a15f36c8701bc0 --approved-manifest-sha256 6402188734e50485418ed39feba7a1be5d0e1a03676e08d5054cc5134191e857
```

Оценка до запуска: максимум60s плюс5–10min на разбор/фиксацию; факт SSH2.906s.
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


<a id="stage-readback-executed-2026-09-29"></a>

## Stage29.09 подтверждён без activation — результат 29.09

**VERIFIED_NOT_ACTIVATED.** Из exact pushed commit
`07e7769f181ab851f0aa5a532ee9aa31eb80049f` выполнен один разрешённый
`PHASE16_BOT_RUNTIME40_STAGE_READBACK_20260929_001`.
[Execution record](phase16-bot-stage-readback-execution-001-2026-09-29.json)
содержит безопасный полный result, claim/result hashes, push bindings и границы.

Push при EXPECTED_OLD0574462 прошёл без force/tags/других branches; pre-push
CHANGELOG hook PASS для всех3 commits, origin/ref readback MATCH. SSH exit0 за
**2.906s**, stdin0, stdout1187bytes, stderr0, pipes complete, failures0,
termination NONE. Получены READY → RECEIPT → CONTENT → METADATA → RESULT;
trailing fragment отсутствует. Marker использован один раз, retry0.

Подтверждено на фиксированном stage29.09:

- Сохранённый claim совпадает с exact retained-stage marker/artifact/bundle.
  Result прошёл прежний frozen success validator: все stage steps завершены
  успешно, runtime40 и126 app Python files, pth0, import origins MATCH без
  импорта приложения. SHA сохранённого result:
  `de51f2e6905ae6860eefaf455e40e4512377d92d97c6024319e01b2cbb5d1694`.
- Текущие159 source +41 payload files: exact inventory, размеры и hashes MATCH;
  paths/owner/mode/link и final snapshot checks прошли.
- Текущие40 runtime pins и1 допустимый bootstrap distribution, pyvenv config,
  статические interpreter links и отсутствие запрещённых startup hooks прошли.
  Установленные binaries целиком не хешировались, interpreter/app не исполнялись.

Неопределённость прежнего stage29.09 снята в границе saved success + текущего
содержимого/metadata. Его первоначальный SSH UNKNOWN receipt остаётся историей,
а не переписывается в PASS. Новую установку, upload или transport probe повторять
не требуется. Причина прежних SSH timeouts **не установлена**: текущий успех
с argv/no stdin и CountMax6 не разделяет влияние этих двух изменений.

### Следующий интеграционный шаг

Stage готов к следующей подготовке, бот ещё не переключён. Фактическое здоровье
bot/web, production DB и готовность maintenance в этом readback не наблюдались.
Продолжается уже согласованная [локальная сборка maintenance пакета](#maintenance-local-core-2026-09-23)
по T14 единого плана; нового design approval не требуется.

| Приоритет | Остаток и зависимость | Разрешённый scope |
| --- | --- | --- |
| P0 | Quality/A-B не закрыт, отложен оператором | Новых клиентских действий нет |
| P1 | Maintenance executor/target bindings: stage теперь подтверждён; writer inventory/ownership, effective flags/user/group, drain/startup/pending остаются UNKNOWN | Локальная подготовка разрешена; новый SSH требует exact approval |
| P1 | Server-local backup и rehearsal, затем migration/switch/recovery | Реальные данные/stop/start/activation требуют отдельного конкретного пакета и разрешения |
| P1 | Windows traffic FAIL | Отдельная задача, этим readback не исследовалась |
| P2 | Push/readback/evidence текущего этапа завершены | Локальная фиксация результата; новый result commit пока не pushed |

Проверены local claim/result, SHA/size, manifest/script/target/destination,
строгая последовательность событий и exit code. Восстановленный из fixed events
stdout совпал с observed1187bytes/SHA. Документы сверены readback/links/diff;
исходники, inventory и manifests не менялись, прежние28 local PASS сохранены
без повторного запуска suites. Это новое live evidence чтения, не новое тестирование.

Фактический scope: push07e7769, SSH1, retry0; remote writes/children/install0,
app/candidate interpreter/DB/service/activation/cleanup0. AWG2_UNTOUCHED,
package016 immutable, general issuance disabled. Чужой candidates-for-amn2.md
сохранён вне commit. CURRENT_MODEL/CURRENT_EFFORT: недоступны;
RECOMMENDED_MODEL_NEXT=gpt-6-astra, RECOMMENDED_EFFORT_NEXT=high — сложная привязка
maintenance/recovery; рекомендация не даёт live authority.


<a id="maintenance-target-binding-2026-09-30"></a>

## Maintenance target binding — локальный результат 30.09

**LOCAL_BINDINGS_PASS / BLOCKED_UNKNOWN_PRECONDITIONS / LIVE_EXECUTOR_NOT_READY.**
Продолжение T14 по операторскому «приступай», база360ef0c (ранее exact pushed).
Новый [binding module](../../scripts/phase16_bot_maintenance_binding.py),
[draft manifest](phase16-bot-maintenance-target-manifest-2026-09-30.json),
[45 PASS receipt](phase16-bot-maintenance-binding-local-verification-2026-09-30.json).
Нового SSH collector или live approval marker этот этап не создаёт.

### Реализованная связь модулей

| Производитель → потребитель | Реализованный контракт |
| --- | --- |
| Readback29.09 + immutable inventory → прежний maintenance stage verifier | Pin SHA самого execution record, inventory и integration manifest; восстановление126 app Python-file hashes и40 pins из проверенных200 files, затем существующий verify_stage. Source, paths и статус исторического stage связаны; свежесть maintenance из него не выводится |
| Нормализованные inputs + декларация окна → coordinator manifest | Exact target/operation/boot, aware timestamps, stage receipt, unit baseline/User/Group/launch fingerprints, writer classes/process scan, flags/admission/startup bound, network CIDR, rollback fingerprints и pending state |
| Target contract → persistent Journal | Новый adapter всегда добавляет target_contract_sha256; он входит в digest/сохранённый manifest журнала. Изменённые paths/boot/hash/manifest отвергаются; журнал проверен на реальном временном filesystem |

Фиксированы candidate source/interpreter в stage29.09, прежний source/site-packages,
shared DB `/var/lib/amn2-spain/amn2.sqlite3` и будущая private operation directory
`/var/lib/amn2-spain/phase16-maintenance/<operation>` с backup/rehearsal/journal.
Эти пути — binding, не созданные на сервере файлы. Существующий generic core
сохраняет совместимость со старыми core-only fixtures; live adapter обязан
использовать новую пару target/coordinator, не обходить её старым manifest.

На фактически доступных данных CLI выдаёт BLOCKED_UNKNOWN_PRECONDITIONS,
coordinator_manifest=null, authorized=false, live_executor_ready=false.
Три явных blockers: fresh_server_observation, operator_window_declaration,
maintenance_operation_adapters. Ключа --execute нет; CLI ничего не исполняет.
Синтетически полные inputs дают только PRECONDITIONS_VALIDATED_NOT_AUTHORIZED.

**Проверка формы входа не доказывает, что факты собраны на сервере.** Будущий
runner должен сам привязать их происхождение и перепроверить состояние перед
мутацией. JSON с true не заменяет фактическую полноту writer inventory или
операторское владение окном. Реальных наблюдений этих полей сейчас нет.

### Проверки и принятые решения

[Tests](../../tests/test_phase16_bot_maintenance_binding.py):23 новых binding
проверки +22 затронутых maintenance-core = **45 PASS/0FAIL/0SKIP,2.857s**.
RED отсутствующего adapter; self-review воспроизвёл два дополнительных RED:
валидатор проверял hashes, но принимал пересчитанную пару с неверным DB path
или разным boot_id. Исправлено: смысловая проверка fixed paths/context независимо
от hashes; prepared input также теряет валидность по времени. Проверены tamper,
unknown/missing/extra fields, stale/future/naive timestamps, wrong flags/budget,
extra writer/unknown class, identity, pending, ownership и redaction. Реальный
Windows CLI с -I -S -B проверен в пустом temporary cwd: writes0, --execute rejected.

Ruling: продолжаем существующий T14, без второго execution plan и нового design
approval. Stage readback используется как историческое основание paths/hashes;
для обслуживания требуется свежая запись. Цена неверного provenance — ложная
готовность, поэтому этот adapter никогда не возвращает live READY/authorization.
Ruling: для локальной проверки inputs выбран возраст до300s и оставшийся срок
операторского окна900..3600s, единые operation/target/boot. Это консервативный
input contract, **не доказанный maintenance SLA и не разрешённое окно**; точные
runner deadlines/recovery reserve ещё предстоит реализовать в T14c. Цена слишком
строгого допуска — STOP/обновление inputs, не автоматическое продолжение.
Ruling: project AGENTS сохраняет один affected suite, self-review без делегирования
и канонический план/receipt вместо отдельного skill workspace. Неизменные DB helper
и readback suites не повторялись; прежние frozen manifests24/27/29.09 MATCH.

### Незавершённая часть и следующий шаг

T14a/b закрыты локально; **T14c и весь live executor не закрыты**. Требуются
конкретные adapters всех фаз fence/stop/backup/rehearsal/migrate/start/release,
устойчивый Linux runner с OS wall deadlines/network isolation, фактический writer
inventory/maintenance ownership, storage/rollback bindings, проверки fresh fence,
cgroup/drain/forced kill и startup/pending. Синтетические callbacks старого core
нельзя выдать за готовый live пакет. Новое «согласование дизайна» для продолжения
этой локальной реализации не требуется; SSH/data/service действия — отдельно
после конкретного пакета. Старые stage/readback markers использованы, не повторять.

P0 quality/A-B отложен; P1 integration зависит от T14c и фактических prerequisites,
Windows traffic остаётся отдельным P1. P2 target/input binding завершён локально.
В этом ходе SSH/live data/stage/install/service/activation/push0. AWG2_UNTOUCHED,
package016 immutable, issuance disabled; последний stage evidence29.09 остаётся
VERIFIED_NOT_ACTIVATED, свежего наблюдения30.09 нет. Чужой candidates-for-amn2.md
сохранён вне commit. CURRENT_MODEL/CURRENT_EFFORT недоступны;
RECOMMENDED_MODEL_NEXT=gpt-6-astra, RECOMMENDED_EFFORT_NEXT=high — реализация
Linux maintenance/recovery, рекомендация не даёт live authority.


<a id="maintenance-operations-local-2026-09-30"></a>

## Maintenance operations — локальный результат 30.09

**LOCAL_DATA_AND_LINUX_PRIMITIVES_PASS / FULL_EXECUTOR_NOT_READY.**
Продолжение согласованного T14c, база568c24c; новый design approval не запрашивался.
[Receipt](phase16-bot-maintenance-operations-local-verification-2026-09-30.json)
фиксирует **88 PASS/0FAIL/0ERROR/0SKIP,21.422s**, включая26 новых проверок.
Это промежуточная реализация T14c, не завершение всего maintenance executor.
Новый SSH gate/approval marker не создавался; исторические approvals не повторялись.

### Что теперь исполняется кодом

- [DataOperations](../../scripts/phase16_bot_maintenance_operations.py): реальные
  SQLite backup → rehearsal → production-path migration, только внутри уже
  сохранённого action intent. В этом прогоне production-path был временным
  synthetic SQLite файлом. Путь и состояние исходной БД сверяются до записи;
  используются прежние pinned schema/repository slices и allowlist delta.
  Проверка миграции связывает main/WAL/journal: main hash не замечал WAL-only
  commit (воспроизведён RED, исправлен). Пустой WAL от чтения не считается
  изменением данных; sidecars автоматически не удаляются.
  Backup неизменяем, clone отдельный; репетиция создаёт ещё один private base copy.
  Receipts связывают journal/intent/predecessor и hashes, не содержат строк БД.
- Перед backup/migration проверяются aggregate pending devices, незавершённые
  issuance receipts и requests без полного числа completed receipts. Ожидающие
  оплаты/ручного рассмотрения orders не объявляются работающими обработчиками.
  Частичная выдача, custom seeds, изменившийся source, повреждённый backup/receipt
  останавливают последовательность. Неудачная миграция не запускает restore.
- [Linux primitives](../../scripts/phase16_bot_maintenance_linux.py): child process
  с EOF stdin, чистым окружением, ограничением времени и вывода, без raw errors;
  systemd stop/start через один `--no-block` request с ограниченным опросом;
  проверка actual loaded fence через D-Bus Conditions и DropInPaths. Оставшееся
  cgroup/PID, ненулевой exit, timeout/kill и поздний ответ не дают PASS.
- Подготовлена команда отдельного data-worker service с PrivateNetwork,
  ProtectSystem, ReadWritePaths, ограничениями памяти/размера/времени. Он работает
  с уже созданным intent и не продвигает журнал. Это дочерний worker, **не полный
  sustained coordinator**; на Linux команда не запускалась. Самостоятельно
  брать prepared JSON из T14b и запускать worker запрещено: admission/provenance,
  непрерывный fence/ownership/drain и точный approved packet ещё не собраны.
- Candidate drop-in пока формируется как текст: прежний WorkingDirectory сохраняет
  `.env` и относительные config paths; `-I -B -u` и добавление только candidate
  source исключают старый cwd/PYTHONPATH из поиска app и дают немедленный admission
  receipt. Timeout/User/Group/flags/env не переписываются. Установка drop-in,
  start/READY/receipt/web-start/release в полный coordinator ещё не подключены.
  Проверка admission receipt привязана к unit, boot, invocation, PID и identity.

Новые бюджеты относятся только к будущим helper/coordinator actions: data worker120s,
recovery reserve300s; перед действием должно оставаться время на само действие и
reserve. Это локальная модель, не согласованное live-окно. Прежние bot start40s,
web start90s и stop90s сохранены. Таймаут клиента systemctl не считается отменой
задания manager: результат остаётся UNKNOWN/NO_RETRY под сохранённым fence.

### Существенная граница старого runtime

Исходник55dc243b8e6c6bdb57f8301b56326e4cd4072d19, `app/main.py`
blob`cb21a416d3e31f61dadf095cacdd4b4cbdc0e586`: отменяет polling/watchdog и закрывает
session, но не содержит candidate HandlerLifetime.drain/WorkflowWorker.aclose.
У candidate6e68235 эти cleanup steps есть; polling начинается перед READY.
Поэтому exit0/пустой cgroup и нулевые persisted pending counts дают только
**PROCESS_QUIESCENCE**, не доказательство завершения всех старых handlers.
Новый adapter явно возвращает business_drain=NOT_ESTABLISHED; он не подставляет
`drain=complete`. Это вывод по source, не утверждение о потерянной live-операции.

### Проверки, ограничения и продолжение

[Data tests](../../tests/test_phase16_bot_maintenance_operations.py) работают с
реальными disposable SQLite/files; [Linux tests](../../tests/test_phase16_bot_maintenance_linux.py)
запускают реальные локальные Python children и используют строгий command double
на границе systemd. RED/GREEN выполнен; self-review исправил преждевременный STOP
для queued job и принятие ответа после deadline. Default CLI даёт
LOCAL_PRIMITIVES_ONLY/authorized=false/live_executor_ready=false; Windows worker
завершается exit2 без чтения DB/вывода. Старый target manifest остаётся MATCH.
Linux process groups, private mode/namespace/cgroup/D-Bus/systemd требуют Linux
acceptance; Windows PASS их не подтверждает. Делегирования не было.

Далее в том же T14c: source-backed критерий old-handler drain, actual host admission
с происхождением фактов, непрерывные per-action fence/ownership checks, полный
sustained coordinator со start/recovery и конкретный packet. Локальная подготовка
разрешена; SSH/live data/services, установка и push требуют своих точных разрешений.
Нельзя закрывать T14c или объявлять READY по одному JSON/успешному helper.

Семантика service вместо scope и Type=exec сверена с
[systemd-run](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-run.xml);
RuntimeMaxSec и его ограничение для oneshot — с
[systemd.service](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.service.xml),
изоляция — с [systemd.exec](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.exec.xml).
Форма Conditions взята из
[D-Bus API](https://raw.githubusercontent.com/systemd/systemd/main/man/org.freedesktop.systemd1.xml),
property JSON — из [busctl source](https://raw.githubusercontent.com/systemd/systemd/v252/src/busctl/busctl.c).
Это не проверка версии systemd на целевом VPS.

Safety: SSH0/upload0/stage-install0/live DB0/services0/activation0/push0.
Последний stage29.09 VERIFIED_NOT_ACTIVATED; AWG2/package016 untouched, issuance off.


<a id="legacy-stop-decision-2026-09-30"></a>

## Решение о завершении старого runtime — согласовано 01.10

**APPROVED_POLICY_NOT_LIVE_AUTHORIZATION.** Оператор 01.10.2026 ответил
«Подтверждаю» на предложение из итогового сообщения после commit652ae3e.
Однократное исключение ниже согласовано для локальной подготовки перехода
old55dc → 6e68235; повторного согласования этого решения не требуется.
Конкретная операция/packet и SSH/stop/start/DB/install/push ещё не разрешены.

Историческое обоснование 30.09: Локальная source-bound проверка `_send_admin_config_handoff`
из55dc243 (`app/bot/handlers.py` SHA256
`31987a5fb46c9cee35c16817e805da76eef8fde178a7ce8cf86a5c9a6adf7d39`)
выполнена без импорта app и без сети. Нормальный synthetic ответ даёт1 запись
о доставке; cancellation после начала send_document, до ответа —0 записей.
`except Exception` не перехватывает CancelledError. Это воспроизведение возможного
окна неопределённости, не факт потери сообщения на VPS и не доказательство
конкретного поведения пока не сверенной installed aiogram. Existing pending
counts проверяют issuance, но не запущенные async Telegram deliveries.

Утверждённый дизайн требует: «неполный drain, неизвестные in-flight операции
или процесс вне cgroup → STOP». Согласованное ниже исключение касается только
неизмеримого завершения старых Telegram handlers. Все остальные UNKNOWN, включая
нечистую остановку, процессы, внешние writers и persisted pending, остаются STOP.
Успешный stop нельзя переименовать в подтверждённое завершение доставки.

Согласованное **однократное исключение только для перехода с old55dc на6e68235**:

1. В конкретном будущем maintenance packet оператор принимает возможность
   прерывания старого Telegram-ответа/доставки. Документ мог быть принят Telegram,
   хотя локальное подтверждение не записано. Команды и доставки автоматически
   не повторяются; возникшие спорные доставки разбираются отдельно.
2. До stop по-прежнему требуются exact inventory, ownership, effective flags и
   непрерывный start fence. После stop обязательны exit0, отсутствие timeout/kill,
   старых PID/cgroups/внешних writers и persisted pending operations. UNKNOWN в
   этих проверках по-прежнему STOP; исключение не разрешает продолжать после kill.
3. Завершённые записи старого бота входят в новый backup/rehearsal baseline.
   Сохраняется явное `old_handler_drain=NOT_OBSERVABLE_ACCEPTED_BY_OPERATOR`,
   а не `complete`. Разрешение исключения привязывается к exact source, операции
   и будущему approval packet. До candidate-start restore остаётся отдельным
   решением, требующим подтверждения отсутствия внешних effects; автоматический
   restore по этому исключению запрещён. После candidate-start DB сохраняется.
4. Candidate и прочие переходы не получают этого исключения. Старый код, токен,
   выдача, AWG2 и web-код не меняются. Это согласование локальной политики;
   SSH/stop/start/DB/stage/push по-прежнему требуют своих точных разрешений.

Предлагавшаяся альтернатива строгого STOP при любом неизвестном old-handler drain
не выбрана. Новая телеметрия потребовала бы отдельной runtime-доработки;
это согласование её не разрешает. Политика не доказывает состояние сервера.

<a id="maintenance-jobs-local-2026-09-30"></a>

## T14c: одноразовые задачи БД и доказательство остановки — локальный результат 30.09

**LOCAL_DATA_JOB_SUPERVISION_PASS; полный executor ещё не готов.**
[Receipt](phase16-bot-maintenance-jobs-local-verification-2026-09-30.json):
109 affected PASS / 0 SKIP за 29.197 s; из них 19 новых job tests и 2 проверки
старого handoff. RED/GREEN на отсутствии supervisor/worker-side guard,
self-review без делегирования. Завершённые stage/readback не повторялись.

[DataJobSupervisor](../../scripts/phase16_bot_maintenance_jobs.py) связывает
существующие data adapters с отдельными systemd services. До обращения к manager
сохраняются durable intent и одноразовая claim с hashes контекста/argv/stop-witness.
Worker независимо проверяет boot, ownership window, собственный InvocationID/PID,
заданные свойства изоляции и сохранённое состояние остановленных bot/web до и после
операции. Результат связывается с конкретным data receipt; родитель принимает его
только после чистого завершения того же запуска. Сам worker журнал не продвигает.

Stop-witness хранит identity и monotonic timestamps остановленных units; изменение
состояния/restart/boot/fence ведёт к STOP. Проверки на границах действий не заменяют
inventory внешних writers и не доказывают отсутствие обхода fence через root.
`business_drain=NOT_ESTABLISHED` и `live_authorized=false` сохраняются явно.
Этот low-level helper не принимает решение об исключении для старого runtime и
не является самостоятельным approval/admission gate.

Runtime задачи БД ограничен прежними 120 s; на dispatch/start/stop/readback отведено
всего 140 s, сверх этого перед действием сохраняется recovery reserve 300 s.
Таймауты bot 40/90 и web 90/90 не увеличивались. Потерянный ответ, отсутствующий
receipt или timeout оставляют intent/claim/fence для отдельного разбора: нет
повторного запуска, kill чужого процесса, cleanup, restart или restore.

[Job tests](../../tests/test_phase16_bot_maintenance_jobs.py) исполняют полную
цепочку backup → rehearsal → migrate на реальной temporary SQLite через strict
systemd command double: старые business rows и backup сохранены, issuance false,
receipt chain проверен. Отрицательные случаи: потеря launch ACK, чужой invocation
или PID, отсутствующая network policy, изменение unit/boot/fence, истечение окна,
подмена receipt и deadline. Проверки не содержат live DB, ключей или Telegram.

[Characterization tests](../../tests/test_phase16_legacy_handoff.py) исполняют
[точный frozen fragment](../../tests/fixtures/phase16_legacy_admin_handoff.txt)
старого `_send_admin_config_handoff`, без импорта app и сети. Нормальный ответ
создаёт 1 audit record, отмена после начала send_document до ответа — 0. Исходный
Git object и hashes приведены в receipt; AMN2 checkout не изменялся. Это возможное
окно неопределённости, не доказательство потери live-сообщения. Предложение
[однократного исключения](#legacy-stop-decision-2026-09-30) остаётся
**PROPOSED_NOT_APPROVED на момент проверки30.09**. Согласование01.10 записано
в решении выше; этот исторический receipt не переписывался.

Формы systemd properties сверены с [D-Bus API v252](https://raw.githubusercontent.com/systemd/systemd/v252/man/org.freedesktop.systemd1.xml)
и [unit source v252](https://raw.githubusercontent.com/systemd/systemd/v252/src/core/unit.c).
Это source review, не проверка версии/поведения целевого VPS. Linux namespace,
mode/owner, cgroup, D-Bus и реальный systemd-run локально не исполнялись; WSL здесь
не установлен. Default CLI сохраняет LOCAL_PRIMITIVES_ONLY/authorized=false.
Frozen target manifest MATCH; новые helper hashes входят в worker context и
отдельный receipt, существующий immutable target manifest не переписывался.

Далее в том же T14c: решение по old-handler policy, fresh host admission/provenance,
полный sustained coordinator (candidate switch/start/admission, web/recovery/release),
Linux acceptance и конкретный approval packet. Эти части ещё не собраны; successful
local jobs не разрешают исполнение prepared JSON на сервере. Новый live scope не
выдан; локальная подготовка базового согласованного дизайна остаётся разрешённой.

Safety: SSH0/upload0/stage-install0/live DB0/services0/activation0/push0.
Stage29.09 VERIFIED_NOT_ACTIVATED; AWG2/package016 сохранены, general issuance off.

<a id="legacy-stop-policy-bound-2026-10-01"></a>

## T14c: согласованное исключение привязано к операции — 01.10

**APPROVED_POLICY_BOUND_LOCALLY_NOT_LIVE_AUTHORIZATION.** Подтверждение оператора
01.10 зафиксировано в [решении](#legacy-stop-decision-2026-09-30); повторно
согласовывать само исключение не требуется. Исторические receipts30.09 сохранены.
[Новый receipt](phase16-legacy-stop-policy-local-verification-2026-10-01.json):
120 affected PASS / 0 SKIP за 27.586 s, RED/GREEN, self-review без делегирования.

[Policy adapter](../../scripts/phase16_legacy_stop_policy.py) связывает только
old55dc → 6e68235 для bot с operation/boot/journal/target, точными hashes старых
handlers/workflows и SHA256 будущего статического approval packet. Derived runtime
context формируется после такого packet; нельзя включать его обратно в hash
packet и создавать циклическую привязку. Source/packet values проверяются как
входной контракт, но adapter сам не собирает live evidence и не даёт разрешения.

Supervisor и Linux worker требуют `legacy_stop_policy` в контексте. Его отсутствие,
подмена source/subject/operation или попытка включить replay/restore/live authority
останавливают задачу. Hash всего worker context связывает политику с job claim;
сам policy adapter включён в worker artifact inventory. Старые контексты без поля
политики теперь STOP; frozen target manifest и исторические packets не менялись.

Принятая неопределённость отмечается как
`NOT_OBSERVABLE_ACCEPTED_BY_OPERATOR`; stop-witness сохраняет объективное
`business_drain=NOT_ESTABLISHED`. Ни один статус не заменяется на `complete`.
Все прежние проверки чистой остановки, fence/ownership, writers и pending остаются
обязательными; согласование не даёт права продолжать после kill или UNKNOWN в них.

Recovery adapter до candidate-start выбирает HOLD_FENCE_MANUAL_RECOVERY; после
сохранённого candidate-start intent — PRESERVE_DB_MANUAL_RECOVERY. В состоянии
prepared действий не было: LEAVE_OLD_RUNTIME. Автоматические restore/replay не
добавлены. Возможный отдельный restore до запуска требует нового evidence об
отсутствии внешних effects и отдельного решения; после запуска БД сохраняется.
Полный coordinator ещё не вызывает этот adapter: его объединение остаётся в T14c.

[Policy tests](../../tests/test_phase16_legacy_stop_policy.py) проверяют запрет
расширения scope даже после пересчёта hash, сохранение явной неопределённости и
recovery routing. [Job tests](../../tests/test_phase16_bot_maintenance_jobs.py)
проверяют STOP до manager request без политики и при чужой операции; реальная
synthetic SQLite цепочка backup/rehearsal/migrate продолжает проходить.
Фактическое Linux/systemd поведение, source/writer inventory на сервере и полный
maintenance executor по этим локальным тестам не объявляются проверенными.

Следующий разрешённый scope: fresh host admission/provenance и объединение
candidate switch/start/admission, web/recovery/release в том же T14c. Для live
операции потребуется отдельный конкретный packet и exact approval, не повторное
согласование принятой политики. SSH0/install0/live DB0/services0/push0;
AWG2/package016 untouched, stage29.09 VERIFIED_NOT_ACTIVATED, issuance не включалась.

<a id="service-operations-facts-2026-10-02"></a>

## T14c: service operations и входные факты maintenance — 02.10

**LOCAL_SERVICE_OPERATIONS_PASS; FACTS_PACKET_READY_NOT_EXECUTED.**
Оператор запросил `/GO` до закрытия Phase16 без промежуточных «продолжать?».
Продолжается ранее согласованный scope. Точные SSH/live/push границы AGENTS
сохранены; старые consumed approvals не используются повторно. Нового approval
для принятого old-handler исключения не требуется.

[Receipt](phase16-service-operations-facts-local-verification-2026-10-02.json):
**152 affected PASS / 0 SKIP, 56.323 s**, включая 18 service и 14 facts tests.
Self-review без делегирования. Завершённые stage/install/readbacks не повторялись.

[ServiceOperations](../../scripts/phase16_bot_service_operations.py) связывает
migration proof → candidate switch/start → admission → web start/readiness →
release только своих fence-файлов. До изменения drop-in проверяется завершение
migration job; каждый receipt привязан к intent/предшественнику. Потеря evidence,
изменение candidate/launch, late command или отсутствие READY/admission/HTTP
останавливают последовательность. Нет повторного start, автоматического rollback,
DB restore, cleanup чужих файлов или изменения AWG2/general issuance.

Таймауты bot40/90 и web90/90 сохраняются. Whole-action deadline ограничивает
суммарные команды; остаток ownership window и recovery reserve проверяются
отдельно. Web проверяется по прежнему launch fingerprint, PID/InvocationID,
владению loopback listener и HTTP200 `/login` с HTML-ответом ограниченного размера.
Это минимальная readiness, не полноценная acceptance приложения/VPN. Проверка
runtime/settings/source admission остаётся обязательной внешней предпосылкой.

RED/GREEN обнаружил: web active без HTTP readiness; принятие подменённой цепочки
receipt и изменённого source; принятие позднего ответа; слишком позднюю проверку
migration proof. Реальная форма scalar `busctl get-property --json=short`
сверена с [upstream v252](https://raw.githubusercontent.com/systemd/systemd/v252/src/busctl/busctl.c)
(`get_property` → `json_transform_variant` → `json_transform_one`): строка
возвращается строкой. Исправлены adapter и double; Conditions/ExecStart arrays
не менялись. Это source review, не утверждение о версии systemd целевого VPS.

### Один следующий read-only packet

Нужно получить отсутствующие факты для конкретного maintenance исполнения:
identity/launch units, происхождение выбранных настроек, признаки других задач.
Новый [manifest](phase16-maintenance-facts-manifest-2026-10-02.json) и
[gate](../../scripts/phase16_maintenance_facts_gate.py) не расширяют старые
integration-readback `_011` и stage-readback. Старые receipts неизменны.

- Approval: `PHASE16_MAINTENANCE_FACTS_20261002_001`: оператор ответил
  «разрешаю»02.10 на вопрос с exact manifest/remote SHA. Разрешена одна попытка;
  на момент этого preparation commit ещё не исполнена.
- Remote SHA256: `b46c277299fd73da9752cd729747414147badf4d33f134b078839bdb9794f376`.
- Manifest SHA256 LF: `08302d9d270811a937b6ada52304cb8055431c833b6796d11de98e2b7f2a727a`.
- Spain target binding: `87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6`.
- Одна попытка SSH, remote45s/local60s, stdout cap65536; compressed bound argv,
  stdin DEVNULL, pinned host key, ConnectTimeout10, ServerAlive5/6; retry запрещён.
- Читаются bot/web systemd properties, selected process environment и фиксированный
  old-source `.env` с выводом только проверенных несекретных полей; старый/candidate
  `settings.py` сверяется по pinned Git object hash. Токен/пароли не выводятся.
  Также читаются unit-file names, hashes/reference flags cron и hashes команд
  связанных процессов. Полные env/config/argv и журналы не сохраняются.
- Unsupported dotenv syntax, отсутствующий ключ или неоднозначный alias остаются
  UNKNOWN/ABSENT; defaults не подставляются. Static inventory не доказывает
  отсутствие opaque wrappers/external writers. Startup bound и installed binary
  integrity остаются NOT_ESTABLISHED; успешный результат — только
  `FACTS_COLLECTED_NOT_ADMITTED`, никогда admission/activation PASS.
- Remote writes/upload, DB open, app/candidate execution, Telegram, stop/start,
  install/stage/activation —0. Обычные серверные журналы SSH могут обновляться.

Offline preview (не SSH):

```powershell
python -B -m scripts.phase16_maintenance_facts_gate
```

**Только после exact approval указанного packet**, один запуск:

```powershell
python -B -m scripts.phase16_maintenance_facts_gate --execute --approve PHASE16_MAINTENANCE_FACTS_20261002_001 --approved-remote-sha256 b46c277299fd73da9752cd729747414147badf4d33f134b078839bdb9794f376 --approved-manifest-sha256 08302d9d270811a937b6ada52304cb8055431c833b6796d11de98e2b7f2a727a
```

Claim/result создаются только в новом локальном
`C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-maintenance-facts-20261002/execution-001`.
При timeout/invalid receipt: UNKNOWN_NO_RETRY; не запускать следующий marker
автоматически. Сначала разобрать evidence и устранить только подтверждённую причину.

### Что ещё не закрыто

Full sustained coordinator, admission/provenance и Linux acceptance ещё открыты.
Сервисные adapters не дают execute-ready; нельзя запускать prepared JSON как GO.
После facts read нужно разобрать settings precedence/writer scope и ownership,
завершить одно связное maintenance исполнение с проверками внутри его packet.
Требуемые read checks не превращать в отдельное разрешение на каждую PRAGMA.
Maintenance packet должен охватывать конкретные checksum/state/stop/start/DB
и recovery границы; согласованный old-handler exception уже учтён.

Для закрытия самой Phase16 остаются Windows traffic, strict same-device/app/network
Spain AWG2/AWG3.1 A/B, acceptance/persistence/leaks/restart/recovery и handoff.
Исторический Android/iPhone connectivity PASS не заменяет quality. По `/GO`
у оператора запрошена доступность устройств/версий/сетей; ответа пока нет,
client tests не запускались. Оценки сроков до получения этих входов не являются SLA.

Safety этого прохода: SSH0/install0/live DB0/services0/activation0/push0.
Frozen target MATCH; AWG2/package016 untouched, stage29.09 VERIFIED_NOT_ACTIVATED,
general issuance не включалась; чужие28 planning lines сохранены unstaged.


<a id="maintenance-facts-executed-2026-10-02"></a>

## Maintenance facts: исполнено, admission не получен — 02.10

**FACTS_COLLECTED_NOT_ADMITTED.** Однократный пакет
`PHASE16_MAINTENANCE_FACTS_20261002_001` исполнен из commit
`a21d0774b1ef49c2ac3c260ee3e271281f4142ea` после точного ответа «разрешаю».
[Execution receipt](phase16-maintenance-facts-execution-001-2026-10-02.json):
SSH exit0, 9.406 s, stdin0, stdout4699 bytes, stderr0, output complete.
Approval consumed; команда в предыдущем разделе теперь историческая, повтор запрещён.
Claim/result сохранены локально; hashes и normalized result повторно сверены.

| Наблюдение 02.10 | Результат и граница |
| --- | --- |
| User/Group bot и web | `amn2-spain`, оба active/running, NRestarts0 |
| Bot | Type=notify, start40s/stop90s, Restart=no |
| Web | Type=simple, start90s/stop90s, Restart=on-failure, port3031 |
| Process environment обоих | VPS_APPLY_ENABLED=false; DB path соответствует authoritative DB; CIDR10.212.12.0/24 |
| Bot admission | timeout30s, expected username `NeobyatnayaAMNZ_bot` |
| AWG3_BOOTSTRAP_ENABLED | ABSENT в process environment; это не доказательство будущего effective=false |
| Source settings | pinned old/candidate settings.py hashes совпали; old-source .env отсутствует |
| Inventory | 303 unit names, 5 связанных units, 4 cron files без найденных маркеров, 114 процессов/6 совпадений по маркерам |

Дополнительные docker/network/forward-compat units совпадают с прежним Phase12
набором инфраструктуры: см. `EXPECTED_ACTIVE_ENABLED_UNITS` в
[историческом source](../../scripts/vps/phase13_bot_web_migration_production_stage_remote.py).
Это не доказательство наличия ещё трёх DB writers. И наоборот, статический поиск
имён/маркеров не исключает opaque wrappers, внешние pollers и ручные операции.
Исторический executor не запускался и не является разрешением на запуск.

Оператор ответил **«Не уверен»** о других копиях бота/администраторах/ручных writers.
`exclusive_maintenance_owner`, `external_pollers_excluded`, `manual_cli_paused`
остаются UNKNOWN; не подставлять true. Позднее02.10 оператор ответил **«да»**
на вопрос, виден ли `@NeobyatnayaAMNZ_bot` в `/mybots` у `@BotFather`:
`BOTFATHER_ACCESS=OPERATOR_CONFIRMED`. Это ответ оператора, не самостоятельный
осмотр Telegram. Сам доступ к BotFather не исключает другие запущенные копии,
доступ других администраторов и DB writers. Исторический execution receipt
состояния до ответа сохранён без изменения. Базовый дизайн сохраняет bot
identity/token; rotation, удаление бота и reset БД не разрешены и не выполнялись.
Секреты в чат не запрашиваются; повторно доступ к `/mybots` не спрашивать.

Обнаружена обязательная предпосылка доступа: stage29.09 создавался root0700,
source/runtime размещены под приватными каталогами, фактический service user —
`amn2-spain`. До candidate start нужно проверить и адресно подготовить доступ
для его UID/GID/namespace. Права/ACL на момент нового SSH не собирались;
фактический ACCESS_DENIED не объявляется установленным. Нельзя применять общий
chmod/chown ко всему stage: payload/receipts/scratch должны остаться приватными,
владелец root сохраняется. Изменений прав на сервере не было.

Настройки работающего процесса не подменяют EnvironmentFile для будущего запуска.
Полные source/runtime integrity, effective settings precedence, startup bound,
writer exclusion, ownership, sustained coordinator и Linux acceptance остаются
незавершёнными. Следующий шаг — локально завершить единое maintenance исполнение
с проверками внутри; нового SSH-пакета ради повторения этих фактов не создавать.
Live mutation потребует отдельного exact approval готового packet.

Оператор указал Windows, Android и iPhone и **отложил клиентские тесты до утра
03.10 (Europe/Moscow)**. Точное время не назначено; сейчас connectivity/quality/A-B
не выполняются, старые FAIL/open не превращаются в PASS. Это не закрывает Phase16.

Safety этого SSH: remote file writes0, DB opens0, service actions0,
upload/stage/install/activation0, push0. AWG2/package016 untouched,
stage29.09 VERIFIED_NOT_ACTIVATED, general issuance не включалась.


<a id="maintenance-sequence-local-2026-10-02"></a>

## T14c: единая локальная последовательность — 02.10

**LOCAL_SEQUENCE_PASS_NOT_LIVE_READY.**
[MaintenanceSequence](../../scripts/phase16_bot_maintenance_sequence.py) соединяет
все восемь существующих операций: fence → stop → backup → rehearsal → migrate →
candidate_start → web_start → release. [Receipt](phase16-maintenance-sequence-local-verification-2026-10-02.json):
19 новых сквозных проверок PASS/0SKIP; итоговые **171 affected PASS/0SKIP, 68.078s**.
Реальные временные SQLite/backup/migration/journal/drop-in/receipt файлы;
manager/procfs/network и host admission заменены тестовыми реализациями.
Это не проверка реального systemd или production DB.

Одноразовый durable sequence claim записывается до обращения к manager.
Даже STOP до fence или прерывание с prepared-журналом запрещают повтор данного
sequence. Перед fence/stop обязательны свежий prepared contract и внешний
host_guard с привязкой к нему; boolean не принимается. Исходные launch hashes,
PID/InvocationID, source fingerprint, boot и ownership window сверяются.
Web останавливается перед bot; остановка с kill/остаточными процессами не даёт
перейти к backup. Выход старого процесса не объявляется business drain.

Каждое action_done требует собственной проверки: effective fence, stop witness,
согласованные job claim/result/complete/data receipts либо service readiness.
Подмена даже пересчитанного job completion блокирует следующий шаг.
Внутренние бюджеты: fence30s, stop190s, три data jobs по140s, candidate55s,
web105s, release30s; всего830s плюс отдельный запас300s в ownership window.
Это верхние бюджеты вызовов, не ETA и не реализованный OS RuntimeMaxSec полного
координатора. Проверки входят в бюджет шага до action_done.

Сбой сохраняет текущую фазу и безопасный код причины из фиксированного allowlist.
Raw exception/config/log не попадает в result. Итог должен записаться на диск до
возврата completion; отказ записи даёт sequence_result_unpersisted. Исключение
старого drain вызывает ранее согласованный recovery route: до candidate-start
сохранить fence для ручного решения, после intent — сохранить БД. Автоматических
restore/replay/start/cleanup после ошибки нет. Прерывание сохраняет claim/intent,
без ложного успешного result.

Независимый read-only review нового sequence/tests обнаружил P2: после медленного
source read можно было создать fence drop-in за пределами бюджета. Два RED-теста
воспроизвели задержку source read и durable intent fsync. Теперь после admission,
до intent и непосредственно перед operation повторяются deadline/lease checks.
19 sequence tests и171 affected PASS; focused re-review закрыл P2. Reviewer не
менял файлы и не запускал тесты. Предыдущие RED/GREEN также проверили отсутствие
связанной последовательности и потерю безопасного кода причины late response.
Реальный collector/OS timeout/Linux launcher reviewer не считал реализованными;
это остаётся явным незавершённым scope, а не молчаливым исключением из Phase16.

Открытая часть T14c конкретна: host collector должен сам доказать writer exclusion,
source/runtime/settings/startup/access и ownership; переданный hash этого не
доказывает. Также ещё нет manager-owned процесса полного координатора, exact
approval packet и actual Linux acceptance. У новых файлов нет CLI/SSH/автоматической
активации. Нельзя считать восемь локально связанных операций готовым live gate.
Новый readback ради повторения завершённых facts не выполнялся.

Следующий локальный scope — фактический admission и запуск устойчивого процесса
с проверкой доступа `amn2-spain` к сохранённому stage; затем единый reviewable
packet с exact live approval при выполнении остальных gates. Доступ оператора
к BotFather подтверждён; exclusive maintenance ownership остаётся UNKNOWN.
Клиентские тесты отложены до утра03.10.

Локально уточнена последовательность runtime/access admission: существующий
[stage readback](../../scripts/vps/phase16_bot_stage_readback_remote.py)
проверяет hashes source/payload и runtime METADATA/venv isolation/interpreter links,
но не сравнивает каждый установленный module/binary с доверенными wheels.
Сначала требуется content inventory установленного import path, связанный с40
runtime wheels из immutable payload и отдельно проверенным bootstrap. Подмена
RECORD или совпадение версии не заменяют сравнение содержимого. Generated files,
bytecode, дополнительные distribution и wheel data relocation требуют явной
политики; неизвестное содержимое остаётся STOP. Только после такого inventory
можно подготовить адресный service-user доступ, не открывая весь stage вместе
с payload/receipts/scratch. Этот порядок — локальное уточнение следующего шага,
не реализованный verifier и не разрешение читать/менять VPS; новые live gates
по этому уточнению не создавались.
SSH0/live DB0/services0/stage-install0/activation0/push0;
AWG2/package016 untouched, stage29.09 VERIFIED_NOT_ACTIVATED, issuance не включалась.


<a id="maintenance-packet-local-2026-10-03"></a>

## T14c: единый пакет обслуживания — локальная подготовка 03.10

Это текущая локальная реализация после исторического раздела02.10. Серверный
запуск не выполнен. Наличие manifest и предложенного owner statement не означает,
что оператор уже подтвердил этот statement или разрешил live mutation.

Оператор уточнил: **«Никто, доступ только у меня»** о SSH и ручных задачах на Spain.
Это закрывает вопрос других SSH-администраторов по его сообщению. BotFather access
подтверждён ранее; повторно не спрашивать. Отдельный вопрос о копиях Telegram-бота
с тем же токеном вне Spain ещё ожидает ответа. Отсутствие таких копий нельзя
выводить из единоличного SSH-доступа. Смена токена/идентичности и reset БД не входят
в пакет. Клиентские проверки Windows/Android/iPhone остаются отложенными.

[Packet gate](../../scripts/phase16_bot_maintenance_packet.py) готовит один
проверяемый набор кода обслуживания и существующих несекретных JSON/TXT bindings.
Candidate6e68235, его immutable bundle и package016 не перестраиваются и не
загружаются повторно. Полный список кодовых файлов, SHA256 и ограничения находятся
в [manifest](phase16-bot-maintenance-packet-2026-10-03.json). Контрольные суммы
конкретной версии и итоговый набор локальных проверок публикуются в
[verification receipt](phase16-bot-maintenance-packet-local-verification-2026-10-03.json).

Реализованы следующие проверки и переходы:

- Runtime content сравнивается с40 доверенными wheels сохранённого payload;
  bootstrap pip — с отдельным OS seed wheel и установленной dpkg-базой. OS/root
  остаются доверенной основой, подпись издателя заново не проверяется. RECORD,
  generated metadata, bytecode и relocation проверяются явно; неизвестные файлы
  дают STOP. Совпадение версий само по себе недостаточно.
- Проверяются все159 source-файлов, включая155 файлов приложения, шаблоны и
  статику. Доступ service group получают только проверенные пути; root-владелец
  сохраняется, payload/receipts/scratch и непроверенные console wrappers закрыты.
  Claim → plan → intent записываются до chmod/chown; stage root открывается для
  traversal последним. При частичном результате нет повторного применения или
  автоматического возврата прав.
- Один probe проверяет чтение и directory access от UID/GID сервиса в текущем
  mount namespace бота и новом net namespace. Shared objects проверяются через
  RX-mmap без выполнения. App/DB/Telegram не вызываются этим probe. Это проверка
  текущего доступа в поддержанном sandbox-контексте, не обещание будущего старта.
- Будущие selected effective settings вычисляются с учётом Environment,
  EnvironmentFiles, UnsetEnvironment, dotenv и pinned candidate defaults.
  VPS_APPLY/AWG3 bootstrap остаются false, DB/CIDR/port/username связаны с target.
  Бюджет39s от запроса запуска через READY/identity/admission принудительно
  ограничен; TimeoutStartSec=40 сохраняется. Это deadline наблюдения, не benchmark.
- Начальные pending aggregates читаются отдельным child с read-only DB mount и
  закрытой сетью; повторная проверка выполняется после остановки обоих writers.
  Выход старого процесса по-прежнему не доказывает business-handler drain.
- Writer admission принимает только явно подтверждённую полную APPLICATION
  topology bot+web, отсутствие других app cron/agent/timer/socket writers,
  паузу ручных задач и исключение внешних pollers на всё окно. Полный bounded
  visible proc FD/maps scan проверяет фактических holders DB/sidecars. Это не
  аудит всех OS services; `complete_bot_web_only` в старом manifest обозначает
  именно эту ограниченную, явно объявленную application topology.
- Старые source/dependencies получают content fingerprints и сохраняемый
  metadata/children snapshot. Два критических legacy source SHA проверяются;
  old55dc является ссылкой согласованной policy, deployed Git не объявляется
  установленным по двум файлам. Повторные guards проверяют исходную continuity,
  settings/launch/PID/namespace/lease и holders без полной повторной установки.

[Host admission](../../scripts/phase16_bot_host_admission.py) связывает сохранённые
proofs через observation digest с prepared contract. Проверяются также смысловые
совпадения settings/startup/rollback/inventory между dossier и observation.
[Координатор](../../scripts/phase16_bot_coordinator_process.py) запускается отдельным
manager-owned systemd service, принимает один durable claim и переживает обрыв SSH.
Затем идёт существующая последовательность8 действий: fence → stop web/bot →
backup → rehearsal → migrate → candidate start → web start → release.
Подготовленные proof-файлы не служат самостоятельным разрешением этой цепочки.

Штатный `/var/lib/amn2-spain` принадлежит service UID/GID61212, mode0750 по
installer contract. Новый storage adapter допускает ровно этот ancestor;
maintenance directories/code/records остаются root:root0700/0600. Каталог БД не
chown/chmod. Чтение удерживает directory FD и проверяет identity; импортируемые
модули связываются с утверждёнными bytes, чтобы изменение именованного предка
не перенаправило импорт. Исторические validators/receipts остаются неизменными.

Предложенные пределы всего пакета: окно ownership45min; preflight до600s;
координатор RuntimeMax900s (830s sequence +70s wrapper), ожидание930s;
**общий remote deadline1560s, transport1590s**, включая bootstrap и bounded cleanup.
Это верхние пределы, не ETA. Один SSH/одна передача maintenance code/один запуск,
без дополнительных диагностических SSH. Новый root-private каталог операции
и `/run/phase16` подготавливаются до manager submission. Claim запрещает повтор,
даже когда первый ответ потерян. При local transport timeout координатор может
продолжать работу; сначала требуется readback сохранённых intents/manager state,
новый запуск не подразумевается.

Точный live approval ещё не получен. Он должен привязываться к текущим manifest
и payload SHA256 и явно включать owner statement, перечисленные permission/DB/
service операции и допустимую startup Telegram admission. Успех локальных тестов
не является native Linux acceptance, реальным rehearsal или закрытием Phase16.
После серверного успеха остаются клиентские connectivity/quality/A-B и acceptance.
AWG2/package016 untouched; stage29.09 VERIFIED_NOT_ACTIVATED; general issuance off.
SSH/live DB/service/stage/install/activation/push в этой локальной работе:0.
### Проверенный результат и граница следующего действия

**461 PASS / 0 FAIL / 0 ERROR / 0 SKIP за146.610s**, Python3.12.14/Windows:
18 новых и11 затронутых существующих test modules. Временные files/SQLite и
локальные child processes реальные; Linux/procfs/systemd границы моделируются.
Проверена полная import/resource closure сохранённого payload из отдельного
временного каталога с `-I -S -B`; импорты используют подтверждённые bytes,
посторонние scripts/stdlib/subpackage paths отвергаются. Native Linux acceptance
этот результат не заменяет. Независимый focused review закрыл найденные P1/P2;
текущее review не обнаружило оставшихся конкретных P1/P2 в этом пакете.

Замороженная версия `PHASE16_BOT_MAINTENANCE_20261003_001`:

- manifest SHA256: `431bd0f93411651d6e604542e31aac40b55182dc2c947ef4c68ac7fe3c723eff`;
- payload SHA256: `cb8d39f97861ea36bc251245c3b9becf8ec10c124a428e755fc8b767e0f41b89`;
- bootstrap SHA256: `dd2e4a7d5e3bb5f1bbc3982989f2651e4b0ec0d66b70e777e9272840781c3e20`;
- frame345515 bytes,55 code/resource files; default preview exit0, SSH0.

Manifest сохранён в canonical JSON, поэтому его файловый SHA равен указанному
manifest SHA. Код, тесты, immutable bundle и frozen target проверены; чужой
planning diff сохранён. Исполнительный local claim отсутствует: пакет не запускался.

Для исполнения нужны ответ о внешних копиях и точное согласование этого пакета:
единственные application writers — bot/web, других app cron/agent/timer/socket
writers нет, ручные задачи приостановлены, внешние pollers исключены на все45min.
Согласование включает перечисленные permission/backup/rehearsal/migration/service
операции и startup Telegram admission. Общий `/GO` и единоличный SSH-доступ этого
утверждения не подменяют. Повторно согласовывать старый drain exception не нужно.
После такого подтверждения выполняется один запуск; при STOP/UNKNOWN сохраняются
intents/evidence и запрашивается только необходимый конкретный recovery/readback.

### Уточнение после локальной подготовки03.10 — пакет снят с очереди

Оператор напомнил конечную цель: завершить проект и перенести его на другой
сервер/сервис. Поэтому приведённое выше согласование обновления Spain больше
не запрашивается, packet не исполняется. Source/manifest/receipt сохраняют
проверенные bytes и исторический local PASS; они не переписываются ради другого
host. Возможная роль Spain теперь определяется целевым переносом: согласованный
source export/cutover при необходимости, а не повторная интеграция здесь.
См. [основу передачи](../../docs/PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md#transfer-baseline-2026-10-03).

<a id="maintenance-executed-2026-10-03"></a>

## Exact maintenance approval исполнен03.10 — STOP, без повтора

После уточнения цели переноса оператор отдельно прислал exact разрешение прежнего
пакета с manifest431bd0… и payloadcb8d39… и подтвердил: другие копии бота не
работают, application writers только bot/web, других фоновых writers нет, ручные
задачи приостановлены на45min. Это разрешение новее временного снятия packet с
очереди; оно разрешило именно один запуск, не отменяет конечную цель переноса.

Разрешённый push **0421da7c2202c6d55a8c2bdf0d117d38b765ed1b** выполнен при
EXPECTED_OLD568c24cf, NO_FORCE/NO_TAGS/NO_OTHER_BRANCHES. Pre-push changelog gate
проверил8 новых commits; Git readback подтвердил точный SHA. Local196e343 и
следующие docs/diagnostic commits этим разрешением не публикуются.

[Execution record](phase16-bot-maintenance-execution-001-2026-10-03.json):

- один SSH,22.937s, returncode3; stdin345515 bytes accepted полностью;
- stdout657 bytes, EOF complete, stderr0; timeout/pipe errors нет;
- valid bound entry receipt: `STOP_OR_UNKNOWN_NO_RETRY`, reason
  `packet_precondition_or_execution_failed`, manual route
  `INSPECT_RETAINED_INTENTS_AND_MANAGER_STATE`;
- сохранены claim/result/operator-authorization hashes. Maintenance code upload и
  запись packet result подтверждаются bound entry receipt; claim consumed once.

Исходный entry не сохранил имя failed boundary/исключения. Из ответа нельзя
доказать отсутствие stage chmod/chown, service fence/stop/start или DB migration;
их state остаётся UNKNOWN. Нельзя объявлять recovery/activation PASS, называть
timeout причиной отказа или повторять packet. Structural preview старого gate по-прежнему считает
bytes/hash, но факт исполнения берётся из execution record и durable claim.

### Один предложенный read-only readback

[Readback gate](../../scripts/phase16_bot_maintenance_readback.py),
[manifest](phase16-bot-maintenance-readback-manifest-2026-10-03.json) и
[local verification](phase16-bot-maintenance-readback-local-verification-2026-10-03.json)
подготовлены для `PHASE16_BOT_MAINTENANCE_READBACK_20261003_001`:

- фиксированные saved operation JSON: hashes/size и только allowlisted status,
  phase, reason; journal names/count/hash; fixed fence/permit metadata;
- selected state properties bot/web/coordinator до/после. Нет raw environment,
  command line, logs, токенов, конфигов или строк БД в выводе;
- только если access/coordinator claim отсутствует: authenticated readonly
  unit/candidate/legacy proofs, включая selected settings/source/runtime provenance.
  Старый root0700 observer не повторяется после permission claim;
- first readonly proof STOP выдаёт pinned literal reason. Общий readback UNKNOWN
  сообщает fixed boundary/reason; произвольный exception text редактируется;
- deadline120s включает launcher/bootstrap; transport150s, output64KiB,
  одна попытка, strict pinned SSH. Remote code исполняется в памяти, не загружается
  на диск. Application/SQLite/permission/data/service action не запускаются этим gate.

БД не открывается; pending/writer admission, migration correctness и оригинальное
скрытое исключение не объявляются доказанными readback. Если unit/candidate/legacy
proofs проходят, а поздних claims нет, отказ сужается до дальнейшего preflight,
но причина pending/writer не угадывается. Native Linux readback не выполнен.
Новое exact разрешение должно включать manifest и remote SHA; старое maintenance
approval его не разрешает. До результата нет cleanup/recovery/restore/replay.
AWG2/package016 сохраняются; general issuance disabled по bound packet.

Локальная завершающая группа: **34 PASS / 0 SKIP**, Windows fixtures; Linux native
не запускался. Независимый review нашёл P1: legacy wrapper поглощал deadline;
actual-wrapper RED → GREEN закрыл его без изменения original frozen packet.
Gate/default preview и manifest совпали; proposed readback claim отсутствует.

<a id="maintenance-readback-executed-2026-10-03"></a>

## Readback исполнен03.10 — M0a завершён, дальше перенос

[Execution record](phase16-bot-maintenance-readback-execution-001-2026-10-03.json)
содержит bound snapshot, hashes локальных claim/result/authorization и source
ordering. По exact approval выполнен один SSH: 4.031s/rc0, stdin0, stdout4408,
stderr0, EOF complete. Статус READBACK_COLLECTED_NOT_RECOVERY; approval consumed.
Push5acb675 подтверждён при EXPECTED_OLD0421da7, pre-push2 commits PASS.

Bot/web active/running, selected properties одинаковы до/после. Coordinator
not-found; saved host/access/coordinator/sequence records, journal, dropins и
permits отсутствуют. Present только upload claim, original manifest и исходный
packet-result с прежним точным hash. Bound source требует durable claim до
chmod/chown и service/data sequence. Поэтому в доверенном OS/root контуре
permission/maintenance sequence, backup/rehearsal/migration/activation не
начинались **этим packet**. Это inference по source+retained state; содержимое
живой БД, inherited runtime/deployed revision и app health не проверялись.

Current readonly unit_facts PASS; candidate_content STOP с
candidate_collection_failed. Это generic wrapper для скрытого inner exception,
не установленная root cause оригинального entry. Legacy proof не запускался
после candidate STOP. Recovery/replay/cleanup не требуются этим snapshot и не
исполнялись. Новых Spain diagnostics не поставлено в очередь; candidate admission
остаётся открытым ограничением для целевого контракта переноса. Следующий шаг M1:
точный сервер/сервис или проект. AWG2/package016 сохранены; issuance disabled.

<a id="candidate-component-diagnostic-2026-10-03"></a>

## Component diagnostic candidate — local preparation03.10

Общая админка ещё формируется; её готовность не является precondition локальной
подготовки. Current candidate STOP не имеет inner reason из-за широкого wrapper.
Новый bounded diagnostic даёт один конкретный readonly ответ для дальнейшего
local fix; original candidate collector и original packets не переписываются.

[Script](../../scripts/phase16_bot_candidate_diagnostic.py),
[manifest](phase16-bot-candidate-diagnostic-manifest-2026-10-03.json),
[local verification](phase16-bot-candidate-diagnostic-local-verification-2026-10-03.json).
Approval ID: `PHASE16_CANDIDATE_COMPONENT_DIAGNOSTIC_20261003_001`.

Во время существующего readonly candidate.collect_live temporary memory wrappers
фиксируют closed component label, calls/status, pinned literal reason, fixed
exception kind и allowlisted returned status. Аргументы/return bodies, paths,
команды, raw errors/traceback, configs/tokens и DB rows не выводятся. Обёртки
снимаются в finally, включая deadline; inherited methods возвращаются в исходное
состояние. Сам collector и его checks/return/exception остаются прежними.

| Наблюдаемые компоненты | Что различает результат |
| --- | --- |
| catalog / stage_observation | Binding inventory и retained stage proof |
| settings / settings_file_read | Effective settings и ownership/continuity выбранных файлов |
| bootstrap / readonly_command / secure_tree_open / secure_file_read | Existing OS package provenance, bounded metadata commands, no-follow reads |
| identity / nss_groups | Service identity и NSS membership |
| runtime_expected / venv / access_plan | Wheel-derived runtime и semantic venv/access PLAN, без apply |
| collection | Original outer result и скрываемый им inner failure |

Reuse fixed operation records, unit properties/fence metadata from frozen
readback; candidate вызывается только при отсутствии access/coordinator claims.
Legacy live proof исключён из этого diagnostic. Remote120s/transport150s/output64KiB,
один SSH/stdin0/strict pinned key, code in memory. DB/app/permission/install/
service actions/writes0. New durable execution claim не существует; SSH пока0.
Все PASS означают DIAGNOSTIC_COLLECTED_NOT_ADMITTED, не разрешение обслуживания.
Если ошибка не воспроизведётся, это не root cause и не live acceptance. UNKNOWN
или timeout не разрешают повтор; original maintenance/readback не replay.

Локально: итог40 PASS/0 SKIP, actual settings/OS-command/runtime/access errors,
успешный original proof, redaction, schema и deadline/restoration проверены.
Review P2 (literal reasons из `_require` терялись) закрыт targeted RED/GREEN:
actual `ancestor_access` и `wheel_inventory` сохраняются только в component
telemetry через отдельный allowlist verified frozen sources; прежние `REASONS`,
record summary/probe и frozen validator неизменны. Независимый focused review PASS,
открытых P0/P1/P2 нет. Это Windows fixtures, native Linux diagnostic не исполнен.

Дизайн ограничен существующим flow и представлен в чате; пользовательский /GO
разрешает автономную локальную подготовку. Live SSH и push по-прежнему требуют
точного отдельного разрешения. Никакой новой админки или интеграции другого
проекта эта работа не создаёт. Статус и очередь только в основном плане Phase16.
