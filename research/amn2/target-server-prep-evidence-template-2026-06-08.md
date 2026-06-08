# Target Server Prep Evidence Template

Дата: 2026-06-08.

Назначение: шаблон safe evidence для нового целевого VPS AMN2. Заполнять после ручных проверок на новом сервере.

## Server

```text
target_server_label:
provider:
public_ip_or_domain_ready:
os:
kernel:
time_utc:
docker_status:
docker_containers_summary:
public_3030:
public_3040:
```

## AMN2 Runtime

```text
amn2_path: /opt/amn2
amn2_head_or_source_overlay:
runtime_mode: manual
service_mode: not-enabled
VPS_APPLY_ENABLED: false
data_dir: present
env_file: present
servers_yml: present
venv: present
```

## Read-Only Preflight

```text
bot_check_network:
server_preflight:
server_config:
database_sync:
server_check_dry_run:
peer_apply_dry_run:
peer_revoke_dry_run:
traffic_dry_run:
backup_target:
```

## API Loopback Smoke

```text
api_smoke_run_id:
api_smoke_status:
checked_routes:
route_status_codes:
forbidden_markers_count:
auth_status:
missing_bearer_http:
wrong_scope_http:
revoked_token_http:
listener_status:
audit_status:
safe_evidence_dir:
safe_bundle:
```

## Web/Admin Manual Check

```text
web_runtime_mode: manual
web_login_http:
web_listener:
public_3030:
api_listener:
public_3040:
```

## Backup

```text
backup_create:
backup_file:
backup_verify:
database_kind:
includes:
excludes:
```

## Decision

```text
decision:
target_server_manual_gate:
service_mode_gate:
next_step:
```

## Boundary

This evidence does not authorize:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse-proxy deployment without a separate gate;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links, backup contents or full logs.
