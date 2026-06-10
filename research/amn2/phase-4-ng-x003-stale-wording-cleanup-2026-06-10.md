# Phase 4 NG-X003: stale wording cleanup

Дата: 2026-06-10.

Назначение: закрыть косметическую docs-only задачу `NG-X003` и убрать устаревшие active-next формулировки, которые после закрытия `NG-S002`/`NG-S004` могли оставлять `NG-X003` как текущую рекомендацию или звучать как неявное разрешение live/write/public/config работ.

## Решение

```text
slice_id: NG-X003
slice_name: stale wording cleanup
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
selected_next_slice: NG-X001 gate naming consistency
```

## Что обновлено

- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md` переносит `NG-X003` в закрытые задачи и удаляет его из активного косметического списка.
- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, `docs/PROJECT_CONTEXT_IMPORT.ru.md`, `research/amn2/transfer-backlog.md`, `research/amn2/phase-4-candidate-registry-2026-06-09.md`, `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md` и `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md` теперь указывают `NG-X003` как закрытую docs-only cleanup-задачу.
- Исторические WAPI/NG evidence-файлы больше не оставляют `NG-X003` как активный next-step; они описывают его как последующий закрытый cleanup.
- Следующая безопасная рекомендация стала `NG-X001` gate naming consistency.

## Негативные проверки

`NG-X003` не разрешает:

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

Косметические:

- `NG-X001` gate naming consistency.
- `NG-X002` Russian-first operator wording polish.

## Handoff

`NG-X003` is closed. The recommended next docs-only slice is `NG-X001` gate naming consistency, because stale active-next wording is cleaned up and the remaining safe cosmetic work is to make gate-stage names consistent before any future VPS/read-only gate discussion.

Do not run `NG-V001` until the operator explicitly approves the gate and provides the target SSH alias/host outside repository secrets.
