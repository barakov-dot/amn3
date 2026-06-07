# Controlled prod status visibility git-checkout smoke

Date: 2026-06-07.

Purpose: record the safe coordination update from neighboring AMN2 work after the `c8a6363` controlled-prod-ready decision. This file summarizes only non-secret evidence from AMN2 docs and git metadata.

## Current State

```text
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 branch: codex-vps-test-prep
current AMN2 git head: 42ffa65 Record git checkout smoke status
current app-code read-only smoke slice: 62ff184 Update controlled prod status visibility
VPS source overlay at git-checkout smoke time: c8a6363 Add Local Agent runtime summary mapper
controlled prod decision: controlled-prod-ready for source overlay c8a6363
```

Interpretation:

- At this git-checkout smoke time, `c8a6363` remained the source-overlay production baseline on `/opt/amn2`.
- `62ff184` passed a real VPS smoke on a git-managed checkout `/opt/amn2-git`.
- `42ffa65` records that smoke/status contract in AMN2.
- This evidence alone did not claim that `/opt/amn2` source overlay had been promoted to `62ff184` or `42ffa65`.

Later update: AMN3 package `42ffa65` passed source-overlay update/read-only smoke on `/opt/amn2`, `run_id=20260607T165625Z`; see `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`.

## Safe VPS Evidence

Source documents in AMN2:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
docs/API_VPS_SMOKE_EVIDENCE.ru.md
docs/AMN2_VPS_SMOKE_62FF184_RUNBOOK.ru.md
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
```

Recorded safe facts:

```text
workspace: /opt/amn2-git
branch: codex-vps-test-prep
target read-only gate head: 62ff184 Update controlled prod status visibility
api bind: http://127.0.0.1:3040
server name: local
smoke command: python -m app.cli api smoke-cycle
checked_routes: 6
status: passed
servers: 200
integration_status: 200
local_agent_runtime_summary: 200
server_summary: 200
metrics_summary: 200
users_summary: 200
forbidden_markers: none
smoke token status: revoked
smoke token revoke reason: smoke-complete
raw token display: hidden
decision: 62ff184 read-only git-checkout VPS smoke passed
source_overlay_promotion: not claimed by this evidence; later passed in separate source-overlay smoke
```

## Safety Boundary

Still blocked without a separate gate:

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

Recommended next step:

```text
Source-overlay promotion for 42ffa65 is now passed; continue controlled production launch checklist,
or continue another read-only controller/status/observability slice.
```

Do not jump directly to broad write API, config delivery, backup/import, Local Agent mutations, public API exposure, or new live peer operations.
