# Phase 5 P5-C007 live update/smoke 9bff807

Date: 2026-06-12.

Status: `live-update-smoke-pass`.

Scope: named live update/smoke gate for the disposable test VPS.

Target identity: operator-local SSH target, redacted from evidence.

## Decision

```text
task_id: P5-C007
scope: named live update/smoke gate
target_class: disposable test VPS
AMN2_source_commit: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
AMN2_source_commit_short: 9bff807
package: dist/amn2-vps-update-and-smoke-kit-9bff807.zip
package_sha256: 882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9
source_sha256: 5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD
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
source_overlay_commit_before: de2557639cd3853e6973002be3cab24033d2f722
web_active_before: active
bot_active_before: active
login_http: 200
tcp_3030_loopback: yes
tcp_3040_absent: yes
tcp_80_absent: yes
tcp_443_absent: yes
```

## Package Upload And Verify

```text
package_upload: passed after one retry
package_sha_check: passed
source_sha_check: passed
package_extract_status: passed
package_entries: 5
```

## Source Overlay

```text
source_update_run_id: 20260612T180725Z
source_update_status: passed
target: /opt/amn2
source_commit: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
source_sha: 5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD
python: Python 3.12.3
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
permission_strategy: target-root-metadata-preserved
copied_root_entries: 9
safe_log_dir: /opt/amn2/vps-smoke/source-update-20260612T180725Z
```

## Read-Only API Smoke

```text
api_smoke_run_id: 20260612T184701Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260612T184701Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260612T184701Z.tar.gz
```

## Service Restart And Readiness

Initial readiness check three seconds after restart returned `web_login_http=000`
with an empty listener snapshot. A repeat check after ten seconds passed.

```text
restart_after_source_overlay: passed
web_active: active
bot_active: active
web_login_http_after_wait: 200
source_overlay_commit_after: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
```

Permissions after source overlay:

```text
/opt/amn2: drwxr-x--- root:amneziya
/opt/amn2/app: drwxr-x--- root:amneziya
/opt/amn2/.env: -rw-r----- root:amneziya
/opt/amn2/data: drwxrwxr-x root:amneziya
/opt/amn2/logs: drwxrwxr-x root:amneziya
```

Final listener snapshot:

```text
127.0.0.1:3030: listening
3040: absent after smoke
80: absent on remote listener snapshot
443: absent on remote listener snapshot
```

External HTTP probes from the operator workstation:

```text
http://target:3030/login: timeout
http://target:3040/api/servers: timeout
http://target:80/: empty reply from server
remote ss listener for 80/443: absent
```

The public TCP/HTTP-80 behavior appears outside the AMN2 listener process and
was not introduced by this gate. It should be treated as an operator-network or
provider-edge artifact unless a separate network exposure investigation is
opened.

## Findings

1. SSH transport had intermittent banner exchange timeouts/refusals during the
   gate. Waiting between attempts restored access. The live AMN2 operations that
   did run completed successfully.
2. Web readiness immediately after service restart needed more than three
   seconds. A repeat check after ten seconds returned `/login` HTTP `200`.
3. The corrected source-overlay apply script preserved target-root metadata and
   service-readable permissions; no manual permission repair was required.
4. Local `Test-NetConnection` produced ambiguous TCP results for public ports,
   but remote listener evidence showed AMN2 web/admin remained loopback-only and
   API `3040`, `80` and `443` had no remote listener.

## Boundary

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
P5-C007 Named live update/smoke gate for AMN2 9bff807
```

Remaining default local-only active work: none.

## Next Recommendation

`P5-O001` operator-only post-update UI smoke for AMN2 `9bff807`: read-only
web/admin tunnel walkthrough and bot/service-mode sanity checks, with no config
delivery, write API, peer/user mutation or public exposure.
