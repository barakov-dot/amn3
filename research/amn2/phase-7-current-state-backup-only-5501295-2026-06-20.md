# AMN2 Phase 7 P7-C006 Current-State Backup-Only Evidence

Дата: 2026-06-20.

Статус: `completed-current-state-backup-only-create-verify-no-restore-import-reboot`.

Scope:

- Exact named `P7-C006` current-state backup-only evidence gate.
- Target: disposable VPS `89.185.80.166`.
- AMN2 source overlay: `5501295`.
- Create and verify encrypted backup artifact only.
- No restore, import, reboot, provider mutation, remote backup download, service
  restart, public exposure, config delivery, write execution, Local Agent
  mutation, Telegram action or secret-bearing output.

Transcript:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p7-c006-current-state-backup-only-5501295-20260620T050111Z.log
```

## Source And Runtime State

```text
source_overlay_commit=5501295
source_overlay_expected_full=55012958ff6b8338254f3f68dfe6779f4bc56f5d
source_overlay_expected_short=5501295
source_overlay_match=yes
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
web_runtime=127.0.0.1:3030
public_listener_change_performed=false
```

Safe env flags:

```text
app_secret_presence=present
web_admin_username_presence=present
web_admin_hash_presence=present
web_admin_session_key_presence=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
secret_values_printed=false
```

Current-state safe inventory:

```text
db_present=True
db_bytes=155648
users_count=0
devices_count=0
servers_count=1
api_tokens_count=8
admin_actions_count=14
db_rows_printed=false
```

## Backup Evidence

```text
app_secret_loaded_into_process=yes
app_secret_value_printed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_basename=amneziya-backup-20260620T050141Z.tar.enc
backup_artifact_bytes=218552
backup_artifact_sha256=1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2
backup_artifact_mode=600
manifest_format_version=1
manifest_app=amneziya
manifest_database_kind=sqlite
manifest_includes_count=2
manifest_excludes_count=4
manifest_database_checksum_sha256_present=True
manifest_database_checksum_sha256_printed=false
backup_artifact_contents_printed=false
backup_output_dir=/opt/amn2/backups/p7-c006-current-state-5501295-20260620T050111Z
backup_artifact_count=1
```

The backup artifact stayed on the VPS. It was not downloaded.

## Guards

```text
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
provider_action_performed=false
remote_backup_download_performed=false
service_restart_performed=false
public_exposure_performed=false
public_listener_change_performed=false
config_delivery_performed=false
write_execution_performed=false
write_api_enablement_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
telegram_action_performed=false
secret_values_printed=false
p7_c006_current_state_backup_only_status=completed_create_verify
remote_p7_c006_current_state_backup_exit_code=0
```

External probes stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Result

`P7-C006` current-state backup-only evidence for `5501295` is complete. The
remaining `P7-C006` scopes are restore apply, archive import, remote backup
download, reboot, disaster-recovery drill, destructive migration and any
provider restore use, all exact named gates only.
