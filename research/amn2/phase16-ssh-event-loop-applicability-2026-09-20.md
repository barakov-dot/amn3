# Phase16 — применимость Panel #174: SSH и цикл событий

Статус web slice: LOCAL_IMPLEMENTED_TESTED_REVIEWED_PUSHED_NOT_DEPLOYED.
Bot: LOCAL_IMPLEMENTED_TESTED_REVIEWED_PUSHED_NOT_DEPLOYED.
Проверка завершена 2026-09-20 20:25 Europe/Moscow. Это ограниченный разбор
одного сигнала из [реестра](../../docs/UPSTREAM_INTAKE.ru.md), не полный weekly.
Цель: определить, применима ли защита от блокирующего SSH к нашему коду.

## Источники и результат

AMN2 checkout: C:/Users/SooL/Documents/amn2-phase15-local-package-bootstrap-readiness,
HEAD 56540e2084140e3a6277d7472c88c599d7153ccf, дерево чистое до/после чтения.
Во время source review приложение, SSH и тесты не запускались; configs/keys/БД
не читались. Последующая локальная реализация и synthetic tests описаны ниже.

[Официальный Panel PR #174](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/174)
merged 14.09.2026; head 1248ce68c031a5c5d2ed0fe1a4e45ea702cedfbb,
merge cb0a5db3b568befe96792f4278baa493129011f5. В diff проверены перенос
блокирующих вызовов из async handlers, circuit breaker и его тесты. Upstream
использует pooled Paramiko, AMN2 — отдельные subprocess ssh. Копирование
upstream source/GPL-кода и полный перенос его pool/cooldown не предлагаются.

Решение: **уже учтено в плане**, уточнена существующая карточка «Параллельная
проверка статусов»; подтверждена необходимость отдельной локальной доработки.
Отличие SSH transport не отменяет применимость проблемы event loop.

## Проверенные цепочки AMN2

| Путь при указанном HEAD | Наблюдение |
| --- | --- |
| app/web/app.py:2178,2194 | async run_server_health синхронно вызывает run_server_health_check |
| app/web/server_health.py:68,88 | Синхронная функция загружает конфигурацию и вызывает run_server_checks с SystemSshClient; репозиторий/SQLite в неё не передаются |
| app/server/checks.py:149,157 → app/server/operation_runner.py:39,50 | Проверки исполняются синхронно; runner вызывает ssh.run последовательно |
| app/server/ssh.py:50,81,138 | subprocess.run блокирует вызывающий поток; default timeout 20 секунд на вызов в обоих auth-путях |
| app/bot/handlers.py:320,328 → app/bot/workflows.py:844,860 → app/services/device_revoke.py:143,169 → app/server/peer_apply.py:53,206,216 | При remote revoke async handler доходит до синхронного SSH; здесь также есть обращения к Repository |
| app/main.py:103; app/db/connection.py:10 | handle_as_tasks/concurrency limit не изолируют блокирующий вызов; SQLite connection создаётся с параметрами по умолчанию |
| app/bot/workflows.py:681 | Страница статусов бота читает local_server_summaries; это не SSH polling, его нельзя приписывать этому пути |

Вывод из source: при достижении subprocess.run цикл событий вызывающего процесса
не сможет выполнять другие coroutine до возврата вызова. Задержка на реальном
сервере сейчас не измерялась; состояние deployed bot/web этим не установлено.
20 секунд — timeout одного вызова, не всей операции: runner продолжает остальные
read-only steps после ненулевого exit code. Нет собственного reconnect retry или
cooldown в просмотренном SystemSshClient/runner; несколько шагов — не retry одной
команды. Проверка не охватывает все handlers/agent/API и не доказывает общий предел
SSH concurrency, жёсткий deadline операции или остановку remote-процесса по timeout.

## Согласованный ограниченный fix

- В AMN2 app/web/app.py выполнять только run_server_health_check через
  await asyncio.to_thread; передавать settings и строковое server name.
- Проверки auth/CSRF и оба блока _open_repository оставить в прежнем потоке.
  Первый блок закрывается до await; после результата создаётся новое соединение
  для записи summary/audit. Бот и peer mutations в этот slice не включать.
- tests/web/test_servers.py: синтетический медленный health stub с управляемым
  завершением; другая coroutine должна работать до освобождения stub. Проверить
  сохранение summary/audit и прежний redirect; invalid auth/CSRF не запускает stub.
- Сначала RED на существующем handler, затем минимальный fix и GREEN целевого
  набора. Не читать реальную конфигурацию, не отправлять SSH или Telegram.
- Offload освобождает event loop, но не добавляет очереди/лимиты/circuit breaker.
  Отмена await не доказывает остановку worker или remote-команды; rollback и
  отмена state-changing операций этим изменением не решаются.

Оператор согласовал этот scope командой «приступай» 20.09.2026. Для реализации
создан отдельный AMN2 checkout; исходный checkout сохранён. Commit/push сверяются
с AMN2 remote отдельно от документации AMN3.
Для bot flow нужны независимое решение о SQLite/transactions и сохранении порядка
remote/local side effects; не оборачивать весь workflow в to_thread и не отключать
check_same_thread ради обхода ошибки. Circuit breaker/retries требуют отдельных
идемпотентности, классификации ошибок и политики повторов.

## Проверки и границы исходного source review

Прочитаны tests/server/test_system_ssh.py (timeout/missing binary), соответствующие
runner tests (продолжение после failed step) и web health/CSRF tests. Они не
доказывают отзывчивость event loop; их результаты сейчас не перепроверялись.
Изменения исходного review — только документы AMN3, ссылки/readback/diff/CHANGELOG.
AWG2, package016, выдача, source AMN2, VPS/stage/install не изменены. Общая выдача
по-прежнему отключена; этот fix не закрывает Windows traffic или quality.

Семантика Python: [asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread),
[SQLite check_same_thread](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect).
Проверка четырёх ideas-файлов нашла существующую карточку; дубль не создан.
Weekly cursor не продвигается: закрыт только узкий вопрос #174.


## Локальная реализация после согласования — 2026-09-20

Worktree: C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop.
Ветка codex/phase16-web-health-event-loop; исходный baseline 56540e2084140e3a6277d7472c88c599d7153ccf.
Native worktree tool обслуживает репозиторий текущей задачи AMN3, поэтому отдельный
AMN2 worktree создан через git. Родительский worktrees/ игнорируется Git; исходный
AMN2 checkout не изменялся. В исходниках изменены только app/web/app.py,
tests/web/test_servers.py и добавлен CHANGELOG.md для этого материального commit.

Handler теперь await-ит asyncio.to_thread(run_server_health_check, settings, name).
Оба блока SQLite и auth/CSRF остаются в прежнем потоке. Ответ и запись summary/audit
не вынесены в worker. Dependencies, SSH runner и остальные handlers не изменены.

Проверки в существующем Python 3.12.14, PYTHONPATH — существующий .codex_deps,
PYTHONDONTWRITEBYTECODE=1; pytest -q --tb=short -p no:cacheprovider:

- Baseline: tests/web/test_servers.py + tests/web/test_server_health.py — 28 PASS.
- RED: только новые slow_health_check/health_rejected_request — 2 ожидаемых FAIL
  (другой HTTP-запрос timeout во время удерживаемой проверки), 3 guards PASS.
- GREEN: один итоговый прогон обоих файлов — 33 PASS, 22.88 s.
- Общий suite не запускался: согласован релевантный web server/health набор.
- Во всех прогонах одно прежнее StarletteDeprecationWarning о httpx; это warning
  baseline, не новая ошибка и не повод менять зависимости внутри этого scope.

Новые тесты: два реальных HTTP-запроса к одному TestClient event loop, synthetic
health stub удерживается Event до ответа страницы /servers. Проверяются online и
offline summary, audit и 303 redirect через временную SQLite. Три случая отказа
(auth, CSRF, missing server) не запускают remote boundary. Таймауты в тесте —
защита от зависания теста, не измерение production latency и не новый SLA.

Независимый read-only review /root/review_web_health_offload завершён: Critical,
Important, Minor — нет. Reviewer не повторял тесты. Нагрузочные пределы/очередь,
перекрывающиеся проверки, отмена worker/SSH, общий deadline, bot и live acceptance
сознательно оставлены за пределами; исполнитель сохранил эти ограничения.
Документация и changelog проверены исполнителем отдельно. Это локальный fix; live health check, VPS/SSH/Telegram, production БД, package016 и выдача не
запускались. Отмена await по-прежнему не гарантирует прекращение worker; общий
лимит операций, повторы/cooldown и bot workflow остаются вне этого slice.


Source commit: [2069e4147437067c08a7d3bde7361433179ac727](https://github.com/barakov-dot/amn2/commit/2069e4147437067c08a7d3bde7361433179ac727).
Push в https://github.com/barakov-dot/amn2.git,
refs/heads/codex/phase16-web-health-event-loop, без force и тегов; remote readback
подтвердил exact SHA. Новая ветка основана на указанном local baseline 56540e2,
включая его прежнюю историю. Исходная ветка/checkouts не передвигались, merge и
развёртывание не выполнялись. Source worktree сохранён для дальнейшей интеграции.
Документация AMN3 фиксируется отдельно с собственной записью CHANGELOG.

## Bot: SQLite и границы переноса — 2026-09-20

Статус исходного разбора: SOURCE_REVIEW_COMPLETE.
По последующему «учтем и продолжим» подготовлен [письменный design варианта A](../../docs/superpowers/specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md):
Design утверждён последующим «подтверждаю» после commit b277154.
[План реализации](../../docs/superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md)
впоследствии утверждён и выполнен; результаты находятся в разделе реализации ниже.
Это продолжение source review по команде оператора «работаем», а не выполненный
bot fix или второй execution plan. Проверен source HEAD
2069e4147437067c08a7d3bde7361433179ac727 в сохранённом AMN2 worktree выше;
исходники не изменялись, приложение/тесты/SSH/Telegram не запускались.

### Подтверждённые ограничения

- app/main.py:82,288 создаёт один workflow с Repository/SQLite;
  app/db/connection.py:10 сохраняет стандартный check_same_thread.
  app/bot/main.py:65 передаёт тот же workflow всем handlers. AST-инвентаризация
  app/bot/handlers.py обнаружила 41 прямой вызов 30 методов workflow. Это число
  call sites этого файла, не полное покрытие приложения или все методы класса.
- app/bot/workflows.py:844 и app/services/device_revoke.py:143 выполняют
  удаление peer на сервере до локальной транзакции. При ошибке БД после удаления
  поднимается RemoteOperationPartialFailure; это RuntimeError, не PeerApplyError
  (app/services/access.py:90). Reset (workflows.py:870) также может удалить
  часть peers до ошибки. Handlers revoke/reset (handlers.py:320,362) ловят
  PeerApplyError, но не дают отдельного ответа для RemoteOperationPartialFailure.
  Это вывод из кода, не зарегистрированный live-инцидент.
- Прочитан tests/bot/test_bot_workflows.py:
  test_user_reset_reports_partial_failure_when_one_remote_remove_succeeds_and_next_fails
  уже описывает состояние remote-changed-local-failed. Тест здесь не запускался;
  наличие проверки workflow не доказывает обработку этого исхода в UI бота.
- _send_admin_config_handoff (handlers.py:738) после Telegram send_document
  отдельно вызывает record_admin_config_delivery для успеха/ошибки. При смене
  lifecycle нельзя закрыть worker между отправкой и этой записью или назвать
  выдачу доставленной только по результату фоновой операции.
- create_dispatcher дополнительно публикует _phase15_awg3_components в своём
  context (app/bot/main.py:193). Компоненты содержат сервисы с тем же Repository:
  переносить только 41 вызов и оставлять этот обход к БД недостаточно.
- Часть list-методов возвращает sqlite3.Row. Граница фонового исполнителя должна
  возвращать материализованные значения, не Repository/connection/cursor или
  сервис с доступом к БД; секретные config bytes допустимы только в существующем
  пути доставки и не должны попадать в новые diagnostic records.
- handle_as_tasks и limit=8 (main.py:103, bot/persistent_runtime.py:15)
  не освобождают event loop от синхронного вызова. После переноса остаётся предел
  одновременных handlers: когда заняты все слоты, немедленный ответ на новую
  команду также не гарантируется. Watchdog должен работать независимо от SSH.
- ProtocolIssuanceBarrierService.begin_block меняет статус всего пользователя
  и отменяет reserved issuance. Это не готовый mutex для отдельного device revoke;
  использовать его как такой mutex без изменения контракта нельзя.

### Два подхода и рекомендация

| Подход | Что изменится | Цена и ограничения |
| --- | --- | --- |
| A — один последовательный исполнитель workflow, рекомендуется первым | Создание, вызовы и закрытие SQLite принадлежат одному рабочему потоку; handlers ожидают async facade; существующий remote → local порядок внутри метода сохраняется | DB-backed меню ждут медленную операцию в очереди; нужен перенос всего bot boundary, lifecycle и доставка результатов; это не параллельное управление VPN |
| B — prepare → SSH → finalize с независимыми операциями | БД остаётся в event loop, SSH вынесен отдельно; независимые чтения/операции могут продолжаться | Нужны reservations/rechecks, координация revoke/reset/issuance, отмена и recovery; шире изменение состояния/интерфейсов, возможна миграция БД |

Рекомендация A опирается на цель освободить event loop без одновременных изменений
peer из одного bot workflow. Это не обещание общей межпроцессной блокировки:
web/CLI и другие writers продолжают требовать собственных контрактов.
Один последовательный исполнитель сохраняет атомарность синхронного метода по
отношению к другим его jobs, но не всего handler из нескольких вызовов. Проверки
прав/состояния должны оставаться внутри бизнес-операции, рядом с изменением.

Перед реализацией A в письменном design нужно зафиксировать:

1. Закрытый async API с явными разрешёнными методами и ограниченной очередью;
   обработку перегрузки без незаметной постановки повторной mutation.
2. Владение БД от factory до close, включая startup error/timeout; отсутствие
   доступа к repo/phase15 components из event loop и сохранение синхронного API
   для существующих service/CLI callers, если они не входят в bot boundary.
3. Отмену ещё не начатой работы отдельно от уже запущенной. Отмена await не
   останавливает поток/SSH и не должна пропустить локальное завершение после
   remote side effect. Терминальный исход учитывается даже без ожидающего handler.
4. Shutdown: порядок остановки приёма, завершения принятых handlers/jobs,
   записи delivery outcome, закрытия БД/Telegram и освобождения instance lock.
   Простое cancel_futures недостаточно для начавшихся операций; принудительное
   завершение процесса и жёсткий общий deadline этим подходом не решаются.
5. Явный безопасный ответ при RemoteOperationPartialFailure: нужна ручная сверка,
   автоматического повтора нет; не сообщать, что сервер не изменился или всё
   откатилось. Не печатать exception cause, raw SSH output, конфиги или ключи.

Критерии будущих synthetic тестов: временная SQLite с обычной thread check;
управляемый медленный peer stub и работа другой coroutine/watchdog до release;
последовательный revoke/reset; отрицательная auth-проверка перед side effect;
queue overflow; отмена до/после старта; partial remote/local failure; startup
failure; shutdown во время SSH и между Telegram send и delivery record. Telegram
и SSH заменяются test doubles, реальные секреты/серверы не используются.
Это требования к проверкам, не PASS и не утверждённый implementation plan.

Семантика сверена с официальной документацией Python 3.12:
[SQLite thread ownership](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.connect),
[Executor shutdown и cancellation](https://docs.python.org/3.12/library/concurrent.futures.html#concurrent.futures.Executor.shutdown).
Ни check_same_thread=False, ни обычный to_thread вокруг уже созданного workflow
не являются предлагаемым решением. Retries/circuit breaker, DB schema, live
recovery, включение выдачи, package/stage/install не входят в этот review.

На момент исходного разбора следующий шаг — review implementation plan и выбор
метода; впоследствии выполненная реализация описана ниже. Политика очереди/отмены/drain
зафиксирована в design; этот source review остаётся основанием, а не конкурирующим
контрактом. До review плана bot-код не меняется.
Текущий статус отдельного DefaultVPN направления — в [обращении и ответе поддержки](phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md);
новых phone tasks этот bot review не задаёт.
Проверка этой записи: source readback, локальные ссылки, diff/whitespace и
CHANGELOG; runtime tests не запускались. AWG2_UNTOUCHED; package016 immutable;
общая issuance не включалась.


## Bot worker: реализация и проверки — 2026-09-20

Разрешение: после design approval и плана ddabc6d оператор подтвердил весь план
и рекомендованный inline execution («подтверждаю всё»). Выполнены Tasks 1–4,
обычные commits/push в существующую source ветку; новых live approvals нет.

Source: C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop,
ветка codex/phase16-web-health-event-loop, remote amn2 =
https://github.com/barakov-dot/amn2.git. Диапазон от 2069e41; commits:
614dfd87120f908d2ff6d275ee8097945056a35b,
b9f5d4e816492f28f741daccf76eace1303a866c,
28a4e43431d1c16fc1e2b875c5150ec57bcab18e,
8bc8496a85d520096022b55c8ee3f4698c9b0a30. Все четыре включают CHANGELOG;
remote readback подтвердил последний SHA. Исходный checkout/ветка не перемещались.

- Один worker владеет SQLite create/use/close, восемь outstanding jobs в своей FIFO,
  один executor job одновременно, ContextVar копируется на вызов. Queued cancel
  удаляется, dispatched операция заканчивается; join не блокирует event loop.
- 30 явных async methods и 41 await в handlers; Row/DTO превращаются в независимые
  данные. Sync service/CLI API сохранён; raw phase15 bundle из dispatcher убран.
- Lifetime учитывает восемь handlers, ticket привязан к точной task. Shutdown
  запрещает новые handlers, сохраняет принятые jobs/send/record и закрывает
  SQLite, Telegram session и instance lock в этом порядке. Повторная отмена
  не ускоряет освобождение; ошибки runtime и cleanup не теряются.
- Partial failure даёт безопасный ru/en ответ без ложного rollback; failure
  отправки этого ответа не переносит secret-bearing exception context в logger.
  False/ошибка delivery record после send не дают success или повторной выдачи.

Проверки Python 3.12.14, aiogram 3.28.2, существующие локальные зависимости:

| Этап | Доказательство |
| --- | --- |
| Baseline | 278 passed: tests/bot + test_device_revoke.py + test_phase15_bootstrap.py |
| Worker | RED отсутствующего API; 6 PASS (SQLite ownership, capacity/FIFO, cancel churn, context, factory/close failure) |
| Factory/facade | RED трёх незакрытых connections и отсутствующего close; 75 PASS вместе с bootstrap/workflows |
| Lifetime | RED отсутствующего API; 11 PASS с worker, включая повторную отмену cleanup и copied-ticket отказ |
| Runtime/handlers | 5 handler/partial RED + 6 runtime RED; после исправлений 93 PASS affected набора |
| Итог | 310 passed in 54.80s, без warnings; дополнительно real SQLite recheck прав после очереди и remote success/local failure |

Все peer/Telegram boundaries — doubles; ключи/адреса/БД синтетические. Нет SSH,
реальной выдачи, package build/stage/install, schema/dependency changes или deploy.
Это local source PASS; deployed revision и Phase16 acceptance не меняются.
Ограничения: один bot process, DB-backed меню ждёт FIFO, hard drain deadline нет;
external kill/crash/exactly-once и межпроцессная serialization вне scope.

Независимый read-only review 2069e41..8bc8496 завершён. Critical нет.

1. Important: при queued waiter.cancel() pump мог запуститься раньше обработчика
   CancelledError и передать отменённую mutation executor. Детерминированный RED
   подтвердил один лишний side effect. Pump проверяет cancelled waiter перед
   dispatch и освобождает слот ровно один раз.
2. Minor по review, повышен до Important исполнителем: close до dispatch factory
   не препятствовал её последующему запуску. Factory может выполнять schema/seed
   writes после закрытия admission, поэтому это нарушение поведения, а не polish.
   RED подтвердил ненужные factory/close; теперь OPEN проверяется перед submit.

Оба исправления выполнены одним fix pass: 1bd7f62d1fdd3829bc278110ecdc44d3568676a3.
Итоговый набор: 312 passed in 47.46s, без warnings. Повторный review не запускался;
два новых regression tests сначала упали по доказанным причинам, после исправления прошли.
Source HEAD = remote ref, рабочее дерево чистое; пятый commit также содержит CHANGELOG.
Сознательно не оценивались reviewer: external kill/crash/exactly-once и live/systemd
stop budget. Решение исполнителя: сохранить исключения design, не делать live
claims; отдельный deployment gate обязан проверить stop budget/recovery.
Отложенных Minor после этой классификации нет.

Организационные решения: один runtime test файл выделен для читаемости (поведение
и scope неизменны); targeted suite выбран согласно утверждённому плану/AGENTS
(вне набора нет новой общей гарантии); ветка/worktree сохранены, без merge/PR
(интеграция остаётся отдельным решением).
Далее — отдельный integration gate с текущими Phase16 ограничениями,
AWG2_UNTOUCHED; package016 immutable; general AWG3 issuance disabled.


<a id="dependency-validation-2026-09-21"></a>

## Dependency validation M3 — 2026-09-21

Статус: **LOCAL_DEPENDENCY_SLICE_PASS_NOT_TARGET_ACCEPTANCE**.
Approval: оператор ответил «согласовываю, продолжай» после предложения локальной
проверки кандидата с выбранным dependency lock. Scope: отдельная venv, установка
hash-bound dependencies, один existing worker/admission/drain набор. Исходники,
tests, lock-файлы, units, package016 и глобальные зависимости не менялись.

Source AMN2: 1bd7f62d1fdd3829bc278110ecdc44d3568676a3, чистый до/после.
AMN3 entry baseline: 35099d976fb1c9e23c1adb6c834e62a3e58dfe87.
Среда: Windows 11 10.0.26200 AMD64, CPython 3.12.14.
Выбран неизменённый requirements/phase15-test-py312.lock; все его 48 pins
включают exact 40 pins runtime lock. Hashes обоих lock-файлов совпали с gate.
[Нормализованный evidence: все версии/wheel SHA256, locks, run и hashes результатов](phase16-web-bot-dependency-validation-2026-09-21.json).

Изолированный каталог (сохранён, автоматически не очищен):
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-dependency-validation-20260921-1bd7f62.
Он игнорируется основным AMN3 checkout. include-system-site-packages=false;
aiogram/pytest и все 48 dependencies загружены из его venv. Нет зависимости
от прежнего .codex_deps/PYTHONPATH. Bootstrap pip 25.0.1 — единственный пакет
venv вне test lock; он не является runtime dependency приложения.

Установка: только https://pypi.org/simple, все wheel URLs files.pythonhosted.org;
require-hashes, only-binary=:all:, no-cache-dir, retries=0, request timeout 15s,
общий предел 300s. Pip config отключён через PIP_CONFIG_FILE=os.devnull,
унаследованные PIP_* и PYTHONPATH/PYTHONHOME исключены. Exit 0 за 30.88s.
Независимая сверка install-report: имя/version/hash каждого wheel соответствует
lock; runtime pins — точное подмножество test pins. pip check:
No broken requirements found. Глобальные env/config/dependencies не менялись.

Один runtime-прогон, только существующие файлы:

| Файл AMN2 | Проверяемая граница |
| --- | --- |
| tests/bot/test_workflow_worker.py | SQLite ownership, FIFO/capacity/context, cancellation races, factory/close |
| tests/bot/test_async_workflow.py | Материализация данных, auth recheck, remote/local partial outcome |
| tests/bot/test_handler_lifetime.py | Accepted handlers, ticket/лимит, drain, repeated cancellation и safe replies |
| tests/bot/test_persistent_runtime.py | Identity/webhook/backlog admission, recheck, timeout и instance lock |
| tests/bot/test_app_bootstrap.py | Factory cleanup, injection и persistent startup/readiness/watchdog |
| tests/bot/test_bot_runtime_worker.py | Busy revoke/queued reset, send→record drain, runtime failure cleanup |

Запуск venv Python с -I -B; в sys.path добавлен только exact source checkout.
pytest: -q --tb=short --maxfail=1 -p no:cacheprovider; новый отдельный basetemp,
JUnit вне Git; PYTEST_DISABLE_PLUGIN_AUTOLOAD=1. Окружение дочернего процесса
ограничено системными launch/temp переменными и тестовыми флагами, VPS_APPLY_ENABLED=false.
Предел всего процесса 180s, первая ошибка останавливает набор.
Существующие fake Telegram/peer adapters и temporary SQLite; VPS/Telegram API
и реальные configs не используются. Процесс выполнялся в штатном sandbox.

**Результат: 68 passed in 8.27s**, exit 0; wall time 9.17s.
JUnit подтвердил 68 tests, 0 failures/errors/skipped; warnings не сообщались.
Повторных прогонов не было. Это проверка нового dependency environment, не
повтор прежнего 312-набора, не новый RED/GREEN fix и не полный web/bot acceptance.

Локальный lifecycle gap aiogram 3.28.2 → pinned 3.30.0 закрыт в этом scope.
Target Python/dependencies/deployed SHA, Linux execution, effective systemd
properties и конечный stop budget остаются UNKNOWN. Новый совместный web+bot,
persistence/leak/recovery acceptance не выполнялся. M3 целиком не закрыт,
Task 3B/5/6 не приняты. [Gate и M1–M7](../../docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#integration-readiness-web-bot)
и [главный план](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md)
обновлены; следующий предмет решения — локальный source-only stop-budget M4.

Прежние Windows traffic/quality FAIL, DNS bridge STOP и отложенные iPhone/A/B
сохранены. AWG2_UNTOUCHED; package016 immutable; general issuance disabled.
Нет SSH/VPS/реальной выдачи, stage/install/deploy, cleanup, source fix или merge.

<a id="stop-budget-m4-2026-09-21"></a>

## Stop budget M4: source-only evidence — 2026-09-21

Статус: **SOURCE_REVIEW_COMPLETE / STOP_BUDGET_UNPROVEN / TARGET_UNKNOWN**.
Approval: «приступаем» после предложения source-only M4. Только локальное
чтение и документация; без новых tests, dependency install, code/unit edits,
systemd simulation, процесса приложения или любых VPS/Telegram действий.
AMN3 entry HEAD 3597eb78c3f3a5f14ec4093872bbfe327bf3185e, clean.
AMN2 1bd7f62d1fdd3829bc278110ecdc44d3568676a3, clean; unchanged.

### Проверенная цепочка source

Ссылки привязаны к одному immutable candidate; это не deployed SHA.

| Source | Проверенный факт и предел |
| --- | --- |
| [app/main.py:46–172](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/main.py#L46-L172) | Lock/client до startup timer; admission → worker.start → state recheck внутри; polling после; cleanup cancel → lifetime → worker → session без общего срока |
| [Factory:323–359](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/main.py#L323-L359), [settings:32](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/config/settings.py#L32) | Factory schema/seed writes; admission default 30s, validation 1..120, не manager start/stop SLA. Settings и синхронные операции не становятся hard bounded |
| [WorkflowWorker](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/bot/workflow_worker.py#L67-L181), [HandlerLifetime](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/bot/handler_lifetime.py#L30-L119) | Shielded factory/jobs/handlers; drain без общего deadline, executor shutdown wait=True; repeated root cancellation не даёт terminal proof |
| [SSH](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/server/ssh.py#L50-L157), [Docker revoke:413](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/server/peer_apply.py#L413-L447) | SSH default 20s на subprocess; Docker read/write/restart последовательно. Не один timeout на всю revoke, не remote quiescence |
| [Reset:878](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/bot/workflows.py#L878-L939), [cascade:143](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/services/device_revoke.py#L143-L208) | Список устройств без локального reset cap; remote removals, затем local cascade/transaction/audit; remote success/local fail остаётся partial |
| [Delivery record:739](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/bot/handlers.py#L739-L787), [delivery:873](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/bot/handlers.py#L873-L923) | Несколько sends либо send→record→reply; handler drain сохраняет весь путь, queue capacity не ограничивает его время |
| [SystemdNotifier](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/systemd_notify.py#L45-L73) | Синхронный Unix datagram send без заданного socket timeout; READY/STOPPING/WATCHDOG, нет EXTEND_TIMEOUT_USEC |
| [Web health/repository](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/web/app.py#L2179-L2265), [CLI entrypoints](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/cli.py#L1573-L1612) | Health to_thread и последующий summary/audit имеют отдельный lifetime. Web/API uvicorn.run без graceful timeout; request cancellation не доказывает прекращения worker thread |
| [Agent launch](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/cli.py#L1791-L1817), [agent audit](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/agent/audit.py#L37-L61), [API repository](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/api/app.py#L247-L254), [CLI mutation](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/cli.py#L1615-L1647) | Возможные независимые writers; schema/audit тоже запись. Scope не является полным аудитом всех endpoints. Target presence, DB equality и scheduler/manual ownership UNKNOWN |

### Pinned dependencies и signal boundary

Прочитаны сохранённые M3 файлы из
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-dependency-validation-20260921-1bd7f62/venv/Lib/site-packages.
[Wheel versions/SHA256](phase16-web-bot-dependency-validation-2026-09-21.json)
связывают aiogram 3.30.0 и Uvicorn 0.52.3 с unchanged lock; версии не взяты
из latest docs. Библиотеки не импортировались для runtime probe.

| Файл относительно site-packages | Source evidence |
| --- | --- |
| aiogram/client/session/base.py:45–60; aiohttp.py:129–187 | DEFAULT_TIMEOUT=60.0; app.create_bot не переопределяет timeout. Session close await + sleep(0.25), не hard deadline всей операции |
| aiogram/dispatcher/dispatcher.py:198–258, 520–630 | Polling request timeout отдельно от send; polling backoff существует. handle_signals=True по умолчанию; SIGTERM/SIGINT handlers ставятся в start_polling до emit_startup; затем await/cancel polling tasks и shutdown hooks |
| uvicorn/config.py:231,279; server.py:272–319 | timeout_graceful_shutdown=None по умолчанию; shutdown ждёт connections/tasks через wait_for с этим значением, затем отдельно lifespan. CLI web/API/agent не передают override |

Статический вывод: app.main не устанавливает собственный SIGTERM handler до
admission/factory/recheck; регистрация pinned aiogram происходит позже, внутри
polling. Это отдельная **startup signal gap** в доказательстве graceful cleanup:
существующие synthetic cancellation tests на Windows не проверяют Linux SIGTERM
в этом окне. Не утверждается, что такое прерывание происходило на target, и
не предлагается проверять его live. Нужен отдельно согласованный lifecycle design
и затем bounded Linux/signal validation выбранного решения.

M4 нельзя закрыть формулой 8 × 20s или простым увеличением 30s из bot unit example:
нет полного bound для accepted handler, startup cleanup, DB/filesystem/close,
других writers и terminal remote state. Uvicorn default None — ещё один открытый
участок для exact CLI entrypoint; фактический target может иметь иной entrypoint
или настройки и пока UNKNOWN. Timers источника не переименованы в target values.

### Результат и границы

[Существующий контракт M4](../../docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#stop-budget-m4)
теперь содержит карту bounded/unbounded участков, writers и минимальный future
readback: exact identities/manager version, state/process identity, start/stop/
kill/restart/watchdog/start-limit properties, execution hooks/entrypoint binding,
DB identity equality и owner/launch source. Сбор не выполнялся. Реальные unit
names/target/caps отсутствуют, исполняемый /APPROVE не выдаётся; raw env/config/
cmdlines/DB/journal не запрашиваются.

Следующее решение: отдельный локальный lifecycle design для stop до polling,
workload bounds и terminal/recovery policy; затем отдельные code/test и target
readback scopes. M3 target и M4 budget остаются открыты, M1/M2/M5/M6/M7 не сняты.
Прежние 33/312 и M3 68 PASS сохранены как датированные результаты, не повторены.
Проверка этого изменения: документационный readback, локальные links/anchors,
source line bindings, diff/whitespace, added-line secret scan; AMN2 неизменён.
AWG2_UNTOUCHED; package016 immutable; general issuance disabled; DNS bridge STOP.
Windows traffic/quality FAIL, iPhone/A/B отложены. Нет stage/install/deploy/cleanup.


<a id="lifecycle-design-m4-2026-09-21"></a>

## Lifecycle design M4 — 2026-09-21

Оператор следующим «приступаем» согласовал подготовку design после source-only
receipt M4. AMN3 entry HEAD 1dd7795fe99eec35e0db351deb84c011ca63085e;
AMN2 1bd7f62d1fdd3829bc278110ecdc44d3568676a3, оба active worktrees чистые до
правок. Основной AMN3 checkout остаётся старым/грязным; его файлы не менялись.

Подготовлен [design A в существующем контракте](../../docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#lifecycle-design-m4),
статус DESIGN_PROPOSED / NOT_IMPLEMENTED. Сравнены три варианта: единый signal
owner с сохранением drain (рекомендация), жёсткое прерывание по таймеру (не выбрано),
полная переработка deadlines/durable recovery/writers (отдельный большой scope).
Цель A — stop до startup, единственный cleanup и недопущение factory/READY
после уже обработанного stop. Startup-only guard не закрывает worker для
последующих jobs ранее принятых handlers. Signal latency и полный stop budget
не объявлены ограниченными.

Сохранены H=8/Q=8 и бизнес-семантика reset; число устройств в существующей БД
не подменено max_devices. Для будущих tests определены конечные synthetic cases,
а production bulk cap/enforcement остаётся отдельным gate. Отделены local cleanup
и business outcome. PARTIAL/UNKNOWN не разрешают replay/resend/cleanup; operator
gate не выдаётся за durable marker или уже реализованный systemd restart fence.

Reviewable source slice: app entrypoint/StopController/signal adapter, startup
factory guard, targeted synthetic tests и AMN2 CHANGELOG; без services/schema/
web/units/реальных Telegram или SSH операций. Linux signal check возможен только
в отдельно связанном disposable synthetic child; Windows injection не заменяет
Linux evidence. Числа production timeouts не назначены, новая среда не создавалась.

Проверка design: чтение существующих source/contracts/tests (без запуска),
inline self-review races/error paths/scope, links/anchors, readback/diff/whitespace
и added-line secret scan. Это подготовка документа, не RED/GREEN, signal probe
или test PASS. Утверждение written design, implementation plan и его выполнение
ещё впереди. M3 target/M4 budget и остальные prerequisites остаются открытыми.
AWG2_UNTOUCHED, package016 immutable, general issuance disabled; Windows/quality
FAIL, DNS bridge STOP, iPhone/A/B отложены. Нет code/dependencies/units changes,
stage/install/deploy/cleanup, пересборки package или повторения прежних tests.


<a id="lifecycle-plan-m4-2026-09-21"></a>

## Lifecycle implementation plan M4 — 2026-09-21

Оператор ответил «Подтверждаю» на design A в commit
8ba7e5d31236824bddd304a4f278965029d1578b. Design утверждён, подготовлен
[подчинённый implementation plan](../../docs/superpowers/plans/2026-09-21-amn2-bot-startup-stop-lifecycle-plan.ru.md),
PLAN_READY_FOR_REVIEW / NOT_EXECUTED. AMN2 source остаётся
1bd7f62d1fdd3829bc278110ecdc44d3568676a3, чистым и неизменённым.

План содержит три задачи: controller/signal scope; runtime/factory wiring;
isolated Linux signal evidence и итоговый affected regression. Зафиксированы
точные paths/interfaces, RED selectors, test caps, ownership/error races,
существующая pinned M3 среда и отдельный Linux NOT_RUN при отсутствии среды.
Никакие test caps не стали production timeout. Сигналы допускаются в будущем
только exact synthetic child, не службам; установка Linux/dependencies исключена.
Метод — inline одним агентом. Source commit/push только в remote amn2;
документы отдельно в AMN3, каждый существенный commit со своим CHANGELOG.

Проверки подготовки: source/fixture/API readback, coverage пяти Review Focus,
syntax check code snippets без исполнения, local links/anchors, diff/whitespace,
added-line secret scan. Python runner source проверен локально для границы
SIGINT ownership; новый runtime probe не выполнялся. Самопроверка уточнила
failure propagation контроллера и READY child без ненужного RELEASE handshake.
Код/units/tests/dependencies не менялись; pytest/OS signals/VPS/Telegram не запускались.
Design/current plan синхронизированы; review/approval исполнения этого плана
остаётся следующим шагом. Все Phase16 ограничения, M3 target/M4 budget,
AWG2_UNTOUCHED, package016 immutable и general issuance disabled сохранены.


<a id="lifecycle-implementation-m4-2026-09-21"></a>

## Lifecycle M4: выполненный локальный source slice — 2026-09-21

Статус **SOURCE_IMPLEMENTED_WINDOWS_TESTED / LINUX_SIGNAL_NOT_RUN /
STOP_BUDGET_UNPROVEN / NOT_DEPLOYED**. Оператор подтвердил исполнение плана
после AMN3 11ea3a6 словами «в части ожидания подтверждения, подтверждаю» и
передал официальный compare клиента 5.0.1.5...5.0.3.0. Это approval локальных
source/tests и описанного commit/push; live scope не расширен.

AMN2 before 1bd7f62d1fdd3829bc278110ecdc44d3568676a3 →
after **6e682356ed14a62d636ee58039fd3a389e794809**:

- 095057235edbc0da5e5756dedff283954822c2b9 — controller/process signal scope;
- a9cd59b75bdd3bd55a1bb7d482acf49ba53bf907 — startup/worker/runtime integration;
- 1e86056d05dadc275ae27e23ca008e992846fa71 — synthetic child и initial affected tests;
- 6e682356ed14a62d636ee58039fd3a389e794809 — bounded self-review fix: запрет повторного bind runtime.

Обычный push в https://github.com/barakov-dot/amn2.git, remote amn2,
refs/heads/codex/phase16-web-health-event-loop выполнен; ls-remote вернул after SHA.
Source worktree чистый. Origin AMN3 не использовался для source push.
Каждый commit содержит содержательный AMN2 CHANGELOG, staged checker PASS.
AMN2 hooks отсутствуют. AMN3 --range checker неприменим напрямую: его policy SHA
5bb1b14 отсутствует в другом репозитории. Перед первым push проверены три parent→commit
через тот же check_change без policy override: три PASS; это явная проверка,
не утверждение о hook/CI protection. Четвёртый commit также содержит CHANGELOG,
staged gate PASS; его exact-ref push/readback подтверждён. История не переписывалась.

Поведение: process scope до asyncio.run/Settings, pending stop до loop/bind,
однократное закрытие admission, отдельная идентичность owned cancellation.
Factory guard перед submit; checkpoints до lock/client/admission/recheck,
polling/receipt/READY. Aiogram handle_signals=False. Принятые handlers/jobs и
send→record дренируются до workflow/session/lock close. Повторный stop и первый
stop в cleanup не отменяют cleanup. Wrapper нормализует только owned stop;
external cancellation, controller failure и runtime/cleanup errors сохраняются.

Дополнительный concurrency regression обнаружил потерю уже завершившейся
polling error при stop + close error: RED 56 PASS/1 FAIL. Cleanup теперь
передаёт эту ошибку наружу без дублирования primary error. Это исправлено до
финального прогона. Scope не затрагивает facade/handlers/business/schema/units,
network timeouts/retries/dependencies либо другие writers.

| Evidence label | Actual result |
| --- | --- |
| task1-red / task1-scope-red | ожидаемый RED отсутствующих API |
| task1-green | 10 PASS / 2.48s |
| task2-factory-red / runtime-red / main-red | ожидаемый RED отсутствующих guard/controller/wrapper |
| task2-initial-green | 54 PASS / 8.03s до дополнительных race cases |
| task2-final-green (имя запуска, не результат) | 56 PASS / 1 FAIL / 9.02s, воспроизведена потеря polling error |
| task2-error-fix-green | 59 PASS / 8.32s |
| lifecycle-final-affected | 93 PASS / 6 SKIP / 8.87s, до финального contract finding |
| lifecycle-generation-red | ошибка черновика test: missing import, не поведенческий RED |
| lifecycle-generation-valid-red | ожидаемый RED: повторный bind не вызвал RuntimeError |
| lifecycle-reviewed-affected | **94 PASS / 6 SKIP / 9.16s**, 0 warnings/errors |

Self-review выявил разрешённый второй bind после normal unbind, вопреки single
runtime generation contract. Добавлен постоянный one-bind latch, подтверждён
валидным RED; affected набор повторён только после этого нового исправления.

Итог — ровно восемь affected файлов из плана; прежний полный 312 suite не
повторён. Селекторы ранних RED уточнены под фактические parameterized tests,
а не буквальные примерные имена плана. Полные argv/caps/exit/duration:
[JSON evidence](phase16-bot-lifecycle-validation-2026-09-21.json).
JUnit/stdout/basetemp/runner/ledger сохранены в
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-lifecycle-validation-20260921.

Повторно использована M3 venv: Python 3.12.14, aiogram 3.30.0, pytest 8.4.2,
include-system-site-packages=false; оба lock hashes совпали с machine-readable
M3 evidence. В prose spec исправлена опечатка runtime hash (пропущенная a);
lock/venv не менялись. Parent runner: isolated Python, plugin autoload disabled,
allowlisted system/temp env, fake adapters, VPS_APPLY_ENABLED=false, no cache.
Отклонение от плана: task-local runner был настроен на 120s/256KiB вместо
90s/128KiB (RED cap см. JSON); фактические времена и output ниже исходных
лимитов, cap не достигнут. Повторов без изменения/диагностированной причины нет.

Linux child подготовлен с SIGTERM/SIGINT × PRE_LOOP/FACTORY_DISPATCHED/READY,
exact Popen handle, fixed enum protocol, 10s watchdog/deadline, 64 records/16KiB,
bounded stderr и cleanup только собственного процесса. Syntax PASS. На Windows
все шесть cases SKIP: **Linux OS-signal execution и negative control NOT_RUN**.
Compatible Linux environment не предоставлена, WSL/Docker/dependencies не
устанавливались. Код child не выдается за исполненное Linux evidence.

Inline self-review пяти Review Focus: pre-resource latch; partial signal install
и restore; external/owned cancellation и combined errors; stop/dispatch/READY
с accepted record; exact-child-only signals и честный NOT_RUN. Subagents/reviewers
не запускались. UNKNOWN остаются target/Linux/systemd lifecycle, stop budget,
writer/restart fence, production workload caps, recovery/activation/rollback.
Следующий отдельный evidence scope — уже доступная compatible Linux среда для
шести child cases и test-only negative control либо согласованный target readback;
ни один из них не разрешён этим receipt автоматически.

AWG2_UNTOUCHED; package016 immutable; general issuance disabled. Нет SSH/VPS,
Telegram API, установки клиента, выдачи, package build/stage/install/deploy/cleanup.
Windows traffic/quality FAIL, DNS STOP и отложенные iPhone/A/B сохранены.
Обзор нового клиента: [release/source receipt](phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md).


<a id="linux-environment-discovery-2026-09-21"></a>

## Linux signal gate: проверка доступности среды — 2026-09-21

После «продолжай» выполнен bounded local read-only inventory, checked_at=2026-09-21T15:47:31+03:00.
Вопрос: есть ли уже доступная локальная Linux-среда для утверждённых шести
synthetic-child cases без установки и без live/VPS? Git сверены: AMN2
6e682356ed14a62d636ee58039fd3a389e794809 и AMN3 f003b3424b826f1aef1258c1a022b774a96ac08f
чисты; старый основной checkout 551055f с пользовательским diff сохранён.

- wsl.exe присутствует в System32; wsl.exe --list --quiet завершился exit=1
  с сообщением, что подсистема Windows для Linux не установлена.
- HKCU Software/Microsoft/Windows/CurrentVersion/Lxss отсутствует:
  зарегистрированных дистрибутивов в текущем профиле не обнаружено.
- docker.exe и podman.exe не найдены через Get-Command/shutil.which в PATH.
  Это не полный аудит всех возможных VM, установочных каталогов или других users.
- Дистрибутивы/службы не запускались, engine/container/VM не создавались.
  Установки, SSH/network, host/service signals и тесты не выполнялись.

Лимит WSL query — 15s, timeout не достигнут. Первый display имел повреждённую
кодировку вывода; один повтор того же read-only list сохранил Unicode в JSON
и подтвердил текст ошибки. Ошибка запуска не выдана за Linux PASS.
Evidence сохранено в существующем scratch:
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-lifecycle-validation-20260921/linux-environment-discovery-20260921.json
SHA256: 91d4a1b25fbf708e1199dd2bc1b7bf07fe07a22463c2516a0a2da6a0666c6f6a.

**ENVIRONMENT_NOT_AVAILABLE_ON_CHECKED_PATHS / LINUX_SIGNAL_NOT_RUN**.
Прежние 94 PASS/6 SKIP — результат source validation предыдущего шага, сейчас не
повторялись. Source/locks/units/dependencies неизменны. От оператора нужен только
идентификатор уже готовой локальной Linux VM/дистрибутива и путь к её Python/venv;
после этого сначала проверяются source SHA, Python/ABI и точные dependency pins,
затем допускается child-only negative control + six-case run по существующему
плану. Подключение к VPS или установка новой среды требуют отдельного scope;
эта проверка их не разрешает. Отсутствие ответа не считается approval.

M3 target/M4 budget/writer/restart fence и Phase16 acceptance остаются открыты.
AWG2_UNTOUCHED, package016 immutable, general issuance disabled;
stage/install/deploy/cleanup не выполнялись, Windows/quality FAIL и DNS STOP сохранены.


<a id="spain-bot-target-readback-2026-09-21"></a>

## Существующий Spain bot: target подтверждён, первый readback PARTIAL — 2026-09-21

Оператор ответил «подтверждаю» на уточнение Spain/amn2-spain-bot.service и
представленный следующий read-only шаг. Подготовка пересоздания продолжается;
само переключение приложения, DB/service/Telegram mutation не выполнялись.
AMN2 source по-прежнему 6e682356ed14a62d636ee58039fd3a389e794809, чистый.

Проверены существующие Spain trust binding, no-follow/ACL и host pin через
load_fixed_role_binding; значения target/user/key/pin не выводились.
Системный C:/Windows/System32/OpenSSH/ssh.exe имеет Authenticode Status=Valid.
Затем выполнен **один** SSH-сеанс: strict host key, batch mode, connect 10s,
one attempt, общий wall cap 60s/output 64KiB; remote собственный deadline 45s.
Python работал с -I -B, без app import, EnvironmentFile, DB, journals, Telegram,
service action, установки или записи файлов на сервере. Старые executors/GO
не запускались; из проверенного helper использованы только trust и bounded I/O.

[Нормализованный JSON](phase16-spain-bot-readonly-2026-09-21.json) содержит
actual properties и fingerprints. checked_at remote: 2026-09-21T16:26:59.966385+00:00.
Часы remote/local расходятся; duration не вычислять вычитанием этих timestamps.

| Свойство | Bot | Web |
| --- | --- | --- |
| Unit | amn2-spain-bot.service | amn2-spain-web.service |
| State | loaded / active / running | loaded / active / running |
| Type | notify | simple |
| Restart / NRestarts | no / 0 | on-failure / 0 |
| TimeoutStart / TimeoutStop | 40s / 90s | 90s / 90s |
| KillMode / KillSignal / FinalKillSignal | control-group / 15 / 9 | control-group / 15 / 9 |
| SendSIGKILL / Watchdog | yes / 0 | yes / 0 |
| Drop-ins | 0 | 0 |
| WorkingDirectory | expected shared /opt/amn2-spain/runtime/source | тот же |

Это снимок свойств, не stability/health/single-poller или successful-drain PASS.
90s — установленное ожидание manager, не доказанный верхний предел accepted work.
В отличие от source example у фактического bot Restart=no и TimeoutStop=90s;
настройки не менялись. Другие writers, DB emptiness и AWG equality не проверялись.

**Почему STOP:** одноразовый collector ошибочно ожидал web `-m app.web`.
При несовпадении он штатно остановился до source fingerprints/Python metadata:
STOP_ENTRYPOINT_OR_DROPIN_UNKNOWN. Это дефект допущения collector, не доказанный
серверный дефект. Последующий локальный разбор нашёл Spain web unit с запуском
`/usr/bin/python3 -B -m app.cli web serve --host 127.0.0.1 --port 3031`.
LF-normalized bytes сохранённых Phase12 bot/web units имеют ровно те SHA256,
которые получены на сервере; package файлы не менялись. Это доказывает совпадение
unit bytes, но не подменяет ещё не собранный source/dependency binding.

Исправленный отдельный collector v2 подготовлен локально: правильный web
entrypoint, проверка unit hashes против первого снимка, systemd version,
пять allowlisted source/lock hashes и 48 публичных distribution metadata versions.
Он не импортирует application и не читает protected runtime/environment/DB.
Metadata относятся к isolated system interpreter; без service environment они
не доказывают полную эквивалентность sys.path/dependencies рабочего процесса.
Syntax/readback PASS; v2 **НЕ ИСПОЛНЕН**, автоматического повторного SSH нет.
Probe SHA256: ddccba65df992c389a2399d1fd8f2919ef4ef9eea526e9b387b92973d04fc236.
Scratch: C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-lifecycle-validation-20260921;
spain_bot_readonly_probe_v2.py, run_spain_bot_readonly_v2.py. Первый claim/result
сохранены отдельно, новый runner имеет собственный create-new single-attempt claim.
Оператору предложен ровно один дополнительный read-only сеанс с теми же caps,
чтобы завершить пропущенный binding; ответ пока ожидается. Никакого deploy GO.

Прежние 94 PASS/6 SKIP не повторялись. Linux signals по-прежнему NOT_RUN.
AWG2_UNTOUCHED по области действий, package016 immutable, general issuance disabled;
нет stage/install/deploy/cleanup, DB reset, выдачи или live signal службам.


<a id="spain-bot-target-readback-v2-2026-09-21"></a>

## Spain bot readback v2: разрешённый сбор завершён — 2026-09-21

Оператор ответил «разрешаю» на один дополнительный read-only SSH-сеанс до 60s.
Перед запуском AMN3 ac3bacc и AMN2 6e68235 сверены, worktrees чистые;
SHA probe v2 совпал с предложенным ddccba65df992c389a2399d1fd8f2919ef4ef9eea526e9b387b92973d04fc236.
Одноразовый v2 claim ранее отсутствовал. Trust/ACL/host pin проверены тем же
фиксированным loader без вывода значений; выполнен ровно один новый SSH.

Результат **READONLY_SNAPSHOT_COMPLETE / CANDIDATE_NOT_DEPLOYED**;
[actual JSON](phase16-spain-bot-readonly-v2-2026-09-21.json), checked_at remote
2026-09-21T16:37:59.879117+00:00. 60s/64KiB caps не достигнуты. Это успешный
сбор перечисленных сведений, не полный M3/M4, preflight/deploy или acceptance PASS.
Remote/local timestamps имеют прежнее небольшое расхождение; интервал работы
не считать разностью часов разных машин.

- Bot/web loaded, active/running. Unit hashes, MainPID и process-start ticks
  совпадают с первым снимком; drop-ins=0, NRestarts=0. На снимках нет признака
  замены этих двух процессов; это не длительный stability test и не полный
  census других pollers/writers.
- Bot effective: Type=notify, Restart=no, TimeoutStart=40s, TimeoutStop=90s,
  Watchdog=0, KillMode=control-group, KillSignal=15, FinalKillSignal=9.
  Оба entrypoint соответствуют сохранённым Spain units: bot app.main,
  web app.cli web serve с loopback 127.0.0.1:3031. HTTP readiness не запрашивался.
- Systemd 255.4-1ubuntu8.17; system Python **3.12.3**, SOABI
  cpython-312-x86_64-linux-gnu; Linux machine **x86_64**, glibc **2.39**.
  Это соответствует minor/ABI/platform policy существующего py312 lock,
  но не доказывает installability/importability всех wheels. Local tests были
  на Python 3.12.14; target runtime tests на 3.12.3 ещё не выполнялись.
- app/main.py: 12640 bytes,
  c34a0f457b2242ede138dd0b6dc1b08b860515f7bd2fadb7df8f2b86a3f5ed31.
  Локальный git object read подтвердил совпадение этого файла с 55dc243 и
  910539e, а не с candidate 6e68235 (там c83059bbf43c44a6fea1b1f96179a336376c9952c7a13a6111734f7bfeb3f4d8).
  Один совпавший файл не устанавливает exact deployed revision всего дерева.
- app/bot/lifecycle.py, app/bot/workflow_worker.py и оба phase15 py312 locks
  **ABSENT** в проверенном deployment source. Новый worker/lifecycle кандидат
  туда ещё не установлен; live tree не «чинить» копированием поверх общего source.

**Что значит ABSENT у aiogram/pytest.** Collector намеренно использует системный
Python -I -B, не наследует service EnvironmentFile и не импортирует application.
Среди 48 metadata names: 37 ABSENT, 10 версий отличаются от candidate test lock,
1 совпадает. Это **не** доказательство отсутствия зависимостей у активного бота.
Локальный исторический backend scripts/phase12_spain_live_backend.py разворачивает
отдельный wheel tree /opt/amn2-spain/runtime/site-packages. Его наличие/версии
на сервере этим collector не проверялись. Путь объясняет возможный отдельный
контур зависимостей, но не подменяет fresh service sys.path evidence.
System interpreter нельзя считать готовой candidate test/production средой.

**Следующий конкретный локальный шаг.** Подготовить отдельно reviewable bot
release из immutable AMN2 6e682356ed14a62d636ee58039fd3a389e794809 с собственным
Linux CPython3.12 x86_64 dependency tree/venv и проверенными runtime/test lock
hashes. До materialization уточнить точный состав/лимиты разрешённого package
scope; runtime40 и test48 разделить, не ставить pytest в production environment.
Имеющиеся Windows wheels/venv не переносить на Linux. Package016 не менять.
Подготовить source/dependency/manifest hashes, ограниченные synthetic tests
на Linux и обратимое переключение **только bot**, сохраняя общий web/source/DB.
App startup и schema compatibility проверить до activation: «нулевой бот»
не делает общую DB disposable. Старый release сохранить как revert target.

Сбор v2 не разрешает установку зависимостей, upload, service stop/start,
DB schema/write/reset или Telegram smoke. Следующий remote шаг — только по
конкретным artifact/state/rollback bindings. Третьего SSH не выполнялось.
Application не импортировалось; DB/environment/journal не читались, секреты не сохранялись;
source и прежние 94 PASS/6 SKIP неизменны. Linux synthetic signals NOT_RUN.
AWG2_UNTOUCHED по области действий; stage/install/deploy/cleanup не выполнялись,
package016 immutable, general issuance disabled, Phase16 acceptance открыт.

<a id="bot-candidate-local-preparation-2026-09-21"></a>

## Отдельный bot candidate: локальная подготовка завершена — 2026-09-21

После readback v2 оператор ответил «разрешаю» на локальную подготовку отдельного
развёртывания: файлы, Linux-зависимости, совместимость DB и rollback.
Это расширило прежний local scope на materialization нового bot candidate;
package016, shared source/DB и remote mutation в разрешение не входят.
Перед работой сверены основной грязный checkout, worktrees, clean AMN3 88a68b6
и clean AMN2 6e682356ed14a62d636ee58039fd3a389e794809; чужие файлы сохранены.

Статус: **LOCAL_PREPARATION_COMPLETE_NOT_DEPLOYED**.
[Нормализованный результат](phase16-bot-candidate-preparation-2026-09-21.json),
[manifest](phase16-bot-candidate-manifest-2026-09-21.json),
[состав, будущие gates и границы rollback](phase16-bot-candidate-runbook-2026-09-21.ru.md).
Runbook — сопроводительный документ immutable candidate, не второй execution plan.

**Материализовано локально.** Новый retained scratch:
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-bot-release-preparation-20260921-6e68235.
Bundle phase16-bot-candidate-20260921-6e68235-001.zip, 30485208 bytes;
source.tar содержит 159 файлов из exact Git archive, test-support.tar — 142.
Весь app сохранён из-за общих импортов; web/API/agent не активируются.
PyPI download только из неизменённых locks: binary-only/require-hashes,
target CPython3.12 Linux x86_64/glibc2.39, без установки. Получены runtime40
и test-only8 wheels, физически разнесены по папкам; test lock использует все48.
Windows venv в пакет не входит. Wheels проверены по lock SHA256, Name/Version
в METADATA и целевым CPython/abi3/pure-Python manylinux tags.

| Binding | SHA256 |
| --- | --- |
| Bundle ZIP | e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7 |
| Manifest | 6792cb2cd28b0ce70ae031cac04b29f40db908f5e8bad0770e689de390a9a37d |
| Source tar | 0607d6db2a6670b5cb66ab8ee5d6f1d254e563c1e402fa6bcfbe201428e69a4b |
| Test-support tar | b22f6a656217cebfe653fded0a104399a5a78321f76902f027ed0cb14909ef15 |
| Runtime lock | a381be185b19777b9198526e11df8dcfa0afaf7f15acccd829809e698d679fab |
| Test lock | 52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235 |

Payload inventory/hash verifier: 55 files PASS. ZIP CRC/member set и каждый
payload hash прочитаны обратно и совпали; unpacked payload 33910243 bytes,
wheel bytes 21697999. Локальные scripts, logs, manifests, synthetic SQLite,
JUnit и preparation-result сохранены; large binaries и fixtures в Git не добавлены.
Source/dependency archive hashes не означают installability/runtime Linux PASS.

**Schema compatibility — новый вопрос, не повтор baseline.** На извлечённом
source выполнены четыре DB test modules: test_schema, test_phase13_protocol_schema,
test_phase14_dual_protocol_schema, test_phase15_bootstrap_schema.
**101 PASS / 0 SKIP / 0 FAIL, pytest 46.80s**, harness47.156s/cap120s/256KiB.
Использована прежняя pinned Windows venv Python3.12.14, SQLite3.53.1.
Прежние lifecycle94 PASS/6 Linux SKIP и worker312 PASS не повторялись.

Отдельный synthetic audit использовал две локальные исторические схемы,
55dc243 и 910539e: до перехода 18/19 таблиц, после — 29. Добавлены 11/10
таблиц и 16 columns в devices/device_passports/admin_config_issuance_receipts.
По пять synthetic rows на вариант (user/server/plan/device/passport), без
live DB/config/secret чтения. Старые columns/rows сохранены, новый initializer
идемпотентен; старый initializer сохранил новые columns и marker values.
Старый Repository в отдельном процессе прочитал user/device и записал второго
synthetic user; новый код прочитал запись. integrity_check и foreign_key_check PASS.
Repository между двумя историческими refs идентичен. Совпадение deployed main.py
с этими refs по v2 не доказывает revision остальных live файлов или live schema.
Тест не покрывает все доменные таблицы, реальный web HTTP и concurrent writers.

**Два подтверждённых ограничения startup.** seed_default_plans перезаписал
name/price/is_free/is_active изменённого synthetic days_30; max_devices сохранён.
Это прежнее поведение старта, не regression lifecycle. initialize_schema при
unsupported partial Phase15 schema выбросил ожидаемую ошибку, но таблицы,
созданные до поздней проверки, остались: общий startup не атомарен.
VPS_APPLY_ENABLED=false не запрещает эти local DB writes. Candidate запускать
на authoritative shared DB как «проверку» нельзя; DB reset/restore не выполнялись.

**Результат rollback review.** До запуска нового кода возможен адресный возврат
только собственного unit override к сохранённому source/dependency tree.
После старта code revert не откатывает seed/schema writes; нужны фактическая
schema/release identity, writer fence и доказанная совместимость старого кода.
Backup не разрешает DB restore поверх web/других писателей. Старый source,
token/identity, web, AWG2 и retained packages сохраняются. Поэтому production
activation всё ещё BLOCKED_PENDING_SHARED_DB_AND_LINUX_GATES.

**Следующее допустимое локальное действие:** подготовить checksum-bound
single-attempt runner изолированного Linux gate для этого exact bundle:
новый каталог, test-only venv с offline wheels, один negative control и
шесть synthetic signal cases, без polling/рабочих DB/служб; limits/STOP описаны
в runbook. Затем отдельное согласование upload/test-environment writes на Spain.
Готового remote runner и разрешения его исполнения сейчас нет; deployment
activation и DB migration остаются отдельными от isolated test gate.

В этом прогоне SSH=0, remote writes=0; Telegram/service signals/install/
stage/deploy/cleanup отсутствуют. Linux execution NOT_RUN. AMN2 source,
locks и units неизменны; AWG2_UNTOUCHED, package016 immutable,
general issuance disabled; Windows traffic/quality FAIL остаются открыты.

<a id="bot-linux-runner-local-2026-09-21"></a>

## Локальный исполнитель isolated Linux gate подготовлен — 2026-09-21

После «продолжай» завершён следующий согласованный local slice Task3B:
[конкретный gate/approval contract](phase16-bot-linux-isolated-gate-2026-09-21.md),
[local evidence](phase16-bot-linux-runner-local-validation-2026-09-21.json).
AMN3 base329ee06, AMN2 source6e68235 и bundleSHA e19abc5c… прежние.
Добавлены отдельные local/remote runners и32guard tests; remote startup,
trust loader и SSH не вызываются при default offline preview.
Artifact checks, framed stdin hash verification, exclusive claims, pinned
offline48wheel test-venv, network namespace, expected negative/six GREEN,
caps/owned-child cleanup и fail-closed/no-retry правила материализованы.

RED/GREEN и path fix завершены; итог32PASS/0SKIP/0FAIL/0.50s. Offline CLI
подтвердил exact bundle и remote SHA без SSH. Details/caps/hashes/команда и
границы находятся в gate, не копируются как второй execution plan.
Linux OS cases/negative control/unshare/venv availability остаются NOT_RUN;
локальные tests не являются Linux evidence или production stop-budget PASS.
Shared DB compatibility/seed/writer-fence и activation gates остаются открыты.
Следующий шаг — отдельное approval на один exact isolated server test gate,
после него только один запуск и сохранение результата без automatic retry.
Source101schema/94+6lifecycle/312worker не повторялись; package016/bot bundle
immutable, AWG2_UNTOUCHED, issuance disabled, stage/install production/deploy/
Telegram/service actions/cleanup не выполнялись.
