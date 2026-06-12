# Phase 5 P5-C003: live rollout for AMN2 de25576 2026-06-12

Дата: 2026-06-12.

Назначение: выполнить named live rollout gate для disposable test VPS, используя пакет `de25576`, уже собранный в `P5-C001`. Этот gate разрешал только bounded package upload/source overlay, read-only loopback API smoke, service restart/readiness check and safe evidence. Он не открывал public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation or destructive provider actions.

## Decision

```text
task_id: P5-C003
scope: named live rollout gate
target_class: disposable test VPS
target_identity: operator-local SSH key/known_hosts, redacted from evidence
AMN2_source_commit: de2557639cd3853e6973002be3cab24033d2f722
AMN2_source_commit_short: de25576
package: dist/amn2-vps-update-and-smoke-kit-de25576.zip
package_sha256: B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87
source_sha256: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
result: live-rollout-pass-with-permission-repair
VPS_APPLY_ENABLED: false
public_exposure_changed: no
config_delivery_performed: no
write_api_enabled: no
Local_Agent_mutation: no
backup_import_reboot: no
production_peer_user_mutation: no
destructive_provider_action: no
```

## Live Steps

Preflight:

```text
ssh_status: connected
amn2_dir: present
env_file: present
vps_apply_env: false
source_overlay_commit_before: f7f6131
web_active_before: active
bot_active_before: active
listener_before: 127.0.0.1:3030 only
```

Package upload/extract:

```text
package_sha_check: passed
source_sha_check: passed
package_extract_status: passed
package_entries:
- AMN2_VPS_UPDATE_AND_SMOKE_de25576.ru.md
- amn2_api_loopback_smoke.sh
- amn2_apply_source_zip.sh
- amn2-codex-vps-test-prep-de25576-source.zip
- amn2-codex-vps-test-prep-de25576-source.zip.sha256.txt
```

Source overlay:

```text
source_update_run_id: 20260612T054750Z
source_update_status: passed
target: /opt/amn2
source_commit: de2557639cd3853e6973002be3cab24033d2f722
source_sha: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
```

Read-only API smoke:

```text
first_api_smoke_run_id: 20260612T054818Z
first_api_smoke_result: blocked-before-api-start
root_cause: default server name debian-vps-1 was not present in servers.yml
available_server_name: local

passing_api_smoke_run_id: 20260612T054913Z
VPS_verdict: pass
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260612T054913Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260612T054913Z.tar.gz
```

Service restart/readiness:

```text
initial_restart_result: blocked-by-service-permissions
root_cause: source overlay changed /opt/amn2 and tracked source directories to root:root 700, so User=amneziya systemd units failed with status=200/CHDIR
permission_repair_status: passed
permissions_after:
- /opt/amn2: drwxr-x--- root:amneziya
- /opt/amn2/app: drwxr-x--- root:amneziya
- /opt/amn2/.env: -rw-r----- root:amneziya
- /opt/amn2/data: drwxrwxr-x root:amneziya
- /opt/amn2/logs: drwxrwxr-x root:amneziya

restart_after_permission_repair: passed
web_active: active
bot_active: active
web_login_http: 200
source_overlay_commit_after: de2557639cd3853e6973002be3cab24033d2f722
```

Final listener snapshot:

```text
127.0.0.1:3030: listening
public_or_loopback_3040: absent after smoke
tcp_80_443: absent
domain_https_cutover: not changed
reverse_proxy_changed: no
```

## Findings

1. `amn2_api_loopback_smoke.sh` defaulted to `AMN2_SERVER_NAME=debian-vps-1`, while this target uses `local`. Rerunning with `AMN2_SERVER_NAME=local` passed. Future runbooks for this VPS should set the server name explicitly.
2. `amn2_apply_source_zip.sh` inherited a permission-preservation bug: extracting a tar stream rooted at `.` from a staging directory created under `umask 077` can clobber `/opt/amn2` directory permissions. The live repair restored service-mode permissions and services recovered. This needs a local package tooling follow-up before the next package rebuild/apply.

## Boundary

The gate did not perform:

- `VPS_APPLY_ENABLED=true`;
- peer apply/revoke/sync;
- `/api/clients` write CRUD;
- API `config:read`;
- config delivery, `.conf`, QR or `vpn://`;
- public `3030`, public `3040`, TCP `80/443`, domain, HTTPS, reverse proxy or firewall changes;
- Local Agent write/config mutations;
- backup/import/reboot;
- destructive provider action;
- secret-bearing evidence publication.

## Next Recommendation

Recommended next task: `P5-C005` local package tooling fix for source-overlay permission preservation and explicit target server-name runbook defaults. Do this before any future package rebuild/apply. `P5-C004` remains available only if fresh operator secrets/server config must be handed off.
