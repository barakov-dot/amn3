# AMN2 Bot Startup/Stop Lifecycle — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task, inline, одним агентом. Steps use checkbox
> syntax for tracking. Не запускать subagents/reviewers и не менять модель.

**Goal:** закрыть startup signal gap и сохранить принятый drain без ложного
обещания конечного stop budget или доказанного восстановления.

**Architecture:** Один StopController и scoped process-signal adapter принимают
stop до создания app resources. Runtime закрывает admission и проходит прежний
owned cleanup; startup-only guard в worker запрещает ещё не dispatched factory,
не запрещая продолжения уже принятых handlers.

**Tech Stack:** CPython 3.12.14, asyncio/threading/signal, pinned aiogram 3.30.0,
pytest из сохранённой M3 venv; стандартный SQLite thread guard, без новых dependencies.

**Spec:** [lifecycle design A](../specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#lifecycle-design-m4).
Оператор ответил «Подтверждаю» на письменный design из AMN3 commit
8ba7e5d31236824bddd304a4f278965029d1578b. Это утвердило design и подготовку плана.
Статус плана: **SOURCE_IMPLEMENTED_WINDOWS_TESTED / LINUX_SIGNAL_UNKNOWN**.
Исполнение согласовано оператором «в части ожидания подтверждения, подтверждаю».
Tasks 1–2 реализованы; Task 3 не принят. После отдельного server approval
[попытка 21.09](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#execution-2026-09-21)
вернула UNKNOWN_NO_RETRY/process_io; negative/6signals не подтверждены.
Нижние NOT_RUN/запрет install описывают исходный local-only этап; последующее
разрешение одной isolated test-venv попытки использовано и не разрешает retry.
[Actual evidence](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-implementation-m4-2026-09-21), AMN2 6e68235. Inline method
сохраняется из ограничений Phase16; отдельный выбор делегирования не нужен.
Подплан подчинён [главному Phase16 plan](2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md),
не является вторым execution status и не возобновляет выполненный worker plan.

## Global Constraints

- AMN2 baseline: 1bd7f62d1fdd3829bc278110ecdc44d3568676a3, ветка codex/phase16-web-health-event-loop.
- Source: C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop.
- AMN3 docs: C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB; detached state сохранить.
- Сверить HEAD/status перед исполнением; при чужом diff/drift не reset/stash/clean.
- H=8 accepted handlers; Q=8 outstanding jobs; один submitted workflow job.
- После stop новых handlers 0; принятые сохраняют право на последующие jobs/send/record.
- Не менять facade/handlers/business services/schema, SSH/Telegram timeouts, retries,
  lock/dependency files, web/API/agent, units или production max_devices/reset policy.
- AWG2_UNTOUCHED; package016 immutable; general issuance disabled.
- Нет VPS/SSH/Telegram API, рабочих DB/configs, stage/install/deploy, package build,
  реальной выдачи, автоматического cleanup, live signals/restarts или durable outbox.
- Stop budget UNKNOWN. M3 target, M4 writer/restart/bulk gates и M1/M2/M5/M6/M7 открыты.
- Прежние 33/312 и M3 68 PASS не повторять baseline-прогоном. RED/GREEN относятся
  к новому поведению; один итоговый affected набор после изменения.
- Нет dependency install, WSL/Docker/Linux setup, global config/skills/memory changes.
- Каждый substantive AMN2 commit содержит AMN2 CHANGELOG; AMN3 sync — свой CHANGELOG.

## Review Focus

1. Сигнал до loop/bind не теряется: до Settings и factory нет side effect — Task 1 pre-attach latch, Task 2 pre-resource stop.
2. Ошибка второй регистрации/первого restore не оставляет чужой signal handler заменённым — Task 1 partial-install/restore failure.
3. Stop и external cancellation приходят вместе: только собственная cancellation может стать normal stop; errors не теряются — Task 1 ownership, Task 2 combined errors.
4. Stop побеждает factory dispatch/READY, но не запрещает record принятому handler — Task 2 ordered-race и send→record tests.
5. Signal test не может остановить службу/соседний процесс либо выдать skip за Linux PASS — Task 3 exact child, barrier, caps и отдельный NOT_RUN.

## Files и контракт интерфейсов

Пути ниже относительно AMN2. Baseline line numbers — ориентиры, не патч по номерам.

| Файл | Роль |
| --- | --- |
| Create app/bot/lifecycle.py | StopController и ProcessSignalScope; нет побочных эффектов при import |
| Modify app/main.py:41–172,445–446 | main wrapper до asyncio.run/Settings; передача controller; startup checkpoints; handle_signals=False; прежний cleanup |
| Modify app/bot/workflow_worker.py:44–78 | Необязательный startup-only factory guard непосредственно перед executor submit |
| Create tests/bot/test_lifecycle.py | Controller/adapter unit tests, fake signal registry, без OS signals хосту |
| Modify tests/bot/test_workflow_worker.py | Stop-first/dispatch-first regression; сохранение FIFO/close contracts |
| Modify tests/bot/test_app_bootstrap.py | Runtime wiring/registration order/kwargs; reusable fakes сохранить |
| Modify tests/bot/test_bot_runtime_worker.py | Stop на стадиях, accepted work, send/record и error races |
| Create tests/bot/test_lifecycle_signals.py | Linux-only parent/child signal acceptance |
| Create tests/bot/lifecycle_signal_child.py | Synthetic disposable child, только allowlisted trace и fake resources |
| Modify CHANGELOG.md | Причина, actual RED/GREEN, пределы; в каждом существенном commit |

Stable interfaces, определяются в Task 1 и используются без переименования:

| API | Точный контракт |
| --- | --- |
| StopController() | Новый owner, requested=False; не ставит OS handlers |
| requested: bool | True только после обработки stop в loop; monotonic |
| failure: BaseException \| None | Неожиданная ошибка close_admission, сохраняется для supervisor; без raw логирования |
| notify_signal() -> None | OS adapter entry: до attach сохраняет pending, после attach ставит request_stop через call_soon_threadsafe; без DB/network/cleanup |
| attach(loop: asyncio.AbstractEventLoop) -> None | Привязка к единственному loop; pending применить до app resources; чужой/repeated concurrent attach — RuntimeError |
| detach() -> None | Убрать ссылку на loop/owner после cleanup; queued callbacks после detach не трогают прежний runtime |
| request_stop() -> None | Loop-owned idempotent latch; немедленно close admission, один owner cancellation request вне cleanup |
| bind(task: asyncio.Task, close_admission: Callable[[], None]) -> ContextManager[None] | Не терять уже requested stop; не разрешать два owners; finally снимает owner после resource cleanup |
| begin_cleanup() -> None | Пометить cleanup; первый/повторный stop в этой фазе не делает новую root.cancel |
| raise_if_requested() -> None | При latch поднимает cancellation с private owner token; до side effects |
| owns_cancellation(exc: asyncio.CancelledError, task: asyncio.Task) -> bool | True только для этого private token и доказанно собственной cancellation без внешних cancel requests; иначе False |
| ProcessSignalScope(controller, *, get_handler=signal.getsignal, set_handler=signal.signal) | Context manager устанавливает SIGTERM/SIGINT до loop, сохраняет/восстанавливает оба previous handlers, injectable registry для tests |
| WorkflowWorker(..., factory_start_allowed: Callable[[], bool] \| None = None) | Default сохраняет старый API; guard проверяется только перед factory submit |
| run_persistent_bot(settings, ..., stop_controller: StopController \| None = None) -> None | Existing injection API сохраняется; controller не ставит OS handlers; default создаёт scoped local controller |
| main(*, runtime: Callable[[StopController], Awaitable[None]] \| None = None) -> None | Default вызывает run; synthetic child может передать fake runtime; ProcessSignalScope снаружи asyncio.run |

run сохраняет возможность вызова без аргументов: run(stop_controller=None).
Process-level signal guarantee относится к штатному main(), а не к произвольному
embedded caller. Embedded run/run_persistent_bot получают явный controller или
обычную coroutine cancellation; они не меняют глобальные signal handlers.

## Среда, команды и бюджеты будущих tests

Команды ниже — утверждённый шаблон. Actual argv/results и отклонения от caps
сохранены в receipt/JSON выше; Linux-only команды не запускались.

Существующий Python:
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-dependency-validation-20260921-1bd7f62/venv/Scripts/python.exe.
Binding: [M3 receipt](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#dependency-validation-2026-09-21)
и [versions/wheel hashes](../../../research/amn2/phase16-web-bot-dependency-validation-2026-09-21.json).
Перед первым новым тестом проверить existence/pyvenv.cfg, версии и locks read-only;
mismatch означает STOP без переустановки. Scratch для новых evidence:
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-lifecycle-validation-20260921.
Если уже существует, сохранить содержимое и выбрать новый пустой run directory.

Шаблон argv (в каждом task ниже указан точный selector):

~~~powershell
$phase16Python = 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-dependency-validation-20260921-1bd7f62/venv/Scripts/python.exe'
$phase16Source = 'C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop'
& $phase16Python -I -B -c 'import sys; sys.path.insert(0, sys.argv.pop(1)); import pytest; raise SystemExit(pytest.main(sys.argv[1:]))' $phase16Source tests/bot/test_lifecycle.py -q --tb=short --maxfail=1 -p no:cacheprovider
~~~

Для actual run использовать parent supervisor с argv list, cwd=source,
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, PYTHONDONTWRITEBYTECODE=1,
VPS_APPLY_ENABLED=false и ограниченным system/temp launch environment.
Не наследовать application secrets/PYTHONPATH/PYTHONHOME/PIP config. В synthetic
Settings всегда _env_file=None; network adapters всегда fake.
Output/JUnit/basetemp — отдельные paths в scratch, не в source Git.

| Запуск | Parent wall cap | Output cap | Stop |
| --- | --- | --- | --- |
| Один новый RED selector | 60s | 128 KiB | maxfail=1, одна диагностированная ожидаемая failure |
| Task-local GREEN | 90s | 128 KiB | первая failure/cap, без автоматического rerun |
| Итоговый affected набор | 180s | 256 KiB | первая failure/cap, один прогон после изменений |
| Один Linux synthetic child | 10s, внутри parent cap | 64 фиксированных trace records, 16 KiB | только exact child terminate/kill/wait в finally; cap не PASS |

Это лимиты test harness, не stop SLA приложения. Supervisor проверяет deadline и
размер output, останавливает только созданный им test process при превышении,
записывает FAIL/UNKNOWN. Каждый fake blocking wait имеет предел 5s и release
в finally; signal child дополнительно сам прекращает synthetic probe после 10s.
Процессные IDs берутся из Popen handles, не из поиска по имени/порту.
Не скрывать hangs через pytest skip. Для Linux child отсутствие подходящей среды
фиксируется отдельно; нет скачивания образа, включения WSL или SSH.

## Task 1: StopController и scoped signal adapter

**Files:** app/bot/lifecycle.py (new), tests/bot/test_lifecycle.py (new), CHANGELOG.md.
**Consumes:** стандартная библиотека; app services/Settings не импортировать.
**Produces:** controller/scope API из таблицы выше.

- [x] **1. RED:** добавить следующий сценарий pre-attach latch. Он должен упасть
  из-за отсутствующего lifecycle API, а не отсутствующих dependency/config.

~~~python
def test_signal_before_attach_is_retained():
    import asyncio
    from app.bot.lifecycle import StopController

    stop = StopController()
    stop.notify_signal()
    async def scenario():
        stop.attach(asyncio.get_running_loop())
        try:
            assert stop.requested
            assert not stop.owns_cancellation(asyncio.CancelledError("external"),
                                              asyncio.current_task())
        finally:
            stop.detach()
    asyncio.run(scenario())
~~~

- [x] **2. Запустить RED selector:** tests/bot/test_lifecycle.py::test_signal_before_attach_is_retained.
  Сохранить actual exit/result; не считать collection failure от среды ожидаемым RED.

- [x] **3. Реализовать controller** с private cancellation token. attach/request_stop/
  bind сериализованы loop; notify_signal только доставляет событие. Основной
  transition внутри request_stop после проверки loop identity:

~~~python
if self._requested:
    return
self._requested = True
try:
    if self._close_admission is not None:
        self._close_admission()
except BaseException as exc:
    self._failure = exc
finally:
    if self._task is not None and not self._cleaning and not self._task.done():
        self._external_cancel_seen |= self._task.cancelling() != 0
        self._cancel_sent = self._task.cancel(self._cancel_token)
~~~

  Инициализировать все показанные поля в constructor. owns_cancellation сравнивает
  token по identity, флаг external cancel и фактический task.cancelling count;
  не использовать только stop.requested. При explicit raise_if_requested без
  task.cancel учитывать zero count отдельно; при >1 cancel не подавлять ошибку.
  Если close_admission неожиданно падает, сохранить ошибку и всё равно инициировать
  owner cleanup, не оставлять полузакрытый live runtime.
  detach инвалидирует callbacks и очищает owner; не допускать повторного использования
  controller для новой runtime generation.

- [x] **4. Реализовать ProcessSignalScope** на signal.signal для main thread.
  __enter__ сохраняет старое значение непосредственно перед каждой установкой;
  callback вызывает controller.notify_signal(). При partial install восстановить
  уже изменённые signals. __exit__ пытается восстановить каждый изменённый signal,
  даже если предыдущий restore упал. Сохранить body/install error вместе с restore
  errors через BaseExceptionGroup, не заменять исходную ошибку последней ошибкой.
  При registration failure runtime/Settings не стартуют.

~~~python
def test_partial_install_restores_first_signal():
    import signal
    import pytest
    from app.bot.lifecycle import ProcessSignalScope, StopController

    previous = {signal.SIGTERM: object(), signal.SIGINT: object()}
    registry = dict(previous)
    def set_handler(signum, handler):
        if signum == signal.SIGINT and handler is not previous[signum]:
            raise ValueError("synthetic registration failure")
        registry[signum] = handler
    with pytest.raises(ValueError, match="synthetic registration failure"):
        with ProcessSignalScope(StopController(),
                                get_handler=registry.__getitem__,
                                set_handler=set_handler):
            pytest.fail("runtime must not start")
    assert registry == previous
~~~

- [x] **5. Добавить параметризованные случаи** в этот же файл: два notify после bind
  дают один close/cancel; pending до bind даёт close и запрет startup; первый stop
  во время begin_cleanup не отменяет root; external cancel до/после собственного
  не распознаётся как normal stop; callback после detach не трогает старый owner;
  ошибка первого restore не мешает второму. Использовать counter lists и fake
  registry как выше; в host process не отправлять OS signals.
- [x] **6. GREEN:** tests/bot/test_lifecycle.py. Проверить no unhandled task errors,
  module import не устанавливает handlers, public API совпадает с таблицей.
- [x] **7. Commit:** source CHANGELOG с actual результатом; exact files выше.
  Suggested message: feat(bot): add scoped stop controller and signal ownership.
  При intermediate API mismatch остановиться и исправить этот task до wiring.

## Task 2: Runtime wiring, factory fence и сохранение drain

**Files:** app/main.py, app/bot/workflow_worker.py,
tests/bot/test_workflow_worker.py, tests/bot/test_app_bootstrap.py,
tests/bot/test_bot_runtime_worker.py, CHANGELOG.md.
**Consumes:** Task 1 API. **Produces:** main/runtime APIs и factory_start_allowed.

- [x] **1. RED factory fence:** добавить тест ниже к существующим worker regressions.

~~~python
def test_stop_guard_prevents_factory_submit():
    import asyncio
    import pytest
    from app.bot.workflow_worker import WorkflowClosed, WorkflowWorker

    async def scenario():
        calls = []
        worker = WorkflowWorker(lambda: calls.append("factory"),
                                allowed_methods=frozenset(),
                                factory_start_allowed=lambda: False)
        try:
            with pytest.raises(WorkflowClosed):
                await worker.start()
        finally:
            await worker.aclose()
        assert calls == []
    asyncio.run(scenario())
~~~

- [x] **2. RED selector:** tests/bot/test_workflow_worker.py::test_stop_guard_prevents_factory_submit.
  Затем добавить необязательный constructor argument/field; guard проверяется
  только в _open_resource непосредственно после существующей OPEN проверки:

~~~python
if self._factory_start_allowed is not None and not self._factory_start_allowed():
    raise WorkflowClosed("Workflow stopped before factory dispatch")
self._resource = await asyncio.get_running_loop().run_in_executor(
    self._executor, self._factory)
~~~

  Между guard и submit нет await. Не менять call/_pump/_close contracts.
  Добавить dispatch-first case с threading.Event: await entered, stop latch,
  assert resource/lock ещё не закрыты, release finally; factory/close ровно один
  раз на одном потоке. Existing close-before-dispatch test сохранить.

- [x] **3. RED runtime stop на admission:** использовать уже существующие helpers;
  ниже полный минимальный сценарий. Новый optional runtime argument ещё отсутствует,
  поэтому ожидается failure этого нового contract.

~~~python
def test_stop_at_admission_does_not_start_factory(tmp_path):
    import asyncio
    import pytest
    from app.bot.lifecycle import StopController
    from app.main import run_persistent_bot
    from tests.bot.test_app_bootstrap import (
        _FakePersistentBot, _FakeNotifier, _RecordingLock, _persistent_settings)

    async def scenario():
        events = []
        stop = StopController()
        stop.attach(asyncio.get_running_loop())
        async def admission(bot, config):
            stop.request_stop()
            await asyncio.sleep(0)
        try:
            with pytest.raises(asyncio.CancelledError):
                await run_persistent_bot(
                    _persistent_settings(tmp_path), stop_controller=stop,
                    bot_factory=lambda **kw: _FakePersistentBot(events),
                    workflow_factory=lambda settings: events.append("factory"),
                    admission_checker=admission,
                    notifier=_FakeNotifier(events),
                    lock_factory=lambda path: _RecordingLock(events),
                    receipt_writer=lambda value: events.append("receipt"))
            assert "factory" not in events and "receipt" not in events
            assert events[-2:] == ["session_close", "lock_exit"]
            assert not any(isinstance(e, tuple) and e[0] == "ready" for e in events)
        finally:
            stop.detach()
    asyncio.run(scenario())
~~~

- [x] **4. RED selector:** tests/bot/test_bot_runtime_worker.py::test_stop_at_admission_does_not_start_factory.
  Подключить lifetime/owner binding до lock/client, но ресурсы закрывать лишь
  после фактического создания. При injected controller не повторять attach/detach;
  default runtime controller создаёт и снимает собственный loop scope. bind
  охватывает весь lock scope, finally снимает owner после lock release.
  Checkpoints: до lock, client, admission, worker.start, dispatcher/recheck,
  polling task, после polling yield и перед receipt/READY.
  Worker получает factory_start_allowed=lambda: not stop.requested.

~~~python
stop.raise_if_requested()
polling_task = asyncio.create_task(dispatcher.start_polling(
    bot,
    polling_timeout=settings.telegram_polling_timeout_seconds,
    allowed_updates=list(PERSISTENT_ALLOWED_UPDATES),
    close_bot_session=False, handle_signals=False,
    handle_as_tasks=True,
    tasks_concurrency_limit=PERSISTENT_TASKS_CONCURRENCY_LIMIT))
~~~

  В existing finally сначала stop.begin_cleanup() и lifetime.begin_shutdown().
  Сохранить порядок cancel watchdog/polling → lifetime.drain → worker.aclose →
  session.close → lock release и await_owned_cleanup. Нельзя вызывать worker.aclose
  в stop callback: это сломает record у принятых handlers.
  ready receipt/READY не имеют await между финальной проверкой и вызовами.
  Runtime сам не подавляет cancellation; нормализация — только в executable wrapper.

- [x] **5. Добавить main wrapper** с ProcessSignalScope до asyncio.run и Settings.
  Внутренний awaitable supervisor привязывает loop, проверяет pending stop ДО вызова
  runtime, после возврата/ошибки снимает loop. Только owns_cancellation=True
  подавляет CancelledError; любые другие ошибки/ExceptionGroup идут наружу.
  После runtime cleanup проверяется stop.failure: если есть, поднять её, а при
  одновременной runtime/cleanup ошибке сохранить обе через BaseExceptionGroup.
  Даже owned cancellation при failure не даёт success.
  run(stop_controller=None) по-прежнему создаёт Settings и вызывает runtime,
  но делает pre-Settings checkpoint. У __main__ заменить asyncio.run(run()) на main().
  Порядок wrapper:

~~~python
stop = StopController()
with ProcessSignalScope(stop):
    asyncio.run(supervise(stop, runtime or run))
~~~

  supervise — приватная async функция app/main.py с аргументами controller и
  Callable[[StopController], Awaitable[None]], attach/try-await/classify/finally-detach
  по предыдущему абзацу. Не читать secrets в exception text/trace.

- [x] **6. Добавить runtime cases** с existing _FakeDispatcher/_FakeNotifier/
  _runtime_workflow и Events: stop до Settings/lock; stop на recheck; stop между
  polling yield и READY; ready-first затем stop даёт один STOPPING; busy revoke
  с queued reset (ровно 2 devices); stop между fake send и record; два stop на
  удержанном drain; runtime + close errors + stop сохраняют ошибки.
  Existing cancellation cases не заменять signal-owner cases: добавить новый
  параметр trigger (root.cancel либо stop.request_stop) к соответствующим тестам.
  Assert kwargs["handle_signals"] is False в bootstrap test.
  Проверка ошибки notifier требует, чтобы session/lock всё равно закрывались.
  Fake barriers освобождать в finally, без timing-only race на случайном sleep.
- [x] **7. GREEN affected task set:** tests/bot/test_lifecycle.py,
  tests/bot/test_workflow_worker.py, tests/bot/test_app_bootstrap.py,
  tests/bot/test_bot_runtime_worker.py. RED новых selectors запускать до их fix,
  не объявлять новым RED прежние passing cases.
- [x] **8. Commit:** только перечисленные source/tests и AMN2 CHANGELOG.
  Suggested message: fix(bot): honor startup stop before factory and readiness.
  Записать actual RED/GREEN, сохранение direct cancellation и предел Linux UNKNOWN.

## Task 3: Реальные сигналы только disposable synthetic child и итог

**Files:** tests/bot/test_lifecycle_signals.py (new),
tests/bot/lifecycle_signal_child.py (new), CHANGELOG.md.
**Consumes:** controller/signal scope + runtime из Tasks 1–2.
**Produces:** Linux signal evidence либо явно NOT_RUN; не target/systemd PASS.

- [x] **1. Добавить parent acceptance** для SIGTERM и SIGINT на трёх барьерах:
  PRE_LOOP, FACTORY_DISPATCHED, READY. Всего шесть cases, по одному signal на child.
  Для двух первых нет последующего READY; в factory case close происходит только
  после release; в READY case STOPPING ровно один раз и cleanup order сохранён.
  Файл помечен skipif(sys.platform != "linux", reason="Linux OS signal evidence required").
  Skip на Windows записывается как NOT_RUN, не как закрытый signal gate.

~~~python
@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
@pytest.mark.parametrize("barrier", ["PRE_LOOP", "FACTORY_DISPATCHED", "READY"])
def test_owned_child_signal_stops_at_barrier(tmp_path, signum, barrier):
    trace = run_owned_child(tmp_path, signum, barrier)
    assert trace[-1] == "CLOSED"
    assert trace.count("STOP_ACCEPTED") == 1
    if barrier != "READY":
        assert "READY" not in trace
    else:
        assert trace.count("STOPPING") == 1
    if barrier == "FACTORY_DISPATCHED":
        assert trace.index("RELEASE") < trace.index("WORKFLOW_CLOSE")
~~~

  run_owned_child(tmp_path: Path, signum: int, barrier: str) -> list[str]
  определяется в том же parent test file; импорты pytest/signal/sys/pathlib/subprocess
  явные. Запускает argv list [sys.executable, "-I", "-B", "-c", bootstrap, source,
  barrier, scratch], вставляет только source в sys.path и вызывает helper entrypoint.

- [x] **2. Child helper**: функция run_child(barrier: str, scratch: Path) -> None.
  Использовать _persistent_settings(scratch) с _env_file=None, _FakePersistentBot,
  _RecordingLock, fake notifier и _runtime_workflow; вся DB in-memory/temporary.
  Settings/DB создавать внутри injected runtime после attach/stop-check,
  не перед установкой signal scope. PRE_LOOP stop не создаёт их.
  Никаких настоящих Telegram/network adapters/Settings defaults.
  ProcessSignalScope установлен до PRE_LOOP; parent получает BARRIER:<name>.
  Для PRE_LOOP ожидать stdin GO до loop attach; OS handler сохраняет pending.
  Для FACTORY_DISPATCHED factory устанавливает Event и ждёт release с 5s cap;
  для READY fake notifier печатает barrier после своей READY записи.
  Один daemon stdin-reader принимает только GO/RELEASE, не исполняет строки.
  Child controller callback печатает STOP_ACCEPTED после применения request_stop.
  Parent для FACTORY_DISPATCHED после STOP_ACCEPTED отправляет RELEASE;
  для PRE_LOOP после сигнала отправляет GO, чтобы pending мог примениться.
  READY не требует RELEASE: после STOP_ACCEPTED ждать CLOSED/exit. Печатать только фиксированные enum records,
  flush=True; ни Settings, ни exceptions с runtime data, ни kwargs целиком.
  Автозавершение synthetic child по 10s watchdog — nonzero/UNKNOWN, не CLOSED.
- [x] **3. Parent safeguards**: держать Popen handle и poll-check непосредственно
  перед child.send_signal(signum); запрет сигналов по найденным/внешним PID.
  Читать stdout с deadline 10s и cap 64 records/16 KiB; malformed/out-of-order
  record — failure. После trace/ошибки в finally release, terminate ещё живого
  exact child, при необходимости kill и wait; не возвращать PASS после такого kill.
  stderr также ограничен; сохранить безопасную классификацию, не raw secrets.
  Baseline state до начала должен быть тот же source/dependency binding.
- [ ] **4. NOT_RUN — проверить механизм RED на доступной Linux среде:** до claim actual
  OS-signal PASS один test-only negative control с пропущенным pending delivery
  должен нарушить trace assertion. Вернуть штатный helper, затем выполнить шесть
  cases один раз GREEN. Negative control не изменяет production code и не коммитится.
  Если Linux/Python/dependencies не доступны уже сейчас, этот шаг NOT_RUN;
  подготовленные tests остаются для отдельно согласованного compatible environment.
  Не переносить Windows venv на Linux и не устанавливать новую среду.
  21.09 после «продолжай» выполнен [inventory среды](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#linux-environment-discovery-2026-09-21):
  WSL не установлен, Docker/Podman отсутствуют в PATH; Linux gate остаётся
  NOT_RUN до указания уже готовой compatible среды. Source tests не повторены.
- [x] **5. Итоговый affected набор один раз** после всех source/test changes:

~~~text
tests/bot/test_lifecycle.py
tests/bot/test_lifecycle_signals.py
tests/bot/test_workflow_worker.py
tests/bot/test_async_workflow.py
tests/bot/test_handler_lifetime.py
tests/bot/test_persistent_runtime.py
tests/bot/test_app_bootstrap.py
tests/bot/test_bot_runtime_worker.py
~~~

  Это новый affected regression на изменённом source, не повтор полного 312 suite.
  JUnit отдельно показывает passed/failed/skipped; Windows skip Linux cases не
  превращать в ALL_PLATFORM_PASS. Errors/warnings/unretrieved task exception —
  разобрать; повтор только после исправления/нового вопроса, не после commit.
- [x] **6. Self-review без subagent:** проверить пять Review Focus, spec coverage,
  exact source scope, сохранение existing queue/factory races, отсутствие secrets.
  Если выявлена проблема — один bounded fix с воспроизводимым RED и affected GREEN.
- [x] **7. Commit source CHANGELOG + два новых tests** (и только необходимые
  исправленные task files при наличии fix). Suggested message:
  test(bot): cover owned startup and running signal boundaries.
  Затем source push/readback и AMN3 evidence sync по правилам ниже.

## Git, evidence и критерий завершения

После approval исполнения commit/push scope наследует handoff раздел 1:
AMN2 source commits только remote amn2 https://github.com/barakov-dot/amn2.git,
refs/heads/codex/phase16-web-health-event-loop. Remote origin AMN2 указывает
на AMN3 — source туда не push. Перед каждым commit staged names/diff,
CHANGELOG/secret/whitespace gate; перед push exact URL/ref/HEAD и hook results.
Только обычный push, NO_FORCE/NO_TAGS/NO_OTHER_REFS; после push remote SHA readback.

AMN3 sync после результата: этот подплан (фактические checkbox/results),
existing lifecycle design (source status, не снять M4 budget), главный plan,
existing SSH/web/bot receipt и CHANGELOG. Документы — origin
https://github.com/barakov-dot/amn3.git,
refs/heads/codex/phase16-awg3-family-3-1-spain-pilot-016. Exact-file staging,
отдельный substantive commit со своим CHANGELOG; source SHA не подменять docs SHA.

Evidence: actual source before/after, lock/dependency binding, selectors/argv,
RED причина, GREEN/JUnit counts и durations/caps, Linux six-case result или
NOT_RUN, limits, commit/push readback. Сохранить scratch; cleanup не делать попутно.

Завершение локального source slice: Tasks 1–2 реализованы, targeted regression
пройден, Task 3 evidence честно classified, Git/receipt синхронизированы.
Если Linux NOT_RUN, формулировка только SOURCE_IMPLEMENTED_WINDOWS_TESTED:
реальная Linux signal boundary остаётся непроверенной. Даже Linux six-case PASS
не доказывает systemd stop budget, remote quiescence, business success или deploy.
M3 target/M4 production budget, workload enforcement, writer/restart fence и все
Phase16 live/acceptance prerequisites остаются открыты.

## Self-review плана и approval

- Spec A1/A2 покрыты Tasks 1–2; A3 capacities сохранены, production bulk cap
  не реализуется; A4 error/UNKNOWN boundaries проверяются в Task 2/receipt;
  A5 synthetic OS boundary и отсутствие Linux evidence — Task 3.
- Все пять Review Focus имеют owning task и проверяемое ожидаемое поведение.
- API/paths сверены с source 1bd7f62; implementation snippets — будущие edits,
  а не уже применённый patch. Production timeouts/target state не назначены.
- Исполнение этого локального плана завершено в допустимых границах. Следующий
  отдельный scope: compatible Linux signal evidence либо target readback.
  Настоящие target inventory/units/activation и live gates этим не открываются.
