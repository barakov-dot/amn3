# Phase 4 NG-X002: Russian-first operator wording polish

Дата: 2026-06-10.

Назначение: закрыть косметическую docs-only задачу `NG-X002` и сделать активные P4-NG operator-facing headings, next-step wording и инструкции русскими-first. Технические идентификаторы, route names, gate names, file paths, branch names и candidate ids не переименовываются.

## Решение

```text
slice_id: NG-X002
slice_name: Russian-first operator wording polish
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
selected_next_slice: none
default_docs_only_cosmetic_queue: closed
```

## Что Обновлено

- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md` теперь использует Russian-first operator headings для текущей границы, закрытого списка, активного плана и рекомендации.
- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`, `docs/PROJECT_STATUS_CURRENT.ru.md`, `docs/PROJECT_CONTEXT_IMPORT.ru.md`, `research/amn2/transfer-backlog.md`, `research/amn2/phase-4-candidate-registry-2026-06-09.md`, `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md` и `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md` фиксируют, что `NG-X002` закрыт и default docs-only cosmetic queue больше не имеет активных задач.
- Старые evidence-файлы больше не оставляют `NG-X002` как active next-step.

## Что Не Менялось

- `NG-*`, `WAPI-*`, `P4-*` task ids.
- Route names, scopes, request/response field names.
- Gate names, включая `P4-NG-*`.
- File paths, branch names, commit ids and evidence ids.
- Runtime behavior, API routes, web templates, tests and AMN2 code.

## Негативные Проверки

`NG-X002` не разрешает:

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

## Оставшийся Активный План

Критичные: нет активных задач.

Очень важные:

- `NG-V001` read-only VPS baseline gate, только после отдельного явного named approval.

Важные: нет активных задач.

Нормальные: нет активных задач.

Простые: нет активных задач.

Косметические: нет активных задач.

## Handoff

`NG-X002` is closed. Очередь default docs-only cosmetic закрыта. Следующее осмысленное P4-NG решение: либо explicit approval для `NG-V001` read-only VPS baseline gate с target SSH alias/host вне repository secrets, либо отдельный local-only design boundary, например `P4-PRVTPRO-REFRESH-003`, до любой implementation.

Do not run `NG-V001` until the operator explicitly approves the gate and provides the target SSH alias/host outside repository secrets.
