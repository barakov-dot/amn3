# Controlled prod status visibility VPS package

Date: 2026-06-07.

Purpose: record the AMN3 package prepared for promoting the current AMN2 read-only status line from git-checkout smoke evidence to `/opt/amn2` source-overlay smoke evidence.

## Package

```text
AMN2 branch: codex-vps-test-prep
AMN2 package/source commit: 42ffa65 Record git checkout smoke status
app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
previous VPS source overlay: c8a6363 Add Local Agent runtime summary mapper
package status: package-ready-not-vps-smoked
```

Artifacts:

```text
dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source zip: dist/amn2-codex-vps-test-prep-42ffa65-source.zip
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
operator doc: dist/amn2-vps-update-and-smoke-kit-42ffa65/AMN2_VPS_UPDATE_AND_SMOKE_42ffa65.ru.md
```

## Validation

Local package validation:

```text
AMN2 current git head: 42ffa65 Record git checkout smoke status
smoke route inventory: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
expected checked_routes after source overlay update: 6
package SHA: matched sha256 file
source SHA: matched sha256 file
kit source SHA: matched sha256 file
package entries: 5
source entries: 297
forbidden source entries: none
required source entries: present
text hygiene: no BOM, no CRLF in kit scripts/doc
test extraction: passed
```

Focused AMN2 status contract check before package build:

```text
tests/api/test_api_integration_status.py
tests/services/test_integration_status_service.py
tests/web/test_web_integration_status.py
result: 8 passed
warnings: StarletteDeprecationWarning and pytest cache warning only
```

## Safety Boundary

This package does not authorize:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links, or full logs.

## Next Gate

Operator-only next step:

```text
Download/update with dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
Run source overlay update on /opt/amn2 with VPS_APPLY_ENABLED=false
Run read-only API loopback smoke
Return only safe summary evidence
```

Until that pass is returned, the current VPS-smoked source overlay remains `c8a6363`.
