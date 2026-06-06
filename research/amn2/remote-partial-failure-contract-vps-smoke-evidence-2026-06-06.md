# Remote Partial-Failure Contract VPS Smoke Evidence 2026-06-06

Purpose: record the real VPS read-only update/smoke result for AMN2 stable head `1a193b9 Add remote partial failure contract`.

This evidence intentionally includes only the operator-provided safe summary and route result. It excludes `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://` links and full logs.

## Result

```text
status: read-only-vps-smoke-pass
amn2 branch: codex-vps-test-prep
amn2 head: 1a193b9 Add remote partial failure contract
package: dist/amn2-vps-update-and-smoke-kit-1a193b9.zip
package sha256: 48530E59618C413BF8B298CD01801D28DD1AA6E144EAD946EF5BCF303BE56533
source zip: dist/amn2-codex-vps-test-prep-1a193b9-source.zip
source sha256: 8FA2E86FF056A4BA0DE5BC3F913EF33DFC2CC9EF34DDCDC03B0EA09FAD655AEC
run_id: 20260606T154636Z
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260606T154636Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260606T154636Z.tar.gz
```

## Safe Summary

```text
VPS verdict: pass
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
```

## API Smoke Result

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
VPS_APPLY_ENABLED=true used: no
apply-peer --apply used: no
revoke-peer --apply used: no
live peer mutation performed: no
broad API/config/agent surfaces unlocked: no
public web/API exposure performed: no
```

This establishes `1a193b9` as the latest VPS-smoked runtime/source. The previous VPS-smoked package `568c611` remains historical evidence.
