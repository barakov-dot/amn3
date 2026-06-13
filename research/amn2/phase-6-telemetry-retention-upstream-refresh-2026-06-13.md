# Phase 6 telemetry retention and upstream refresh incorporation

Date: 2026-06-13.

## Scope

Closed together:

- `P6-N004` Aggregate telemetry retention/redaction policy.
- `P6-S002` Recurring upstream refresh incorporation.

This was completed as AMN2 local-only code/tests/docs. It does not enable raw
telemetry export, live upstream actions, public exposure, config delivery, write
API or production mutation.

## AMN2 result

Repository: `barakov-dot/amn2`.

Branch: `codex-vps-test-prep`.

Commit:

```text
a9f53d7 Add telemetry retention refresh policy
```

Pushed to:

```text
amn2/codex-vps-test-prep
```

Latest VPS-smoked/package head remains:

```text
2215761 Polish operator web admin UX
```

Package/smoke status for `a9f53d7`: not package-rebuilt, not VPS-smoked.

## Implemented

- Added `app.services.telemetry_retention_policy` with a machine-checkable
  retention/redaction and upstream refresh incorporation manifest.
- Added `docs/TELEMETRY_RETENTION_POLICY.ru.md`.
- Exposed the safe boundary through integration status and web
  `/integration-status`.
- Added blocked lanes for raw telemetry export and upstream refresh live actions
  without named gates.
- Advanced integration status `next_gate` to
  `P6-N001 public docs/API taxonomy if approved`.

## Verification

RED before implementation:

```text
tests/services/test_telemetry_retention_policy.py
result: 1 error, 1 warning
expected: ModuleNotFoundError: app.services.telemetry_retention_policy
```

Focused GREEN:

```text
tests/services/test_telemetry_retention_policy.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/web/test_web_integration_status.py
result: 11 passed, 1 warning
```

Expanded GREEN:

```text
tests/services/test_telemetry_retention_policy.py
tests/services/test_privacy_status_boundary.py
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/api/test_app.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
tests/web/test_web_integration_status.py
tests/web/test_logs_settings_orders.py
tests/web/test_server_health.py
result: 68 passed, 1 warning
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

`P6-N004` and `P6-S002` are removed from the active Phase 6 plan.

Next recommendation: `P6-X001 + P6-X002` together as local-only/docs/tests copy
and brand/media consistency work. `P6-N001` remains conditional on public docs
approval.
