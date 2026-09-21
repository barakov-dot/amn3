# Журнал изменений AMN3 / VPS-OPS-LAB

Ведётся с 2026-09-13. Предыдущие записи ниже восстановлены по указанным receipts
и Git, это не полная история проекта. Даты — даты действий/подтверждений;
записи не означают deployment или новую выдачу. Текущая очередь — в
[плане Phase16](docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).

## 2026-09-21

- По «продолжай» [контрольный framed SSH probe v2 прошёл](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#readonly-probe-v2-pass-2026-09-21):
  одна попытка, exit0, exact32-byte SHA response, stderr0. Короткий framed path
  после PROGRAMDATA fix подтверждён; ZIP/venv/unshare/Linux signals не проверены.
  Remote writes/install/service/DB/deploy=0. Сохранён нормализованный receipt;
  подготовлен новый exact isolated test attempt contract с отдельным execution-v2
  claim, pending approval. Offline bundle/hash binding PASS, код/пакеты прежние,
  tests не повторялись. Checks readback/JSON/links/diff/secret/changelog;
  AWG2/package016 сохранены, общая выдача disabled, не acceptance.

- По «продолжай» выполнен [один no-write SSH probe и local root-cause check](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#programdata-diagnosis-2026-09-21):
  exit255/пустой output; allowlist исключал PROGRAMDATA. Локальный ssh -V
  воспроизвёл255, добавление одной переменной дало0, обратный контроль снова255.
  Исправлен общий local ssh_environment: PROGRAMDATA сохраняется, её отсутствие
  блокирует trust/claim/SSH, app secrets исключены. 2RED→45PASS и local ssh -V0.
  Подготовлен отдельный no-write probe v2, pending approval; повторного SSH нет.
  Remote runner/bundle/AMN2 не менялись; Linux evidence UNKNOWN, не deployment.
  Сохранены нормализованный receipt и scratch; checks hashes/readback/links/JSON/
  diff/secret/changelog. AWG2/package016/issuance safety сохранены.

- Исправлена [локальная потеря transport diagnostics](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#transport-diagnostics-2026-09-21):
  ранний exit/pipe error теперь сохраняет exit code, stage, размеры/prefix hashes
  и фиксированные stderr hints без raw logs. stdout/stderr разделены, общий cap,
  exclusive claim/no-retry/trust сохранены. Remote runner и bundle не менялись.
  RED7 → итог43PASS/0SKIP/0FAIL (11 transport +32 gate), offline previews и local
  framed probe PASS. Ad-hoc harness length исправлен30→32, source probe неизменён.
  Подготовлен exact no-write SSH transport probe, pending отдельного approval.
  SSH/remote writes/deploy=0; причина предыдущего SSH сбоя и Linux results UNKNOWN.
  Evidence/JUnit/scratch сохранены; checks links/JSON/diff/secret/changelog PASS.
  AWG2/package016 сохранены; AMN2 source/locks и прежние baseline suites не тронуты.

- По «продолжай» выполнен [один read-only recovery](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#recovery-readback-result-2026-09-21)
  после UNKNOWN test attempt: parent bot-candidates отсутствует, target/venv/
  results на момент чтения нет. Причина сбоя и quiescence UNKNOWN; не Linux PASS.
  Сохранены bounded collector/runner и hashes в локальном scratch; нормализованный
  JSON опубликован.9 local guard checks и1 Windows frame roundtrip PASS, без
  повторения baseline suites. Remote writes/service actions/test retry=0;
  source/approved runner/bundle/package016 не менялись, AWG2 сохранён.
  Предложена локальная доработка транспортной диагностики до нового test gate.
  Проверки: JSON/readback, docs links/diff/secret scan/changelog; не deployment.

- По точному «разрешаю» выполнена [одна isolated Linux попытка](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#execution-2026-09-21):
  exact hashes подтверждены, claim сохранён; SSH attempts=1, UNKNOWN_NO_RETRY /
  process_io, remote receipt отсутствует. Approval consumed, retry/cleanup=0.
  Target/test-venv/negative/6signals state UNKNOWN; production activation нет.
  Локальный synthetic child воспроизвёл потерю транспортной диагностики, но
  причину SSH-сбоя не установил. Код/AMN2/locks/packages не менялись; прежние
  suites не повторялись. Сохранены первичные evidence; планы синхронизированы,
  подготовлен точный read-only recovery scope с отдельным approval.
  Проверки: local result readback/JSON, hashes, docs links/diff/secret scan и
  changelog gate. AWG2/package016/general issuance safety сохранены.

- Подготовлен [исполнитель одного isolated Linux gate](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md)
  для immutable bot candidate6e68235: offline default, exact bundle/script SHA,
  fixed Spain trust, exclusive claims, one SSH framed upload, no-index pinned
  test-venv, network namespace, expected negative и6signal cases, caps/no retry.
  [Local evidence](research/amn2/phase16-bot-linux-runner-local-validation-2026-09-21.json):
  RED/GREEN, self-review path fix, итог32PASS/0SKIP/0FAIL; offline preview PASS.
  Linux signals/negative/venv/unshare/POSIX group cleanup NOT_RUN; server approval
  pending. Source/locks/packages неизменны, прежние101/94+6/312 не повторялись;
  SSH/remote writes/service/DB/poller actions=0. Сохранены scratch и новые evidence.
  Checks: targeted tests, exact artifact hashes, readback/links/diff/secret scan/
  changelog. AWG2/package016/general issuance safety сохранены; не deployment.

- Исправлено устаревшее заключение о [DefaultVPN2.0.2](research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md#defaultvpn-202-store-confirmed):
  после уточнения оператора свежий Apple RU/US lookup подтвердил выпуск
  21.09.2026 20:36:20 МСК, notes об улучшении стабильности, iOS>=16.
  Статус реестра STORE_RELEASE_VERIFIED/уже учтён в плане; прежние2.0.1 ответы
  сохранены только как устаревшие снимки. Source binding и конкретные fixes
  не доказаны. Проверки: official API, docs readback/links/diff/changelog;
  без client/runtime tests, установки, package или live изменений.

- Оператор уточнил [DefaultVPN 2.0.2](research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md#defaultvpn-202-operator-report).
  Версия сохранена как operator-reported; прежний API snapshot2.0.1 не принят
  за опровержение. Exact build/ОС/канал/source и исправления неизвестны.
  Реестр уточнён; проверки docs links/readback/diff/whitespace и changelog gate.
  Без нового network lookup, установки, runtime tests, package/live изменений.

- По сообщению об обновлении клиентов выполнена [узкая official store/release сверка](research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md#client-store-recheck-2026-09-21):
  AmneziaVPN iOS5.0.3 подтверждён в US Store (21.09), GitHub latest5.0.3.0
  прежний; RU lookup Amnezia resultCount=0. DefaultVPN RU/US пока2.0.1 от24.08,
  public head прежний; более новая версия из сообщения оператора не подтверждена.
  UPSTREAM_INTAKE дополнен без продвижения weekly cursor или повторной карточки
  format_version. Installed build/source и исправления импортера не доказаны.
  Проверки: official API/store readback, links/JSON-free docs diff/whitespace,
  secret scan и changelog gate. Runtime tests/установка/ретест/A/B/SSH не выполнялись;
  bot candidate, package016, ideas и monitor baseline неизменны.

- По «разрешаю» завершена [локальная подготовка bot candidate](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-candidate-local-preparation-2026-09-21)
  из AMN2 6e68235: отдельный immutable ZIP/manifest, runtime40/test-only8
  Linux wheels с hash/tag/metadata binding, [runbook](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md)
  и условный rollback без перезаписи shared source/DB/web. Package016 неизменён.
  Проверки: payload55/hash/ZIP readback PASS; четыре schema modules101 PASS,
  два synthetic historical schema transitions и old-code read/write PASS.
  Обнаружены существующие startup seed overwrites и неатомарность общего schema
  initialize; live DB/release compatibility и Linux OS tests не доказаны.
  [Evidence](research/amn2/phase16-bot-candidate-preparation-2026-09-21.json),
  [manifest](research/amn2/phase16-bot-candidate-manifest-2026-09-21.json).
  Source/locks не менялись; прежние94/6 и312 не повторялись. SSH/remote writes=0,
  нет install/stage/deploy/Telegram/cleanup; AWG2 и issuance safety сохранены.
  Следующий шаг — локальный runner isolated Linux gate перед отдельным server approval.
  Docs readback/links/diff/secret scan и changelog gate обязательны перед commit.

- По отдельному «разрешаю» выполнен [Spain bot readback v2](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#spain-bot-target-readback-v2-2026-09-21):
  один SSH, 60s/64KiB, READONLY_SNAPSHOT_COMPLETE; [JSON](research/amn2/phase16-spain-bot-readonly-v2-2026-09-21.json).
  Bot/web unit/process identities прежние; system Python3.12.3, x86_64,
  glibc2.39. Deployed main.py совпал с отдельным файлом 55dc243/910539e;
  новый worker/lifecycle и locks отсутствуют. 37 ABSENT/10 different/1 matching
  в system metadata не объявлены фактическими service dependencies: прежний
  backend использует отдельный site-packages tree. Candidate не установлен.
  Spec/очередь направлены на отдельный bot artifact/environment и rollback,
  без замены общего web/source/DB. Проверки: readback/hash comparison, links,
  diff/whitespace и changelog gate; tests не повторены. Нет третьего SSH,
  app import, secret/DB чтения, service/data mutation, stage/install/deploy/cleanup.

- После подтверждения Spain выполнен [один bounded read-only bot/web snapshot](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#spain-bot-target-readback-2026-09-21)
  с проверенным SSH trust, 60s/64KiB. Bot/web active; bot Restart=no,
  TimeoutStart=40s, TimeoutStop=90s; это properties, не доказанный stop budget.
  [JSON evidence](research/amn2/phase16-spain-bot-readonly-2026-09-21.json).
  Collector остановился на ошибочном ожидании app.web вместо исторического
  app.cli web serve; source/dependency binding не получен. Локальная сверка
  LF unit bytes совпала с обоими remote hashes. V2 исправлен и syntax-checked,
  но не исполнен; повторный SSH не автоматизирован и ожидает решения.
  Scope: нет service/data action, .env/token/DB/journal чтения, app import,
  package/stage/install/deploy/cleanup. Source 6e68235 и прежние tests сохранены.
  Spec/план обновлены; docs links/readback/diff/whitespace/changelog проверены.

- Оператор согласовал [пересоздание приложения существующего тестового бота](docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#existing-bot-recreation-2026-09-21).
  По историческому Phase13 receipt установлена привязка Spain/amn2-spain-bot.service;
  это не fresh target evidence. Подготовлен короткий маршрут: подтвердить instance,
  bounded read-only inventory, отдельный bot release, Linux synthetic signals,
  single-poller activation/restart и operator smoke. Общая DB/web/token/AWG2
  сохраняются; «нулевой бот» не интерпретируется как разрешение удаления DB.
  Source candidate 6e68235; исправлен устаревший абзац spec о якобы ожидающем
  исполнения source plan. Проверки: local source/receipt readback, links/diff,
  whitespace и CHANGELOG. SSH/Telegram/package/deploy/service/data changes нет;
  текущий недостающий факт — подтверждение, что целевой бот именно Spain.

- После «продолжай» проверена [доступность локальной Linux-среды](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#linux-environment-discovery-2026-09-21)
  для оставшегося lifecycle gate: WSL list exit=1 сообщает об отсутствии
  подсистемы, зарегистрированных distro нет, Docker/Podman в PATH отсутствуют.
  Inventory bounded 15s/query; один повтор исправил Unicode readback.
  Linux signals/negative control остаются NOT_RUN; требуется указать готовую
  среду/Python path. Source 6e68235, locks/units/dependencies неизменны;
  прежние 94 PASS/6 SKIP не повторялись. Проверки docs: ссылки/readback,
  diff/whitespace и changelog gate. Нет установки, SSH/VPS, signals службам,
  stage/install/deploy/cleanup; AWG2/package016/issuance safety сохранены.

- По подтверждению оператора выполнен [локальный lifecycle M4 slice](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-implementation-m4-2026-09-21):
  AMN2 1bd7f62→6e68235, четыре commits с CHANGELOG, exact-ref push/readback;
  stop до Settings/factory/READY, принятый drain и combined errors сохранены.
  Финальный affected regression: 94 PASS/6 SKIP/9.16s без warnings; Linux signals
  и negative control NOT_RUN. SOURCE_IMPLEMENTED_WINDOWS_TESTED, не M4 budget PASS.
  [Evidence JSON](research/amn2/phase16-bot-lifecycle-validation-2026-09-21.json)
  фиксирует actual argv/caps, RED/GREEN и отклонение task-local caps; scratch сохранён.
  Spec, subordinate plan и текущий Phase16 plan синхронизированы; исправлена
  prose-опечатка runtime lock hash по прежнему M3 JSON, locks/dependencies неизменны.
- Учтён [официальный AmneziaVPN 5.0.3.0](research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md):
  API stable/11 assets, Windows/Linux/macOS/Android; iOS rollout UNKNOWN.
  Узкая source delta (30 commits/224 files inventory): Windows AWG pin прежний,
  format_version не требует новой доработки AMN2; Windows traffic FAIL остаётся.
  Intake/Windows P1 обновлены без дублирования карточек/weekly cursor.
  Проверки docs: readback, links/anchors, diff/whitespace, secrets и changelog gate.
  Нет live SSH/Telegram, клиентских retests/install, package/stage/install/deploy/
  cleanup; AWG2/package016/issuance safety и отложенные quality/iPhone/A/B сохранены.

- После «Подтверждаю» design A отмечен DESIGN_APPROVED и подготовлен
  [план source реализации lifecycle M4](docs/superpowers/plans/2026-09-21-amn2-bot-startup-stop-lifecycle-plan.ru.md):
  controller/signal scope, runtime/factory guard и bounded synthetic signal
  evidence; точные paths/API/RED-GREEN, caps, один affected regression,
  inline execution и раздельные AMN2/AMN3 commit/push rules.
  [Receipt подготовки](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-plan-m4-2026-09-21),
  design и главный Phase16 plan синхронизированы. PLAN_READY_FOR_REVIEW,
  source execution ещё не разрешён/не выполнен. Проверки: source/fixture read,
  self-review coverage/interfaces, snippet syntax без исполнения, links/anchors,
  readback/diff/whitespace и secrets. AMN2 source/tests/units/dependencies неизменны;
  нет pytest, установки среды, OS signals, VPS/Telegram, package/stage/install/
  deploy/cleanup. M4 budget и все Phase16 prerequisites остаются открытыми.

- По следующему «приступаем» подготовлен [lifecycle design M4](docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#lifecycle-design-m4)
  со статусом DESIGN_PROPOSED / NOT_IMPLEMENTED: рекомендован единый stop owner
  до startup, factory-dispatch guard и сохранение accepted handler/job drain.
  Разделены количество нагрузки и wall-time, local cleanup и business outcome;
  PARTIAL/UNKNOWN не выданы за rollback или implemented restart fence.
  Определены ограниченный будущий source slice и synthetic acceptance cases;
  [receipt](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-design-m4-2026-09-21),
  main plan и список открытых M4 gates синхронизированы. Проверки: source read,
  inline design self-review, links/anchors, readback/diff/whitespace и secrets.
  Только документы; без code/tests/units/dependencies changes, Linux/systemd
  probes, target/Telegram, package build/stage/install/deploy или cleanup.
  Прежние evidence и все Phase16 ограничения сохранены; design ждёт review.

- После «приступаем» завершён [source-only stop-budget M4](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#stop-budget-m4-2026-09-21)
  кандидата AMN2 1bd7f62 и сохранённых pinned aiogram 3.30.0/Uvicorn 0.52.3.
  Зафиксированы ранний startup SIGTERM gap в доказательстве cleanup,
  неограниченные handler/factory/close paths, независимые writers и Uvicorn
  graceful timeout None по CLI default. Конечный budget не доказан; target
  properties UNKNOWN. В существующий contract добавлен минимальный future
  readback, main plan связан с receipt; следующий предмет решения — локальный
  lifecycle design, без выбора секунд/изменения units. Проверки: readback,
  ссылки/anchors/source lines, diff/whitespace и added-line secrets.
  Source/tests/locks/dependencies/units/package016 неизменны; тесты не повторены,
  нет VPS/Telegram/systemd execution, stage/install/deploy или cleanup.
  AWG2, прежние FAIL, отложенные iPhone/A/B и все Phase16 gates сохранены.

- После «согласовываю, продолжай» выполнена [локальная dependency-validation M3](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#dependency-validation-2026-09-21)
  кандидата AMN2 1bd7f62: отдельная Windows/Python 3.12.14 venv, неизменённый
  test lock с aiogram 3.30.0. Exact 48 test pins, включая 40 runtime pins,
  wheel hashes и pip check PASS; один existing worker/admission/drain набор:
  68 PASS за 8.27s, без warnings. [Полный нормализованный binding](research/amn2/phase16-web-bot-dependency-validation-2026-09-21.json).
  Contract/main plan обновлены: локальный lifecycle gap закрыт, target M3 и
  stop budget M4 остаются UNKNOWN. Проверены source/lock readback, ссылки,
  diff/whitespace и added-line secrets; scratch venv/evidence сохранены вне Git.
  Source/tests/locks/units/package016 и глобальная среда не менялись; полный
  312 suite не повторялся. Нет SSH/VPS/Telegram API, stage/install/deploy,
  выдачи или cleanup. AWG2 и все Phase16 prerequisites сохранены.

## 2026-09-20

- Подготовлен [integration-readiness gate web+bot в существующем Phase16 design](docs/superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#integration-readiness-web-bot),
  главный план связан с ним без второго execution plan. Кандидат AMN2 1bd7f62
  сверён с Git/remote; прежние 33 web и 312 bot PASS сохранены с пределами.
  Read-only source check выявил aiogram 3.30.0 в runtime lock против tested 3.28.2
  и недоказанный stop budget (30s в unit example не равны target state).
  Записаны startup/drain, artifact/activation/recovery/rollback boundaries,
  bounded acceptance scenarios и M1–M7 недостающих evidence. Проверки: readback,
  SHA256 locks, ссылки, scope/diff/whitespace, added-line secret scan.
  Только документация; нет новых tests/code/dependencies, merge/package/live,
  повторной выдачи или cleanup. Windows/quality/DNS/recovery gates сохранены;
  AWG2_UNTOUCHED, package016 immutable, general issuance disabled.

- По просьбе оператора подготовлен [полный handoff в новый чат](docs/NEXT_CHAT_PHASE16_2026-09-20.ru.md)
  после завершения bot worker: готовая команда, структура AMN3/AMN2, канонические
  планы/архитектура, проверенные HEAD/remote, 312 ранее выполненных PASS, клиентские
  ограничения, approvals и следующий local integration-readiness scope. START_HERE
  ведёт к новому снимку; второй execution plan не создаётся. Проверки: readback,
  локальные ссылки, согласованность, diff/whitespace; исходники/тесты, серверы,
  профили, пакеты и глобальные настройки не изменялись. Новый чат не создан.

- По подтверждённому [плану bot worker](docs/superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md)
  выполнены четыре этапа inline: one-thread SQLite ownership, bounded FIFO/async facade,
  handler lifetime и persistent runtime/delivery integration. Source AMN2 commits
  614dfd8, b9f5d4e, 28a4e43, 8bc8496 и review fix 1bd7f62 включают свой CHANGELOG
  и отправлены обычным push в codex/phase16-web-health-event-loop; remote SHA сверены.
  Baseline 278 PASS; итог 312 PASS без warnings. Независимый read-only review выявил
  две гонки до dispatch (queued cancellation и factory после close); обе воспроизведены
  RED и исправлены. [Полное evidence и ограничения](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-worker-реализация-и-проверки--2026-09-20).
  Docs проверены readback, локальными ссылками и diff/whitespace; source и docs
  фиксируются раздельно. Нет live/VPS/Telegram/реальной выдачи, package/stage/install,
  dependency/schema changes или deployment. Phase16 gates, AWG2 и package016 сохранены.

- Оператор подтвердил [письменный bot worker design](docs/superpowers/specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md)
  после commit b277154; статус DESIGN_APPROVED_NOT_IMPLEMENTED_NOT_DEPLOYED.
  Подготовлен [технический implementation plan](docs/superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md):
  четыре части с явными API, RED/GREEN, factory cleanup, queue/cancel/context,
  handler ownership и runtime/delivery integration; затем независимый review.
  План ожидает review и выбора метода; рекомендуется inline, subagents не запускались.
  Выполнены self-review покрытия design, readback, ссылки и diff/whitespace.
  Код AMN2 и runtime tests не менялись/не запускались; live/package/выдача вне scope.

- Подготовлен [design последовательного bot workflow worker](docs/superpowers/specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md)
  на baseline AMN2 2069e41: SQLite принадлежит одному потоку, ограниченная очередь
  на 8 outstanding jobs, async facade и явное владение lifetime handlers.
  Отмена до dispatch исключает job, после dispatch операция завершается; shutdown
  дожидается уже принятых handlers, включая delivery record, до закрытия БД/сессии.
  Учтены partial failure и отсутствие гарантии быстрого меню/жёсткого drain timeout.
  Статус DESIGN_DRAFT_READY_FOR_REVIEW: документ ещё не утверждён, код не реализован.
  Выполнены source/self-review, readback, проверка ссылок и diff/whitespace;
  bot/runtime tests, VPS/Telegram, package/stage/install не запускались.

- [DefaultVPN: получен ответ поддержки](research/amn2/phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md#ответ-поддержки-предоставленный-оператором--2026-09-20),
  предоставленный оператором. Восстановлен порядок русского письма из истории
  задачи; он отличается от английского черновика. Поддержка отрицает возможность
  имени при .conf и полное сохранение MTU/AWG через vpn://, без уточнения полей.
  Точные параметры, шаги экспорта и привязка source остаются неподтверждёнными;
  native delivery не включается. WAITING_REPLY заменён на CLARIFICATION_NEEDED,
  узкое уточнение подготовлено, не отправлено. Проверены readback, ссылки,
  согласованность и diff/whitespace. Source/tests/live/профили не менялись,
  повторных GitHub lookup, phone tests или отправок сообщений не было.

- [Bot SSH/SQLite: завершён source review](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-sqlite-и-границы-переноса--2026-09-20)
  на AMN2 2069e41: 41 прямой вызов 30 методов в handlers, общий SQLite,
  partial remote/local failure и запись доставки после Telegram send.
  Сравнены последовательный worker и разделение prepare/remote/finalize;
  рекомендован первый, выбор/design/реализация ещё не согласованы.
  Зафиксированы ограничения очереди, отмены, shutdown и необходимые synthetic
  проверки. Source/readback, ссылки и diff/whitespace проверены; pytest не
  запускался, AMN2 source/VPS/AWG2/package016/выдача не менялись.

- [Локальный web health fix AMN2](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#локальная-реализация-после-согласования--2026-09-20):
  после согласования оператора SSH-ожидание вынесено из event loop одного handler.
  Baseline 28 PASS; RED 2 ожидаемых FAIL + 3 guards PASS; GREEN 33 PASS.
  SQLite/auth/CSRF/summary/audit сохранены; новое CHANGELOG в source checkout.
  Source 2069e41 pushed в AMN2/codex/phase16-web-health-event-loop; remote SHA
  подтверждён. Независимый review без замечаний. Существующий warning httpx
  сохранён; общий suite и live действия не запускались. Документация проверена
  readback/links/diff, source checkout и пакет сохранены.

- DefaultVPN: оператор сообщил об отправке письма на support@dfvpn.com;
  статус SENT_OPERATOR_REPORTED / WAITING_REPLY, направление отложено как несрочное.
  Доставка и ответ независимо не проверены; исходный черновик сохранён.
- [Panel #174: применимость к AMN2](research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md):
  source review подтвердил синхронный SSH в async web health и условном bot revoke.
  Уточнена существующая карточка, предложен локальный fix только web health;
  bot SQLite и retry/cooldown требуют отдельного решения. Проверены официальный
  PR/diff, локальные source/tests, дубли в четырёх ideas-файлах и ссылки/whitespace.
  Код/тесты AMN2 и VPS не запускались и не менялись; weekly cursor не продвинут.

- [DefaultVPN: зафиксирована следующая граница](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#следующая-граница-после-name_fail-и-остановки--2026-09-20):
  оператор остановил переподключение и подтвердил отсутствие просмотра/экспорта
  одного профиля. Read-only AMN2 source check отделил готовый native exporter от
  двух legacy delivery call sites; source/tests/выдача не менялись.
- Точный source cb7ea0c не найден через commit lookup в двух официальных repositories;
  source/build binding и сохранность параметров остаются UNKNOWN. Подготовлен
  [запрос разработчикам](research/amn2/phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md)
  на support@dfvpn.com, не отправлен. GitHub issues отключены; PR #23 меняет
  заголовок настроек и не является исправлением импорта .conf. Проверки: source/API readback, пользовательские ответы, ссылки и diff;
  повторных runtime tests/import/connect, изменений VPS/AWG2/package016 нет.

- Уточнена версия [DefaultVPN с .conf NAME_FAIL](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#результат-conf--скриншот-получен-2026-09-20):
  UI показывает 2.0.1.1 (Aug 22 2026, cb7ea0c). Второй скриншот под тем же
  локальным именем отделён по SHA256 от первого. Версия iOS, параметры, restart
  и остановка переподключения не подтверждены. Проверка: оба изображения и hashes,
  readback/ссылки/diff; это docs-only, без повторного импорта, подключения или code fix.

- Зафиксирован [DefaultVPN .conf NAME_FAIL](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#результат-conf--скриншот-получен-2026-09-20):
  пользовательский скриншот после инструкции импорта показывает Server 1 вместо
  Neobyatnaya.NET и Reconnecting…. Предложено остановить попытку; её причина,
  остановка, build и сохранение параметров пока UNKNOWN. Native vpn:// NAME_PASS
  от 16.09 остаётся отдельным результатом. Проверка: изображение, SHA256, согласованность
  записи, ссылки и diff; код, runtime-тесты, выдача и серверы не менялись/не запускались.

- Завершён независимый review локальных recovery observations (b8bb1c8..86e4adc):
  Critical/Important/Minor замечаний нет. [План и границы](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md)
  переведены в LOCAL_IMPLEMENTED_TESTED_REVIEWED_NOT_LIVE_APPROVAL; очередь Phase16
  согласована с локальным результатом. Сохранено evidence 164 targeted PASS,
  проверены 53 локальные ссылки, diff и changelog; docs-only завершение без повторных тестов.
  Ручные Snapshot в обход parser, достоверность источника и live recovery не проверены;
  остальные подсистемы не объявлены прошедшими regression. VPS/AWG2/package016 неизменны.

- Добавлено [сравнение recovery snapshots](scripts/vps/phase16_recovery_observation.py):
  проверка контекста/порядка, отдельные исходы смены идентичности, появления,
  отсутствия в scope и UNKNOWN при query failure. Эти исходы не разрешают cleanup.
  RED: 39 проверок отсутствующей функции; GREEN: 164 PASS (137 новых + 27 metadata).
  [План](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md)
  и очередь обновлены; заключительный review пока ожидается. I/O/collector,
  live stage/install, AWG2, package016 и выдача остаются вне изменений.

- Реализован [локальный parser recovery observations](scripts/vps/phase16_recovery_observation.py):
  строгий canonical JSON до 64 KiB, проверка bindings/host/query/scope и пяти видов
  идентификаторов, неизменяемые снимки и фиксированная ошибка без исходного ввода.
  [План и evidence](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md):
  98 ожидаемых RED до появления модуля → 98 PASS. Сравнение ещё не реализовано;
  I/O/collector, ownership/quiescence GO, VPS, выдача и package016 не добавлялись/не менялись.

- Подготовлен [локальный recovery-план](docs/superpowers/plans/2026-09-20-phase16-recovery-evidence-local-plan.ru.md):
  строгие наблюдения и сравнение идентификаторов вместо принятия имён/PID за
  доказательство владения. По source записаны недостающие creation/process bindings,
  критерии будущего ownership/quiescence evidence и 2 локальные задачи с тестами.
  Реализация/collector/cleanup не выполнялись; metadata не разрешает live действия.
- План связан с единственной очередью Phase16. Проверка: адресный source readback,
  официальный контракт /proc/cgroup/inspect, самопроверка плана, ссылки и diff;
  runtime tests, SSH, stage/install и повтор старых diagnostics не запускались.

- Выполнена [сверка AWG Go](research/amn2/phase16-awg-go-pinned-runtime-review-2026-09-20.md):
  declared source старее двух fixes; отдельно обнаружен пробел image/source binding.
  SHA256 публичных manifest/config/layer проверены, бинарник прочитан в памяти без
  запуска; exact source не подтверждён. Применимость ограничена настройками шаблона.
  Добавлен один P2 candidate; weekly cursor, runtime, package016 и выдача не изменены.
- [Первый GitHub CI](docs/CHANGELOG_GATE.ru.md#первый-github-run--подтверждено-2026-09-20)
  для 3eb18f6 подтверждён SUCCESS по run/job/steps. Документирована граница между
  успешным workflow и отдельно настраиваемыми required checks. Локальные тесты
  повторно не запускались; проверки этого пакета — source/readback, ссылки и diff.

- Добавлен [автоматический changelog gate](docs/CHANGELOG_GATE.ru.md): проверка
  index перед commit и каждого нового commit перед push; поздняя общая запись
  не закрывает пропуски. Учтены датированные записи, формальные исключения с
  причиной, старая история и остановка при недостаточных Git-данных.
- Подготовлены версионируемые hooks и GitHub workflow с read-only token,
  полным checkout и закреплённым action SHA. Обновлены AGENTS и навигация.
  26 integration tests PASS, включая реальные hooks и push во временный
  локальный bare repository; исправлен относительный путь из вложенной папки.
  По review исправлены трактовка буквальных # строк после trailer и неявный
  lazy fetch Git: оба дефекта воспроизведены RED, добавлены regression tests.
  Hooks подключены только в активном worktree, config readback выполнен;
  2 markdown-hygiene tests и диапазон двух предыдущих commits PASS.
  Смысловое review остаётся обязательным. CI/required checks ещё не подтверждены;
  серверы, VPN, выдача и package016 не изменены.
- Синхронизирован DefaultVPN: NAME_PASS через vpn:// подтверждён скриншотом
  16.09, .conf и параметры остаются открытыми. В [чеклисте](research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md)
  подготовлен короткий вечерний сценарий без повторения paste/Windows проверок
  и без изменения рабочего профиля «Испания».
- Старый .conf в Temp отсутствовал; синтетическая fixture восстановлена в
  отдельной папке Downloads из ранее проверенного native ключа, 417 bytes,
  SHA256/readback и параметры проверены. В Git payload/ключи не добавлены.
- Read-only upstream на 20.09 14:40 MSK: #3043 без новых ответов, #3113 открыт
  и не слит. Ссылки/diff документации проверены; code/тесты повторно не запускались.

- Выполнен шаг 2 [format_version review](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md):
  NO_CHANGE_REQUIRED для текущего exporter. Записана матрица missing/0/1/future
  и malformed типов, source/build границы DefaultVPN. Целевые 52 offline tests
  PASS; exporter/legacy/delivery не менялись. Новый importer/restore не создаётся.


- По запросу оператора оформлены [реестр upstream](docs/UPSTREAM_INTAKE.ru.md)
  и [план format_version](docs/superpowers/plans/2026-09-20-upstream-format-version-review.ru.md),
  добавлены переходы из AGENTS/START_HERE и существующей P3-карточки.
  Уточнено: native exporter уже существует, missing version upstream принимает
  как 0; несовместимость не доказана. Первым идёт проверка применимости.
- Исправлены границы выводов weekly: неполные issues/PR/AWG coverage и 161-commit
  диапазон Panel не считаются полностью проверенными; IPv6 DNS не приравнивается
  к двух-IPv4 fix, а pooled SSH не является основанием отклонять event-loop isolation.
- Проверка пакета: адресный readback, локальные ссылки, diff/whitespace;
  runtime/code/tests, Phase16 gates, package016 и общая выдача не изменяются.
  Запись документации выполняется штатным apply_patch с одобренным повышением
  доступа; неисправность sandbox ACL этим не объявляется устранённой.

- В [кандидаты AMN2](ideas/candidates-for-amn2.md) добавлен отдельный P3 design
  candidate по upstream PR #3184: версионирование собственного JSON/envelope,
  отказ до side effects, import/restore tests и redaction. GitHub merge SHA и
  diff проверены. Это planning-only, не реализация или изменение Phase16.
- Проверка: readback и diff/whitespace; существующие профили, форматы, выдача
  и серверы не изменены. DefaultVPN .conf test остаётся незавершённым.

## 2026-09-13

### Правила и документация

- Создан этот журнал, добавлена навигация из START_HERE. В AGENTS.md введено
  обязательное обновление changelog в том же commit для существенных изменений
  кода, настроек, правил, инструкций и результатов проверок. Исключение для
  правок без изменения смысла требует явного обоснования в commit body.
- Проверка: readback, staged diff/whitespace и локальные ссылки. Изменения
  только документационные; автоматический commit/CI gate не установлен.

## 2026-09-12 — ретроспективно

### Проверено: импорт Windows

- AmneziaVPN local 5.0.1.5 + PR #3113: имя Neobyatnaya.NET и metadata MTU1280
  сохраняются; в backup двух профилей совпали 45 ожидаемых полей каждого.
  Повторный импорт создаёт одноимённый дубль.
- AmneziaWG official 3.1.0 x64: имя и MTU1280 сохраняются после полного выхода;
  UI-параметры проверены, одноимённый повторный импорт отклоняется. Пропуск
  PersistentKeepalive=0 объяснён официальным serializer, исправление не требуется.
- DefaultVPN остаётся NOT_RUN на iOS. Windows import PASS не закрывает Windows
  traffic FAIL/quality FAIL и не переключает delivery. AWG2_UNTOUCHED.
- По просьбе оператора в тестовом .wsb включён clipboard и добавлена guest-only
  настройка EN/RU Alt+Shift. Статические проверки PASS; фактическая работа обоих
  механизмов отдельно не подтверждена.
- Evidence: [receipt](research/amn2/phase16-windows-import-acceptance-2026-09-12.md),
  commit `4447dc4`; push в согласованную ветку подтверждён readback SHA в задаче.

## 2026-09-11 — ретроспективно

### Проверено: начальный импорт в Sandbox

- Исправленная сборка AmneziaVPN запущена в offline Sandbox; правильное имя
  сохранилось после полного открытия, отдельный MTU1280 подтверждён в preview.
  Полная проверка backup выполнена позже, см. 2026-09-12.
- Evidence: [build/import receipt](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commit `78e8815`.

## 2026-09-09 — ретроспективно

### Подготовлено: локальная сборка

- Собрана AmneziaVPN 5.0.1.5 с upstream MTU fix PR #3113. Одна попытка сборки,
  0 циклов исправлений; ZIP CRC и SHA проверены. Build Tools/SDK установлены
  по разрешению, Qt/Conan/Python изолированы по каталогам.
- Подготовлен offline Sandbox launcher. Рабочий VPN не заменён; service installer
  candidate на хосте не запускался. Сам build PASS не означал import/traffic PASS.
- Evidence: [receipt и SHA](research/amn2/phase16-amneziavpn-pr3113-windows-build-2026-09-09.md),
  commits `fe31852`, `5560e5d`.
