# `amn2` VPS Gate Evidence Checklist

Дата: 2026-06-01.

Назначение: короткий чеклист для фиксации результата реального VPS gate по ветке `codex/remote-operation-vps-gate-prep`.

Базовый runbook: `research/amn2/vps-gate-remote-operation-dry-run-audit.md`.

## Candidate

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex/remote-operation-vps-gate-prep
head: aca6663 Add VPS gate handoff for remote ops
base: 1fdcde5 Add scoped API token storage contract
```

## Phase 0: вход в gate

- [ ] Подтверждено, что оператор намеренно входит в real VPS gate.
- [ ] Проверен maintenance window и доступ восстановления.
- [ ] Выбран server alias из `servers.yml`.
- [ ] Выбран dedicated test peer, не production user/device.
- [ ] PSK/private key/full config не заносятся в AMN3/GitHub/chat.
- [ ] Перед live mutation остается стоп-точка для отдельного подтверждения.

## Phase 1: read-only/dry-run evidence

- [ ] `bot check-network` выполнен.
- [ ] `server preflight` выполнен.
- [ ] `server check --dry-run` выполнен.
- [ ] `server check` выполнен как read-only check.
- [ ] `collect-traffic --dry-run` выполнен.
- [ ] `apply-peer --dry-run` выполнен для test peer.
- [ ] `revoke-peer --dry-run` выполнен для test peer.

Обязательная проверка вывода:

- [ ] Есть `operation_id`.
- [ ] Есть `risk_class`.
- [ ] Есть `consistency_status=dry-run`.
- [ ] Есть side effects summary.
- [ ] Есть rollback/recovery note.
- [ ] Нет raw PSK.
- [ ] Нет private key.
- [ ] Нет full client/server config.
- [ ] Нет raw command string.
- [ ] VPS state не изменился.

Phase 1 decision:

```text
dry-run-only-pass / needs-fix
```

## Phase 2: optional live single peer

Phase 2 разрешена только после отдельного подтверждения оператора.

- [ ] Отдельное подтверждение получено.
- [ ] `apply-peer --apply` выполнен только для dedicated test peer.
- [ ] `sync-peers` после apply выполнен.
- [ ] Добавлен ровно один test peer.
- [ ] Existing peers не изменились.
- [ ] `revoke-peer --apply` выполнен для того же test peer.
- [ ] `sync-peers` после revoke выполнен.
- [ ] Test peer больше не активен.
- [ ] Ошибки, если были, redacted и содержат recovery note.

Phase 2 decision:

```text
verified-live / needs-fix / skipped-after-dry-run
```

## Evidence record

Заполнять после теста, без секретов:

```text
date/time:
operator:
candidate branch:
candidate head:
server alias:
phase 1 result:
phase 2 result:
redaction result:
final peer state:
rollback/recovery used:
decision:
next action:
```

## Gate result rules

`verified-live` можно ставить только если:

- Phase 1 прошла без state changes и без secret leaks;
- Phase 2, если запускалась, добавила и удалила ровно один test peer;
- final sync подтверждает ожидаемое состояние;
- recovery не потребовал manual cleanup за пределами test peer.

`needs-fix` ставится, если:

- dry-run выводит секреты или raw command strings;
- apply/revoke затронул не test peer;
- состояние после revoke не подтверждено;
- recovery note отсутствует или не помогает оператору.

`dry-run-only-pass` допустим как промежуточный результат:

- read-only/dry-run успешно прошли;
- live `--apply` осознанно не запускался;
- интеграционные write/API решения остаются заблокированными до live evidence.
