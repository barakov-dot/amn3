# AMN2 Phase 6 final closeout and known-good snapshot

Дата: 2026-06-14.

Статус: `phase-6-final-closeout-complete`.

AMN3 commit at closeout: to be verified after this evidence commit.

AMN2 branch: `codex-vps-test-prep`.

AMN2 current head: `b121865 Add multi instance conflict model`.

AMN2 latest VPS-smoked/package head:
`0de7a77 Polish fresh installer preflight planning`.

Current disposable VPS: `89.185.80.166`.

## Decision

Phase 6 default lane is closed.

Default local queue is empty.

The project remains private/operator-only. Public/self-service launch is not
opened.

Known-good live state remains the disposable VPS smoke for `0de7a77`. Later AMN2
heads `4cde273` and `b121865` are local-only, pushed, tested and not
package-rebuilt or VPS-smoked.

## Closed Phase 6 / after-Phase-6 local work

- `P6-C005` production security review gate.
- `P6-I001` scoped API tokens production implementation.
- `P6-I002` user self-service/admin separation.
- `P6-M001 + P6-N003` capability registry and current-head alignment.
- `P6-I003 + P6-I004` payment/manual approval and support/news bot split.
- `P6-I005` Telegram profile/icon apply gate policy.
- `P6-M002 + P6-N002` aggregate-only health/status and analytics boundary.
- `P6-M003 + P6-S001` reconciliation/release boundary.
- `P6-S003` project operating-system extraction template.
- `P6-N004 + P6-S002` telemetry retention and upstream refresh incorporation.
- `P6-M004 + P6-X001 + P6-X002` client compatibility/copy/brand boundary.
- `P6-C006`, `P6-C009`, `P6-C010` live update/smoke gates for named heads.
- `P6-C002-design + P6-I006` config-link/entitlement boundary.
- `P6-I007` fresh install wizard/bootstrap boundary.
- `P6-N001 + P6-C007 checklist-only`.
- `P6-C008` current-head package preflight for `c46f664`.
- `P6-X003` package runbook escaping hygiene.
- `P6-S004` closeout packet / next-chat / fresh installer backlog grooming.
- `P6-AI001` automation intake aggregation and closeout readiness.
- `FI-M004 + P6-N005` package asset path preflight and route-order guard.
- `P6-M005` multi-instance/port/IPAM conflict model.

## Current known-good VPS snapshot

Known-good live head: `0de7a77f3eb09d23dc2785d402bc51c2b5eb7835`.

Evidence:

```text
research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
```

Package:

```text
dist/amn2-vps-update-and-smoke-kit-0de7a77.zip
sha256: 7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B
```

Source zip:

```text
dist/amn2-codex-vps-test-prep-0de7a77-source.zip
sha256: B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295
```

Live smoke summary:

- source overlay updated to `0de7a77`;
- source update run_id `20260614T062734Z`;
- read-only API smoke run_id `20260614T063327Z`;
- web remains loopback-only on `127.0.0.1:3030`;
- temporary API smoke used loopback `127.0.0.1:3040`;
- auth/listener/audit passed;
- negative auth checks returned `401/403/401`;
- external probes for `3030/3040/80/443` returned `000`;
- `VPS_APPLY_ENABLED=false` remained explicit.

## Current local AMN2 head

Current AMN2 head `b121865` includes local-only work after the known-good VPS
head:

- `4cde273 Add installer preflight taxonomy guards`;
- `b121865 Add multi instance conflict model`.

Verification for `b121865`:

```text
full AMN2 suite: 724 passed, 1 StarletteDeprecationWarning
git diff --check: passed
git diff --cached --check: passed
```

`b121865` is not package-rebuilt or VPS-smoked. Any future live update from
`0de7a77` to `b121865` requires a new named live package/apply/smoke gate.

## Remaining gated/deferred work

These are not active default work:

- `P6-C001` public exposure/public docs/OpenAPI publication;
- `P6-C002` real config delivery, `.conf`, QR, `vpn://`, tokenized public
  redeem and Telegram live config send;
- `P6-C003` write API production and `/api/clients` CRUD;
- `P6-C004` production backup/restore/import;
- `P6-C007` destructive cleanup/reinstall;
- `VPS-REBUILD-001` destructive rebuild;
- Local Agent write/config routes;
- production peer/user mutation;
- live package apply/smoke for any head after `0de7a77`;
- Telegram identity/profile/media mutation.

## Next phase entry

Recommended next mode:

```text
Clean installer / productization follow-up, local-only by default
```

Start from:

```text
docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md
docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
research/amn2/transfer-backlog.md
```

Recommended next action:

```text
Pause on known-good 0de7a77, or open a separately named gate if live/public/config/destructive work is intentionally chosen.
```

## Negative controls

No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed for this closeout packet.
