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

### TASK_PLAN_BY_CRITICALITY

1. **P0 — quality/A/B, ОТЛОЖЕНО.** После возврата оператора: подтвердить импорт
   существующего d7 и физическую сеть, метод/лимиты/outcomes; затем exact approval
   на последовательный same-device/same-app/same-access-network Spain A/B.
   Новая выдача и автоматический повтор не разрешены.
2. **P1 — Windows, BLOCKED.** Следующий bounded test только при значимом изменении
   официального клиента/engine ИЛИ новой проверяемой гипотезе: записать отличие
   от закрытых диагностик и исходы, получить live approval. Повтор kill-switch A/B,
   поиска отсутствующего адаптера или общего IPv4 HTTPS без новой гипотезы не нужен.
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
   транзакции и не доказывает quiescence/сохранность pilot. Возможный следующий
   code scope — новая локальная версия parser с одним offline TDD-набором;
   пока не реализована и не разрешена этим планом. Это не готовность live recovery.
5. **P2 — integration, BLOCKED предыдущими gates.** После клиентских и quality
   доказательств: checksum/state/rollback-bound approval, проверка persistence,
   restart policy, leaks и границ отката. Затем Task 5 и Task 6.

### Текущий вертикальный статус

- ✅ Task 0 — baseline.
- ✅ Task 1 — package016/local tooling; три stage-защиты завершены только локально; DNS bridge STOP.
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
Последняя docs-only синхронизация фиксирует публикацию #3043 и завершённый R1
review; recovery-контракт не пересогласовывается. Без кода, новых тестов,
package/live/stage/install/push.
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
