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
- Статус 2026-05-31: первый implementation slice выполнен в `amn2` branch `codex/remote-operation-contract-metadata`, commit `57d484d`.
- Что должно появиться: `operation_id`, `risk_class`, `consistency_status`, `rollback_note`, `local_side_effects`, `remote_side_effects`, `idempotency_key`.
- Почему P0: без этого нельзя безопасно отличать read-only диагностику от операций, которые меняют VPS или локальную БД.
- Локальная проверка: contract tests для state-changing operations и совместимость с уже существующим read-only `RemoteOperationRunner`.
- Проверено 2026-05-31: `23 passed` для `tests/server/test_operation_runner.py tests/server/test_checks.py`.
- Full suite 2026-05-31: `517 passed, 1 warning`.
- Готово, когда: старые read-only tests проходят, а новые state-changing tests требуют явной metadata. Первый срез готов; следующий слой должен подключить fake runner/partial-failure сценарии.

### Partial-failure model

- Цель: описать состояние, когда remote операция уже сработала, а локальная часть, audit или DB transaction не завершились.
- Статус 2026-05-31: implementation slice выполнен в `amn2` branch `codex/remote-operation-partial-failure`, commit `0afb22a`.
- Что должно появиться: минимальный result/status contract для `remote-applied`, `local-applied`, `partial-failure`, `manual-review-required`.
- Почему P0: approve/revoke/reset устройства могут оставить VPS и локальную БД в разных состояниях.
- Локальная проверка: fake applier успешно применяет remote change, затем искусственно ломается local audit/DB step.
- Проверено 2026-05-31: `38 passed` для `tests/services/test_access_service.py tests/bot/test_bot_workflows.py`.
- Full suite 2026-05-31: `519 passed, 1 warning`.
- Готово, когда: тесты фиксируют recovery note и состояние для ручной проверки, а не теряют факт частичного применения. Первый срез готов для approve/reset; следующие surfaces должны использовать тот же result/exception contract.

### Fake runner and fake peer applier harness

- Цель: проверить опасные сценарии без VPS.
- Статус 2026-05-31: fake peer applier/remover сценарии для approve/reset выполнены в `codex/remote-operation-partial-failure`.
- Что должно появиться: тестовые double-объекты для успешного apply, failed apply, failed revoke, timeout и mixed multi-device reset.
- Почему P0: real VPS gate нельзя начинать, пока поведение не воспроизводится локально.
- Локальная проверка: pytest-сценарии для approve, revoke, reset и command output.
- Готово, когда: state-changing flows покрыты fake success/failure сценариями без network access. Первый approve/reset partial-failure слой закрыт; command timeout/dry-run metadata идут следующим срезом.

### Secret-safe audit/redaction gate

- Цель: не допустить утечек `.conf`, QR payload, `vpn://`, private key, PSK, tokens и command output в metadata, logs, audit и diagnostics.
- Статус 2026-06-01: dry-run/audit metadata slice перенесен на fresh VPS-gate candidate `codex/remote-operation-vps-gate-prep`, head `aca6663`.
- Что должно появиться: tests, которые проверяют redacted output для новых remote mutation metadata.
- Почему P0: remote operations почти всегда рядом с секретами и конфигами.
- Локальная проверка: focused redaction/security tests плюс audit serialization tests.
- Проверено 2026-06-01: `79 passed, 1 warning` для focused server/security/web набора.
- Full suite 2026-06-01 на fresh candidate: `551 passed, 1 warning`.
- Готово, когда: ни один новый dry-run/audit/report path не содержит raw secrets. Первый dry-run/audit срез готов; live VPS не трогался.

### SSH host key verification policy

- Цель: не начинать live SSH/VPS gate с молчаливого доверия неизвестному host key.
- Статус 2026-06-01: design подготовлен в `research/amn2/ssh-host-key-enrollment-design.md`; VPS gate checklist получил Phase 0 host key verification.
- Что должно появиться: operator-side verification для ближайшего gate и будущий app-managed pinning перед web/API remote-operation expansion.
- Почему P0: host key trust решается до первого SSH command, иначе read-only/live remote operations могут стартовать через непроверенный endpoint.
- Локальная проверка: docs review и future fake tests для missing/mismatch/matching pin без реального VPS.
- Готово, когда: Phase 0 evidence присутствует в runbook/checklist, а будущий implementation boundary не использует `accept-new` как production trust model.

## P1. Важные локальные задачи

### Dry-run preview for mutations

- Цель: до выполнения показать оператору, что будет изменено.
- Статус 2026-06-01: implementation slice включен в `amn2` branch `codex/remote-operation-vps-gate-prep`, commit `b7a12ca`.
- Что должно появиться: preview с `operation_id`, `risk_class`, side effects, rollback/recovery note и `consistency_status=dry-run`.
- Почему P1: dry-run нужен до live VPS apply/revoke, но опирается на P0 contract.
- Локальная проверка: tests для apply-peer/revoke-peer dry-run без live execution.
- Проверено 2026-06-01: `tests/server/test_operation_runner.py tests/server/test_peer_apply.py tests/security/test_redaction.py tests/web/test_servers.py tests/web/test_users.py -v` -> `79 passed, 1 warning`.
- Готово, когда: preview понятен оператору и не содержит секретов. Первый срез готов: `RemoteOperationRunner.plan()` отдает `dry-run` для state-changing операций, `OperationPlan.to_safe_metadata()` не публикует command strings, `apply-peer`/`revoke-peer` dry-run выводит operation metadata без PSK.

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
- Статус 2026-06-01: выполнено в `amn2` branch `codex/remote-operation-vps-gate-prep`, commit `50be810`.
- Что должно появиться: короткая запись в `docs/RUNTIME_REGISTRY.ru.md` и, при наличии английского слоя, в `docs/RUNTIME_REGISTRY.en.md`.
- Почему P1: это превращает договоренность в повторяемое правило для следующих чатов и веток.
- Локальная проверка: docs review, `git diff --check`.
- Проверено 2026-06-01: `tests/deploy/test_runtime_registry.py -v` -> `7 passed`.
- Готово, когда: по docs понятно, что real VPS gate начинается только после локального green suite. Первый registry update готов.

### Backup/import policy registry and restore-preview contract

- Цель: не дать future backup/import API стать обычным download/upload endpoint для secret-bearing state.
- Статус 2026-06-01: design подготовлен в `research/amn2/backup-import-dangerous-api-design.md`.
- Что должно появиться: локальный policy registry для backup/import lanes, redacted field policy и `restore-preview` contract без записи в target state.
- Почему P1: backup/import касается peer private keys, PSK, token hashes, users/devices/servers, audit и future Local Agent metadata.
- Локальная проверка: no-side-effect tests для preview/validation/redaction; никаких web/API full backup, restore apply или import apply в первом срезе.
- Готово, когда: metadata export, redacted backup и encrypted full backup имеют разные policy gates, а destructive apply/import остаются заблокированы до отдельного решения.

### Manager config export contract

- Цель: дать UI/API/bot/self-service единый typed contract для `.conf`, QR, `vpn://` и future protocol-specific artifacts.
- Статус 2026-06-01: design подготовлен в `research/amn2/manager-config-export-contract.md`.
- Что должно появиться: `ConfigExportResult`/artifact boundary, capability model, safe metadata и safe error categories поверх текущего `DeviceConfigDelivery`/`ConfigDeliveryPackage`.
- Почему P1: config export является `secret-read`, а несовместимые manager signatures могут ломать config delivery прямо в UI/API.
- Локальная проверка: no-route contract tests, adapter tests, unsupported artifact/target tests, redaction/audit metadata tests; без public/self-service endpoint и без API `config:read`.
- Готово, когда: каждый будущий protocol manager возвращает typed artifacts или safe unsupported category, а caller не зависит от manager-specific function signature.

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

1. Сделать `State-changing operation contract` и сохранить совместимость read-only runner - выполнено в `codex/remote-operation-contract-metadata`.
2. Добавить fake runner/fake peer applier harness - первый approve/reset слой выполнен в `codex/remote-operation-partial-failure`.
3. Покрыть partial-failure model для approve/revoke/reset - первый approve/reset слой выполнен в `codex/remote-operation-partial-failure`.
4. Добавить dry-run preview и safe audit/redaction metadata - выполнено и перенесено на fresh candidate `codex/remote-operation-vps-gate-prep`.
5. Прогнать focused tests - выполнено: `79 passed, 1 warning`.
6. Прогнать full local suite на fresh candidate - выполнено: `551 passed, 1 warning`.
7. Обновить Runtime Registry и lab notes - Runtime Registry включен в commit `50be810`, lab notes обновлены этим срезом.
8. Перед controlled real VPS verification gate зафиксировать Phase 0 SSH host key verification по `research/amn2/ssh-host-key-enrollment-design.md`.
9. Зафиксировать backup/import dangerous API boundary по `research/amn2/backup-import-dangerous-api-design.md` - выполнено локально, без web/API routes и без VPS.
10. Зафиксировать manager config export contract по `research/amn2/manager-config-export-contract.md` - выполнено локально, без новых config routes и без VPS.
11. Только после этого перейти к controlled real VPS verification gate по `research/amn2/vps-gate-remote-operation-dry-run-audit.md` - следующий шаг, отдельно подтверждаемый оператором.

## Не переносим в локальную фазу

- Реальные SSH-подключения.
- Реальный Docker reload/apply.
- Реальное добавление или удаление peer на VPS.
- Проверку firewall на живом сервере.
- Диагностический snapshot с реального VPS.
- Backup/restore rehearsal на настоящем runtime.

Эти пункты остаются во второй фазе и требуют отдельного подтверждения оператора, тестового peer/device, backup/recovery window и записи результата в lab.
