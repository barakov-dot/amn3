# Phase 6 P6-C005 production security review gate

Date: 2026-06-13.

Status: `security-review-gate-closed-local-docs`.

Scope: AMN3 docs/security review with focused AMN2 local code/test verification.

This is not an exhaustive repository-wide Codex Security scan, penetration test,
public launch approval or live deployment gate. It does not open public exposure,
config delivery, write API, backup/import/reboot, Local Agent mutations,
production peer/user mutation, destructive VPS action or Telegram identity
mutation.

## Decision

```text
task_id: P6-C005
decision: production-security-review-complete-for-planning
public_self_service_launch: no-go-until-separate-named-gates
current_mode: private/operator-only
AMN2_current_head: 2215761 Polish operator web admin UX
latest_VPS_smoked_head: 2215761
VPS_APPLY_ENABLED: false
live_vps_commands: no
ssh_commands: no
package_apply_rebuild_on_vps: no
service_restart_deploy: no
public_exposure_changed: no
config_delivery_performed: no
write_api_enabled: no
Local_Agent_mutation: no
backup_import_reboot: no
production_peer_user_mutation: no
destructive_provider_action: no
Telegram_token_use_or_identity_mutation: no
upstream_GPL_code_copy: no
```

P6-C005 closes the first Phase 6 security review gate as a local/docs/security
checkpoint. The review confirms that the risky Phase 6 branches have explicit
named-gate boundaries and local controls, but it does not approve public launch
or any live mutation by itself.

## Inputs Reviewed

AMN3 coordination and evidence inputs:

- `docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md`
- `docs/PHASE_5_6_FORWARD_PLAN.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/PROJECT_CONTEXT_IMPORT.ru.md`
- `research/amn2/transfer-backlog.md`
- `research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md`
- `research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md`
- `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`
- `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`
- `docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md`
- `docs/AMN2_READ_ONLY_SERVER_STATUS_LATENCY_UX_BOUNDARY.ru.md`

AMN2 local controls reviewed:

- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`
- `app/security/surface_policy.py`
- `app/security/surface_bindings.py`
- `app/api/app.py`
- `app/agent/api.py`
- `app/agent/policy.py`
- `app/services/api_tokens.py`
- `app/services/integration_status.py`
- `app/bot/delivery.py`
- `app/bot/handlers.py`
- `app/backup/*`
- focused tests under `tests/security`, `tests/services`, `tests/agent`,
  `tests/api`, `tests/bot` and `tests/backup`.

## Verification

Toolchain:

```text
C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe --version
Python 3.12.13

C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m app.toolchain check
AMN2 toolchain ok: CPython 3.12.x.
```

Focused security regression suite:

```text
PYTHONPATH=C:\Users\SooL\Documents\Amneziya\.codex_deps
python -m pytest \
  tests/security/test_surface_policy.py \
  tests/security/test_surface_policy_bindings.py \
  tests/security/test_redaction.py \
  tests/services/test_api_tokens.py \
  tests/agent/test_api.py \
  tests/agent/test_policy.py \
  tests/api/test_app.py \
  tests/api/test_api_integration_status.py \
  tests/bot/test_delivery.py \
  tests/backup/test_backup_service.py \
  -q --basetemp tmp\pytest-p6-c005-security

result: 98 passed, 1 warning
warning: StarletteDeprecationWarning from local fastapi/starlette TestClient dependency
```

The first attempt with the bundled Python failed because that runtime did not
have `pytest` installed. The successful run used the same CPython 3.12.13 plus
the repository-local `.codex_deps` path; no dependency install or network access
was performed.

## Surface Review

### Public exposure

Current accepted baseline remains private/operator-only:

- latest live smoke evidence for AMN2 `2215761` reports remote listener
  `127.0.0.1:3030` only, with `3040`, `80` and `443` absent;
- AMN2 settings default `API_HOST=127.0.0.1`;
- Phase 6 handoff keeps direct public web/admin `3030`, public API `3040`,
  Caddy/nginx/domain/HTTPS and firewall exposure behind `P6-C001`.

Verdict: public exposure remains blocked. `P6-C001` must include auth/session
hardening, rate limits, listener/firewall plan, monitoring/log redaction,
rollback and incident-response steps before any public cutover.

### Read-only API and scoped tokens

Current API surface is read-only and scope-limited:

- implemented routes are the six read-only API routes documented in
  `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`;
- first-slice scopes are `server:read` and `metrics:read`;
- `config:read`, write scopes and destructive scopes are rejected in tests;
- raw API tokens are issued once, hashes are stored, expiry/revoke/last-use are
  tracked, and API read audit metadata excludes raw token/hash material;
- API smoke/redaction tests assert secret markers such as `PrivateKey`,
  `PresharedKey`, `vpn://` and `token_hash` are absent from safe responses.

Verdict: current read-only API controls are adequate for private/operator-only
planning. Production token implementation remains active as `P6-I001`.

### Web/admin state changes

AMN2 has historical operator web routes for user/server/device actions, including
remote-exec paths that were verified in earlier live gates. P5-O002 disabled
operator-only visible create/token/template write affordances in sampled web UI.
The machine-readable `SurfacePolicy` inventory still classifies the underlying
POST routes by risk class, side effects, audit and live retest requirement.

Verdict: no broad write API or production mutation is approved. Any behavior
change touching peer apply/revoke, config templates/defaults, IP allocation,
peer sync classification, disable/enable/delete or Docker runtime write/restart
still requires local tests and a separate live gate.

### Config delivery

Config artifacts remain `client-config-secret`:

- `.conf`, QR payload/PNG and `vpn://` are treated as secret-bearing;
- `vpn://` is recognized as reversible full config encoding;
- Telegram copy affordance exists only when the exact import link fits the Bot
  API copy-text limit;
- short public links, web download pages, Telegram Web App clipboard flows and
  self-service config delivery remain separate config/public gates.

Verdict: config delivery remains blocked except for already accepted private
operator/bot behavior. Public/self-service delivery must go through `P6-C002`.

### Local Agent

Current Local Agent implementation remains first-slice/read-only:

- FastAPI docs, redoc and OpenAPI are disabled for the agent app;
- mounted routes are `/agent/health`, `/agent/version`, `/agent/runtime` and
  `/agent/protocols`;
- `/agent/version` returns `write_enabled=false`;
- clients/configs/backup/restore/reboot future routes are listed as
  `blocked-future` and tests assert they are not mounted;
- allowed read routes require hash-only bearer tokens and emit audit events.

Verdict: Local Agent write/config routes remain blocked and require a separate
named Local Agent mutation gate.

### Backup, restore, import and reboot

Existing AMN2 backup code is local/operator recovery functionality, not a public
or API route:

- backup archive bytes are encrypted;
- manifests exclude `app_secret_key` and `telegram_bot_token`;
- restore validation rejects invalid schemas, checksum mismatch, missing
  required tables/columns and incompatible encrypted peer secrets before writing
  target state;
- Local Agent backup/restore/reboot routes remain `blocked-future`.

Verdict: production backup/restore/import remains `P6-C004`. Future production
work needs encrypted backup handling, restore preview/apply policy, disaster
recovery drill, audit, confirmation, rollback and retention decisions.

### Telegram bot identity and media

Phase 5 split local media registry from Telegram identity mutation:

- local validation/stage/select/manifest for bot media is allowed;
- Telegram profile photo apply, Bot API token use and live bot identity changes
  are not default actions;
- support/news bot production split needs separate tokens/scopes/runtime
  ownership before any live apply.

Verdict: `P6-I004` and `P6-I005` remain separate production/Telegram identity
gates.

### Logs, audit and evidence

Security evidence policy is consistent across AMN3 docs and AMN2 tests:

- no raw `.env`, `servers.yml`, tokens, Authorization headers, private keys,
  PSK, `.conf`, QR, `vpn://`, target host/IP or full logs in evidence;
- redaction tests cover private keys, Telegram tokens, API private values and
  backup-code-like material;
- admin/API/agent audit metadata is safe summary metadata, not raw secret output.

Verdict: current redaction/evidence posture is adequate for Phase 6 planning.
Any future public/config/write/backup gate must include its own forbidden-marker
tests and safe evidence template.

### Upstream/license boundary

PRVTPRO remains GPL-3.0 research-only. Phase 6 may use ideas and behavioral
signals, but must not copy upstream code, templates, UI, manager implementations,
scripts or workflow code.

Verdict: no upstream/GPL code copy was performed.

## Findings And Follow-Ups

No new blocking vulnerability was validated in this focused local/docs review.
This statement is limited to P6-C005 scope and the focused test suite above; it
is not a claim that a full repository-wide exhaustive security scan has been
completed.

Follow-up created by this review:

```text
P6-N003 Integration status current-head alignment
importance: normal
source: P6-C005 review
gate: local-only code/tests/docs
reason: app/services/integration_status.py still carries historical c92/7764/7281254 status constants while AMN3 Phase 6 source of truth is AMN2 2215761. This does not open a live surface, but stale status can confuse operator/API evidence and should be aligned in a separate local-only slice.
```

Production/public launch blockers that remain gated:

- `P6-C001` Public exposure gate.
- `P6-C002` Config delivery gate.
- `P6-C003` Write API production gate.
- `P6-C004` Production backup/restore/import gate.
- `VPS-REBUILD-001` destructive rebuild.
- Local Agent write/config routes.
- Production peer/user mutation.
- Telegram bot profile/icon apply.

## Boundary

Performed:

- local AMN3 docs/security review;
- read-only AMN2 policy/code inspection;
- focused AMN2 local security regression suite;
- AMN3 evidence/status/backlog/handoff updates.

Not performed:

- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery, `.conf`, QR or `vpn://`;
- `/api/clients` write CRUD;
- API `config:read`;
- Local Agent write/config mutation;
- backup/import/reboot action;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Active Plan Update

Remove from active Phase 6 plan:

```text
P6-C005 Production security review gate
```

Remaining active Phase 6 plan:

```text
critical_default: none

critical_gated_deferred:
- P6-C001 Public exposure gate.
- P6-C002 Config delivery gate.
- P6-C003 Write API production gate.
- P6-C004 Production backup/restore/import gate.
- VPS-REBUILD-001 destructive rebuild.
- Local Agent write/config routes.
- Production peer/user mutation.

very_important:
- P6-I001 Scoped API tokens production implementation.
- P6-I002 User self-service surface separated from admin surface.
- P6-I003 Payments/manual approval boundary if commercial access is enabled.
- P6-I004 Support bot and news bot production split.
- P6-I005 Telegram bot profile/icon apply gates.

important:
- P6-M001 Multi-server/multi-protocol capability registry.
- P6-M002 Health/status polling scheduler with aggregate-only privacy boundary.
- P6-M003 Attach-existing-server reconciliation beyond read-only report mode.

normal:
- P6-N001 Public docs/API taxonomy if public docs are approved.
- P6-N002 Admin analytics without per-peer/user leakage.
- P6-N003 Integration status current-head alignment.
- P4-PRVTPRO-REFRESH-003-LIVE live probes/actions.

simple:
- P6-S001 Release checklist and changelog.
- P6-S002 Recurring upstream refresh incorporation.

cosmetic:
- P6-X001 Public product copy polish.
- P6-X002 Brand/media consistency across bots, panel and docs.
```

## Next Recommendation

Recommended next choice:

```text
P6-I001 Scoped API tokens production implementation
```

Start it as local-only code/tests/docs. It should not add public exposure,
`config:read`, write scopes, `/api/clients` CRUD, Local Agent mutations,
config delivery, backup/import/reboot or live VPS actions without their own
named gates.
