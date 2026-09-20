# Phase16 — применимость Panel #174: SSH и цикл событий

Статус: LOCAL_IMPLEMENTED_TESTED_REVIEWED_PUSHED_NOT_DEPLOYED.
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
