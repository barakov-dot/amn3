# Phase 5 P5-C010 live update/smoke 2215761

Date: 2026-06-13.

Status: `live-update-smoke-pass`.

Scope: named live update/smoke gate for the disposable test VPS.

Target identity: operator-local SSH target, redacted from evidence.

## Decision

```text
task_id: P5-C010
scope: named live update/smoke gate
target_class: disposable test VPS
AMN2_source_commit: 221576169a84bbf662114c564e83c41fba0091b5
AMN2_source_commit_short: 2215761
package: dist/amn2-vps-update-and-smoke-kit-2215761.zip
package_sha256: 6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44
source_sha256: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
result: live-update-smoke-pass
VPS_APPLY_ENABLED: false
public_exposure_changed: no
config_delivery_performed: no
write_api_enabled: no
Local_Agent_mutation: no
backup_import_reboot: no
production_peer_user_mutation: no
destructive_provider_action: no
```

## Preflight

The first plain SSH attempt without the target key failed with `Permission denied`.
Using the dedicated operator-local target key, the next attempt timed out once on
port 22 and then succeeded after a short wait. This matches the intermittent SSH
transport behavior recorded in `P5-C007`.

```text
ssh_status: connected after retry
amn2_dir: present
env_file: present
vps_apply_env: false
source_overlay_commit_before: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
web_active_before: active
bot_active_before: active
login_http_before: 200
```

## Package Upload And Verify

```text
package_upload: passed
package_sha_check: passed
source_sha_check: passed
package_extract_status: passed
package_entries: 5
```

Package entries on the target:

```text
AMN2_VPS_UPDATE_AND_SMOKE_2215761.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-2215761-source.zip
amn2-codex-vps-test-prep-2215761-source.zip.sha256.txt
```

## Source Overlay

```text
source_update_run_id: 20260613T045004Z
source_update_status: passed
target: /opt/amn2
source_commit: 221576169a84bbf662114c564e83c41fba0091b5
source_sha: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260613T045004Z
source_overlay_commit_after: 221576169a84bbf662114c564e83c41fba0091b5
vps_apply_env_after: false
```

## Service Restart And Readiness

```text
restart_after_source_overlay: passed
web_active_after_restart: active
bot_active_after_restart: active
web_login_http_after_wait: 200
source_overlay_commit_after_restart: 221576169a84bbf662114c564e83c41fba0091b5
```

## Read-Only API Smoke

```text
api_smoke_run_id: 20260613T045107Z
VPS_verdict: pass
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260613T045107Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260613T045107Z.tar.gz
```

## Final State

```text
web_active_final: active
bot_active_final: active
web_login_http_final: 200
source_overlay_commit_final: 221576169a84bbf662114c564e83c41fba0091b5
vps_apply_env_final: false
```

Final remote listener snapshot:

```text
127.0.0.1:3030: listening
3040: absent on remote listener snapshot
80: absent on remote listener snapshot
443: absent on remote listener snapshot
```

External HTTP probes from the operator workstation:

```text
http://target:3030/login: empty reply / 000
http://target:3040/api/servers: empty reply / 000
http://target:80/: empty reply / 000
```

Remote listener evidence shows AMN2 did not bind public `3030`, `3040`, `80`
or `443`. Treat the external empty-reply behavior as provider/network edge
behavior unless a separate network exposure investigation is opened.

## Boundary

The gate performed:

- SSH to the disposable test VPS;
- package upload to `/root`;
- package and source checksum verification;
- scoped package extraction under `/root/amn2-vps-update-and-smoke-kit-2215761`;
- source overlay update of `/opt/amn2` to AMN2 `2215761`;
- AMN2 web/bot service restart;
- read-only loopback API smoke.

The gate did not perform:

- `VPS_APPLY_ENABLED=true`;
- peer apply/revoke/sync;
- `/api/clients` write CRUD;
- API `config:read`;
- config delivery, `.conf`, QR or `vpn://`;
- public web/admin exposure;
- public API `3040`;
- domain, HTTPS, reverse proxy or firewall changes;
- Local Agent write/config mutations;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider action;
- secret-bearing evidence publication;
- Telegram token use, live bot send or Telegram profile mutation.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-C010 Named live update/smoke gate for AMN2 2215761
```

Remaining default Phase 5 plan:

```text
critical_default: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Deferred/gated work remains not executed:

```text
VPS-REBUILD-001: critical destructive, not executed, defer.
write API: critical gated, not executed.
config delivery: critical gated, not executed.
public exposure: critical gated, not executed.
P4-PRVTPRO-REFRESH-003 live probes/actions: normal gated, not executed; safe design boundary and local cached display are closed.
```

## Next Recommendation

Recommended next choice:

```text
P5-D001 Operator-only pilot acceptance and Phase 6 entry decision
```

`P5-D001` is a local/docs decision checkpoint: accept the current private
operator-only state, decide whether Phase 6 public/self-service/productization
should open, and keep write API, config delivery, public exposure and
destructive rebuild behind their own named gates.
