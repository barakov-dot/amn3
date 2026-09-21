/GO PHASE 16 — AWG3 FAMILY 3.1, SPAIN PREFLIGHT, CONTROLLED STAGE AND ONE PILOT

## Актуальный контракт — согласование 2026-09-05

Единственный актуальный execution status, очередь и правила повторных прогонов:
[план Phase 16](../plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
Ниже сохранены датированные основания; они не являются свежим upstream/server
readback и не разрешают повторять completed/consumed операции.

- Windows application traffic failure подтверждён, upstream root cause не
  доказана. Новый exact-approved bounded test требует изменившегося официального
  client/engine path или новой различающей гипотезы, а не повторения симптома.
- Acceptance остаётся закрытой до Windows PASS, устранения причины quality
  failure, стабильной проверки и полного Task 4.5. Численные пороги и длительность
  согласуются до acceptance-прогона; этот docs-only GO их не устанавливает.
- Strict A/B выполняется на существующем минимальном пилоте до Task 3B.
  Создание нового peer для повторения уже выполненного Task 4 не требуется.
  Application stage раньше пытались выполнять с STOP; интеграция не завершена.
- Наш code fix требует TDD; upstream/environment correction требует
  соответствующей проверки без обязательного собственного исправления протокола.
- DNS compatibility gap генератора закрыт локальным TDD follow-up 2026-09-05:
  новая файловая подготовка требует два IPv4 DNS; legacy validation сохранена.
  Evidence: `research/amn2/phase16-local-dns-generator-two-ipv4-compatibility-2026-09-05.md`.
  Это не live deployment, не полный Qt import и не изменение существующих профилей/package 016.
- iPhone/A/B отложены оператором; отсрочка не снимает Task 4.5 и acceptance gates.
- AWG2, freshness, checksum/state/rollback approvals, секретность и запрет
  general issuance сохранены. Restart/persistence и leak checks остаются
  требованиями отдельно разрешённого integration/acceptance этапа.

<a id="integration-readiness-web-bot"></a>

## Task 3B: integration-readiness web + bot — локальная подготовка 2026-09-20

Статус: **LOCAL_DEPENDENCY_SLICE_PASS / INTEGRATION_EXECUTION_BLOCKED / NOT_DEPLOYED**.
Это уточнение существующего integration-контракта, не новый execution plan
и не approval на исполнение или runtime-настройки. Подготовка разрешена командой
раздела 1 [handoff](../../NEXT_CHAT_PHASE16_2026-09-20.ru.md).
Очередь остаётся в главном плане; исторические команды ниже не возобновляются.
21.09 оператор согласовал следующий локальный M3 scope ответом «согласовываю,
продолжай»: отдельная среда с неизменённым lock и ограниченные existing tests.
Он выполнен; [receipt и границы](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#dependency-validation-2026-09-21).
21.09 после «приступаем» завершён source-only M4: карта stop paths и writers,
минимальный future readback contract; конечный stop budget не доказан.
Target inventory, source fix, merge/build и live-действия этим не разрешены.

### 1. Source и имеющееся evidence

Кандидат AMN2: **1bd7f62d1fdd3829bc278110ecdc44d3568676a3**,
ветка codex/phase16-web-health-event-loop, remote amn2:
https://github.com/barakov-dot/amn2.git. При подготовке HEAD и remote ref совпали,
дерево чистое. AMN3 entry baseline — handoff 111cfa9a0f41e354d876fa8e80f5cbc23e96ff83,
detached worktree 7489. Старый основной checkout и четыре ideas-файла сохраняются.

| Состав кандидата | Имеющееся evidence | Предел |
| --- | --- | --- |
| Web health offload, 2069e4147437067c08a7d3bde7361433179ac727 | 33 targeted PASS, независимый review без замечаний | Результат на web commit. app/web, dependencies и unit examples не менялись пятью последующими bot commits; нового совместного прогона на финальном SHA нет |
| Bot worker/facade/lifetime/runtime, 614dfd8 → b9f5d4e → 28a4e43 → 8bc8496 → 1bd7f62 | 312 PASS на конечном SHA; review 2069e41..8bc8496, два findings исправлены RED/GREEN в 1bd7f62 | Повторного review после fixes не было; temporary SQLite, fake peer/Telegram, не target runtime |
| Унаследованная история до web fix | Полный кандидат включает baseline 56540e2 и предков | Весь кандидат не равен двум патчам; delta относительно deployed SHA пока UNKNOWN |

Подробности — [завершённый receipt](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-worker-реализация-и-проверки--2026-09-20),
[bot design](2026-09-20-amn2-bot-workflow-worker-design.ru.md) и
[выполненный plan](../plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md).
Проверки не повторять на неизменном коде ради документации.

Source SHA не является package identity/deployed revision.
[Source receipt package016](../../../research/amn2/phase16-source-readiness-receipt.md)
связан с a3682fc44dd9e74ff96392ad99623474facf377f, не с кандидатом.
Package016 immutable; web/bot изменения в него не переносить.
Для будущего artifact нужны отдельный packaging scope, выбранная новая identity,
source/tooling/lock binding и manifest checksums. Сейчас они не назначены;
merge, package build и перенос файлов этим gate не разрешены.

### 2. Dependencies и target binding

Статически прочитаны файлы именно candidate SHA:

| Источник | Установленный факт |
| --- | --- |
| [pyproject.toml](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/pyproject.toml) | Python >=3.12,<3.13; aiogram >=3.4,<4 — диапазон, не target lock |
| [Runtime lock](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/requirements/phase15-runtime-py312.lock) | aiogram==3.30.0; SHA256 файла a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab |
| [Test lock](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/requirements/phase15-test-py312.lock) | SHA256 файла 52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235 |
| Выполненные bot tests по receipt | Python 3.12.14 / aiogram 3.28.2, существующий .codex_deps; не установка из candidate runtime lock |
| Локальный M3, 21.09 | Изолированная Windows AMD64 / Python 3.12.14 / aiogram 3.30.0; 48 test pins включают все 40 runtime pins; hashes wheels и pip check PASS; 68 lifecycle tests PASS |
| Target environment | Python patch/build, platform/ABI, aiogram/transitive versions, фактический lock/artifacts и deployed source UNKNOWN |

312 прежних PASS с 3.28.2 не переобозначаются как результат 3.30.0.
Локальный пробел lifecycle на pinned dependencies закрыт новым отдельным набором:
**68 PASS на неизменённом test/runtime lock**, без общего повторного suite.
[Нормализованный binding всех wheels и проверки](../../../research/amn2/phase16-web-bot-dependency-validation-2026-09-21.json).
Это Windows evidence, не Linux/target acceptance. M3 остаётся частично открытым:
нужны фактическая target среда, её соответствие intended lock и отдельная оценка
platform-specific разницы. Source/dependency locks и глобальная среда не изменялись.

Нужен нормализованный target receipt: checked_at, target identity, deployed
source, Python/platform/ABI, полный dependency binding, entrypoints и effective
unit/drop-in properties. EnvironmentFile, tokens и реальные configs не читать
и не выводить ради этого receipt. Новый target readback требует exact approval.

### 3. Startup и readiness

[app/main.py на кандидате](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/app/main.py)
сохраняет порядок:

1. Instance lock; создание Telegram client/session.
2. Telegram admission: exact identity, отсутствие webhook/backlog по существующему
   контракту; затем worker-owned workflow/SQLite factory в выделенном потоке.
3. Dispatcher с async facade/lifetime; повторная проверка Telegram state.
4. Polling task; один turn event loop и проверка раннего завершения.
5. Admission receipt и READY; затем watchdog.

Admission/factory/recheck находятся внутри существующего startup timeout.
Его target значение UNKNOWN; тестовые таймеры не SLA. Failure/timeout не разрешают
polling/READY. Dispatched factory может завершать cleanup после deadline;
не dispatched factory после close не запускается (исправленный regression).
READY подтверждает admission и отсутствие обнаруженного раннего завершения
polling, не бизнес-операцию, доставку или VPN acceptance.

[Web unit example](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/deploy/systemd/amneziya-web.service.example)
имеет Type=simple: active-state не заменяет согласованную web readiness проверку.
Реальный Telegram startup сейчас запрещён.

### 4. Drain, stop budget и restart

Bot cleanup закрывает приём, посылает STOPPING только после ранее отправленного
READY, останавливает watchdog/polling, ждёт accepted handlers, затем worker jobs/
close, Telegram session и освобождение instance lock. Queued mutations и
send → delivery record завершаются. Отмена waiter после dispatch не отменяет SSH;
повторная отмена root не ускоряет освобождение ресурсов. Bot FIFO не сериализует
web/CLI/другие процессы; web health to_thread имеет отдельный lifetime.

[Bot unit example](https://github.com/barakov-dot/amn2/blob/1bd7f62d1fdd3829bc278110ecdc44d3568676a3/deploy/systemd/amneziya-bot.service.example)
содержит TimeoutStartSec=135s, TimeoutStopSec=30s, WatchdogSec=60s,
Restart=on-failure, RestartSec=30s. Это **пример source**, не effective units target.
В web example TimeoutStopSec не задан; effective default/drop-ins UNKNOWN.
Units не меняются.

Общего hard drain deadline нет. Восемь jobs не дают формулу 8 × SSH timeout:
handler делает несколько jobs/send, reset может затронуть несколько устройств;
remote timeout не доказывает прекращения удалённой работы. Startup timeout
не ограничивает cleanup. Нельзя объявить примерные 30s достаточными или просто
увеличить их до выдуманного значения.

До исполнения нужны effective TimeoutStartSec/TimeoutStopSec, KillMode,
KillSignal/FinalKillSignal/SendSIGKILL, restart/watchdog/start-limit properties
bot/web; состав других writers; upper bound разрешённой нагрузки и всех
последовательных действий, terminal readback и согласованный запас.
Отдельно учесть startup cleanup, web health threads, Telegram send/record.
Если конечный upper bound не доказан, budget UNKNOWN и deployment BLOCKED:
нужно отдельное lifecycle/recovery решение. Manager escalation/force kill
не является drain PASS; restart после UNKNOWN не доказывает отсутствие дублей.

<a id="stop-budget-m4"></a>

#### M4: результат локального source-only разбора — 2026-09-21

Статус: **SOURCE_REVIEW_COMPLETE / STOP_BUDGET_UNPROVEN / TARGET_UNKNOWN**.
[Датированный receipt с точными source/dependency ссылками](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#stop-budget-m4-2026-09-21).
Читались кандидат 1bd7f62 и сохранённые pinned aiogram 3.30.0 / Uvicorn 0.52.3
из M3; code/tests/units/dependencies не менялись, runtime не запускался.

| Участок | Что действительно ограничено | Чего недостаточно для stop budget |
| --- | --- | --- |
| Вход и startup | Admission/factory/recheck имеют общий coroutine timeout; default 30s, allowed 1..120s в source settings | Settings, lock/client setup до таймера; синхронные участки и dispatched factory не получают hard execution deadline. Factory выполняет schema/seed writes; после timeout cleanup ждёт её |
| Вход по сигналу | Pinned aiogram регистрирует SIGTERM/SIGINT внутри start_polling | В app.main нет более раннего SIGTERM handler: admission/factory/recheck уже прошли к регистрации. Coroutine cancellation в Windows tests не доказывает startup cleanup по Linux SIGTERM; exact target signal path UNKNOWN |
| Остановка polling | После входа в cleanup приём закрыт, watchdog/polling cancel запрошен до drain | Ожидание отмены tasks без отдельного срока; aiogram shutdown hooks также await. STOPPING и READY — синхронные sends, без настроенного socket timeout; EXTEND_TIMEOUT_USEC в этом notifier нет |
| Принятые handlers | Не более 8 одновременно; lifetime сохраняет их до завершения, worker FIFO capacity 8 | Один handler содержит несколько workflow calls и Telegram sends; drain ждёт весь handler. Число jobs не является числом SSH-вызовов или секунд |
| Remote/local mutation | SystemSshClient default 20s на локальный subprocess invocation | Docker revoke: read → write → restart, три invocation; reset обходит список устройств без собственного cap. После remote идёт local transaction/audit. Timeout локального SSH не доказывает terminal remote state; общего operation deadline нет |
| Delivery/record | Pinned aiogram default request timeout 60s, app.create_bot его не переопределяет | Несколько последовательных sends, затем запись результата/ответ. 60s — настройка отдельного HTTP request, не bound handler/drain; пример unit Stop=30s не покрывает даже настроенное окно одного send |
| Resource close | Порядок handlers → worker → session → lock сохраняется | Worker ждёт factory/pump/close и executor.shutdown(wait=True) без общего deadline; SQLite/filesystem/close не имеют доказанного wall-time bound. Session close await + 0.25s sleep не дают hard 0.25s bound |
| Web/API/agent | CLI запускает Uvicorn без timeout_graceful_shutdown; pinned default None | Ожидание connections/tasks без этого deadline; lifespan идёт отдельно. Web health await to_thread не ограничивает работу потока и не доказывает её прекращение при отмене request |

Это source-level ограничения доказательства, не сообщение о наблюдавшемся
зависании или потере данных. Состав reset зависит от repo.list_user_devices:
max_devices настройки выдачи не подставляется как доказанный cap существующих
данных. Наличие конечных отдельных request timeouts не доказывает конечную
сумму до освобождения lock/процесса. Увеличение TimeoutStopSec само по себе
не закрывает ранний signal path и неограниченные участки.

**Другие writers.** Bot instance lock относится к bot instance. В source есть
независимые web repositories (включая summary/audit после health), API repository
с schema initialization, CLI mutations и local-agent RepositoryAgentAuditSink.
Даже read-oriented agent request может записывать audit. Их наличие в коде
не доказывает запуск на target или общую БД. Необходима матрица роли → точный
entrypoint/revision → process/cgroup → нормализованная DB identity → владелец/
источник запуска. Scheduler/manual CLI/child operations учитываются отдельно;
пустой bot queue или stopped bot unit не доказывают quiescence этих контуров.

**Минимальный будущий readback M4 (не команда на исполнение).**

1. До exact approval заполнить target identity, реальные имена bot/web units,
   известные дополнительные API/agent/writer entrypoints, source/dependency
   binding и allowlist источников. Не считать example names именами Spain units.
   Задать конечные time/output/object caps и stop-condition для сбора; сейчас
   target/имена/caps не установлены, готового исполняемого /APPROVE нет.
2. Один нормализованный снимок по согласованным units: checked_at, версия manager,
   Id, LoadState, ActiveState, SubState, Type, NotifyAccess; MainPID, ControlGroup
   и process-start identity для защиты от повторного использования PID.
3. Effective properties: TimeoutStartUSec, TimeoutStopUSec,
   TimeoutStartFailureMode, TimeoutStopFailureMode, KillMode, KillSignal,
   FinalKillSignal, SendSIGKILL, Restart, RestartUSec, WatchdogUSec,
   StartLimitIntervalUSec, StartLimitBurst. Не заданное/неподдерживаемое поле
   сохраняется UNKNOWN; source example и manager default не подставляются.
4. Отдельно нормализовать execution hooks: наличие и число ExecStartPre/
   ExecStartPost/ExecStop/ExecStopPost, ожидаемый entrypoint/аргументы и fingerprints
   unit/drop-ins/deployed files без raw environment/команд с секретами. Для
   дополнительных hooks сначала нужен их bounded scope: одних timers мало.
   Действующий Uvicorn graceful timeout и bot admission/polling/client settings
   сверять с approved intended values, не читать .env ради этого gate.
5. Для каждого writer — role/count, entrypoint/source binding, DB identity
   equality и evidence owner/launch source. Если нельзя установить DB identity
   без protected configs, сохранить UNKNOWN до отдельного разрешённого способа.
   Отсутствие в allowlist не равно отсутствию процесса; неизвестный writer,
   drift, ошибка запроса или cap означают STOP без расширения поиска/повторов.

Readback только описывает состояние: он не stop/restart/signal/Telegram probe,
не запись в БД и не proof quiescence. Не собирать raw cmdlines, EnvironmentFile,
конфиги, keys, journals или содержимое БД. Фактические target evidence по всем
этим пунктам отсутствуют; M3/M4 не закрыты будущим перечнем properties.

**Решение перед реализацией/activation.** Нужен отдельный локальный lifecycle
design: обработка stop во время startup до polling; конечный разрешённый workload
и пределы каждой стадии либо явная recovery policy для неограниченных/partial
операций. Для выбранного решения затем отдельно согласуются code/tests/units,
Linux signal validation и target readback. Нельзя обещать lossless stop за
выбранное число секунд, просто отменить dispatched mutation или приравнять
manager force kill к успешному drain. До этого budget UNKNOWN, execution BLOCKED.

<a id="lifecycle-design-m4"></a>

#### M4: утверждённый lifecycle design — 2026-09-21

Статус: **DESIGN_APPROVED / PLAN_READY_FOR_REVIEW / NOT_IMPLEMENTED / STOP_BUDGET_UNPROVEN**.
После подготовки design в commit 8ba7e5d31236824bddd304a4f278965029d1578b
оператор ответил «Подтверждаю». Утверждён design A и подготовка
[ограниченного implementation plan](../plans/2026-09-21-amn2-bot-startup-stop-lifecycle-plan.ru.md);
его source/tests исполнение ещё не согласовано.
Основание — [source-only M4](#stop-budget-m4), AMN2 1bd7f62; текущий worker
[design](2026-09-20-amn2-bot-workflow-worker-design.ru.md) сохраняет силу.
Документ описывает предлагаемое поведение, не выдает его за нынешний runtime.

**Цель и критерий успеха.** Stop, обработанный до polling или во время работы,
должен закрывать вход один раз и сохранять владение ресурсами до cleanup.
Не начинать следующую startup-стадию/READY после принятого stop; уже dispatched
factory/mutation и accepted send→record завершать по прежнему контракту.
Local cleanup completion и успешный business outcome — разные результаты.
Source fix этого поведения сам по себе не делает M4 или integration PASS.

| Вариант | Выигрыш | Ограничение / решение |
| --- | --- | --- |
| A — единый stop owner + сохранение drain, рекомендуется | Закрывает ранний signal path и делает startup/stop races проверяемыми; сохраняет remote→local и send→record | Не обещает hard wall-time, требует отдельно target/recovery/workload evidence. Это следующий ограниченный source scope |
| B — общий таймер с отменой/force exit | Ограничивает ожидание supervisor только при реально исполнимом внешнем termination | Не останавливает Python thread/remote operation безопасно; возможны send без record и потеря terminal evidence. Не выбран |
| C — полные operation deadlines, durable recovery/согласование всех writers | Может стать основанием общего production lifecycle contract | Новый большой scope: DB/SSH/HTTP/filesystem, bulk caps, durable state и межпроцессное fencing. Не добавлять попутно к signal fix |

**A1. Один владелец сигнала и остановки.**

- Небольшой process-signal adapter устанавливается в штатном executable entrypoint
  до Settings, lock, Telegram client и worker. Импорт модуля не меняет signals.
  Один StopController хранит состояние и передаётся runtime; сигнал до готовности
  loop сохраняется как pending stop и применяется до создания app resources.
- Signal adapter переводит SIGTERM/SIGINT в одно событие контроллера, не делает
  DB/network/logging/close прямо в OS callback. Все lifecycle transitions идут
  в event loop; момент принятия stop — выполнение его callback. Между доставкой
  OS signal и callback может быть задержка: блокирующий sync код не стал preemptible.
  Startup imports до установки adapter остаются вне гарантии app cleanup.
- Scope действует до завершения cleanup и выхода из lock; прежние signal handlers
  восстанавливаются в finally, включая частичную ошибку регистрации. На Linux
  ошибка регистрации не допускает startup/polling. Windows использует явно
  проверяемый adapter либо synthetic controller в tests; тихий fallback,
  объявленный Linux PASS, запрещён. Соседние event loops/процессы не затрагиваются.
- Dispatcher вызывается с handle_signals=False: aiogram не второй signal owner.
  Существующие polling timeout, close_bot_session=False и concurrency=8 сохраняются.
  CLI/network-check/другие приложения не получают новую signal policy незаметно.
- Первый stop синхронно фиксирует latch, закрывает handler admission, затем
  инициирует один выход из startup/polling в существующий cleanup. Повторный stop
  не отменяет owned cleanup и не является командой force kill. Direct coroutine
  cancellation и runtime error по-прежнему приходят в тот же cleanup.
- До каждого startup перехода и перед admission receipt/READY проверяется latch.
  Решение о READY и его вызов выполняются в одном loop segment без await;
  stop, обработанный раньше, побеждает. Если READY уже отправлен до stop,
  действуют обычные STOPPING/drain. Ошибка notifier не пропускает cleanup.

**A2. Factory dispatch и сохранение принятых операций.**

Критический race: после запроса stop одной отмены startup waiter недостаточно —
worker._open_resource уже мог быть поставлен в event loop. Поэтому нужен
startup-only guard непосредственно перед submit factory в executor. Проверка
latch и решение submit выполняются в одном loop segment без await: кто первым
зафиксировал stop или dispatch, определяет исход. Сигнал, ещё ожидающий callback,
не переобозначается задним числом как уже обработанный stop.

| Состояние при stop | Требуемое поведение |
| --- | --- |
| До app resources / factory ещё не dispatched | Не создавать новые ресурсы/не submit factory; закрыть только уже созданное. Нет polling, admission success receipt или READY |
| Factory dispatched, в том числе ещё не начала исполняться в потоке | Ждать factory и её штатный close в owner thread; не отменять executor future. Не переходить к recheck/polling/READY |
| Recheck или промежуток перед polling/READY | Прекратить дальнейший startup, дождаться cleanup ресурса; для раннего stop не отправлять STOPPING как замену неотправленному READY |
| Polling и accepted handlers | Закрыть admission, остановить polling/watchdog, дождаться handlers и их следующих jobs/send/record; затем worker close, session close, lock release |
| Cleanup уже идёт | Повторный signal не вызывает второе закрытие, новый timer/retry или ранний release |
| Runtime/cleanup error одновременно со stop | Сохранить ошибку/ошибки и не превратить их в успешную остановку; cancellation, вызванную owner, отличать от посторонней отмены |

Нельзя вызывать worker.aclose непосредственно из signal callback в RUNNING:
принятые handlers ещё имеют право enqueue последующие jobs, включая delivery
record. Startup-only guard не распространяется на эти продолжения. Существующие
queued-cancel и factory-after-close fixes остаются; stop не означает отменить
всю принятую очередь. Lock удерживается до окончания cleanup, даже при ошибке.

**A3. Пределы нагрузки: количество отдельно от времени.**

| Область | Решение этого design | Что остаётся за gate |
| --- | --- | --- |
| Bot admission / FIFO | Сохранить H=8 accepted handlers, Q=8 outstanding jobs (running+queued), один submitted workflow job. После stop новых handlers 0; без retry overflow | Нет нового production env knob или изменения max_devices |
| Продолжение accepted handler | Разрешены существующие последовательные jobs/send/record до terminal outcome, без новых detached mutation tasks | H и Q не ограничивают число всех последовательных шагов или их latency |
| Reset/bulk | В signal fix не менять бизнес-семантику и не обрезать список. В synthetic acceptance использовать ровно 2 устройства для partial path; для queue case — 1 running + 7 queued | Production upper bound требует отдельного утверждённого cap и проверки полного набора ДО первого remote side effect. Unknown/overflow должен отклонять всю новую bulk operation, а не частично исполнять; enforcement пока отсутствует |
| Telegram | Сохранить текущие пути и send→record; не добавлять resend, новые retry или сокращение request timeout | HTTP timeout не доказательство недоставки; число/размер payloads и sequence bound задаются для каждого будущего workload |
| Другие writers | Локальные scenarios только с fake boundaries/temporary DB; ни один не запускает настоящие web/API/agent/CLI writers | Future production admission требует полной writer matrix, scope fence и target evidence из M4; bot lock их не заменяет |

Для будущего production budget нужен конечный workload manifest: method allowlist,
число handlers/объектов/последовательных шагов/bytes, known writer set, dependency/
entrypoint binding и доказанные time bounds, включая setup/cleanup и scheduler/I/O.
Верхняя оценка включает signal-to-loop, остаток startup, stop polling, принятый
handler graph, worker/session/lock close и согласованный запас. Перекрывающиеся
участки можно консервативно пересчитать, но нельзя пропустить следующий job/record.
Любой недоказанный член сохраняет budget UNKNOWN; наблюдённый максимум одного
теста не upper bound. Числа TimeoutStopSec, Uvicorn graceful timeout и запас
этим design не назначаются. Изменение units/manager policy — отдельный scope.

**A4. Terminal outcome и recovery при отсутствии доказательства.**

| Наблюдение | Классификация | Следующее действие, не выполняемое этим design |
| --- | --- | --- |
| Все owned tasks terminal, close/session/lock завершены без ошибки | LOCAL_CLEANUP_COMPLETE; операции отдельно success/error/partial | Не называть автоматически remote rollback, successful delivery или target acceptance |
| Stop до dispatch, отсутствие side effects доказано trace | NOT_STARTED для соответствующей операции | Не переносить этот вывод на ранее выполненные startup schema/seed writes |
| Remote success + local failure либо send success + record failure | PARTIAL / MANUAL_REVIEW_REQUIRED, даже если cleanup завершился | Сохранить нормализованное evidence; без повторной mutation, выдачи/отправки или ложного rollback |
| Deadline наблюдения истёк, thread/remote жив, процесс потерян/убит или cleanup failed | UNKNOWN либо явно подтверждённая ошибка; DRAIN_PASS отсутствует | Закрытый gate на повтор операции/activation/stage; отдельный readback/ownership/quiescence/reconciliation |
| Процесс перезапустился | Сам restart не evidence чистого предыдущего завершения | Проверять предыдущий outcome и recovery gate; не выполнять автоматическое reconciliation/resend |

Таймер наблюдения не переводит живой worker в terminal state. Design не добавляет
durable outbox/incident journal, automatic restart latch, schema migration или
автоматическую очистку. Убитый процесс может вообще не записать outcome:
отсутствие receipt означает UNKNOWN. **Блокировка следующего исполнения здесь —
правило operator gate, не уже реализованный запрет рестарта systemd.**
До activation нужно отдельно доказать/выбрать enforced restart/fencing policy
при UNKNOWN для всех writers. Пример Restart=on-failure такого доказательства
не даёт; менять его сейчас или обещать, что A препятствует всем restarts, нельзя.
Recovery contract v1 сохраняет раздельные inventory → quiescence → cleanup →
readback approvals; rollback/DB restore без них не выполняются.

**A5. Проверяемый будущий source scope и acceptance.**

После утверждения design следующий source slice ограничивается signal adapter/
StopController, app/main.py wiring, startup-only factory guard в worker и их
tests/AMN2 CHANGELOG. Реализация может выделить helper app/bot/lifecycle.py.
Facade/handlers/business services/SQLite schema, web/API/agent и units не меняются.
Точные edits и тестовые команды — в последующем подчинённом implementation plan,
главная очередь Phase16 остаётся одна. Сейчас никакие tests не запускаются.

| Новый вопрос для будущего RED/GREEN | Конечный synthetic scenario / требуемый результат |
| --- | --- |
| Stop до loop и на admission | По одному stop на этих двух барьерах; отсутствие последующего factory/polling/READY, закрытие только созданных ресурсов |
| Stop против dispatch factory | Две детерминированные очередности: stop-first даёт 0 factory submits; dispatch-first даёт 1 factory, 1 close на том же потоке после release |
| Stop на recheck/READY boundary | По одному stop до recheck completion и до READY; нет success receipt/READY после latch. Отдельный ready-first case даёт один STOPPING |
| Stop при mutation и send→record | По одному удержанному synthetic revoke и send/record; сохранить queued continuation и lock до terminal, без resend и повторной mutation |
| Повторный stop и ошибки | Два stop во время drain; один close. Одновременная runtime/cleanup ошибка не теряется и не становится success |
| Владелец OS signals | Fake registration/readback проверяет install до Settings, handle_signals=False, restore после cleanup и rollback частичной регистрации |
| Linux signal boundary | Отдельный disposable subprocess с synthetic resources, signal только по exact child identity после barrier; SIGTERM и SIGINT по одному, проверка порядка startup stop/cleanup. Windows injection не заменяет этот результат |

В source плане назначить конечные parent wall/output caps для каждого probe и
гарантированное освобождение fake barriers в finally. Termination только зависшего
synthetic child после cap — TEST_FAIL/UNKNOWN, не drain PASS. Никакого signal
существующим службам, shell-wide kill или systemd stop. Если локальной Linux
среды нет, результат NOT_RUN и Linux gate открыт; не устанавливать/скачивать
среду или зависимости без отдельного scope. Target systemd/Telegram/VPS не нужны
для synthetic source slice и не разрешаются его одобрением.

**Граница утверждения.** Design A утверждён; implementation plan подготовлен
и ждёт review. Исполнение source/tests согласуется по этому конкретному плану,
inline одним агентом, без новых dependencies или среды. После будущего A PASS можно закрыть
только source signal ownership/races. Target M3, полный stop budget M4, bulk
enforcement, restart/writer fence, M1/M2/M5/M6/M7 и Phase16 acceptance остаются
открытыми. Прежние 33/312 и M3 68 PASS не повторять без нового code/question.

### 5. Stage, recovery и rollback

Application-stage сохраняет snapshot/backup, но сам по себе не активирует
проверенную web+bot ветку. Требуется отдельный activation contract: exact units/
entrypoints/DB-path identity, coexistence/writer fence, переключение, readiness,
revert target и readback. Реальные DB/EnvironmentFile не обследованы.
Code revert не отменяет remote peer mutation или отправленный документ;
backup не разрешает перезапись основной БД.

Controlled-stage runtime без peers и minimal pilot — разные контуры.
Нужна state-bound проверка ресурсов/исключений: AWG2, pilot container/network/
interface/peers, общий image, основное application state, retained package,
имеющийся backup и transaction audit. Текущий retained inventory UNKNOWN;
прошлое отсутствие ресурса не доказывает его отсутствие сейчас.
General issuance disabled; DefaultVPN native delivery не включать; peer не создавать.

| Будущий исход | Классификация и граница |
| --- | --- |
| Admission/factory/recheck failure | Нет READY; возможные factory writes/cleanup отдельно. Отсутствие READY не означает отсутствие изменений БД |
| Drain/operation timeout, потеря транспорта, external kill | Terminal state UNKNOWN; без повторной mutation/send/stage, сохранить evidence и открыть отдельный recovery gate |
| Remote success + local failure; send success + record failure | Partial/manual review, без false success, auto retry/reissue/resend и утверждения rollback |
| Coordinator recovery_required | Сохранить package/имеющийся backup/ресурсы; новый stage блокирован, quiescence не доказана, удаление не разрешено |
| rollback_failed либо attempts_completed_unverified | Ошибка/непроверенные попытки; восстановление не подтверждено |
| Успешный процесс, закрытая SQLite или rolled_back | Недостаточно: нужны resource/DB/remote readback и сохранность исключений в согласованном scope |

[Recovery v1](2026-09-08-phase16-controlled-stage-recovery-contract.ru.md)
не изменён: inventory → доказательство прекращения операций → адресная очистка →
readback, с отдельными exact approvals. Нужны transaction/resource ownership
и quiescence всех установленных источников операций. PID/имя/consumed claim/
совпавшие metadata этого не доказывают. Parser/observations и 164 synthetic PASS
не заменяют live evidence. Автоматический cleanup, Docker prune, снятие
package-блокировки и DB restore сейчас не разрешены.

### 6. Локальные проверки и будущие bounded acceptance checks

Input каждого сценария: candidate/source и dependency binding; для target —
exact state/transaction; fixture либо разрешённая identity, side-effect allowlist,
доказанный time cap, output/data cap, terminal readback и rollback scope.
UNKNOWN обязательного input блокирует запуск. Старые значения не подставлять.
Failure injections допустимы только в отдельно разрешённой synthetic среде;
live partial failure/kill намеренно не вызывать.

| Сценарий | Конечный объём/вход | PASS / FAIL / UNKNOWN и STOP |
| --- | --- | --- |
| Dependency/admission/start | На выбранном lock по одному synthetic identity/webhook/backlog/factory/recheck/timeout case; один штатный startup | PASS: правильный порядок, нет READY при отказе; FAIL: нарушение; UNKNOWN: нет trace/лимита. Прежний suite без нового environment/question не повторять |
| Worker responsiveness/ownership | Одна удерживаемая synthetic operation; 1 running + 7 queued, один overflow, независимая coroutine, temporary SQLite/fake peer | PASS: нет overlap, loop прогрессирует, overflow без side effect, close в owner thread; FAIL: нарушение; UNKNOWN: неполная наблюдаемость. 8 — source capacity, не latency SLA |
| Drain/delivery | Один shutdown между fake send и record; queued/dispatched cases по одному, agreed stop budget | PASS: terminal jobs/record → close → session → lock без manager kill; FAIL: обрыв/повтор/ранний release; UNKNOWN: исход не доказан. Реальный config ради теста не выдавать |
| Web + bot coexistence | Один bounded health stub/request и один bot fixture path, временная БД, exact serving entrypoints | PASS: loop прогресс, прежние auth/CSRF/summary/audit, нет SQLite ownership errors; без модели других writers UNKNOWN/STOP. Общая межпроцессная serialization не обещана |
| Activation/persistence | После prerequisites/approvals одна activation и один согласованный app/runtime restart, exact resource allowlist, без новой выдачи | PASS: intended revisions, readiness/persistence/restart policy, AWG2 equality/pilot сохранены; FAIL: drift/утрата; UNKNOWN: нет binding/readback. Temporary rules/restart=no не production PASS |
| Leaks / Task 5 | Один IPv4/IPv6/DNS набор на существующем peer последовательно, endpoints/method/data/time caps заранее | По [критериям v1](../../PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md). DNS bridge STOP; нет метода/coverage — INCOMPLETE/UNKNOWN, не замена моделью и не разрешение A/B |
| Scoped rollback/recovery | Конкретный исход и approvals v1; одна операция на разрешённый объект и bounded readback | PASS только для списка целей/исключений; query error UNKNOWN. Нет owner/quiescence либо пересечение AWG2/pilot — STOP до изменения |

Общий STOP: mismatch source/deps/state, неизвестный владелец, потеря доступа/
контроля, достижение любого cap, неожиданный side effect или выход за allowlist.
Без retries, продления окна и автоматического kill/cleanup.
Валидный FAIL сохраняется при других UNKNOWN. Прежние 33/312 PASS остаются
локальным evidence. 21.09 existing worker/facade/lifetime/admission/bootstrap tests
покрыли локальную часть первых трёх строк: 68 PASS на новом dependency set.
Это не доказательство systemd stop budget. Web+bot coexistence, target activation/
persistence, leaks и live recovery остаются NOT_EXECUTED в этом gate.

### 7. Ровно недостающие evidence и следующий шаг

| ID | Недостающее доказательство/решение | Как закрывается / разрешено сейчас |
| --- | --- | --- |
| M1 | Windows traffic PASS на обоснованном client/engine/hypothesis path; root-cause-bound quality correction, стабильное acceptance и полный strict A/B | Отложенные P0/P1 главного плана; только после возврата оператора и exact approval. Сейчас повтор не запрашивать |
| M2 | Валидная DNS/прочая measurement coverage, endpoints и budgets критериев v1 | Отдельное решение по методике; DNS bridge STOP, tooling ради gate не создавать |
| M3 | Fresh target deployed/source/state + Python/ABI/full dependencies и соответствие intended lock | Локальная Windows часть закрыта 21.09: exact pins/hashes, pip check, 68 PASS. Target/Linux evidence отсутствует; live readback требует exact approval, повтор local suite без новой причины не нужен |
| M4 | Effective units/entrypoints, другие writers, конечный startup-cleanup/stop budget и recovery policy для UNKNOWN | Source-only карта/readback contract готовы; lifecycle design A утверждён 21.09, source plan готов к review, не исполнен. Он не закрывает общий budget/writer/restart gates; target readback по exact approval |
| M5 | Retained inventory, transaction ownership/quiescence, preservation/cleanup readback с исключениями v1 | Четыре раздельных recovery gates; metadata tools готовы локально, live authority отсутствует |
| M6 | Future artifact source/tooling/dependency binding, identity/manifest; activation/revert contract и DB/remote preservation | Отдельный packaging/activation scope после dependencies; package016 сохранить, новый ID/hash/revert target не назначены |
| M7 | Исполненные bounded startup/drain/coexistence/persistence/restart/leak/rollback checks на связанных artifact/target | Раздел 6 после prerequisites и exact approvals; 33/312 PASS не закрывают target acceptance. Synthetic dependency slice может отдельно предшествовать live gates |

Локальный dependency-validation M3 и согласованный source-only M4 выполнены.
Подготовлен [lifecycle design A](#lifecycle-design-m4): один stop owner до startup,
factory dispatch guard, сохранение accepted drain и явная UNKNOWN/recovery policy.
Design A утверждён; [source implementation plan](../plans/2026-09-21-amn2-bot-startup-stop-lifecycle-plan.ru.md)
готов к review. Следующий предмет решения — его inline source/tests execution
с существующей pinned средой и conditional Linux NOT_RUN. Target readback/units
остаются отдельными scopes/approvals; code/tests/units ещё не менялись.
Stop seconds не назначены. Systemd simulation, новый code fix и live execution
не выполнялись. iPhone/A/B остаются отложенными; deployment не разрешён.

Для будущего исполнения approvals раздельны: bounded target inventory;
recovery signals; адресная cleanup и снятие package-блокировки; новый package
build; checksum/state/rollback-bound stage; application activation/Telegram
interaction; restart/leak acceptance. В каждом нужны конкретные цели, bindings,
лимиты и stop-condition. Готовую /APPROVE с UNKNOWN полями не выдавать;
согласование этого текста не заменяет разрешения.

Проверка первоначального дополнения 20.09 была docs-only. После отдельного
согласования 21.09 выполнены isolated dependency install и 68 synthetic tests;
source/locks неизменны. Документы проверяются readback/ссылками/diff/whitespace
и added-line secret scan. Package materialization, SSH/VPS/Telegram API,
restart/install/deploy не выполнялись.
AWG2_UNTOUCHED; package016 immutable; general issuance disabled.

## Историческая ревизия — PACKAGE 016, 2026-08-27

Approved local preparation: baseline `392cc339f7f6afaed0a0dc2a0a80139ca030f560`, local-fix receipt SHA256 `549b515ea50e7668f56f433772633a63c674aaba973876f978f0a2ea15f823de`. Изменяются только package/branch bindings и локальное evidence; scalar-exit и BOM-free stdin fixes сохраняются. Один targeted regression, одна materialization и один separate verifier. Package 015 immutable, transaction 006 consumed. Spain egress, remote write, stage/install, config/issuance и AWG2 changes запрещены. После локальной готовности нужен новый exact preflight approval; прежние approvals не переиспользуются. Подробный текущий scope и вертикальный статус находятся в плане Phase 16; требования ниже сохранены как исходный контракт.

ИСТОРИЧЕСКАЯ ACCEPTANCE BOUNDARY — 2026-08-30, route/counter evidence commit `bb266df`

- Minimal isolated AWG3.1 runtime и non-Windows connectivity подтверждены, но это не разрешает Task 3B application integration и не является acceptance.
- Windows 11 / AmneziaVPN 5.0.1.5 проходит tunnel creation и handshake, но не application data plane; kill switch A/B результата не изменил. Это Windows upstream-class blocker, соответствующий по классу открытой официальной issue #3043, без утверждения окончательной root cause.
- Синхронный route/counter watcher подтвердил активные IPv4/IPv6 addresses, MTU 1280 и default routes, а также двусторонний рост интерфейсных byte counters во время одного HTTPS timeout. Отсутствие full-tunnel route исключено; точная Windows tunnel data-plane/session root cause не доказана. Evidence: `research/amn2/phase16-windows-awg31-active-route-counter-diagnostic-2026-08-29.md`.
- Official GitHub status refresh: `5.0.1.5` остаётся Latest release (`prerelease=false`) и уже установлен; issue #3043 открыта без maintainer-confirmed fix. Issue #3064 про fallback MTU 1376 не совпадает с доказанным MTU 1280 пилота. Stable release metadata не отменяет failed compatibility evidence. Evidence: `research/amn2/phase16-windows-official-upstream-status-2026-08-29.md`.
- Source-level refresh: 9 commits / 78 changed files между `5.0.1.5` и текущим `dev` не затрагивают Windows tunnel/route/session paths; обе ревизии используют `awg-windows/3.1.20260814`. Issue #3043 не имеет linked fix, #3050 является только corroborating Windows speed report, а #3073 про ranged H1-H4 не совпадает с fixed values пилота. Повтор того же engine path не является bounded remediation. Evidence: `research/amn2/phase16-windows-official-source-level-status-2026-08-30.md`.
- iPhone AWG3.1 connectivity прошёл, но quality gate failed; strict same-device AWG2 ↔ AWG3.1 A/B остаётся incomplete.
- Alternate-network iPhone retest сохранил HTTPS/YouTube/Telegram/reconnect PASS, но воспроизвёл существенное ухудшение upload, latency и jitter до и после reconnect. Вторая сеть сама download-limited, а baseline loss не измерен; результат блокирует acceptance, но не доказывает source root cause. Evidence: `research/amn2/phase16-iphone-awg31-alternate-network-quality-retest-2026-08-30.md`.
- Task 5 и Task 6 заблокированы до root-cause-bound correction, успешного Windows retest на официально поддерживаемом client path и полного Task 4.5.
- До закрытия этих gates запрещены speculative server/DNS/port/MTU/firewall/profile changes, Task 3B stage, install и general issuance. AWG2_UNTOUCHED.
- Canonical evidence: `research/amn2/phase16-windows-awg31-data-plane-regression-2026-08-29.md`, `research/amn2/phase16-windows-official-source-level-status-2026-08-30.md`, `research/amn2/phase16-iphone-awg31-quality-and-server-metrics-2026-08-29.md`, `research/amn2/phase16-iphone-awg31-alternate-network-quality-retest-2026-08-30.md`, `research/amn2/phase16-spain-transport-quality-ab-gate-2026-08-26.md`.

Выполнить единую Phase 16 внутри проекта VPS-OPS-LAB. Эта фаза объединяет ранее предполагавшиеся Phase 16 и Phase 17. Не создавать отдельную Phase 17.

Модель:
- GPT-5.6 SOL High;
- reasoning High;
- один основной агент;
- не использовать subagents и независимых reviewers.

Цель:
1. Довести семейство AWG3 до текущей ревизии 3.1.
2. Один раз собрать новый checksum-bound Phase 16 package.
3. Выполнить checksum-bound Spain read-only preflight.
4. После отдельного approval выполнить controlled stage.
5. После отдельного approval выдать ровно один операторский AWG3.1 pilot config.
6. Проверить его на реальном клиенте и принять либо откатить пилот.

РАБОЧИЙ КОНТЕКСТ

Основной проект:
C:\Users\SooL\Documents\VPS-OPS-LAB

Exact Phase 15 application source baseline:
- worktree:
  C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness
- HEAD:
  c01c2e34ca506102e485ee3fa50b9420de6e591a

Exact Phase 15 tooling/receipt baseline:
- worktree:
  C:\Users\SooL\Documents\VPS-OPS-LAB-phase15-local-package-bootstrap-readiness
- HEAD:
  1c945dcfcda92c2945fe71ee95f9219546c1f4e3

Phase 15 baseline package:
- package ID:
  phase15-dual-protocol-bootstrap-20260811-001
- package identity:
  00b56972a7e3f3423fb3a1d6437f877910b6f23c690fe9a398ce8263d74faf1d
- manifest:
  d99e6e6b7df651f7cda6f63de2ee9b2a353afef4bfe1c93e82391d5c48aac6df
- collector:
  e122315df1db91f654da0411ef08cadaa15a4a4e6318f1973444ec1d531b6465
- source-readiness receipt:
  0d45708c6aab6b7812ffa8ca05d052f1db175086f57c504b5af8e1f6a99c4eb8
- package-readiness receipt:
  040a9959f60ce725a9aa626d299d482b782da317fed11de0fd39193fe71f911d
- runtime lock:
  a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab
- test lock:
  52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235

Phase 15 package является baseline/readiness evidence. Не использовать его для AWG3.1 staging: текущие stage scripts намеренно inert, а application renderer ещё не содержит AWG3.1 fields.

УТВЕРЖДЁННОЕ ПРОДУКТОВОЕ РЕШЕНИЕ

- `awg3` — постоянное семейство протокола AWG 3.*.
- Текущая активная ревизия — exact `3.1`.
- Не создавать `ProtocolVersion.AWG31`, отдельный protocol profile или отдельную Phase 14.1.
- Сохранять `ProtocolVersion.AWG3 = "awg3"` и существующую dual-protocol модель AWG2/AWG3.
- Для новой выдачи использовать exact config revision `amneziawg_v3_1`.
- Старый `amneziawg_v3` считать известным предыдущим форматом, но не использовать для нового pilot issuance.
- Будущие `3.2`, `3.3` и другие `3.*` относятся к семейству `awg3`, но не принимаются автоматически: exact revision/runtime/capability/client admission остаётся обязательным.

OFFICIAL UPSTREAM BASIS

Использовать только как независимо реализуемый контракт, без копирования GPL client code/UI:

1. AmneziaVPN AWG3.1:
   PR #2984
   merge commit 44c10b39e38471a78f6090c96acffac626faec82

2. Android AWG3.1:
   PR #91
   merge commit d6cd6647465a9a593aa9ccadbbd20c44bf600d5b

3. Runtime AWG3.1:
   amneziawg-go commit
   1f50ad736ecca22a9bfc7b4606805ec9ca49fe48

4. Android pilot candidate:
   AmneziaWG v3.1.20260814
   release commit 5c16489e2cd9ed3a0a7a27c7445bba5238132f86

5. AmneziaVPN 5.0.1.5 официально опубликован как Latest release; GitHub
   metadata сообщает `prerelease=false`. Классифицировать его как
   `release_kind=stable`, но связывать release metadata отдельно от
   compatibility result: Windows data-plane FAIL запрещает global acceptance.

6. Не включать незавершённый `libagw` PR #3028.

TASK 0 — EXACT LOCAL BASELINE

Read-only подтвердить:

- оба exact HEAD;
- named branches;
- linked-worktree state;
- clean tracked worktrees;
- отсутствие unexpected source/tooling diffs;
- Phase 15 package/receipt identities.

Не удалять и не изменять unrelated untracked files.

При несовпадении exact baseline:
STOP и сообщить только конкретное несовпадение.

TASK 1 — BOUNDED LOCAL AWG3.1 DELTA

Application:

1. Сохранить `ProtocolVersion.AWG3 = "awg3"`.

2. Добавить exact config revision:
   `amneziawg_v3_1`.

3. Новая AWG3 issuance должна использовать только `amneziawg_v3_1`.

4. Расширить typed AWG3 config input двумя обязательными параметрами:

   RandomTrailers = on
   DisableCookies = on

5. Использовать точные native config keys:

   `RandomTrailers`
   `DisableCookies`

6. Значения должны иметь строгий typed boolean/on-off contract.
   Blank, malformed, contradictory, missing или unknown capability должны fail closed до генерации ключей, БД и peer/runtime side effects.

7. Связать в provider/receipt identities:

   - protocol_family = awg3;
   - protocol_revision = 3.1;
   - exact runtime identity;
   - exact capability set;
   - exact client application/platform/version/build;
   - exact compatibility evidence.

8. Runtime должен быть закреплён на официальном artifact/digest, реально поддерживающем UAPI:

   - random_trailers;
   - disable_cookies.

9. Не принимать runtime только по названию/tag. Нужны pinned digest и capability evidence.

10. Сохранить AWG2 golden bytes, AWG2 allocation, runtime, profiles, peers и Phase 14 contracts без изменений.

Tooling:

11. Реализовать существующие Phase 15 inert stage envelopes как Phase 16 controlled stage operations.

12. Новый package ID:

   phase16-awg3-family-3-1-spain-pilot-20260824-016

13. Stage scripts должны оставаться checksum-bound, state-bound, claim-bound, fail-closed и rollback-aware.

14. Никаких Spain/SSH/remote действий во время Task 1.

15. Package 014 остаётся checksum-immutable; package 015 сохраняет передачу `StageExpectedHost`, fixed runner STOP/outcome и local hash/length-only transport evidence. Transaction 004 consumed и не переиспользуется.

16. Application stage использует текущую БД `/var/lib/amn2-spain/amn2.sqlite3` и Python `sqlite3.Connection.backup`; зависимость от `sqlite3` CLI запрещена.

17. AWG3.1 runtime использует только `/opt/amn2-spain/docker/bin/docker` и `unix:///run/amn2-spain-docker/docker.sock` под `amn2-spain-docker.service`.

18. Server-only AWG3.1 config генерируется внутри controlled stage, имеет ноль `[Peer]` и не включает global issuance.

19. Controlled stage coordinator обязан проверять exact package manifest/identity, approval checksum, current-state checksum и canonical rollback-scope checksum; при failure удаляются только созданные транзакцией ресурсы, checksum-bound SQLite backup сохраняется.

20. AWG2 freshness policy остаётся 600 секунд и не изменяется этим исправлением.

21. Package 015: claim `consumed` означает только вход. `application_complete`, `runtime_entry`, `runtime_complete`, post-runtime AWG2 snapshot/equality и публикация outcome фиксируются раздельно в ordered transaction-bound `milestones.json`.

22. На failure coordinator сохраняет `failure-locus.json` только с allowlisted locus/class, milestone prefix, claim-entry classes, checksum bindings и normalized runtime-image class. Raw stdout/stderr/exception text не сохраняются; терминальный failure outcome остаётся фиксированным.

23. Milestone `*_entry` означает вход coordinator в вызов этапа; фактическое consumption подтверждается отдельным claim-entry class. Completion записывается только после успешного возврата stage subprocess, а не из status claim.

24. Mandatory rollback выполняется до публикации failure artifact; ошибка одного действия не пропускает остальные действия в прежнем rollback scope. `rollback_attempts_completed`/`attempts_completed_unverified` не равны resource readback или доказательству clean remote; ошибка отмечается как `attempt_failed`. Backup и transaction audit сохраняются.

25. Runtime-image class выводится из успешной bounded выдачи `docker image ls --all --digests --no-trunc`; неизвестная/неуспешная выдача даёт `query_failed`. Текст daemon errors не является доказательством отсутствия image.

Для текущего local `/GO` package 015 разрешены только TDD, локальные commits, одна materialization и один separate verifier. Ни раздел Task 2 ниже, ни прежние approvals не разрешают egress этой ревизии: новый Spain preflight требует нового exact checksum-bound `/APPROVE`. Stage/install/config/issuance запрещены текущим запуском.

TASK 1 TESTING

Использовать TDD, но только targeted tests:

- AWG3.1 typed config rendering;
- exact `RandomTrailers = on`;
- exact `DisableCookies = on`;
- missing/malformed/unknown revision and capability rejection;
- exact config revision mapping;
- runtime/evidence/build/provider content identity;
- stable release metadata does not override failed compatibility evidence or
  permit global acceptance;
- stage claim and rollback boundaries;
- AWG2 preservation tests непосредственно рядом с изменённым кодом.

Не выполнять:

- полный source suite;
- полный legacy tooling suite;
- четыре независимых review;
- whole-branch review;
- Codex Security whole-diff scan;
- повторные fresh-review rounds;
- многократную package materialization;
- повтор verifier после receipt-only commit;
- subagents.

Разрешены:

- один focused RED/GREEN cycle на изменяемый контракт;
- один targeted regression suite;
- `git diff --check`;
- exact changed-file scope check;
- короткий added-line secret scan;
- один package materialization;
- один package verifier pass.

При первом unexpected test failure:
- диагностировать;
- разрешён один bounded scoped correction.

При втором unexpected failure или расширении scope:
STOP и сообщить blocker, без самостоятельного fix/review loop.

TASK 1 OUTPUT

После PASS:

- сделать локальные commits;
- materialize package ровно один раз;
- verifier выполнить ровно один раз;
- вывести exact:
  - application source SHA;
  - tooling SHA;
  - package ID;
  - package identity;
  - manifest SHA-256;
  - collector SHA-256;
  - receipts;
  - runtime/client artifact identities;
  - targeted test result;
  - clean status.

Receipts изменять только при реальном изменении evidence.

TASK 2 — CHECKSUM-BOUND SPAIN READ-ONLY PREFLIGHT

Этот `/GO` явно разрешает после успешного Task 1 выполнить один Spain read-only preflight новым Phase 16 package.

Разрешено:

- один checksum-bound upload/transport нового пакета;
- read-only SSH;
- read-only OS/runtime/application/AWG2/resource inspection;
- проверка exact current-state SHA;
- проверка свободных AWG3 resources;
- проверка rollback prerequisites;
- удаление только созданных этой операцией временных transport artifacts.

Запрещено:

- stage;
- install;
- service mutation;
- container creation/start;
- firewall/routes mutation;
- DB migration;
- peer/config/QR creation;
- issuance;
- AWG2 restart/stop/change;
- live AWG3 runtime start;
- push.

При transport timeout:
- проверить отсутствие orphan upload process и partial remote artifact;
- не делать blind retry;
- STOP с точным transport status.

При любом preflight mismatch:
STOP без fix loop и без staging.

TASK 2 OUTPUT / STAGE GATE

После PASS подготовить:

- preflight receipt;
- observed state SHA;
- new package/checksum identities;
- exact intended stage resources;
- rollback scope.

Затем STOP.

Вывести один exact следующий approval:

/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_<PACKAGE_ID> IDENTITY_<PACKAGE_IDENTITY> MANIFEST_SHA256_<MANIFEST_SHA256> STATE_<STATE_SHA256> ROLLBACK_SCOPE_SHA256_<ROLLBACK_SCOPE_SHA256> TRANSACTION_<TRANSACTION_ID> MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED

Не выполнять stage без этого отдельного сообщения пользователя.

TASK 3 — CONTROLLED STAGE

Только после exact `/APPROVE ... STAGE`:

1. Stage application.
2. Stage isolated AWG3.1 runtime.
3. Не включать general issuance.
4. Не создавать peers/configs.
5. Не менять AWG2.
6. Проверить:
   - service/container health;
   - UDP/listener/interface/bridge/CIDR ownership;
   - runtime revision/capabilities;
   - application bootstrap;
   - AWG2 equality;
   - отсутствие recovery markers.

При failure выполнить только заранее ограниченный rollback из approval и подтвердить его readback.

После PASS — STOP.

TASK 3 OUTPUT / PILOT GATE

Зафиксировать:

- staged application/runtime identities;
- AWG2 equality receipt;
- health result;
- exact pilot client candidate;
- exact proposed pilot device/passport;
- exact rollback target.

Затем вывести один approval:

/APPROVE PHASE16 ONE_AWG31_OPERATOR_PILOT CLIENT_<APPLICATION_PLATFORM_VERSION_BUILD> RUNTIME_<RUNTIME_IDENTITY> PACKAGE_<PACKAGE_ID> MANDATORY_PEER_ROLLBACK_ON_FAILURE NO_GLOBAL_ISSUANCE

Не создавать peer/config до этого сообщения.

TASK 4 — ONE AWG3.1 PILOT

Только после exact pilot approval:

1. Принять ровно один exact client build.

2. Предпочтительный Android target:
   AmneziaWG v3.1.20260814, exact installed build readback required.

3. Если используется AmneziaVPN 5.0.1.5:
   - сохранить `release_kind=stable` по текущему official GitHub metadata;
   - сохранить Windows compatibility result как failed/blocked независимо от
     release kind;
   - только admin pilot;
   - не включать global acceptance.

4. Создать ровно один AWG3.1 operator-owned profile/peer/config.

5. Delivery:
   - только `.conf`;
   - не создавать QR;
   - не создавать `vpn://`;
   - не включать public/self-service/global issuance.

6. Config должен содержать:

   - HeaderProtectionKey;
   - ContentPaddingAddition;
   - RekeyAfterTime;
   - RekeyTimeout;
   - RejectAfterTime;
   - KeepaliveTimeout;
   - MaxHandshakeAttempts;
   - RandomTrailers = on;
   - DisableCookies = on;
   - AllowedIPs = 0.0.0.0/0, ::/0.

Не печатать и не сохранять private key, PSK, HPK или полный config в logs/receipts.

TASK 5 — REAL CLIENT ACCEPTANCE

Acceptance gate закрыт текущими Windows data-plane и Task 4.5 quality
blockers. Handshake, connectivity на одном клиенте или здоровые server metrics
не заменяют client data-plane/performance acceptance. Повторное открытие gate
требует успешного bounded Windows retest на официально поддерживаемом client
path по актуальному контракту выше, устранения причины quality failure,
стабильного AWG3.1 quality retest по заранее согласованным критериям и полного последовательного
same-device/access-network AWG2 ↔ AWG3.1 A/B. Task 3B application integration
требует отдельного checksum/state/rollback-bound approval и не может быть
предварительным обходом этих client gates.

С участием оператора проверить:

- `.conf` import;
- tunnel activation;
- handshake;
- IPv4 traffic;
- DNS;
- reconnect;
- Wi-Fi/mobile network switch;
- client restart;
- server/application restart, только если отдельно подтверждён в pilot approval;
- отсутствие AWG2 regression.

При pilot failure:

- остановить general progression;
- выполнить только заранее утверждённый pilot peer rollback;
- подтвердить отсутствие orphan peer/profile/reservation;
- AWG3 general issuance оставить disabled.

TASK 6 — CONCISE CLOSEOUT

Подготовить один краткий handoff:

- final source/tooling/package identities;
- preflight result;
- staged runtime result;
- exact client build;
- pilot result;
- AWG2 equality;
- rollback status;
- что разрешено дальше;
- что остаётся disabled.

Не выполнять:

- повторные full suites;
- новые independent reviews;
- whole-branch review;
- повтор package materialization;
- rollout на других пользователей;
- global AWG3 issuance;
- push.

ОГРАНИЧЕНИЯ ВСЕЙ PHASE 16

- Один новый чат и одна Phase 16.
- Не создавать Phase 17.
- Не повторять процедуры Task 7/Task 8 Phase 15.
- Не изменять AWG2 golden bytes/runtime/peers.
- Не останавливать AWG2 для тестов.
- Не менять Phase 14 contracts, кроме минимального additive AWG3 revision wiring.
- Не трогать unrelated untracked files.
- Не делать push.
- Не расширять scope на QR, vpn://, general import subsystem, libagw или global rollout.
- Любой scope expansion требует отдельного решения пользователя.

Ожидаемое время при штатном прохождении:
3–5 часов.

Начать с Task 0.
