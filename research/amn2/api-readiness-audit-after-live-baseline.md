# `amn2`: API-readiness audit after verified live baseline

Дата: 2026-05-31.

Режим: AMN3 lab audit. Production-код `amn2` не менялся. Upstream code не копировался. Live VPS не трогался.

## Цель

Зафиксировать, насколько текущий `amn2` готов к следующему API / Local Agent / operations слою после verified live VPS baseline, и выбрать первый безопасный slice для отдельного future transfer в production repo.

## Проверенный baseline

`amn2`:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
head: 91aeb3e Document VPS verified tag
stable tag: vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
git status: clean
```

`VPS-OPS-LAB`:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
branch: master
status: ahead 2 from origin/master before this audit
head before audit: a0ccfef Expand secret inventory priority gate
```

Important correction from local git history: Local Agent first slice and production wiring are already contained in `codex-vps-test-prep` through merged PRs:

```text
62ae49e Merge pull request #2 from barakov-dot/codex/config-delivery-artifact-integrity-isolated
286b5cc Merge pull request #3 from barakov-dot/codex/local-agent-production-wiring
8697b60 Document Local Agent production wiring
ac2baa8 Add typed local agent auth errors
3119ee6 Add local Amnezia agent first slice
```

This means the next safe slice must not be "add Local Agent from zero". The baseline already includes the read-only agent foundation and opt-in production wiring.

Focused verification run from `amn2` with bundled Python and `.codex_deps`:

```text
tests/agent
tests/config/test_settings.py
tests/server/test_operation_runner.py
tests/server/test_checks.py
tests/web/test_cli_web.py

result: 109 passed, 1 expected StarletteDeprecationWarning
note: pytest emitted an ignored Windows temp cleanup PermissionError after the successful session; command exit code was 0.
```

## Verified live behavior as API contract

The live VPS baseline is now a behavior contract, not an open retest task:

- Telegram approve creates a working peer on Docker AmneziaWG runtime.
- Generated client config works.
- Web panel shows working server config immediately after approve.
- `Run peer sync` confirms live state.
- External peers created in Amnezia are preserved and shown separately.
- Missing local device can be added to AmneziaWG.
- Disable, enable and selective delete flows work.
- Docker runtime apply/revoke is live-verified.
- AmneziaWG 2.0 defaults/templates are known-good.

Any future slice that changes apply/revoke/config/sync, IP allocation, peer classification, disable/enable/delete or Docker reload/write behavior requires a new live retest. Slices that only add policy, tests, docs, fake adapters or read-only classifications do not.

## Current surfaces

### Web admin

Current strength:

- Session auth and CSRF protect admin state-changing routes.
- Server health run is a good read-only remote operation model: web admin session, CSRF, stored result and admin action.
- Config template preview is synthetic and avoids real device secrets.

Gaps before API expansion:

- Route policy is not centralized near route definitions.
- Login success/failure audit and rate limit are not yet a general API policy.
- Web admin is still a single configured actor, not a granular operator model.

### Telegram bot

Current strength:

- Admin flows use Telegram admin checks.
- User resend/revoke/reset checks ownership.
- Apply/revoke order is conservative: remote remove/apply happens before local state mutation in the verified flows.

Gaps before API expansion:

- Bot, web and future API actors are not expressed in one actor/risk matrix.
- Partial failure for multi-device reset still needs explicit recovery/resume policy before broader write APIs.

### Local Amnezia Agent

Current strength:

- Disabled by default through `LOCAL_AGENT_ENABLED=false`.
- Default bind is `127.0.0.1`.
- Raw token is not stored; token hash is `sha256:<digest>`.
- First-slice scopes are limited to `agent:health`, `agent:read`, `agent:protocols:read`.
- Exposed routes are only:
  - `GET /agent/health`
  - `GET /agent/version`
  - `GET /agent/runtime`
  - `GET /agent/protocols`
- Public docs/openapi are disabled for the agent app.
- Future secret/write/destructive routes exist only as policy records and are not exposed.
- Tests prove insufficient scopes are rejected and first-slice responses do not contain secret markers.

Gaps before expansion:

- Audit sink is first-slice/test-oriented, not yet unified with production admin action audit.
- Runtime detection is read-only but still local command execution; future adapters need the same command/risk contract discipline as remote operations.
- Client list, config delivery, backup/import and write routes remain blocked until policy and secret gates are stronger.

### Remote operations

Current strength:

- Read-only command allowlist exists.
- `RemoteOperationRunner` supports planning and applying `read-only-remote` operations only.
- Mutating commands are blocked before SSH.
- Secret-like operation inputs are rejected by validation.
- Docker live peer apply/revoke is verified in existing app flows, but not generalized as a runner write contract.

Gaps before expansion:

- State-changing remote operations are not yet safe as generic API operations.
- Host key enrollment/pinning is not in place.
- Sudo/privilege policy is not centralized.
- Partial failure and idempotency model for remote-state-write operations needs explicit contract.
- Traffic telemetry should share the read-only command policy or define an equivalent allowlist.

### Config delivery and secrets

Current strength:

- Config delivery is centralized through `build_device_config_delivery()`.
- Peer private key and PSK are encrypted in DB and decrypted only for runtime delivery/apply.
- Email recovery tokens are hash-only, one-time and TTL-controlled.
- `.conf`, QR and `vpn://` are now classified as `client-config-secret`.

Gaps before expansion:

- New self-service or API config endpoints need explicit route policy, ownership/token gate, audit and rate-limit decisions.
- `vpn://` must stay treated as secret-bearing, not metadata.
- Redaction coverage should be expanded before new token/config/API outputs.

## Actor and risk map

| Actor | Current trust channel | Safe first capability | Blocked for first slice |
| --- | --- | --- | --- |
| Web admin | session + CSRF | read current policy matrix, existing health flow | new broad API token, destructive ops |
| Telegram admin | Telegram identity + admin flag | existing approve/resend/admin flows as inventory | generic remote write API |
| Telegram user | Telegram identity + ownership checks | existing owned config resend/revoke/reset as inventory | cross-user reads, public config API |
| Public email token user | raw token + email, stored hash | existing verify/recover flow as inventory | reusable share links without rate/audit policy |
| Local Agent controller | hash-only bearer token + scopes | health/version/runtime/protocols read-only | clients/configs/backup/reboot |
| CLI operator | local shell | dry-run/read-only checks, hash-token helper | secret-bearing args, destructive operations |
| Future API client | not implemented | no direct production access yet | admin-equivalent bearer token |

## Candidate slices reviewed

### Candidate A: Route/Auth/Operation Policy Matrix for current surfaces

Summary: add a machine-checkable policy layer and tests that classify existing web, bot, Local Agent and remote operation surfaces by actor, auth method, risk class, secret class, audit requirement, idempotency/dry-run/rollback needs and live-retest trigger.

Risk: low. This can be implemented without touching live VPS behavior and without adding new API routes.

Value: high. It makes future API work harder to accidentally widen: every new route/operation must first state its actor, scope, secret behavior and tests.

Verdict: recommended first safe slice.

### Candidate B: Local Agent read-only clients list

Summary: expose `GET /agent/clients` with no secrets.

Risk: medium. Even without configs, client names, allowed IPs, endpoints and handshakes are privacy-sensitive metadata. It also couples controller behavior to runtime adapter semantics.

Verdict: defer until policy matrix and metrics/privacy classes exist.

### Candidate C: Config delivery API/self-service endpoint

Summary: expose download/share/recover config via API.

Risk: high. `.conf`, QR and `vpn://` are `secret-read` outputs. Requires ownership, token lifecycle, rate limit, audit, no-secret logs and revoke story.

Verdict: defer.

### Candidate D: Generic write client lifecycle API

Summary: create/disable/enable/delete clients through API or Local Agent.

Risk: high. Changes remote/local state and can require live retest. Needs idempotency, partial failure, audit, rollback/recovery and runtime adapter contract.

Verdict: defer.

### Candidate E: Backup/import/reboot API

Summary: expose operational endpoints inspired by upstream API projects.

Risk: unacceptable for first slice. Backup is secret-bearing and import/reboot are destructive.

Verdict: blocked until separate dangerous-operation design.

## Decision

First safe API / Local Agent / operations slice:

```text
Route/Auth/Operation Policy Matrix for current `amn2` surfaces
```

This slice should be transferred to `amn2` only after a separate implementation plan. It should not add new production API behavior. It should make current and future behavior explicit.

Proposed production scope:

- Add a small policy registry for current surfaces:
  - Local Agent first-slice routes.
  - Web admin config-delivery and server-health routes.
  - Public email verify/recover token routes.
  - Telegram admin/user config and revoke/reset flows as named logical surfaces.
  - Remote operation classes, starting with read-only server health.
- Add tests that every registry entry has:
  - actor;
  - auth method;
  - risk class;
  - secret class;
  - side effects;
  - audit requirement;
  - idempotency/dry-run/apply note;
  - rollback/recovery note;
  - live-retest trigger.
- Add negative tests for blocked first-slice categories:
  - `agent:clients:write`;
  - `agent:configs:read`;
  - backup/import/reboot;
  - generic remote-state-write.
- Document that policy records are a transfer gate, not a replacement for runtime guards.

Why this is first:

- It respects the verified live baseline and avoids changing working VPS behavior.
- It uses Local Agent readiness without expanding Local Agent privileges.
- It prepares scoped API tokens, self-service config delivery, telemetry and write operations without implementing them prematurely.
- It gives future implementation plans a stable review artifact.

## Required boundaries for next plan

The next implementation plan for `amn2` should preserve:

- no live VPS calls;
- no new public endpoint;
- no new secret-readable response;
- no write operation;
- no copied upstream code;
- tests first;
- AMN3 return note with branch, commits and verification evidence.

## Not selected now

- No production API CRUD.
- No client config API.
- No QR/`vpn://` delivery endpoint.
- No Local Agent client list.
- No state-changing Local Agent adapter.
- No generic remote-state-write runner.
- No backup/import/reboot.
- No 2FA restart while it is paused.

## Next artifact

After review of this audit, write an implementation plan for:

```text
docs/superpowers/plans/YYYY-MM-DD-amn2-route-auth-operation-policy-matrix.md
```

The plan should target `C:\Users\SooL\Documents\Amneziya`, but code changes should wait until that plan is explicitly accepted.
