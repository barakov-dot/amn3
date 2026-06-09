# Phase 4 Web-panel User/Config Visibility Implementation 2026-06-09

Date: 2026-06-09.

Status: `local-only-implemented`.

AMN2 branch:

```text
codex/phase-4-web-panel-user-config-visibility
```

AMN2 worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-p4-c009
```

## Root Cause

The web-panel `/users` view loads local AMN2 database users via `repo.list_users_for_admin()`.
It does not query live AmneziaWG peer inventory and does not automatically backfill live VPS peers into local users/devices.

Live/test peers that were created outside local AMN2 user/device records are represented through the server peer-sync/read-only inventory flow on server detail pages, not on the Users table by default.

Conclusion: the operator observation was a real product visibility gap, but the safe first fix is a read-only navigation/empty-state clarification. Any DB backfill, live sync, peer mutation, config delivery or automatic import remains blocked until a separate named write/config gate.

## Local Change

Changed in AMN2:

- `app/web/templates/users.html`
  - clarifies that Users lists local AMN2 database users/devices;
  - links operators to server peer sync for live VPS peers created outside AMN2;
  - changes the empty state from `No users yet.` to `No local users yet.`.
- `tests/web/test_users.py`
  - adds regression coverage for the local-vs-live visibility boundary.

## Verification

RED test:

```text
tests\web\test_users.py::test_users_page_explains_remote_peer_visibility_boundary
result: failed as expected before template change
```

GREEN focused test:

```text
tests\web\test_users.py::test_users_page_explains_remote_peer_visibility_boundary
result: 1 passed, 1 warning
```

Focused verification:

```text
tests\web\test_users.py
tests\web\test_servers.py::test_server_sync_run_displays_peer_inventory_report
tests\web\test_servers.py::test_server_detail_shows_managed_configs_before_peer_sync
tests\web\test_servers.py::test_collect_server_peer_sync_enriches_known_peers_with_user_and_device
result: 26 passed, 1 warning
```

Static check:

```text
git diff --check
result: passed
```

Note: tests used the existing AMN2 virtualenv from `worktrees\amn2-api-web-panel-finish\.venv` because the system and bundled Python did not have `pytest` installed.

## Safety Boundary

No live VPS commands were executed.
No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, API token issue/revoke, peer sync/apply/revoke or production peer/user mutation was performed.

## Next Recommendation

Continue with `P4-I002`: service-mode/read-only status and safety wording in AMN2 web/status surfaces.

Keep `P4-I001` as a fallback only if a second page-by-page private-panel UX pass is needed.
