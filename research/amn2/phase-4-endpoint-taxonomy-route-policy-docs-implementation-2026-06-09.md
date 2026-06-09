# Phase 4 Endpoint Taxonomy / Route-Policy Docs Alignment Implementation

Дата: 2026-06-09.

Status: `completed-local-only-docs`.

## AMN2 Source

```text
repo: C:\Users\SooL\Documents\Amneziya
worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-endpoint-taxonomy-route-policy-docs
branch: codex/phase-4-endpoint-taxonomy-route-policy-docs
base: codex/phase-4-read-only-api-status-schema
base_commit: b71b8f4 Lock read-only API status contract
commit: acf39f86e9669bd09ca032768a260289a9c2ff1a Add API endpoint taxonomy docs
```

## Implemented Scope

AMN2 docs-only changes:

- added `docs/API_ENDPOINT_TAXONOMY.ru.md`;
- linked the taxonomy from `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`;
- linked the taxonomy from `docs/API_TOKEN_POLICY.ru.md`;
- updated `docs/PROJECT_PHASE_MAP.ru.md` so `P4-I003` remains the runtime/contract guard baseline and the endpoint taxonomy is recorded as a follow-up local docs alignment.

The taxonomy records the current private/local read-only `/api/*` surface:

- `GET /api/servers` with `server:read`;
- `GET /api/servers/{server_name}/summary` with `server:read`;
- `GET /api/integration/status` with `server:read`;
- `GET /api/local-agent/runtime/summary` with `server:read`;
- `GET /api/metrics/summary` with `metrics:read`;
- `GET /api/users/summary` with `metrics:read`.

It keeps `route_count=6`, `checked_routes=6`, `API_RUNTIME_ROUTE_BINDINGS`, safe `api_read` metadata, forbidden response markers and no-public-docs/public-listener boundaries visible in one local product/policy map.

## Verification

AMN2 verification:

```text
git diff --check
passed

Select-String marker scan for placeholder markers and forbidden enabled-claim phrases
passed on the AMN2 touched docs with no matches

C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py tests/api/test_read_only_status_contract.py -v
33 passed, 1 warning
```

Post-commit AMN2 status:

```text
## codex/phase-4-endpoint-taxonomy-route-policy-docs
clean
```

## Non-Actions

No live VPS commands were run.

No runtime route code changed.

No public OpenAPI/Swagger/docs exposure was added.

No public API `3040` was opened.

No direct public web/admin `3030` was opened.

No Caddy/HTTPS/domain cutover was performed.

No config delivery was added.

No `/api/clients` write CRUD was added.

No Local Agent mutation route was added.

No token issue/revoke/rotate action was performed against production state.

No backup/import/reboot action was performed.

No production peer/user mutation was performed.

No upstream GPL code, templates or OpenAPI definitions were copied.

## Follow-Up Recommendation

Remove endpoint taxonomy / route-policy docs alignment from the active plan.

Next safe local-only slice: `P4-N003` aggregate metrics privacy boundary visibility, because the endpoint taxonomy now names the aggregate metrics route and the next product risk is keeping metrics useful without drifting into per-peer/per-user detail.
