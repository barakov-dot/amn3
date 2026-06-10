# Phase 4 NG: named gate / write API readiness charter 2026-06-10

Дата: 2026-06-10.

Назначение: открыть следующий этап после закрытой default local-only Phase 4 очереди. Этот этап называется `P4-NG` и используется для named gate planning, read-only VPS baseline gate readiness и будущего write API design без неявного live/write допуска.

## Decision

```text
stage_id: P4-NG
stage_name: Named Gate / Write API Readiness
operator_decision: proceed with gate-first planning
default_mode: docs-only gate planning
first_recommended_live_gate: NG-V001 read-only VPS baseline gate, only after explicit approval
write_api_live_status: blocked until separate P4-WRITE-API-LIVE-GATE
AMN2_code_changed: no
live_vps_commands: no
public_exposure: no
config_delivery: no
write_api_implementation: no
```

## NG-C001 Closed: Named Gate Charter

Every `P4-NG` gate must define:

```text
gate_name:
target:
operation_class:
allowed_actions:
blocked_actions:
preflight:
rollback_or_recovery:
safe_summary_fields:
secrets_policy:
go_no_go_decision:
evidence_file:
```

Default behavior:

- if a requested action is not in `allowed_actions`, it is blocked;
- if preflight fails, the gate returns `no-go` or `defer`;
- if evidence would require secrets/full logs, evidence must be reduced to safe summary fields;
- a named gate authorizes only the listed actions, not adjacent work.

## NG-C002 Closed: Safety Boundary

The following remain closed after this charter:

- `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS public cutover;
- production peer/user mutation;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- token issue/revoke/rotate API routes;
- secret-bearing evidence publication.

## Priority Plan

Plan file:

```text
docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md
```

Closed and removed from active plan:

- `NG-C001` named gate charter;
- `NG-C002` safety boundary restatement.
- `NG-C003` secrets policy for gate outputs;
- `NG-C004` go/no-go format for all gates;
- `NG-S003` reusable named-gate evidence template;
- `NG-C005` write API live-block assertion;
- `WAPI-V001` write API threat model;
- `WAPI-V002` write API route taxonomy;
- `WAPI-V003` local fake-runner contract;
- `WAPI-V004` idempotency, locking and partial-failure model;
- `WAPI-V005` write API audit/redaction requirements;
- `WAPI-I004` operation status model;
- `WAPI-I003` scoped write-token model;
- `WAPI-I002` config delivery decoupling;
- `WAPI-I001` `/api/clients` design without live CRUD;
- `WAPI-I005` web-panel gated action labels;
- `NG-N003` operation queue design after write API contract.

Active next recommendation:

```text
NG-N002 health/status polling design
```

Reason: it is docs-only and is constrained by `live_write_authorized: no`.

Reusable gate evidence template:

```text
research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md
```

Write API live-block assertion:

```text
research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md
```

Write API threat model:

```text
research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md
```

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
