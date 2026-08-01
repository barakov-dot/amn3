# AMN2 Phase 13 — квитанция проекта пакета и предварительной проверки AWG3

Дата: 2026-08-01

Статус: `design_written_pending_operator_review`

## Полученный результат

Записана русскоязычная проектная спецификация:

`docs/superpowers/specs/2026-08-01-amn2-phase13-awg3-isolated-runtime-package-readonly-spain-preflight-design.ru.md`

Принята архитектура: неизменяемая основа проверки равенства Phase 12 плюс
новые управляющий сценарий и схема Phase 13 с контрольными суммами.
Спецификация
определяет ресурсы-кандидаты, контракты манифеста и доказательств,
классификацию конфликтов, условия равенства, разрешённый список команд только
для чтения, защиту от повторного использования результата, коды завершения и
критерии готовности.

## Соблюдённые границы

- implementation: `not_performed`;
- package build: `not_performed`;
- SSH/preflight run: `not_performed`;
- Spain/USA/AWG mutation: `not_performed`;
- config/peer/key issuance: `not_performed`;
- reboot/rollback rehearsal: `not_performed`;
- foreign Spain service change: `not_performed`;
- USA retirement/reuse authorization: `false`.

Следующий шаг — проверка записанной спецификации оператором. Только после её утверждения
можно написать отдельный локальный план TDD реализации. Готовых управляющего
сценария, сборщика, манифеста и SHA-256 результата ещё нет, поэтому точное
разрешение на SSH пока не формируется.
