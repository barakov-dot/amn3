# Phase16: один изолированный Linux-прогон bot candidate

Статус: **APPROVAL_CONSUMED / ONE_SSH_ATTEMPT / UNKNOWN_NO_RETRY**.
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

## Следующий точный scope — read-only recovery, пока НЕ согласован

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
