# Phase 4 P4-I003 Read-only API Status Schema Implementation 2026-06-09

Date: 2026-06-09.

Status: `implemented-local-gate-complete`.

Candidate:

```text
candidate_id: P4-I003
priority: important
design: research/amn2/phase-4-read-only-api-status-design-2026-06-09.md
plan: docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md
```

AMN2 implementation:

```text
branch: codex/phase-4-read-only-api-status-schema
commit: b71b8f4 Lock read-only API status contract
base: 83f6d28 Show service mode status boundary
worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-i003-read-only-api-status-schema
```

## Changed AMN2 Files

```text
app/security/surface_bindings.py
docs/API_TOKEN_POLICY.ru.md
docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
tests/api/test_api_integration_status.py
tests/api/test_read_only_status_contract.py
tests/security/test_surface_policy_bindings.py
```

## Implementation Summary

Implemented local-only contract hardening for the existing read-only API/status surface:

- added `API_RUNTIME_ROUTE_BINDINGS` for exactly the six existing `/api/*` routes;
- added runtime drift coverage proving the mounted FastAPI API routes match policy bindings;
- added `tests/api/test_read_only_status_contract.py` to lock:
  - exactly six read-only API routes;
  - `server:read` and `metrics:read` scope separation;
  - safe response payloads without forbidden markers;
  - safe `api_read` audit metadata without raw bearer tokens, Authorization headers, token hashes or response bodies;
  - `service_mode_loopback_ready` status and service-mode boundary fields on `/api/integration/status`;
  - blocked lanes for public API, write CRUD, config delivery, Local Agent configs/mutations and backup/import/reboot;
- updated stale `/api/integration/status` API expectations from the old manual-prelaunch baseline to the accepted Phase 3 service-mode baseline;
- updated AMN2 policy docs to describe the P4-I003 contract hardening.

No runtime route expansion was performed.

## Verification

RED:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/security/test_surface_policy_bindings.py::test_api_runtime_routes_match_policy_bindings -v

result: failed as expected
reason: ImportError: cannot import name 'API_RUNTIME_ROUTE_BINDINGS'
```

GREEN and focused checks:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/security/test_surface_policy_bindings.py::test_api_runtime_routes_match_policy_bindings -v
result: 1 passed

C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py -v
result: 25 passed

C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/api/test_read_only_status_contract.py -v
result: 8 passed, 1 StarletteDeprecationWarning

C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests/security/test_surface_policy_bindings.py tests/security/test_surface_policy.py tests/api/test_app.py tests/api/test_api_integration_status.py tests/api/test_cli_tokens.py tests/api/test_read_only_status_contract.py tests/services/test_integration_status_service.py -v
initial result: 1 failed, 55 passed, 1 StarletteDeprecationWarning
fix: updated stale manual-prelaunch expectations in tests/api/test_api_integration_status.py to service-mode loopback baseline
final result: 56 passed, 1 StarletteDeprecationWarning

git diff --check
result: passed
```

Post-commit AMN2 checks:

```text
git status --short --branch
result: clean on codex/phase-4-read-only-api-status-schema

git log -3 --oneline --decorate
result:
b71b8f4 (HEAD -> codex/phase-4-read-only-api-status-schema) Lock read-only API status contract
83f6d28 (codex/phase-4-service-mode-status-wording) Show service mode status boundary
a73e845 (codex/phase-4-web-panel-user-config-visibility) Clarify user visibility boundary
```

## Explicit Non-actions

```text
live_vps_commands: none
new_routes: none
public_exposure: none
public_api_3040: not opened
direct_public_web_admin_3030: not opened
caddy_https_domain_cutover: none
config_delivery: none
api_clients_write_crud: none
local_agent_mutation: none
backup_import_reboot: none
token_lifecycle_real_operator_action: none
production_peer_user_mutation: none
upstream_code_copied: none
```

## Next Recommendation

Treat `P4-I003` as local-gate-complete. Recommended next default-mode work is `P4-I001` only if another private-panel read-only UX pass is needed; otherwise continue with normal local-only endpoint taxonomy / route-policy docs alignment based on this implementation result.
