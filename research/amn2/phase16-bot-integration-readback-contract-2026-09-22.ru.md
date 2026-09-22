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

<a id="synthetic-linux-gate-ready-2026-09-22"></a>

## Bounded synthetic Linux gate готов локально — 2026-09-22

Следующий согласованный локальный slice завершён. Добавлены
[local runner](../../scripts/phase16_bot_readback_guard_gate.py) и
[remote supervisor](../../scripts/vps/phase16_bot_readback_guard_remote.py).
По умолчанию runner выполняет только offline preview. Execute требует exact
approval marker, remote SHA, SHA канонического manifest и фиксированный новый
local evidence-dir. Exclusive claim создаётся до чтения trust binding; затем
сверяется digest роли/host/user/key/known_hosts и допускается один SSH без
retry/cleanup SSH. Remote supervisor принимает hash-bound payload, создаёт только
новый retained target, запускает synthetic fixtures в отдельных mount+network
namespaces и валидирует точную закрытую schema receipt.

[Gate manifest с hashes, caps и command contract](phase16-bot-readback-guard-gate-manifest-2026-09-22.json)
и [local receipt](phase16-bot-readback-guard-local-verification-2026-09-22.json)
сохранены. После RED исправлен race combined-output cap при быстром завершении
child; отдельный RED закрепил network namespace. Независимый review выявил
неполную approval/target binding, поздний claim, неполный deadline, отдельную
process group namespace-child и неточную STOP schema. Все замечания исправлены
с отдельными regression tests. Итог **56 PASS**, preview:
manifest SHA `ac51ca3966bd2363d5969ecaf936c981cde35eddaf0fe3947a0209a0410a6964`,
remote SHA `47f64ad29e684934761c17b74b6fe68086973fc19b09d0f2f14540a7a7f9c9e9`,
payload SHA `2898ecdc1476a3144c2438c1237990cbe6c9e249bb302f1848c01521dabb6224`.
Local evidence parent создан, execution-001 отсутствует и остаётся exclusive claim.

Будущий run ограничен 45s на весь remote gate/60s transport/64KiB combined
output. Он проверяет
только новую synthetic SQLite: WAL read shape, OS-level SQLITE_READONLY,
missing-shm/journal STOP, sentinel preservation и writable parent view. Production
DB/source/units/services/Telegram/runtime исключены кодом и receipt. Destination
`/opt/amn2-spain/bot-candidates/phase16-readback-guard-20260922-001` должен
отсутствовать; существование означает STOP без overwrite. После создания target
он retained при PASS/STOP; STOP до создания честно сообщает отсутствие retained
scratch. Exact stdout receipt совпадает с сохранённым `remote-result.json`, либо
явно сообщает невозможность его сохранить. Не запускать command без отдельного
точного подтверждения оператора.

Точная единственная команда сохранена в local receipt и требует одновременно
marker, remote SHA, manifest SHA и exact evidence path. Эти значения повторно
проверяются непосредственно перед transport; drift даёт local STOP и SSH=0.

Это закрывает локальную подготовку synthetic namespace/WAL gate, но не сам Linux
gate и не actual readback. После его PASS следующий локальный deliverable — общий
production read-only collector/transport с unit IO, atomic path hardening и полным
receipt schema; после этого потребуется отдельное разрешение на actual readback.
SSH/mount/live DB/service actions в текущем шаге=0; прежние suites не повторялись.

<a id="synthetic-linux-gate-pass-2026-09-22"></a>

## Bounded synthetic Linux gate — PASS, 2026-09-22

После точного описания одной попытки оператор ответил «продолжай». Выполнена
ровно одна hash-bound SSH попытка по неизменённому manifest SHA
`ac51ca3966bd2363d5969ecaf936c981cde35eddaf0fe3947a0209a0410a6964`.
Exit `0`, `ssh_attempts=1`, stderr `0`, transport stdin/output complete; retry и
cleanup SSH не выполнялись.

Remote receipt: **SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE**. WAL case подтвердил
чтение формы и OS-level запрет записи (`SHAPE_READ_WRITE_BLOCKED`, одна таблица);
missing-SHM и rollback-journal дали точные ожидаемые STOP
`sqlite_sidecars` / `sqlite_journal_present`. Synthetic sentinel сохранён,
mount+network namespaces закрыты внешней process group. Remote result записан,
новый scratch retained по адресу manifest.

Локальные `claim.json` и `result.json` перечитаны: claim совпадает с вложенным
claim результата, закрытая schema PASS, production DB/source/units не читались,
service actions/runtime activation=false. SHA256 evidence:
`claim.json=dc07412c3de5520f36e2406792dda5e04e85be90b9046715788f39fadd7cf523`,
`result.json=db54ce302de0accdeab03edc6ba5bed353d8d1a1ddad165fb5e1c04c130590a3`.

Этот PASS закрывает только synthetic namespace/WAL prerequisite. Он не открывал
live DB и не доказывает deployed source/runtime binding, полную schema/semantic
compatibility или writer quiescence. Следующий шаг снова локальный: собрать общий
production read-only collector/transport и его точный actual-readback contract;
actual SSH readback потребует отдельной границы. AWG2/package016 неизменны,
general issuance disabled, production stage/install/deploy отсутствуют.

<a id="actual-readback-gate-ready-2026-09-22"></a>

## Actual integration readback gate готов локально — 2026-09-22

После synthetic PASS собран общий production read-only
[local runner](../../scripts/phase16_bot_integration_readback_gate.py) и
[remote supervisor](../../scripts/vps/phase16_bot_integration_readback_remote.py).
По умолчанию runner выполняет только offline preview. Execute требует точный
marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_001`, SHA remote/исходного
manifest/gate и новый exclusive evidence-dir. Claim создаётся до trust read;
drift или занятый path дают local STOP при SSH=0. Разрешён ровно один SSH без
retry и cleanup SSH.

[Gate manifest](phase16-bot-integration-readback-gate-manifest-2026-09-22.json)
фиксирует target binding, payload и пределы: 44s work + 4s bounded cleanup + 2s
finalization внутри абсолютных 50s; transport 60s; stdout 64KiB, stderr 8KiB.
Remote supervisor приходит через stdin и не записывает source на сервер. Он
читает metadata/hash production `.py`, dist-info METADATA и `.pth`, закрытый
allowlist systemd properties без Environment/journal, а также только schema
SQLite без строк. DB child запускается в private mount+network namespaces,
bind-remount существующего DB directory read-only, открывает SQLite `mode=ro`,
`query_only` и authorizer. Service actions, application imports, Telegram,
runtime activation и remote result writes исключены.

TDD завершён **69 PASS**. Независимый review сначала нашёл permissive nested
receipt, неполный deadline/finalization, общий output cap, небезопасную partial
evidence и снятие watchdog до stdout flush. Все findings закрыты отдельными
RED/GREEN regression tests; итоговый verdict **APPROVE**, open findings 0.
Offline preview: gate SHA
`de969b61b3279f0e1748ae639949e704b7979ad9401b5289517ff57e3433d2c2`,
remote SHA `8eadb22e72616eccf81c3e238e5b6c8c1e28f7e253513d427865c1d9f3ec07fc`,
source manifest SHA
`dc8462f415890d1d8bb975f915531a314fe8bfc85a5549e1f85b58d81c3228dc`.
[Local verification](phase16-bot-integration-readback-gate-local-verification-2026-09-22.json)
содержит exact future command. Execution-001 отсутствует; actual SSH = 0,
production DB не открывалась, services не менялись.

Gate **READY_NOT_EXECUTED**. Следующая граница — отдельное точное подтверждение
одной actual readback попытки. Даже успешный receipt даст только source/runtime/
unit/schema/observed-holder evidence; он не докажет полную writer quiescence,
semantic DB compatibility, stop/switch/seed/migration/rollback или acceptance.
AWG2/package016 неизменны, general issuance disabled; production
stage/install/deploy отсутствуют.

<a id="actual-readback-execution-001-stop-2026-09-22"></a>

## Actual integration readback execution-001 — STOP_NO_RETRY

После точного подтверждения
`PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_001` preflight повторно подтвердил
AMN3 `cf1c76c8202cf31c6230862e3db2c1f1a6ca69b6`, clean worktree, три approved
SHA, свободный evidence path и неизменный Spain trust binding. Выполнена ровно
одна SSH попытка; retry и cleanup SSH не выполнялись.

[Нормализованный execution receipt](phase16-bot-integration-readback-execution-001-2026-09-22.json):
transport exit3, stdin/output complete, stderr0, remote status
`STOP_NO_RETRY`, reason `unit_show`. Закрытая receipt schema повторно
валидирована. Локальные evidence сохранены; SHA256 claim
`5f825076e423092b2ca4b85afa1aff119304cfd43ec4d65c9424b176aab5e6bb`,
result `e096becf217fde0fd196764ba604264eb064c5e72f06046f5ec6762616a43e75`.

Remote успел подтвердить только нормализованные host metadata: Linux x86_64,
Python3.12.3, SQLite3.45.1. Сбор остановился до завершения обоих unit receipts;
поэтому exact subcause внутри command/format/property boundary остаётся
**UNKNOWN**. Production source/dependencies не читались, DB не открывалась,
service actions=0, application import/write/runtime activation=false. Нельзя
переносить исторический unit snapshot в текущий PASS или считать этот STOP
доказательством отсутствия units.

Повтор этой команды запрещён consumed evidence path и no-retry contract.
Следующий допустимый шаг только локальный: подготовить новый hash-bound gate с
более точной безопасной unit-property диагностикой и новым marker/evidence path;
его SSH потребует отдельного exact approval. Stop/switch/seed/migration/
Telegram/activation не разрешены. AWG2/package016 сохранены, general issuance
disabled, production install/stage/deploy отсутствуют.

<a id="actual-readback-gate-002-ready-2026-09-22"></a>

## Actual integration readback gate-002 готов локально

После execution-001 STOP недифференцированный batch `systemctl show` заменён
локально на отдельный fixed allowlisted вызов для каждой property. Опции
расположены до фиксированного unit; `Environment` не входит в allowlist. При
ошибке fail-closed receipt раскрывает только role/property/stage/returncode и
stdout/stderr byte counts, без raw values, argv, paths или stderr. Успешный
сбор по-прежнему выдаёт только нормализованные unit fields и digests.

Новый gate связан с marker
`PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_002`, новым
[manifest](phase16-bot-integration-readback-gate-002-manifest-2026-09-22.json)
и exclusive `execution-002`. `_001` повторно использовать нельзя. Остальные
scope/caps сохранены: one SSH/no retry, absolute remote50s, transport60s,
schema-only DB в private RO mount+network namespaces, rows/env/journal/service
actions/imports/activation excluded.

TDD: три новых RED на exact per-property command, полный allowlist iteration и
bounded diagnostic receipt; итог **71 PASS**. Independent review — **APPROVE**,
open findings0. [Local verification](phase16-bot-integration-readback-gate-002-local-verification-2026-09-22.json).
Preview: gate SHA
`80a3a62bea7e5e2b6e662ad1a4ae8b95a47e69558829ce8e63c692b8c69cd52a`,
remote SHA `c5d326262724c0f7b7c280087789bebaeb3e73c6f4a1f6c38a102cdf673c315a`,
SSH0; execution-002 отсутствует.

Gate-002 **READY_NOT_EXECUTED**. Его единственная попытка требует отдельного
точного approval marker. Ни execution-001 approval, ни общие прежние разрешения
не переносятся. AWG2/package016 неизменны, issuance disabled; production
install/stage/deploy отсутствуют.

<a id="actual-readback-execution-002-stop-2026-09-22"></a>

## Actual integration readback execution-002 — STOP_NO_RETRY

После exact approval `_002` preflight подтвердил commit/hashes/trust и свободный
execution-002. Выполнена одна SSH попытка: transport exit3, stdin/output complete,
stderr0; retry отсутствует. [Нормализованный receipt](phase16-bot-integration-readback-execution-002-2026-09-22.json)
прошёл закрытую schema validation. Evidence SHA256: claim
`e22077e7468fb2e6bc4a46d1665e5542222c592106ca5a3b4af44493958677ae`,
result `e3d594711e02b3477107e6347fd5e9e394edbf1ececa17ea7f3f506e939e3417`.

STOP теперь точный: bot `ExecStartPre`, command exit0, stderr0, stdout0,
stage `format`. `systemctl show --value` для этой пустой property возвращает
zero bytes; gate ошибочно требовал terminal newline для любого значения.
Root cause — локальная нормализация empty property, не отсутствие unit и не
service failure. Source/dependencies/DB не читались; actions/imports/writes/
activation отсутствуют.

Execution-002 consumed и не повторяется. Следующий local-only fix должен
принимать zero-byte output как точное пустое значение, сохраняя newline/formats
checks для непустого output, новый marker и execution-003. Новый SSH требует
отдельного exact approval. AWG2/package016 сохранены, issuance disabled;
production install/stage/deploy отсутствуют.

<a id="actual-readback-gate-003-ready-2026-09-22"></a>

## Actual integration readback gate-003 готов локально

По evidence execution-002 исправлена только empty-property normalization:
`b''` принимается как пустое значение лишь после exit0 и stderr0. Любой
непустой output сохраняет строгие UTF-8, ровно один terminal LF, запрет CR и
embedded LF. Per-property allowlist и bounded STOP receipt gate-002 сохранены.

Новые binding: marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_003`,
[manifest](phase16-bot-integration-readback-gate-003-manifest-2026-09-22.json),
exclusive execution-003. `_002` consumed и до claim/trust отвергается тестом.
Scope/caps прежние: one SSH/no retry, remote50s/transport60s, rows/env/journal/
service actions/imports/activation excluded.

Observed zero-byte fixture дал RED; после узкого fix итог **71 PASS**.
Independent review — **APPROVE**, open findings0. [Local verification](phase16-bot-integration-readback-gate-003-local-verification-2026-09-22.json).
Preview: gate SHA
`7b6468ecb314400899e920e65cd64e8c5bbdb5fc95ecf75dee5965743e95367d`,
remote SHA `5d88cbe49de4ac6ce8619287a5bd0a3ddf0e080f93599e8a2275ed62a186fdb7`,
SSH0; execution-003 отсутствует.

Gate-003 **READY_NOT_EXECUTED** и требует отдельного exact approval. AWG2 и
package016 неизменны, issuance disabled; production install/stage/deploy нет.

<a id="actual-readback-execution-003-unknown-2026-09-22"></a>

## Actual integration readback execution-003 — UNKNOWN_NO_RETRY

После exact approval `_003` preflight подтвердил commit/hashes/trust и свободный
execution-003. Выполнена одна SSH попытка без retry. Transport завершился:
exit255, stdin68077 complete, stdout0, stderr49, output complete, pipe failures0.
Безопасная классификация stderr — `UNCLASSIFIED_STDERR`, raw stderr не сохранён;
remote JSON receipt отсутствует, local reason `JSONDecodeError`.

[Нормализованный receipt](phase16-bot-integration-readback-execution-003-2026-09-22.json),
evidence SHA256: claim
`79a07b1c9e6de8c5ed6908f56f49ab8a4d82233738b2b66dc38166b6cd92b578`,
result `57c346e5c15f07f8796363fb761121aaf81c8610df89a46e9185adce598cb716`.
Так как remote receipt не получен, достигнутые read stages и фактическое
наблюдение service/write/import/activation — **UNKNOWN**. Код gate не содержит
этих mutations, но это не заменяет terminal receipt. Нельзя переносить PASS или
STOP evidence предыдущих попыток на execution-003.

Execution-003 consumed; retry запрещён. Следующий local-only scope — безопасно
различить no-stdout/non-receipt transport до JSON parse, расширить только
redacted SSH stderr categories и hash-bind общий local transport helper. Затем
новый marker/execution-004 и отдельный exact approval. AWG2/package016 сохранены,
issuance disabled; production install/stage/deploy отсутствуют.

<a id="actual-readback-gate-004-ready-2026-09-22"></a>

## Actual integration readback gate-004 готов локально

После execution-003 UNKNOWN пустой stdout теперь получает стабильную причину
`transport_no_remote_receipt` до JSON parse. Общий transport helper добавил
redacted HINT categories для reset/disconnect/broken-pipe/KEX/banner; специфичные
KEX/banner проверяются раньше общих patterns. Evidence по-прежнему содержит
только sizes, prefix SHA, pipe states и category, без raw stderr. Categories —
диагностические hints, не доказанная root cause.

Shared [transport helper](../../scripts/phase16_bot_linux_gate.py) впервые включён
в закрытые manifest `sha256_lf`/`bytes_lf`; его drift останавливает gate до SSH.
Новые binding: marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_004`,
[manifest](phase16-bot-integration-readback-gate-004-manifest-2026-09-22.json),
exclusive execution-004. `_003` consumed и отклоняется до claim/trust.

TDD на no-receipt, five redacted classifier paths, helper binding и old-marker
rejection: **73 PASS**. Independent review — **APPROVE**, open findings0.
[Local verification](phase16-bot-integration-readback-gate-004-local-verification-2026-09-22.json).
Standalone pytest transport module не запущен: pytest отсутствует в bundled
runtime; новые paths функционально покрыты прошедшей integration unittest suite.
Preview: gate SHA
`128ae86f4a06b0e424df40561527660d72e117f26ca476f0cd62ef171e75443b`,
remote SHA `fb29b0e6643a506cdbb20aef6ebb37fe4693f3116e76b573d50162fd7c20508b`,
transport helper SHA
`713289a6082bf621d704e6dd3b04855fa020fbfecc8a9e86db8a861019bbd35e`,
SSH0; execution-004 отсутствует.

Gate-004 **READY_NOT_EXECUTED** и требует отдельного exact approval. Scope/caps
и exclusions прежние. AWG2/package016 неизменны, issuance disabled; production
install/stage/deploy отсутствуют.

<a id="actual-readback-execution-004-unknown-2026-09-22"></a>

## Actual integration readback execution-004 — UNKNOWN_NO_RETRY

После exact approval `_004` preflight подтвердил commit/hashes/trust и свободный
execution-004. Выполнена ровно одна SSH попытка без retry. Transport завершился:
exit255, `failure_stage=stdin_write`, requested68077, accepted0, stdout0,
stderr49, output complete. Safe stderr classification — `UNCLASSIFIED_STDERR`,
raw stderr не сохранён; remote JSON receipt отсутствует. Local reason —
`transport_stdin_write`.

[Нормализованный receipt](phase16-bot-integration-readback-execution-004-2026-09-22.json),
evidence SHA256: claim
`7bf290e3a37ce364edf1f458e63ef290a1c9546420a77c3bb0fdc5a267efc0da`,
result `59f86abc063434f5cf7a4ca159aa7c698f6b02198ad488f8b2e638223e14cfe4`.
Так как remote receipt не получен, production source/dependencies/database read
stages и фактическое наблюдение service/write/import/activation — **UNKNOWN**.
Кодовые exclusions не заменяют terminal receipt.

Execution-004 consumed; повтор запрещён. Наблюдаемая граница сместилась раньше,
чем в execution-003: SSH завершился до принятия первого байта framed stdin. Это
не доказывает handshake, auth или remote-command subcause. Следующий допустимый
local-only scope — подготовить новый exact-bound zero-input SSH preflight,
который меняет только наличие stdin payload: успех отделит payload/framing path,
а failure до receipt оставит проблему в SSH/auth/remote-command boundary. Новый
SSH потребует нового marker и отдельного approval. AWG2/package016 сохранены,
issuance disabled; production install/stage/deploy отсутствуют.

<a id="ssh-zero-input-preflight-gate-005-ready-2026-09-22"></a>

## Zero-input SSH preflight gate-005 готов локально

После execution-004 systematic diagnosis не предлагает transport fix без root
cause. Следующий probe меняет только одну переменную: исключает framed stdin.
[Runner](../../scripts/phase16_bot_transport_preflight_gate.py) вызывает fixed
`/usr/bin/python3 -I -S -B -c` с exact approval argument и `input_bytes=0`.
Remote command не читает source, units, dependencies, database, environment или
Telegram и не выполняет service actions; closed receipt сообщает только marker,
нулевые scope-счётчики и `SSH_ZERO_INPUT_PREFLIGHT_PASS`.

[Manifest](phase16-bot-transport-preflight-gate-005-manifest-2026-09-22.json)
hash/size-binds runner и shared transport helper, target binding и exclusive
execution-005. Limits: one SSH, no retry/cleanup SSH, transport20s, stdout4KiB,
stderr8KiB, stdin0. Старый `_004` marker отклоняется до claim/binding/transport.

TDD:5 ожидаемых RED до реализации, затем5 GREEN; вместе с existing integration
suite итог **78 PASS**. [Local verification](phase16-bot-transport-preflight-gate-005-local-verification-2026-09-22.json).
Offline preview: gate SHA
`386f27dcfc250e5b1f8ae0c9d8be719aec178aa60cb8c7ab901e1570dd675b0a`,
remote command SHA
`e4fbc8b0e2143358f733cfb4ce52f0f02f02e36a0f8eef2ba6531f20665b9e4b`,
SSH0; execution-005 отсутствует.

Интерпретация заранее ограничена: PASS подтвердит SSH/auth/remote-command только
без stdin payload и не подтвердит production integration compatibility. Отсутствие
receipt покажет, что failure boundary не специфична для framed stdin, но точный
subcause останется UNKNOWN. Gate-005 **READY_NOT_EXECUTED** и требует exact marker
`PHASE16_SSH_ZERO_INPUT_PREFLIGHT_20260922_005`. AWG2/package016 неизменны,
issuance disabled; production install/stage/deploy отсутствуют.

<a id="ssh-zero-input-preflight-execution-005-pass-2026-09-22"></a>

## Zero-input SSH preflight execution-005 — PASS

После точного approval `_005` один SSH завершился exit0, stdin requested/accepted0,
stdout293, stderr0, pipe failures0. Получен точный closed remote receipt
`SSH_ZERO_INPUT_PREFLIGHT_PASS`; retry не выполнялся. [Нормализованная запись](phase16-bot-transport-preflight-execution-005-2026-09-22.json)
ссылается на неизменённые evidence: claim SHA256
`bc66d4137d008714dc5e3b491354d884cac9fc902e3c7f436923c061e805ca76`,
result SHA256
`06470f9c99d390de0ab074583331bd6cf242dca9fefa64d5d104e18d3a888bb6`.

PASS подтверждает SSH connection/auth и выполнение короткой remote Python command
без stdin payload на момент попытки. Он не определяет причину transport failures
`_003` и `_004`: они могли зависеть от времени, payload или иного условия. Большой
framed stdin, полный integration readback и compatibility остаются **UNKNOWN**.
Fixed remote command не содержит production reads/actions/database access/imports/
activation; receipt содержит соответствующие нулевые поля. Следующий локальный
вопрос — подготовить отдельный узкий hash-bound frame transport probe с новым
marker и exclusive evidence. Execution-005 consumed; новый SSH требует отдельного
approval. AWG2/package016 сохранены, issuance disabled; install/stage/deploy нет.

<a id="ssh-bound-frame-preflight-gate-006-ready-2026-09-22"></a>

## Bound-frame SSH preflight gate-006 готов локально

Новый [runner](../../scripts/phase16_bot_frame_preflight_gate.py) проверяет
передачу stdin объёмом ровно68077 байт — размер frame execution-004. Данные
синтетические и детерминированные; их SHA256
`2e47b52d9c8a4480f3c5ec77997d2732b7c35c88251ae6872620329ccf0e7437`.
Remote `/usr/bin/python3 -I -S -B -c` читает максимум68078 байт и возвращает
только exact PASS или `STOP_NO_RETRY/frame_binding`; raw frame и stderr не входят
в persisted receipt. Команда не читает production source/units/dependencies/DB,
не импортирует приложение и не выполняет service action/activation.

[Manifest](phase16-bot-frame-preflight-gate-006-manifest-2026-09-22.json)
hash/size-binds runner, transport helper и frame, target binding и exclusive
execution-006. Один SSH, transport25s, combined output cap8192, no retry/cleanup
SSH. `_005` marker отвергается до claim/transport. TDD:5 ожидаемых RED до
реализации;6 GREEN, вместе с существующими наборами **84 PASS**.
[Local verification](phase16-bot-frame-preflight-gate-006-local-verification-2026-09-22.json).
Offline preview: gate SHA
`4724a8137db3b5ccd03ec35bbd144c9a36063c2fb9d59e09059d1ea9fbcf5db2`,
remote command SHA
`52244f27968b250e2168dad3f95c534b154d590e7256bc847faf10de9d32f053`,
SSH0; execution-006 отсутствует.

PASS подтвердит только, что синтетический frame прошёл в момент проверки;
предыдущие transport errors могут быть intermittent. STOP покажет точный frame
mismatch; отсутствие receipt сохранит `UNKNOWN_NO_RETRY`. Ни один исход не
равен production integration acceptance. Gate-006 **READY_NOT_EXECUTED**;
для нового SSH нужен exact marker
`PHASE16_SSH_BOUND_FRAME_PREFLIGHT_20260922_006`. AWG2/package016 сохранены,
issuance disabled; install/stage/deploy отсутствуют.

<a id="ssh-bound-frame-preflight-execution-006-pass-2026-09-22"></a>

## Bound-frame SSH preflight execution-006 — PASS

После exact approval `_006` один SSH завершился exit0; stdin requested/accepted
68077/68077, stdout382, stderr0, pipe failures0. Удалённая команда подтвердила
SHA256 всего синтетического frame и вернула точный closed receipt. Retry0.
[Нормализованная запись](phase16-bot-frame-preflight-execution-006-2026-09-22.json)
проверена по внешним evidence: claim SHA256
`3f7cf4ab17de24244f6d7e33d8dc9519104858765ad91f597fed883e91298a41`,
result SHA256
`30e619602647208ef0e91a6f538723e2a726a41798fbb008516e6f72108337f1`.

Это подтверждает передачу 68077 байт в момент прогона, но не объясняет
transport errors `_003`/`_004`: их возможная зависимость от времени остаётся.
Actual production readback и integration compatibility по-прежнему UNKNOWN.
Execution-006 consumed; следующий допустимый шаг — новый exact-bound actual
readback с одним SSH и отдельным approval. AWG2/package016 сохранены, issuance
disabled, install/stage/deploy отсутствуют.

<a id="actual-readback-gate-007-ready-2026-09-22"></a>

## Actual integration readback gate-007 готов локально

Новый [runner](../../scripts/phase16_bot_integration_readback_gate_007.py)
использует неизменённые portable core, source manifest, payload, transport helper
и caps gate-004. Supervisor создаётся только заменой ровно одного marker `_004`
на `_007`; test сравнивает каждый байт, а [manifest](phase16-bot-integration-readback-gate-007-manifest-2026-09-22.json)
hash/size-binds обе версии runner, преобразованный supervisor, core, helper,
payload, source и старый gate manifest. Старые файлы и execution-004 не меняются.

Новый marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_007`, exclusive
execution-007. `_004` отклоняется до claim/transport. Remote budget50s включает
cleanup/finalization; transport60s, stdout64KiB/stderr8KiB, one SSH/no retry.
Production readback только source/units/dependency metadata и SQLite schema в
private read-only mount+network namespaces, без строк БД, service actions,
application imports, Telegram или activation.

Шесть ожидаемых RED до реализации, затем шесть GREEN; вместе с существующими
наборами **90 PASS**. [Local verification](phase16-bot-integration-readback-gate-007-local-verification-2026-09-22.json).
Offline preview: gate SHA
`8aa7d8418f927a479a62783bbf1632d69e9b19ecceadc00f9d3abef62ae8925d`,
remote SHA `2dc1d1678b4bf7d81e0e3a12e5e880fe8d20d1f5351a294d338d97016e1b00f6`,
source manifest SHA
`dc8462f415890d1d8bb975f915531a314fe8bfc85a5549e1f85b58d81c3228dc`;
SSH0, execution-007 отсутствует. Gate-007 **READY_NOT_EXECUTED** и требует
отдельного exact approval. PASS `_006` не гарантирует новый transport result.
AWG2/package016 сохранены, issuance disabled; install/stage/deploy отсутствуют.
