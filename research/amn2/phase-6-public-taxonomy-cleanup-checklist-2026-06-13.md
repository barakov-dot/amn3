# Phase 6 P6-N001 public docs/API taxonomy + P6-C007 checklist-only

Date: 2026-06-13.

## Scope

`P6-N001` Public docs/API taxonomy if public docs are approved and the
checklist-only part of `P6-C007` Destructive cleanup/reinstall gate were
completed together as AMN2 local-only code/tests/docs.

AMN2 branch: `codex-vps-test-prep`.

AMN2 commit: `c46f664 Add public taxonomy cleanup checklist`.

AMN2 remote: `amn2/codex-vps-test-prep`.

Latest VPS-smoked/package head remains: `b3102db Add client compatibility
delivery boundary`.

`c46f664` is local-only and not package-rebuilt/VPS-smoked.

## What changed in AMN2

- Added `app.services.public_productization_boundaries`.
- Added `docs/PUBLIC_DOCS_API_TAXONOMY.ru.md`.
- Added `docs/DESTRUCTIVE_CLEANUP_GATE_CHECKLIST.ru.md`.
- Exposed safe summaries through `/api/integration/status`.
- Exposed the same safe summaries through web `/integration-status`.
- Added regression tests for the taxonomy/checklist boundaries and integration
  status redaction.

## Public docs/API taxonomy result

Status: `public_docs_api_taxonomy_ready`.

Publication flags remain disabled:

- `publication_enabled=false`;
- `public_docs_enabled=false`;
- `public_openapi_enabled=false`;
- `public_api_exposed=false`.

The taxonomy separates:

- public-safe product/client guidance;
- operator-only admin/API/status surfaces;
- blocked secret-bearing delivery/config material;
- blocked write/destructive surfaces.

Actual public publication still requires `P6-C001 Public exposure gate`.

## Destructive cleanup checklist result

Status: `destructive_cleanup_checklist_ready`.

Mode: `checklist_only`.

Execution flags remain disabled:

- `destructive_execution_enabled=false`;
- `cleanup_commands_enabled=false`.

The checklist records required preconditions for a future destructive gate:

- operator opens `P6-C007` by name;
- retention/data-loss decision is recorded;
- current AMN2 head/package choice is recorded;
- rollback or rebuild stop criteria are recorded;
- operator-local secret handoff is ready;
- second confirmation is required before any destructive action.

Blocked without the named gate:

- provider rebuild;
- disk wipe;
- service stop;
- database deletion;
- firewall/public listener change;
- live cleanup command execution.

## Verification

Focused taxonomy/status suite:

```text
11 passed, 1 StarletteDeprecationWarning
```

Security and file hygiene:

```text
26 passed
```

Toolchain:

```text
AMN2 toolchain ok: CPython 3.12.x.
```

Whitespace checks:

```text
git diff --check passed
git diff --cached --check passed
```

## Safety statement

This slice did not perform live VPS commands, SSH commands, package
apply/rebuild on VPS, service restart/deploy, public exposure, real config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive VPS action, payment provider integration,
Telegram token use, live bot send, Telegram profile mutation, secret-bearing
evidence publication or upstream/GPL code copy.

`P6-N001` is removed from the active Phase 6 plan.

`P6-C007` remains critical gated/deferred. Only the checklist was completed;
cleanup/reinstall/destructive execution still requires a separate named gate.

## Next recommendation

The default local-only Phase 6 queue is now empty. Practical next choices are:

- single: `P6-C006` local package refresh/preflight for AMN2 `c46f664`, without
  live apply;
- pair: `P6-C006` local package refresh/preflight + current-head smoke plan,
  without VPS commands;
- gated live path: open a named live gate only if the operator wants to update
  the disposable VPS from `b3102db` to the current AMN2 head.
