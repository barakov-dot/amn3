# Integration Status Controlled Prod Update 2026-06-06

Purpose: record the AMN2 read-only integration status update after `1a193b9` passed real VPS smoke, then record the `32d01fd` real VPS read-only smoke result before the next operator controlled-prod readiness check.

This evidence contains no secrets, no `.env`, no `servers.yml`, no raw tokens, no Authorization headers, no token hashes, no private keys, no PSK, no `.conf`, no QR, no `vpn://` links and no full logs.

## Result

```text
status: read-only-vps-smoke-pass
amn2 branch: codex-vps-test-prep
amn2 head: 32d01fd Update integration status for controlled prod
previous VPS-smoked runtime/source: 1a193b9 Add remote partial failure contract, run_id 20260606T154636Z
new AMN3 package: dist/amn2-vps-update-and-smoke-kit-32d01fd.zip
package sha256: BE59AF74001AC4F094C753B565A4E672194D823C4F65B6CB476F4FF01B310807
source zip: dist/amn2-codex-vps-test-prep-32d01fd-source.zip
source sha256: 034753DA7EC42ACF869519F43909EEFDC8A392A5665B2A33C935F8A058CCB99B
operator doc: dist/amn2-vps-update-and-smoke-kit-32d01fd/AMN2_VPS_UPDATE_AND_SMOKE_32d01fd.ru.md
VPS smoke run_id: 20260606T185114Z
VPS smoke safe bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T185114Z.tar.gz
```

## AMN2 Change

`/api/integration/status` now reports the current safe control state:

```text
status: read_only_vps_smoked
api_baseline.stable_head: 1a193b9
api_baseline.integration_status_head: 7764ae7
remote_operation_gate.phase_2: verified_live
controlled_prod_readiness.status: runbook_published
controlled_prod_readiness.decision: pending_operator_evidence
next_gate: operator-only controlled prod readiness checklist
api_baseline.write_routes_enabled: false
remote_operation_gate.write_operations_enabled: false
```

This is a read-only status correction. It does not enable live peer mutations, API write routes, config delivery, public exposure, Local Agent mutations, backup/import/reboot or `config:read`.

## Local Verification

TDD red/green:

```text
RED before service update: 3 failed, 4 passed
GREEN focused: 7 passed, 2 warnings
GREEN adjacent smoke/security: 26 passed, 1 warning
```

Focused command:

```text
tests/services/test_integration_status_service.py
tests/api/test_api_integration_status.py
tests/web/test_web_integration_status.py
```

Adjacent command:

```text
tests/api/test_smoke.py
tests/security/test_surface_policy.py
tests/security/test_surface_policy_bindings.py
```

Expected warning noise:

```text
StarletteDeprecationWarning from testclient/httpx
Windows pytest cache cleanup/access warning
```

Package verification:

```text
package checksum: passed
source checksum: passed
source forbidden entry scan: 0
shell script BOM check: absent
test extract: passed
```

## VPS Read-Only Smoke

Operator safe evidence:

```text
VPS verdict: pass
run_id: 20260606T185114Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260606T185114Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T185114Z.tar.gz
```

Route smoke:

```text
checked_routes: 5
status: passed
servers: 200, forbidden_markers=[]
integration_status: 200, forbidden_markers=[]
server_summary: 200, forbidden_markers=[]
metrics_summary: 200, forbidden_markers=[]
users_summary: 200, forbidden_markers=[]
```

## Safety

```text
VPS touched during this local update/package build: no
VPS_APPLY_ENABLED=true used: no
apply-peer --apply used: no
revoke-peer --apply used: no
public web/API exposure enabled: no
broad API/config/agent/backup surfaces unlocked: no
```

## Operator Next

`32d01fd` is now the read-only VPS-smoked runtime/source baseline. Continue the controlled-prod readiness checklist in:

```text
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
```

This next gate still does not authorize public prod, live peer mutations, broad API/config/agent/backup surfaces or secret-bearing evidence.
