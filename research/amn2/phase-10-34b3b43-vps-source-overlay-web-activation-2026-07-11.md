# Phase 10 34b3b43 VPS source overlay and web activation

Date: 2026-07-11.

Status: `completed-pass-private-loopback`.

## Approval And Preflight

The operator explicitly approved the selected
`UPLOAD -> APPLY_WITH_SNAPSHOT_AND_ROLLBACK -> READ_ONLY_SMOKE` sequence.

```text
source_overlay_before=6f475e6
candidate=34b3b43
web_before=active
bot_before=inactive
VPS_APPLY_ENABLED=safe
OPERATOR_DEVICE_CREATE_ENABLED=safe
listener_before=127.0.0.1:3030
public_listener_before=false
login_before=200
disk_available_kb=3231000
collision_paths=false
```

## Upload And Rollback Bundle

```text
remote_package_sha=matched
remote_source_sha=matched
package_extract=passed
rollback_dir=/root/amn2-rollbacks/34b3b43-20260711T054507Z
rollback_dir_mode=0700
rollback_source_mode=0600
rollback_database_mode=0600
rollback_overlay=6f475e6
rollback_tracked_root_count=10
rollback_source_sha=2d8f37bb12e3d94b8193f48c1f0b50405b964f3598c11125fc3084312f5157ca
rollback_database_sha=14965ab1dc925af0ce419082f9c6ccb00757d429a11f882cf5a4344c5c226e84
rollback_database_integrity=ok
```

The private rollback files remain on the VPS and were not copied into Git or
evidence. Only safe paths, modes, hashes and integrity status are recorded.

## Source Overlay

The first invocation attempt stopped before executing the script because a
Windows CR character reached the remote command stream. It changed no source.
The repeated command normalized stdin to LF and completed successfully.

```text
source_overlay_after=34b3b43
source_update_run_id=20260711T054627Z
source_update_status=passed
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260711T054627Z
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
rollback_triggered=false
```

## Read-Only API Smoke

```text
run_id=20260711T054705Z
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
api_3040_closed=true
safe_evidence_dir=/opt/amn2/vps-smoke/api-loopback-20260711T054705Z
```

The smoke credential lifecycle remained internal to the script. No raw token,
hash or Authorization header was returned into evidence.

## Private Web Activation

The first immediate readiness probe after restart saw systemd active before
the listener was ready and returned HTTP `000`. The bounded retry then passed;
rollback was not required.

```text
systemd_service=amneziya-web.service
service_user=amneziya
active_state=active
exec_main_status=0
restart_count=0
listener=127.0.0.1:3030
unexpected_public_listener=false
login_http=200
registry_unauth_http=303
telegram_operator_callbacks_present=true
integration_surface_policy_bound=true
bot_service=inactive
rollback_database_integrity_after=ok
```

## Boundary

Performed: checksum-bound private package upload, private tracked-source and
SQLite rollback backup, tracked source overlay, read-only API smoke and
controlled private web restart.

Not performed: Telegram bot activation/send/polling, Telegram token use,
credential issue/rotate/revoke, peer/user mutation, config generation/delivery,
Android TV device `8` action, public exposure, firewall/reverse-proxy/TLS
change, reboot, provider action, secret publication or rollback restore.

## Next Gate

```text
START_PHASE10_PRIVATE_TELEGRAM_BOT_RUNTIME_GATE_REVIEW
```

Review bot token/network/service readiness and rollback independently. Do not
start the bot or perform a live Telegram API call until that gate is approved.
