# AMN2 Phase 7 P7-C006 Backup-Only Evidence

Дата: 2026-06-19.

Статус: `completed-backup-only-create-verify-no-restore-import-reboot`.

Gate: `P7-C006 backup-only evidence gate`.

Target VPS: `89.185.80.166`.

AMN2 source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

## Scope

Оператор открыл gate:

```text
Открываю P7-C006 backup-only evidence gate для b121865 на текущем disposable VPS 89.185.80.166. Без restore/import/reboot.
```

Разрешённый scope:

- create backup artifact;
- verify backup artifact;
- record secret-safe metadata only.

Explicitly excluded:

- restore apply;
- archive import apply;
- reboot;
- destructive migration;
- remote backup download;
- service restart;
- public exposure;
- write API enablement;
- Local Agent mutation;
- production peer/user mutation;
- Telegram action.

## Attempt 1

Transcript:

```text
tmp/p7-c006-backup-only-evidence-20260619T170657Z.log
```

Result:

```text
backup_command_exit_code=1
backup_files_before=1
backup_files_after=1
backup_artifact_count=0
backup_only_status=failed
secret_values_printed=false
```

The failure log was not printed because the safe diagnostic found forbidden
markers in the backup command log:

```text
log_forbidden_marker_count=2
sanitized_tail_skipped=true
```

## Root Cause

Read-only diagnostic transcript:

```text
tmp/p7-c006-backup-failure-diagnostic-20260619T170934Z.log
```

Diagnostic result:

```text
backup_create_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
remote_backup_download_performed=false
service_restart_performed=false
backup_help_exit_code=0
backup_help_forbidden_marker_count=0
module_probe_exit_code=0
p7_c006_failure_diagnostic_status=completed_read_only
```

Local source review of `b121865` showed `app.backup.storage.secret_box_from_env`
requires `APP_SECRET_KEY` from the process environment. The first SSH command
did not load `.env` into the backup process environment, so backup encryption
could not initialize. The root cause was env propagation for backup CLI use, not
missing backup CLI support.

## Successful Retry

Transcript:

```text
tmp/p7-c006-backup-only-retry-20260619T171342Z.log
```

The retry loaded `APP_SECRET_KEY` only inside the remote Python process from the
existing VPS `.env` and did not print the value.

Precondition summary:

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

Runtime/listener summary:

```text
web_runtime=127.0.0.1:3030
public_api_3040_exposed=false
public_80_exposed=false
public_443_exposed=false
```

Safe inventory:

```text
db_present=True
db_bytes=172032
users_count=1
devices_count=2
servers_count=1
api_tokens_count=24
admin_actions_count=58
```

Backup result:

```text
app_secret_loaded_into_process=yes
app_secret_value_printed=false
backup_create_status=passed
backup_verify_status=passed
backup_output_dir=/opt/amn2/backups/p7-c006-retry-20260619T171342Z
backup_artifact_count=1
backup_artifact_basename=amneziya-backup-20260619T171402Z.tar.enc
backup_artifact_bytes=245860
backup_artifact_sha256=9947bf97b242e46d86cf7cbf41ed7ffb8cec8a9bae728a71f3095c86d50b73c9
backup_artifact_mode=600
backup_artifact_contents_printed=false
remote_backup_download_performed=false
```

Manifest safe summary:

```text
manifest_format_version=1
manifest_app=amneziya
manifest_database_kind=sqlite
manifest_includes_count=2
manifest_excludes_count=4
manifest_database_checksum_sha256_present=True
manifest_database_checksum_sha256_printed=false
```

External probes stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Mutation Guard

```text
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
destructive_migration_performed=false
remote_backup_download_performed=false
service_restart_performed=false
public_exposure_performed=false
write_api_enablement_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
telegram_action_performed=false
secret_values_printed=false
p7_c006_backup_only_status=completed_create_verify
```

## Decision

`P7-C006 backup-only evidence gate` is closed as
`completed-backup-only-create-verify-no-restore-import-reboot`.

Remaining `P7-C006` scopes are still not opened:

- restore apply;
- archive import apply;
- remote backup download;
- reboot;
- disaster-recovery drill;
- destructive migration.

Those require separate exact named gates.
