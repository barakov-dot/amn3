# Phase 5 P5-D001 operator-only pilot acceptance and Phase 6 entry decision

Date: 2026-06-13.

Status: `operator-only-pilot-accepted`.

Scope: AMN3 docs-only decision checkpoint after `P5-C010`.

## Decision

```text
task_id: P5-D001
decision: operator-only-pilot-accepted
current_mode: private/operator-only
current_access_model: SSH tunnel / loopback web-admin
AMN2_current_head: 2215761 Polish operator web admin UX
latest_VPS_smoked_head: 2215761
latest_live_update_smoke: P5-C010
Phase_5_default_queue: empty
Phase_6_entry: planning-ready only
Phase_6_live_public_self_service: not opened
```

The Phase 5 operator-only pilot is accepted for the current private service-mode
baseline: AMN2 `2215761` is installed on the disposable test VPS, web/bot
services are active after restart, read-only loopback API smoke passed, and
remote listeners remain loopback/closed as expected.

This decision does not make AMN2 a public/self-service product. It only closes
the controlled operator-only pilot checkpoint and allows a separate Phase 6
planning/productization lane to be opened when the operator chooses.

## Evidence Inputs

```text
P5-C010 evidence: research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md
AMN2 source commit: 221576169a84bbf662114c564e83c41fba0091b5
package: dist/amn2-vps-update-and-smoke-kit-2215761.zip
package_sha256: 6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44
source_sha256: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
source_overlay_run_id: 20260613T045004Z
api_smoke_run_id: 20260613T045107Z
api_smoke_verdict: pass
web_bot_services: active after restart
loopback_login_http: 200
remote_listener_snapshot: 127.0.0.1:3030 only; 3040/80/443 absent
VPS_APPLY_ENABLED: false
```

## Accepted Private Baseline

Accepted as current private/operator-only baseline:

- AMN2 branch `codex-vps-test-prep` at `2215761`;
- web/admin brand and sampled authenticated pages use the Phase 5 Russian-first
  operator UX cleanup;
- web/admin remains loopback-only;
- bot service is active, but no live Telegram send/profile mutation was
  performed by this decision;
- read-only API smoke passed on loopback;
- package/source evidence is recorded in AMN3;
- current Phase 5 default work queue is empty.

## Phase 6 Entry Position

Phase 6 is useful only if the project moves beyond private/operator-only mode
toward public/self-service/productization.

The safe Phase 6 entry posture is:

```text
phase6_status: planning-ready
phase6_first_recommendation: P6-C005 Production security review gate
phase6_public_exposure: not authorized
phase6_config_delivery: not authorized
phase6_write_api: not authorized
phase6_backup_restore_import: not authorized
phase6_destructive_rebuild: not authorized
```

`P6-C005` should be first because it blocks the risky Phase 6 branches:
public exposure, config delivery, write API, backup/import/restore, and
Telegram identity/runtime split.

## Remaining Gated Work

These are not executed by `P5-D001`:

```text
VPS-REBUILD-001: critical destructive, not executed, defer.
write API / /api/clients CRUD: critical gated, not executed.
config delivery: critical gated, not executed.
public exposure: critical gated, not executed.
backup/import/reboot: critical gated, not executed.
Local Agent write/config routes: critical gated, not executed.
production peer/user mutation: critical gated, not executed.
P4-PRVTPRO-REFRESH-003-LIVE probes/actions: normal gated, not executed.
```

## Boundary

Performed:

- AMN3 docs/evidence/status decision only;
- active-plan cleanup for `P5-D001`;
- Phase 6 recommendation alignment.

Not performed:

- live VPS command;
- SSH command;
- package upload/apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery, `.conf`, QR or `vpn://`;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-D001 Operator-only pilot acceptance and Phase 6 entry decision
```

Remaining default Phase 5 plan:

```text
critical_default: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Remaining gated/deferred work:

```text
critical_gated: VPS-REBUILD-001, write API, config delivery, public exposure, backup/import/reboot, Local Agent write/config routes, production peer/user mutation
normal_gated: P4-PRVTPRO-REFRESH-003-LIVE probes/actions
```

## Next Recommendation

Recommended next choice:

```text
P6-C005 Production security review gate
```

This should start as local/docs/security review work. It must not open public
exposure, config delivery, write API, backup/import/reboot, Local Agent
mutations or destructive VPS actions by itself.
