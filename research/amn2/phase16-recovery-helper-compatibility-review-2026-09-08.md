# Phase 16 — R1: совместимость старого recovery-helper

Дата записи: 2026-09-08. Статус: `READ_ONLY_REVIEW_COMPLETE_NOT_IMPLEMENTED`.
Фиксация уже завершённого в текущей задаче локального чтения; новый диагностический
прогон, тесты, SSH и исполнение collector/driver при записи не выполнялись.
Baseline документации: `d2383a9fcdff0942aa426790afc31d330f52ca95`.
Это не deployed revision и не свидетельство текущего состояния VPS.

## Вопрос и источники

Можно ли повторно использовать старый helper для
[согласованного recovery-контракта v1](../../docs/superpowers/specs/2026-09-08-phase16-controlled-stage-recovery-contract.ru.md)?
Ответ: без изменений и новых точных bindings — нет.

Оба исходника найдены и полностью прочитаны в другом worktree того же репозитория:
`C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-004/tmp/`.
Это локальные исторические файлы, не переносимые зависимости текущей ветки.

| Файл | SHA256 | Bytes |
| --- | --- | --- |
| `phase16-transaction007-recovery-state-v1.py` | `6d5b81d1221e7171fa0b17cbc9cbefc24b0ea518ca8b06a11577f56af62cc592` | 22235 |
| `phase16-transaction007-recovery-runner-v1.ps1` | `074c789efd85f6e8fe72c9693a6e134b39e079cfe124e46cebf35cdb398bfb76` | 16099 |

Хеши совпали с [историческим receipt transaction-007](phase16-spain-controlled-stage-recovery-state-diagnostic-receipt-016-transaction-007-v1.md).
Файлы не исполнялись, не импортировались, не копировались и не изменялись в R1.
Receipt и consumed approvals не разрешают повтор того запуска.

## Результат завершённого чтения

- Collector: `milestone_shape` (строки 139–143) допускает старые rollback milestones,
  но не `recovery_required` с пустым списком. `outcome_shape` (около строки 196)
  принимает только `application_and_awg31_staged`/`rolled_back`, а не новые
  `rollback_failed`/`recovery_required` текущего coordinator.
- Driver: `$recAllowedStrings` (строки 16–27) также не принимает новые классы.
  Bindings относятся к package016/transaction007 и прежним state/approval;
  есть абсолютные пути старого worktree и guard существующего receipt.
  Переписывать старый receipt или снимать guard ради повтора нельзя.
- Проверка процесса через `pgrep -f` даёт presence/absence, не удостоверяет
  ownership, полный набор дочерних процессов или прекращение операций (quiescence).
- Inventory старых controlled-stage имён не доказывает сохранность minimal pilot.
  Pilot и coordinator используют общий image digest; удаление по одному имени
  image недопустимо. Границы исключений задаёт контракт v1.
- Collector ограничивает сбор примерно 19 секундами, отдельные probes — 3 секундами;
  timeout закрывает handles без сигналов. Это не доказательство остановки probes.
  Driver ограничивает local SSH ожидание 30 секундами; остановка локального SSH
  не доказывает остановку удалённых процессов.
- Ограничения размера metadata, symlink checks, нормализованный вывод и
  `query_failed` при ошибках полезны, но не закрывают перечисленные пробелы.

Текущий coordinator уже содержит три локальные защиты. Обнаруженная несовместимость
относится к старому diagnostic helper, не означает откат этих исправлений.
`phase16_awg31_client_recovery.py` решает иную задачу клиентского профиля Jc/I1;
это не замена server recovery inventory.

## Следующая граница

Не повторять R1 на неизменных исходниках. Возможный отдельный ограниченный code scope:
новая локальная версия parser/validator с поддержкой текущих outcome/milestone
классов и одним offline TDD-набором; старые helper, receipts и package016 сохранить.
Реализация ещё не выполнена. Даже её PASS не докажет ownership/quiescence,
сохранность pilot или готовность runner к live inventory/recovery.

Любой live inventory, signal, cleanup и новый stage имеют отдельные gates
контракта. Эта запись их не разрешает. Очередь задач — только в
[актуальном плане](../../docs/superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
