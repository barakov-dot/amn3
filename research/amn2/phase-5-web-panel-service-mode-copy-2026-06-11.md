# Phase 5 P5-N002 web panel service-mode and external-only copy

Date: 2026-06-11.

Status: `completed-amn2-local-only`.

## Summary

`P5-N002` was completed as an AMN2 local-only web-panel copy polish slice.

AMN2 branch and commit:

```text
branch: codex/web-panel-service-external-copy
commit: 17454e9 Clarify web panel service-mode copy
source-of-truth branch: codex-vps-test-prep
push: ad6aa1b..17454e9 codex-vps-test-prep -> codex-vps-test-prep
```

Changed AMN2 files:

- `app/web/templates/integration_status.html`
- `app/web/templates/server_detail.html`
- `app/web/templates/user_detail.html`
- `tests/web/test_web_integration_status.py`
- `tests/web/test_servers.py`
- `tests/web/test_users.py`

## Behavior

The web panel now makes three operator-only boundaries clearer:

- `/integration-status` shows an `Operator-only boundary` note: web/admin stays on `127.0.0.1:3030` through SSH tunnel, API `3040` remains loopback-only/read-only, and public exposure/config delivery/write routes require separate named gates.
- `/servers/{id}` action notes distinguish a read-only local health record from a read-only peer inventory comparison that does not add or remove peers.
- `/users/{id}` marks `external_only` devices as `external-only import`, explains that they were imported for visibility only, and states that config resend, secrets and email delivery are unavailable for those records.

No route, form action, permission, database, config-generation or delivery behavior changed.

## Safety Boundary

No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed.

The slice changed local AMN2 web templates and tests only.

## Verification

RED before implementation:

```text
tests/web/test_web_integration_status.py tests/web/test_users.py::test_user_detail_marks_external_only_device_without_config_actions tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions -q
result: 3 failed, 1 passed, 1 warning
expected failures:
- missing operator-only boundary copy on /integration-status
- missing external-only import copy on /users/{id}
- missing clarified read-only action notes on /servers/{id}
```

GREEN after implementation:

```text
tests/web/test_web_integration_status.py tests/web/test_users.py::test_user_detail_marks_external_only_device_without_config_actions tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions -q
result: 4 passed, 1 warning

tests/web/test_web_integration_status.py tests/web/test_users.py tests/web/test_servers.py -q
result: 47 passed, 1 warning

python -m pytest -q
result: 664 passed, 1 warning

git diff --check
result: passed
```

AMN2 final state:

```text
branch: codex-vps-test-prep
head: 17454e9 Clarify web panel service-mode copy
working tree: clean
remote: amn2/codex-vps-test-prep at 17454e9
```

## Decision

`P5-N002` is closed as a local-only web-panel copy polish slice.

Follow-up status: `P5-X002` Единообразие bot button labels and captions was completed later on 2026-06-11 as AMN2 commit `fed832c`. Evidence: `research/amn2/phase-5-bot-labels-captions-2026-06-11.md`.
