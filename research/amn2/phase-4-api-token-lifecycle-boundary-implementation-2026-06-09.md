# Phase 4 P4-I005 API Token Lifecycle Boundary Implementation 2026-06-09

Дата: 2026-06-09.

## Decision

```text
candidate_id: P4-I005
status: implemented-local-only
AMN2 branch: codex/phase-4-api-token-lifecycle-boundary
AMN2 commit: 22061ea Show API token lifecycle boundary
base branch: codex/phase-4-aggregate-metrics-privacy-boundary
base commit: 8b6aef8 Show aggregate metrics privacy boundary
VPS gate: not required
```

## Scope

The slice makes the existing scoped API token lifecycle boundary visible in the read-only API status surface.

Changed in AMN2:

- `app/services/integration_status.py`
- `tests/api/test_api_integration_status.py`
- `tests/services/test_integration_status_service.py`
- `docs/API_TOKEN_POLICY.ru.md`
- `docs/API_ENDPOINT_TAXONOMY.ru.md`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`
- `docs/PROJECT_PHASE_MAP.ru.md`

`GET /api/integration/status` now includes safe `api_token_lifecycle_boundary` policy/status fields:

- route-connected tokens require explicit expiry;
- one-time secret display;
- digest-only storage label;
- allowed first-slice scopes: `metrics:read`, `server:read`;
- blocked scope classes: `config:read`, write, destructive remote-exec;
- owner status enforcement;
- idempotent revoke;
- create-new-then-revoke-old rotation;
- no production token mutation.

## RED/GREEN

RED:

```text
command: python -m pytest tests/services/test_integration_status_service.py::test_build_integration_status_reports_controlled_prod_without_write_enablement -v
result: 1 failed
expected failure: KeyError: 'api_token_lifecycle_boundary'
```

GREEN:

```text
command: python -m pytest tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit tests/services/test_integration_status_service.py::test_build_integration_status_reports_controlled_prod_without_write_enablement -v
result: 2 passed, 1 StarletteDeprecationWarning
```

Extended focused regression:

```text
command: python -m pytest tests/api/test_api_integration_status.py tests/services/test_integration_status_service.py tests/services/test_api_tokens.py tests/api/test_cli_tokens.py tests/api/test_read_only_status_contract.py tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py -v
result: 59 passed, 1 StarletteDeprecationWarning
```

Hygiene:

```text
git diff --check: passed
changed-file unsafe-marker scan: no matches
```

## Non-actions

No live VPS commands were run.

No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, production peer/user mutation, token issue/revoke/rotate API route or production token mutation was performed.

No upstream PRVTPRO/KYORESUAS code, UI, templates, scripts or managers were copied.

## Next Recommendation

Take `P4-N004` next as a local-only product polish slice: bot/admin read-only navigation labels and empty states. Use `P4-I001` only if another private-panel read-only UX pass is needed before wording can be inferred safely.
