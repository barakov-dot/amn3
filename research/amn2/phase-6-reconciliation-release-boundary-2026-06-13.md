# Phase 6 attach-existing-server reconciliation and release checklist boundary

Date: 2026-06-13.

## Scope

Closed together:

- `P6-M003` Attach-existing-server reconciliation beyond read-only report mode.
- `P6-S001` Release checklist and changelog.

This was completed as AMN2 local-only code/tests/docs. It does not enable live
reconciliation, write API, Local Agent mutation, package apply/rebuild on VPS,
public exposure, config delivery or production peer/user mutation.

## AMN2 result

Repository: `barakov-dot/amn2`.

Branch: `codex-vps-test-prep`.

Commit:

```text
3e1f4cc Add reconciliation release boundary
```

Pushed to:

```text
amn2/codex-vps-test-prep
```

Latest VPS-smoked/package head remains:

```text
2215761 Polish operator web admin UX
```

Package/smoke status for `3e1f4cc`: not package-rebuilt, not VPS-smoked.

## Implemented

- Added `app.services.reconciliation_release_boundary` with a machine-checkable
  report-only attach-existing-server reconciliation and release checklist
  manifest.
- Added `docs/RECONCILIATION_RELEASE_CHECKLIST.ru.md`.
- Exposed the safe boundary through integration status and web
  `/integration-status`.
- Added blocked lanes for reconciliation apply and release/package/public launch
  without the required named gates.
- Advanced integration status `next_gate` to
  `P6-N004 aggregate telemetry retention/redaction policy`.

## Verification

RED before implementation:

```text
tests/services/test_reconciliation_release_boundary.py
result: 1 error, 1 warning
expected: ModuleNotFoundError: app.services.reconciliation_release_boundary
```

Focused GREEN:

```text
tests/services/test_reconciliation_release_boundary.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/web/test_web_integration_status.py
result: 11 passed, 1 warning
```

Expanded GREEN:

```text
tests/services/test_reconciliation_release_boundary.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/api/test_app.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
tests/web/test_web_integration_status.py
tests/web/test_logs_settings_orders.py
tests/web/test_servers.py
result: 81 passed, 1 warning
```

`git diff --check` and staged `git diff --cached --check` passed.

Warning: existing `StarletteDeprecationWarning` from bundled FastAPI testclient.

## Safety

Not performed:

- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- payment processor integration;
- Telegram token use;
- live bot send;
- Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the required default.

## Plan update

`P6-M003` and `P6-S001` are removed from the active Phase 6 plan.

New candidate accepted by standing rule:

- `P6-N004` Aggregate telemetry retention/redaction policy: added to the
  normal-priority Phase 6 plan.

Next recommendation: `P6-N004` as local-only/docs/tests boundary work.
