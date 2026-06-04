# `amn2` VPS Gate Evidence Checklist

Дата: 2026-06-01.

Назначение: короткий чеклист для фиксации результата реального VPS gate по ветке `codex/remote-operation-vps-gate-prep`.

Базовый runbook: `research/amn2/vps-gate-remote-operation-dry-run-audit.md`.

Актуализация 2026-06-04: Phase 1 read-only/dry-run gate пройден на VPS как `dry-run-only-pass`; evidence записана в `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`. Phase 2 live single peer apply/revoke не запускалась.

## Candidate

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex/remote-operation-vps-gate-prep
head: 7281254 Merge stable API web panel baseline into remote operation gate
base: 294803e Add API readiness and token web pages
```

## Phase 0: вход в gate

- [x] Подтверждено, что оператор намеренно входит в real VPS gate.
- [x] Проверен maintenance window и доступ восстановления.
- [x] Выбран server alias из `servers.yml`.
- [ ] SSH host key verified/pinned outside AMN3 notes.
- [ ] Если SSH client показывает unknown host key prompt, gate остановлен до out-of-band verification.
- [x] Выбран synthetic/dedicated test peer, не production user/device.
- [x] PSK/private key/full config не заносятся в AMN3/GitHub/chat.
- [x] Перед live mutation остается стоп-точка для отдельного подтверждения.

## Phase 1: read-only/dry-run evidence

- [x] `bot check-network` выполнен.
- [x] `server preflight` выполнен.
- [x] `server check --dry-run` выполнен.
- [x] `server check` выполнен как read-only check.
- [x] `collect-traffic --dry-run` выполнен.
- [x] `apply-peer --dry-run` выполнен для test peer.
- [x] `revoke-peer --dry-run` выполнен для test peer.

Обязательная проверка вывода:

- [x] Есть `operation_id`.
- [x] Есть `risk_class`.
- [x] Есть `consistency_status=dry-run`.
- [x] Есть side effects summary.
- [x] Есть rollback/recovery note.
- [x] Нет raw PSK.
- [x] Нет private key.
- [x] Нет full client/server config.
- [x] Нет secret-bearing raw command output; planned command preview redacted and contains no PSK/private key/full config.
- [x] Live apply/revoke не запускались.

Phase 1 decision:

```text
dry-run-only-pass
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
skipped-after-dry-run
```

## Evidence record

Заполнять после теста, без секретов:

```text
date/time:
operator:
candidate branch:
candidate head:
server alias:
host key verification:
phase 1 result:
phase 2 result:
redaction result:
final peer state:
rollback/recovery used:
decision:
next action:
```

Recorded 2026-06-04:

```text
date/time: 2026-06-04
operator: VPS operator
candidate branch: codex/remote-operation-vps-gate-prep
candidate head: 7281254
server alias: local
host key verification: not recorded in AMN3; no unknown-host prompt evidence published
phase 1 result: dry-run-only-pass
phase 2 result: skipped-after-dry-run
redaction result: passed for published evidence
final peer state: no live test peer apply/revoke executed
rollback/recovery used: not needed
decision: dry-run-only-pass
next action: either request separate Phase 2 single test peer apply/revoke approval, or continue read-only integration design only
```

## Gate result rules

`verified-live` можно ставить только если:

- Phase 1 прошла без state changes и без secret leaks;
- Phase 2, если запускалась, добавила и удалила ровно один test peer;
- final sync подтверждает ожидаемое состояние;
- recovery не потребовал manual cleanup за пределами test peer.

`needs-fix` ставится, если:

- dry-run выводит секреты, full config или secret-bearing raw command output;
- apply/revoke затронул не test peer;
- состояние после revoke не подтверждено;
- recovery note отсутствует или не помогает оператору.

`dry-run-only-pass` допустим как промежуточный результат:

- read-only/dry-run успешно прошли;
- live `--apply` осознанно не запускался;
- интеграционные write/API решения остаются заблокированными до live evidence.
