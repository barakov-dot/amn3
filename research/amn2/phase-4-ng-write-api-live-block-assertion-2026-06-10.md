# Phase 4 NG-C005: write API live-block assertion 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `NG-C005` как AMN3 docs-only решение перед любым write API design slice. Этот документ не разрешает AMN2 runtime changes, live VPS commands, SSH commands, public exposure, config delivery or production mutation.

## Decision

```text
task_id: NG-C005
task_name: keep write API live work blocked
result: closed
live_write_authorized: no
write_api_design_authorized: docs-only/local-only after explicit selection
selected_next_slice: WAPI-V001 write API threat model
selected_next_slice_mode: docs-only
selected_next_slice_live_write_authorized: no
AMN2_code_changed: no
runtime_routes_changed: no
live_vps_commands: no
ssh_commands: no
public_exposure: no
config_delivery: no
production_peer_user_mutation: no
```

`NG-C005` is satisfied because the next write API slice is explicitly constrained to `live_write_authorized: no`.

## Blocked Live/Write Surface

The following remain blocked after this decision:

- `/api/clients` write CRUD;
- peer apply/revoke/sync;
- config delivery, including `.conf`, QR, `vpn://`, share/download links and archives;
- token issue/revoke/rotate API routes;
- Local Agent mutations;
- backup/import/reboot;
- package apply;
- service restart/enable/disable;
- firewall/reverse proxy edits;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- production peer/user mutation.

## Required Header For Future Write API Slices

Every future write API design or implementation slice must state:

```text
slice_id:
slice_mode:
live_write_authorized: no
runtime_routes_changed:
config_delivery:
production_mutation:
required_gate_for_live_write: P4-WRITE-API-LIVE-GATE
```

If a future slice needs live write behavior, the current slice must stop and a separate named gate must be created first.

## WAPI-V001 Entry Gate

`WAPI-V001` may be selected next only as docs-only threat modeling:

```text
slice_id: WAPI-V001
slice_name: write API threat model
slice_mode: docs-only
live_write_authorized: no
runtime_routes_changed: no
AMN2_code_changed: no
live_vps_commands: no
```

Allowed `WAPI-V001` output:

- threat model categories;
- safe route taxonomy assumptions;
- fake-runner and idempotency questions;
- audit/redaction requirements;
- test requirements for a future local-only implementation plan.

Blocked `WAPI-V001` output:

- adding runtime API routes;
- adding `/api/clients` write CRUD;
- adding token issue/revoke/rotate routes;
- enabling config delivery;
- running SSH or VPS commands;
- changing production peer/user state.

## Go/No-Go Result

```text
go_no_go_decision: go
go_scope: WAPI-V001 docs-only threat model with live_write_authorized: no
no_go_scope: live write, runtime route expansion, public exposure, config delivery, SSH/VPS commands, production mutation
defer_scope: any request that requires P4-WRITE-API-LIVE-GATE or NG-V001 approval
```

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
