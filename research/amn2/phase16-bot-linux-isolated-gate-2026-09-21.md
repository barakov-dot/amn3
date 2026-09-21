# Phase16: один изолированный Linux-прогон bot candidate

Статус: **READONLY_FRAME_PROBE_PASS / NEW_ISOLATED_TEST_APPROVAL_PENDING / LINUX_RESULT_UNKNOWN**.
[Результат единственной попытки](#execution-2026-09-21); повтор запрещён.
Это конкретный approval contract под Task3B [единственного плана](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md),
не новый план deployment. После локальной подготовки оператор ответил
«разрешаю» на этот exact gate. Разрешение использовано одной попыткой
21.09.2026; remote результат не получен. Ниже сохранён согласованный scope.

## Предмет использованного разрешения

Ровно один SSH на Spain через существующий fixed-role trust loader, передачу
заранее проверенных bytes и создание отдельной тестовой среды. В ней — один
отрицательный контроль и шесть штатных signal cases. Это не запуск рабочего
бота: нет polling, service actions, shared DB, runtime.env/token чтения или
активации нового кода. General issuance остаётся disabled.

Bindings первой выполненной попытки (история); текущий local runner hash —
в [локальной доработке ниже](#transport-diagnostics-2026-09-21).

| Binding | Значение |
| --- | --- |
| Gate ID | PHASE16_ISOLATED_LINUX_TEST_6e68235_001 |
| Source | 6e682356ed14a62d636ee58039fd3a389e794809 |
| Bundle | phase16-bot-candidate-20260921-6e68235-001.zip; 30485208 bytes |
| Bundle SHA256 | e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7 |
| Manifest SHA256 | 6792cb2cd28b0ce70ae031cac04b29f40db908f5e8bad0770e689de390a9a37d |
| Remote script SHA256 (UTF-8/LF) | 5df6b2fc76d616f5a0b1c64b6168868a19c9894f71a3cde11b19ce5e119ed102 |
| Local runner SHA256 (UTF-8/LF) | 7098b4e05335a0896b937058301bf7392bd036e0f3f8cf05b84e2c08fb250bcc |
| Target | /opt/amn2-spain/bot-candidates/phase16-bot-candidate-20260921-6e68235-001 |

Исходники исполнителя: [local](../../scripts/phase16_bot_linux_gate.py),
[remote](../../scripts/vps/phase16_bot_linux_gate_remote.py),
[тесты](../../tests/test_phase16_bot_linux_gate.py).
[Immutable candidate manifest](phase16-bot-candidate-manifest-2026-09-21.json)
и [его runbook](phase16-bot-candidate-runbook-2026-09-21.ru.md) остаются прежними;
этот contract закрывает указанное там отсутствие готового runner.

## Точные действия и ограничения

1. Локально проверить bundle size/SHA, manifest и все payload/tar entries.
   Default CLI только OFFLINE_READY_NOT_EXECUTED: без trust read, SSH и claims.
   Для execution нужны exact approval ID и approved remote SHA.
2. Использовать существующий trust/spain loader с ACL/nofollow/host pin validation,
   OpenSSH BatchMode/IdentitiesOnly/StrictHostKeyChecking, -F none, один ConnectAttempt.
   Не менять keys/known_hosts, не выводить адрес/user/key material.
   Локальный exclusive claim сохраняется до единственного SSH; повтор с тем же
   evidence-dir останавливается. Транспорт не повторяется при UNKNOWN.
3. Передать через stdin 8-byte length + <=64KiB remote script + exact ZIP.
   Bootstrap проверяет SHA script перед исполнением. Remote проверяет bytes
   пакета до записи. Нет scp/SFTP-второго соединения, скачиваний или curl/pip сети.
4. Проверить Linux x86_64, CPython3.12, glibc2.39, existing venv/ensurepip,
   /usr/bin/unshare --net capability, безопасные parents и >=512MiB свободно.
   Если prerequisites отсутствуют — STOP, без apt, внешнего bootstrap или sudo.
   Наличие venv/ensurepip/unshare на Spain пока UNKNOWN; предыдущий snapshot
   этого не проверял. Local Windows PASS не доказывает эти prerequisites.
5. Создать только новый target и, если отсутствует, его parent bot-candidates.
   Уже существующий target/symlink блокирует запись. Сохранить claim.json,
   payload/source, отдельные test-venv, negative-source и scratch/results.
   Никаких правок /opt/amn2-spain/runtime/source, runtime/site-packages,
   /etc/amn2-spain, systemd units и /var/lib/amn2-spain.
6. Все venv/pip/test subprocesses — в новой network namespace через unshare --net
   с чистым environment, без inherited token/PYTHONPATH/DB-path. Это не меняет
   host networking и не требует установки WSL/Docker на АРМ.
   Offline --no-index/--require-hashes/--only-binary, test lock48 (runtime40+extra8).
   Проверить pip check, metadata48pins, origin внутри изолированной venv;
   bootstrap pip/setuptools допускаются отдельно и не считаются runtime pins.
7. Negative control: только копия tests/bot/lifecycle_signal_child.py обнуляет
   pending в Controller.attach перед вызовом родителя. Один синтетический
   PRE_LOOP/SIGTERM должен завершиться pytest exit1, exactly one failure с
   Invalid synthetic trace order. Произвольная ошибка не принимается за RED.
   Штатный source не меняется; negative copy сохраняется отдельно.
8. Перепроверить штатный source, затем tests/bot/test_lifecycle_signals.py:
   exactly6 PASS/0SKIP/0FAIL; все сигналы только собственным disposable Popen.
   Negative/green имеют SQLite/fake bot/notifier/lock из bound helper, не
   вызывают main() приложения и не открывают живую DB. Source hashes после
   GREEN должны совпасть; JUnit и нормализованный result сохраняются.

Лимиты: bundle64MiB, script64KiB, each archive unpack128MiB (это не квота venv),
output256KiB/command, local SSH result64KiB. Remote work watchdog290s с резервом
cleanup в общем300s бюджете; transport330s. Venv45s, install100s, pip check15s,
metadata15s, negative25s и green95s (tests суммарно<=120s), child10s.
Остаток общего бюджета ограничивает каждый следующий процесс.
Кап/ошибка останавливает owned process group; external PID/unit не выбираются.
POSIX group termination и network namespace ещё не выполнены на Linux;
timeout/transport loss означает UNKNOWN, не доказанную quiescence.

## Результат и возврат

PASS только ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED: exact hashes/pins,
ожидаемый negative и6green, source readback, service_actions=0,
live_database_opened=false, telegram_polling=false, runtime_activation=false.
STOP сохраняет папки/claims/results; cleanup и повтор не автоматизированы.
Нет переключения службы, поэтому production rollback в этом gate не нужен.
Если транспорт потерян, не считать remote процессы завершёнными и не
переисполнять: отдельное recovery/readback разрешение. Удаление test directory
не входит в scope, даже после PASS.

## Историческая команда единственной попытки — НЕ ПОВТОРЯТЬ

Перед этой попыткой сверены code hashes с таблицей, clean Git state,
bundle SHA и отсутствие локального execution claim. Теперь claim существует;
команда ниже — receipt, не новый GO. Не менять evidence-dir ради повтора.
Рабочий каталог: C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB.

~~~powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -B scripts/phase16_bot_linux_gate.py `
  --bundle 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-release-preparation-20260921-6e68235/phase16-bot-candidate-20260921-6e68235-001.zip' `
  --execute --approve PHASE16_ISOLATED_LINUX_TEST_6e68235_001 `
  --approved-remote-sha256 5df6b2fc76d616f5a0b1c64b6168868a19c9894f71a3cde11b19ce5e119ed102 `
  --evidence-dir 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-linux-runner-20260921/execution'
~~~

Команда исполнена один раз по явному «разрешаю» оператора; approval consumed.
Новый readback/recovery или retry этим не разрешён. Production deployment,
миграция shared DB и Telegram smoke также не разрешены.

## Выполненная локальная проверка

RED (отсутствующий remote module) →23PASS; RED (local runner отсутствует) →30PASS.
Self-review нашёл Windows backslashes в remote path receipt: отдельный RED
воспроизвёл ошибку; исправлено as_posix. Итог **32PASS/0SKIP/0FAIL, 0.50s**.
Покрыты archive traversal/links/duplicate/size, bad hash before writes,
exclusive directory/claim, clean environment, specific negative failure,
JUnit count mismatch/skips, real local child timeout/output cap, stdin framing
и запрет исполнения изменённого remote payload, no retry after transport error.
Linux signals/negative control, unshare, Linux venv install и POSIX killpg NOT_RUN.

Первый pytest harness попал в parent ACL при autodiscovery; исправлены
rootdir/confcutdir. Один RED использовал default pytest temp и дал atexit ACL
ошибку; итоговый прогон использовал новый explicit basetemp, shared temp не
исправлялся и вручную не очищался. Это ошибки harness, не дефекты AMN2.
Self-review inline, без subagent. Прежние101schema,94/6lifecycle и312worker
не повторялись; AMN2 source6e68235, оба locks и immutable bundle неизменны.
[Нормализованное local evidence](phase16-bot-linux-runner-local-validation-2026-09-21.json).

<a id="execution-2026-09-21"></a>

## Единственная согласованная попытка — UNKNOWN, 2026-09-21

AMN3 baf1bebe6f3902a20d15a0765d45e573d7898385, AMN2 source6e68235;
оба checkout чистые перед действием, local/remote LF hashes и bundle совпали.
Оператор ответил «разрешаю» после предложения именно одного isolated test gate.
Claim создан 2026-09-21T18:50:23.493117+00:00 (21:50:23 МСК), attempts=1.
[Нормализованный локальный результат](phase16-bot-linux-execution-2026-09-21.json):
**UNKNOWN_NO_RETRY / process_io / ssh_attempts=1**. Remote receipt не получен.
Это факт запуска SSH-процесса, не доказательство установленной SSH-сессии,
полной передачи ZIP, создания target, установки test-venv или запуска тестов.
Negative/6signals/unshare/Linux install теперь UNKNOWN, не PASS и не доказанный
NOT_RUN. Нет оснований утверждать quiescence или свежую health bot/web.
Production service/DB/poller actions в утверждённом коде отсутствуют;
повтор, cleanup и дополнительные SSH после ошибки не выполнялись.

Локально без сети воспроизведена потеря диагностики: disposable Python child
вывел SYNTHETIC_EARLY_EXIT и завершился с17, не читая1MiB stdin; неизменный
run_process вернул только process_io. Он объединяет pipe errors, а при них
не возвращает захваченный output и returncode. Это подтверждает ограничение
наблюдаемости, но НЕ причину реального SSH-сбоя. Код исполнителя не исправлялся;
первичные claim/result сохранены в локальном execution каталоге из команды.
Старые32guard/101schema/94+6lifecycle/312worker не повторялись.

<a id="recovery-readback-scope"></a>

## Read-only recovery scope — согласован и выполнен один раз

Один SSH через прежний fixed-role Spain trust, без ZIP upload, установки,
повторного запуска gate/тестов, сигналов, удаления или service actions.
Только nofollow metadata фиксированного target из binding выше и его двух
regular files claim.json/result.json (каждый <=64KiB). Никакого recursive scan,
чтения source/venv, .env/token, shared DB, journal, argv или поиска других hosts.
Вывести нормализованные schema/status/reason/step returncodes/counts/hashes,
проверить artifact/source/bundle/scope bindings. Не публиковать raw content
невалидного файла. Не следовать symlink; отсутствие/размер/type/binding mismatch
означает STOP. Бюджет одного соединения60s, output64KiB, без retry и remote writes.

Если result содержит PASS, принять его только после полной проверки прежнего
receipt contract; если STOP — зафиксировать точный reason, не устранять его на
сервере автоматически. Если target/result отсутствует или transport вновь
не даёт результата — сохранить UNKNOWN. Readback двух файлов не доказывает
отсутствие оставшихся процессов; никакого kill/cleanup или нового тестового
прогона из такого вывода. Это ограничение относится и к историческому watchdog.

Основание отдельного согласования — уже утверждённый раздел «Результат и возврат»:
«Если транспорт потерян ... отдельное recovery/readback разрешение».
Этот scope не расширяет разрешение на production activation или shared DB.

<a id="recovery-readback-result-2026-09-21"></a>

## Read-only recovery выполнен — parent отсутствует, 2026-09-21

Оператор ответил «продолжай» на точный запрос одного read-only подключения для
claim.json/result.json. По этому scope выполнен ровно один SSH, без test retry.
[Нормализованный результат и локальные проверки](phase16-bot-linux-readback-2026-09-21.json).
AMN3 base5b1383c, probe SHA256
b794dc3728358a00b2400236b3d5c1eb111ca03820bcf3bc972798534d91d924.
Claim18:58:44.714414Z, завершение18:58:47.219509Z (21:58:47 МСК).
Read-only transport ответил: **PATH_ABSENT_UNKNOWN**, missing_component=
**bot-candidates**. Nofollow traversal прошёл /opt и /opt/amn2-spain, затем
родитель тестового target отсутствовал. Target/venv/claim/result отсутствуют
на момент этого чтения; содержимое результатов не прочитано. Это не доказывает
причину первой ошибки, историю remote execution или отсутствие процессов.
Process scan не выполнялся; quiescence и Linux signal evidence остаются UNKNOWN.
Remote writes=false, service_actions=0; нет DB/.env/token/journal/argv чтения.

Использован прежний fixed-role trust и run_bounded_process с успешно применявшимся
read-only stdin протоколом /usr/bin/python3 -I -B -, без framed ZIP/bootstrap.
Collector stdlib-only: только read-only nofollow directory/file descriptors,
regular-file/owner/mode/64KiB limits, allowlisted normalized receipt fields.
Локально9 checks PASS: valid PASS, bad bindings/actions/counts/steps, STOP,
missing path и nonregular file. Эти mock checks не доказывают Linux nofollow
file-open path: до файлов remote не дошёл. Скрипты и claims/results сохранены
в C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-linux-runner-20260921;
LF hashes обоих скриптов записаны в JSON выше. Read-only approval использован.

Дополнительно один полностью локальный frame roundtrip: unchanged remote script
и exact30485208-byte ZIP через исходный run_process в Windows Python, после
POSIX shlex разбора command. Получен ожидаемый exit3/platform_python, без
process_io и без writes. Это проверка framing/pipe на локальном пути, не SSH
command transmission, Linux prerequisites или реальная причина первого сбоя.
Source/runner/bundle не исправлялись, старые baseline suites не повторялись.

**Следующий шаг:** локальная доработка наблюдаемости transport: сохранять отдельно
exit code, стадию pipe failure, размеры/hash и безопасную классификацию ошибки;
без raw SSH stderr/секретов, ослабления caps/trust/no-retry. Сначала synthetic
early-exit RED и bounded transport GREEN; затем новый exact gate только по
отдельному разрешению. Это предложение code fix, ещё не выполненное и не
разрешение второго upload/test. К повторному SSH сейчас не переходить.

<a id="transport-diagnostics-2026-09-21"></a>

## Локальная диагностика транспорта исправлена — 2026-09-21

По «продолжай» после предложения локально улучшить SSH diagnostics выполнен
ограниченный local code fix. AMN3 basef093300; AMN2 source6e68235 не менялся.
Причина потери информации доказана прежним synthetic early-exit: общий remote
run_process выбрасывал process_io без output/exit code. Серверный скрипт оставлен
byte-identical; только [локальный runner](../../scripts/phase16_bot_linux_gate.py)
теперь использует собственный run_transport и сохраняет transport metadata в
result.json даже при pipe failure/невалидном JSON. Это не исправление доказанной
причины первого SSH-сбоя: она всё ещё UNKNOWN.

stdin пишется порциями32KiB; bytes_accepted означает приём локальным pipe,
не receipt на сервере. stdout и stderr разделены, их общий retained cap64KiB;
при превышении — STOP, prefix hashes явно обозначают только сохранённую часть.
В evidence идут exit code, failure_stage, pipe_failures, input completion,
observed/retained byte counts, prefix SHA и только фиксированные stderr hints
(auth/host key/Python syntax/timeout/unclassified). Raw stderr, command, keys,
адрес и exception message не сохраняются. Hints не являются root-cause verdict.
Лимиты payload64MiB+frame, timeout330s и ограниченный cleanup сохранены;
local cleanup может добавить до3s wait и до3x1s thread joins к process timeout.
Незакрытый pipe остаётся UNKNOWN, remote quiescence не утверждается.
Fixed trust/SSH options, offline default, exclusive claims и no-retry прежние.

[Тесты](../../tests/test_phase16_bot_transport.py),
[нормализованное evidence](phase16-bot-transport-diagnostics-2026-09-21.json):
7 ожидаемых RED (нет local transport/evidence) →42PASS; после дополнительного
integration case valid STOP + stderr + chunked stdin итог **43PASS/0FAIL/0SKIP,
1.01s** (11 новых +32 прежних gate tests). Реальные disposable local children
покрыли ранний exit17/незаписанный stdin, stdout/stderr separation, cap/timeout,
start failure, safe classification, persisted diagnostics и запрет retry.
Self-review inline; никаких subagents. AMN2 baseline101/94+6/312 не повторялись.
POSIX killpg/inherited-open-pipe branch не подтверждены Windows тестами.
Оба offline previews PASS; probe framing roundtrip на local Python PASS.
Первый ad-hoc probe check ошибочно ожидал30 bytes вместо32; исправлен только
harness expectation. Production probe использует len(SENTINEL) и не менялся
из-за этой ошибки; никакого server execution не было.

Current local runner SHA256 (UTF-8/LF):
420ebe44ff9ba3fce4485d4466f17f6dcdd910e25899798396f1da59a1b3e363.
Remote runner SHA5df6b2fc… и bundle SHAe19abc5c… прежние, exact offline binding PASS.
В этом slice SSH=0; прежние claims/results сохранены, test approval consumed.
AWG2/package016/general issuance safety прежние; deployment не выполнялся.

<a id="readonly-transport-probe-approval"></a>

## Исторический SSH transport probe v1 — approval consumed, exit255

Цель: проверить именно прежний framed-command путь через Windows OpenSSH,
который локальный Python roundtrip и успешный read-only stdin readback не доказали.
Один SSH через fixed Spain trust, stdin226 bytes: 8-byte length, stdlib-only
probe и32-byte non-secret sentinel. Нет ZIP/candidate upload. Тот же frame_request
проверяет SHA probe перед exec; probe читает только stdin (<=128 bytes) и печатает
schema/length/SHA. Ни файловых операций, ни subprocess/service/network/API calls
в remote probe; Python -I -B, remote bytecode writes выключены. Проверка не
обследует prerequisites, процессы, /opt, config/token/DB и не запускает бота.
Host trust/keys/known_hosts неизменны; timeout20s, stdout+stderr cap4KiB,
один attempt, exclusive local claim, STOP/UNKNOWN без retry/cleanup.

Локальные файлы в
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-transport-diagnostics-20260921:
readonly_transport_probe.py и будущие readonly-probe.claim.json/result.json.
До запуска сверить clean/scoped HEAD, LF hashes и отсутствие нового claim.
Probe runner дополнительно проверяет exact local runner SHA выше до trust/SSH.
Local probe script SHA256:
7690601690e283afeac518fbffdb80f7daa05a4f088c913a1534d9ea925951f4.
Remote probe SHA256:
475d31ae4babbc2c3e995328a82a7517a708194d306a08e865b7232ca435caa3.
Sentinel ожидается32 bytes, SHA256:
3bf188a05aa9316d60a03dc7500d53c7a3cb12ebd0bd310a39736353f650893d.

Историческая команда, исполненная один раз по «продолжай»; не повторять:

~~~powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -B 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-transport-diagnostics-20260921/readonly_transport_probe.py' --execute --approve PHASE16_TRANSPORT_PROBE_READONLY_001 --sha256 7690601690e283afeac518fbffdb80f7daa05a4f088c913a1534d9ea925951f4
~~~

PASS только exit0 и exact schema/32-byte SHA response; иначе сохранить normalized
transport evidence/UNKNOWN, не повторять. Даже PASS не разрешает original test
upload, install или activation; он только проверяет путь передачи короткого frame.
Команда v1 исполнена один раз; результат ниже. Это больше не готовый GO.

<a id="programdata-diagnosis-2026-09-21"></a>

## Probe v1 и подтверждённый local OpenSSH startup defect — 2026-09-21

Оператор ответил «продолжай» на точное предложение одного no-write SSH probe.
При clean AMN3 HEAD37dc1d7 сверены local/probe hashes и отсутствие claim.
Единственная попытка19:14:12.695826Z →19:14:12.712373Z (22:14:12 МСК):
exit255, stdout0/stderr0, stdin226 bytes accepted локальным pipe, pipe failures0,
UNKNOWN_NO_RETRY. [Первичный probe и local diagnosis evidence](phase16-bot-ssh-programdata-diagnosis-2026-09-21.json).
Не получен ни remote response, ни proof framed execution. Это одна попытка
SSH-процесса, не доказанная сессия. Никакого retry или дополнительного подключения.

После STOP выполнены только локальные ssh.exe -V, без target/trust/key inputs:

| Локальное окружение | exit | stderr bytes |
| --- | --- | --- |
| inherited | 0 | 43 |
| прежний allowlist | 255 | 0 |
| прежний allowlist + только PROGRAMDATA | 0 | 43 |
| inherited без PROGRAMDATA | 255 | 0 |
| исправленный ssh_environment() | 0 | 43 |

В успешных вариантах совпал SHA43-byte version output. Значения environment,
raw stderr/host/key material не записывались. Это причинный однофакторный тест:
**на данном Windows host отсутствие PROGRAMDATA ломает запуск OpenSSH**.
Та же ошибка была в local candidate runner и probe v1. Ранее успешный read-only
collector наследовал environment и не имел этого дефекта. Это объясняет
подтверждённый локальный startup failure; framed remote path, Linux environment
и результаты первой test attempt остаются непроверенными. Не утверждать
server health, quiescence или факт выполнения remote команд по stdin counter.

Минимальная локальная коррекция в прежнем transport-fix scope: общий
ssh_environment() добавляет только PROGRAMDATA к allowlist, нормализует имена,
при отсутствии переменной останавливает выполнение до trust/claim/SSH.
Application secrets/PYTHONPATH/DB variables по-прежнему исключены. Remote runner
и bundle не менялись; ни global Windows environment, ни серверные настройки
не изменялись. **2RED →45PASS/0FAIL/0SKIP,1.03s** (13transport+32gate), плюс
реальный локальный ssh -V через новый helper exit0. Baseline101/94+6/312 не
повторялись. Raw error и retry не добавлены, caps/trust/exclusive claims сохранены.

Текущий local runner LF SHA256:
8d5ce722245f11aba159d8544e7125c1c0d78b267fe41096445f186861e0d75b.
Предыдущие SHA в этом документе — bindings исторических попыток, не текущий код.
AMN2 source6e68235, remote SHA5df6b2fc… и bundle SHAe19abc5c… прежние.
AWG2_UNTOUCHED, package016 immutable, issuance disabled; server writes/install/
service/DB/Telegram/deploy/cleanup в этом slice отсутствуют.

<a id="readonly-transport-probe-v2-approval"></a>

## Исторический probe v2 после local fix — выполнен, PASS

Тот же no-write scope226-byte frame/32-byte sentinel, прежний remote probe
SHA475d31ae… и ожидаемый sentinel SHA3bf188a0…; timeout20s/output4KiB/no retry.
Отличие только local environment helper с PROGRAMDATA и отдельные v2 claim/result.
Original ZIP/test-venv/test run/бот/службы/DB не входят в scope. Старые v1 artifacts
сохранены. Новый local probe сверяет exact local runner SHA выше до trust/SSH.

Local script:
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-transport-diagnostics-20260921/readonly_transport_probe_v2.py.
Его LF SHA256: ba50b0fbadbf1e97ab630fb9e9ef43ca6fd54b4a33da2ed974ccfa19426dd322.
Сохранённые evidence: readonly-probe-v2.claim.json и readonly-probe-v2.result.json
в том же scratch. Перед попыткой сверены hashes/Git и отсутствие claim.
Историческая команда ниже исполнена один раз по «продолжай»; не повторять.

~~~powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -B 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-transport-diagnostics-20260921/readonly_transport_probe_v2.py' --execute --approve PHASE16_TRANSPORT_PROBE_READONLY_002 --sha256 ba50b0fbadbf1e97ab630fb9e9ef43ca6fd54b4a33da2ed974ccfa19426dd322
~~~

Команда исполнена один раз: exit0 и exact schema/32-byte SHA response PASS.
Approval использован. Этот PASS не разрешает загрузку candidate или Linux tests;
следующий конкретный server gate описан ниже, pending отдельного согласования.

<a id="readonly-probe-v2-pass-2026-09-21"></a>

## Контрольный framed SSH probe v2 — PASS, 2026-09-21

Оператор ответил «продолжай» на точный запрос одного no-write SSH после fix.
AMN3 HEAD5fbf181, clean; local/probe LF hashes совпали, claim до запуска отсутствовал.
Один SSH attempt19:21:56.382946Z →19:22:03.432620Z (22:22:03 МСК),
[сохранённый нормализованный receipt](phase16-bot-transport-probe-v2-2026-09-21.json).
**READONLY_FRAME_PROBE_PASS**: exit0, stdin226 bytes, stdout132, stderr0,
pipe failures0. Remote response содержит ровно schema phase16.transport-probe.v1,
bytes32 и SHA3bf188a0… как в contract. Проверены fixed-trust SSH и исполнение
короткого hash-bound frame после PROGRAMDATA fix. Этот путь больше не UNKNOWN.

Это не проверка передачи30.5MB ZIP, Linux venv/ensurepip/unshare, зависимости48pins,
negative/6signal cases, bot startup/stop budget, shared DB или health служб.
Содержимое remote probe не выполняет file writes/service actions/DB/Telegram;
установки, загрузки candidate и cleanup не было. Старые test/readback/probe claims
сохранены. Quiescence старых процессов этим probe не исследовалась.

После PASS локальный offline candidate preview подтвердил точные bundle,
manifest/payload и remote script bindings. Candidate/source/locks/package016
не менялись и не пересобирались; прежние45/101/94+6/312 tests не повторялись.
Это docs/evidence slice; checks readback/JSON/links/diff/secret/changelog.

<a id="isolated-linux-attempt2-approval"></a>

## Следующий gate: одна новая isolated Linux test attempt после fix

**PENDING_APPROVAL / NOT_EXECUTED.** Это запрос нового отдельного разрешения на
вторую test attempt; read-only probe approval уже использован. Первый test claim
и все receipts остаются immutable. Замена evidence-dir сама по себе не является
разрешением retry; выполнить следующую команду можно только после отдельного
ответа оператора именно на этот upload/test-environment scope.

Код и payload уже подготовлены и проверены, без изменений серверного скрипта:

| Binding | Значение |
| --- | --- |
| AMN2 source | 6e682356ed14a62d636ee58039fd3a389e794809 |
| Bundle size / SHA256 | 30485208 / e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7 |
| Manifest SHA256 | 6792cb2cd28b0ce70ae031cac04b29f40db908f5e8bad0770e689de390a9a37d |
| Local runner LF SHA256 | 8d5ce722245f11aba159d8544e7125c1c0d78b267fe41096445f186861e0d75b |
| Remote runner LF SHA256 | 5df6b2fc76d616f5a0b1c64b6168868a19c9894f71a3cde11b19ce5e119ed102 |
| Remote target | /opt/amn2-spain/bot-candidates/phase16-bot-candidate-20260921-6e68235-001 |
| New local evidence | C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-linux-runner-20260921/execution-v2 |

Один SSH/upload immutable ZIP. Remote сначала проверяет platform/ABI, hashes,
nofollow parents/target absence, >=512MiB free, existing venv/ensurepip и unshare.
Parent отсутствовал при readback18:58:47Z; это исторический факт, не свежая
проверка. Существующий target при новом запуске означает STOP, без overwrite.
Нет apt/sudo/bootstrap/download; отсутствие prerequisites означает STOP.
Только после проверок создаётся отдельная test-venv с offline48pins в новом
каталоге, затем один expected-negative PRE_LOOP/SIGTERM и шесть synthetic cases.
Все дочерние команды изолированы unshare --net, fake SQLite/bot/lock;
source readback и прежние exact PASS/STOP criteria обязательны.

Прежние caps: remote watchdog290s с резервом в300s; transport timeout330s плюс
bounded local cleanup; venv45s/install100s/pip-check15s/metadata15s/negative25s/
green95s, tests суммарно<=120s, own child10s, output256KiB/command и64KiB SSH.
Любой STOP/UNKNOWN/timeout — сохранить claim/result, без второго соединения,
retry или cleanup. Никаких live DB/config/token/poller/service actions, production
activation, изменения AWG2/web/package016 или общей выдачи.

CLI marker PHASE16_ISOLATED_LINUX_TEST_6e68235_001 сохранён ради неизменности
remote protocol/artifact. Он не идентификатор нового разрешения: новую attempt
отличают этот contract, явное подтверждение оператора и exclusive execution-v2
claim. При фиксации результата обязательно указать, что это вторая test attempt.

После точного нового согласования, из active AMN3 checkout, повторно сверить
hashes/Git и отсутствие execution-v2; затем ровно один запуск:

~~~powershell
& 'C:/Users/SooL/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -I -B scripts/phase16_bot_linux_gate.py --bundle 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-release-preparation-20260921-6e68235/phase16-bot-candidate-20260921-6e68235-001.zip' --execute --approve PHASE16_ISOLATED_LINUX_TEST_6e68235_001 --approved-remote-sha256 5df6b2fc76d616f5a0b1c64b6168868a19c9894f71a3cde11b19ce5e119ed102 --evidence-dir 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-linux-runner-20260921/execution-v2'
~~~

Новый evidence-dir отсутствовал при подготовке. Команда **не исполнена**;
Linux signal acceptance/shared DB compatibility/activation gates остаются открыты.
