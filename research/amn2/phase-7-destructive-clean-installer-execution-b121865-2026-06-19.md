# AMN2 Phase 7 P7-C004b Destructive Clean Installer Execution

Дата: 2026-06-19.

Статус: `completed-clean-install-loopback-smoke`.

Gate: `P7-C004b destructive clean installer execution gate`.

Target VPS: `89.185.80.166`.

AMN2 source/package: `b121865 Add multi instance conflict model`.

Transcripts:

```text
tmp/p7-c004b-destructive-clean-installer-20260619T173819Z.log
tmp/p7-c004b-recovery-diagnostic-20260619T174511Z.log
tmp/p7-c004b-resume-clean-smoke-20260619T174912Z.log
```

## Scope

Оператор открыл destructive gate через точную фразу:

```text
Открываю P7-C004b destructive clean installer execution gate для b121865 на disposable VPS 89.185.80.166. Разрешаю wipe/reinstall/apply clean installer на этом disposable VPS.
```

Дополнительная final destructive phrase была введена в локальном PowerShell
окне:

```text
DESTROY_AND_CLEAN_INSTALL_B121865_ON_DISPOSABLE_VPS
```

Разрешенный scope:

- stop current AMN2 loopback runtime;
- move old `/opt/amn2` to a root-only quarantine path;
- create clean `/opt/amn2`;
- install verified `b121865` package/source;
- generate fresh secret-safe `.env`;
- create placeholder `servers.yml` for loopback smoke;
- initialize clean DB;
- start loopback web runtime;
- run loopback API smoke;
- record only safe evidence.

Explicitly excluded:

- provider rebuild;
- reboot;
- restore apply;
- archive import apply;
- remote backup download;
- public exposure;
- reverse proxy, TLS, firewall or public listener changes;
- config delivery;
- write API enablement;
- Local Agent mutation;
- production peer/user mutation;
- Telegram API/token/profile/media action;
- secret-bearing evidence output.

## Pre-Destructive Preconditions

Local package verification:

```text
package_path=dist/amn2-vps-update-and-smoke-kit-b121865.zip
package_sha256=364025bd1ae5a23979889a6ded3d78078e1c939f883af277106f9851ce660849
package_sha256_expected=364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849
package_sha256_match=True
```

Remote package/source verification:

```text
package_sha256=364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849
package_sha256_match=yes
package_sha256sum_check=passed
source_zip_sha256=D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647
source_zip_sha256_match=yes
```

Backup prerequisite from `P7-C006` was present and matched:

```text
backup_artifact_present=true
backup_artifact_bytes=245860
backup_artifact_mode=600
backup_artifact_owner=root:root
backup_artifact_sha256=9947bf97b242e46d86cf7cbf41ed7ffb8cec8a9bae728a71f3095c86d50b73c9
backup_artifact_sha256_match=yes
backup_artifact_contents_printed=false
```

## Destructive Execution

Initial remote identity:

```text
os_id=ubuntu
os_version_id=24.04
hostname_static=166780.ip-ptr.tech
old_source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
old_source_overlay_match=yes
```

Destructive runtime-path result:

```text
service_stop_attempted=true
manual_runtime_stop_attempted=true
old_opt_amn2_quarantined=true
old_opt_amn2_quarantine_path=/opt/amn2.pre-p7-c004b-20260619T173819Z
clean_target_created=true
wipe_runtime_path_performed=true
base_packages_installed=true
python3_version=Python 3.12.3
venv_created=true
source_apply_status=passed
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
package_apply_performed=true
env_written=true
servers_yml_written=true
secret_values_printed=false
```

The first execution stopped after `env_written=true` because the local helper
ran a settings validation probe from the wrong working directory and did not
load the new `.env`. This did not require another wipe or another package
apply.

## Recovery Diagnostic

Read-only recovery diagnostic confirmed the clean target state:

```text
wipe_performed=false
package_apply_performed=false
service_restart_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
public_exposure_performed=false
write_api_enablement_performed=false
telegram_action_performed=false
opt_amn2_present=true
opt_amn2_old_quarantine_count=1
old_quarantine_path=/opt/amn2.pre-p7-c004b-20260619T173819Z
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=false
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
settings_load_status=passed
secret_values_printed=false
```

## Resume Smoke

The resume pass did not perform another wipe or package apply:

```text
already_opened_gate=P7-C004b
wipe_performed=false
package_apply_performed=false
provider_rebuild_performed=false
reboot_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
remote_backup_download_performed=false
public_exposure_performed=false
write_api_enablement_performed=false
local_agent_mutation_performed=false
telegram_action_performed=false
config_delivery_performed=false
```

Clean install validation:

```text
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
old_quarantine_count=1
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
source_overlay_match=yes
settings_load_status=passed
WEB_ADMIN_HOST=127.0.0.1
WEB_ADMIN_PORT=3030
SERVER_NAME=local
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
secret_values_printed=false
```

Database and web runtime:

```text
db_initialize_status=passed
db_present=True
db_bytes=147456
web_runtime_start_attempted=true
web_pid=256770
web_login_loopback_http=200
web_runtime_status=passed
```

API loopback smoke:

```text
VPS verdict: pass
run_id: 20260619T174957Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260619T174957Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260619T174957Z.tar.gz
```

Clean DB safe inventory after smoke:

```text
users_count=0
devices_count=0
servers_count=1
api_tokens_count=2
admin_actions_count=6
```

Final runtime/listener summary:

```text
web_runtime=127.0.0.1:3030
public_api_3040_exposed=false
public_80_exposed=false
public_443_exposed=false
bot_runtime_started=false
```

External probes stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Final Status

```text
clean_install_resume_status=completed_loopback_smoke
wipe_runtime_path_performed_in_original_gate=true
clean_install_performed_in_original_gate=true
loopback_web_started=true
loopback_api_smoke_passed=true
bot_runtime_started=false
telegram_api_called=false
public_exposure_performed=false
public_listener_change_performed=false
write_api_enablement_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
config_delivery_performed=false
secret_values_printed=false
remote_safe_evidence_dir=/root/p7-c004b-resume-clean-smoke-20260619T174912Z
```

## Decision

`P7-C004b` is closed as `completed-clean-install-loopback-smoke`.

The disposable VPS now has a clean AMN2 `b121865` install at `/opt/amn2`, with
web/admin bound to loopback and API smoke passing on loopback. The old pre-wipe
runtime path remains quarantined at
`/opt/amn2.pre-p7-c004b-20260619T173819Z` for operator/debug recovery only.

This evidence does not open public exposure, config delivery, write API, Local
Agent mutation, restore/import/reboot, production peer/user mutation or
Telegram identity/profile/media mutation. Those scopes remain separate exact
named gates.

## New Structural Suggestion

The operator reported that a hosting-provider backup is now visible in the
provider console. Suggested inactive candidate:

```text
P7-C006a Provider backup restore-point confirmation
Importance: important
Gate: docs-only/provider-console evidence unless restore is explicitly opened
Scope: record safe provider-console evidence that a restore point exists and is
available; no restore/import/reboot/provider mutation.
```

This suggestion is not active without explicit operator consent.
