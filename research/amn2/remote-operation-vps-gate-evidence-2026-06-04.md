# `amn2` Remote Operation VPS Gate Evidence 2026-06-04

Date: 2026-06-04.

Purpose: record the safe real VPS Phase 1 evidence for `amn2/codex/remote-operation-vps-gate-prep`, head `7281254`, without publishing `.env`, `servers.yml`, PSK, private keys, raw API tokens, token hashes, full configs, QR payloads, `vpn://` links or raw peer/server public keys.

## Candidate

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex/remote-operation-vps-gate-prep
head: 7281254 Merge stable API web panel baseline into remote operation gate
base: 294803e Add API readiness and token web pages
package: dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip
package_sha256: 85FE02C2D9F402562E36CD08990CCA0A891E9173D5257EFC52E5DDF8F5C2061B
```

## Source Overlay Verification

The VPS `/opt/amn2` install is a source-overlay install, not a git checkout. `branch/head: not a git checkout` is expected for this package path.

A stale shell environment issue was found during the first overlay attempt: an old `AMN2_SOURCE_ZIP` pointed to a historical `2010d60` source zip while the marker was written as `7281254`. AMN3 fixed the package script in commit `6e8bc3c Harden remote operation gate overlay script` by refusing unexpected source zip basenames and checking the dry-run metadata markers before overlay completion.

Verified after re-overlay:

```text
.amn2_source_overlay_commit: 7281254
peer_apply_path: /opt/amn2/app/server/peer_apply.py
source_has_metadata: True
source_has_operation_id: True
```

## API Sanity

API loopback sanity was rerun after the `7281254` package overlay.

```text
run_id: 20260604T124552Z
workspace: /opt/amn2
server_name: local
api_bind: http://127.0.0.1:3040
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260604T124552Z.tar.gz
```

No raw API token, Authorization header, token hash, `.env`, `servers.yml`, private key, PSK or full API server log is recorded here.

## Phase 1 Read-Only Checks

The operator kept `VPS_APPLY_ENABLED=false`.

Observed safe summary:

- `python -m app.cli bot check-network`: Telegram API ok, bot identity returned, proxy enabled.
- `python -m app.cli server preflight --config servers.yml --server "$SERVER_NAME" --db "$DB_PATH"`: server config ok, database sync ok, server check dry-run ok, peer apply dry-run ok, peer revoke dry-run ok, traffic dry-run ok, backup target ok.
- `python -m app.cli server check --config servers.yml --server "$SERVER_NAME" --dry-run`: read-only command preview only, no changes.
- `python -m app.cli server check --config servers.yml --server "$SERVER_NAME"`: read-only SSH/Docker diagnostics ok; Debian detected, Docker installed, target container running, AmneziaWG interface check succeeded, UDP port visible. Private key and preshared keys were hidden by command output.
- `python -m app.cli server collect-traffic --config servers.yml --server "$SERVER_NAME" --db "$DB_PATH" --dry-run`: dry-run traffic collection only, no DB write.

Raw peer/server public keys from `awg show` output are intentionally not copied into AMN3.

## Phase 1 Mutation Dry-Run

`apply-peer --dry-run` for a dedicated synthetic test peer returned:

```text
Dry-run peer apply: local
No changes will be made.
Operation ID: server.peer.apply
Risk class: remote-state-write
Consistency status: dry-run
Local side effects: none
Remote side effects: docker-config-peer-upsert, container-restart
Rollback note: Remove the peer from the persistent config and restart the Docker container.
Peer: TEST_PEER_PUBLIC_KEY allowed-ips 10.8.1.250/32
```

`revoke-peer --dry-run` for the same synthetic test peer returned:

```text
Dry-run peer revoke: local
No changes will be made.
Operation ID: server.peer.revoke
Risk class: remote-state-write
Consistency status: dry-run
Local side effects: none
Remote side effects: docker-config-peer-remove, container-restart
Rollback note: Re-apply the peer from local device metadata and restart the Docker container.
Peer: TEST_PEER_PUBLIC_KEY
```

The CLI printed a planned command preview for operator review. This is acceptable for this dry-run gate because it did not include PSK, private keys, full config contents, raw token/header/hash, QR payloads or `vpn://` links. The preview was not executed in this phase.

## Decision

```text
phase_1_result: dry-run-only-pass
phase_2_result: not-run
live_apply_or_revoke: not-run
vps_apply_enabled: false
redaction_result: passed for published evidence
state_change_result: no intentional state-changing apply/revoke command was run
decision: dry-run-only-pass
```

## Consequences

- Do not mark the branch `verified-live` yet.
- Do not merge remote-state-write behavior as live-verified solely from this evidence.
- KYORESUAS/PRVTPRO work may continue only on read-only/API status/UX design lanes.
- Write lifecycle, config delivery API, Local Agent mutation routes, public config delivery and live manager flows remain blocked until a separate Phase 2 single test peer apply/revoke gate is explicitly approved and recorded.
