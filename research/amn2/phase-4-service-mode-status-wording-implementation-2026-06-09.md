# Phase 4 Service-mode Status Wording Implementation 2026-06-09

Date: 2026-06-09.

Status: `local-only-implemented`.

AMN2 branch:

```text
codex/phase-4-service-mode-status-wording
```

AMN2 commit:

```text
83f6d28 Show service mode status boundary
```

Stacked base:

```text
a73e845 Clarify user visibility boundary
```

AMN2 worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-i002
```

## Scope

`P4-I002` updated AMN2 local/read-only integration status wording so the private web/admin panel now shows the accepted Phase 3 service-mode baseline:

- web/bot services are active;
- web/admin is `127.0.0.1:3030` loopback-only;
- operator access is SSH tunnel only;
- direct public web/admin `3030` is closed;
- public API `3040` is absent/closed;
- TCP `80/443` are absent;
- domain/HTTPS cutover is deferred because no domain is planned;
- `VPS_APPLY_ENABLED=false`;
- public/write/config changes require a separate named gate.

## Local Change

Changed in AMN2:

- `app/services/integration_status.py`
  - updates the status report from stale manual-prelaunch/systemd-deferred wording to `service_mode_loopback_ready`;
  - adds a safe `service_mode_boundary` section;
  - adds blocked lanes for direct public web/admin `3030`, Caddy/HTTPS/domain cutover and production peer/user mutation;
  - updates the next gate wording to require a separate named gate before public/write/config changes.
- `app/web/templates/integration_status.html`
  - renders a `Service-mode boundary` panel.
- `tests/services/test_integration_status_service.py`
  - covers the service-mode boundary and current safe status contract.
- `tests/web/test_web_integration_status.py`
  - covers visible private-panel wording and no-secret markers.

## Verification

RED test:

```text
tests\web\test_web_integration_status.py
tests\services\test_integration_status_service.py
result: 2 failed, 3 passed, 1 warning
expected failures: stale manual_prelaunch_ready status and missing Service-mode boundary panel
```

GREEN focused test:

```text
tests\web\test_web_integration_status.py
tests\services\test_integration_status_service.py
result: 5 passed, 1 warning
```

Focused verification:

```text
tests\web\test_web_integration_status.py
tests\services\test_integration_status_service.py
tests\web\test_api_readiness.py
result: 7 passed, 1 warning
```

Static check:

```text
git diff --check
result: passed
```

Note: tests used the existing AMN2 virtualenv from `worktrees\amn2-api-web-panel-finish\.venv`.

## Safety Boundary

No live VPS commands were executed.
No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, API token issue/revoke, peer sync/apply/revoke or production peer/user mutation was performed.

## Next Recommendation

Default next step: do not start another implementation slice until the operator decides whether a second read-only UX pass is needed.

Recommended options:

1. `P4-I001`: second detailed private-panel read-only UX pass if page-level wording/details are still unclear.
2. Route/secret gate planning for future API expansion if no more immediate private-panel UX evidence is needed.
