# Журнал изменений AMN3 / VPS-OPS-LAB

Ведётся с 2026-09-13. Предыдущие записи ниже восстановлены по указанным receipts
и Git, это не полная история проекта. Даты — даты действий/подтверждений;
записи не означают deployment или новую выдачу. Текущая очередь — в
[плане Phase16](docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).

## 2026-10-04

- Продолжена разрешённая локальная подготовка переноса после публикации
  `373e3a1` (exact remote MATCH, pre-push PASS). В существующей
  [базе передачи](docs/PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md#source-transfer-contract-2026-10-04)
  зафиксирована исходная сторона M1/M2 по чистому AMN2 `6e68235`: 20 pinned
  файлов, карта всех 29 объявленных таблиц, фактические границы backup/restore,
  APP_SECRET_KEY, Phase13 copy-only history import, startup writes и local bot lock.
  Исторический backup-policy другой ветки отделён от текущей реализации;
  согласованность snapshot и restore для indefinite rows требуют целевой проверки.
  [Статический receipt](research/amn2/phase16-transfer-source-review-2026-10-04.json)
  не доказывает live schema или migration acceptance. Граница переноса запрошена,
  target/data ownership неизвестны; M1/M2 остаются открытыми. Единственный план
  обновлён без нового gate. Проверки: source/blob equality, table coverage 29/29,
  docs readback/links/diff/whitespace; тесты кода не повторялись. SSH, DB open,
  app imports, backup/export/import, package build, service/install и source edits: 0.
  AWG2/package016/issuance/client deferral и чужие 58 строк сохранены. Новый push
  требует отдельного exact разрешения.

- По exact разрешению выполнены normal pusha93b785 при EXPECTED_OLDdce10e0
  (fresh ref MATCH, CHANGELOG2 commits/pre-push PASS, NO_FORCE/NO_TAGS/NO_OTHER_REFS)
  и [private seal](research/amn2/phase16-bot-private-seal-execution-001-2026-10-04.json):
  один SSH0/30.000s/stdin0/stdout3201 complete/stderr0. Claim/result root:root0600
  после двух held-FD fchmod, metadata/ACL verified, result durable; новый root700
  audit с четырьмя root600 records. Parent0710/stage-root/payload/scratch0700 прежние.
  Все14 components/candidate PASS: ACCESS_PLAN_READY_NOT_APPLIED5278 objects,
  runtime/bootstrap content PASS4621files/2092bytecode. Final selected guards PASS;
  UNCLASSIFIED_ERROR в runtime reason — frozen telemetry mapping, не failure.
  Access apply/DB/app/services/install/activation0; original maintenance не
  повторялся, approval consumed once/no replay/auto rollback.
  M0f и проверенная основа передачи закрыты; навигация/единственный план/runbook/
  handoff синхронизированы. Далее M1/M2 при готовности target contract, новый
  diagnostic/install на Spain не назначается. App/data/target acceptance и Phase16
  не закрыты; client deferral, AWG2/package016/issuance и foreign58lines сохранены.
  Local receipt validator/digest/byte count PASS; docs-only readback/links/
  whitespace/secret guard, code suites не повторялись. Original57/FROZEN7 и
  consumed packet неизменны; фиксация результата локальная, новый push отдельно.

- По запросу оператора применены рекомендации upstream04.10 в существующем
  [intake](docs/UPSTREAM_INTAKE.ru.md#upstream-intake-2026-10-04) и базе передачи.
  Official PR183/200 merged SHA и release v1.7.3 metadata проверены12:38:48
  Europe/Moscow. MTU budget — уже записанный отложенный P3; дополнен HYB-AI-001
  критериями context/request/cache binding и delayed/mixed/incomplete snapshots.
  Active AMN2 source6e68235 clean: budget gap renderer сохраняется, но production
  defect/quality root cause не заявлены; чужая админка не обследована.
  Сохранены четыре planning-файла: AMN2/priority/rejected bytes прежние,
  hybrid изменён только в HYB-AI-001. Чужие58lines AMN2 не включены в commit.
  Navigation/единственный Phase16 plan/handoff синхронизированы, [receipt](research/amn2/phase16-upstream-intake-application-2026-10-04.json)
  фиксирует applied requirements отдельно от NOT_IMPLEMENTED/NOT_DEPLOYED.
  Docs-only readback/ссылки/whitespace и secret guard; code/tests не менялись,
  suite не повторялся. Seal manifest/remote/57original/FROZEN7 неизменны,
  claim absent; новый SSH/push/install0, M0f ещё требует exact approval.
  AWG2/package016/general issuance/client deferral/target unspecified сохранены.

- По exact разрешению выполнены normal pushdce10e0 при EXPECTED_OLD4d57e2d
  (fresh ref MATCH, CHANGELOG1 commit/pre-push PASS, NO_FORCE/NO_TAGS/NO_OTHER_REFS)
  и [private-boundary readback](research/amn2/phase16-bot-private-boundary-readback-execution-001-2026-10-04.json):
  один SSH0/2.578s/stdin0/stdout3855 complete/stderr0, BOUNDARY_READBACK_COLLECTED_NOT_ADMITTED.
  Claim/result root:root0644 regular single-link/ACLclear; payload/scratch700,
  parent root:61212/0710 и stage-root700 прежние, durable repair result hash verified.
  Selected bot/web stable/coordinator absent; contents/candidate/runtime rerun,
  writes/permissions/DB/app/services0. Approval consumed once, no replay.
  Подготовлен [separate two-file seal](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-private-seal-2026-10-04):
  exact preimage/held FD/rootprivate durable intent → только fchmod600 двух JSON,
  затем original readonly candidate/access-plan build с safe telemetry.
  Parent/stage/other DAC, app/DB/services/access apply/install не меняются;
  audit dir/четыре root600 records новые, max2 permission syscalls, SSH1/stdin0,
  remote180s/transport210s. Неопределённый effect → PARTIAL/UNKNOWN_NO_RETRY,
  manual rollback отдельный exact approval; old maintenance не повторяется.
  RED11+RED6→GREEN17; review P2 ctime/reason RED3→GREEN3, final20 PASS/0 SKIP
  за9.681s, independent review PASS/openP0P1P2=0; [verification](research/amn2/phase16-bot-private-seal-local-verification-2026-10-04.json).
  Portable tests only, native fchmod/fsync/new live NOT_EXECUTED; FROZEN7/original57
  сохранены, новый claim absent. Синхронизированы navigation/единственный план/
  runbook/handoff, далее M0f. Foreign ideas сохранены; AWG2/package016/general
  issuance unchanged, clients deferred, admin IN_FORMATION/target unspecified.
  Новый local commit не равен push/install, Phase16/integration/transfer не закрыты.

- По exact разрешению выполнены normal push4d57e2d при EXPECTED_OLD2410dea
  (fresh ref MATCH, CHANGELOG1 commit/pre-push PASS, NO_FORCE/NO_TAGS/NO_OTHER_REFS)
  и [v2 parent repair](research/amn2/phase16-bot-ancestor-repair-v2-execution-001-2026-10-04.json):
  один SSH0/12.297s/stdin0/stdout2748 complete/stderr0, parent root:61212/0710
  dev64770/ino262273 verified после двух held-FD permission syscalls, result durable.
  Installed content впервые PASS_SITE_CONTENT_ONLY/runtime+bootstrap PASS:
  4621files/2092bytecode, IMPORT_PATH_CONTENT; app/startup/access/admission не доказаны.
  Candidate STOP access_plan/private_boundary, exact failed object не сообщён.
  Child DAC/DB/app/services/install/activation/maintenance replay0; final guard
  selected units/boot/NSS PASS, approval consumed once, no retry/rollback/cleanup.
  Локальный writer допускает644 JSON при umask022; actual private metadata неизвестны.
  Подготовлен [short readonly boundary packet](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-private-boundary-readback-2026-10-04):
  metadata/ACL count четырёх fixed objects, held postrepair parent/stage, selected
  units и pinned durable result hash; без contents/sibling listing/candidate rerun.
  RED8→GREEN8; P2 helper-closure regression RED1→GREEN1, final9 PASS/0 SKIP
  за279.056s; independent review PASS/openP0P1P2=0. Native metadata readback не выполнялся.
  Frozen helpers/v2/actual trigger и original57 pinned, new claim/approval,
  remote45s/transport60s/SSH1/stdin0. Local verification/review — [receipt](research/amn2/phase16-bot-private-boundary-readback-local-verification-2026-10-04.json).
  New live NOT_EXECUTED; exact checksum approval/push разрешаются отдельно.
  Навигация/единственный план/runbook/передача синхронизированы, M0d завершён по
  parent/runtime и M0e остаётся. AWG2/package016/issuance и foreign ideas сохранены;
  Windows/quality/client tests deferred, admin IN_FORMATION/target unspecified.
  Integration/acceptance/transfer/Phase16 не закрыты.

- По разрешению оператора на оба ранее конкретно предложенных действия выполнены
  normal push2410dea при EXPECTED_OLD6be4149 (fresh ref MATCH, CHANGELOG1 commit PASS,
  NO_FORCE/NO_TAGS/NO_OTHER_REFS) и [parent repair](research/amn2/phase16-bot-ancestor-repair-execution-001-2026-10-04.json):
  один SSH3/7.125s, stdin0/stdout557 complete/stderr0, bound STOP_NO_REMOTE_CHANGE,
  reason sibling_inventory, audit_creation_attempted=false, operation=null.
  Approval consumed once; audit mkdir/write, fchown/fchmod, candidate scan, app/DB/
  services/install не начинались. Auto retry/cleanup/restore не выполнялись.
  Локально обнаружен пропущенный historical readback-guard22.09 в name whitelist;
  модель воспроизводит STOP, exact live names/наличие fixture не доказаны receipt.
  Подготовлен [отдельный v2](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-ancestor-repair-v2-2026-10-04):
  вместо name predicate каждый прямой child должен быть root:root0700 directory,
  no links/xattrs, max16, fixed retained-stage witness; unknown audit names SHA256.
  Те же parent-only0710/GID61212 held-FD syscalls после durable intent, identity/
  continuity/private siblings guards, затем original readonly candidate proof.
  Frozen consumed v1 core/gate/manifest и original57 не меняются; new OP/claim/approval,
  source materialization4 exact-shape patches/sha и trigger execution bound.
  RED9 → GREEN9; [final60 PASS/0 SKIP](research/amn2/phase16-bot-ancestor-repair-v2-local-verification-2026-10-04.json),
  независимый review PASS/openP0P1P2=0; isolated Windows launcher platform STOP и
  private-name redaction verified. Native Linux v2 NOT_EXECUTED; SSH требует нового
  checksum-bound approval (180s/210s/one-shot). Current plan/navigation/runbook/
  transfer handoff синхронизированы; AWG2/package016/issuance и foreign ideas diff
  сохранены. Parent/integration/quality/transfer/Phase16 остаются незавершёнными.

## 2026-10-03

- По exact approvals выполнены push6be4149 при EXPECTED_OLDe0bdf39 (fresh ref MATCH,
  CHANGELOG/pre-push PASS) и [ancestor facts](research/amn2/phase16-bot-ancestor-readback-execution-001-2026-10-03.json):
  SSH0/2.938s, stdin0/stdout3636 complete/stderr0, metadata-safe/ACL-clear.
  Single blocker `/opt/amn2-spain/bot-candidates` root:root0700, dev64770/ino262273,
  service UID/GID61212; other3 parents traversable, stage-root0700 expected private.
  Bot/web selected identities unchanged; DB/app/writes/permission/service actions0.
  Approval consumed, no retry. Full installed runtime verify этим packet не выполнялся.
  По /GO локально подготовлен [отдельный parent repair](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-ancestor-repair-2026-10-03):
  exact witness + held FD, known private sibling metadata/exclusive group guards,
  новый root-private durable audit intent/result → только parent root:61212/0710;
  затем original readonly candidate proof с safe return telemetry runtime verifier.
  Frozen57 artifacts, исходный access plan и consumed operations не изменены.
  New live NOT_EXECUTED, exact checksum approval required, remote180s/transport210s,
  one-shot; child DAC/maintenance/DB/app/services/install/auto rollback0.
  RED availability13+8 и два review regression RED→GREEN; [final51 PASS/0 SKIP](research/amn2/phase16-bot-ancestor-repair-local-verification-2026-10-03.json),
  independent review PASS после двух P2 validator fixes (no-change consistency,
  immutable parent_after identity). Native Linux repair не заявлен. Актуальный план/
  START_HERE/runbook/передача синхронизированы. AWG2/package016/general issuance и
  foreign ideas diff сохранены; client tests deferred, target admin in formation,
  integration/acceptance/Phase16 не закрыты.

- По exact approvals выполнены push e0bdf39 при EXPECTED_OLD5acb675 (pre-push2
  commits PASS, fresh ref MATCH) и [component diagnostic](research/amn2/phase16-bot-candidate-diagnostic-execution-001-2026-10-03.json):
  один SSH0/4.218s, stdin0/stdout5950 complete/stderr0, current access_plan
  STOP/AccessError/ancestor_access. Bot/web/process identities и retained records/
  journal/fences прежние; DB/app/writes/permission/service actions0. Approval consumed,
  повтор/repair/recovery не выполнялись. Expected wheels/venv PASS отделены от full
  installed runtime verify, который ещё не достигнут; original exception не доказан.
  Сохранены fixed ancestor security check и57 original artifacts. Локально подготовлен
  [ancestor facts packet](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-ancestor-facts-2026-10-03):
  четыре parents +stage root metadata/ACL-clear/validated identity, без content scans
  или candidate replay, remote30s/transport45s/one-shot. Новый SSH/mutation не разрешены.
  RED availability → GREEN real metadata/identity-boundary fixtures; итог37 PASS/
  0 SKIP, независимый review PASS, original policy preserved. Native Linux facts
  не исполнялись; hashes/closure/receipt validation в [local receipt](research/amn2/phase16-bot-ancestor-readback-local-verification-2026-10-03.json).
  Current plan, START_HERE и база передачи обновлены; общая админка в формировании,
  target contract отложен до её готовности; AWG2/package016 и foreign diff сохранены.

- По уточнению оператора «общая админка ещё в стадии формирования» исправлен
  преждевременный hold локальной работы на M1: target contract нужен при реальном
  переносе, сейчас продолжаются подготовка Phase16 и [база знаний](docs/PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md#forming-admin-2026-10-03).
  Подготовлен один [candidate component diagnostic](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#candidate-component-diagnostic-2026-10-03)
  поверх frozen readonly collector: memory wrappers сохраняют fixed inner step/
  reason/type без raw inputs/errors и снимаются в finally; original code/pins
  не меняются. Legacy proof исключён, DB/app/install/services/writes0,
  remote120s/transport150s, one-shot exact approval; SSH пока не исполнялся.
  RED/GREEN воспроизвёл потери nested settings/OS-command reason; cleanup/deadline,
  redaction, successful runtime/access proof и schema проверяются в [local receipt](research/amn2/phase16-bot-candidate-diagnostic-local-verification-2026-10-03.json).
  Итог40 PASS/0 SKIP; review P2 по `_require` literal reasons закрыт actual
  runtime/access RED/GREEN с отдельным component allowlist; inherited record/probe
  semantics не менялись. Независимый focused review PASS; финальные local checks
  и hash closure привязаны в receipt. Цель передачи,
  открытые client/quality gates, AWG2/package016 и чужой planning diff сохранены.


- По exact approval выполнен [maintenance readback](research/amn2/phase16-bot-maintenance-readback-execution-001-2026-10-03.json):
  один SSH0/4.031s, stdin0/stdout4408 complete/stderr0, bound
  READBACK_COLLECTED_NOT_RECOVERY; remote writes/DB/service actions0.
  Bot/web active/stable, coordinator not-found, durable access/coordinator/sequence
  records и fences absent. С bound source ordering установлена граница STOP до
  permission/maintenance sequence этого packet; original inner exception и DB/
  inherited deployed state не доказаны. Current readonly candidate STOP с generic
  candidate_collection_failed сохранён как открытое transfer limitation.
  Push5acb675 при EXPECTED_OLD0421da7 подтверждён, pre-push2 commits PASS.
  Новый execution record проверен против exact receipt/hashes/schema, source
  ordering и prior packet result; docs/routes/criticality plan обновлены, M0a закрыт.
  Original packets/receipts и foreign planning diff сохранены. Оба SSH approvals
  consumed, новых Spain diagnostics/retry/recovery/activation нет; дальше target M1.


- По позднему exact разрешению оператора выполнены push0421da7 при EXPECTED_OLD568c24cf
  (pre-push8 commits PASS, readback MATCH) и один [maintenance запуск](research/amn2/phase16-bot-maintenance-execution-001-2026-10-03.json):
  SSH3/22.937s, input345515/output657 complete, stderr0; bound STOP_OR_UNKNOWN_NO_RETRY.
  Owner statement подтверждён, approval consumed; DB/service/permission/activation
  state UNKNOWN, причина исходным entry не выведена. Никаких retry/restore/replay.
  Цель переноса сохранена; current plan/START_HERE/handoff/runbook уточнены.
  Подготовлен один [read-only readback](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-executed-2026-10-03):
  saved record hashes/allowlisted fields, fence/unit state и при отсутствии claims
  authenticated readonly unit/candidate/legacy probes; DB/app/services/writes0.
  Remote120s включает bootstrap, transport150s. RED/GREEN проверил deadline и
  redaction pinned raise reasons. Review P1 (legacy wrapper swallowing deadline)
  закрыт actual-wrapper RED/GREEN; итог34 PASS/0 SKIP в [local receipt](research/amn2/phase16-bot-maintenance-readback-local-verification-2026-10-03.json),
  native Linux readback не выполнен.
  Новый readback/SSH пока не разрешён и не исполнялся; исходный packet/receipts,
  package016 и чужой planning diff сохранены. AWG2 untouched по bound receipt,
  issuance disabled; новые local commits не опубликованы этим push approval.

- По уточнению оператора [исправлена цель и очередь Phase16](docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md#transfer-priority-2026-10-03):
  завершение проекта и перенос на другой сервер/сервис вместо обязательного
  обновления Spain. Подготовленный maintenance packet03.10 снят с очереди,
  прежний запрос его approval больше не актуален; code/manifest/receipt сохранены.
  [Основа передачи](docs/PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md#transfer-baseline-2026-10-03)
  обновлена: AMN2 HEAD6e68235/чистый status сверены локально, AMN3 tools0421da7 и
  прежний461 local PASS обозначены с target/OS/data ограничениями. Target пока
  не указан; фактический перенос/acceptance/closeout не выполнены. START_HERE и
  runbook направляют к единственной очереди M0–M5. Docs-only: readback, ссылки,
  diff/whitespace и сохранность чужого planning diff; tests не повторялись,
  packages не создавались. SSH/live DB/services/stage/install/activation/push0;
  AWG2/package016 untouched, general issuance disabled.

- Подготовлен [единый пакет обслуживания Phase16](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-packet-local-2026-10-03):
  verified runtime/source и OS-bootstrap provenance, effective settings, application
  writer/ownership admission, pending aggregates, durable stage permissions и service
  access probe. Manager-owned coordinator соединяет существующие8 операций через
  одноразовые claims, привязанные proofs и receipts; remote1560s/transport1590s,
  без retry/replay/restore. Существующие validators, receipts, candidate/package016
  и чужой planning diff сохранены. Права каталога БД не изменяются; code imports
  привязаны к проверенным bytes, stdlib paths — к исходному isolated interpreter.
  [461 affected PASS/0SKIP за146.610s](research/amn2/phase16-bot-maintenance-packet-local-verification-2026-10-03.json),
  RED/GREEN, isolated saved-payload closure и независимый focused review без оставшихся
  конкретных P1/P2. Реальные локальные files/SQLite/child processes; Linux/systemd
  границы моделируются, native acceptance и live rehearsal/migration не выполнены.
  Оператор подтвердил единоличный SSH-доступ; внешний bot poller вопрос и owner
  statement остаются открыты. Manifest/payload SHA заморожены, exact live approval
  ещё не получен. SSH/live DB/services/stage/install/activation/push0;
  AWG2 untouched, stage VERIFIED_NOT_ACTIVATED, issuance off, client tests отложены.

## 2026-10-02

- Зафиксирован ответ оператора «да» о наличии `@NeobyatnayaAMNZ_bot` в `/mybots`
  у BotFather: [уточнение ownership](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-facts-executed-2026-10-02).
  Подтверждён доступ к управлению ботом; external pollers/manual DB writers и
  exclusive maintenance ownership остаются UNKNOWN. Token rotation не согласована,
  исторический execution receipt сохранён. Локально уточнён порядок admission:
  сначала installed import-path content provenance, затем адресный доступ service
  user к stage. Реализация этого verifier ещё открыта. Проверки docs-only:
  readback/затронутые ссылки/diff; прежний171 PASS не повторялся. SSH/live DB/services/
  stage/install/activation/push0; AWG2/package016 untouched, client tests до утра03.10.

- [Единая maintenance sequence](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-sequence-local-2026-10-02)
  соединяет8 concrete операций с durable one-shot claim, fresh bound host-guard
  boundary, process/launch continuity, whole-step deadlines и receipt checks.
  Сбой не запускает recovery/restore/replay; результат сохраняется до completion,
  безопасный код причины не раскрывает raw exception. RED/GREEN и19 новых checks,
  [171 affected PASS/0SKIP](research/amn2/phase16-maintenance-sequence-local-verification-2026-10-02.json)
  на временных SQLite/files и systemd double. Независимый review выявил и после
  исправления закрыл P2: проверка срока/lease после admission и intent fsync
  предотвращает просроченное создание fence-файлов. Actual host admission, service-user
  доступ, persistent Linux coordinator process/packet и Linux acceptance ещё открыты;
  нового live gate нет. SSH/live DB/services/stage/install/activation/push0;
  AWG2/package016 untouched, stage VERIFIED_NOT_ACTIVATED, issuance off.

- [Maintenance facts исполнены один раз](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-facts-executed-2026-10-02)
  по exact approval: SSH exit0/9.406s, FACTS_COLLECTED_NOT_ADMITTED; сохранён
  normalized receipt, claim/result hashes сверены, approval consumed/no retry.
  Установлены фактические service identity/port/CIDR и selected process settings;
  host admission из них не следует. Ответ «Не уверен» сохраняет ownership/writers
  UNKNOWN. Доступ service user к root-private stage требует подготовки/проверки.
  Windows/Android/iPhone тесты перенесены оператором на утро03.10; acceptance открыт.
  Docs readback/links/diff проверяются отдельно; прежние152 tests не повторялись
  ради docs-only результата. SSH1, DB/services/remote writes/install/activation/push0;
  AWG2/package016 untouched, stage VERIFIED_NOT_ACTIVATED, issuance не включалась.

- Продолжен Phase16 `/GO`: [service adapters и следующий facts packet](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#service-operations-facts-2026-10-02).
  Candidate switch/admission, web launch/owned-loopback HTTP readiness и release
  связаны с migration proof, durable intents/receipts, source и whole-action budgets.
  RED/GREEN закрыл late response, source/receipt drift, отсутствие HTTP readiness,
  позднюю migration verification и неверный scalar busctl double. Одноразовый
  read-only SSH packet подготовлен локально: strict command allowlist, redaction,
  bound argv, claims/no retry; он не даёт admission/activation или writer-absence
  PASS. [152 affected PASS/0SKIP](research/amn2/phase16-service-operations-facts-local-verification-2026-10-02.json),
  self-review, actual local child/bootstrap, disposable SQLite, Linux boundaries
  substituted. Full coordinator/host admission/Linux acceptance остаются открыты.
  Exact одноразовое read-only SSH разрешено02.10, ещё не исполнено; push не разрешён.
  SSH/install/live DB/services/activation/push0,
  AWG2/package016 untouched, last stage VERIFIED_NOT_ACTIVATED, issuance off.
  Frozen target MATCH; старые receipts и чужой planning diff сохранены.

## 2026-10-01

- Оператор подтвердил однократное old55dc → 6e68235 исключение неизвестного
  завершения старых Telegram handlers. [Решение и local binding](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#legacy-stop-policy-bound-2026-10-01)
  связаны с точными source/operation/boot/journal/target/packet; supervisor/worker
  требуют этот контракт. Scope нельзя расширить rehash; drain не объявляется
  complete, автоматические replay/restore запрещены, остальные UNKNOWN → STOP.
  [120 affected PASS/0SKIP](research/amn2/phase16-legacy-stop-policy-local-verification-2026-10-01.json),
  два RED/GREEN, self-review. Полный coordinator/admission/recovery wiring и Linux
  acceptance остаются открыты. Повторный design approval не нужен; live approval
  не выдан. Frozen target MATCH, старые receipts и чужой planning diff сохранены.
  SSH/stage/install/live DB/services/push0; AWG2/package016 untouched,
  последний stage VERIFIED_NOT_ACTIVATED, issuance не включалась.

## 2026-09-30

- Продолжен T14c: [одноразовые data jobs](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-jobs-local-2026-09-30)
  сохраняют claim до manager request, связывают worker/result с intent/InvocationID,
  проверяют lease/boot/stopped-unit/fence и PID/policy внутри worker; при UNKNOWN
  сохраняют evidence без retry/cleanup/restore. Реальная temporary SQLite цепочка
  backup/rehearsal/migration через systemd double; source-bound cancellation test
  старого handoff. [109 affected PASS/0SKIP](research/amn2/phase16-bot-maintenance-jobs-local-verification-2026-09-30.json),
  RED/GREEN, self-review; Linux/systemd acceptance и полный coordinator ещё открыты.
  Old-handler исключение только предложено, не согласовано; неизвестный drain
  по-прежнему STOP. Frozen target MATCH; AMN2 source checkout и чужой planning diff
  сохранены. SSH/stage/install/live DB/services/push0; AWG2/package016 untouched,
  stage VERIFIED_NOT_ACTIVATED, issuance off. T14c не закрыт.

- Продолжен T14c: [реальные data adapters и Linux primitives](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-operations-local-2026-09-30).
  Durable intent/receipts, SQLite backup/rehearsal/migration, pending/missing-receipt
  guards; bounded child processes, systemd no-block polling/effective fence,
  isolated worker specification и candidate launch text. Исправлены queued-job
  и late-response ошибки; verification обнаруживает WAL-only DB изменения. [88 affected PASS/0SKIP](research/amn2/phase16-bot-maintenance-operations-local-verification-2026-09-30.json),
  RED/GREEN, real synthetic SQLite/child/files, self-review; Linux/systemd execution
  не проверено. Old55dc exit0/pending0 не доказывают handler drain; full sustained
  coordinator/admission/start/recovery остаются открыты, T14c не закрыт.
  Frozen target manifest MATCH; docs/links/diff/whitespace проверены.
  SSH/stage/install/live DB/services/push0, AWG2/package016 untouched, issuance off.

- Продолжен T14: [maintenance target/input binding](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-target-binding-2026-09-30)
  связывает pinned stage29.09 с прежним source/runtime verifier и фиксированными
  путями; typed inputs/ownership, same target/operation/boot и freshness формируют
  только неавторизованный coordinator manifest. Target digest сохраняется в
  Journal. Actual preview BLOCKED_UNKNOWN_PRECONDITIONS; CLI без --execute.
  [45 affected PASS/0SKIP](research/amn2/phase16-bot-maintenance-binding-local-verification-2026-09-30.json),
  RED/GREEN, real temporary journal/CLI, self-review; исправлены два RED с
  rehashed unsafe path и mismatched boot, добавлена expiry prepared inputs.
  Frozen manifests MATCH, unchanged DB/readback suites не повторялись;
  docs/links/diff/whitespace проверены. T14a/b готовы, T14c/full live executor и
  actual prerequisites ещё не готовы. SSH/data/stage/install/service/push0,
  AWG2/package016 сохранены, issuance off; новый design approval не требуется.

## 2026-09-29

- По exact approvals опубликован07e7769 (EXPECTED_OLD0574462, три CHANGELOG
  hook PASS, remote SHA MATCH) и выполнен один [stage readback](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#stage-readback-executed-2026-09-29):
  [VERIFIED_NOT_ACTIVATED](research/amn2/phase16-bot-stage-readback-execution-001-2026-09-29.json),
  SSH exit0/2.906s, stdin0/stdout1187/stderr0, полный validated receipt. Saved-stage
  success и текущие200 source/payload hashes, runtime40 metadata+1 bootstrap
  подтверждены; прежний UNKNOWN stage29.09 разрешён в этой границе. Повторная
  установка не нужна; старый failed execution receipt сохранён. Проверены
  claim/result hashes, bindings, event stdout reconstruction, docs/links/diff.
  Код/manifests не менялись, прежние28 local PASS без повтора. Новый install/
  remote writes/DB/services/activation0, SSH1/retry0; AWG2/package016 сохранены,
  issuance off. Maintenance и root cause SSH timeout не закрыты; дальше ранее
  согласованная локальная привязка maintenance, новый live scope не разрешён.

- После подтверждения оператора подготовлен [read-only stage readback](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#stage-readback-ready-2026-09-29):
  bound compressed argv без stdin, per-command SSH5/6, remote45s/local60s,
  один marker/claim; чтение saved receipt,159 source+41 payload hashes и static
  runtime40 metadata. Нет remote writes/app/candidate execution/install/DB/services.
  [28 local PASS/0SKIP](research/amn2/phase16-bot-stage-readback-local-verification-2026-09-29.json),
  RED/GREEN, реальный Windows argv/bootstrap с DEVNULL и corrupt-digest STOP,
  strict events/negative controls, preview/hash/length checks, self-review.
  Исправлена классификация отсутствующего parent: UNKNOWN; descriptor checks
  проверены моделями, Linux syscalls/SIGALRM не исполнялись. Frozen manifests MATCH, suites не
  повторялись; docs readback/links/diff проверены. Actual server stage/install
  UNKNOWN; VERIFIED не закрывает maintenance/activation. SSH/push/stage/install0,
  AWG2/package016 сохранены, issuance off; далее отдельные exact push/SSH approvals.

- Выполнен [локальный transport/EOF review](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#transport-readback-design-2026-09-29):
  successful22.09 использовал те же SSH5/1 и close stdin; installed ssh9.5p2/SHA
  зафиксированы без network call. Exact41104-byte frame с правильным marker
  дошёл в реальном local Python child до Windows platform STOP за0.110s,
  pipes complete/stderr0/no writes. Это не проверка SSH channel и не root cause.
  [Receipt](research/amn2/phase16-bot-transport-local-review-2026-09-29.json)
  содержит comparisons/ограничения/official references и inventory159+41.
  Предложен bounded readback существующего stage: argv/no stdin, per-command5/6,
  remote45s/local60s, receipt+current hashes/static metadata, без app/install/DB/
  services. Дизайн ожидает ответа; executor не написан. Readback/links/diff/hashes
  проверены, frozen code/suites сохранены. SSH/push/stage/install/activation0,
  AWG2/package016 сохранены, issuance off; server stage остаётся UNKNOWN.

- По exact approvals опубликован0574462 (EXPECTED_OLD8800fc6, hook/remote SHA
  PASS) и исполнен один [retained-stage](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#retained-runtime40-stage-executed-2026-09-29).
  [Результат](research/amn2/phase16-bot-retained-stage-execution-001-2026-09-29.json):
  UNKNOWN_NO_RETRY,12.297s, SSH255; local stdin41104/41104 complete, stdout0,
  тот же stderr49/SHA/server-alive timeout hint, что24/27.09. Малый frame отказ
  не устранил; root cause UNKNOWN. Remote directory мог появиться, stage/install
  не приняты; transport_json означает пустой stdout, не дефект remote JSON.
  Следующий scope — локальный transport review и подготовка readback возможного stage,
  без повторного install, cleanup или автоматической цепочки probes. Проверены
  evidence hashes/bindings/comparison/readback/links/diff; frozen code/manifests
  и suites не менялись/не повторялись. SSH1/retry0, service/DB/activation commands0,
  AWG2/package016 сохранены, issuance не включалась; result commit пока не pushed.

- Подготовлен [runtime40 из retained candidate](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#retained-runtime40-stage-ready-2026-09-29):
  frame41 104 bytes вместо30.5MB bundle,43 files с external immutable hash/size
  verification и descriptor-relative no-follow/owner/mode/link/race checks до
  stage. Новая private destination, offline40; старый candidate/test-venv48 и
  frozen stage001/transfer001 сохранены. Missing/drift STOP, retry/cleanup/fallback0.
  [23 local PASS/0SKIP](research/amn2/phase16-bot-retained-stage-local-verification-2026-09-29.json),
  RED/GREEN, actual immutable bundle validation/selection, CLI preview exit0,
  self-review; STOP receipt boundary усилена после RED. Linux syscalls/unshare/
  install моделировались, не исполнялись; server retained state ещё не наблюдалось.
  Manifest/receipt/readback/links/diff проверены; SSH/live reads/stage/install/
  service/DB/activation/push0, exact разрешения ещё нужны. Maintenance BLOCKED;
  AWG2/package016 сохранены, issuance off. Чужие ideas changes исключены из commit.

## 2026-09-27

- По exact approvals опубликован7e7d64a0 (EXPECTED_OLD9086bc3, hook/remote readback
  PASS) и выполнен один [transfer001](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#transfer-diagnostic-executed-2026-09-27).
  [Результат](research/amn2/phase16-bot-transfer-probe-execution-001-2026-09-27.json):
  UNKNOWN_NO_RETRY,34.313s, SSH255; READY+5 progress подтвердили5MiB,
  terminal отсутствует. SSH_SERVER_ALIVE_TIMEOUT_HINT; stderr49 bytes/hash
  совпал с stage001. Полная причина потери ответа UNKNOWN; pip/application
  в synthetic scope не запускались. Смысл hint проверен по official OpenSSH
  docs/source; это не exact Windows binary trace. Evidence/hashes/events/readback/
  links/diff проверены, suites не повторялись. Frozen scripts/manifests сохранены.
  По историческому PASS22.09 выбрано следующее локальное направление: runtime40
  из retained candidate с fresh immutable file verification, без bulk reupload;
  новый executor/approval ещё не готовы. SSH1/retry0, service/DB/stage/install/
  activation0, AWG2/package016 сохранены, issuance не включалась. Этот result
  commit ещё не pushed; прежнее push-разрешение на него не распространяется.

- Подготовлен [one-shot transfer diagnostic packet](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#transfer-diagnostic-ready-2026-09-27):
  30 485 208 synthetic bytes только в памяти, READY/1MiB progress/COMPLETE,
  strict event validator и новый exact approval/manifest/evidence binding.
  Optional bounded stdout observer сохраняет validated prefix при stdin failure;
  malformed/extra/duplicate fields и ложный COMPLETE не принимаются.
  [25 local PASS/0SKIP](research/amn2/phase16-bot-transfer-probe-local-verification-2026-09-27.json),
  реальные Windows children; default CLI preview PASS/SSH0, frozen001 MATCH.
  RED отсутствующих gate/observer, исправлен CRLF тестового stdout; self-review,
  hashes/readback/links/diff, без независимого review. Linux SIGALRM не исполнялся.
  Remote90s/local110s, no retry; settings SSH неизменны. Progress/synthetic payload
  отличаются от stage001: PASS не доказывает root cause, install или runtime.
  Новый SSH требует exact approval; live reads/service/DB/stage/install/activation/
  push0, AWG2/package016 сохранены, general issuance не включалась.

## 2026-09-24

- По «продолжай» подготовлен [отдельный diagnostic transport](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#transport-diagnostic-local-2026-09-24):
  несколько fixed stderr hints без raw strings, elapsed/last-write timing и
  termination action при прежних bounded process/IO limits. Новый module не
  подключён к live gate, frozen001 и manifests не менялись. RED →
  [11 local PASS/0SKIP](research/amn2/phase16-bot-transport-diagnostic-local-verification-2026-09-24.json),
  реальные Windows children; exact bootstrap отклонил synthetic partial frame
  до stage, script tamper до main. Исправлены test quoting и chunk-read fixture.
  Self-review, hashes/manifest/readback/links/diff checks; старые suites не
  повторялись. Stage001 root cause UNKNOWN, actual stage не принят; новый exact
  SSH packet ещё NOT_PREPARED. SSH/service/DB/stage/install/activation/push0,
  AWG2/package016 сохранены, general issuance не включалась.

- По exact approvals опубликован 68df5b9 (EXPECTED_OLD b28749a, hook и remote
  readback PASS) и выполнен один [runtime40 stage001](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#runtime40-stage-execution-001-2026-09-24).
  Результат **UNKNOWN_NO_RETRY**: SSH 255/stdin_write, неполная передача
  3 702 784/30 513 539 bytes, remote receipt отсутствует. Сохранён
  [execution record](research/amn2/phase16-bot-runtime40-stage-execution-001-2026-09-24.json)
  с exact local evidence hashes; root cause UNKNOWN, stderr raw не сохранялся.
  Source-order review подтверждает full bundle validation до stage claim/write;
  это не readback отсутствия каталога. Stage/install не приняты, повтор/cleanup
  не выполнялись. Проверены local claim/result, hashes, docs links/diff/whitespace;
  unchanged suites не повторялись, frozen code/manifests сохранены. Service/DB/
  activation commands0; AWG2/package016/AMN2 source не менялись, issuance не
  включалась. Следующий локальный шаг — transport diagnostic, новый SSH не
  разрешён. Этот result commit ещё не опубликован; approval 68df на него не действует.

- Подготовлен [exact runtime40 stage пакет](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#runtime40-stage-ready-2026-09-24)
  после публикацииb28749a. Новый executor создаёт отдельный private stage,
  устанавливает40 runtime pins из прежнего immutable bundle через offline wheels
  и unshare --net, проверяет metadata/import origins без app import; bot/web/DB
  и старый runtime не затрагивает. Local gate: preview default, checksum-bound
  fresh approval, exact target/evidence, одна SSH attempt без retry; false PASS
  отклоняется. [15 offline PASS/0SKIP](research/amn2/phase16-bot-runtime40-stage-local-verification-2026-09-24.json),
  real immutable bundle/CLI preview PASS; metadata child на synthetic app traps
  PASS. До исполнения исправлены wire paths Windows→POSIX. Self-review, artifact
  hashes, docs links/diff/secret review; frozen helpers/old suites не менялись.
  Stage approval ещё не предоставлен, SSH/stage/install/DB/service actions0.
  Maintenance prerequisites UNKNOWN/BLOCKED; general issuance disabled,
  AWG2/package016/AMN2 source сохранены. Local PASS не Linux stage acceptance.

## 2026-09-23

- По согласованному дизайну0928ca0 реализовано [локальное maintenance ядро](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#maintenance-local-core-2026-09-23):
  pinned DB backup/rehearsal и strict data delta всех18 old tables, explicit
  pre-poll restore с failed-file archive, durable intent/ownership journal,
  ordered coordinator, scoped systemd condition adapter и runtime40 snapshot
  verifier. [39 offline PASS/0SKIP,11.468s](research/amn2/phase16-bot-maintenance-local-verification-2026-09-23.json),
  synthetic rows/SQLite WAL; systemd только injected executor. RED/GREEN закрыл
  WAL artifact mode, intent bypass, SQL LIKE schema-name exemption; self-review
  учёл restore/forward race и servers AUTOINCREMENT при conflict. Docs readback,
  hashes/links/diff/secret review; независимый review не проводился.
  Полный live executor/callback bindings, actual writer inventory, import origins
  и Linux adapter execution ещё не готовы: local PASS не READY_TO_EXECUTE.
  SSH/live DB reads/writes/stage/install/service actions/activation/push0;
  AWG2/package016/AMN2 source сохранены, general issuance disabled. Дальнейшая
  локальная сборка остаётся в согласованном scope без нового design approval.


- Подготовлен [конкретный startup/fence/backup/recovery дизайн](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#startup-fence-backup-design-2026-09-23)
  после завершённого011 и публикации9cb5706. Source review6e68235 уточнил восемь
  seed plans и все upsert fields; exact old55dc243 web вызывает initializer
  при открытии repository. Рекомендованы краткий stop bot+web, server-local
  backup/rehearsal, сохранение existing business values и STOP при drift.
  Polling начинается до READY: после candidate start DB restore не автоматический.
  Описаны recovery states, approvals, пределы данных и плановые timing ranges.
  Проверки: exact source/clean Git, официальные SQLite docs, readback/links/
  diff/secret review; без code changes, повторов tests, SSH/backup/stage/install.
  Дизайн ожидает согласования; runner/migration allowlist не реализованы.
  AWG2/package016 и bot identity сохранены, issuance disabled, activation0.

- По exact SSH approval выполнен один [readback011](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-011-complete-2026-09-23)
  из local f33a5b4: **COMPLETE_WITH_LIMITATIONS**,10.609s, полный transport,
  validated receipt. Сохранены [полная разрешённая DB metadata и artifact hashes](research/amn2/phase16-bot-integration-readback-execution-011-2026-09-23.json).
  Offline сравнение18 таблиц совпало с exact old55dc243; candidate требует11
  новых таблиц/4 triggers и изменений3 таблиц. Source/dependencies равны010;
  observed holder — bot, PID bot/web стабильны; writer completeness UNKNOWN.
  Обновлены readiness/план: сбор закрыт, далее startup/fence/backup/recovery.
  Проверки: receipt validation, hashes, full metadata comparison, docs links/
  diff/secret review; без повторных suites, SSH retry или candidate startup.
  Push не разрешён/не выполнен; AWG2/package016 сохранены, issuance disabled,
  service actions/DB write attempted/stage/install/activation0. Semantic
  compatibility и live switch не подтверждены и не разрешены.

- По согласованию реализован [единый schema fix v3](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#schema-reader-v3-ready-2026-09-23):
  static ALTER/TRIGGER allowlist, typed expression/rowid/column index terms,
  trigger owner validation и versioned receipts; без SQL/rows/ослабления guard.
  Сохранены frozen v1/v2, добавлены exact-source full-schema fixtures с hashes.
  RED→**125 PASS**,18/29/29 таблиц без удаления объектов; полный receipt до48125B.
  Self-review выявил и исправил stale child-bootstrap bindings через RED/GREEN;
  независимого review не было. [Evidence](research/amn2/phase16-bot-integration-readback-v3-local-verification-2026-09-23.json)
  включает caps/invariance/binding/transport-fixture проверки; preview011 SSH0.
  Проверены AST guard delta, source/hash bindings, docs links/diff/secrets.
  Live schema/compatibility/recovery UNKNOWN; новый SSH/push требуют exact
  approvals. AWG2/package016 сохранены, issuance disabled, stage/install0.

- Завершена [локальная диагностика полного schema coverage](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#schema-coverage-diagnosis-2026-09-23)
  на exact old55dc243/candidate6e68235 и old→candidate in-memory fixtures:
  18/29/29 таблиц; expression index, четыре triggers и три ALTER-added columns
  не покрыты текущими reader/manifest/validator. Контрольные clones проходят
  полный validator после изоляции этих препятствий; это не production fix.
  Сохранены [evidence и hashes probes](research/amn2/phase16-schema-coverage-diagnosis-2026-09-23.json),
  причина ошибки measurement harness и предлагаемый единый bounded fix,
  ожидающий согласования. Проверки: source provenance, memory byte invariance,
  causal controls/receipt caps, self-review, docs readback/links/diff/secrets.
  Product code и frozen manifests не менялись; прежние108 PASS не повторялись.
  SSH/live DB/service actions/stage/install/activation0, AWG2/package016
  сохранены, issuance disabled. Live index identity/compatibility UNKNOWN.

- После exact push7275732 и approval выполнен один [readback010](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-010-stop-2026-09-23):
  **STOP_NO_RETRY / database_schema_expression_index**; полный transport,
  validated receipt. Зависимости впервые собраны:27 matched/13 different/
  missing0/extra3/1pth; source map прежняя. DB schema stage достигнут, полный
  shape/holders/units_after отсутствуют. Сохранён [execution record](research/amn2/phase16-bot-integration-readback-execution-010-2026-09-23.json)
  с claim/result hashes. Локально установлен неподдержанный collector'ом класс
  index metadata и найден expression index в старом source; exact live index
  UNKNOWN. Проверки: receipt validation/hash readback, source map comparison,
  links/diff/secret review; без retry или нового code fix. Service actions0,
  AWG2/package016 сохранены, issuance disabled, stage/install/activation0.

- По согласованию реализован [readback v2/gate010](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-010-ready-2026-09-23):
  METADATA cap256KiB/total8MiB, фиксированные причины ошибок этапов и DB child,
  без отражения произвольных local/remote exceptions. Старые hash-bound версии
  и manifests сохранены; SQLite/WAL/namespace guard не менялся. RED → **108 PASS**,
  отдельно40/40 runtime wheel metadata по pinned lock; [verification](research/amn2/phase16-bot-integration-readback-gate-010-local-verification-2026-09-23.json).
  Проверены preview SSH0, checksum bindings, version delta, ссылки/diff/secrets.
  Это локальный fix, не доказательство причины live009 или DB compatibility.
  Execution-010 не создан; push/SSH требуют exact approvals, service/stage/
  install/activation0; AWG2/package016 сохранены, issuance disabled.

- Подготовлен [ограниченный дизайн единого runtime/DB readback](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#consolidated-readback-design-2026-09-23).
  Локально сверены40 wheels с exact runtime lock; штатный reader отверг
  pydantic109397bytes и yarl103964bytes по METADATA cap65536. Установлена
  потеря core.Stop в generic remote_exception; причина live009 остаётся UNKNOWN.
  Proposed fix: METADATA256KiB при прежнем total8MiB и fixed stage/child reasons,
  с test/STOP матрицей; код ещё не менялся. Обновлены навигация статуса contract
  и ссылка из Phase16 plan. Проверки: bounded local reproduction, readback,
  ссылки, diff/whitespace и secret review; SSH/stage/install/activation0,
  immutable candidate/package016 и AWG2 сохранены, issuance disabled.

- [Локальная сверка source снимка009 с историей AMN2](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#source-history-reconciliation-2026-09-23)
  установила полное совпадение 102 Python-файлов/path set с 55dc243 после
  поиска по 361 commit изменения app (70 совпадений main.py). Независимая
  прямая проверка 102 blobs подтвердила результат; input receipt hash проверен.
  Уточнена [готовность bot-only switch](research/amn2/phase16-bot-candidate-runbook-2026-09-21.ru.md#switch-readiness-2026-09-23),
  исправлен устаревший статус Linux-проверки и добавлена ссылка из плана.
  Проверки docs-only: readback, ссылки, diff/whitespace и scope/secret review.
  Это не exact deployed release/runtime/DB identity; SSH, повтор тестов,
  package build/stage/install/activation отсутствуют, AWG2/package016 сохранены.

- Подготовлена [датированная база знаний для будущего единого VPN-проекта](docs/PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md):
  source/evidence/capability boundaries AMN2/AMN3, открытые Task3B/Windows/A/B
  и состав окончательной передачи после Phase16. Добавлена навигация в START_HERE.
  Проверены локальные Git HEAD/clean status, канонический план, source и ссылки;
  это docs-only snapshot, не новая приёмка или разрешение переноса/SSH/deploy.
  AWG2/package016 сохранены, общая выдача выключена; live-действий нет.

## 2026-09-22

- После exact push/approval [actual readback-009 завершился STOP_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-009-stop-2026-09-22):
  один SSH, полный transport, remote receipt прошёл local validation; reason
  `remote_exception`, доступны host/units_before/source. Dependency result и
  DB stage не достигнуты. Source против bound AMN2 6e68235 — DIFFERENT:
  102/126 ожидаемых файлов присутствуют, 24 missing, 24 different, extra0;
  workflow_worker/lifecycle отсутствуют. [Execution record](research/amn2/phase16-bot-integration-readback-execution-009-2026-09-22.json)
  связывает claim/result hashes. Подпричина exception и deployed revision
  UNKNOWN; retry нет. Retained отдельный bot candidate ZIP/manifest повторно
  hash-validated; следующий шаг — локальная сверка его runtime40 и shared
  source/DB rollback, не новая сборка или SSH. AWG2/package016
  сохранены, issuance disabled; package build/stage/install/deploy не выполнялись.

- После exact push и `_008` approval [actual integration readback снова UNKNOWN_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-008-unknown-2026-09-22):
  один SSH, полный stdin68077/stdout14614, exit3/stderr0; local diagnostic
  указал `units_before`. Полный stdout SHA совпал с `_007`, но raw ответ не
  сохранялся, remote reason/read stages/live side effects UNKNOWN; retry нет.
  [Execution record](research/amn2/phase16-bot-integration-readback-execution-008-2026-09-22.json)
  связывает claim/result hashes. Synthetic пример выявил возможный конфликт
  numeric signal values с local validator; production field не доказан.

- Подготовлен [actual readback gate-009](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-009-ready-2026-09-22):
  remote collector/payload/limits прежние, новый marker; локально в копии
  receipt принимаются только decimal `1..64` в `KillSignal`/`FinalKillSignal`,
  прочие поля проверяет прежний validator. 4 ожидаемых RED → 97 PASS,
  marker-only/manifest binding PASS, preview SSH0. Push и SSH требуют новых
  exact approvals; AWG2/package016 сохранены, issuance disabled,
  stage/install/deploy отсутствуют.

- После exact `_007` approval [actual integration readback завершился UNKNOWN_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-007-unknown-2026-09-22):
  один SSH, полный stdin68077/stdout14614, exit3/stderr0; JSON разобран,
  local validator отверг receipt (`receipt_binding`). Raw stdout не сохранялся;
  remote status/reason/read stages и live side effects UNKNOWN, retry запрещён.
  Нормализованный [execution record](research/amn2/phase16-bot-integration-readback-execution-007-2026-09-22.json)
  связывает claim/result SHA256. AWG2/package016 сохранены, issuance disabled;
  stage/install/deploy отсутствуют.

- Подготовлен [diagnostic actual readback gate-008](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-008-ready-2026-09-22):
  remote collector/payload/limits прежние, заменён только marker; при отказе
  local validator пишет фиксированное имя сбойной стадии без raw значений.
  Три ожидаемых RED, целевой итог93PASS, byte-for-byte и manifest binding PASS,
  preview SSH0. Широкий isolated discovery дал два import error без `pytest`;
  отдельные exact approvals нужны для push и одного SSH `_008`.

- Подготовлен [actual integration readback gate-007](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-007-ready-2026-09-22):
  после `_006` PASS сохранены collector, payload, source manifest и все лимиты
  gate-004; в remote supervisor меняется только exact approval marker.
  Новый runner/manifest/execution-007, consumed `_004` отвергается до claim.
  Шесть ожидаемых RED до реализации, шесть GREEN, общий итог90PASS; preview SSH0.
  Для одного production read-only SSH требуется новый exact approval. AWG2 и
  package016 сохранены, issuance disabled, install/stage/deploy отсутствуют.

- После exact `_006` approval [bound-frame SSH preflight завершился PASS](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#ssh-bound-frame-preflight-execution-006-pass-2026-09-22):
  одна SSH попытка, exit0, stdin68077/68077, stdout382, stderr0, remote SHA
  совпал; evidence hash-validated, retry0. Большой синтетический frame прошёл в
  момент проверки. Root cause `_003`/`_004` и production integration compatibility
  всё ещё UNKNOWN; следующий шаг — один новый actual readback, не повтор `_006`.
  AWG2/package016 сохранены, issuance disabled, install/stage/deploy отсутствуют.

- Подготовлен [bound-frame SSH preflight gate-006](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#ssh-bound-frame-preflight-gate-006-ready-2026-09-22):
  synthetic stdin ровно68077 байт как в `_004`, remote command проверяет SHA256
  и отдаёт только fixed PASS/STOP. Production reads/actions отсутствуют. Один SSH,
  timeout25s/no retry, новый marker/execution-006; `_005` не переиспользуется.
  Пять ожидаемых RED до реализации, шесть GREEN, общий итог84PASS; preview SSH0.
  Клиентская/production integration совместимость этим probe не подтверждается.
  AWG2/package016 сохранены, issuance disabled, install/stage/deploy отсутствуют.

- После exact `_005` approval [zero-input SSH preflight завершился PASS](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#ssh-zero-input-preflight-execution-005-pass-2026-09-22):
  одна попытка, exit0, stdin0, stdout293, stderr0, закрытый remote receipt;
  evidence hash-validated. Подтверждено подключение и короткая remote command
  без payload. Передача большого frame, причина сбоев `_003`/`_004` и production
  integration compatibility остаются UNKNOWN. Retry0. AWG2/package016 сохранены,
  issuance disabled, install/stage/deploy отсутствуют.

- Подготовлен [zero-input SSH preflight gate-005](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#ssh-zero-input-preflight-gate-005-ready-2026-09-22):
  один новый exact marker, один SSH/no retry, timeout20s и stdin0. Fixed remote
  command не читает production state и возвращает только closed receipt. Probe
  меняет одну переменную после execution-004: исключает 68077-byte framed stdin,
  чтобы отделить SSH/auth/remote-command path от payload transport. TDD5 GREEN,
  общий итог78PASS, preview SSH0; execution-005 отсутствует. Для запуска нужен
  отдельный exact approval. AWG2/package016 сохранены, issuance disabled,
  install/stage/deploy отсутствуют.

- После exact `_004` approval [actual readback execution-004 завершён
  UNKNOWN_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-004-unknown-2026-09-22):
  один SSH, exit255, stdin write0/68077, stdout0, stderr49/unclassified, remote
  receipt отсутствует. Gate зафиксировал `transport_stdin_write`; достигнутые
  production read stages и terminal observations UNKNOWN, retry0. Evidence
  hash-validated. Следующий шаг — минимальный zero-input SSH preflight с новым
  marker; он отделяет SSH/auth/remote-command от framed-stdin transport.
  AWG2/package016 сохранены, issuance disabled,
  install/stage/deploy отсутствуют.

- Подготовлен [actual readback gate-004](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-004-ready-2026-09-22):
  no stdout классифицируется до JSON parse; SSH reset/disconnect/KEX/banner
  получают только redacted HINT без raw stderr. Shared transport helper впервые
  hash/size-bound manifest. Новый marker/execution-004, consumed `_003` отвергается.
  Итог73PASS, independent review APPROVE, preview SSH0. Standalone pytest module
  не запущен из-за отсутствия pytest, новые paths покрыты integration unittest.
  Production readback не выполнялся; нужен exact approval. AWG2/package016
  сохранены, issuance disabled, install/stage/deploy отсутствуют.

- После exact `_003` approval [actual readback execution-003 завершён
  UNKNOWN_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-003-unknown-2026-09-22):
  один SSH, exit255, stdout0, stderr49/unclassified, remote JSON receipt нет.
  Достигнутые read stages и terminal observations UNKNOWN; raw stderr не сохранён,
  retry0. Evidence hash-validated. Следующий gate сначала получает local redacted
  transport classification/helper binding и новый marker. AWG2/package016
  сохранены, issuance disabled, install/stage/deploy отсутствуют.

- Подготовлен [actual readback gate-003](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-003-ready-2026-09-22):
  observed `systemctl --value` zero-byte output принимается как empty только
  после exit0/stderr0; nonempty output остаётся strict UTF-8/single terminal LF.
  Новый marker/execution-003, consumed `_002` отклоняется до claim/trust.
  RED→GREEN, итог71PASS, independent review APPROVE, preview SSH0. Production
  readback не выполнялся; нужен новый exact approval. AWG2/package016 сохранены,
  issuance disabled, install/stage/deploy отсутствуют.

- После exact `_002` approval [actual readback execution-002 завершён
  STOP_NO_RETRY](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-002-stop-2026-09-22):
  один SSH, complete transport, stderr0; bot ExecStartPre вернул exit0/stdout0,
  а gate остановился на newline format check. Root cause — локальная нормализация
  empty systemd property. Source/dependencies/DB/actions=0, retry0. Evidence
  hash-validated; следующий local gate-003 требует нового marker. AWG2/package016
  сохранены, issuance disabled, install/stage/deploy отсутствуют.

- После execution-001 STOP подготовлен [actual readback gate-002](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-002-ready-2026-09-22):
  каждая fixed allowlisted systemd property читается отдельно; STOP содержит
  только bounded role/property/stage/exit/byte metadata без raw output/env.
  Новый marker и execution-002, прежний `_001` не переиспользуется. Три RED→GREEN,
  итог 71 PASS, independent review APPROVE, preview SSH 0. Production readback не
  выполнялся; следующая попытка требует отдельного exact approval. AWG2/package016
  сохранены, issuance disabled, install/stage/deploy отсутствуют.

- После exact approval [actual integration readback execution-001 остановлен
  fail-closed](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-execution-001-stop-2026-09-22):
  один SSH, transport complete, stderr0, `STOP_NO_RETRY/unit_show`; partial
  содержит только host metadata. Source/dependencies/DB не читались, service
  actions0, retry0. Exact unit subcause UNKNOWN. Claim/result сохранены и
  hash-validated; новый diagnostic gate сначала требует local preparation и
  отдельный marker. AWG2/package016 сохранены, issuance disabled.

- Подготовлен [actual integration readback gate](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#actual-readback-gate-ready-2026-09-22):
  one-attempt/no-retry runner, exact target/payload/SHA binding, private read-only
  mount+network namespaces, schema-only SQLite и закрытые source/dependency/unit
  receipts. Абсолютный remote budget 50s включает cleanup/finalization и stdout
  flush; output caps раздельны. 69 targeted PASS после RED/GREEN, independent
  review APPROVE. Offline preview: SSH 0, execution-001 отсутствует; production
  DB/service/install/stage/deploy не затронуты. Следующий actual readback требует
  отдельного exact marker. AWG2/package016 сохранены, issuance disabled.

- Выполнен [bounded synthetic Linux readback guard gate](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#synthetic-linux-gate-pass-2026-09-22):
  hash/manifest/target-bound runner, remote supervisor, one-SSH/no-retry transport,
  whole-gate 45s/transport 60s/64KiB caps и mount+network-isolated fixtures.
  56 PASS после RED; independent review fixes закрыли claim order, deadline,
  process-group cleanup, exact receipt schema и retention semantics. Manifest и
  local receipt сохраняют command contract/exact command/hashes. После ответа
  оператора «продолжай» один SSH завершился exit0/stderr0: WAL read + OS write
  block и expected missing-SHM/journal STOP; persisted retained receipt PASS.
  Production DB/source/units/services=0. AMN2/AWG2/package016 не менялись,
  issuance disabled, production stage/install/deploy отсутствуют.

- Реализована [локальная portable часть integration readback](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#portable-implementation-2026-09-22):
  bounded metadata/schema helpers, namespace guards, offline pinned manifest
  builder и source synthetic Linux harness.42 portable PASS после RED; исправлены
  AST JoinedStr и CRLF metadata regressions. Manifest126source/runtime40pins;
  неизвестные names/env/DDL/rows не публикуются. Windows refusal/host-namespace
  refusal проверены, actual Linux guard не выполнен: WSL не установлен, Docker
  отсутствует. Общий live runner/transport/watchdog ещё не собран, --execute
  disabled; следующий local slice и границы явно сохранены. SSH/mount/live DB/
  services=0, AMN2/immutable artifacts не менялись. Проверки target unittest,
  hashes/readback/links/JSON/diff/secret/changelog; прежние suites не повторялись.
  AWG2/package016/issuance safety сохранены; production stage/install/deploy нет.

- По «продолжай» подготовлен [bounded integration readback contract Task3B](research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md):
  проверена source writer matrix, определены paths/fields/caps/STOP для deployed
  source/static dependencies/schema metadata/observed DB holders. Проект SQLite
  WAL guard использует отдельный private read-only mount view; capability и
  collector ещё не проверены/не реализованы. Runtime binding, semantic DB
  compatibility и writer completeness остаются UNKNOWN; это не server GO.
  Canonical plan/spec/gate/receipt синхронизированы. Checks readback/links/diff/
  secret/changelog; SSH/DB open/service actions=0, прежние suites не повторялись.
  Следующий локальный шаг — collector/manifests/synthetic guards до отдельного
  live approval. Linux PASS/AWG2/package016/issuance safety сохранены; production
  stage/install/deploy не выполнялись.

- По точному «продолжай» [isolated Linux gate завершён PASS](research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#isolated-linux-pass-2026-09-22):
  вторая test attempt/один SSH/execution-v2, exact bundle/source6e68235,
  test-venv/offline48pins/pip-check/metadata PASS, expected negative +6PASS/0SKIP,
  source hashes сохранены;47.487s remote. Retained test directory создан,
  production services/live DB/polling/activation=0; не deployment/acceptance.
  Lifecycle Task3 checkbox и canonical status синхронизированы, сохранён JSON.
  Остаток DB/source/runtime binding/writer fence/seed/rollback выделен в существующем
  contract; следующим будет локальная подготовка bounded readback, без нового SSH.
  Checks receipt/readback/counts/hashes, links/JSON/diff/secret/changelog;
  прежние baseline suites не повторялись. AWG2/package016/issuance safety сохранены.

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
