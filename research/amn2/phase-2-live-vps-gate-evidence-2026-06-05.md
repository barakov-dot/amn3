# AMN2 Phase 2 Live VPS Gate Evidence

Date: 2026-06-05.

Purpose: record the Phase 2 live single disposable test peer apply/revoke gate for current stable `amn2/codex-vps-test-prep` without publishing `.env`, `servers.yml`, raw API token, Authorization header, token hash, private keys, PSK, raw peer public keys, full `.conf`, QR payload, `vpn://` links or full logs.

## Candidate

```text
repo: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
head: 7764ae7 Cover integration status in API smoke
package: dist/amn2-vps-update-and-smoke-kit-7764ae7.zip
package_sha256: 832E1B1F6516A02E0D6AA45672B8FF526DF15D27117D2063CE45F9966825A66A
source_sha256: 94D110BB9AA17C65E02C1780380BA77E49A4F0ADDDECEA7DE267FFC9F353B42B
```

Important ancestry:

```text
7281254 is an ancestor of 7764ae7.
The VPS was not downgraded to the historical 7281254 package.
```

## VPS Update And Read-Only Smoke

The first API smoke attempt produced a `VPS verdict: pass`, but `api-smoke-result.json` checked only four routes. Diagnostics showed the VPS source overlay marker was still `7281254`, and `app.cli._api_smoke_paths("local")` did not include `integration_status`.

The operator reapplied the `7764ae7` source overlay with explicit expected source commit/SHA:

```text
source_update_status: passed
source_commit: 7764ae7
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260605T070422Z
```

Post-overlay sanity:

```text
.amn2_source_overlay_commit: 7764ae7
app_cli_file: /opt/amn2/app/cli.py
smoke_paths: servers, integration_status, server_summary, metrics_summary, users_summary
```

Read-only/API smoke after re-overlay:

```text
run_id: 20260605T071302Z
workspace: /opt/amn2
branch/head: not a git checkout
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
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260605T071302Z.tar.gz
```

`api-smoke-result.json` checked five read-only routes and reported `status=passed` with no forbidden markers:

```text
servers: 200
integration_status: 200
server_summary: 200
metrics_summary: 200
users_summary: 200
```

No raw API token, Authorization header, token hash, `.env`, `servers.yml`, private key, PSK, full config, QR payload or `vpn://` was recorded.

## Phase 2 Confirmation And PSK Handling

The operator separately confirmed Phase 2 live single disposable peer apply/revoke after the read-only `7764ae7` smoke passed.

PSK handling decision:

```text
decision: option 1
meaning: use the current CLI --preshared-key argument only for a disposable one-time test peer
strict_no_secret_on_local_command_line: not required for this gate
```

The stricter `--preshared-key-stdin` slice remains a recommended hardening follow-up before future repeated live operations.

## Immediate Dry-Run

The first dry-run attempt was safely invalid because the disposable peer variables were unset. It produced `allowed-ips /32`; no live command was run from that state.

The operator generated a disposable test peer in shell-local variables and repeated dry-run. Redacted dry-run result:

```text
apply_dry_run_status: passed
revoke_dry_run_status: passed
operation_id_apply: server.peer.apply
operation_id_revoke: server.peer.revoke
risk_class: remote-state-write
consistency_status: dry-run
local_side_effects: none
remote_side_effects_apply: docker-config-peer-upsert, container-restart
remote_side_effects_revoke: docker-config-peer-remove, container-restart
rollback_note_apply: Remove the peer from the persistent config and restart the Docker container.
rollback_note_revoke: Re-apply the peer from local device metadata and restart the Docker container.
peer: TEST_PEER_PUBLIC_KEY allowed-ips TEST_PEER_IP/32
```

The dry-run planned the expected Docker persistent config read/write and container restart steps. The AMN3 evidence does not record the raw peer public key or PSK.

## Live Apply / Sync / Revoke / Sync

Live gate scope:

```text
server_alias: local
test_peer: dedicated disposable test peer
production_peer_used: no
live_commands: apply-peer --apply, sync-peers, revoke-peer --apply, sync-peers
```

Redacted live result:

```text
apply_result: passed
apply_effect: one disposable test peer added and Docker container restarted
sync_after_apply: passed
sync_after_apply_state: unknown remote peers increased from 3 to 4, with the disposable test peer present
revoke_result: passed
revoke_effect: the same disposable test peer removed and Docker container restarted
sync_after_revoke: passed
sync_after_revoke_state: unknown remote peers returned to 3, disposable test peer absent
existing_peers_unchanged: yes, based on peer count returning to the pre-test count and no production peer being targeted
rollback_recovery_used: no
```

The operator output contained raw peer public keys in the shell transcript. They are intentionally not copied into AMN3 evidence.

## Decision

```text
phase_1_result: api-smoke-passed-on-7764ae7
phase_2_result: verified-live
live_apply_or_revoke: exactly one disposable test peer apply/revoke
redaction_result: passed for AMN3 evidence; raw peer keys are omitted here
final_peer_state: disposable test peer removed; final sync returned to the pre-test remote peer count
rollback_recovery_used: not needed
decision: verified-live
```

## Local Post-Gate Verification

Focused remote-operation verification was rerun locally on `amn2/codex-vps-test-prep` at `7764ae7` after the live gate:

```text
tests/deploy/test_runtime_registry.py
tests/server/test_operation_runner.py
tests/server/test_peer_apply.py
tests/services/test_access_service.py
tests/server/test_cli_server_check.py
result: 71 passed
```

The local `amn2` worktree remained clean.

## Consequences

- `dry-run-only-pass` is no longer the current result for this gate; Phase 2 has verified one disposable peer live apply/revoke on current stable `7764ae7`.
- This does not unlock broad write API, public config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes or Local Agent mutations.
- Future changes to peer apply/revoke, config templates/defaults, IP allocation, peer sync classification or Docker write/restart behavior still require their own gate.
- Recommended follow-up before repeated operator usage: implement a safer local secret input path such as `--preshared-key-stdin`.
