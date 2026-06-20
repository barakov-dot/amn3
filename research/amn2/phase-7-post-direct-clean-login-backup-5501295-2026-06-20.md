# AMN2 Phase 7 Post-Direct-Clean Login And Backup Evidence

Date: 2026-06-20.

Status: `completed-login-verified-backup-create-verify`.

Gate: `P7-C004d + P7-C006b`.

Scope:

- loopback admin login verification after `P7-C004c` direct clean install;
- backup create and verify only for the current AMN2 `5501295` clean state.

Explicitly out of scope:

- restore/import/reboot/download;
- provider mutation;
- public exposure or public listener change;
- config delivery;
- write execution;
- Local Agent mutation;
- Telegram action;
- secret-bearing output.

## Inputs

```text
Target VPS: 89.185.80.166
AMN2 expected source overlay: 55012958ff6b8338254f3f68dfe6779f4bc56f5d
AMN2 expected short overlay: 5501295
Transcript: tmp/p7-c004d-c006b-login-backup-5501295-20260620T061005Z.log
Remote safe evidence dir: /opt/amn2/vps-smoke/p7-c004d-c006b-login-backup-20260620T061005Z
```

The operator entered the web admin username/password only in the local
PowerShell prompt. Secret values were not printed.

## Runtime State

```text
source_overlay_commit=55012958ff6b8338254f3f68dfe6779f4bc56f5d
source_overlay_match=yes
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
web_runtime=/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
listener=127.0.0.1:3030
```

Safe env flags:

```text
app_secret_presence=present
web_admin_username_presence=present
web_admin_hash_presence=present
web_admin_session_key_presence=present
vps_apply_enabled=false
local_agent_enabled=false
web_admin_host=127.0.0.1
web_admin_port=3030
server_name=local
secret_values_printed=false
```

## Loopback Admin Login

```text
http://127.0.0.1:3030/login 200
http://127.0.0.1:3030/ 303
login_get_http=200
login_get_has_csrf=yes
login_get_set_cookie=yes
login_post_http=303
login_post_location=/
login_post_has_invalid_credentials=no
login_post_set_cookie=yes
dashboard_after_login_http=200
dashboard_after_login_has_login_form=no
loopback_admin_login_status=passed
secret_values_printed=false
```

Earlier helper retries exposed two helper-only issues that were fixed without
changing AMN2 product code:

- the login helper initially used a too-narrow CSRF extraction pattern;
- the backup helper initially tried to `source` the whole `.env`, which is
  unsafe for password hashes containing shell metacharacters.

The final successful helper parsed only the required `APP_SECRET_KEY` value for
the backup process and did not print it.

## Backup Create And Verify

Safe DB inventory before backup:

```text
db_present=True
db_bytes=147456
users_count=0
devices_count=0
servers_count=1
api_tokens_count=2
admin_actions_count=6
db_rows_printed=false
```

Backup result:

```text
app_secret_loaded_into_process=yes
app_secret_value_printed=false
backup_create_exit_code=0
backup_create_status=passed
backup_verify_exit_code=0
backup_verify_status=passed
backup_artifact_basename=amneziya-backup-20260620T061102Z.tar.enc
backup_artifact_bytes=204900
backup_artifact_sha256=f8e0591db75e8ec9ce58f4fa9d71972d577e1ec103194d1943a626aa9b156b97
backup_artifact_mode=644
backup_output_dir=/opt/amn2/backups/p7-c006b-post-direct-clean-5501295-20260620T061005Z
backup_artifact_count=1
backup_artifact_contents_printed=false
```

The encrypted backup artifact stayed on the VPS and was not downloaded.

## Closed External Probes

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Guard Results

```text
loopback_admin_login_verified=true
backup_create_performed=true
backup_verify_performed=true
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
p7_c004d_c006b_status=completed_login_verified_backup_create_verify
remote_p7_c004d_c006b_exit_code=0
```

## Conclusion

`P7-C004d + P7-C006b` is closed for AMN2 `5501295`.

The direct clean installer RC now has post-clean admin login evidence and a
fresh post-direct-clean backup create+verify artifact. AMN2 remains
loopback-only on the disposable VPS, with public probes closed and
`VPS_APPLY_ENABLED=false`.

Residual `P7-C006` restore/import/download/reboot/DR/provider-restore scopes
remain exact named gates only.
