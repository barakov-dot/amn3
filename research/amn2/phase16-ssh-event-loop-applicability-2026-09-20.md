# Phase16 — применимость Panel #174: SSH и цикл событий

Статус web slice: LOCAL_IMPLEMENTED_TESTED_REVIEWED_PUSHED_NOT_DEPLOYED.
Bot: SOURCE_REVIEW_COMPLETE / APPROACH_PROPOSED_NOT_APPROVED.
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

Статус этого раздела: SOURCE_REVIEW_COMPLETE / APPROACH_PROPOSED_NOT_APPROVED.
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

Следующий шаг — выбрать A либо B и согласовать его письменный design; затем
implementation plan в рамках единого плана Phase16. До этого bot-код не меняется.
Текущий статус отдельного DefaultVPN направления — в [обращении и ответе поддержки](phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md);
новых phone tasks этот bot review не задаёт.
Проверка этой записи: source readback, локальные ссылки, diff/whitespace и
CHANGELOG; runtime tests не запускались. AWG2_UNTOUCHED; package016 immutable;
общая issuance не включалась.
