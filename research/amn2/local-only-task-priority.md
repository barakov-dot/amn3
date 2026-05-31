# `amn2`: локальный приоритетный список перед VPS gate

Дата: 2026-05-31.

Этот список отделяет задачи, которые можно безопасно выполнить локально, от задач, которые требуют реального VPS. Основа: [AMN2 Remote Operations Local/VPS Split Implementation Plan](../../docs/superpowers/plans/2026-05-31-amn2-remote-ops-local-vps-split.md).

## Граница локальной фазы

Локально выполняем только то, что можно проверить через код, тесты, fake runner, fake peer applier, SQLite test DB и документацию.

Локальная фаза не должна:

- читать `.env`;
- подключаться к реальному VPS;
- выполнять live SSH/sudo/Docker/firewall команды;
- менять реальные peers, контейнеры, firewall или runtime-конфиги;
- использовать production user/device как тестовый объект.

Выход из локальной фазы возможен только после зеленых focused tests и full local suite. После этого начинается отдельный controlled real VPS verification gate.

## P0. Критически важные локальные задачи

### State-changing operation contract

- Цель: явно описать любые операции, которые меняют remote/local state.
- Что должно появиться: `operation_id`, `risk_class`, `consistency_status`, `rollback_note`, `local_side_effects`, `remote_side_effects`, `idempotency_key`.
- Почему P0: без этого нельзя безопасно отличать read-only диагностику от операций, которые меняют VPS или локальную БД.
- Локальная проверка: contract tests для state-changing operations и совместимость с уже существующим read-only `RemoteOperationRunner`.
- Готово, когда: старые read-only tests проходят, а новые state-changing tests требуют явной metadata.

### Partial-failure model

- Цель: описать состояние, когда remote операция уже сработала, а локальная часть, audit или DB transaction не завершились.
- Что должно появиться: минимальный result/status contract для `remote-applied`, `local-applied`, `partial-failure`, `manual-review-required`.
- Почему P0: approve/revoke/reset устройства могут оставить VPS и локальную БД в разных состояниях.
- Локальная проверка: fake applier успешно применяет remote change, затем искусственно ломается local audit/DB step.
- Готово, когда: тесты фиксируют recovery note и состояние для ручной проверки, а не теряют факт частичного применения.

### Fake runner and fake peer applier harness

- Цель: проверить опасные сценарии без VPS.
- Что должно появиться: тестовые double-объекты для успешного apply, failed apply, failed revoke, timeout и mixed multi-device reset.
- Почему P0: real VPS gate нельзя начинать, пока поведение не воспроизводится локально.
- Локальная проверка: pytest-сценарии для approve, revoke, reset и command output.
- Готово, когда: state-changing flows покрыты fake success/failure сценариями без network access.

### Secret-safe audit/redaction gate

- Цель: не допустить утечек `.conf`, QR payload, `vpn://`, private key, PSK, tokens и command output в metadata, logs, audit и diagnostics.
- Что должно появиться: tests, которые проверяют redacted output для новых remote mutation metadata.
- Почему P0: remote operations почти всегда рядом с секретами и конфигами.
- Локальная проверка: focused redaction/security tests плюс audit serialization tests.
- Готово, когда: ни один новый dry-run/audit/report path не содержит raw secrets.

## P1. Важные локальные задачи

### Dry-run preview for mutations

- Цель: до выполнения показать оператору, что будет изменено.
- Что должно появиться: preview с `operation_id`, `risk_class`, side effects, rollback/recovery note и `consistency_status=dry-run`.
- Почему P1: dry-run нужен до live VPS apply/revoke, но опирается на P0 contract.
- Локальная проверка: tests для apply-peer/revoke-peer dry-run без live execution.
- Готово, когда: preview понятен оператору и не содержит секретов.

### Bot/service partial-failure сценарии

- Цель: проверить не только runner, но и user-facing flows.
- Что должно появиться: тесты для approve order, revoke device, reset devices, где remote/local части расходятся.
- Почему P1: именно bot/service workflows чаще всего будут запускать операции с пользователями.
- Локальная проверка: `tests/services/*` и `tests/bot/*` на fake applier.
- Готово, когда: пользовательский workflow возвращает безопасный статус и audit/recovery note.

### Web/admin audit metadata

- Цель: если web-admin запускает remote operation, audit должен видеть безопасную metadata.
- Что должно появиться: route/action tests для metadata без raw secrets.
- Почему P1: admin UI должен объяснять риск действия и оставлять trace для оператора.
- Локальная проверка: web tests только если web surface реально меняется в этом срезе.
- Готово, когда: web/admin audit не раскрывает секреты и фиксирует consistency status.

### Runtime Registry update

- Цель: зафиксировать локальный gate как обязательное условие перед VPS.
- Что должно появиться: короткая запись в `docs/RUNTIME_REGISTRY.ru.md` и, при наличии английского слоя, в `docs/RUNTIME_REGISTRY.en.md`.
- Почему P1: это превращает договоренность в повторяемое правило для следующих чатов и веток.
- Локальная проверка: docs review, `git diff --check`.
- Готово, когда: по docs понятно, что real VPS gate начинается только после локального green suite.

## P2. Малая важность или после P0/P1

### Real VPS checklist refinement

- Цель: уточнить команды controlled VPS verification gate.
- Почему P2: сама проверка будет не локальной, поэтому сейчас достаточно подготовить checklist, без выполнения.
- Не делать локально: live apply/revoke, SSH health check, Docker reload, firewall changes.

### Docker manager design

- Цель: описать persistent config path, backup, reload/apply semantics и rollback note до live Docker apply/revoke.
- Почему P2: это важно, но должно идти после общего remote operation contract.
- Локальная проверка: design note и test plan, без live Docker mutations.

### Route/Auth machine-checkable tests

- Цель: превратить Route/Auth Policy Matrix в тесты.
- Почему P2: полезно для общего hardening, но текущий блок сфокусирован на remote operation safety.
- Локальная проверка: endpoint tests, auth/role tests, audit expectations.

### Background jobs and cancellation

- Цель: длинные remote operations оформить как jobs с progress, timeout, cancellation и final audit summary.
- Почему P2: сначала нужен единый operation contract, потом job abstraction.
- Локальная проверка: fake long-running operation tests.

## P3. Косметика, UX и документация

### Naming cleanup

- Цель: снизить путаницу между `amn2`, `amn3`, `vpn-ops-lab`, Amneziya и future hybrid.
- Почему P3: полезно для ясности, но не блокирует безопасность remote operations.

### README and handoff polish

- Цель: обновлять входные README и handoff-файлы после каждого закрытого среза.
- Почему P3: помогает не терять контекст, но не должно задерживать P0/P1.

### Operator wording consistency

- Цель: одинаково называть risk class, dry-run, rollback, recovery note и manual review во всех docs/UI surfaces.
- Почему P3: улучшает UX, но зависит от финального contract wording.

### OpenAPI grouping

- Цель: сгруппировать API docs по auth, users, servers, devices, config delivery, admin, metrics.
- Почему P3: полезно после стабилизации route policy и remote operation surfaces.

## Первая партия исполнения

1. Сделать `State-changing operation contract` и сохранить совместимость read-only runner.
2. Добавить fake runner/fake peer applier harness.
3. Покрыть partial-failure model для approve/revoke/reset.
4. Добавить dry-run preview и safe audit metadata.
5. Прогнать focused tests.
6. Прогнать full local suite.
7. Обновить Runtime Registry и lab notes.
8. Только после этого перейти к controlled real VPS verification gate.

## Не переносим в локальную фазу

- Реальные SSH-подключения.
- Реальный Docker reload/apply.
- Реальное добавление или удаление peer на VPS.
- Проверку firewall на живом сервере.
- Диагностический snapshot с реального VPS.
- Backup/restore rehearsal на настоящем runtime.

Эти пункты остаются во второй фазе и требуют отдельного подтверждения оператора, тестового peer/device, backup/recovery window и записи результата в lab.
