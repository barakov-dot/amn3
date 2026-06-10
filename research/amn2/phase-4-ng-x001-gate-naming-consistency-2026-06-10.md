# Phase 4 NG-X001: gate naming consistency

Дата: 2026-06-10.

Назначение: закрыть косметическую docs-only задачу `NG-X001` и выровнять stage-level gate labels вокруг префикса `P4-NG-*` в P4-NG docs/evidence, чтобы будущие live/write/config/public decisions не выглядели как отдельная параллельная naming-система.

## Решение

```text
slice_id: NG-X001
slice_name: gate naming consistency
mode: AMN3 docs-only
live_write_authorized: no
AMN2_code_changed: no
runtime_routes_changed: no
live_vps_commands: no
ssh_commands: no
public_exposure: no
config_delivery: no
write_api_implementation: no
production_peer_or_user_mutation: no
closed_follow_up_slice: NG-X002 Russian-first operator wording polish
closed_follow_up_slice_status: completed in research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md
current_next_slice: none
```

## Naming Contract

Stage-level P4-NG gate labels now use `P4-NG-*`:

```text
P4-NG-VPS-READONLY-BASELINE-2026-06-10
P4-NG-WRITE-API-LIVE-GATE
P4-NG-CONFIG-DELIVERY-GATE
P4-NG-PUBLIC-EXPOSURE-GATE
P4-NG-WAPI-CLIENTS-LOCAL-IMPLEMENTATION-GATE
P4-NG-WAPI-OPERATION-QUEUE-LOCAL-IMPLEMENTATION-GATE
P4-NG-WAPI-PANEL-LABELS-LOCAL-IMPLEMENTATION-GATE
P4-NG-HEALTH-POLLING-LOCAL-IMPLEMENTATION-GATE
P4-NG-ATTACH-EXISTING-SERVER-RECONCILIATION-LOCAL-IMPLEMENTATION-GATE
P4-NG-ATTACH-EXISTING-SERVER-WRITE-BACKFILL-GATE
```

`NG-*`, `WAPI-*`, `P4-*` task ids, route names, branch names, file paths and historical candidate ids were not renamed.

## Что обновлено

- P4-NG plan, charter, next-chat handoff, project context import, project status, transfer backlog and unified-product handoff now refer to `P4-NG-WRITE-API-LIVE-GATE`.
- WAPI/NG evidence files now use `P4-NG-*` for local implementation, config delivery, public exposure, write live, attach/backfill and polling gate labels.
- `NG-X002` was selected next and later closed in `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`.
- Очередь default docs-only cosmetic теперь закрыта.

## Негативные проверки

`NG-X001` не разрешает:

- запуск `NG-V001`;
- live VPS command или SSH command;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- `/api/clients` write CRUD;
- config delivery, `.conf`, QR, `vpn://`, archive, share/download link;
- Local Agent mutation;
- token issue/revoke route;
- backup/import/reboot;
- production peer/user mutation;
- копирование GPL/upstream code.

## Оставшийся активный план

Критичные: нет активных задач.

Очень важные:

- `NG-V001` read-only VPS baseline gate, только после отдельного явного named approval.

Важные: нет активных задач.

Нормальные: нет активных задач.

Простые: нет активных задач.

Косметические: нет активных задач.

## Handoff

`NG-X001` is closed. `NG-X002` was selected next and later closed in `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`. Очередь default docs-only cosmetic теперь закрыта.

Do not run `NG-V001` until the operator explicitly approves the gate and provides the target SSH alias/host outside repository secrets.
