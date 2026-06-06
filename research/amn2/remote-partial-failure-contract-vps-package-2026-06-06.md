# Remote Partial-Failure Contract VPS Package Evidence 2026-06-06

Purpose: record the AMN3 update+smoke package for AMN2 stable head `1a193b9 Add remote partial failure contract`.

This evidence intentionally excludes `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://` links and full logs.

## Result

```text
status: published-pending-read-only-vps-smoke
amn2 branch: codex-vps-test-prep
amn2 head: 1a193b9 Add remote partial failure contract
package: dist/amn2-vps-update-and-smoke-kit-1a193b9.zip
package sha256: 48530E59618C413BF8B298CD01801D28DD1AA6E144EAD946EF5BCF303BE56533
source zip: dist/amn2-codex-vps-test-prep-1a193b9-source.zip
source sha256: 8FA2E86FF056A4BA0DE5BC3F913EF33DFC2CC9EF34DDCDC03B0EA09FAD655AEC
operator doc: dist/amn2-vps-update-and-smoke-kit-1a193b9/AMN2_VPS_UPDATE_AND_SMOKE_1a193b9.ru.md
```

## Local Verification

```text
AMN2 focused merged stable tests: 70 passed
package checksum: passed
source checksum: passed
source forbidden entry scan: no matches
shell script BOM check: passed
test extract and inner source checksum: passed
```

## Safety

```text
VPS touched: no
live write performed: no
VPS_APPLY_ENABLED=true used: no
apply-peer --apply used: no
revoke-peer --apply used: no
broad API/config/agent surfaces unlocked: no
```

`568c611` remains the latest VPS-smoked runtime/source until the operator runs the read-only smoke for `1a193b9`.

## Operator Next

Use either `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md` or `docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md`.

Return only safe summary/result JSON after the VPS read-only smoke. Do not send secrets or full logs.
