# Phase 6 P6-C009 live update/smoke c46f664

Date: 2026-06-13.

Status: `live-update-smoke-pass`.

Scope: named live apply/smoke gate for the current disposable VPS.

Target: operator-provided disposable VPS `89.185.80.166`.

## Decision

```text
task_id: P6-C009
scope: named live apply/smoke gate
target_class: disposable test VPS
AMN2_source_commit: c46f664762d7774756b88db8d4e1ebc038b20bb5
AMN2_source_commit_short: c46f664
package: dist/amn2-vps-update-and-smoke-kit-c46f664.zip
package_sha256: 5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE
source_sha256: 5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248
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
hostname: 166780.ip-ptr.tech
amn2_dir: present
env_file: present
source_overlay_commit_before: b3102db250da7ca9aef78ca095602187d0efc462
web_unit_before: inactive
bot_unit_before: inactive
login_http_before: 200
runtime_mode_before: manual python processes
listener_3030_before: 127.0.0.1:3030
listener_3040_before: absent
listener_80_before: absent
listener_443_before: absent
vps_apply_env_before: false
target_package_dir_exists: no
target_package_zip_exists: no
```

SSH access used the operator-local project key
`codex_amn2_target_20260608`. No secret material from the key or target was
published.

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
AMN2_VPS_UPDATE_AND_SMOKE_c46f664.ru.md
amn2_api_loopback_smoke.sh
amn2_apply_source_zip.sh
amn2-codex-vps-test-prep-c46f664-source.zip
amn2-codex-vps-test-prep-c46f664-source.zip.sha256.txt
```

## Source Overlay

```text
source_update_run_id: 20260613T173232Z
source_update_status: passed
target: /opt/amn2
source_commit: c46f664762d7774756b88db8d4e1ebc038b20bb5
source_sha: 5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260613T173232Z
source_overlay_commit_after: c46f664762d7774756b88db8d4e1ebc038b20bb5
vps_apply_env_after: false
```

## Runtime Restart And Readiness

The VPS runtime remains in manual process mode rather than active systemd units.

The first restart attempt stopped the old manual web/bot processes but then
aborted before starting new processes because its process filter still matched
the live SSH shell chain. The runtime was immediately checked, then started in
the same manual mode with explicit loopback web bind.

```text
old_manual_processes_stopped: yes
first_restart_started_new_processes: no
transient_login_http_after_first_restart: 000
```

Manual runtime was then started successfully:

```text
manual_runtime_run_id: 20260613T173638Z
restart_status: started
web_alive: yes
bot_alive: yes
login_http_after_restart: 200
source_overlay_commit_after_restart: c46f664762d7774756b88db8d4e1ebc038b20bb5
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

The smoke was run with `AMN2_SERVER_NAME=local`, matching this target's
`servers.yml` server name.

```text
api_smoke_run_id: 20260613T173738Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260613T173738Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260613T173738Z.tar.gz
post_smoke_overlay_commit: c46f664762d7774756b88db8d4e1ebc038b20bb5
```

## Final State

```text
login_http_final: 200
source_overlay_commit_final: c46f664762d7774756b88db8d4e1ebc038b20bb5
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
http://89.185.80.166:3030/login: 000
http://89.185.80.166:3040/api/servers: 000
http://89.185.80.166:80/: 000
```

Remote listener evidence shows AMN2 did not bind public `3030`, `3040`, `80`
or `443`.

## Boundary

The gate performed:

- SSH to the disposable test VPS;
- package upload to `/root`;
- package and source checksum verification;
- scoped package extraction under `/root/amn2-vps-update-and-smoke-kit-c46f664`;
- source overlay update of `/opt/amn2` to AMN2 `c46f664`;
- AMN2 manual web/bot runtime restart;
- read-only loopback API smoke;
- safe listener/runtime/external-probe evidence capture.

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
- Telegram token use by Codex, live bot send or Telegram profile mutation;
- upstream/GPL code copy.

## Follow-Up

Add cosmetic follow-up:

```text
P6-X003 Package runbook escaping hygiene
```

Reason: the operator doc inside the already-smoked `c46f664` zip contains a few
PowerShell-generated control characters where inline backticks were intended.
The apply/smoke scripts, checksums and smoke result are not affected. Do not
rewrite the smoked package artifact after this gate, because that would change
checksum evidence.

Status update: this follow-up is closed by
`research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md`.

## Active Plan Update

Remove from active Phase 6 plan:

```text
P6-C009 Named live apply/smoke gate for c46f664
```

Latest VPS-smoked/package head is now:

```text
c46f664 Add public taxonomy cleanup checklist
```

Remaining active Phase 6 plan:

```text
critical_default: none
critical_gated_deferred:
  - P6-C001 Public exposure gate
  - P6-C002 Config delivery gate
  - P6-C003 Write API production gate
  - P6-C004 Production backup/restore/import gate
  - P6-C007 Destructive cleanup/reinstall gate
  - VPS-REBUILD-001 destructive rebuild
  - Local Agent write/config routes
  - Production peer/user mutation
normal:
  - P4-PRVTPRO-REFRESH-003-LIVE live probes/actions, carried from Phase 4, gated
cosmetic: none after P6-X003
```

## Next Recommendation

Recommended next choice:

```text
Phase 6 closeout packet + next-chat handoff + fresh installer backlog grooming
```

This is docs-only by default. It must not open live/destructive/public/config or
write gates.
