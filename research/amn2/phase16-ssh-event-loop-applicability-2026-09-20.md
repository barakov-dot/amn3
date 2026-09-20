# Phase16 — применимость Panel #174: SSH и цикл событий

Статус: SOURCE_REVIEW_COMPLETE / LOCAL_FIX_PROPOSED_NOT_IMPLEMENTED.
Проверка завершена 2026-09-20 20:25 Europe/Moscow. Это ограниченный разбор
одного сигнала из [реестра](../../docs/UPSTREAM_INTAKE.ru.md), не полный weekly.
Цель: определить, применима ли защита от блокирующего SSH к нашему коду.

## Источники и результат

AMN2 checkout: C:/Users/SooL/Documents/amn2-phase15-local-package-bootstrap-readiness,
HEAD 56540e2084140e3a6277d7472c88c599d7153ccf, дерево чистое до/после чтения.
Ни приложение, ни SSH, ни тесты не запускались; configs/keys/БД не читались.

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

## Первый ограниченный fix для согласования

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

Это предлагаемый scope, код ещё не изменён. После согласования работать в отдельном
checkout AMN2, сохранив исходный; AMN2 commit/push target проверить отдельно.
Для bot flow нужны независимое решение о SQLite/transactions и сохранении порядка
remote/local side effects; не оборачивать весь workflow в to_thread и не отключать
check_same_thread ради обхода ошибки. Circuit breaker/retries требуют отдельных
идемпотентности, классификации ошибок и политики повторов.

## Проверки и границы

Прочитаны tests/server/test_system_ssh.py (timeout/missing binary), соответствующие
runner tests (продолжение после failed step) и web health/CSRF tests. Они не
доказывают отзывчивость event loop; их результаты сейчас не перепроверялись.
Изменения этого review — только документы AMN3, ссылки/readback/diff/CHANGELOG.
AWG2, package016, выдача, source AMN2, VPS/stage/install не изменены. Общая выдача
по-прежнему отключена; этот fix не закрывает Windows traffic или quality.

Семантика Python: [asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread),
[SQLite check_same_thread](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect).
Проверка четырёх ideas-файлов нашла существующую карточку; дубль не создан.
Weekly cursor не продвигается: закрыт только узкий вопрос #174.
