# `c8a6363` Local Agent runtime summary VPS smoke evidence

Дата: 2026-06-06.

Назначение: зафиксировать реальный read-only VPS update/smoke для текущего `amn2/codex-vps-test-prep` head `c8a6363 Add Local Agent runtime summary mapper`.

## Итог

```text
decision: read-only-vps-smoke-pass
source commit: c8a6363 Add Local Agent runtime summary mapper
source update run_id: 20260606T202012Z
API smoke run_id: 20260606T202040Z
safe bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T202040Z.tar.gz
previous VPS-smoked source: 32d01fd Update integration status for controlled prod
```

`c8a6363` становится текущим VPS-smoked runtime/source baseline. Это не открывает live peer mutations, public web/API exposure, config delivery, backup/import/reboot или Local Agent mutation surfaces.

## Source update evidence

```text
LATEST_SOURCE=/opt/amn2/vps-smoke/source-update-20260606T202012Z
run_id=20260606T202012Z
target=/opt/amn2
source_zip=/root/amn2-vps-update-and-smoke-kit-c8a6363/amn2-codex-vps-test-prep-c8a6363-source.zip
source_sha=E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
expected_commit=c8a6363
python=Python 3.13.5
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
source_update_status=passed
source_commit=c8a6363
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260606T202012Z
```

## API loopback smoke evidence

```text
LATEST_SMOKE=/opt/amn2/vps-smoke/api-loopback-20260606T202040Z
VPS verdict: pass
run_id: 20260606T202040Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260606T202040Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T202040Z.tar.gz
```

`branch/head: not a git checkout` is expected for the source-overlay VPS install path.

## Checked routes

```text
checked_routes: 5
status: passed
```

Routes:

| Route name | HTTP | Forbidden markers |
| --- | --- | --- |
| `servers` | 200 | none |
| `integration_status` | 200 | none |
| `server_summary` | 200 | none |
| `metrics_summary` | 200 | none |
| `users_summary` | 200 | none |

## Auth evidence

```text
auth_status=passed
missing_bearer_expected=401
missing_bearer_actual=401
wrong_scope_expected=403
wrong_scope_actual=403
revoked_token_expected=401
revoked_token_actual=401
```

## Listener evidence

```text
listener_rows=1
expected_host=127.0.0.1
host=127.0.0.1
pid_match=yes
port=3040
loopback_only=yes
```

This confirms the API smoke listener stayed on loopback for this gate.

## Audit evidence

```text
api_read_rows=5
audit_safe=yes
```

Each `api_read` audit row had only these metadata keys:

```text
aggregate_only
method
owner_label
path
scope
status
token_id
token_name
```

Forbidden markers:

```text
row_1: none
row_2: none
row_3: none
row_4: none
row_5: none
```

## Server DB sync evidence

```text
server_db_sync=passed
id=1
name=local
status=active
runtime=docker
```

## Safety review

The returned evidence did not include:

- raw API token;
- Authorization header;
- token hash;
- `.env`;
- `server.yml` / `servers.yml`;
- `.conf`;
- QR payload;
- `vpn://`;
- `PrivateKey`;
- `PresharedKey`;
- SSH private key or password;
- full `api-server.log`.

The source update preserved:

- `/opt/amn2/.env`;
- `/opt/amn2/data`;
- `/opt/amn2/venv`;
- `/opt/amn2/servers.yml`.

## Decision

```text
result: read-only-vps-smoke-pass
current VPS-smoked runtime/source: c8a6363
previous VPS-smoked runtime/source: 32d01fd
next gate: operator-only controlled prod readiness decision
```

Still blocked until separate gates:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply`;
- live `revoke-peer --apply`;
- public/self-service config delivery;
- API `config:read`;
- `/api/clients` write CRUD;
- backup/import/reboot routes;
- Local Agent clients/configs/write mutations;
- public web/API exposure.
