# `c8a6363` VPS smoke preflight

Дата: 2026-06-06.

Назначение: зафиксировать попытку перейти от package-ready статуса `c8a6363` к read-only VPS update/smoke и сохранить безопасный результат проверки до реального доступа к VPS.

## Итог

```text
target commit: c8a6363 Add Local Agent runtime summary mapper
package: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
preflight status: local-package-preflight-pass
real VPS update/smoke: not run
reason: no safe non-interactive VPS access in current environment
server touched: no
last VPS-smoked source remains: 32d01fd, run_id=20260606T185114Z
```

Это не меняет статус `c8a6363`: пакет остается `package-ready-not-vps-smoked`.

## Что проверено локально

### Update/smoke kit SHA256

```text
actual:   027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
expected: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
result: matched
```

### Source zip SHA256

```text
actual:   E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
expected: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
result: matched
```

### Source zip hygiene

```text
entry_count: 294
required_missing: none
forbidden_entries: 0
```

Required entries checked:

```text
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
app/agent/runtime_summary.py
tests/agent/test_runtime_summary.py
```

Forbidden checks covered exact/prefix/suffix classes used by the update script:

```text
.env
server.yml
servers.yml
.git/
data/
venv/
.venv/
logs/
tmp/
__pycache__/
.pytest_cache/
*.sqlite3
*.db
*.key
*.pem
```

Only example env files were present, which is acceptable for source/package docs:

```text
.env.example
deploy/examples/.env.production.example
```

## Why real VPS smoke was not run here

Local discovery found:

```text
OpenSSH client: present
scp: present
~/.ssh/config: absent
sshpass: absent
Amneziya server.yml: present
server.yml auth.type: password
Amneziya .env key VPS_SSH_PASSWORD: present
```

The password value was not read, printed, copied, or used.

Running the VPS update from this desktop session would require either an interactive password prompt or passing a secret through command-line/process state. That conflicts with the current project rules for secret-bearing values and evidence hygiene.

## Safe next operator path

Use one of these safe access paths before running the real VPS smoke:

1. Run the kit manually from an operator terminal already logged into the VPS.
2. Configure key-based SSH for the VPS and use a local SSH alias without putting passwords in commands.
3. Use a temporary operator-controlled SSH session and paste only the safe commands from the runbook.

Primary runbook:

```text
dist/amn2-vps-update-and-smoke-kit-c8a6363/AMN2_VPS_UPDATE_AND_SMOKE_c8a6363.ru.md
```

Required boundaries for the real run:

```text
VPS_APPLY_ENABLED=false
AMN2_DIR=/opt/amn2
AMN2_RUN_PREFLIGHT=0
AMN2_SYNC_SERVER_CONFIG=1
AMN2_REQUIRE_SERVER_DB_SYNC=1
AMN2_SERVER_NAME=local
```

Expected safe smoke result:

```text
VPS verdict: pass
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

## What to return after the real run

Allowed:

- `api-smoke-safe-summary.txt`;
- `api-smoke-result.json`;
- `api-auth-evidence.txt`;
- `api-listener-evidence.txt`;
- `api-audit-evidence.txt`;
- `server-db-sync.txt`;
- `source-update-summary.txt`;
- path to `safe_bundle`.

Forbidden:

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
- full `api-server.log` without manual redaction.

## Decision

```text
decision: keep c8a6363 as package-ready-not-vps-smoked
next gate: real operator read-only VPS update/smoke
controlled-prod readiness: still pending
```
