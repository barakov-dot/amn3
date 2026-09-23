# Phase16 Task3B: bounded integration readback contract — 2026-09-22

Статус на 23.09: **GATE011_COMPLETE_WITH_LIMITATIONS / OLD_SCHEMA_METADATA_MATCH**.
[Полный readback011 завершён](#actual-readback-execution-011-complete-2026-09-23);
DB migration/semantic compatibility, writer fence и switch не разрешены.
[Synthetic Linux guard PASS](#synthetic-linux-gate-pass-2026-09-22),
[результат009](#actual-readback-execution-009-stop-2026-09-22) и
[результат010](#actual-readback-execution-010-stop-2026-09-23)
отделены от первоначального проекта ниже. Прежние approvals использованы;
новое live-исполнение не разрешено.
[Локальная диагностика полного schema coverage завершена](#schema-coverage-diagnosis-2026-09-23);
[Согласованное исправление v3 проверено локально](#schema-reader-v3-ready-2026-09-23):
125 PASS; последующий gate011 исполнен один раз по exact approval, см. результат ниже.
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

Ниже **исходные проектные hard caps**, не измеренная длительность target.
Реализованное23.09 изменение METADATA cap относится только к v2/новому gate010
и описано отдельно в конце документа. Превышение
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

<a id="actual-readback-execution-007-unknown-2026-09-22"></a>

## Actual integration readback execution-007 — UNKNOWN_NO_RETRY

После exact approval `_007` и push `ec2f8926e773e2c9233c9acc65df2fbee151fb7e`
выполнена ровно одна SSH-попытка. [Нормализованная запись](phase16-bot-integration-readback-execution-007-2026-09-22.json)
связана с локальными `claim.json` SHA256
`752d4163d1539b01e375ab68c4afa6f555e326e5e1ebbae758be6fd8a34ebb3b`
и `result.json` SHA256
`1a7988a031a2675a4b8410536d6807c4358f5164b9a41043b4980e09242fb849`.
Путь к ним — `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-integration-readback-runner-20260922/execution-007`.

Transport вернул exit3: stdin 68077/68077, stdout 14614/14614 байт,
stderr0, output complete, pipe failures0. JSON синтаксически разобран,
но локальный закрытый валидатор отверг его с `receipt_binding`.
Raw stdout не сохранялся. Поэтому remote status/reason, завершённые стадии чтения,
production DB/source/dependency observations и отсутствие live side effects
**не подтверждены**; размер ответа не служит доказательством стадии. Код
remote collector не содержит service actions, DB write, application import или
activation, но это свойство кода не заменяет проверенный remote receipt.
Approval `_007` использован, retry запрещён. Gate-007 не повторять.

Локальная статическая сверка форм host/units/source/dependencies и существующих
fixture-тестов не воспроизвела точное расхождение; исправление валидатора без
доказательства конкретного поля не делалось. Следующий возможный локальный шаг —
подготовить новый exact-bound gate с закрытым кодом места отказа валидатора и
RED/GREEN тестами; ни этот шаг, ни текущая запись не разрешают новый SSH.

<a id="actual-readback-gate-008-ready-2026-09-22"></a>

## Actual integration readback gate-008 готов локально

После согласования локального дизайна подготовлены [runner](../../scripts/phase16_bot_integration_readback_gate_008.py)
и [manifest](phase16-bot-integration-readback-gate-008-manifest-2026-09-22.json).
Remote collector, portable core, source manifest, payload и transport limits
сохранены; supervisor побайтово отличается от gate-004 только marker `_004` →
`_008`. Новый runner при невалидном STOP receipt сохраняет лишь фиксированное
имя стадии (`host`, `units_before`, `source`, `dependencies`, `database` и т. д.)
либо `envelope`; значения и raw stdout не пишет. Невалидный receipt остаётся
`UNKNOWN_NO_RETRY`, и diagnostic не превращается в production observation.
Новый marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_008` привязан к
exclusive execution-008, one SSH/no retry, remote50s/transport60s.

[Локальная проверка](phase16-bot-integration-readback-gate-008-local-verification-2026-09-22.json):
3 ожидаемых RED до реализации, затем релевантный набор **93 PASS**; preview
SSH0. Byte-for-byte marker-only и manifest binding PASS. Gate SHA256
`eb47d0d56a004bfeefcdb1fe1bab4a5c62dace34b2848402f6b596ab0947f870`,
remote SHA256 `49a917e65565293353abea8e77034c05f4e1aae3abf7028e18a9df3f18ed43ad`,
source manifest SHA256
`dc8462f415890d1d8bb975f915531a314fe8bfc85a5549e1f85b58d81c3228dc`.
Более широкий `test_phase16_bot_*.py` discovery дал два import error из-за
отсутствующего `pytest` в изолированном Python; целевой набор их не включает.
Gate-008 **READY_NOT_EXECUTED**. Для push нужен отдельный exact HEAD/origin/ref
approval; для одного SSH — отдельный exact marker `_008`. AWG2/package016
сохранены, issuance disabled; install/stage/deploy отсутствуют.

<a id="actual-readback-execution-008-unknown-2026-09-22"></a>

## Actual integration readback execution-008 — UNKNOWN_NO_RETRY

После exact push `a296668d5604a80df9f717814a4d6b459ac32930` и approval `_008`
выполнена ровно одна SSH-попытка. [Нормализованная запись](phase16-bot-integration-readback-execution-008-2026-09-22.json)
связана с `claim.json` SHA256
`b856a061cca808e1910c2e347adbcc72f92c9abc1300fb7d31d91a6852ff7223`
и `result.json` SHA256
`910b4d9f1679738120c54fcef7121a09646a72fa54a94c784d7a1be2e7668ac9`.
Путь — `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-integration-readback-runner-20260922/execution-008`.

Transport exit3, stdin68077/68077, stdout14614/14614, stderr0, output complete,
pipe failures0. JSON разобран, но local validator снова вернул
`receipt_binding`; закрытый diagnostic указал `units_before`. SHA256 полного
stdout `2cd91d9ab0b8736de6f159c2c99f3f4f9dc7b853db5cac099bdc33f0169692ec`
совпал с execution-007. Raw stdout не сохранялся; это не раскрывает фактические
поля, remote reason или завершённые read stages. `_008` использован, retry
запрещён; production observations и отсутствие live side effects остаются UNKNOWN.

Локальный synthetic пример выявил конкретное **возможное** расхождение в
`units_before`: portable parser сохраняет `KillSignal=15` и
`FinalKillSignal=9`, а local validator принимал только `SIG…` или `UNKNOWN`.
Пример воспроизвёл `receipt_binding`, но фактические значения remote ответа
неизвестны; другие ошибки в unit snapshot не исключены. Исправление ниже
ограничено этими полями и не переинтерпретирует receipt `_008` задним числом.

<a id="actual-readback-gate-009-ready-2026-09-22"></a>

## Actual integration readback gate-009 готов локально

После согласования bounded design подготовлены [runner](../../scripts/phase16_bot_integration_readback_gate_009.py)
и [manifest](phase16-bot-integration-readback-gate-009-manifest-2026-09-22.json).
Remote collector, portable core, payload, source manifest и caps не меняются;
supervisor побайтово отличается от gate-004 только marker `_004` → `_009`.
Local validator копирует receipt, заменяет **только для проверки** десятичные
строки `1..64` в `KillSignal`/`FinalKillSignal` двух unit snapshots на
`UNKNOWN`, затем запускает прежнюю закрытую проверку остальных полей.
Исходный receipt сохраняется только после полного validation. `0`, `65`,
`015` и постороннее unit поле отклонены тестами. При новом отказе остаются
`UNKNOWN_NO_RETRY` и закрытый код стадии, raw stdout не пишется.

[Локальная проверка](phase16-bot-integration-readback-gate-009-local-verification-2026-09-22.json):
4 ожидаемых RED до реализации, затем **97 PASS** в релевантном наборе;
marker-only и manifest binding PASS, preview SSH0. Gate SHA256
`f624594cbee5eadbbe86d4871b94d377554df445bf073c4568f901caed8e383b`,
remote SHA256 `224f5476fbc6ccb7314b9552fd36dc260ba3134da4225a59fe62beb03aaa82cc`,
source manifest SHA256
`dc8462f415890d1d8bb975f915531a314fe8bfc85a5549e1f85b58d81c3228dc`.
Marker `PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_009` привязан к exclusive
execution-009, one SSH/no retry, remote50s/transport60s. Gate-009
**READY_NOT_EXECUTED**. Push и SSH требуют отдельных exact approvals.
AWG2/package016 сохранены, issuance disabled; stage/install/deploy отсутствуют.

<a id="actual-readback-execution-009-stop-2026-09-22"></a>

## Actual integration readback execution-009 — STOP_NO_RETRY

После exact push `09dcc7e14f4bddc2bac41c71a16c4711e7e91f88` и approval `_009`
выполнена ровно одна SSH-попытка. [Нормализованная запись](phase16-bot-integration-readback-execution-009-2026-09-22.json)
связана с `claim.json` SHA256
`765bf55665cab7a02387864f9ed3eba8da161998df163b1886a2a505427e055e`
и `result.json` SHA256
`cfa7c590347ceb17b61515000246fdc7f7b24d59d66ac30caf985e17836508ec`.
Путь — `C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-integration-readback-runner-20260922/execution-009`.

Transport exit3, stdin68077/68077, stdout14614/14614, stderr0, output complete,
pipe failures0. Remote receipt **прошёл** новый local validator и содержит
`STOP_NO_RETRY / remote_exception` с завершёнными `host`, `units_before`,
`source`. Это тот же полный stdout SHA256, что в `_007`/`_008`; прежняя локальная
ошибка валидатора скрывала этот STOP. По последовательному коду исключение
возникло после source и до готового dependency result. Его подпричина UNKNOWN:
`core.Stop` и другие исключения попадают в общий `remote_exception`; не
приписывать это отсутствующему dependency root или конкретному METADATA.
DB stage не достигнут. `_009` использован, retry запрещён.

Source относительно bound AMN2 `6e682356ed14a62d636ee58039fd3a389e794809`
имеет **DIFFERENT**: 126 ожидаемых `.py`, присутствуют 102, отсутствуют 24,
ещё 24 отличаются, extra0; runtime binding UNKNOWN. `app/main.py` совпадает
по SHA с [снимком 21.09](phase16-ssh-event-loop-applicability-2026-09-20.md#spain-bot-target-readback-v2-2026-09-21),
`bot/workflow_worker.py` и `bot/lifecycle.py` отсутствуют и сейчас.
Локальное сравнение 102 наблюдаемых файлов с AMN2 commits 6e68235, 1bd7f62,
2069e41 и 56540e2 дало по 78 совпадений с каждым; exact deployed revision
этим не установлен. Bot/web unit snapshots показывают active, expected
entrypoint/cwd, но это не startup/drain или длительная stability проверка.
Validated remote flags: service actions0, database write attempted=false,
application imported=false, runtime activation=false.

Этот свежий source mismatch уже блокирует integration acceptance. Следующий
локальный шаг — сверить уже [подготовленный отдельный bot candidate](phase16-bot-candidate-runbook-2026-09-21.ru.md)
6e68235, runtime40 и границы shared source/DB с существующим integration
планом; новый package build не нужен. Retained ZIP SHA256
`e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7`
и manifest SHA256
`6792cb2cd28b0ce70ae031cac04b29f40db908f5e8bad0770e689de390a9a37d`
повторно сверены локально после `_009`. Новый SSH для раскрытия dependency
exception не является ближайшим gate: сначала нужен reviewable путь установки
candidate и rollback с отдельными approvals.
AWG2/package016 не менять; general issuance disabled, stage/install/deploy
не выполнялись.

<a id="source-history-reconciliation-2026-09-23"></a>

## Локальная сверка серверного source с историей — 2026-09-23

Без SSH использована сохранённая карта `remote.partial.source.files` из
execution-009/result.json; внешний SHA256 файла повторно проверен по записи
выше. В локальном AMN2 при HEAD `6e682356ed14a62d636ee58039fd3a389e794809`
команда `git rev-list --all -- app` дала 361 commit изменения app. Из них
70 совпали по SHA256 `app/main.py`. Для этих кандидатов через `git ls-tree -rz`
и `git cat-file --batch` сопоставлены множества путей `.py`, размеры и SHA256
Git blobs со всеми 102 наблюдаемыми файлами. Поиск занял 2.94s, лимит100s;
сеть, checkout файлов и импорт приложения не использовались.

**Полное совпадение в наблюдаемом scope: AMN2
`55dc243b8e6c6bdb57f8301b56326e4cd4072d19` (2026-07-20).**
Все 102/102 размера и хеша совпали; множества `.py` путей равны, серверный
`extra_count=0`. Результат дополнительно проверен прямым `git show` каждого
из 102 blobs. Это единственное такое совпадение среди проверенных commits
изменения app; commits без изменения app могли содержать тот же source.
`276e6061db62c80ad4cce0e6dbb29b281e4fd421` также совпал по 102 файлам, но
содержит два дополнительных migration `.py`, отсутствующих в снимке.

Идентификаторы для повторной локальной сверки при необходимости:

- Git tree `55dc243:app`: `32b14f343016610a0f4082d8b24fda7bce2735ee`;
  это идентификатор Git, не утверждение проверки всех non-Python assets.
- SHA256 карты 102 файлов, сериализованной Python
  `json.dumps(files, sort_keys=True, separators=(',', ':')).encode()`:
  `a79734e30a8922830c8f5a2b7d6757f95d52bc75a7e3b0cd6c289392738087e7`.

Так установлен **эталон старого Python source**, а не exact deployed commit,
текущие загруженные модули процесса или полный release. Non-Python assets,
dependencies и фактическая DB schema этим не проверены; runtime binding UNKNOWN.
Наличие старого `schema.py` не доказывает применение именно его схемы к БД.
Уже выполненный synthetic переход `55dc243 → 6e68235` теперь относится к
совпавшему старому source; его ограниченное покрытие и необходимость проверки
фактической схемы сохраняются. Тесты повторно не запускались.

Оставшиеся условия переключения собраны в
[матрице готовности bot candidate](phase16-bot-candidate-runbook-2026-09-21.ru.md#switch-readiness-2026-09-23).
Это локальное уточнение evidence, не новый remote gate и не разрешение activation.

<a id="consolidated-readback-design-2026-09-23"></a>

## Единый readback runtime/DB: локальная подготовка — 2026-09-23

Статус при подготовке: **DESIGN_READY_NOT_IMPLEMENTED**, SSH0; после согласования
оператора реализация завершена в [следующем разделе](#actual-readback-gate-010-ready-2026-09-23).
Цель следующего исполнения —
получить статические runtime metadata, guarded DB shape и наблюдаемых holders
за одну ограниченную попытку существующего collector. Не обещать полный список
writers, effective runtime binding или готовность switch по одному снимку.
Повтор transport/signal preflights `_005–009` и попытка только ради раскрытия
текста exception не предлагаются. Перед любым новым remote approval нужны
локальный fix, проверки полного пути receipt и новые checksum bindings.

### Доказанный локальный дефект, не установленная причина live STOP

`collect_dependencies` вызывает `safe_read(METADATA, 65536)`, хотя для
Name/Version разбираются только headers. На сохранённом runtime40 проверены
SHA256 всех 40 wheels против lock из exact AMN2 6e68235, без установки/import
зависимостей. Совокупный размер их METADATA — 511094 bytes; два превышают cap:

| Runtime dependency | METADATA bytes | Header bytes до пустой строки | Результат штатного safe_read |
| --- | ---: | ---: | --- |
| pydantic 2.13.4 | 109397 | 2350 | core.Stop: file_cap |
| yarl 1.24.5 | 103964 | 1797 | core.Stop: file_cap |

Wheel SHA256 соответственно:
`45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba` и
`f08c7513ecef5aad65687bfdf6bc601ae9fccd04a42904501f8f7141abad9eb9`.
Воспроизведение использовало только временные копии двух METADATA и текущий
core.safe_read; обе дали ожидаемый file_cap. Временные файлы удалены штатным
TemporaryDirectory, сервер и retained candidate не менялись.

В remote main обработчик ловит RemoteStop, но класс загруженного core.Stop
ему не наследует. Он попадает в общий Exception → remote_exception; аналогично
теряются причины FileNotFoundError/PermissionError между этапами. Поэтому
из009 нельзя выбрать между file_cap, отсутствующим root и другой причиной.
Доказаны непригодность текущего cap для собственного candidate и потеря
классификации ошибок; наличие этих версий/размеров на сервере не проверено.

### Ограниченный дизайн изменения для согласования

1. Только для `.dist-info/METADATA` поднять cap до262144 bytes. Сохранить
   total8MiB/8s,128 dist-info/1024 entries; `.pth` остаётся65536 bytes/16files.
   Общий safe_read и его nofollow/type/identity/change guards не ослаблять.
   Name/Version output прежний; body/неизвестные names наружу не выходят.
   Это проще отдельного prefix-reader, которому понадобились бы новые правила
   неполного чтения. Чтение только headers оставлено за scope этого fix.
2. На границах существующих этапов классифицировать core.Stop и ожидаемые
   filesystem errors фиксированными allowlisted reason codes с этапом в поле
   reason (например dependencies_file_cap/dependencies_path_missing).
   Не копировать str(error), пути, SQL, errno text или traceback. Неизвестная
   ошибка → фиксированный stage_exception. Remote timeout/cleanup STOP не
   перехватывать как разрешение продолжить. Receipt envelope v1 сохраняется.
3. Для DB child сохранить фиксированную STOP reason только после строгой
   проверки child JSON/exit/limits и allowlist; произвольный child output не
   отражать. Защита namespace/read-only mount/SQLite и порядок open неизменны.
   Если child receipt повреждён, остаётся database_child/UNKNOWN, без fallback.
4. Сохранить fail-closed последовательность: ошибка пути, cap, I/O, guard,
   timeout или unit drift останавливает попытку. Валидные source DIFFERENT,
   missing/different pins и incomplete holder coverage остаются evidence с
   ограничениями; не повышать их до integration PASS. После fatal dependency
   ошибки DB не открывается. Одно исполнение может снова закончиться STOP —
   полнота результата не гарантируется ценой ослабления safeguards.
5. Переиспользовать проверенный transport и numeric-signal validation009;
   новый runner/manifest должен bind весь изменённый core/remote/validator,
   payload, target и caps. Старые receipts/manifests не переписывать, старые
   approval markers отвергать. Новый marker/hashes назначить после локальных
   проверок, не публиковать прежнюю команду как готовую к повтору.

Scope реализации после согласования: существующий core dependency reader,
remote stage/child error boundaries, связанный local validator и checksum
builder/runner; targeted integration-readback tests. App/DB schema/production
units, locks/wheels, bot ZIP и package016 не меняются. Это не новый subsystem.

### Проверки до запроса SSH

| Проверка | Обязательный результат |
| --- | --- |
| Две воспроизведённые METADATA и runtime40 fixture | RED на прежнем cap, затем корректные40 pins без import/network; hash-bound wheels как данные |
| METADATA262144/262145; .pth65536/65537; total/count/time caps | Граница разрешена, превышение STOP; cap не превращается в truncation/PASS |
| Symlink, смена inode/mtime, missing/denied path | Сохранён fail-closed; после отказа dependencies вызов DB child отсутствует |
| core.Stop/OS error/unexpected exception по этапам | Валидируемый фиксированный reason; завершённые partial blocks сохранены |
| Secret-bearing exception и child output | В нормализованном receipt нет raw сообщений/путей/SQL; malformed child отклонён |
| PASS/STOP end-to-end collector → transport fixture → validator | Числовые signals15/9 принимаются; повреждённые/лишние поля и неверные exits отклонены |
| Gate binding/claim/timeout/cleanup | Drift и старые approvals отвергнуты до SSH; one attempt, no retry; preview SSH0 |

Один релевантный итоговый integration-readback suite после fix; завершённые
worker/lifecycle/Linux suites на неизменённом app не повторять. Изменение
SQLite guard не входит в дизайн; при необходимости такого изменения остановить
этот scope и отдельно пересмотреть его Linux проверку до live-readback.

Remote пределы остаются: transport60s, remote50s (work44/cleanup4/finalization2),
DB transaction2s/child5s, stdout64KiB/stderr8KiB; один SSH, no retry. Никаких
service actions, app imports, reads env/rows/argv/logs, backup или migrations.
При COMPLETE следующий шаг — offline оценка actual shape и старого source;
при STOP — разбор сохранённого результата без автоматической новой попытки.
Writer completeness/startup seed policy/backup/fence требуют своих фактов и
решений даже при COMPLETE. Новые filesystem roots или чтение конфигов ради
поиска неизвестных writers этим дизайном не разрешаются.

<a id="actual-readback-gate-010-ready-2026-09-23"></a>

## Actual integration readback gate010 — локальный fix готов, SSH0

По согласованию оператора реализован описанный выше bounded fix. Сохранены
отдельные v2 [core](../../scripts/vps/phase16_bot_integration_readback_v2.py),
[remote supervisor](../../scripts/vps/phase16_bot_integration_readback_remote_v2.py)
и [runner](../../scripts/phase16_bot_integration_readback_gate_v2.py).
Это версии прежнего collector: старые файлы/manifests/receipts не менялись,
чтобы не перепривязывать уже использованные approvals и Linux guard evidence.
Дублирование frozen версии намеренное; correctness новой версии проверяется
delta и регрессиями. Core отличается только cap METADATA65536→262144;
код SQLite/WAL/namespace guard, .pth cap и source reader побайтно сохранён.

Remote wrapper передаёт только фиксированные stage/core/filesystem reasons,
сохраняет partial blocks и останавливается до DB при отказе dependencies.
DB child STOP принимается только при exit3, stderr0, точной форме и allowlist
reason; malformed output не отражается. Local validator сохраняет numeric
signals009, проверяет новый allowlist reason, а local exceptions больше не
публикуют произвольный текст даже если он похож на безопасный identifier.
Не установлена причина серверного009; работоспособность live path не заявляется.

[Локальные проверки](phase16-bot-integration-readback-gate-010-local-verification-2026-09-23.json):
начальный RED — 9 tests/10 failures с subtests, errors0; дополнительные RED
для binding и двух каналов exception disclosure. Итоговый целевой набор
**108 PASS / 0 FAIL / 0 ERROR / 0 SKIP, 2.847s** включает прежние readback tests
и [новые регрессии](../../tests/test_phase16_bot_integration_readback_v2.py).
Отдельно все40 wheels сверены с exact runtime lock; temporary metadata-only
fixture дал40/40 matched pins, missing/different/extra0, всего511094 bytes.
Зависимости не устанавливались и не импортировались. Fixture удалён,
retained candidate и package016 сохранены. Проведён self-review delta;
независимый review в этом ходе не выполнялся.

[Новый manifest](phase16-bot-integration-readback-gate-010-manifest-2026-09-23.json)
фиксирует source6e68235, новые core/payload/remote/runner, старый validator и
transport, target и caps. Marker:
`PHASE16_ACTUAL_INTEGRATION_READBACK_20260923_010`; прежние markers отвергаются.
Evidence directory — существующий parent
`C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-integration-readback-runner-20260922`
с **новым** exclusive `execution-010`; он при preview отсутствует.

Preview PASS, SSH0:

- Gate SHA256: `388e9805b54a13ad649de84f2565e2a4371653360a0e297b13ace43a160b23f6`.
- Remote SHA256: `b1c8612dec962c74f4586dd3fd4bb01f70052d49b55395fa898d23c975759bf1`.
- Source manifest SHA256: `dc8462f415890d1d8bb975f915531a314fe8bfc85a5549e1f85b58d81c3228dc`.
- Payload SHA256: `1e817e1a05b74733577341b103453820d5a54438e500efd596ce46718425ab3b`.

Будущий gate имеет одну попытку, transport60s/remote50s, read transaction2s,
child5s, metadata cap256KiB/total8MiB и неизменные остальные limits. Source,
metadata, guarded DB shape и observed holders собираются последовательно;
fatal failure даёт STOP_NO_RETRY, не обход защиты ради полного результата.
AWG2_UNTOUCHED, package016 immutable, issuance disabled. Реальные rows/env/
argv/logs, service actions, app startup, backup/migration, stage/install
исключены. Local PASS не является DB compatibility или разрешением switch.
Push и один live gate требуют отдельных точных approvals; сейчас не выполнены.

<a id="actual-readback-execution-010-stop-2026-09-23"></a>

## Actual integration readback execution010 — STOP_NO_RETRY

После exact approval опубликованы077e16f/7275732 в разрешённый ref origin:
EXPECTED_OLD a238dec совпал; remote SHA после push —
72757328f34ee0933785d2be8dcf322c9ccc2d7d, NO_FORCE/NO_TAGS.
Затем выполнена ровно одна SSH-попытка010; shell command завершилась за7.064s
в пределах transport60s (это не измерение только remote работы).
[Нормализованная запись](phase16-bot-integration-readback-execution-010-2026-09-23.json)
связана с exclusive execution-010 и хешами:

- claim.json SHA256: be16d7ba579e950c32c98ae0b8dd4c92e6ab00147dc8e8b13af50e0a9741484d.
- result.json SHA256: 673e3f2a611e263c4b76446cd72685b6d7097b9a984d354934e3117fcab41ee7.

Transport полный: exit3, stdin71644/71644, stdout15726, stderr0, pipe failures0.
Remote receipt прошёл validator: **STOP_NO_RETRY / database_schema_expression_index**.
Завершены host, units_before, source, dependencies, database_files_before.
DB schema stage достигнут; полный database result, holders и units_after
отсутствуют. Это новый наблюдаемый STOP, причину009 ретроспективно не объявлять.
Approval010 использован; повтор и дополнительный SSH не выполнялись.

Новые подтверждённые факты:

- Карта102 source files (size/SHA256) равна009; прежняя сверка с55dc243 применима
  и к этому снимку. Против candidate6e68235 missing24/different24/extra0;
  exact deployed release/runtime binding UNKNOWN.
- Dependency metadata: matched27, different13, missing0, extra3, pth_count1.
  Версии13 известных pins сохранены в record; неизвестные extra names и .pth
  contents не раскрываются. Pydantic/yarl входят в matched. Это static metadata,
  не loaded module binding и не пригодность старого site-packages для candidate.
  Отдельный production runtime40 venv по-прежнему необходим.
- DB file перед open присутствовал,258048bytes; wal/shm/journal в этом снимке
  отсутствовали. Это не доказательство journal_mode или отсутствия writers.
- Bot/web snapshot active/running, expected entrypoint/cwd/cgroup, hooks false,
  по одному unit file; TimeoutStopUSec=1min 30s, KillMode=control-group.
  Это конфигурация, не успешный drain/stop или итоговая stability.
- Validated flags: service actions0, database_write_attempted=false,
  application_imported=false, runtime_activation=false. До причины
  schema_expression_index код доходит после guarded open и metadata queries;
  child вернул штатный STOP, полный schema receipt не сформирован.

Локальный разбор без нового запуска: core.read_schema отклоняет PRAGMA
index_info, если имя индексного поля не входит в разрешённые columns.
Выражение возвращает не обычное имя столбца; точные term/type/name отказавшего
live-индекса не сохранены. В source55dc243 есть idx_users_operator_label_unique
ON users(lower(trim(operator_label))). Это конкретная гипотеза из совпавшего
Python source, а не подтверждённая идентификация live-индекса. Штатный synthetic
test ранее намеренно проверял STOP на expression index; поддержка полного
старого schema fixture collector'ом не была доказана. Live индекс/DB не менять
ради прохождения readback.

Следующий локальный шаг — проверить покрытие collector на полном старом schema
fixture и candidate schema, затем подготовить представление необычных index
terms как неполной metadata без SQL/rows и ложной semantic compatibility.
Изменение schema reader/validator выходит за выполненный METADATA/error fix;
его сначала согласовать. Новый011 не подготовлен и не разрешён. Повтор worker/
Linux suites или package build для разбора этого STOP не нужен.
Task3B/recovery и acceptance открыты; AWG2/package016 сохранены,
general issuance disabled, stage/install/activation0.


<a id="schema-coverage-diagnosis-2026-09-23"></a>

## Полные synthetic schemas: диагностика покрытия — 2026-09-23

Разрешённый локальный probe завершён, **DIAGNOSIS_COMPLETE_NOT_A_FIX**.
[Нормализованное evidence](phase16-schema-coverage-diagnosis-2026-09-23.json)
содержит exact source/core/manifest hashes и hashes двух внешних throwaway
probe scripts/results. AMN3 base75df5ca; AMN2 source6e68235 чистый.
Сохранённые ранее synthetic DB уже мигрированы, поэтому они не использованы
как доказательство старой схемы. Созданы три новые in-memory схемы из exact
Git blobs: initializer55dc243, initializer6e68235 и55dc243→6e68235.
Импортированы только sqlite3 и три hash-verified schema modules через пустые
package initializers; main/Repository, application startup, dependencies и
live DB не открывались. Temporary modules удалены, memory DB закрыты.

| Полный fixture | Таблицы / columns / indexes / FK | Штатный v2 collector | Пробелы покрытия |
| --- | --- | --- | --- |
| old55dc243 | 18 / 191 / 35 / 26 | schema_expression_index | Один expression index |
| candidate6e68235 | 29 / 338 / 55 / 41 | schema_unknown | Тот же index, четыре triggers, три columns |
| old→candidate | 29 / 338 / 55 / 41 | schema_unknown | Те же элементы |

Во всех трёх fixtures известный users.idx_users_operator_label_unique имеет
unique1/partial1, index_info term sequence0/cid=-2/name=null. Это точная
идентификация synthetic индекса, **не доказательство имени live отказа010**.
Четыре literal triggers из candidate app/db/phase15_bootstrap.py:
trg_phase15_callback_owner_passport_insert/update принадлежат
telegram_callback_handles; trg_phase15_confirmation_owner_passport_insert/update —
protocol_issuance_confirmations. Reader сейчас принимает только table/index.
Три columns из constant ALTER TABLE ADD COLUMN в app/db/phase14_dual_protocol.py:
admin_config_issuance_receipts.client_build,
client_compatibility_evidence.client_build и client_compatibility_evidence.release_kind.
Static manifest builder извлекает CREATE TABLE/INDEX и _ensure_column, но
не эти ALTER/TRIGGER конструкции; валидатор поддерживает только обычные
column names в index columns. Нужны согласованные изменения всех трёх частей.

Контроль причинности, только на дополнительных одноразовых memory clones:
удаление expression index позволяет old пройти reader и полный v2 validator
(SHAPE_ONLY/compatibility UNKNOWN, synthetic receipt32438bytes). На candidate
одного удаления индекса недостаточно. После удаления ещё четырёх известных
triggers и добавления трёх columns только в копию manifest в памяти оба
candidate controls проходят весь путь, receipt42383bytes <65536. Это
исследовательские контроли, **не remedy через DROP, не schema acceptance**.
Размер будущего исправленного receipt ещё проверить. Иных препятствий в
оставшейся metadata этих fixtures не выявлено; live drift по-прежнему UNKNOWN.

Исходные memory fixtures и clones после исходной read-попытки побайтно
неизменны. Начальная ошибка измерительного harness: serialize запрещён
оставленным collector authorizer; исправлен только probe — authorizer снимается
после collector на memory clone ради byte comparison. Production guard не
менялся. Завершённые runs0.312s и0.297s, каждый с probe cap90s/git10s/schema2s;
Python3.12.14/SQLite3.53.1 Windows. Это не повтор Linux mount guard проверки.
Self-review provenance/receipt выполнен; независимого review не было.

### Предлагаемое одно ограниченное исправление — ожидает согласования

Цель: получить полную metadata известных старой/новой схем без SQL/rows и
без ослабления DB guard. Сохранить использованные v1/v2 collectors/manifests
и receipts; подготовить новую связанную версию локальных инструментов.

1. Static manifest: извлекать только literal ALTER TABLE ADD COLUMN и
   literal CREATE TRIGGER name→owning table из exact source, включая adjacent
   string constants AST. Не выполнять source, не разрешать dynamic/f-string
   SQL и произвольные идентификаторы. Сохранить source/runtime hash bindings.
2. Index metadata: вместо потери term фиксировать sequence и строгий kind:
   COLUMN с наблюдаемым неотрицательным cid и allowlisted name, EXPRESSION
   только cid=-2/name=null, ROWID только cid=-1/name=null. Проверять соответствие
   COLUMN наблюдаемой table metadata, порядок/отсутствие повторов sequence;
   сохранять unique/partial. Не читать SQL, expression text или partial predicate;
   наличие выражения не доказывает его семантику.
3. Trigger metadata: передавать только известные name/table и presence;
   тела не читать и не выполнять. Неизвестное имя, вид объекта или неверная
   name→table привязка дают fixed STOP без вывода неизвестного содержимого.
4. Reader, validator, schema version и manifest/payload bindings изменить
   вместе; несовместимые старые receipts/approvals отвергать. Итог остаётся
   SHAPE_ONLY и compatibility UNKNOWN, неизвестные schema differences — STOP.
   SQLite namespace/mount/query_only/authorizer, no-rows policy, caps/timeouts,
   systemd/source/dependency/holder scope сохранить. При необходимости менять
   физический guard остановить этот scope и отдельно пересмотреть дизайн.
5. RED/GREEN на всех трёх **полных неизменённых** fixtures, затем один целевой
   integration-readback suite. Позитивные/негативные проверки terms, forged
   trigger mapping/unknown identifiers, column AST parsing, отсутствие raw
   SQL/rows, exact fields, receipts ≤64KiB, неизменность DB и отказ прежних
   approvals. Fixture provenance привязать к exact blobs; не заменять старую
   схему ранее мигрированной DB. Offline payload/preview SSH0. Не повторять
   worker/lifecycle/dependency/Linux suites на неизменённых компонентах.

Оценка после согласования:30–45мин на fix, локальные регрессии и фиксацию;
это не срок завершения всей Phase16. Если полные fixtures выявят другой класс
дефекта, сначала уточнить результат локально, не превращать его в новый SSH.
Дизайн относится к существующему readback, не добавляет новый execution plan.
SSH011 не подготовлен и не разрешён; использованный010 не повторять. Push
следующего кода требует exact approval; документационный commit можно отправить
вместе с исправлением. AWG2_UNTOUCHED, package016 immutable, issuance disabled,
service actions/DB live open/stage/install/activation0; candidate ZIP не менялся.


<a id="schema-reader-v3-ready-2026-09-23"></a>

## Schema reader v3 — согласованное исправление готово локально

Оператор согласовал единый bounded fix после диагностики. Созданы отдельные
[manifest builder](../../scripts/phase16_bot_integration_manifest_v3.py),
[core](../../scripts/vps/phase16_bot_integration_readback_v3.py),
[validator](../../scripts/phase16_bot_integration_validator_v3.py),
[supervisor](../../scripts/vps/phase16_bot_integration_readback_remote_v3.py) и
[gate runner](../../scripts/phase16_bot_integration_readback_gate_v3.py).
Использованные v1/v2 scripts/manifests/receipts сохранены побайтно для прежних
hash bindings. Новый validator переиспользует неизменные проверки остальных
блоков без monkeypatch globals.

Static AST extraction учитывает literal ALTER ADD COLUMN и TRIGGER name→table,
исключает f-strings, concatenation/format и calls, вычисляющие SQL. Новый
[source manifest](phase16-bot-integration-manifest-v3-6e68235.json) сохраняет126
source files/runtime40 и прежние bindings вне schema allowlist. Allowlist31
исторических/rebuild имён не означает31 actual таблицу. Добавлены три columns
и четыре triggers. Schema wire v2 передаёт column cid, index terms
sequence/cid/kind/name (COLUMN/EXPRESSION/ROWID), trigger name/table.
Проверяются владельцы, sentinels, порядок, уникальность identifiers, caps и
точные поля; unknown → fixed STOP. SQL bodies/defaults/predicates/rows не
выводятся; SHAPE_ONLY/compatibility UNKNOWN сохранены. Manifest и outer receipt
тоже versioned; прежний payload/receipt/approval отвергаются.

[Verification](phase16-bot-integration-readback-v3-local-verification-2026-09-23.json):
первые5 RED → GREEN; дополнительные RED для dynamic SQL extraction и stale
child-bootstrap hashes исправлены. Промежуточные binding setup failures/errors
отделены от финального результата. Итоговый целевой suite: **125 PASS,
0 FAIL/ERROR/SKIP за4.338s** — прежние108 и17 новых регрессий.
[Тесты](../../tests/test_phase16_bot_integration_readback_v3.py) используют
[полные exact-source fixtures](../../tests/fixtures/phase16_schema/README.md),
без удаления объектов или подмены allowlist:

| Fixture | Tables / columns / indexes / triggers | Полный synthetic receipt | DB неизменна |
| --- | --- | --- | --- |
| old55dc243 | 18 / 191 / 35 / 0 | 35653bytes | Да |
| candidate6e68235 | 29 / 338 / 55 / 4 | 48125bytes | Да |
| old→candidate | 29 / 338 / 55 / 4 | 48125bytes | Да |

Проверены bound core/payload, mixed terms, malformed cid/sequence/sentinels,
unknown/wrong-owner triggers, лишние поля/SQL, запрет rows/SQL/writes,
byte invariance, caps/deadline, прежние approvals и exclusive evidence directory.
PASS/STOP/malformed receipts проверены через локальный transport fixture без
сети. Реальный CHILD_BOOTSTRAP с forced non-Linux platform принимает новый
payload до штатного platform guard, отвергает старый/повреждённый раньше;
DB/namespace access запрещены тестом. Это binding test, не Linux mount test.

Self-review выявил stale literal sizes/hashes в child bootstrap; исправлено
через RED/GREEN. AST comparison: в core изменён только collect_schema;
authorizer/query/deadline и physical namespace/mount/open сохранены. Remote
lifecycle не менялся; child отличается только sizes/hashes/magic.
Независимого review не было. Worker/Linux/dependency acceptance suites и
packages не повторялись/не пересобирались.

### Offline gate011 — ещё не разрешён и не исполнен

[Manifest011](phase16-bot-integration-readback-gate-011-manifest-2026-09-23.json)
связывает builder, validator, runner/core/supervisor, source manifest, transport
и frozen base manifest. Preview PASS/SSH0, execution-011 отсутствует;
stdin frame73178bytes. SHA256 LF:

- Gate:a5e87bf8771421afa532cd3c48d01d29dc00e90b5cd3f3f9aa0358088411283b.
- Remote:950d3856956c37e642a9a6c1693331b144a889fc179568028b5b0cc248f91abc.
- Source manifest:faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4.
- Payload:c876d261b3e1e5c01ae05f93fdd5ad0934cf7597cf2b06f6108d3af858d76739.

Marker: `PHASE16_ACTUAL_INTEGRATION_READBACK_20260923_011`.
Следующий отдельный live scope — одна read-only попытка011, transport60s /
remote50s (work44/cleanup4/finalization2), DB transaction2s/child5s,
stdout64KiB/stderr8KiB; no retry. Source/dependencies/units/DB metadata/holders
по прежним roots; без rows/env/argv/logs/app startup/service actions.
COMPLETE → offline оценка actual schema и integration/recovery условий;
STOP → разбор сохранённого результата, не автоматический012. Local PASS не
доказывает actual schema, semantic compatibility или writer completeness,
не разрешает switch. Использованный010 не повторять.

Push требует exact SHA/ref/EXPECTED_OLD, SSH011 — отдельного exact approval.
До обоих согласований только local state. AWG2_UNTOUCHED, package016 immutable,
general issuance disabled, live DB open/service actions/stage/install/activation0.


<a id="actual-readback-execution-011-complete-2026-09-23"></a>

## Actual readback011 — COMPLETE_WITH_LIMITATIONS

По последующему прямому разрешению оператора
`PHASE16_ACTUAL_INTEGRATION_READBACK_20260923_011` выполнена ровно одна
read-only SSH-попытка из чистого local commit f33a5b46ccd799397be6f017e72c8fadb210e596.
Пользователь разрешил именно SSH; push отдельно не разрешён и не выполнялся.
Это уточняет прежнюю очередь push→SSH: execution привязан к проверенному
локальному commit/hashes, публикация остаётся отдельным действием.

[Execution record](phase16-bot-integration-readback-execution-011-2026-09-23.json)
сохраняет полную разрешённую DB metadata, unit snapshots, holders, зависимости,
нормализованное сравнение и hashes внешних artifacts. Gate/remote/source/payload
совпали с011 manifest; preview PASS, exclusive execution-011 был отсутствующим.
Command wall time10.609s, SSH exit0, stdin73178/73178, stdout34337bytes,
stderr0, pipe failures0. Локальные pretty-printed runner stdout83960bytes
не являются remote transport stdout и не сравниваются с его cap64KiB.
Remote receipt validated: **READBACK_COMPLETE_WITH_LIMITATIONS**, completed
2026-09-23T19:19:47.989687+00:00. Approval011 использован; retry0,012 не подготовлен.

- Claim SHA256:7db560779e6f53f80cfaf0d05440fc65f82662a4da05862093837b0dde5ac912.
- Result SHA256:904bf0a99140d7238b8333d2aa4b0716f183ff2c46ef136a32612529d5598459.
- DB:18 таблиц,191 column,35 indexes,26 FK,0 triggers; journal_mode=delete,
  schema_version64/user_version0, SQLite3.45.1. DB258048bytes; identity/size
  стабильны между снимками, wal/shm/journal отсутствуют. Это не whole-DB hash
  и не утверждение отсутствия записей других процессов во время окна.
- Полная собранная metadata совпадает с exact synthetic old55dc243. Включает
  users.idx_users_operator_label_unique: expression term cid=-2/name=null,
  unique1/partial1. SQL expression/predicate не читались; точный отказавший
  индекс исторического010 ретроспективно не идентифицируется доказанно.
- Против candidate6e68235 отсутствуют11 новых таблиц и4 triggers; различаются
  admin_config_issuance_receipts (columns/indexes), device_passports
  (columns/indexes), devices (columns). Лишних таблиц нет. Объекты не удалялись
  и candidate initializer на production DB не запускался.
- Source map и dependency metadata равны010:102 Python files совпадают с55dc243;
  runtime pins27 matched/13 different/missing0/extra3/pth1. Это static identity,
  не effective loaded runtime; нужен отдельный candidate runtime40 venv.
- Holders: OBSERVED_ONLY, coverage_complete=true,109 PID/873 FD, denied0/churn0;
  один наблюдаемый holder — bot PID1106946/start_ticks446930267, database FD.
  Это подтверждает открытие scoped DB bot-процессом в снимке. Web/CLI/agent
  могут открывать её позже; writer_completeness остаётся UNKNOWN.
- Bot/web active/running до и после, PID/start_ticks стабильны; bot Type=notify,
  Restart=no, start40s/stop90s; web Type=simple, Restart=on-failure,
  start90s/stop90s. KillMode=control-group, signals15/9, hooks false.
  Это не фактическая проверка stop/drain и не разрешение менять units.

Сверка old/candidate выполнена offline на hash-verified schema modules в новых
in-memory DB; пользовательские rows не читались. Учитывались все полученные
column/index/FK/trigger fields, независимо от порядка перечисления; не
сравнивались SQLite/schema/user versions и journal_mode synthetic DB.
Отсутствующие SQL/default/CHECK/collation/row semantics не объявляются равными.
Прежние synthetic migration/old-repository и125 tests не повторялись.

Диагностический сбор integration readback закрыт в согласованном scope.
Следующий локальный этап — [startup/fence/backup/recovery readiness](phase16-bot-candidate-runbook-2026-09-21.ru.md#switch-readiness-2026-09-23)
по фактически наблюдаемой old metadata, без очередного collector gate.
Сохранить отдельный runtime40, старый revert target, bot identity/token и shared
DB; согласовать startup seed/server-sync policy и writer fence. Один открытый
bot FD не позволяет остановить только bot и считать миграцию безопасной.
Если нужен stop web/ограничение API/CLI, это отдельное изменение live scope.
Task3B/recovery, Windows, quality/A-B и acceptance остаются открыты.
AWG2_UNTOUCHED, package016 immutable, issuance disabled; validated service
actions0/database_write_attempted=false/application_imported=false/activation=false.
Stage/install/push0. Документационный результат фиксируется локально.
