# Phase 16 — текущий execution plan

## Актуальный порядок и gates — 2026-09-08

Единственный текущий execution status Phase 16. Исходный baseline документационной
оптимизации: `2d63b5572d8bca6aa6adc6dbfc6c043e6d6884d5`. Локальные исправления ниже
синхронизированы по source commit `b6c5fd7f188473b1f2c079115a3cfd4d4459f01a`;
это не package/deployed revision и не указание текущего checkout будущих запусков.
История вынесена в отдельное приложение; её GO/approvals не являются командами.

### Границы доказательств

- Android/iPhone connectivity и iPhone reconnect подтверждены исторически.
  Windows: adapter/routes присутствовали, прикладной трафик FAIL; гипотеза
  отсутствующих маршрутов отвергнута. Совпадение с issue не доказывает root cause.
- Quality FAIL; strict Spain AWG2/AWG3.1 A/B неполон и отложен оператором.
  Не запрашивать повторно iPhone/две сети до возврата оператора к этому этапу.
  ICE timeout и незавершённый speedtest не считать измеренным packet loss.
- [Критерии v1](../../PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md):
  `CRITERIA_APPROVED_NOT_EXECUTED`. Методика m1 —
  `METHOD_DRAFT_BLOCKED_NOT_EXECUTED`; согласование чисел не равно live approval.
- HTTP/ICMP helper — только offline evidence; DNS lifecycle — чистая модель,
  не native adapter. [DNS source check](../../PHASE16_ACCEPTANCE_HISTORY_2026-09-08.ru.md#official-dns-source-check-2026-09-07):
  `OFFICIAL_SOURCE_CHECK_COMPLETE_DNS_BRIDGE_STOP`. Общий hard-wall 2000 ms
  не доказан. Не создавать bridge/worker/новую модель. Критерии не ослаблены.
- [Локальный DNS-fix генератора](../../../research/amn2/phase16-local-dns-generator-two-ipv4-compatibility-2026-09-05.md)
  завершён; profiles/package016 не изменены. Это не исправление Windows/quality
  и не DNS measurement bridge. Развёртывание/реальная генерация требуют approval.
- Minimal runtime не завершает application integration. Прежние stage-попытки
  STOP; отсутствие ресурсов в recovery receipt не доказывает успешный rollback.

### Завершённые локальные исправления stage — 2026-09-08

Изменены только mutable source и offline-тесты. Package016 не изменён и не
пересобран; эти исправления не развёрнуты и не закрывают client/quality gates.
Числа ниже — результаты уже выполненных целевых RED/GREEN, не новый прогон.

| Commit | Исправление | Offline evidence |
| --- | --- | --- |
| `db9f4a0` | Application cleanup удаляет staging только после его эксклюзивного создания текущим запуском; прежний staging сохраняется | 2 ожидаемых падения → 5/5 PASS |
| `e97eda2` | Обнаруженная ошибка cleanup отражается как `rollback_failed`, остальные шаги очистки продолжаются | 3 ожидаемых падения → 10/10 PASS |
| `b6c5fd7` | Неподтверждённое завершение application/runtime stage, включая timeout, даёт `recovery_required`; координатор не выполняет cleanup | 7 ожидаемых падений → 13/13 PASS |

Источники: [application shell](../../../scripts/vps/phase16_application_stage_remote.sh),
[coordinator](../../../scripts/vps/phase16_controlled_stage_coordinator.py),
[ownership suite](../../../tests/test_phase16_application_staging_ownership.py),
[failure-locus suite](../../../tests/test_phase16_controlled_stage_failure_locus.py).
Ownership suite исполняла shell на временных fixtures; POSIX modes на Windows не
проверялись. Failure-locus suite исполняла реальный coordinator с временными файлами
и заменой внешних OS-команд; это не реальное прерывание Linux-процессов или live rollback.

**Граница recovery остаётся открытой.** При `recovery_required` координатор сохраняет
package, имеющийся backup и ресурсы; сохранённый package блокирует новый stage даже
с другим transaction ID. Выходной результат остаётся `recovery_required` и при сбое
записи audit-файлов. Это не доказывает наличие backup до его создания, сохранность
данных от действий дочернего процесса или остановку оставшихся процессов.
Автоматический recovery и управление деревом процессов не реализованы.
`rollback_failed` означает обнаруженную ошибку cleanup; прежний `rolled_back` на
остальных путях не заменяет readback (`attempts_completed_unverified`).
Не удалять retained package ради обхода блокировки и не повторять закрытые тесты
на неизменном коде. Для recovery сначала нужны отдельный согласованный scope,
доказательство прекращения операций и ownership ресурсов; live-чтение, сигналы
и удаления требуют соответствующих точных approvals.

### Локальное именование импорта — 2026-09-08

По подтверждённому оператором scope добавлен явный client-specific export API
в AMN2 source commit `b3ed202ba118adb36c474eab5722065ea420d274`:
AmneziaWG — `Neobyatnaya.NET.conf`; AmneziaVPN/DefaultVPN — Amnezia envelope с description.
[Результат, исходники и границы](../../../research/amn2/phase16-client-import-naming-research-2026-09-08.md#выполненная-локальная-реализация-после-подтверждения-оператора).
51 целевой offline-тест PASS. Реальный import/сохранность параметров в клиенте
не проверены, DefaultVPN MTU остаётся отдельным ограничением. Delivery handlers,
общая issuance и package016 не переключены; код не развёрнут. Следующая граница
этого пакета — изолированный import acceptance, не Windows traffic test и не A/B.
Recovery-parser реализован только локально (см. P1 recovery ниже); #3043 — ожидание реакции.

Дополнение 2026-09-09: [проверочный лист трёх клиентов](../../../research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md)
подготовлен, не исполнен. Windows UI runtime повторно не инициализировался
(deny-read ACLs); импорт не запускался. GitHub API: после комментария оператора
в #3043 новых комментариев нет. Следующий шаг — восстановить доступность штатного
UI и подтвердить изолированную среду, затем выполнить import acceptance без подключения.

### Результат ручного импорта и MTU — 2026-09-09

[Наблюдения и source trace](../../../research/amn2/phase16-amneziavpn-native-import-mtu-trace-2026-09-09.md):
AmneziaVPN 5.0.1.5 NAME_PASS; native-import MTU preservation FAIL (1280 → 1376
в метаданных). Прослеженный Windows backend использует метаданные; raw просмотр
продолжает показывать 1280. Фактический MTU адаптера не измерен. Оператор сообщил
случайную попытку подключения; connectivity не подтверждена. Другие клиенты
и повторный импорт не проверены. Следующий шаг — bounded upstream MTU reproduction
и поиск дублей завершены: PR #3113 OPEN, патч применён к временной копии source; последующая Windows-сборка завершена ниже. AMN2 compatibility note исправлено, 52 offline PASS. Публикация комментария заблокирована GitHub integration HTTP 403; черновик сохранён в receipt. Остаются проверка исправленного клиента в отдельной среде и публикация через доступную учётную запись. Delivery не переключать, Windows traffic/A/B не повторять.

### Клиентский импорт — обновлено 2026-09-20

[Итоговый receipt](../../../research/amn2/phase16-windows-import-acceptance-2026-09-12.md):
AmneziaVPN local 5.0.1.5 + PR #3113: имя после restart PASS, сохранённый MTU1280
PASS; 45 expected fields в каждом из двух backup-профилей совпали. Повторный
импорт создаёт одноимённый дубль. AmneziaWG official 3.1.0 x64: имя/MTU после
restart PASS, UI parameters совпадают; повторный импорт отклонён. Нулевая строка
keepalive пропускается штатным serializer; source trace завершён.
DefaultVPN/iOS: 16.09 оператор подтвердил NAME_PASS через synthetic vpn://;
20.09 после инструкции synthetic .conf import получен скриншот с **Server 1**:
**NAME_FAIL** этого пути. На экране Reconnecting…, предложена остановка попытки;
причина запуска UNKNOWN; остановка подтверждена оператором «ОСТАНОВИЛ». По следующему скриншоту версия
приложения: **2.0.1.1 (2026-08-22, cb7ea0c)**. Параметры/restart не проверены.
Предыдущий native NAME_PASS сохранён отдельно; рабочую «Испанию» не менять.
Оператор не нашёл просмотр/экспорт отдельного профиля. Параметры UNKNOWN;
cb7ea0c не разрешился в двух официальных source repositories. Export API уже готов,
но legacy delivery не переключён. [Ответ поддержки получен от оператора](../../../research/amn2/phase16-defaultvpn-2.0.1.1-compatibility-question-draft-2026-09-20.md#ответ-поддержки-предоставленный-оператором--2026-09-20):
.conf имя задать нельзя; сохранение MTU/AWG через vpn:// не подтверждено
(ответ «Нет» без перечня полей). Source и путь экспорта остаются неясны;
уточнение подготовлено, не отправлено. DefaultVPN отложен, native delivery заблокирован.
[Материалы и короткий сценарий](../../../research/amn2/phase16-client-import-acceptance-checklist-2026-09-09.md#defaultvpn-подтверждённое-и-вечерний-тест--2026-09-20).
Локальная проверка не закрывает Windows traffic/quality gates и не разрешает
переключить delivery. iPhone connectivity/A/B не возобновляются этим импортом.
Clipboard/EN-RU setup подготовлены по просьбе оператора, UI-работа ещё не подтверждена.

### TASK_PLAN_BY_CRITICALITY

1. **P0 — quality/A/B, ОТЛОЖЕНО.** После возврата оператора: подтвердить импорт
   существующего d7 и физическую сеть, метод/лимиты/outcomes; затем exact approval
   на последовательный same-device/same-app/same-access-network Spain A/B.
   Новая выдача и автоматический повтор не разрешены.
2. **P1 — Windows, BLOCKED.** Следующий bounded test только при значимом изменении
   официального клиента/engine ИЛИ новой проверяемой гипотезе: записать отличие
   от закрытых диагностик и исходы, получить live approval. Повтор kill-switch A/B,
   поиска отсутствующего адаптера или общего IPv4 HTTPS без новой гипотезы не нужен.
   21.09 учтён официальный [релиз 5.0.3.0 и узкая source delta](../../../research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md):
   Windows/Linux/macOS/Android assets подтверждены; Windows AWG pin прежний.
   Новый binary traffic PASS и iOS rollout не подтверждены; retest не запускался.
   Upstream receipts действуют на дату чтения, не заменяют новый readback.
   [Согласованный комментарий #3043](../../../research/amn2/phase16-windows-issue-3043-comment-2026-09-08.md)
   опубликован вручную; readback 2026-09-08 подтвердил публикацию. Не отправлять повторно.
3. **P1 — DNS measurement, STOP.** Пересмотр методики — только отдельный scope
   при реальной необходимости. Не наращивать tooling ради открытого gate.
   Полный runner/endpoint manifest/stability/server coverage не готовы.
4. **P1 — controlled-stage recovery, КОНТРАКТ СОГЛАСОВАН; НЕ РЕАЛИЗОВАН.**
   [Контракт v1](../specs/2026-09-08-phase16-controlled-stage-recovery-contract.ru.md):
   `CONTRACT_APPROVED_NOT_IMPLEMENTED_NOT_EXECUTED`. Локальная защита и её
   offline-проверки завершены выше. Inventory, прекращение операций, адресная
   очистка и readback — раздельные gates. Реализация и live-операции требуют
   отдельного scope/approval; `recovery_required` не разрешает cleanup.
   **R1 read-only compatibility review завершён, не реализация:**
   [результат и точные исходники](../../../research/amn2/phase16-recovery-helper-compatibility-review-2026-09-08.md).
   Старые collector/driver найдены, checksum подтверждены; повторный поиск/аудит
   не нужен. Parser не принимает новые outcomes; старый runner привязан к прежней
   транзакции и не доказывает quiescence/сохранность pilot. Ограниченный
   code scope parser выполнен по последующему подтверждению оператора:
   [локальная реализация и 27 offline PASS](../../../research/amn2/phase16-recovery-helper-compatibility-review-2026-09-08.md#локальный-parser-после-подтверждения-оператора--2026-09-08).
   Старый collector/driver не подключён; ownership/quiescence и live recovery не готовы.
   20.09 подготовлен [локальный план observations/identity comparison](2026-09-20-phase16-recovery-evidence-local-plan.ru.md):
   Обе локальные задачи реализованы: parser и сравнение снимков, 164 synthetic PASS
   вместе с metadata regression; независимый review завершён без замечаний. Сравнение metadata не становится ownership/quiescence proof или cleanup GO.
5. **P2 — integration, BLOCKED предыдущими gates.** После клиентских и quality
   доказательств: checksum/state/rollback-bound approval, проверка persistence,
   restart policy, leaks и границ отката. Затем Task 5 и Task 6.

   Локальный reviewable gate подготовлен 20.09 в [существующем Phase16 design](../specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#integration-readiness-web-bot):
   LOCAL_DEPENDENCY_SLICE_PASS / INTEGRATION_EXECUTION_BLOCKED / NOT_DEPLOYED.
   Текущий source candidate AMN2 6e682356ed14a62d636ee58039fd3a389e794809;
   source/remote сверены после локального lifecycle slice. M3 baseline — 1bd7f62.
   21.09 после отдельного согласования выполнена локальная M3 validation:
   aiogram 3.30.0, exact 48 test pins/40 runtime pins, hashes и pip check PASS;
   68 worker/admission/drain tests PASS на Windows/Python 3.12.14.
   [Receipt](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#dependency-validation-2026-09-21).
   Target environment и stop budget остаются UNKNOWN (30s только в unit example).
   Source/dependency binding, startup/drain, recovery/activation/rollback,
   bounded acceptance и полный список M1–M7 находятся в этом контракте.
   Локальная часть M3 закрыта. 21.09 после «приступаем» завершён
   [source-only M4](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#stop-budget-m4-2026-09-21):
   startup SIGTERM handler появляется только внутри polling; общий drain bound
   отсутствует, pinned Uvicorn graceful timeout по CLI default None. Карта
   writers и минимальный future readback contract находятся в существующем
   design; target properties не получены, M4 не закрыт. Source/tests/locks/units
   неизменны, тесты не повторялись.
   После следующего «приступаем» подготовлен [lifecycle design A](../specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#lifecycle-design-m4):
   один stop owner до startup, factory-dispatch guard, принятый drain сохраняется;
   H=8/Q=8 не становятся секундным SLA. PARTIAL/UNKNOWN требуют отдельного
   recovery, operator gate не выдаётся за implemented restart fence.
   Оператор подтвердил design A после commit 8ba7e5d. Подготовлен
   [source implementation plan](2026-09-21-amn2-bot-startup-stop-lifecycle-plan.ru.md):
   3 задачи inline, точные файлы/API, RED/GREEN, bounded synthetic signal child,
   один affected regression и source/docs commit/push rules.
   По следующему подтверждению оператора план исполнен inline: controller,
   startup/factory guard, owned cleanup и сохранение combined errors.
   **SOURCE_IMPLEMENTED_WINDOWS_TESTED**: 94 PASS/6 SKIP, 9.16s, без warnings;
   source 6e68235 pushed/readback. [Actual receipt](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#lifecycle-implementation-m4-2026-09-21).
   Linux six-case signals/negative control NOT_RUN; tests подготовлены, среды не
   устанавливались. Следующий отдельный scope — compatible Linux evidence либо
   target readback. M4 stop budget/writer/restart gates открыты; units/locks неизменны.
   [Local environment discovery 21.09](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#linux-environment-discovery-2026-09-21):
   WSL не установлен, registered distro отсутствует; Docker/Podman не найдены
   в PATH. Нужны название готовой локальной Linux-среды и Python/venv path;
   новая установка не разрешена текущим scope. Повторного pytest не было.
   Позднее оператор согласовал [пересоздание приложения существующего нулевого бота](../specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md#existing-bot-recreation-2026-09-21).
   Spain/amn2-spain-bot.service подтверждён оператором. После отдельного «разрешаю»
   [readback v2 завершён](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#spain-bot-target-readback-v2-2026-09-21):
   bot/web active, bot Restart=no/TimeoutStop=90s; Python3.12.3/x86_64/glibc2.39.
   Worker/lifecycle/locks в deployed source отсутствуют; system metadata не
   доказывают service dependency binding. По следующему «разрешаю» завершена
   [локальная подготовка отдельного bot candidate](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-candidate-local-preparation-2026-09-21):
   source6e68235, runtime40/test-only8 Linux wheels, immutable ZIP/manifest,
   101 schema PASS и synthetic compatibility двух исторических схем.
   Startup меняет schema/стандартные планы и не является целиком атомарным;
   actual DB compatibility, writer fence и production rollback ещё не доказаны.
   По «продолжай» [exact-bundle isolated Linux runner подготовлен](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md):
   32 локальных guard PASS, offline preview/hash binding PASS, SSH=0.
   После точного «разрешаю» выполнена [одна попытка](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#execution-2026-09-21):
   SSH attempts=1, UNKNOWN_NO_RETRY/process_io, remote receipt не получен.
   Approval использован; повтор/cleanup не выполнялись. Linux negative/6signals,
   unshare/test-venv и test-directory state UNKNOWN; deployment не подтверждён.
   После «продолжай» [read-only recovery выполнен](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#recovery-readback-result-2026-09-21):
   один SSH, parent bot-candidates отсутствует; target/test-venv/results отсутствуют
   на момент чтения. Причина первого сбоя и quiescence UNKNOWN; Linux PASS нет.
   По «продолжай» [локальная transport diagnostics доработка завершена](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#transport-diagnostics-2026-09-21):
   43PASS, exit/pipe stage/размеры/hashes/hints сохраняются без raw stderr; SSH=0.
   Original remote script/bundle unchanged; причина первого SSH-сбоя не доказана.
   По «продолжай» [probe v1 выполнен один раз](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#programdata-diagnosis-2026-09-21):
   exit255/stdout0/stderr0. Local ssh -V доказал причину startup failure — allowlist
   исключал PROGRAMDATA. Исправлен общий helper; 2RED→45PASS и local ssh -V exit0.
   По следующему «продолжай» [probe v2 PASS](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#readonly-probe-v2-pass-2026-09-21):
   один SSH, exit0/32-byte exact SHA, stderr0; короткий framed remote path доказан.
   По следующему «продолжай» [22.09 isolated Linux gate PASS](../../../research/amn2/phase16-bot-linux-isolated-gate-2026-09-21.md#isolated-linux-pass-2026-09-22):
   одна новая test attempt/execution-v2, offline48pins/pip/metadata PASS,
   expected negative +6signals PASS/0SKIP, source hashes сохранены,47.487s remote.
   Test-venv создана и retained; production service/DB/poller/activation=0.
   По «продолжай»22.09 [bounded readback contract подготовлен локально](../../../research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md):
   exact paths/fields/caps/STOP, source writer matrix и проект SQLite/WAL guard;
   По следующему «продолжай» [portable core/manifest реализованы](../../../research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#portable-implementation-2026-09-22),42 local tests PASS.
   Synthetic Linux harness подготовлен, но Linux guard не проверен (локальной
   Linux среды нет); общий live runner ещё не собран, CLI execution disabled.
   По следующему «продолжай» [bounded synthetic Linux gate готов локально](../../../research/amn2/phase16-bot-integration-readback-contract-2026-09-22.ru.md#synthetic-linux-gate-ready-2026-09-22):
   supervisor/transport, manifest+target binding, whole-gate deadline, точные
   receipt/retention semantics, mount+network namespaces; независимый review
   исправлен отдельными regression tests, итог 56 PASS; SSH=0. Следующая граница — отдельное точное approval на один synthetic
   SSH. Actual DB readback не включён и получит собственный gate после Linux PASS.
   Linux signal gate закрыт; namespace/WAL gate и live DB compatibility/writer fence/production rollback открыты.
   Рабочие службы/DB/poller исключены из gate; Linux на АРМ не требуется.
   AWG2/package016 неизменяемы, general issuance disabled; activation запрещена.

Независимая локальная подготовка 20.09: [Panel #174 / SSH event loop review](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md)
выявил синхронный SSH в async web health handler. После согласования оператора
исправлен только этот AMN2 handler: 2 RED → 33 PASS целевого web/health набора,
review без замечаний, source 2069e41 pushed в отдельную ветку AMN2.
[Bot source review](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-sqlite-и-границы-переноса--2026-09-20)
завершён на source 2069e41: общий SQLite, partial failure, delivery record и
shutdown требуют отдельного design. Подготовлен [письменный проект последовательного исполнителя](../specs/2026-09-20-amn2-bot-workflow-worker-design.ru.md):
Design согласован оператором после commit b277154. Подготовлен [технический план реализации](2026-09-20-amn2-bot-workflow-worker-plan.ru.md):
План и inline execution утверждены; четыре части реализованы и pushed в AMN2
до 1bd7f62. Итоговые 312 локальных PASS; два findings независимого review
исправлены через RED/GREEN; [результаты](../../../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-worker-реализация-и-проверки--2026-09-20).
Повторные SSH попытки/circuit breaker не входят в fix; не развёрнуто.

### Текущий вертикальный статус

- ✅ Task 0 — baseline.
- ✅ Task 1 — package016/local tooling; stage-защиты и recovery observations только локально; DNS bridge STOP.
- ✅ Task 2 — исторические Spain gates/diagnostics, не свежий preflight.
- ✅ Task 3A — minimal runtime по историческим evidence.
- ⏳ Task 3B — integration/recovery не завершены; recovery-контракт v1 согласован.
- ❌ Task 4A — Windows traffic FAIL; root cause не доказана.
- ✅ Task 4B — Android connectivity, не performance acceptance.
- ✅ Task 4C — iPhone connectivity/reconnect, не performance acceptance.
- ❌ Task 4.5 — quality FAIL; strict A/B неполон и отложен.
- ⏳ Task 5 — acceptance заблокирован.
- ⏳ Task 6 — closeout заблокирован.

AWG2_UNTOUCHED; package016 immutable; general issuance disabled.
Историческая синхронизация 08.09 зафиксировала публикацию #3043 и R1 review.
20.09 локальный scope расширен по отдельному подтверждению оператора: parser и
сравнение observations, 164 synthetic PASS. Это не live inventory/recovery;
package/live/stage/install не выполнялись, recovery-контракт не пересогласовывался.
Проверки и Git — по [AGENTS.md](../../../AGENTS.md): docs-only без runtime-тестов;
для code fix — targeted RED/GREEN; ошибка инструмента = UNKNOWN.
Детали выполненного читать адресно в [историческом приложении](2026-09-08-phase16-execution-history.md) и в
[receipts методики](../../PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md#история-реализации-методики--не-текущая-очередь).

## Переходы по прежним ссылкам

Исторические разделы перенесены; читать приложение только по конкретному вопросу.

<a id="актуальный-порядок-и-gates--2026-09-05-дополнение-2026-09-08"></a>

[Актуальный порядок и gates — 2026-09-05, дополнение 2026-09-08](2026-09-08-phase16-execution-history.md#актуальный-порядок-и-gates--2026-09-05-дополнение-2026-09-08)

<a id="доказательства-и-границы"></a>

[Доказательства и границы](2026-09-08-phase16-execution-history.md#доказательства-и-границы)

<a id="task_plan_by_criticality-1"></a>

[TASK_PLAN_BY_CRITICALITY](2026-09-08-phase16-execution-history.md#task_plan_by_criticality-1)

<a id="политика-проверок"></a>

[Политика проверок](2026-09-08-phase16-execution-history.md#политика-проверок)

<a id="текущий-вертикальный-статус-1"></a>

[Текущий вертикальный статус](2026-09-08-phase16-execution-history.md#текущий-вертикальный-статус-1)

<a id="исторический-bounded-local-go--package-016-2026-08-27-завершён"></a>

[Исторический BOUNDED LOCAL GO — PACKAGE 016, 2026-08-27 (завершён)](2026-09-08-phase16-execution-history.md#исторический-bounded-local-go--package-016-2026-08-27-завершён)
