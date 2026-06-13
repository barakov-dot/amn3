# Phase 6 privacy-safe health/status and admin analytics boundary

Date: 2026-06-13.

## Scope

Closed together:

- `P6-M002` Health/status polling scheduler with aggregate-only privacy boundary.
- `P6-N002` Admin analytics without per-peer/user leakage.

This was completed as AMN2 local-only code/tests/docs. No live scheduler, live probe,
public route, write route, config delivery or Local Agent mutation was enabled.

## AMN2 result

Repository: `barakov-dot/amn2`.

Branch: `codex-vps-test-prep`.

Commit:

```text
8f4ac6a Add privacy status analytics boundary
```

Pushed to:

```text
amn2/codex-vps-test-prep
```

Latest VPS-smoked/package head remains:

```text
2215761 Polish operator web admin UX
```

Package/smoke status for `8f4ac6a`: not package-rebuilt, not VPS-smoked.

## Implemented

- Added `app.services.privacy_status_boundary` with a machine-checkable
  aggregate-only health/status and admin analytics policy manifest.
- Added `docs/PRIVACY_STATUS_ANALYTICS_BOUNDARY.ru.md`.
- Exposed the safe boundary through integration status and web `/integration-status`.
- Kept API `/api/integration/status` sanitized: sensitive marker-name lists are
  reduced to counts for API payloads while the service/web policy manifest remains
  available to operator/admin context.
- Added blocked-future surface policy entries for health polling run and
  per-user/per-peer analytics detail routes.
- Advanced integration status `next_gate` to
  `P6-M003 attach-existing-server reconciliation`.

## Verification

RED before implementation:

```text
tests/services/test_privacy_status_boundary.py
result: 1 error, 1 warning
expected: ModuleNotFoundError: app.services.privacy_status_boundary
```

Focused GREEN:

```text
tests/services/test_privacy_status_boundary.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/security/test_surface_policy.py
tests/web/test_web_integration_status.py
result: 33 passed, 1 warning
```

Expanded GREEN:

```text
tests/services/test_privacy_status_boundary.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/api/test_app.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
tests/web/test_web_integration_status.py
tests/web/test_logs_settings_orders.py
tests/web/test_server_health.py
result: 65 passed, 1 warning
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

## Closeout

`P6-M002` and `P6-N002` are removed from the active Phase 6 plan.

Next recommendation: `P6-M003` attach-existing-server reconciliation beyond
read-only report mode, as local-only/docs/tests boundary work without enabling
write API, live reconciliation, Local Agent mutation or production peer/user
mutation.
