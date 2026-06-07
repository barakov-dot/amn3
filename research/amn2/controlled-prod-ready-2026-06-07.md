# Controlled prod ready

Дата: 2026-06-07.

Назначение: зафиксировать operator-only решение `controlled-prod-ready` для текущего `amn2/codex-vps-test-prep` baseline после read-only VPS smoke, reverse proxy confirmation and recovery path check.

## Decision

```text
decision: controlled-prod-ready
target mode: operator-only controlled prod
source overlay commit: c8a6363
current VPS-smoked runtime/source: c8a6363 Add Local Agent runtime summary mapper
read-only VPS smoke run_id: 20260606T202040Z
web/admin access path: approved-reverse-proxy over HTTPS
public API 3040 exposed: no
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
recovery path known: yes
next action: continue with read-only next slice
```

This is not public SaaS readiness and not broad write/API/config/backup/agent enablement.

## Evidence Already Recorded

Read-only VPS smoke:

```text
research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
VPS verdict: pass
run_id: 20260606T202040Z
checked_routes: 5
auth_status: passed
listener_status: passed
audit_status: passed
forbidden_markers: none
```

Reverse proxy confirmation:

```text
research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md
web/admin access path: approved-reverse-proxy
transport: HTTPS
public API 3040 exposed: no
```

Operator safety confirmations:

```text
source overlay commit: c8a6363
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
web listener: 127.0.0.1:3030
login_http: 200
```

## Recovery Evidence

Returned safe evidence:

```text
kits:
/root/amn2-vps-update-and-smoke-kit-32d01fd.zip
/root/amn2-vps-update-and-smoke-kit-c8a6363.zip

sha files:
/root/amn2-vps-update-and-smoke-kit-32d01fd.zip.sha256.txt
/root/amn2-vps-update-and-smoke-kit-c8a6363.zip.sha256.txt

current source:
c8a6363

preserved runtime:
data_dir=present
env_file=present
servers_yml=present

recovery dirs:
32d01fd_dir=present
c8a6363_dir=present
```

Interpretation:

- rollback/update artifacts for previous `32d01fd` baseline are present;
- current `c8a6363` kit and checksum are present;
- runtime state directories/files that must be preserved by the overlay flow are present;
- no rollback command was run during this check.

## Still Blocked

The `controlled-prod-ready` decision does not allow:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply`;
- live `revoke-peer --apply`;
- public API exposure on `3040`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads or `vpn://` links.

## Next Work Boundary

Allowed next work should stay read-only unless a separate gate is opened.

Post-decision AMN2 update:

```text
current AMN2 git head: 42ffa65 Record git checkout smoke status
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
git-checkout VPS smoke: passed on /opt/amn2-git, checked_routes=6
prepared source-overlay package: dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
prepared package status: package-ready-not-vps-smoked
source overlay promotion: not claimed; /opt/amn2 remains c8a6363 until separate update/smoke
```

Recommended next direction:

```text
read-only controlled-prod status/recovery visibility,
operator documentation cleanup,
or another read-only status/observability slice
```

Do not jump directly to config delivery, public API writes, backup/import, Local Agent mutations or new live peer operations.
