# Phase16 Task3B: bounded integration readback contract — 2026-09-22

Статус: **PORTABLE_CORE_IMPLEMENTED / LINUX_GUARD_NOT_VALIDATED / LIVE_EXECUTION_DISABLED**.
Актуальный результат реализации — в [разделе ниже](#portable-implementation-2026-09-22);
остальной документ задаёт целевой contract, а не утверждает покрытие всего runner.
Это детализация существующего [Task3B](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md),
а не новый execution plan. Основание: операторское «продолжай» после
[isolated Linux PASS](phase16-bot-linux-isolated-gate-2026-09-21.md#isolated-linux-pass-2026-09-22).
Первоначальный contract подготовлен локально; последующая реализация описана
ниже. За оба шага SSH/live DB open/service actions=0.

## Назначение и граница результата

Один будущий ограниченный readback должен собрать evidence для M3/DB/M4:
файлы deployed source, статические metadata зависимостей, форму схемы SQLite и
наблюдаемые процессы с открытыми файлами БД. Он не останавливает службы,
не запускает приложение и не доказывает writer quiescence, runtime module
binding, semantic DB compatibility или возможность безопасного switch/revert.

Исторический snapshot21.09 — только начальные ожидания, не текущий факт:
bot/web используют /opt/amn2-spain/runtime/source, Python3.12.3; потенциальный
dependency root /opt/amn2-spain/runtime/site-packages; предполагаемый DB path
/var/lib/amn2-spain/amn2.sqlite3. Несовпадение не исправлять на сервере.
[Источник snapshot](phase16-ssh-event-loop-applicability-2026-09-20.md#spain-bot-target-readback-v2-2026-09-21).
Source для локального сравнения: AMN2 **6e682356ed14a62d636ee58039fd3a389e794809**;
AMN3 base **e046ca02bfdd9c029b7454c6d63122c71b7cf882**. На момент подготовки оба
worktree чистые. Локальный app содержит126 файлов .py,1487221bytes; это
измеренный объём candidate, не инвентарь сервера и не доказательство release SHA.

## Почему нельзя читать через приложение

Source evidence относится к указанному AMN2 commit; номера строк — навигация.

| Потенциальный writer | Проверенный source path | Следствие для readback и fence |
| --- | --- | --- |
| Bot startup/workflow | app/main.py:391–427, app/db/repositories.py:2485–2579 | connect, initialize_schema, seed_default_plans и server sync; даже старт без polling может писать |
| Web repository | app/web/app.py:2254–2257 | Открытие repository инициализирует схему; обычный HTTP read не служит безопасным metadata probe |
| API repository | app/api/app.py:247–250 | Общая writable connection/schema initialization, включая repository dependency |
| Local agent audit | app/agent/audit.py:37–46; app/cli.py:1809 | Даже agent read записывает local_agent_read в audit |
| CLI/admin/maintenance | app/cli.py:764–766,1633–1635,1676–1678,1712–1714,1940–1943,1962–1965 | Ручные и плановые entrypoints могут писать между снимками процессов |

app/db/connection.py:5 создаёт parent и открывает writable SQLite;
connect_read_only:16 использует mode=ro/query_only, но не даёт отдельной
filesystem write boundary. Не импортировать app, Settings, dependency packages,
не вызывать main/create_workflow/CLI/HTTP/agent для этого readback. Названия
дополнительных API/agent services и их владельцы пока UNKNOWN; не выдумывать их.
Bot instance lock не ограждает web/API/agent/CLI. Предыдущие101 schema checks
на synthetic fixtures сохранены, но actual DB и seed policy ими не приняты.

## Разрешаемые поля и фиксированные области будущего чтения

Каждый блок возвращает собственные status/reason/coverage; неизвестное поле
не заменяется значением из snapshot. Выход — schema-validated JSON без raw
exception/stdout/stderr, конфигураций, argv, environment, SQL и пользовательских rows.

| Блок | Фиксированная область | Нормализованный результат и предел утверждения |
| --- | --- | --- |
| Host/stdlib | /usr/bin/python3; existing /usr/bin/unshare и /usr/bin/mount | Linux/architecture, Python/SQLite versions, executable identity; запуск Python только -I -S -B, без site/.pth и app imports |
| Source | /opt/amn2-spain/runtime/source/app, только regular .py | SHA256/size по локально утверждённому relative-path allowlist, missing/extra count и digest; никаких contents/неизвестных names. Полное совпадение только этой области, не Git release proof и не loaded code proof |
| Dependency metadata | /opt/amn2-spain/runtime/site-packages, regular *.dist-info/METADATA | Только Name/Version для runtime40 lock, missing/different/duplicate/extra count; неизвестные names не выводить. METADATA читать как данные, без importlib discovery, pip или выполнения .pth |
| Path activation hints | Тот же dependency root, regular .pth | Только presence/count/hash, не contents/исполнение. Наличие .pth, иных import hooks или непроверенного source root оставляет effective runtime binding UNKNOWN |
| Units | Только amn2-spain-bot.service и amn2-spain-web.service | Load/Active/SubState, Type/Restart, timeout/kill/watchdog values, MainPID/startticks/cgroup role, точное совпадение WorkingDirectory/ExecStart с allowlist; hooks/drop-ins count и digest. Не Environment, EnvironmentFiles contents, raw unit/argv/logs |
| DB files | /var/lib/amn2-spain/amn2.sqlite3 и одноимённые -wal/-shm/-journal | Тип/dev/inode/size и presence, identity before/after. Нет whole-file hash/copy/backup/row counts; предполагаемый path ещё не доказывает settings.database_path рабочего процесса |
| DB schema | Тот же DB path, только через защиту ниже | SQLite/schema/user versions, read-only journal_mode, известные object types/names, column name/type/notnull/pk/hidden, index uniqueness/columns, FK metadata; без SQL/default expressions/rows |
| Observed DB holders | Ограниченный /proc PID/fd stat scan | Совпадения dev/inode DB/WAL/SHM, PID/startticks, known-unit role либо UNKNOWN_OWNER, итог coverage/churn/denied. Без чтения fd contents, cmdline/environ, вывода чужих process names/paths |

Source/табличный allowlist и runtime40 Name/Version manifest генерируются
локально из exact commit/lock, без запуска приложения; их hash включается в
будущий contract исполнения. До такой реализации/hashes серверная команда
не готова. Не пересобирать ZIP, не трогать candidate test-venv48pins.
Нестандартный объект/колонка/тип/индекс отражается как count/digest/UNKNOWN;
неизвестные идентификаторы не выводятся. Список .py не исключает влияние
native modules/resources/изменившегося sys.path; область покрытия указать явно.

Для units допустим только property allowlist; потенциально чувствительные
Exec/hook строки сравниваются в памяти с фиксированными формами, затем
отбрасываются. Неизвестное значение даёт mismatch/UNKNOWN, не raw value.
Прочитать и хешировать fragment/drop-ins можно только внутри канонического
/etc/systemd/system или /usr/lib/systemd/system после nofollow проверки;
иной путь означает UNKNOWN, без расширения roots. Общий contents budget ниже.
Environment file /etc/amn2-spain/runtime.env и bot token исключены.
Без проверки effective import path статические metadata не закрывают M3.

## SQLite/WAL: обязательная граница до первого open

Предлагаемый механизм требует реализации и synthetic Linux проверки; его
доступность на Spain пока UNKNOWN. Он не использован в этой задаче.

1. Отдельный owned child создаёт private mount namespace existing unshare
   с явным private propagation. Проверить отличие namespace от parent и
   отсутствие shared propagation **до mount**. Никаких nsenter в host/service,
   persistent namespaces, новых mountpoint directories или transient units.
2. Проверить nofollow все компоненты DB directory, regular DB/sidecars,
   отсутствие дочерних mounts; сохранить directory/file identity. Только
   внутри нового namespace bind DB directory на себя и remount этого bind
   read-only, mount с -n (без записи mtab). Mount допускается лишь как
   явно описанное временное действие будущего approval; это не host remount.
3. До SQLite open сверить mountinfo + ST_RDONLY, directory identity и private
   propagation; закрыть унаследованные посторонние descriptors. DB открывает
   только guarded child через этот путь. Любая ошибка/неподдерживаемый режим —
   STOP до open, без fallback. Read-only bind не переключает production mount.
4. Stdlib SQLite >=3.37 (table_list/type guard), URI mode=ro, query_only=ON, temp_store=MEMORY,
   trusted_schema=OFF с readback, extension loading disabled; fixed-query
   authorizer запрещает DML/DDL, ATTACH, пользовательские functions и выход за
   schema allowlist. До column/index queries отклонить virtual/shadow tables
   по metadata type; неподдерживаемая type introspection означает STOP.
   Никаких application imports или запросов к virtual/shadow tables.
   Реализация обязана проверить совместимость authorizer с metadata PRAGMA.
5. Короткая read transaction: BEGIN, фиксированные schema queries, ROLLBACK/
   close; busy_timeout=0, progress handler и внешний deadline. WAL допустим
   только при уже существующих readable regular -wal/-shm. Missing sidecar,
   recovery requirement, BUSY/LOCKED/ошибка — STOP, не создание/исправление.
6. После close снять identity/guard readback; изменение inode/schema version
   означает stale evidence/STOP. Изменение размера от иных writers возможно;
   не приписывать его collector. Namespace исчезает с собственными процессами,
   без host umount/cleanup и изменения действующих служб.

mode=ro плюс query_only сами по себе не доказывают отсутствие SQLite sidecar
writes. immutable=1 пропускает locks/change detection и не подходит для
меняющейся БД; nolock тоже исключён. Read-only bind предназначен блокировать
writes через view collector, а не блокировать production writers. Запрещены
checkpoint, VACUUM, integrity_check, backup, копирование DB/WAL, migration,
seed/reset/delete/restore. Даже короткий reader может задержать checkpoint;
поэтому read transaction ограничена2s и не называется «нулевым воздействием».

Это fingerprint **формы** схемы, не полного SQL contract: defaults/CHECK,
trigger bodies, данные тарифов и semantic compatibility остаются UNKNOWN.
Не выводить sql/dflt_value и не выполнять SELECT по прикладным таблицам.
Согласованный оператором будущий schema snapshot не разрешает startup/seed.

Основание механизма: [SQLite WAL](https://www.sqlite.org/wal.html),
[URI mode/immutable](https://www.sqlite.org/uri.html),
[query_only](https://www.sqlite.org/pragma.html#pragma_query_only),
[read-only bind mount](https://man7.org/linux/man-pages/man8/mount.8.html),
[private unshare](https://man7.org/linux/man-pages/man1/unshare.1.html).
Это проектное применение документации, не проверка существующих host capabilities.

## Writers: что снимок может доказать

MainPID/startticks двух известных units сравниваются до/после. /proc scan
фиксирует только открытые holders заданных inode; mode descriptor не даёт
доказательства будущих writes. Нет fd сейчас — не значит writer отсутствует.
Перезапуск PID, access denied, churn или cap даёт PARTIAL/UNKNOWN.

До любого admission fence/migration отдельно нужны владельцы всех API/agent/
CLI/admin/background jobs и их launch sources; в этот readback не добавлять
неограниченные crontabs, container inventory, history/argv/environ или logs.
Writer completeness остаётся UNKNOWN даже при чистом снимке. Будущий stop
известного bot не запрещает запись web/остальных writers. Положительное
inode evidence доказывает лишь открытый файл у process, не его полную DB
конфигурацию. Отсутствие совпадения не разрешает искать другие базы или
сканировать data directories.

## Caps, завершение и STOP

Ниже **проектные hard caps**, не измеренная длительность target. Превышение
не расширяет scope, не разрешает retry и не превращается в усечённый PASS.

| Область | Hard cap |
| --- | --- |
| Транспорт | Один SSH,60s local timeout; remote watchdog50s; единый JSON stdout <=64KiB, stderr <=8KiB, без raw публикации |
| Этапы внутри общего watchdog | Host/units8s, source10s, dependency8s, namespace setup5s, DB child5s, holders5s, finalization4s; итог <=45s +5s reserve |
| DB read transaction | <=2s от BEGIN до close, busy_timeout0; timeout завершает только owned collector child |
| Source | <=256 .py, <=1MiB/file, <=8MiB total; traversal <=1024 entries, depth<=16; symlink/special file/path escape STOP |
| Dependencies | <=128 dist-info, <=64KiB/METADATA, <=8MiB total; <=16 .pth по64KiB, traversal<=1024 entries; duplicate names STOP |
| Units | Два exact units, <=8 drop-ins/unit, <=64KiB/file, <=1MiB total, каждый show call<=2s; unknown hooks не исполнять |
| Schema | <=128 objects, <=512 columns, <=128 indexes, <=128 FK entries, <=256bytes/identifier; overflow STOP, не raw truncation |
| /proc | <=512 PIDs, <=256 fd/PID, <=8192 fd total, <=5s; incomplete/denied/churn сохранять как UNKNOWN |

Timeout cleanup относится только к созданной collector process group с
проверенной ownership; никаких signals service/чужим PID. TERM2s/KILL2s входят
в remote50s/local60s, отдельного SSH для cleanup нет. Невозможность подтвердить
завершение — UNKNOWN_NO_RETRY, не обещание quiescence. Shared DB не исправлять.

Fatal STOP: identity/path/namespace/read-only guard failure, unsupported SQLite,
I/O/query error, timeout/cap, unit identity drift. Блоки с missing dependencies,
source mismatch или incomplete writer coverage дают отдельные UNKNOWN/DIFFERENT;
их нельзя повысить до integration PASS. Только все обязательные поля и caps
дают READBACK_COMPLETE_WITH_LIMITATIONS; это не acceptance. В любом результате
полученные валидные evidence сохраняются, не домысливаются из прежнего receipt.

## Следующий локальный шаг и будущая граница согласования

Подготовить один collector/runner в рамках Task3B и локальные manifests;
проверить synthetic cases: WAL с активным writer, missing/shm/hot recovery,
BUSY, timeout, symlink/extra mount/failed guard, неизвестные schema names,
secret-bearing unit metadata, PID churn/denied/caps и transport truncation.
Доказать отсутствие writable SQLite opens/sidecar writes со стороны collector,
сохранение sentinel rows/schema synthetic DB и запрет запуска приложения.
Windows unit checks не заменят Linux namespace/WAL evidence; использовать
имеющуюся разрешённую локальную Linux среду, а при её отсутствии явно оставить
этот prerequisite UNKNOWN до отдельного ограниченного synthetic Linux scope.

После реализации/review/hash binding подготовить exact single-attempt
исполнение: host/user/trust, script/manifest SHA, caps, exclusive local evidence
path и approval marker без UNKNOWN полей. Лишь затем запросить отдельное
разрешение на bounded SSH/readback и временный private mount. Сейчас ни такой
команды, ни разрешения нет. Stop/switch/migration/seed/Telegram smoke/restore
потребуют собственных state/rollback-bound contracts после анализа evidence.

AWG2_UNTOUCHED; package016/immutable candidate прежние; general issuance disabled.
Linux negative+6signals PASS сохранён. Test-only venv ранее создана; production
stage/install/deploy не выполнялись. Финальный stop budget, M3 runtime binding,
M4 complete writer fence и M6/M7 DB-compatible rollback остаются открыты.

<a id="portable-implementation-2026-09-22"></a>

## Локальная реализация переносимой части — 2026-09-22

По следующему «продолжай», AMN3 basece2add2, подготовлены:

- [Offline manifest builder](../../scripts/phase16_bot_integration_readback.py):
  pinned AMN2 Git blobs, чистый source/точный commit, no app imports; exclusive
  output, runtime40 pins и статический disclosure allowlist SQL identifiers.
  CLI --execute всегда возвращает LIVE_EXECUTION_DISABLED до любых Git/DB действий.
- [Ядро сборщика](../../scripts/vps/phase16_bot_integration_readback.py):
  bounded source/dependency metadata, unit property normalization без env/argv
  output, schema shape/authorizer, observed inode holders, namespace/RO checks
  перед SQLite open. Отдельная child-only mount setup функция отказывает в host
  namespace; сама на Linux ещё не выполнялась.
- [Synthetic Linux harness](../../scripts/vps/phase16_bot_readback_guard_smoke.py):
  только новые собственные fixtures, три child cases (WAL shape/read-only write
  negative, missing-shm STOP, journal STOP), сохранение sentinel и writable parent
  view. Проверка негативной записи принимает только SQLITE_READONLY, не BUSY.
  New scratch exclusive/retained, owned child8s/kill2s, никаких production targets
  или SSH. На Windows NOT_RUN до mkdir; Linux execution ещё НЕ ВЫПОЛНЕН.
- [Целевые portable tests](../../tests/test_phase16_bot_integration_readback.py)
  и [сохранённый manifest](phase16-bot-integration-manifest-6e68235.json).

[Нормализованный local receipt и hashes](phase16-bot-integration-local-verification-2026-09-22.json).
Manifest воспроизведён дважды с одинаковыми bytes.

**42 portable tests PASS**. Первоначальный RED: отсутствующие helpers и
неблокирующий пустой CLI. Затем26PASS. Проверка actual source обнаружила
fragmented f-string DDL: AST теперь не рассматривает части JoinedStr как
самостоятельные complete SQL literals. Отдельный RED на CRLF METADATA отделяет
body от headers; два regression исправлены,40PASS. Ещё два RED →42PASS:
Windows refusal до создания scratch и host namespace refusal до mount.
Они не доказывают kernel enforcement; Linux cases не запускались и не
маскируются под PASS/SKIP. Прежние45/101/94+6/312 suites не повторялись.

Manifest содержит126 .py/1485043 Git-blob bytes,40 pins,31 table identifiers,
25 explicit indexes.31 — disclosure allowlist со старыми/rebuild declarations
(users_new/devices_new), не число таблиц production DB.1487221 в исходном
contract — измерение Windows checkout, отличие line endings; hashes строятся
по Git bytes для Linux. Это не schema compatibility assertion. Dynamic SQL
не исполняется/не достраивается; непокрытая форма остаётся UNKNOWN.

Локальная WSL не установлена, Docker executable не найден; install не выполнялся.
Это не ошибка AMN2 и не причина переносить тест на рабочую БД. Приоритетный
следующий local slice — закончить bounded transport/supervisor и точный contract
для isolated synthetic Linux guard run с hashes/новым scratch; только затем
отдельное approval. Общий live collector ещё не собран: actual unit IO,
atomic/path-race hardening, общий watchdog/output framing и строгая валидация
remote receipt остаются задачами до live readback. Наличие helpers не закрывает
эти требования и не разрешает подключение. Source/dependency циклы содержат
локальные caps/time checks, но внешний deadline для блокирующего I/O требует
runner; это не подтверждённый общий50s budget.

Проведён локальный review scope/error paths/выводов; независимый reviewer в этом
inline шаге не привлекался. Code/tests/manifest не меняют AMN2, locks или
immutable ZIP. SSH/mount/service actions/live DB open=0. AWG2/package016 и
issuance safety сохранены; production stage/install/deploy отсутствуют.
