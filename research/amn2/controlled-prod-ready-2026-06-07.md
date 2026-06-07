# Controlled prod ready

Дата: 2026-06-07.

Назначение: зафиксировать operator-only решение `controlled-prod-ready` для текущего `amn2/codex-vps-test-prep` baseline после read-only VPS smoke, reverse proxy confirmation and recovery path check.

## Decision

```text
decision: controlled-prod-ready
target mode: operator-only controlled prod
source overlay commit at decision time: c8a6363
VPS-smoked runtime/source at decision time: c8a6363 Add Local Agent runtime summary mapper
read-only VPS smoke run_id: 20260606T202040Z
web/admin access path: approved-reverse-proxy over HTTPS
public API 3040 exposed: no
VPS_APPLY_ENABLED shell: false
VPS_APPLY_ENABLED .env: false
recovery path known: yes
next action: continue with read-only next slice
```

This is not public SaaS readiness and not broad write/API/config/backup/agent enablement.

## Later Source Overlay Promotion

After this operator-only decision was recorded for `c8a6363`, AMN2 advanced to `42ffa65 Record git checkout smoke status`. AMN3 package `42ffa65` passed safe source-overlay update and read-only API smoke on `/opt/amn2`. A later controlled production safety follow-up `c92bd1a Bind web admin systemd to loopback` also passed source-overlay update and read-only API smoke on `/opt/amn2`.

```text
current source overlay after later promotion: c92bd1a
previous source overlay: 42ffa65
historical prior source overlay: c8a6363
current_source_update_run_id: 20260607T182118Z
current_api_smoke_run_id: 20260607T182131Z
current evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
prior source overlay: 42ffa65
source_update_run_id: 20260607T165559Z
api_smoke_run_id: 20260607T165625Z
checked_routes: 6
listener: 127.0.0.1:3040 loopback-only
VPS_APPLY_ENABLED: false
evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
```

These later promotions preserve the same controlled-prod boundary: no public API `3040`, no direct public web/admin `3030`, no write routes, no config delivery, no Local Agent mutations and no backup/import/reboot routes.

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
- `c8a6363` kit and checksum were present at the recovery check time;
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
current AMN2 git head: c92bd1a Bind web admin systemd to loopback
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
git-checkout VPS smoke: passed on /opt/amn2-git, checked_routes=6
source-overlay package: dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
source-overlay package status: read-only-vps-smoke-pass
source overlay promotion: passed; /opt/amn2 is now c92bd1a
previous source-overlay package: dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
previous source overlay promotion: passed; /opt/amn2 was promoted to 42ffa65 before c92bd1a
```

Recommended next direction:

```text
complete controlled production launch checklist for operator-only web/admin and bot runtime,
operator documentation cleanup,
or another read-only status/observability slice
```

Do not jump directly to config delivery, public API writes, backup/import, Local Agent mutations or new live peer operations.
