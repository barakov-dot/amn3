# Phase 4 P4-I003 Read-only API Status Design 2026-06-09

Date: 2026-06-09.

Status: `candidate-specific-design-prepared`.

Candidate:

```text
candidate_id: P4-I003
priority: important
registry_row: research/amn2/phase-4-candidate-registry-2026-06-09.md
gate_plan: research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md
```

Purpose: define the next safe AMN2 local-only implementation slice for read-only API/status schema maturity. This design does not authorize new routes, public API exposure, config delivery, write CRUD, Local Agent mutations, live VPS commands, backup/import/reboot, token issue/revoke, or production peer/user mutation.

## Current AMN2 Baseline

Observed local AMN2 baseline from `worktrees/amn2-p4-i002`:

- FastAPI API app exists in `app/api/app.py`.
- Connected read-only routes:
  - `GET /api/servers` with `server:read`;
  - `GET /api/servers/{server_name}/summary` with `server:read`;
  - `GET /api/integration/status` with `server:read`;
  - `GET /api/local-agent/runtime/summary` with `server:read`;
  - `GET /api/metrics/summary` with `metrics:read`;
  - `GET /api/users/summary` with `metrics:read`.
- `python -m app.cli api smoke-cycle` expects `checked_routes=6`.
- Successful reads record `api_read` audit metadata with method, path, scope, token id/name and owner label.
- `/api/integration/status` already reports the Phase 3 service-mode boundary:
  - web/bot service-mode active;
  - web/admin loopback-only on `127.0.0.1:3030`;
  - operator access is SSH tunnel only;
  - public API `3040` absent/closed;
  - TCP `80/443` absent;
  - no domain/HTTPS cutover;
  - `VPS_APPLY_ENABLED=false`.

## Candidate-specific Proposal

```text
candidate_id: P4-I003
route_or_surface: existing read-only API/status routes and schema contract
actor: operator or controller using scoped bearer token over private loopback/tunnel context
auth_method: bearer token backed by hash-only api_tokens storage
required_scope: server:read for server/status routes; metrics:read for aggregate metrics/users routes
risk_class: read-only aggregate API
secret_surface: aggregate metadata only; no config, token, key, endpoint, peer public key, SSH host/port, Local Agent host/port, QR or vpn:// payload
remote_write_surface: none
public_exposure: none; public API 3040 remains absent/closed by Phase 4 default mode
audit_event: api_read with safe route template, scope, token id/name, owner label, status and aggregate_only=true
safe_metadata: route names, booleans, counts, local gate status, smoke route count, service-mode boundary labels
forbidden_outputs: Authorization header, raw token, token hash, .env, servers.yml, peer public key, private key, PSK, endpoint host, ssh_port, Local Agent token/host/port, .conf, QR, vpn://, full logs, response body in audit
local_tests: schema keys, scope split, forbidden marker scan, safe audit metadata, checked_routes=6, no new runtime routes
fake_runner_tests: not required because this slice performs no remote write or fake remote operation
vps_gate_required: no for local schema/docs/tests; required only if a future change samples fresh live runtime telemetry
rollback_or_recovery: revert local AMN2 schema/docs/tests commit; no server rollback because no live runtime change
operator_confirmation: not required for local-only implementation; required before any live/public/write/config change
blocked_until: write/config/public/live candidates remain blocked until their own named gates
```

## Recommended AMN2 Local-only Slice

Name:

```text
P4-I003 read-only API status schema maturity
```

Goal: turn the existing read-only API route shell into a more explicit contract without expanding the route surface.

Allowed changes:

- Add or update AMN2 docs for the stable read-only API/status response contract.
- Add local tests that lock the six-route read-only API matrix and `checked_routes=6`.
- Add local tests that `/api/integration/status` keeps service-mode boundary fields and blocked-lane labels visible.
- Add local tests proving scope separation: `server:read` cannot access metrics/users routes and `metrics:read` cannot access server/status routes.
- Add local tests proving safe audit metadata excludes raw token material, Authorization headers, token hashes and response bodies.
- Add local forbidden-marker tests for serialized responses.

Explicitly blocked in the implementation slice:

- adding `/api/clients`;
- adding `config:read`;
- adding public/self-service config delivery;
- adding Local Agent `/configs` or mutation routes;
- changing `api_smoke` to call new live endpoints;
- opening public API `3040`;
- issuing/revoking real operator tokens outside local tests;
- reading or printing `.env`, `servers.yml`, raw tokens, hashes, keys, configs, QR or `vpn://`;
- running live VPS commands.

## Acceptance Criteria

A future AMN2 implementation branch can be accepted as local-only when:

- no new runtime route is mounted;
- route/auth policy still lists exactly the existing six read-only `/api/*` routes for this slice;
- all current read-only routes have expected scopes and safe response shapes;
- `/api/integration/status` continues to expose service-mode boundary fields without secret-bearing values;
- audit assertions prove no raw token, Authorization header, token hash or response body is stored;
- forbidden-marker scans cover the API response payloads used by tests;
- focused AMN2 API/security/status tests pass locally;
- `git diff --check` passes;
- AMN3 evidence states that no live VPS command, public exposure, config delivery, write CRUD, token lifecycle action, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed.

## Non-permissions

This design does not authorize:

- live VPS commands;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- config delivery, `.conf`, QR or `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations or config output;
- backup/import/reboot;
- production peer/user mutation;
- copying PRVTPRO/KYORESUAS code.

## Recommendation

Proceed next with an AMN2 local implementation plan for `P4-I003 read-only API status schema maturity`.

Do not implement write/config/public routes from this design. The next AMN2 slice should be limited to schema/docs/tests and safe wording around the existing read-only API/status surface.
