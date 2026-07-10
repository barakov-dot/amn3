# Phase 10 e7f6246 read-only VPS source-overlay smoke

Date: 2026-07-10.

Status: `read-only-vps-smoke-pass`.

Scope: exact continuation gate for the locally verified AMN2 package at
`e7f6246 Harden operator single device creation`.

Target identity: existing operator-managed AMN2 VPS. SSH credentials and private
key material are not recorded in this evidence.

## Gate Boundary

```text
source_commit=e7f6246
package=dist/amn2-vps-update-and-smoke-kit-e7f6246.zip
package_sha256=17988115CEBD7CA5D924300506259CE4DB7161DBB1980D248892E4A7CF7DA72E
source_sha256=FE980BDBC209ED339B33231BCABD42000E2DA6910791DAA8ABA85620A099B0EE
VPS_APPLY_ENABLED=false
peer_creation=false
config_generation=false
config_delivery=false
android_import_connect=false
public_exposure_change=false
service_restart=false
```

## Preflight

```text
ssh_status=connected
amn2_dir=present
source_overlay_before=4326cae
vps_apply_enabled=safe_or_unset
free_space_kb=3178332
```

The first preflight command completed all safety checks but returned exit `1`
because an optional final `awk` formatting expression was escaped incorrectly.
The disk-space check was immediately repeated as a read-only command and passed.
No mutation occurred in the failed command.

## Package And Source Overlay

```text
package_upload=passed
package_sha_check=passed
source_sha_check=passed
package_extract_status=passed
source_update_run_id=20260710T072516Z
source_update_status=passed
source_overlay_after=e7f6246
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260710T072516Z
```

The overlay preserved target runtime data and was applied with
`VPS_APPLY_ENABLED=false`. No service restart was requested.

## Read-Only API Smoke

```text
run_id=20260710T072545Z
VPS_verdict=pass
preflight_status=skipped
server_db_sync_status=passed
api_ready_status=passed
api_smoke_status=passed
auth_status=passed
missing_bearer_http=401
wrong_scope_http=403
revoked_token_http=401
listener_status=passed
audit_status=passed
safe_evidence_dir=/opt/amn2/vps-smoke/api-loopback-20260710T072545Z
safe_bundle=/opt/amn2/vps-smoke/api-loopback-safe-evidence-20260710T072545Z.tar.gz
```

## Final Acceptance

```text
source_overlay_after=e7f6246
vps_apply_enabled=false_or_unset
operator_create_cli=available
android_tv_import_connect=pending_physical_device
device_8_mutated=false
```

## Boundary Result

Performed:

- key-based SSH to the existing AMN2 VPS;
- package/checksum upload under `/root`;
- package and source checksum verification;
- tracked source overlay update from `4326cae` to `e7f6246`;
- loopback API smoke and safe operator CLI availability check.

Not performed:

- peer/user creation, revoke or runtime VPN mutation;
- config generation, delivery, QR or `vpn://` handling;
- Android TV import/connect or handshake acceptance;
- web/API public exposure, firewall, reverse proxy or TLS changes;
- service enable/restart, backup/import/reboot or provider action;
- Telegram token use, bot send or identity mutation;
- publication of secret-bearing output or full logs.

## Next Product Slice

```text
START_PHASE10_OPERATOR_DEVICE_CREATE_WEB_UI_SLICE
```

The private operator web panel should call the same hardened
`AccessService.create_operator_device(...)` contract. It must not add a second
device-creation implementation or open public/self-service writes.
