# Remote Partial-Failure Contract Evidence 2026-06-06

Purpose: record the local-only AMN2 slice that tightens remote mutation partial-failure metadata after the Phase 2 live disposable peer gate and the post-PSK-stdin VPS smoke. This note does not publish `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK values, client configs, QR payloads, `vpn://` links, or full logs.

## Result

Status: `merged-in-stable-local-gate-complete`.

```text
repo: C:\Users\SooL\Documents\Amneziya
base branch: codex-vps-test-prep
base head: 6b5b5b7 Document stdin PSK peer apply
worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-remote-partial-failure-contract
branch: codex/remote-partial-failure-contract
head: 1a193b9 Add remote partial failure contract
remote: amn2/codex/remote-partial-failure-contract
target branch: codex-vps-test-prep
merged stable head: 1a193b9 Add remote partial failure contract
```

GitHub connector PR creation was attempted and failed with `403 Resource not accessible by integration`. The branch was pushed successfully, then `codex-vps-test-prep` was fast-forwarded locally and pushed directly:

```text
6b5b5b7..1a193b9  codex-vps-test-prep -> codex-vps-test-prep
```

## Scope

Local-only code and tests:

- centralizes `RemoteMutationResult` in `app.server.operations`;
- adds `remote_changed_local_failed_result()` for remote-changed/local-failed outcomes;
- allows `remote-changed-local-failed` and `local-changed-remote-failed` as state-changing consistency statuses;
- updates access approval and bot reset partial-failure paths to use the specific `remote-changed-local-failed` status;
- redacts recovery notes before they surface to higher-level workflows;
- documents the status in `docs/RUNTIME_REGISTRY.en.md`.

Not included:

- no VPS update or live VPS command;
- no `VPS_APPLY_ENABLED=true`;
- no `apply-peer --apply` or `revoke-peer --apply`;
- no public web/API exposure;
- no `/api/clients` write CRUD;
- no `config:read`;
- no public/self-service config delivery;
- no Local Agent config or mutation route;
- no backup/import/reboot route.

## TDD Evidence

Baseline before edits:

```text
tests/server/test_operation_runner.py tests/server/test_peer_apply.py
30 passed
```

RED checks:

```text
tests/server/test_operation_runner.py
expected failure: missing remote_changed_local_failed_result import

tests/services/test_access_service.py::test_approve_order_reports_partial_failure_when_remote_apply_succeeds_but_admin_audit_fails
tests/bot/test_bot_workflows.py::test_user_reset_reports_partial_failure_when_one_remote_remove_succeeds_and_next_fails
expected failures: old consistency_status was partial-failure
```

Focused validation after implementation:

```text
pytest tests/server/test_operation_runner.py tests/server/test_peer_apply.py tests/services/test_access_service.py tests/bot/test_bot_workflows.py -q --basetemp .pytest-tmp
70 passed
```

Focused validation after fast-forward merge into the main `amn2` checkout:

```text
pytest tests/server/test_operation_runner.py tests/server/test_peer_apply.py tests/services/test_access_service.py tests/bot/test_bot_workflows.py -q -p no:cacheprovider --basetemp C:\Users\SooL\Documents\VPS-OPS-LAB\.pytest-tmp-amn2-stable
70 passed
```

Additional checks:

```text
git diff --check
passed
```

## Safety Decision

This slice is safe to review as a local operation-contract change. It does not expand the live runner beyond the existing read-only runner and does not unlock broader write/API/config/agent surfaces.

The latest VPS-smoked runtime/source package remains `568c611`; the current production branch head after merging this local-only slice is `1a193b9`.
