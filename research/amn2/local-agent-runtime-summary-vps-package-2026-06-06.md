# Local Agent Runtime Summary VPS Package Evidence

Date: 2026-06-06.

Status: package-ready, then read-only VPS-smoked.

## Package

```text
AMN2 head: c8a6363 Add Local Agent runtime summary mapper
package: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
package sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
operator doc: dist/amn2-vps-update-and-smoke-kit-c8a6363/AMN2_VPS_UPDATE_AND_SMOKE_c8a6363.ru.md
```

## Local Verification

AMN2 code verification before stable push:

```text
python -m pytest tests/agent/test_runtime_summary.py tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
result: 37 passed, 1 warning in 1.79s

python -m pytest -q
result: 619 passed, 1 warning in 63.89s
```

Package verification:

```text
package SHA matched .sha256.txt
source SHA matched .sha256.txt
source_entries: 294
forbidden source entries: none
required source entries: present
test extraction: passed
no BOM found in kit shell/doc files
```

Required source entries checked:

```text
app/agent/runtime_summary.py
tests/agent/test_runtime_summary.py
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
```

## Safety Boundary

This package does not add API routes, web routes, CLI commands, package scripts that perform VPS writes, or live peer mutation behavior.

It does not unlock:

```text
controlled-prod-ready
public web/API exposure
config:read
/api/clients write CRUD
Local Agent clients/configs/write routes
backup/import/reboot
VPS_APPLY_ENABLED=true
apply-peer --apply
revoke-peer --apply
config delivery
```

No `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, VPN URI payloads, or full logs were published.

## VPS Verification

Real VPS read-only update/smoke passed after this package was applied:

```text
source update run_id: 20260606T202012Z
API smoke run_id: 20260606T202040Z
VPS verdict: pass
server_db_sync_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
safe bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T202040Z.tar.gz
```

Evidence:

```text
research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
```

## Decision

Result: `read-only-vps-smoke-pass`.

`c8a6363` is now the current VPS-smoked runtime/source baseline.

Next operator action is the operator-only controlled-prod readiness decision. This does not unlock public prod, broad write routes, config delivery, backup/import/reboot, Local Agent mutation routes or `VPS_APPLY_ENABLED=true`.
