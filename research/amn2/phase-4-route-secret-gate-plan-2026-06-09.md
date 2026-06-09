# Phase 4 Route/Secret Gate Plan 2026-06-09

Date: 2026-06-09.

Status: `docs-only-gate-plan`.

Purpose: define the route/auth/secret gates that must be satisfied before AMN2 expands beyond current read-only private surfaces. This plan does not authorize new routes, public exposure, config delivery, live VPS commands, write CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation.

## Current Baseline

Accepted operational boundary:

- web/bot service-mode is active on the target VPS;
- web/admin is loopback-only on `127.0.0.1:3030`;
- operator access is SSH tunnel only;
- public/direct `3030` is closed;
- public API `3040` is absent/closed;
- TCP `80/443` are absent;
- no domain is planned and Caddy/HTTPS public cutover is deferred;
- `VPS_APPLY_ENABLED=false`;
- live peer scope remains the approved test peers only;
- no POST/write/config delivery/token issue-revoke/sync/backup/import/reboot action is authorized by Phase 4 default mode.

## Existing AMN2 Gate Baselines

These are prerequisites for any future route-expansion proposal, not automatic permission to ship routes:

| Baseline | AMN2 commit/branch | Status | Use before expansion |
| --- | --- | --- | --- |
| Route/auth binding tests | `f9d2c79` / `codex/route-auth-binding-tests` | local-gate-complete | every runtime route/action must have policy, auth, risk and audit binding |
| Secret inventory registry | `9ce42f4` / `codex/secret-inventory-registry` | local-gate-complete | every secret-bearing field/artifact must be classified before output or backup |
| Scoped API token lifecycle | `256d0c0` / `codex/api-token-lifecycle-gate-stacked` | local-gate-complete | scopes, expiry, revoke, owner labels and no raw token audit leakage |
| Public/self-service config delivery policy | `2ef3af7` / `codex/public-config-delivery-policy-contract` | local-gate-complete | config share policy exists, but public/self-service routes are still closed |
| Manager config export contract | `4d4e7a4` / `codex/manager-config-export-contract` | local-gate-complete | typed export/safe metadata baseline for future config read surfaces |
| Backup/import policy contract | `afb2702` / `codex/backup-import-policy-contract` | local-gate-complete | preview/manifest policy exists, but apply/import routes are still closed |
| Service-mode status boundary | `83f6d28` / `codex/phase-4-service-mode-status-wording` | local-gate-complete | private panel now states loopback-only, tunnel-only, no public/write/config |

## Route Classes

### Read-only Aggregate API

Examples:

- `GET /api/servers`
- `GET /api/metrics`
- `GET /api/integration/status`

Default gate:

```text
local-only unless a new live telemetry source is introduced
```

Required before implementation:

- route/auth policy entry;
- explicit read scope such as `server:read` or `metrics:read`;
- aggregate-only response contract;
- no peer names, client IPs, endpoint values, raw tokens, configs, QR or `vpn://`;
- audit metadata that does not include Authorization headers or raw token material;
- local route binding/drift tests.

### Read-only Operational Status

Examples:

- private web/admin status pages;
- safe service-mode boundary panels;
- API readiness summaries.

Default gate:

```text
local-only for static/safe local status; requires VPS gate for fresh live runtime sampling
```

Required before implementation:

- source evidence reference;
- safe field list;
- no `.env`, `servers.yml`, secrets, peer public keys, full logs or endpoint values;
- tests proving no forbidden markers in rendered output.

### Write Peer/User Lifecycle

Examples:

- `/api/clients` create/update/delete;
- web/API enable/disable/delete user/device flows that apply or revoke remote peers;
- sync/backfill that mutates local DB or live AmneziaWG state.

Default gate:

```text
blocked until separate write/config/public gate
```

Required before implementation:

- route/auth policy and operation policy;
- scoped write tokens distinct from read-only tokens;
- ownership/admin decision;
- idempotency and lock strategy;
- partial-failure contract;
- fake-runner tests for apply/revoke/sync paths;
- audit entries with redacted metadata;
- rollback/recovery note;
- named single-test-peer VPS gate before broad lifecycle;
- explicit proof that `VPS_APPLY_ENABLED=false` is preserved outside the gate.

### Secret-read Config Delivery

Examples:

- API `config:read`;
- web/admin `.conf`, QR or `vpn://` retrieval;
- Local Agent `/configs`;
- generated config archive or share link.

Default gate:

```text
blocked until separate write/config/public gate
```

Required before implementation:

- secret inventory classification for every output field;
- route/auth policy with a dedicated `config:read` or narrower scope;
- ownership and expiry/revoke model;
- one-time or short-lived delivery decision;
- no config payload in logs, audit metadata, error bodies, backups or docs;
- `.conf` byte-level tests;
- QR payload tests;
- `vpn://` round-trip tests;
- Android/import compatibility check before production delivery;
- safe metadata contract for success/failure responses;
- explicit operator channel for any live secret-bearing artifact.

### Public/self-service Config Delivery

Examples:

- public download URL;
- self-service user download;
- public share token;
- email/SMS config delivery link.

Default gate:

```text
blocked until separate public/config gate
```

Required before implementation:

- all Secret-read Config Delivery requirements;
- hash-only share tokens;
- expiry, revoke and rate-limit behavior;
- generic denial errors;
- no raw token echo;
- public route threat model;
- browser/session ownership decision;
- audit without raw token/config data;
- abuse/guessability tests;
- explicit public exposure approval.

### Local Agent Mutation Or Configs

Examples:

- Local Agent `/clients`;
- Local Agent `/configs`;
- controller-to-agent peer apply/revoke;
- agent-backed config delivery.

Default gate:

```text
requires VPS gate for deployment or controller-to-agent calls; blocked for mutation/config output until write/config gate
```

Required before implementation:

- agent token separation from web/API tokens;
- route/auth policy parity with controller routes;
- secret inventory classification;
- no raw bearer token in audit;
- deployment runbook and rollback;
- fake agent tests before live agent deployment;
- named VPS gate before any real service exposure.

### Backup/import/reboot Dangerous Operations

Examples:

- full backup download;
- restore/import apply;
- reboot;
- service restart;
- raw server config save/apply.

Default gate:

```text
blocked until separate dangerous-operation gate
```

Required before implementation:

- backup/import policy mode (`redacted`, `encrypted-full`, `preview-only`, `apply`);
- explicit confirmation UX/API field;
- backup-before-write evidence;
- manifest secret policy;
- dry-run preview before apply;
- rollback/recovery note;
- destructive audit event;
- no raw secrets in logs/docs/errors;
- named VPS gate for any restore/import/reboot/service restart.

### Public Exposure/Cutover

Examples:

- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- public OpenAPI/docs/metrics.

Default gate:

```text
blocked until separate public gate
```

Required before implementation:

- domain/DNS proof;
- TLS/reverse-proxy plan;
- auth/session cookie review;
- firewall/listener proof;
- rollback plan;
- rate limiting decision;
- no public config delivery or write routes bundled into the cutover;
- `VPS_APPLY_ENABLED=false` proof before and after the gate.

## Mandatory Proposal Template

Every future route-expansion proposal must include:

```text
candidate_id:
route_or_surface:
actor:
auth_method:
required_scope:
risk_class:
secret_surface:
remote_write_surface:
public_exposure:
audit_event:
safe_metadata:
forbidden_outputs:
local_tests:
fake_runner_tests:
vps_gate_required:
rollback_or_recovery:
operator_confirmation:
blocked_until:
```

## Acceptance Checklist Before AMN2 Implementation

A future AMN2 route-expansion branch can start only when all applicable items are true:

- candidate is listed in the Phase 4 registry;
- gate class is explicit;
- route/auth policy entry is designed before code;
- secret inventory coverage exists before any secret-bearing output;
- API token scope exists and is narrower than admin-equivalent access;
- audit event has safe metadata and no raw token/config/secret payload;
- local tests are defined before production code;
- fake-runner coverage exists before any remote write;
- live VPS gate name exists before any live command;
- public exposure gate exists before opening any listener, proxy, domain or public docs;
- backup/import/reboot gate exists before dangerous operations;
- license boundary is explicit for PRVTPRO/KYORESUAS-derived ideas;
- AMN3 return evidence path is declared.

## Explicit Non-permissions

This plan does not authorize:

- live VPS commands;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/HTTPS/domain cutover;
- config delivery, `.conf`, QR or `vpn://`;
- `/api/clients` write CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- copying GPL/upstream code.

## Next Decision

Recommended next product decision:

1. Choose a specific future route-expansion candidate and write its design against this gate plan; or
2. run `P4-I001` second read-only UX pass if more private-panel page evidence is needed before selecting an API candidate.

Do not start AMN2 implementation for write/config/public routes until a candidate-specific design names the gate class and acceptance evidence.
