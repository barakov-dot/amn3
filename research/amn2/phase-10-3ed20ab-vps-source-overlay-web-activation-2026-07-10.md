# Phase 10 3ed20ab VPS source overlay and web activation

Date: 2026-07-10.

Status: `completed-pass-private-loopback`.

## Source Overlay

```text
source_overlay_before=e7f6246
source_overlay_after=3ed20ab
package_sha_check=passed
source_sha_check=passed
source_update_run_id=20260710T081550Z
source_update_status=passed
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260710T081550Z
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

## Loopback API Smoke

```text
run_id=20260710T081622Z
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
safe_evidence_dir=/opt/amn2/vps-smoke/api-loopback-20260710T081622Z
```

## Web Activation Diagnosis

The installed unit was enabled but inactive. Its service identity was
`amneziya:amneziya`, while `/opt/amn2`, source, virtual environment, database,
`.env` and `servers.yml` were all `root:root` with restrictive modes. Initial
start therefore entered an auto-restart loop with `status=200/CHDIR`.

The loop was stopped before repair. A permission metadata snapshot was written
on the VPS without file contents. The targeted repair:

- granted group read/execute to `amneziya` for `/opt/amn2`, `app` and `venv`;
- kept `.env` and `servers.yml` private as `root:amneziya 0640`;
- assigned documented writable runtime directories `data`, `logs`, `backups`
  and `config_templates` to `amneziya:amneziya`;
- did not change either product-write flag.

Service-user toolchain and import checks then passed.

## Stale Process Reconciliation

A manual root web process from 2026-06-21 still occupied loopback port `3030`
from an abandoned SSH session and used a deleted Python executable. It served an
old route set while the new systemd unit failed to bind. The systemd restart loop
was stopped, the stale process received graceful `TERM`, and port `3030` became
free before the unit was started again.

## Final Acceptance

```text
systemd_service=amneziya-web.service
service_user=amneziya
service_group=amneziya
active_state=active
sub_state=running
result=success
source_overlay=3ed20ab
login_http=200
operator_route_unauth_http=303
operator_route_mounted=yes
listener=127.0.0.1:3030
VPS_APPLY_ENABLED=safe_or_unset
OPERATOR_DEVICE_CREATE_ENABLED=safe_or_unset
local_ssh_tunnel=127.0.0.1:3030
local_tunnel_login_http=200
```

The unauthenticated `303` confirms the privacy fix and mounted new route; no
authenticated apply was attempted.

## Boundary

Performed: package upload, source-only overlay, read-only loopback smoke,
targeted runtime permission repair, graceful stale-process reconciliation,
private loopback web service activation and local SSH tunnel setup.

Not performed: peer/user creation or revoke, config generation/delivery,
enabling either write gate, Android TV import/connect, device `8` mutation,
public exposure, firewall/reverse-proxy/TLS changes, bot service start, Telegram
action, backup/import/reboot or secret publication.

## Next Product Slice

```text
START_PHASE10_INTEGRATION_API_KEY_REGISTRY_SLICE
```

Build scoped, owner-bound, expiring, rotatable and audited integration
credentials before connecting them to the Telegram operator workflow.
