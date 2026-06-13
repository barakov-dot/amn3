# Phase 6 P6-C006 live update/smoke b3102db

Date: 2026-06-13.

Status: `live-update-smoke-pass`.

Scope: named live apply/smoke gate for the current disposable VPS.

Target identity: operator-local SSH target, redacted from evidence.

## Decision

```text
task_id: P6-C006
scope: named live apply/smoke gate
target_class: disposable test VPS
AMN2_source_commit: b3102db250da7ca9aef78ca095602187d0efc462
AMN2_source_commit_short: b3102db
package: dist/amn2-vps-update-and-smoke-kit-b3102db.zip
package_sha256: B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B
source_sha256: 72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778
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

```text
ssh_status: connected
amn2_dir: present
env_file: present
vps_apply_env: false
source_overlay_commit_before: 221576169a84bbf662114c564e83c41fba0091b5
web_unit_before: inactive
bot_unit_before: inactive
login_http_before: 200
runtime_mode_before: manual python processes
target_package_dir_exists: no
target_package_zip_exists: no
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
AMN2_VPS_UPDATE_AND_SMOKE_b3102db.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-b3102db-source.zip
amn2-codex-vps-test-prep-b3102db-source.zip.sha256.txt
```

## Source Overlay

```text
source_update_run_id: 20260613T154511Z
source_update_status: passed
target: /opt/amn2
source_commit: b3102db250da7ca9aef78ca095602187d0efc462
source_sha: 72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260613T154511Z
source_overlay_commit_after: b3102db250da7ca9aef78ca095602187d0efc462
vps_apply_env_after: false
```

## Runtime Restart And Readiness

The VPS runtime was in manual process mode rather than active systemd units.
The first restart attempt used a broad `pgrep -f` filter and stopped the old
manual web/bot processes before the command aborted because it matched the
command shell text. The runtime was immediately checked and then started in the
same manual mode with explicit loopback web bind.

```text
manual_runtime_run_id: 20260613T154712Z
restart_status: started
web_alive: yes
bot_alive: yes
login_http_after_restart: 200
source_overlay_commit_after_restart: b3102db250da7ca9aef78ca095602187d0efc462
web_bind: 127.0.0.1:3030
```

Final runtime mode:

```text
web_unit_final: inactive
bot_unit_final: inactive
manual_web_process: /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
manual_bot_process: /opt/amn2/venv/bin/python -m app.main
```

## Read-Only API Smoke

The first smoke attempt was blocked before API startup because the script
defaulted to `AMN2_SERVER_NAME=debian-vps-1`, while this target's
`servers.yml` server name is `local`.

```text
blocked_api_smoke_run_id: 20260613T154746Z
blocked_reason: server config DB-only sync failed before API smoke
detail: Server 'debian-vps-1' not found. Available: local
```

The smoke was rerun with `AMN2_SERVER_NAME=local` and passed.

```text
api_smoke_run_id: 20260613T154826Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260613T154826Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260613T154826Z.tar.gz
post_smoke_overlay_commit: b3102db250da7ca9aef78ca095602187d0efc462
```

## Final State

```text
login_http_final: 200
source_overlay_commit_final: b3102db250da7ca9aef78ca095602187d0efc462
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
http://target:3030/login: 000
http://target:3040/api/servers: 000
http://target:80/: 000
```

Remote listener evidence shows AMN2 did not bind public `3030`, `3040`, `80`
or `443`.

## Boundary

The gate performed:

- SSH to the disposable test VPS;
- package upload to `/root`;
- package and source checksum verification;
- scoped package extraction under `/root/amn2-vps-update-and-smoke-kit-b3102db`;
- source overlay update of `/opt/amn2` to AMN2 `b3102db`;
- AMN2 manual web/bot runtime restart;
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
- Telegram token use by Codex, live bot send or Telegram profile mutation.

## Active Plan Update

Remove from active Phase 6 plan:

```text
P6-C006 Final VPS package refresh/apply gate
```

Remaining active Phase 6 plan:

```text
critical_default: none
critical_gated_deferred:
  - P6-C001 Public exposure gate
  - P6-C002 Config delivery gate
  - P6-C003 Write API production gate
  - P6-C004 Production backup/restore/import gate
  - VPS-REBUILD-001 destructive rebuild
  - Local Agent write/config routes
  - Production peer/user mutation
very_important_proposed:
  - P6-I006 Commercial entitlement/audit boundary
normal:
  - P6-N001 Public docs/API taxonomy if public docs are approved
  - P4-PRVTPRO-REFRESH-003-LIVE live probes/actions, carried from Phase 4, gated
simple: none
cosmetic: none
```

## Next Recommendation

Recommended next choice:

```text
P6-C002 + P6-I006 as local-only design/implementation:
short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary.
```

This should not open real config delivery, public exposure, write API, payment
processor integration, Local Agent mutation, production peer/user mutation or
Telegram identity mutation.
