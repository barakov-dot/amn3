# AMN2 Phase 1 Closeout

Date: 2026-06-04.

## Decision

Phase 1 read-only/API/web-panel baseline is closed on `amn2/codex-vps-test-prep` at:

```text
7764ae7 Cover integration status in API smoke
```

This is a small follow-up to `55a7ed6 Add post dry-run integration status`.

## What changed after 55a7ed6

- `api smoke-check` now includes `GET /api/integration/status`.
- The integration-status payload no longer reports the pre-integration `708c98e` stable head as the read-only API baseline; it reports `55a7ed6` as the Phase 1 read-only integration baseline.
- `remote_operation_gate.stable_merge_head` remains `708c98e`, because that is the dry-run-only remote-operation merge point.

No live VPS write behavior was added. No `/api/clients`, API `config:read`, public/self-service config delivery, Local Agent mutation, SSH write, Docker write, peer apply/revoke, backup/import/reboot route, config artifact, QR payload or `vpn://` output was added.

## Local Verification

Focused verification:

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py tests/api/test_cli_tokens.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q
result: 39 passed, 1 StarletteDeprecationWarning
```

Full verification:

```text
python -m pytest -q -p no:cacheprovider --basetemp tmp/pytest-post-dry-run-smoke-route
result: 610 passed, 1 StarletteDeprecationWarning
```

`git diff --check` passed.

## Published AMN3 Package

Source package:

```text
dist/amn2-codex-vps-test-prep-7764ae7-source.zip
sha256: 94D110BB9AA17C65E02C1780380BA77E49A4F0ADDDECEA7DE267FFC9F353B42B
```

Operator update+smoke kit:

```text
dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
```

Kit contents:

```text
AMN2_VPS_UPDATE_AND_SMOKE_7764ae7.ru.md
amn2-codex-vps-test-prep-7764ae7-source.zip
amn2-codex-vps-test-prep-7764ae7-source.zip.sha256.txt
amn2_api_loopback_smoke.sh
amn2_apply_source_zip.sh
```

Package verification:

```text
source_sha_match: True
kit_sha_match: True
source_entries: 292
forbidden_entries: 0
has_integration_status_service: True
smoke_has_integration_route: True
status_head_55a7ed6: True
```

## Next Gate

Phase 2 must start in a new chat/gate. It needs separate operator confirmation, a dedicated disposable test peer and rollback checklist before any live `apply-peer --apply` or `revoke-peer --apply`.
