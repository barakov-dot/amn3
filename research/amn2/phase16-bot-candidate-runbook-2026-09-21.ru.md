# Отдельный bot candidate — 2026-09-21

Статус: LOCAL_CANDIDATE_NOT_DEPLOYED. Это локальная подготовка по разрешению
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
