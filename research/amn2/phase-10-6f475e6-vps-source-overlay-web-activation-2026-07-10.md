# Phase 10 6f475e6 VPS source overlay and web activation

Date: 2026-07-10.

Status: `completed-pass-private-loopback`.

## Source Overlay

```text
source_overlay_before=3ed20ab
source_overlay_after=6f475e6
package_sha_check=passed
source_sha_check=passed
source_update_run_id=20260710T172523Z
source_update_status=passed
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260710T172523Z
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

The tracked-source overlay preserved `.env`, `servers.yml`, `data`, `venv` and
the existing service-readable permission model.

## Loopback API Smoke

```text
run_id=20260710T172557Z
VPS_verdict=pass
server_db_sync_status=passed
api_ready_status=passed
api_smoke_status=passed
auth_status=passed
missing_bearer_http=401
wrong_scope_http=403
revoked_token_http=401
listener_status=passed
audit_status=passed
safe_evidence_dir=/opt/amn2/vps-smoke/api-loopback-20260710T172557Z
```

The smoke credential was generated with hidden raw material and revoked by the
existing smoke lifecycle. No operator/product integration credential was
issued.

## Private Web Activation

```text
systemd_service=amneziya-web.service
service_user=amneziya
active_state=active
listener=127.0.0.1:3030
login_http=200
registry_unauth_http=303
registry_route_mounted=true
rotate_route_mounted=true
integration_columns=true
VPS_APPLY_ENABLED=safe_or_unset
OPERATOR_DEVICE_CREATE_ENABLED=safe_or_unset
local_ssh_tunnel_login_http=200
```

The `303` confirms that the private registry remains session protected. Route
and schema checks returned booleans only; no token metadata, hash, raw token,
Authorization header or database row values were read into evidence.

## Boundary

Performed: checksum-bound package upload, tracked source overlay, read-only API
smoke, controlled private web service restart and local tunnel acceptance.

Not performed: product credential issue/rotate/revoke, peer/user mutation,
config generation/delivery, Android TV import/connect, device `8` mutation,
public exposure, firewall/reverse-proxy/TLS change, bot service start, live
Telegram action, backup/import/reboot or secret publication.

## Next Product Slice

```text
START_PHASE10_TELEGRAM_OPERATOR_READ_ONLY_STATUS_SLICE
```

Implement and test a local-only authorized Telegram operator aggregate status
workflow without starting the live bot or opening Telegram/public/VPS write
gates.
