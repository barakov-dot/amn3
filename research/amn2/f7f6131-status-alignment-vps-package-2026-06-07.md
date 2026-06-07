# f7f6131 Status Alignment VPS Package 2026-06-07

Date: 2026-06-07.

Purpose: publish an AMN3 update+smoke kit for AMN2 commit `f7f6131 Update integration status for c92 manual prelaunch`.

This is a read-only status-alignment package. It does not introduce a new runtime mode and does not unlock public API, direct public web/admin, write routes, config delivery, Local Agent mutations, backup/import/reboot, or live peer operations.

## Package

```text
amn2 branch: codex-vps-test-prep
amn2 package commit: f7f6131 Update integration status for c92 manual prelaunch
previous VPS-smoked source overlay: c92bd1a Bind web admin systemd to loopback
package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source zip: dist/amn2-codex-vps-test-prep-f7f6131-source.zip
source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
operator doc: dist/amn2-vps-update-and-smoke-kit-f7f6131/AMN2_VPS_UPDATE_AND_SMOKE_f7f6131.ru.md
status: read-only-vps-smoke-pass
VPS source-overlay smoke: passed
VPS smoke evidence: research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
```

## Local Package Checks

```text
kit zip contains: source zip, source sha256, api smoke script, source apply script, operator doc
source zip built with: git archive
runtime files in source zip: not present
forbidden source entries checked: .env, data/, venv/, servers.yml
source contains integration status files: yes
apply script expected commit: f7f6131
apply script expected source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
smoke script expected commit: f7f6131
shell scripts CRLF count: 0
```

## Boundary

Allowed next step:

- apply this source overlay with `VPS_APPLY_ENABLED=false`;
- repeat API loopback smoke on `127.0.0.1:3040`;
- keep the validation VPS in current operator-started manual runtime mode.

Still blocked:

- `VPS_APPLY_ENABLED=true`;
- live peer apply/revoke;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd`/reverse-proxy deployment without a separate gate;
- route expansion to config/write/backup/import/reboot/Local Agent mutations;
- secret-bearing evidence.

## VPS Smoke Evidence

The prepared package was applied to `/opt/amn2` with `VPS_APPLY_ENABLED=false`, then the loopback API smoke was repeated.

```text
source_update_run_id: 20260607T203721Z
source_update_status: passed
source overlay after: f7f6131
api_smoke_run_id: 20260607T203730Z
latest_repeat_api_smoke_run_id: 20260607T204300Z
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
checked_routes: 6
route_status_codes: 200
forbidden_markers: []
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260607T203730Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260607T203730Z.tar.gz
VPS_APPLY_ENABLED: false
```

## Expected Safe Fields

Return only safe summary fields:

The `integration_status_decision` and `service_deployment` values below are the current AMN2 `f7f6131` read-only status labels. They do not authorize service mode on the validation VPS and do not change the current operator-started manual runtime boundary.

```text
source overlay before: c92bd1a
source overlay after: f7f6131
source_update_status: passed
api_smoke_status: passed
checked_routes: 6
listener_status: passed
audit_status: passed
integration_status_current_stable_head: c92bd1a
integration_status_decision: manual-prelaunch-pass-systemd-deferred
manual_runtime_mode: manual
service_deployment: deferred_target_server
VPS_APPLY_ENABLED: false
```

Do not paste `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, backup contents, or full logs.
