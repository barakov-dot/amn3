# Phase 4 NG: secrets policy and go/no-go format 2026-06-10

Дата: 2026-06-10.

Назначение: закрыть `NG-C003` и `NG-C004` как AMN3 docs-only policy work before any read-only VPS command is proposed.

## Decision

```text
stage_id: P4-NG
closed_tasks: NG-C003, NG-C004, NG-S003
default_mode: docs-only gate planning
template_created: research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md
AMN2_code_changed: no
live_vps_commands: no
ssh_command: no
public_exposure: no
config_delivery: no
write_api_implementation: no
```

`NG-S003` is closed together with `NG-C003` and `NG-C004` because both critical tasks require an active reusable gate evidence template.

## NG-C003 Closed: Secrets Policy

Gate evidence may contain only:

- boolean/status summaries;
- safe aggregate counts;
- `present`/`absent`;
- `passed`/`failed`;
- `not_checked`;
- redacted error summaries.

Gate evidence must never publish:

- `.env` values or raw `.env`;
- raw `servers.yml`;
- raw tokens;
- Authorization headers;
- token hashes;
- web password hash;
- session secret;
- private keys;
- PSK;
- peer public keys;
- client `.conf`;
- QR payloads or QR images;
- `vpn://` links;
- backup contents;
- public endpoint values;
- session cookies;
- full logs;
- secret-bearing command output.

## NG-C004 Closed: Go/No-Go Format

Every `P4-NG` gate must end with exactly one of:

```text
go_no_go_decision: go
go_no_go_decision: no-go
go_no_go_decision: defer
```

Decision rules:

- `go`: all approved checks passed, no blocked action was performed, no secret-bearing evidence was published.
- `no-go`: approval is absent/ambiguous, preflight fails, a blocked action would be needed, or a secret-safe summary cannot be produced.
- `defer`: target/context is missing, operator intentionally postpones, or more design work is needed before the gate can run.

`go` authorizes only the completed gate result. It does not authorize adjacent VPS/live/public/write/config work.

## Files Updated

- `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`
- `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`
- `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`
- `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`
- `research/amn2/transfer-backlog.md`

## Safety Statement

No AMN2 code, live VPS command, SSH command, package apply, route expansion, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` CRUD, Local Agent mutation, token issue/revoke/rotate route, backup/import/reboot or production peer/user mutation was performed.
