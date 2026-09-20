# AMN2 Bot Workflow Worker — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> for the recommended inline execution, or superpowers:subagent-driven-development
> if the operator selects that method. Steps use checkbox syntax for tracking.

**Goal:** освободить цикл событий бота от синхронных workflow/SSH вызовов,
сохранив владение SQLite одним потоком и завершение принятых операций.

**Architecture:** Один worker с собственной ограниченной FIFO очередью и одним
потоком executor. Явный async facade отделяет handlers от синхронного workflow;
handler lifetime owner обеспечивает drain до закрытия БД и Telegram session.

**Tech Stack:** Python 3.12.14, asyncio/concurrent.futures/sqlite3, существующий
aiogram 3.28.2, pytest и имеющиеся зависимости. Установка/обновление не требуется.

**Spec:** [согласованный design](../specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md).
Оператор подтвердил письменный design словом «подтверждаю» после commit b277154.
Статус этого плана: PLAN_READY_FOR_REVIEW / NOT_EXECUTED. Метод рекомендован inline,
но review плана и выбор метода ещё не получены. Это технический подплан одного
изменения, подчинённый [единому execution plan Phase16](2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md);
клиентские/live gates и их статусы здесь не дублируются.

## Global Constraints

- Baseline source: 2069e4147437067c08a7d3bde7361433179ac727; не deployed SHA.
- Source worktree: C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop.
- Ветка: codex/phase16-web-health-event-loop; ранее сделанный web fix сохраняется.
- Ровно один business job передан executor одновременно; outstanding jobs <= 8.
- SQLite create/use/close в одном потоке; check_same_thread=False не вводится.
- Меню с БД ждут очередь; не обещать мгновенный ответ при восьми занятых handlers.
- До dispatch отмена удаляет job; после dispatch метод завершается без auto retry.
- Shutdown завершает все принятые handlers, включая queued mutations и delivery record.
- Нет общего жёсткого drain timeout; external kill/crash/exactly-once не решаются.
- Не менять schema, freshness/admission policy, SSH timeout/retries/circuit breaker.
- AWG2_UNTOUCHED; package016 immutable; общая issuance не включается.
- Без VPS/Telegram/рабочей БД/configs, DefaultVPN delivery, package/stage/install.
- Каждый существенный source commit включает source CHANGELOG.md и exact-file staging.

## Review Focus

1. Отмены queued jobs при удерживаемом running job не накапливают отменённые
   объекты во внутренней очереди executor — Task 1, cancellation churn.
2. ContextVar разных callers не смешивается в общем worker — Task 1, per-call context.
3. Ошибка между connect и возвратом workflow закрывает SQLite в создавшем потоке — Task 2.
4. Повторная отмена root во время drain не освобождает instance lock раньше worker — Task 4.
5. Telegram send уже успешен, но delivery record вернул False/ошибку — Task 4;
   отсутствуют false success и повторная выдача/отправка.

## Файлы и интерфейсы

Пути исходников/тестов ниже относятся к source worktree, а не AMN3.

| Файл | Назначение |
| --- | --- |
| app/bot/workflow_worker.py, новый | Очередь, worker-owned resource, context, отмена, close; без aiogram/бизнес-решений |
| app/bot/async_workflow.py, новый | Явный facade, allowlist, адаптер BotWorkflow и материализация результатов |
| app/bot/handler_lifetime.py, новый | Владение handler tasks, ContextVar admission ticket, drain/middleware |
| app/bot/workflows.py | Опциональный resource_closer и идемпотентный close для созданного factory workflow |
| app/main.py | Exception-safe factory; в Task 4 подключение worker/lifetime в run_persistent_bot |
| app/bot/handlers.py, main.py, texts.py | Await facade, middleware и ответы partial/delivery failure; убрать raw bundle из dispatcher |
| tests/bot/test_workflow_worker.py, новый | Worker с Events, временной SQLite и наблюдением потоков |
| tests/bot/test_async_workflow.py, новый | Реальный workflow за facade и отказ от выдачи resource objects |
| tests/bot/test_handler_lifetime.py, новый | Отмена/лимит/drain изолированно от Telegram |
| tests/bot/test_bot_handlers.py, test_app_bootstrap.py | Интеграционные сценарии и миграция sync test doubles |
| tests/services/test_device_revoke.py | Существующая regression remote/local partial outcomes, без переписывания бизнес-логики |
| CHANGELOG.md | Проверенные изменения каждого source commit, limitations и результаты |

Фиксированные интерфейсы между задачами (private поля ниже не являются API):

- SyncWorkflowResource: синхронные invoke(method: str, args: tuple, kwargs: dict)
  -> object и close() -> None; объект создаётся factory исключительно в worker.
- JobOutcome: frozen dataclass с method: str и status: Literal["success", "error", "partial"].
  Не содержит exception/result/kwargs. outcome_sink(outcome: JobOutcome) -> None
  вызывается в event loop; его ошибка не ломает освобождение job/ресурса.
- WorkflowWorker(factory, *, allowed_methods: frozenset[str], capacity: int = 8,
  outcome_sink=None, error_status=None): async start() -> None, async call(method: str, /, *args,
  **kwargs) -> object, async aclose() -> None. capacity > 0; start только один раз;
  повторный aclose безопасен. error_status(exc: BaseException) -> Literal["error", "partial"]
  — доверенный классификатор, по умолчанию "error"; его сбой даёт "error" и не
  пропускает cleanup. WorkflowBusy и WorkflowClosed — собственные RuntimeError.
- make_workflow_resource(factory: Callable[[], BotWorkflow]) -> SyncWorkflowResource:
  создаёт workflow, возвращает adapter; вызывается worker factory, не event loop.
- AsyncBotWorkflow(worker: WorkflowWorker, *, guard: Callable[[], None]): все
  методы из 30-method manifest ниже async, с аргументами и результатами sync API;
  guard вызывается до enqueue. Разрешённые методы — WORKFLOW_METHODS: frozenset[str].
- HandlerLifetime(*, limit: int = 8): async run(handler: Callable[[], Awaitable[T]])
  -> T, begin_shutdown() -> None, require_active() -> None, async drain() -> None.
  require_active проверяет внутренний ticket действующего owned handler, не user data.
- WorkflowLifetimeMiddleware(owner: HandlerLifetime): aiogram BaseMiddleware,
  __call__(handler, event, data) ожидает owner.run для конкретного message/callback.
  Partial failure обрабатывается внутри owned task, до завершения её lifetime.
- await_owned_cleanup(cleanup: Awaitable[None]) -> None: создаёт и удерживает cleanup
  task, ждёт её при повторных cancel, затем возвращает CancelledError вызывающему.
  Исходная runtime ошибка сохраняется, cleanup failures не маскируют её молча.

## Команды, данные и checkpoints

Перед Task 1 сверить status/HEAD/worktrees и source remote; не reset/checkout старого
SHA. Уже существующая изоляция достаточна. Изменение baseline/чужой diff — остановка
и сверка, не автоматическое восстановление. Прочитать spec и этот план вместе.

Во всех тестах settings создаются с _env_file=None и синтетическими значениями;
VPS_APPLY_ENABLED=false, AWG3 bootstrap не включается. Network/peer boundaries
заменяются doubles. Events имеют защитные таймауты и освобождаются в finally;
таймауты тестов не становятся production SLA.

Для каждого указанного ниже pytest запуска использовать PowerShell из source cwd:

```powershell
$env:PYTHONPATH = 'C:\Users\SooL\Documents\Amneziya\.codex_deps'
$env:PYTHONDONTWRITEBYTECODE = '1'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/bot/test_workflow_worker.py -q --tb=short -p no:cacheprovider
```

В следующих шагах указан хвост команды (test paths/-k); launcher/флаги те же.
Перед первой правкой один baseline: tests/bot tests/services/test_device_revoke.py
 tests/services/test_phase15_bootstrap.py. Если baseline падает из-за среды,
зафиксировать UNKNOWN и разобраться, не менять зависимости попутно.

Каждая Task 1–4: RED → минимальная реализация → её GREEN → CHANGELOG → diff/check
→ exact-file commit → обычный push существующей source ветки. Не git add -A.
Source remote **amn2** должен указывать на https://github.com/barakov-dot/amn2.git;
origin в этом checkout может указывать на AMN3 и для source push не используется.
Перед push проверить remote/HEAD/ref и changelog всех новых commits, затем readback.
Документация AMN3 коммитится отдельно в её существующую ветку; force/tags запрещены.
Команды этого плана становятся исполняемыми после review, не заменяют live approval.

## Task 1: worker и ограниченная очередь

**Files:** создать app/bot/workflow_worker.py и tests/bot/test_workflow_worker.py;
изменить source CHANGELOG.md. Runtime ещё не подключается.
**Consumes:** только стандартная библиотека и синхронный resource factory.
**Produces:** WorkflowWorker, SyncWorkflowResource, JobOutcome, WorkflowBusy/Closed.

- [ ] Написать RED, начиная с настоящей thread-bound SQLite и медленного double:

```python
import asyncio
import sqlite3
import threading
from app.bot.workflow_worker import WorkflowWorker


def test_worker_keeps_sqlite_on_owner_and_leaves_loop_free():
    async def scenario():
        entered, release = threading.Event(), threading.Event()
        threads = []

        class Resource:
            def __init__(self):
                threads.append(threading.get_ident())
                self.conn = sqlite3.connect(":memory:")
                self.conn.execute("CREATE TABLE observations (value INTEGER)")
            def invoke(self, method, args, kwargs):
                threads.append(threading.get_ident())
                assert method == "save"
                entered.set()
                assert release.wait(5), "test gate was not released"
                self.conn.execute("INSERT INTO observations VALUES (?)", args)
                self.conn.commit()
                return self.conn.execute("SELECT value FROM observations").fetchone()[0]
            def close(self):
                threads.append(threading.get_ident())
                self.conn.close()

        worker = WorkflowWorker(Resource, allowed_methods=frozenset({"save"}))
        await worker.start()
        pending = asyncio.create_task(worker.call("save", 7))
        try:
            assert await asyncio.to_thread(entered.wait, 1)
            marker = await asyncio.wait_for(asyncio.sleep(0, result="alive"), 1)
            assert marker == "alive" and not pending.done()
            release.set()
            assert await pending == 7
        finally:
            release.set()
            await worker.aclose()
        assert len(set(threads)) == 1
        assert threads[0] != threading.get_ident()
    asyncio.run(scenario())
```

- [ ] RED этого файла: ожидается отсутствие нового модуля/API. Затем добавить
  независимые случаи: 1 удерживаемый + 7 queued, девятый WorkflowBusy; запрет
  неизвестного method до resource.invoke; queued cancel без invoke; cancel после
  dispatch с одним invoke; 100 queued cancel/replace при удерживаемом running job
  без роста submitted jobs; ContextVar двух callers с разными значениями;
  exception outcome и падающие outcome_sink/error_status не мешают следующему job/close.
- [ ] Реализовать собственный deque, отдельную pump task и executor(max_workers=1).
  State меняется только в event loop: NEW/OPEN/CLOSING/CLOSED; у job
  QUEUED/DISPATCHED/TERMINAL. В call копировать contextvars.copy_context и kwargs;
  pump не захватывает context caller вместо enqueue. После dispatch Future
  executor хранится отдельно от waiter и не отменяется.

```python
# Ветка отмены в call; queued — собственный deque, не executor._work_queue.
except asyncio.CancelledError:
    if job.state == "QUEUED":
        self._queued.remove(job)
        job.state = "TERMINAL"
        self._release_slot(job)
    raise
```

  _release_slot(job) определён в этом модуле: однократно уменьшает outstanding,
  отмечает released; повторное освобождение — внутренняя ошибка, не отрицательный
  счётчик. Pump пропускает отменённый waiter только при выдаче результата, но
  всегда наблюдает terminal error и освобождает слот в finally. Синхронные factory,
  invoke и close выполняются через один executor; Future ждётся shield. aclose
  закрывает admission, дожидается pump/jobs, запускает resource.close там же и
  await-ит shutdown executor вне event loop. Factory failure/close failure не
  пропускают executor shutdown. Без объектов SQLite/секретов в outcome_sink.
- [ ] GREEN: tests/bot/test_workflow_worker.py. Проверить create/use/close thread ID,
  очередь/cancellation churn/context/failure; не утверждать business integration.
- [ ] Записать результаты в CHANGELOG и commit: feat: add owned sequential workflow worker.

## Task 2: managed factory, materialization и явный facade

**Files:** создать app/bot/async_workflow.py, tests/bot/test_async_workflow.py;
изменить app/main.py:create_workflow, app/bot/workflows.py:BotWorkflow.__init__,
tests/bot/test_app_bootstrap.py, CHANGELOG.md. Dispatcher пока использует старый путь.
**Consumes:** Task 1 worker API; существующий BotWorkflow.
**Produces:** WORKFLOW_METHODS, make_workflow_resource, AsyncBotWorkflow и close.

- [ ] RED на factory failure: monkeypatch main.connect возвращает временную SQLite
  с записанным thread ID; initialize_schema выбрасывает тестовый RuntimeError;
  после factory failure conn.execute должен дать ProgrammingError (closed),
  close выполнен в owner thread. Параметризовать failure на initialize_schema,
  seed_default_plans и BotWorkflow constructor. Успешная factory не закрывает
  connection до явного close; внешний Repository без resource_closer не закрывается.
- [ ] Добавить BotWorkflow(resource_closer: Callable[[], None] | None = None) и
  идемпотентный close. В create_workflow защитить существующую сборку ExitStack,
  зарегистрировать conn.close сразу после connect; передать resource_closer
  конструктору и снять cleanup только перед успешным return. Пример ядра:

```python
def close(self) -> None:
    closer, self._resource_closer = self._resource_closer, None
    if closer is not None:
        closer()
```

  self._resource_closer задаётся в __init__. Инициализация может упасть до/внутри
  конструктора — ответственность factory/ExitStack, не __del__. Не реорганизовывать
  весь app/main.py или Repository ради этой правки.
- [ ] Создать adapter с явной таблицей bound methods из manifest; invoke берёт
  только значение таблицы, а не произвольный getattr. Сразу материализовать
  sqlite3.Row в dict, вложенные list/tuple/dict рекурсивно; DTO с уже материализованными
  полями сохраняют тип. Cursor/connection/repo/service/generator не разрешены.
  Проверки результата не должны печатать его repr или менять бизнес-параметры.
- [ ] Добавить facade с 30 явными async методами. Аргументы/defaults копируются из
  существующих одноимённых sync методов на baseline; _call сначала guard(), затем
  await worker.call. Это механическая смена boundary, не новая validation policy:

```python
async def revoke_user_device(self, *, telegram_id: int, device_id: int,
                             revoked_at: str | None = None) -> bool:
    self._guard()
    return await self._worker.call(
        "revoke_user_device", telegram_id=telegram_id,
        device_id=device_id, revoked_at=revoked_at,
    )
```

  Manifest (не добавлять list_awg3_client_choices/set_config_ready_template без
  найденного bot caller):

```text
is_admin, is_configured_admin, request_awg3, confirm_awg3, issue_admin_config,
record_admin_config_delivery, build_admin_config_handoff_for_device,
register_user, set_user_locale, get_user_locale, request_access,
create_manual_user, create_manual_access_request, grant_admin,
list_active_plans, build_user_traffic_views, list_user_devices,
build_admin_traffic_views, list_pending_orders, get_operator_status,
get_operator_server_statuses, get_operator_credential_statuses, list_users,
approve_order, get_config_ready_template, reset_config_ready_template,
build_resend_delivery, build_user_resend_delivery, revoke_user_device,
reset_user_devices
```

- [ ] RED/GREEN для реального workflow с _env_file=None, временной БД и synthetic
  settings. Внутри разрешённого test guard зарегистрировать пользователя, запросить
  list_user_devices/планы, проверить результаты и отказ не-admin в admin методе.
  Guard failure не вызывает resource.invoke. Проверить snapshot после close ресурса:

```python
def test_snapshot_survives_connection_close():
    import sqlite3
    from app.bot.async_workflow import snapshot_result
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    value = snapshot_result([conn.execute("SELECT 1280 AS mtu").fetchone()])
    conn.close()
    assert value == [{"mtu": 1280}]
```

  snapshot_result(value: object) -> object — внутренний helper adapter, не новый
  формат выдачи. Дополнительно отказ на conn/cursor и сохранение config bytes без
  логирования; существующие dataclasses результата не превращаются в произвольный dict.
- [ ] GREEN: новые worker/facade файлы + tests/bot/test_app_bootstrap.py и
  tests/bot/test_bot_workflows.py. CHANGELOG/commit: feat: add async bot workflow boundary.

## Task 3: lifetime принятых handlers

**Files:** создать app/bot/handler_lifetime.py, tests/bot/test_handler_lifetime.py;
CHANGELOG.md. Middleware/owner готовы, runtime пока не переключён.
**Consumes:** WorkflowBusy/Closed из Task 1; публичный aiogram middleware API.
**Produces:** HandlerLifetime, WorkflowLifetimeMiddleware, await_owned_cleanup.

- [ ] RED: owned handler имитирует send, ждёт Event, затем фиксирует delivery;
  cancellation родительской task не отменяет этот handler; begin_shutdown запрещает
  новое run; drain не заканчивается до record. Все helpers показаны в тесте:

```python
def test_parent_cancel_keeps_accepted_delivery_alive():
    import asyncio
    from app.bot.handler_lifetime import HandlerLifetime
    from app.bot.workflow_worker import WorkflowClosed
    import pytest
    async def scenario():
        owner = HandlerLifetime()
        sent, allow_record = asyncio.Event(), asyncio.Event()
        events = []
        async def delivery():
            events.append("sent")
            sent.set()
            await allow_record.wait()
            owner.require_active()
            events.append("recorded")
        parent = asyncio.create_task(owner.run(delivery))
        await sent.wait()
        parent.cancel()
        with pytest.raises(asyncio.CancelledError):
            await parent
        owner.begin_shutdown()
        drain = asyncio.create_task(owner.drain())
        try:
            with pytest.raises(WorkflowClosed):
                await owner.run(delivery)
            await asyncio.sleep(0)
            assert not drain.done()
            allow_record.set()
            await asyncio.wait_for(drain, 1)
            assert events == ["sent", "recorded"]
        finally:
            allow_record.set()
            await owner.drain()
    asyncio.run(scenario())
```

- [ ] Реализовать atomic admission (проверка closing/limit и регистрация task без
  await между ними), собственные сильные ссылки и ContextVar ticket, принадлежащий
  owner. В owned task установить ticket, вызвать handler, затем очистить ticket и
  регистрацию в finally. Внешний await идёт через shield; done callback извлекает
  ошибки осиротевших tasks безопасно, без exception args/traceback с секретами.
  require_active принимает только ticket в текущем registry этого owner, включая
  DRAINING; после handler exit и для посторонней task/ticket — WorkflowClosed.
  Контекст ticket не даёт дочерней неучтённой task обходить ограничение: связать
  ticket с asyncio.current_task() owned handler, а не только с ContextVar.
  Ядро run; _tasks=set(), _tickets=dict(), _ticket=ContextVar(default=None),
  _closing=False и _limit задаются в __init__:

```python
async def run(self, handler):
    if self._closing:
        raise WorkflowClosed()
    if len(self._tasks) >= self._limit:
        raise WorkflowBusy()
    ticket = object()
    async def owned():
        token = self._ticket.set(ticket)
        try:
            return await handler()
        finally:
            self._ticket.reset(token)
    task = asyncio.create_task(owned())
    self._tasks.add(task)
    self._tickets[ticket] = task
    task.add_done_callback(lambda done: self._on_done(ticket, done))
    return await asyncio.shield(task)
```

  _on_done(ticket, task) удаляет оба registry entries, вызывает task.exception()
  только для не-cancelled task; для orphaned failure пишет фиксированный logging
  marker bot_handler_failed без str/repr exception, args и traceback.
  drain await-ит снимок _tasks, пока registry не пуст; admission закрывается перед
  drain. Middleware использует return await owner.run(lambda: handler(event, data)).
- [ ] Для await_owned_cleanup создать одну task, ожидать shield в цикле после
  повторных CancelledError; наблюсти исход task и только затем вернуть отмену.
  Переданный Awaitable оборачивается coroutine, чтобы принимать и Future:

```python
async def await_owned_cleanup(cleanup):
    async def finish():
        await cleanup
    owned = asyncio.create_task(finish())
    cancelled = False
    while not owned.done():
        try:
            await asyncio.shield(owned)
        except asyncio.CancelledError:
            cancelled = True
    owned.result()
    if cancelled:
        raise asyncio.CancelledError()
```

  Сама cleanup coroutine не должна отменять себя; её ошибка остаётся наблюдаемой.
  При одновременных primary runtime и cleanup ошибках вызывающий run_persistent_bot
  поднимает BaseExceptionGroup с обеими причинами вместо потери одной; в tests
  сверять типы/идентичность, не тексты secrets. Не применять asyncio.run внутри
  библиотечного API и не читать private _handle_update_tasks.
- [ ] Дополнительные RED/GREEN: 8 accepted + отказ девятому; injected/forked stale
  ticket отвергнут; raise handler не мешает drain; begin_shutdown/два drain
  идемпотентны; двукратная cancel ожидающего cleanup всё равно дожидается Event.
  Тесты используют только asyncio Events и fake handler, не Telegram API.
- [ ] GREEN: tests/bot/test_handler_lifetime.py + tests/bot/test_workflow_worker.py.
  CHANGELOG/commit: feat: track accepted bot handlers through shutdown.

## Task 4: подключить и проверить bot runtime

**Files:** app/main.py:run_persistent_bot; app/bot/main.py, handlers.py, texts.py;
app/bot/handler_lifetime.py (middleware domain replies); tests/bot/test_bot_handlers.py,
tests/bot/test_app_bootstrap.py, tests/bot/test_async_workflow.py; CHANGELOG.md.
**Consumes:** все API Tasks 1–3. **Produces:** единственный persistent bot path с
worker-owned workflow; sync service/CLI callers по-прежнему используют sync factory.

- [ ] RED интеграции: реальный временный Repository и fake peer remover удерживают
  revoke; независимая coroutine/watchdog проходит до release, следующий reset ждёт.
  Существующие workflow тесты дают бизнес-ожидания: после release локальные строки
  имеют прежние статусы, remote вызовы ровно по одному, авторизация проверена при
  исполнении. Это тест поведения, не проверка наличия слова await в исходнике.
- [ ] Перевести все 41 call sites handlers.py на await и явный AsyncBotWorkflow.
  Sync test doubles переводятся на async def с прежними возвращаемыми значениями,
  без универсального адаптера sync-or-async в production. Пример исходящего пути:

```python
recorded = await workflow.record_admin_config_delivery(
    admin_telegram_id=admin_telegram_id,
    passport_device_id=result.passport_device_id,
    delivered=True,
    reference=f"telegram_message:{message_id}",
)
if not recorded:
    await message.answer(text("handler.delivery_record_failed"))
    return
await message.answer(success_text)
```

  Сохранить существующий fallback reference при отсутствии message_id; обработать
  также исключение записи и send failure без ложного success. Не повторять send
  или issue. text("handler.delivery_record_failed") ru:
  «Не удалось сохранить результат доставки. Нужна проверка администратором»;
  en: «Could not save the delivery result. Administrator review is required.»
- [ ] Middleware обрабатывает RemoteOperationPartialFailure внутри owned task,
  отправляет безопасный ru/en текст из spec, не re-raises его в сырой aiogram logger.
  PeerApplyError/остальные предусмотренные domain ответы сохраняются. WorkflowBusy
  сообщает отказ текущего шага без обещания rollback предыдущих шагов; WorkflowClosed
  не допускает новый job. Добавить ru/en keys через существующий texts.py.
- [ ] create_dispatcher получает facade и lifetime явно; middleware регистрируется
  на message/callback streams. Удалить экспорт raw phase15_awg3_components в
  dispatcher context; tests проверяют отсутствие raw Repository/bundle и тот же
  routing. Sync factory сохраняет bundle внутри workflow для services.
- [ ] run_persistent_bot: admission → await worker.start с factory замыканием →
  dispatcher(facade, lifetime) → state recheck → polling → READY/watchdog. Factory
  замыкание вызывает make_workflow_resource(lambda: workflow_factory(settings)),
  без открытой БД в event loop. guard facade = lifetime.require_active;
  error_status(exc) возвращает "partial" только для isinstance(exc,
  RemoteOperationPartialFailure), иначе "error". Никаких проверок по str(exc).
- [ ] В finally закрыть lifetime admission до остановки polling; выполнить единый
  учитываемый cleanup с порядком stop polling/watchdog → lifetime.drain →
  worker.aclose → bot.session.close → instance lock exit. Nested finally не
  пропускают следующие ресурсы при close error. Startup timeout запускает cleanup
  даже при ещё работающей factory, но не READY. Не закрывать Telegram session в
  start_polling: close_bot_session=False сохраняется.
- [ ] RED/GREEN matrices, с assert по порядку Events, а не wall-clock benchmark:
  admission failure; schema/factory failure; startup timeout после dispatch factory;
  recheck failure; polling early-return/error; watchdog error; root cancel + повторная
  cancel; shutdown при busy SSH; новое сообщение после closing; send→record drain;
  запись False и exception после send; RemoteOperationPartialFailure с sentinel
  secret в cause отсутствует в ответах/новых diagnostics. В каждом исходе не больше
  одного close, lock exit после последнего SQL/record, нет новых remote/send retries.
- [ ] Итоговый GREEN один раз: tests/bot tests/services/test_device_revoke.py
  tests/services/test_phase15_bootstrap.py, с launcher выше. Сравнить с baseline;
  предупреждения отделить от ошибок. Общий repository suite и web retest не нужны,
  если новые изменения/ошибки не затронули их. Не изменять tests ради скрытия failure.
- [ ] CHANGELOG/commit: fix: keep bot event loop responsive during workflow operations.
  Указать реальные RED/GREEN результаты, оставшиеся границы и отсутствие deployment.

## Завершение, review и handoff

- [ ] По окончании кода провести один независимый read-only review всего диапазона
  source 2069e41..HEAD: ownership, queue/cancel races, drain/startup, auth/data
  boundary, partial failure/delivery. При inline выполнении reviewer не реализует
  соседние задачи; режим/модель выбираются по применимому review skill, без смены
  модели текущей задачи. Это будущий review, сейчас subagents не запускаются.
- [ ] Исправить подтверждённые findings через целевой RED/GREEN; повторять только
  затронутые проверки и расширять при доказанной необходимости. Если review требует
  изменения согласованного контракта (параллельность, recovery, новая схема, отмена
  remote), остановиться перед этим изменением и предъявить конкретное отличие.
- [ ] Финальный diff/whitespace, exact staged files, CHANGELOG; source HEAD/remote
  readback и clean status. Не merge/deploy автоматически и не удалять worktree.
- [ ] В AMN3 обновить существующий SSH receipt, этот checklist и main plan,
  CHANGELOG с фактическими результатами; ссылки/readback/diff без повторного pytest.
  Не превращать локальный PASS в Phase16 acceptance или live approval.

## Self-review и следующий шаг

Покрытие spec: ownership/API → Tasks 1–2; FIFO/bounds/context/cancel → Task 1;
accepted handlers/drain → Tasks 3–4; startup/factory → Tasks 2/4; partial/delivery
→ Task 4; совместимость → baseline и итоговый relevant set Task 4. Все пять Review
Focus привязаны к конкретным тестам. Имена публичных API согласованы между задачами;
helper snapshot_result и приватный _release_slot определены в соответствующих tasks.

План ещё не выполнялся; source AMN2 остаётся 2069e41. Следующий шаг — review этого
плана и выбор метода. Рекомендован inline/native: четыре задачи тесно связаны
lifetime/API, один исполнитель сохраняет контекст; независимый review в конце.
Альтернатива — отдельные исполнители/reviewers на каждую задачу с большей затратой
контекста. Ни один способ не разрешает live-действия или обход acceptance gates.
