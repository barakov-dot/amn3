# Target Server AWG2 Runtime Smoke Evidence 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать safe evidence controlled runtime gate для нового целевого VPS AMN2. Gate поднял новый AmneziaWG Docker runtime, создал реальный `/opt/amn2/servers.yml` на VPS через secret-safe channel и подтвердил официальный read-only API loopback smoke. Это не service-mode launch и не live peer apply/revoke gate.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
target_server_runtime_status: read-only-smoke-pass
service_mode: not-enabled
live_peer_write_gate: closed
VPS_APPLY_ENABLED: false
```

## Runtime Source Notes

Runtime shape was aligned with upstream Amnezia client AWG2 Docker scripts and constants:

- `client/server_scripts/awg/Dockerfile` uses `amneziavpn/amneziawg-go:latest`.
- `client/server_scripts/awg/run_container.sh` starts an AWG container with privileged Docker networking, NET_ADMIN/SYS_MODULE and UDP port publishing.
- `client/server_scripts/awg/configure_container.sh` writes `/opt/amnezia/awg/awg0.conf`.
- `client/core/utils/containers/containerUtils.cpp` maps AWG2 to `amnezia-awg2`.
- `client/core/utils/constants/protocolConstants.h` records AWG config paths and default packet/header constants.

References:

- https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/server_scripts/awg/Dockerfile
- https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/server_scripts/awg/run_container.sh
- https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/server_scripts/awg/configure_container.sh
- https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/core/utils/containers/containerUtils.cpp
- https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/core/utils/constants/protocolConstants.h

## Safe Preflight

```text
source_overlay_commit: f7f6131
docker_active: active
docker_containers_before_runtime: none
ip_forward: 1
tun: present
udp_30001_before_runtime: free
tcp_3030_before_runtime: free
tcp_3040_before_runtime: free
ufw: inactive
```

No public IP, SSH credentials, host key material, provider details, `.env`, raw `servers.yml`, raw tokens, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

## Runtime Gate Result

The first attempt built the image and created the container, then stopped before configuration because the bootstrap check called `docker exec ... command -v ...`; `command` is a shell builtin, not an executable. The script was corrected to use `sh -c 'command -v ...'` and made resume-safe for the already-created container. No secret-bearing config was read or printed during diagnosis.

```text
runtime_gate: passed
image_build: passed
container_name: amnezia-awg2
container_create: passed
container_resume: passed
awg_tools: present
server_private_key_display: hidden
server_psk_display: hidden
server_public_key_file: present
container_config: present
awg_interface: up
udp_30001: listening
self_ssh: passed
servers_yml: present
servers_yml_load: passed
VPS_APPLY_ENABLED: false
```

`servers.yml` exists only on the VPS and was not published. It points AMN2 at local self-SSH for Docker-backed operations and at the new public VPN endpoint for client connectivity.

## API Loopback Smoke

```text
VPS verdict: pass
run_id: 20260609T043158Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260609T043158Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260609T043158Z.tar.gz
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

## Post-Smoke Runtime Snapshot

```text
container: amnezia-awg2
container_status: running
udp_30001: listening
tcp_3030_after_smoke: absent
tcp_3040_after_smoke: absent
servers_yml_load: passed
server_name: local
runtime_type: docker
container_name: amnezia-awg2
vpn_port: 30001
```

## Still Closed

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- production peer mutation;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse proxy deployment;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Completed next gate: exactly one disposable test peer live apply/sync/revoke/sync passed on the new endpoint with `--preshared-key-stdin`. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`.
