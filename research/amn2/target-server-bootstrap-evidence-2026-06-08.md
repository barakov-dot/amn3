# Target Server Bootstrap Evidence 2026-06-08

Дата: 2026-06-08.

Назначение: зафиксировать safe evidence первичного bootstrap нового целевого VPS для AMN2 после target-server prep gate. Это не production/service-mode launch и не full API smoke pass.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
target_server_bootstrap_status: partial-pass
service_mode: not-enabled
live_write_gates: closed
VPS_APPLY_ENABLED: false/not-set
```

## Safe Server Summary

```text
os: Ubuntu 24.04.4 LTS
kernel: Linux 6.8.0-111-generic
arch: x86-64
python: Python 3.12.3
curl: present
sha256sum: present
python3: present
ss: present
git: present
unzip: present
rsync: present
ufw: present
jq: present
docker: present
docker_active: active
docker_containers: none
```

No public IP, SSH credentials, host key material, provider details, `.env`, `servers.yml`, raw tokens, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

## Bootstrap Result

```text
base_bootstrap: passed
kit_download: passed
kit_sha256: passed
kit_extract: passed
source_zip_sha: passed
source_overlay_update: passed
source_update_run_id: 20260608T202421Z
source_overlay_commit: f7f6131
pip_install: passed
cli_import: passed
env_file: present
servers_yml: missing
db_schema_init: passed
db_file: present
```

Runtime guard:

```text
web_admin_enabled: false
api_bind: 127.0.0.1:3040
vps_apply_enabled: false
api_process_after_probe: absent
amn2_loopback_listeners_after_probe: absent
```

## API Bootstrap Probe

This was a partial loopback probe, not the official six-route API smoke. It verified that the API can start on loopback, scoped token auth can be used, the token can be revoked, and the safe `/api/servers` route responds.

```text
api_bootstrap_probe: passed
api_ready: passed
listener_during_probe: 127.0.0.1:3040
servers_route_http: 200
forbidden_markers_count: 0
raw_token_display: hidden
revoke_status: revoked
bootstrap_probe_tokens_open_after_cleanup: 0
```

Expected official route set:

```text
checked_routes_expected: 6
smoke_paths: servers,integration_status,local_agent_runtime_summary,server_summary,metrics_summary,users_summary
full_api_smoke_status: blocked_missing_real_servers_yml
```

## Backup Probe

```text
backup_create: passed
backup_file: backups/amneziya-backup-20260608T203559Z.tar.enc
backup_verify: passed
```

The backup file name is recorded as evidence only; backup contents are not published.

## Blocker

Full read-only API smoke remains blocked until a real target-server `servers.yml` is created on the VPS through a secret-safe channel. A placeholder `servers.yml` was not created because it would make the target server look configured when it is not.

The generated `.env` contains local server-side placeholder/bootstrap values and secrets that are not published. The Telegram bot token is still a placeholder and must be replaced on the VPS before bot runtime checks.

## Still Closed

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse proxy deployment;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Recommended next gate: create or securely transfer the real target-server `servers.yml` on the VPS, then run official read-only API loopback smoke with `VPS_APPLY_ENABLED=false`.
