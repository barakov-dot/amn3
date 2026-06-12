# Phase 4 P4-PRVTPRO-REFRESH-001: read-only About/Version/Build status implementation 2026-06-10

Назначение: закрыть `P4-PRVTPRO-REFRESH-001` как AMN2 local-only product slice после PRVTPRO refresh 2026-06-10. Slice добавляет authenticated read-only About page в web-admin, чтобы оператор видел безопасные version/build/runtime labels перед gate decisions и evidence reporting.

## Gate Summary

```text
task_id: P4-PRVTPRO-REFRESH-001
source_signal: research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md
source_license_boundary: PRVTPRO/Amnezia-Web-Panel GPL-3.0 research-only
amn2_branch: codex/phase-4-prvtpro-build-status
amn2_commit: dc7966628e490da018f55fafe0fc559b44cc1dfa Add web admin build status page
implementation_class: local-only
live_vps_commands: no
ssh_commands: no
public_exposure_changed: no
api_routes_added_or_changed: no
write_api_added_or_changed: no
config_delivery_changed: no
local_agent_mutation_changed: no
backup_import_reboot_changed: no
production_peer_or_user_mutation: no
gpl_code_copied: no
go_no_go_decision: go
```

## AMN2 Changes

- `app/services/build_status.py`: adds `build_about_status()` with package version, Python runtime and read-only build boundary labels.
- `app/web/app.py`: adds authenticated `GET /about` web-admin page.
- `app/web/templates/about.html`: renders application version, runtime labels, read-only build status and blocked surfaces.
- `app/web/templates/base.html`: adds the `About` navigation link for authenticated operators.
- `tests/web/test_about.py`: covers auth requirement, safe version/build/runtime display and forbidden marker absence.

The change does not add API routes, POST handlers, write API, token issue/revoke API routes, config delivery, live peer apply/revoke/sync, backup/import/reboot behavior, public listeners or Local Agent mutations.

## TDD Evidence

RED:

```text
python -m pytest tests\web\test_about.py -q
result: failed as expected
failures:
- /about returned 404 instead of authenticated redirect
- authenticated dashboard did not contain href="/about"
```

GREEN:

```text
python -m pytest tests\web\test_about.py -q
result: 2 passed, 1 warning
```

Regression scope:

```text
python -m pytest tests\web\test_about.py tests\web\test_app.py tests\web\test_api_readiness.py tests\web\test_web_integration_status.py -q
result: 19 passed, 1 warning
warning: existing StarletteDeprecationWarning from fastapi.testclient/httpx
```

Hygiene:

```text
git diff --check
result: passed
git diff --cached --check
result: passed before AMN2 commit
```

## Safety Notes

This slice uses the PRVTPRO refresh only as a product/status UX signal. No GPL code, templates, UI implementation, manager implementation or workflow was copied. The AMN2 page, service and tests are native AMN2 changes.

The About page is available only inside authenticated web-admin navigation. It exposes package/runtime/build boundary labels only and does not print `.env`, raw `servers.yml`, tokens, Authorization headers, token hashes, password/session secrets, keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents, endpoint values, cookies, full logs or command output.

## Closure

`P4-PRVTPRO-REFRESH-001` is closed. Subsequent Phase 5 status:

- `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping was later closed as AMN3 docs-only policy support in `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`.
- `P4-PRVTPRO-REFRESH-003` was later closed as a carried Phase 4 item: AMN3 design boundary first, then AMN2 `P5-L001` local cached display; live probes/actions remain separately gated.

Recommended next safe direction after the later `P4-PRVTPRO-REFRESH-004` closure: choose `WAPI-V002` if continuing the named-gate write API taxonomy track, or create the `P4-PRVTPRO-REFRESH-003` design boundary before any PRVTPRO-derived server status/latency UX work.
