# Phase 4 P4-N004 Bot/Admin Read-only Labels Implementation 2026-06-09

Дата: 2026-06-09.

## Decision

```text
candidate_id: P4-N004
status: implemented-local-only
AMN2 branch: codex/phase-4-bot-admin-read-only-labels
AMN2 commit: c9829b7 Clarify bot admin read-only labels
base branch: codex/phase-4-api-token-lifecycle-boundary
base commit: 22061ea Show API token lifecycle boundary
VPS gate: not required
```

## Scope

The slice improves bot/admin read-only navigation labels and empty-state wording without changing callback data, routes, POST behavior or runtime state.

Changed in AMN2:

- web admin base navigation now shows service-mode SSH tunnel/loopback and gated write/config/public boundaries;
- web users empty state clarifies that approved live peers remain in server peer sync until a separate sync/backfill gate;
- web servers empty state clarifies local server records versus live VPS discovery/mutation gates;
- bot admin navigation marks traffic as aggregate and users as local;
- bot admin empty states clarify safe list views, local users, no live VPS peer reads and no backfill/config delivery from list views;
- AMN2 docs record that these are UI/status labels only.

## RED/GREEN

RED:

```text
command: python -m pytest tests/web/test_app.py::test_login_success_shows_dashboard_with_repository_counts tests/web/test_users.py::test_users_page_explains_remote_peer_visibility_boundary tests/web/test_servers.py::test_servers_empty_state_marks_local_records_and_live_gate tests/bot/test_telegram_ux.py::test_admin_navigation_includes_templates_and_traffic_actions tests/bot/test_telegram_ux.py::test_admin_empty_states_explain_local_read_only_boundaries -v
result: 5 failed, 1 StarletteDeprecationWarning
expected failures: missing service-mode nav labels, missing web empty-state labels, old bot admin labels and old bot empty-state text
```

GREEN:

```text
command: python -m pytest tests/web/test_app.py::test_login_success_shows_dashboard_with_repository_counts tests/web/test_users.py::test_users_page_explains_remote_peer_visibility_boundary tests/web/test_servers.py::test_servers_empty_state_marks_local_records_and_live_gate tests/bot/test_telegram_ux.py::test_admin_navigation_includes_templates_and_traffic_actions tests/bot/test_telegram_ux.py::test_admin_empty_states_explain_local_read_only_boundaries -v
result: 5 passed, 1 StarletteDeprecationWarning
```

Expanded web/bot regression:

```text
command: python -m pytest tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/bot/test_telegram_ux.py tests/bot/test_bot_handlers.py -v
result: 113 passed, 1 StarletteDeprecationWarning
```

Extended regression:

```text
command: python -m pytest tests/web tests/bot tests/security/test_surface_policy.py tests/test_file_hygiene.py -v
result: 238 passed, 1 StarletteDeprecationWarning
```

Hygiene:

```text
git diff --check: passed
changed-file unsafe-marker scan: no matches
```

## Non-actions

No live VPS commands were run.

No public API `3040`, direct public web/admin `3030`, Caddy/HTTPS/domain cutover, config delivery, `/api/clients` write CRUD, Local Agent mutation, backup/import/reboot, production peer/user mutation, token issue/revoke/rotate API route, production token mutation or callback/action behavior change was performed.

No upstream PRVTPRO/KYORESUAS code, UI, templates, scripts or managers were copied.

## Next Recommendation

Take `P4-N001` next as a local-only docs/status drift synchronization slice. Use `P4-I001` only if another private-panel read-only UX pass is needed before choosing more UI wording work.
