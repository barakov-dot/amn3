# Target Server Live Peer Gate Evidence 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать safe evidence live gate для ровно одного disposable test peer на новом целевом VPS после AWG2 runtime smoke. Gate выполнил generate hidden peer material, dry-run apply/revoke, live apply/sync/revoke/sync и post-live read-only API smoke. Production peer не использовался.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
target_server_runtime_status: read-only-smoke-pass before live peer gate
previous runtime evidence: research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
live_peer_gate_status: verified-live
scope: exactly one disposable test peer
service_mode: not-enabled
public_api_3040: closed
direct_public_web_3030: closed
```

## Safety Boundary

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, token hashes, private keys, PSK, peer public key, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

The live apply command used `--preshared-key-stdin`; PSK was not passed as a local command-line argument. `VPS_APPLY_ENABLED=true` was scoped to the live apply/revoke commands and returned to `false` at the end.

## Gate Result

```text
live_peer_gate: passed
run_id: 20260609T045342Z
source_overlay_commit: f7f6131
server_name: local
container_name: amnezia-awg2
runtime_preflight: passed
initial_peer_count: 0
initial_sync_counts: known=0 unknown=0 missing=0
test_peer_material: generated_hidden
test_peer_ip: selected_hidden
apply_dry_run: passed
revoke_dry_run: passed
apply_live: passed
apply_config_presence: passed
after_apply_peer_count: 1
after_apply_sync_counts: known=0 unknown=1 missing=0
revoke_live: passed
revoke_config_absence: passed
after_revoke_peer_count: 0
after_revoke_sync_counts: known=0 unknown=0 missing=0
test_peer_material: unset
VPS_APPLY_ENABLED_final: false
safe_evidence_dir: /opt/amn2/vps-smoke/live-peer-gate-20260609T045342Z
```

## Post-Gate Runtime Snapshot

```text
container: amnezia-awg2
container_status: running
udp_30001: listening
tcp_3030_after_gate: absent
tcp_3040_after_gate: absent
peer_count_after_gate: 0
```

## Post-Gate API Loopback Smoke

```text
VPS verdict: pass
run_id: 20260609T045546Z
branch/head:
  not a git checkout
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260609T045546Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260609T045546Z.tar.gz
```

Route result:

```text
checked_routes: 6
routes:
  servers: 200
  integration_status: 200
  local_agent_runtime_summary: 200
  server_summary: 200
  metrics_summary: 200
  users_summary: 200
forbidden_markers: none
status: passed
```

## Still Closed

- production peer mutation;
- broad `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse proxy deployment;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Recommended next gate: keep the new target VPS as `verified-live` for the remote peer apply/revoke primitive and choose the next layer deliberately:

- manual web/admin + bot runtime check on the new target VPS, still loopback-only; or
- service-mode gate for `systemd`/reverse proxy; or
- product/API expansion planning with write/config/self-service surfaces still closed.
