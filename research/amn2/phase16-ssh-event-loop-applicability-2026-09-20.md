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
