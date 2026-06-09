# Phase 4 Aggregate Metrics Privacy Boundary Implementation

Дата: 2026-06-09.

Status: `completed-local-only`.

## AMN2 Source

```text
repo: C:\Users\SooL\Documents\Amneziya
worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-n003-aggregate-metrics-privacy
branch: codex/phase-4-aggregate-metrics-privacy-boundary
base: codex/phase-4-endpoint-taxonomy-route-policy-docs
base_commit: acf39f8 Add API endpoint taxonomy docs
commit: 8b6aef82d9b5916cf3a6ac9603f4e998ad4fdf50 Show aggregate metrics privacy boundary
```

## Implemented Scope

AMN2 local-only changes:

- `GET /api/metrics/summary` now includes an additive safe `privacy` object:
  - `aggregate_only=true`;
  - `per_peer_fields=false`;
  - `per_user_fields=false`;
  - `public_exposure=false`.
- `tests/api/test_app.py` locks the metrics response privacy boundary and keeps the route under `metrics:read`.
- `docs/API_ENDPOINT_TAXONOMY.ru.md` records the aggregate metrics privacy boundary.
- `docs/API_TOKEN_POLICY.ru.md`, `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md` and `docs/PROJECT_PHASE_MAP.ru.md` link the boundary back to the Phase 4 read-only API contract.

The slice is additive and does not change route count, scopes, token lifecycle, storage, remote operations or listener exposure.

## TDD Evidence

RED:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/api/test_app.py::test_api_metrics_requires_metrics_read_scope_and_shows_privacy_boundary -v
1 failed, 1 warning

Expected failure:
Right contains 1 more item:
{'privacy': {'aggregate_only': True,
             'per_peer_fields': False,
             'per_user_fields': False,
             'public_exposure': False}}
```

GREEN:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/api/test_app.py::test_api_metrics_requires_metrics_read_scope_and_shows_privacy_boundary -v
1 passed, 1 warning
```

## Verification

Focused verification:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/api/test_app.py::test_api_metrics_requires_metrics_read_scope_and_shows_privacy_boundary tests/api/test_read_only_status_contract.py tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py -v
34 passed, 1 warning
```

Extended verification:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/api/test_app.py tests/api/test_read_only_status_contract.py tests/api/test_cli_tokens.py tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py -v
50 passed, 1 warning
```

Static checks:

```text
git diff --check
passed

marker scan for placeholder markers and forbidden enabled-claim phrases in touched AMN2 files
passed with no matches
```

Post-commit AMN2 status:

```text
## codex/phase-4-aggregate-metrics-privacy-boundary
clean
```

## Non-Actions

No live VPS commands were run.

No route count changed.

No new API route was added.

No public OpenAPI/Swagger/docs exposure was added.

No public API `3040` was opened.

No direct public web/admin `3030` was opened.

No config delivery was added.

No `/api/clients` write CRUD was added.

No Local Agent mutation route was added.

No token lifecycle action was performed against production state.

No backup/import/reboot action was performed.

No production peer/user mutation was performed.

No upstream GPL code, templates or OpenAPI definitions were copied.

## Follow-Up Recommendation

Remove `P4-N003` aggregate metrics privacy boundary visibility from the active plan.

Next safe local-only slice: `P4-I005` scoped API token lifecycle boundary, because the read-only API surface now has route count, taxonomy and metrics privacy guards. The next API safety risk is token lifecycle and scope hygiene before any future route expansion.
