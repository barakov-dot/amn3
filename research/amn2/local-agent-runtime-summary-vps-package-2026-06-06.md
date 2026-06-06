# Local Agent Runtime Summary VPS Package Evidence

Date: 2026-06-06.

Status: package-ready, not VPS-smoked.

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

## Decision

Result: `package-ready-not-vps-smoked`.

Next operator action, if continuing on the current stable head, is read-only VPS update/smoke with `dist/amn2-vps-update-and-smoke-kit-c8a6363.zip` and `VPS_APPLY_ENABLED=false`.

The last VPS-smoked runtime/source remains `32d01fd`, `run_id=20260606T185114Z`, until this package is applied and passes read-only smoke.
