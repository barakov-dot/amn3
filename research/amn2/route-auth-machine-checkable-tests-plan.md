# Route/Auth Machine-checkable Tests Plan

Дата: 2026-06-01.

Назначение: зафиксировать next-gate plan для превращения текущего `amn2` route/auth/operation policy registry в drift-resistant machine-checkable coverage. Цель - чтобы новые web routes, bot actions, public-token flows, Local Agent routes, CLI commands и remote operations не появлялись без policy entry, risk class, gates and tests.

Этот документ не является implementation plan для новых endpoints. Он не меняет `amn2`, не добавляет routes, не включает API `config:read`, не меняет web/bot/agent behavior, не читает `.env`, не требует live VPS и не переносит upstream code.

## Current production baseline

В `amn2` уже есть первый machine-checkable slice:

```text
app/security/surface_policy.py
tests/security/test_surface_policy.py
docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
```

Текущий registry:

- описывает web, public-token, bot, local-agent, cli and remote-operation surfaces;
- содержит `policy_id`, `surface`, `method`, `path`, `actor`, `auth_method`, `risk_class`, `secret_class`, `gates`, `audit_required`, `operation_contract`, `live_retest_required`, `implementation_mode` and `test_refs`;
- не включает new behavior (`enables_new_behavior=False`);
- проверяется aggregate tests на uniqueness, required policy ids, secret/public-token gates, web CSRF, remote operation contract and live retest markers;
- синхронизирован с `app.agent.policy` для Local Agent first slice and blocked-future routes.

Это хороший первый gate, но он пока inventory-first. Следующий слой должен ловить drift между реальными routes/actions/commands and policy registry.

## Decision status

Status: `implemented-pushed-local-gate-complete`.

Decision: route/auth work remains a local-only drift-check layer, not route expansion. The first implementation adds binding/coverage tests around current surfaces while preserving `enables_new_behavior=False`.

Implementation evidence:

```text
repo: barakov-dot/amn2
branch: codex/route-auth-binding-tests
commit: f9d2c79 Bind route inventory to surface policies
new files:
- app/security/surface_bindings.py
- tests/security/test_surface_policy_bindings.py
policy drift fixed:
- web.email.verify_start
- web.servers.amnezia_peers.unmark
stale test_ref fixed:
- tests/server/test_peer_sync.py -> tests/services/test_peer_inventory.py
```

Verification:

```text
RED: tests/security/test_surface_policy_bindings.py -> 1 import error as expected
tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -v -> 22 passed
focused web/email/agent/server/peer inventory suite -> 89 passed, 1 warning
full local suite -> 549 passed, 1 warning
```

The known Windows `pytest-current` cleanup `PermissionError` was emitted after successful pytest sessions; commands returned exit code 0.

## Problem

Current aggregate tests prove that important policy entries exist, but they do not yet prove every runtime surface is covered.

Examples of remaining drift risks:

- a new FastAPI web route is added without policy entry;
- a new public-token path appears without TTL/one-time/generic denial policy;
- a new bot callback/action sends config or changes state without `secret-read`/`state-write` policy;
- Local Agent adds `/agent/clients` or `/agent/configs` behavior but policy still says blocked-future;
- a CLI command gains remote mutation behavior without `remote-exec` policy and live retest marker;
- `test_refs` point to stale files;
- a policy says `audit_required=true`, but no focused test names the audit behavior;
- a route serves `client-config-secret` through a read-only-looking path.

## Goals

The next-gate tests must:

- keep policy registry inventory-only;
- discover or declare current runtime surfaces;
- compare runtime surfaces with `SURFACE_POLICIES`;
- keep blocked-future routes explicitly blocked;
- require every `secret-read` and `public-token-secret-read` policy to have safe audit/redaction gates;
- require every web POST policy to include CSRF gate;
- require every remote-exec policy to include operation contract and live retest marker;
- require future API/config/backup/import surfaces to be either absent or explicitly blocked;
- fail loudly when a new surface appears without policy.

## Non-goals

Do not include:

- new `/api/*` routes;
- public/self-service config download route;
- `config:read` scope;
- Local Agent `/clients` or `/configs` implementation;
- backup/import web/API routes;
- route middleware enforcement;
- live VPS calls;
- broad refactor of `app/web/app.py` or bot handlers.

## Proposed approach

Use a conservative two-layer model.

Layer 1: `surface_policy.py` remains the human-readable registry and risk taxonomy.

Layer 2: a small machine-checkable binding layer maps current runtime surfaces to policy ids. It can be introduced as tests first and, if useful, as an inventory-only module:

```text
app/security/surface_bindings.py
tests/security/test_surface_policy_bindings.py
```

The binding layer should not alter route handlers. It only gives tests a stable list of surfaces that must have matching policies.

## Binding sources

| Surface | Binding source | First safe method |
| --- | --- | --- |
| Web routes | FastAPI app route table or explicit route manifest | compare method/path to policy ids |
| Public-token routes | subset of web routes with public-token actor | ensure purpose/TTL/one-time/generic denial policy |
| Bot actions | explicit logical action manifest | map callback/command names to policy ids |
| Local Agent | `app.agent.policy.AGENT_ROUTE_POLICIES` | already partially covered; keep parity tests |
| CLI commands | explicit command manifest | map command/risk to policy ids |
| Remote operations | `app.server.operations`/operation runner contracts | verify risk class and live retest marker |
| Future blocked surfaces | explicit blocked-future policies | assert behavior routes are absent |

## Stage 1: Web route drift tests

Target: current web routes must be covered by policy or listed as safe exemptions.

Test expectations:

- every non-static FastAPI route has method/path entry in `SURFACE_POLICIES` or an explicit exemption;
- every web `POST` policy includes `csrf`;
- every web route with email recovery/config send maps to public-token or secret-read policy as appropriate;
- every route with `secret-read` has `audit_required=true`;
- no public/self-service config download route exists unless policy and tests are added first.

Suggested exemptions:

- static files if present;
- framework docs routes if disabled/not mounted in production;
- health/internal routes only if they are documented.

First implementation should prefer a route manifest if direct FastAPI route extraction is noisy. The point is drift detection, not clever introspection.

## Stage 2: Public-token gate tests

Target: public-token surfaces remain purpose-bound and do not become broad config access.

Test expectations:

- every `public-token-*` policy has `no raw token`;
- `public-token-secret-read` has `purpose`, `ttl`, `one-time`, `generic denial`, `redaction`, `audit_required=true`;
- public config share policies from `public-self-service-config-delivery-policy.md` are either absent from runtime or explicitly blocked;
- no public route returns `.conf`, QR payload/PNG or `vpn://` until share-token contract exists.

This stage uses the existing public email verify/recover baseline and the new public/self-service policy artifact as blockers.

## Stage 3: Bot action coverage

Target: logical bot actions that read secrets or mutate state must have policy ids.

Test expectations:

- admin approve, admin resend config, user resend config, user revoke, user reset and admin grant/create flows map to policies;
- user-owned bot flows include ownership gate;
- config-send actions are `secret-read`, audit-required and no raw config/link in logs/audit;
- remote mutation actions are `remote-exec` when `VPS_APPLY_ENABLED=true`;
- blocked/future bot actions are represented before implementation.

Because bot actions are not HTTP routes, use an explicit manifest:

```text
BotSurfaceBinding(policy_id, command_or_callback, handler_name, risk_class)
```

## Stage 4: Local Agent parity and blocked-future tests

Target: Local Agent route policy remains the source of truth for first-slice vs future routes.

Test expectations:

- first-slice Local Agent routes in `app.agent.policy.first_slice_policies()` match surface policies;
- future Local Agent routes in `AGENT_ROUTE_POLICIES` are present as `blocked-future`;
- `/agent/clients`, `/agent/configs` and write lifecycle remain blocked until separate policy gates are implemented;
- `agent:*` scopes do not imply external API scopes.

This extends existing parity tests rather than replacing them.

## Stage 5: CLI and remote operation binding

Target: remote read/write command surfaces stay attached to operation contracts.

Test expectations:

- `server check` live remains `remote-read`;
- `apply-peer --apply` and `revoke-peer --apply` remain `remote-exec`;
- remote-exec policies require `operation_contract` and `live_retest_required=true`;
- dry-run policies do not require live retest but must not execute live commands;
- any new command that can change VPS/Docker/firewall/config state fails without policy.

This stage is local-only and uses fake runner/metadata tests. It must not SSH.

## Stage 6: Test reference integrity

Target: policy entries point to real evidence.

Test expectations:

- every `test_refs` path exists;
- every policy with `audit_required=true` has at least one test ref in a focused test area;
- every `secret-read` policy references redaction or no-secret tests;
- every `remote-exec` policy references operation/fake runner tests or explicitly says future-gate;
- blocked-future policy may reference docs-only gates, but must not pretend runtime tests exist.

This prevents the registry from becoming ceremonial paperwork.

## Stage 7: Blocked surface assertions

Target: high-risk future surfaces stay blocked until their own gates land.

Assert absent or blocked:

- `/api/*` config routes;
- public/self-service config download;
- `config:read` bearer route;
- Local Agent `/agent/configs`;
- backup/import web/API routes;
- reboot/clear/install/uninstall routes;
- broad admin-equivalent bearer tokens.

If any of these appears, the test must require a dedicated policy artifact and implementation plan before passing.

## First safe implementation boundary

The first safe code slice in `amn2` should be:

```text
route/auth surface binding tests, no behavior change
```

It may include:

- `tests/security/test_surface_policy_bindings.py`;
- optional `app/security/surface_bindings.py` inventory-only manifests;
- web route coverage tests;
- Local Agent parity extensions;
- bot logical action binding manifest/tests;
- CLI/remote operation binding manifest/tests;
- test-ref existence checks.

It must not include:

- new routes;
- route middleware enforcement;
- public config download;
- scoped API route expansion;
- live VPS calls;
- behavior changes in web/bot/agent/CLI;
- upstream code copy.

## Verification commands for future implementation

Focused:

```powershell
python -m pytest tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -v
```

If touched areas require it:

```powershell
python -m pytest tests/web tests/bot tests/agent tests/server -q
```

Full local suite before push:

```powershell
python -m pytest -q
```

VPS gate is not required for this slice because it is policy/test-only and does not alter live apply/sync/config behavior.

## Exit criteria

The next-gate slice is ready when:

- policy registry and binding tests pass;
- current routes/actions/commands are either covered or explicitly exempted;
- blocked future surfaces remain blocked;
- no `enables_new_behavior=True` policy is introduced;
- production docs state that adding a route/action/command without policy coverage is a failing condition.

## Current recommendation

Use the implemented binding tests before any route expansion work. They should run before:

- route-connected scoped API token lifecycle;
- public/self-service config delivery implementation;
- Local Agent clients/configs expansion;
- backup/import web/API design implementation;
- read-only metrics/API route shell.

This keeps API-readiness work boring in the best way: every new surface must first show its actor, auth, risk, audit and tests.
