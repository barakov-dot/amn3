# AMN2 — последовательное выполнение bot workflow

Статус: DESIGN_APPROVED_NOT_IMPLEMENTED_NOT_DEPLOYED.
Дата: 2026-09-20. Рекомендуемый вариант A из
[source review](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-sqlite-и-границы-переноса--2026-09-20).
После «учтем и продолжим» подготовлен конкретный design. Оператор подтвердил
его словом «подтверждаю» после публикации commit b277154. Утверждение относится
к этому design; [план реализации](../plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md)
подготовлен отдельно и ещё ожидает review/выбора метода. Это контракт одного
локального изменения, не второй execution plan Phase16 и не live approval.

## 1. Цель и границы

Медленный синхронный SSH внутри bot workflow не должен останавливать asyncio
цикл событий. Сохраняем существующий порядок remote → local внутри бизнес-метода
и стандартную проверку принадлежности SQLite потоку. Отзывчивость означает
продолжение watchdog и coroutine, которым не нужен workflow. DB-backed меню
ждут очереди; при всех восьми занятых aiogram slots новый update может ждать
освобождения slot. Обещания немедленного ответа каждой команде нет.

Baseline: AMN2 2069e4147437067c08a7d3bde7361433179ac727,
C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/amn2-web-health-event-loop.
Исходный checkout и web health fix сохраняются. Работы только с bot runtime,
его handlers/API boundary, управлением ресурсом workflow и связанными тестами.

Исключены: параллельные mutations, общая межпроцессная блокировка web/CLI,
миграция БД, новые retry/circuit breaker, смена SSH timeout, установка зависимостей,
новая выдача/включение AWG3, DefaultVPN delivery, package build/stage/install,
VPS/Telegram/рабочая БД. AWG2_UNTOUCHED; package016 immutable.

## 2. Компоненты и владение ресурсами

| Компонент | Ответственность и граница |
| --- | --- |
| BotWorkflow и существующие services | Синхронные бизнес-операции; проверки прав и состояния остаются внутри методов перед side effects. CLI/service API остаётся синхронным |
| Workflow worker | Один выделенный поток на bot instance: открыть workflow/SQLite, исполнять jobs последовательно, закрыть ресурс. Нельзя создать SQLite в event loop и потом передать её в поток |
| AsyncBotWorkflow facade | Явные async-методы для всех используемых handlers операций; фиксированный набор, без произвольного getattr/callable от update. Единственная runtime-точка доступа handlers к workflow |
| Handler lifetime owner | Через middleware учитывает принятые handlers, держит сильные ссылки на их tasks, закрывает приём и дожидается завершения. Не использует private task set aiogram |
| run_persistent_bot | Порядок admission/start/readiness и shutdown, владение worker/lifetime owner/Telegram session/instance lock |

Worker использует собственную ограниченную FIFO очередь в event loop и отдельный
ThreadPoolExecutor(max_workers=1). Учитываемый job pump передаёт в executor только
один job и ждёт его terminal state до следующего submit. Cancelled queued jobs
физически удаляются из нашей очереди: их нельзя накапливать во внутренней очереди
executor после освобождения квоты. Общий default executor для workflow не используется.
Создание и close выполняются в том же выделенном потоке. Factory получает settings, но не
уже открытый Repository. При неудачном создании частично открытая connection
закрывается там же; штатный ресурс имеет явный close, без поиска _repo из handler.
check_same_thread=False не вводится. Существующие синхронные callers не получают
async facade незаметно; runtime injection и bot tests переводятся явно.

Все 41 прямой вызов 30 методов из handlers.py входят в миграцию, включая
record_admin_config_delivery. Значения sqlite3.Row превращаются в независимые
mapping/list snapshots в worker; уже материализованные DTO сохраняют контракт.
Cursor, connection, Repository, lazy generator и сервисы с доступом к БД наружу
не выходят. config bytes передаются только существующему пути доставки и не
логируются. Аргументы/результаты не изменяются одновременно в двух потоках;
contextvars копируются на job, а не разделяются между handler requests.

Dispatcher перестаёт публиковать сырой phase15_awg3_components в runtime context.
Этот внутренний interface меняется явно, соответствующий bootstrap test обновляется.
Sync factory по-прежнему может держать bundle внутри BotWorkflow для своих services;
новая async facade его не экспортирует. Имя workflow в dispatcher указывает на facade.

## 3. Последовательность и очередь

Внутри worker одновременно выполняется ровно один бизнес-метод. FIFO определяется
порядком принятия jobs, не временем отправки сообщений Telegram. Несколько вызовов
одного handler не становятся общей транзакцией; проверки полномочий/состояния
сохраняются внутри каждого метода, который выдаёт данные или меняет состояние.
Доступ к конфигу и прежние admission/freshness/issuance checks не ослабляются.

Лимит outstanding jobs — 8 суммарно: running плюс queued. Он связан с существующим
PERSISTENT_TASKS_CONCURRENCY_LIMIT=8, без нового env setting. Каждый принятый handler
имеет не более одного outstanding workflow job и ожидает его перед следующим.
Handler owner также ограничен восемью принятыми handlers; свободное выполнение
Telegram await не разрешает обходить этот предел через необслуживаемые tasks.

Девятый job отклоняется до submit типизированным WorkflowBusy; очередь не растёт
без границ и скрытого ожидания в executor нет. Нет автоматического повторного
submit. Безопасный ответ относится к отклонённому шагу, не заявляет rollback
всей команды, если раньше в этом handler уже был завершён другой шаг.
При shutdown новые handlers не принимаются и не получают доступа к workflow.
Ранее принятые handlers сохраняют свои права на последующие jobs до завершения.

## 4. Отмена и конечный результат

| Состояние job при отмене ожидающей coroutine | Контракт |
| --- | --- |
| Ещё не принят | Никаких действий и резервирования в executor |
| Queued в нашей FIFO | До dispatch job удаляется из очереди, фиксируется NOT_STARTED; место освобождается один раз |
| Dispatched/running | С момента передачи в executor отмена ожидания не отменяет метод, даже если поток ещё не начал его. Remote и local часть доходят до существующего результата/исключения; место освобождается после завершения |
| Completed | Результат/ошибка потребляется один раз; повторного side effect нет |

Переход queued → dispatched и удаление при отмене выполняются в event loop без
await между проверкой и решением; кто выиграл этот переход, определяет исход.
После dispatch Future executor не отменяется. Future worker хранится отдельно
от asyncio waiter. Результат не записывается в уже отменённый waiter и не превращается в InvalidStateError. Для orphaned результата
lifetime owner дожидается terminal state и получает только безопасный diagnostic
outcome: имя разрешённого метода, success/error/partial, без аргументов, cause,
raw result/config/SSH output. Ошибка не остаётся необработанным Future exception.
Это наблюдение в живом процессе, не новый durable recovery journal.

Middleware создаёт и учитывает собственную task handler, а ожидание защищает
shield. Отмена внешней aiogram task не прерывает уже принятый handler: он продолжает
обычный путь, включая отправку/запись доставки. Worker cancellation выше нужна для
отдельно отменённого ожидающего вызова и ошибок lifecycle; это не кнопка отмены VPN.
Сигнал штатной остановки не отменяет принятые handlers и queued mutations.
Все принятые до остановки операции могут завершиться, включая ещё ожидавшие очередь.
Принудительное убийство процесса, повторные updates и восстановление после crash
не получают гарантию exactly-once этим изменением.

## 5. Startup и shutdown

Startup сохраняет текущий порядок: instance lock → Telegram admission → создание
worker-owned workflow → dispatcher → state recheck → polling → READY/watchdog.
Factory ожидается асинхронно внутри существующего startup timeout. Timeout закрывает
приём; ещё не переданная в executor factory не запускается, уже переданная
завершается и закрывает ресурс в своём потоке. Polling/READY не разрешаются после startup failure/timeout. Поэтому
startup timeout — предел допуска, а cleanup может занять дополнительное время.

Нормальный shutdown, отмена root task и ошибка watchdog используют один cleanup:

1. Закрыть приём новых handlers. Перевести runtime в STOPPING; остановить polling
   и watchdog, как предусматривает bootstrap. Начатые owned handlers не отменять.
2. Дождаться всех принятых handlers, включая их очередные workflow jobs и Telegram
   send/record delivery. Telegram session и instance lock пока остаются открытыми.
   Старые разрешённые вызовы принимаются только из уже зарегистрированных handlers;
   новое обращение после закрытия приёма получает WorkflowClosed.
3. Закрыть приём worker jobs, дождаться всех оставшихся running/orphaned jobs.
   Это отдельная страховка, даже если handler уже завершился с ошибкой/отменой.
4. Выполнить close workflow/SQLite в worker, затем завершить executor, не блокируя
   event loop на join/shutdown(wait=True). Повторный cleanup идемпотентен.
5. Закрыть Telegram session и освободить instance lock; вернуть исходный исход
   остановки. Ошибки cleanup учитываются, но не пропускают оставшееся освобождение.

Cleanup имеет собственную учитываемую task: повторная отмена ожидающего root не
позволяет отпустить lock/БД до завершения worker. Нет нового жёсткого общего срока
drain; обычные SSH/HTTP timeouts сохраняются. Зависшая операция может задержать
остановку. Systemd units/TimeoutStopSec не меняются; внешний kill способен оборвать
drain, поэтому deployment требует отдельной проверки stop budget и recovery.

## 6. Частичные ошибки и доставка

Существующий remote → local порядок и доменные исключения сохраняются. В общей
границе bot handlers добавить отдельную обработку RemoteOperationPartialFailure,
не только PeerApplyError. Ответ: «Операция завершилась частично. Состояние сервера
и бота может различаться. Нужна проверка администратором; не повторяйте запрос».
Текст добавляется через существующий app.bot.texts с вариантами ru/en.
Не заявлять успешное удаление, полный rollback или отсутствие remote changes.
Новые diagnostics не выводят exception cause/ключи/raw config. Не выполнять
автоматическое восстановление, повторный SSH или повторную выдачу.

Создание конфига в worker не означает его доставку. Существующий Telegram send
остаётся в event loop, а record_admin_config_delivery возвращается в worker;
handler учитывается до завершения обоих шагов. False или исключение при записи
delivery после send не превращаются в success и не приводят к повторной выдаче.
Неизвестный исход отправки не превращается в гарантию, что пользователь ничего не получил.
Новая durable outbox, доставка после crash и изменение форматов клиентов вне scope.

## 7. Проверки перед признанием локального fix

Только synthetic данные, временная SQLite с обычным check_same_thread, fake
Telegram и управляемые Events вместо реального SSH/сети. Сначала конкретные RED,
затем GREEN одного релевантного набора; это критерии, тесты ещё не запускались.

| Проверка | Что должно быть доказано |
| --- | --- |
| Медленный peer stub | Во время удерживаемого SSH job работает независимая coroutine/watchdog; DB-backed запрос ждёт, затем получает прежний результат |
| Thread ownership | Factory, SQL-запросы и close на одном рабочем потоке; вызов каждого подключённого handler через async boundary не даёт SQLite thread error |
| Последовательные revoke/reset | Нет перекрытия remote частей двух jobs; state/auth checks выполняются при исполнении; каждый side effect не дублируется |
| Очередь | 1 dispatched/running + 7 queued приняты, следующий отклонён без side effect; queued cancel освобождает место один раз, многократные cancel/submit не накапливают jobs в executor |
| Отмена | Queued cancel не меняет remote/local; cancel после dispatch, включая гонку перед стартом потока, не пропускает local finalize; terminal error наблюдается без InvalidStateError/unretrieved exception |
| Частичный сбой | Remote success + local failure и частичный reset дают manual-review ответ, без false success и утечки тестового секрета из cause |
| Доставка | Drain между send и record сохраняет запись; её failure не выдаётся за success, повторной выдачи/отправки нет |
| Startup | Admission failure не создаёт workflow; factory/recheck failure/timeout не дают polling/READY и закрывают открытый ресурс |
| Shutdown | Новые handlers отклонены, принятые завершены; cancel/poll failure/watchdog failure проходят тот же cleanup; close выполняется после последнего SQL/send/record, lock освобождается последним |
| Совместимость | Существующие bot workflow/handlers/bootstrap/persistent runtime и device revoke tests; sync service API, auth и запрет выдачи при выключенных gates сохранены |

Не использовать полный suite как замену этим сценариям; точный релевантный список
зафиксировать в implementation plan после утверждения design. Проверка проводится
с имеющейся локальной зависимостью aiogram 3.28.2; dependencies не обновляются.
Перед интеграцией отдельно сверить версию target environment, не считать latest
документацию доказательством версии установленного runtime.

## 8. Источники, выбор и следующая граница

Исходная инвентаризация и отвергнутое разделение prepare/SSH/finalize — в source
review выше. Последовательный вариант и детали этого design согласованы оператором. Более широкий
параллельный вариант отложен: он требует новых claims/rechecks/recovery.

Локально прочитаны app/main.py, app/bot/main.py, app/bot/persistent_runtime.py,
связанные handlers/services и существующие bootstrap tests. В установленном
aiogram 3.28.2 прочитаны dispatcher.py:_polling/start_polling: handler tasks
учитываются отдельно от polling tasks. Своё drain-владение не основывать на
private _handle_update_tasks или предположении, что завершение polling равно
завершению всех handlers. Это source review, не выполненный runtime test.

Публичные API: [aiogram middleware](https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html),
[long polling](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html).
Семантика SQLite/Future cancellation — по источникам исходного source review.

Design проверен на противоречия очереди/отмены/drain и на границы scope; локальные
ссылки/readback/diff проверяются перед commit. Код/тесты AMN2 не менялись.
Следующий шаг: review подготовленного implementation plan и выбор способа выполнения. Развёртывание требует отдельного gate.
Текущие задачи и live ограничения остаются в [едином плане Phase16](../plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
