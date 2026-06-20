# AMN2 Phase 7 P7-C004c Direct Clean Installer For 5501295

Дата: 2026-06-20.

Статус: `completed-direct-clean-install-5501295-loopback-smoke`.

Target VPS: `89.185.80.166`.

Gate:

```text
P7-C004c direct clean installer execution gate for AMN2 5501295.
```

Scope:

- Destructive clean install from the verified AMN2 `5501295` package on the
  declared disposable VPS.
- Stop current AMN2 loopback runtime.
- Move current `/opt/amn2` to a root-only quarantine path.
- Create clean `/opt/amn2`.
- Install/apply source from verified `5501295` package.
- Generate fresh safe `.env` and placeholder server config.
- Initialize DB.
- Start loopback web runtime.
- Run loopback API smoke.

Not in scope:

- Provider rebuild.
- Reboot.
- Restore/import.
- Remote backup download.
- Public exposure.
- Config delivery.
- Write API enablement or actual installer execution beyond package apply.
- Local Agent mutation.
- Production peer/user mutation.
- Telegram action.
- Public listener change.
- Secret-bearing output.

## Local Package Verification

```text
package_path=dist/amn2-vps-update-and-smoke-kit-5501295.zip
package_present=True
package_sha256=c03d26673ad79d9487a3ed34e9657e0dca10ebc9bb601e429385091f1dfef407
package_sha256_expected=C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407
package_sha256_match=True
package_sha_file_present=True
```

Upload results:

```text
scp_package_exit_code=0
scp_package_sha_exit_code=0
```

## Remote Pre-Wipe Guard

```text
os_id=ubuntu
os_version_id=24.04
hostname_static=166780.ip-ptr.tech
old_source_overlay_commit=5501295
old_source_overlay_expected=55012958ff6b8338254f3f68dfe6779f4bc56f5d
old_source_overlay_match=no
backup_artifact_present=true
backup_artifact_bytes=218552
backup_artifact_mode=600
backup_artifact_owner=root:root
backup_artifact_sha256=1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2
backup_artifact_sha256_match=yes
backup_artifact_contents_printed=false
```

Note: the pre-wipe source overlay file contained short `5501295` while the
guard expected the full commit hash. This was recorded as
`old_source_overlay_match=no`; the package/source verification and final clean
install used the full `55012958ff6b8338254f3f68dfe6779f4bc56f5d` commit and
passed.

Pre-wipe listener state included only loopback AMN2 web on `127.0.0.1:3030`;
no public AMN2 listener was present.

## Package And Source Verification

```text
package_uploaded=true
package_sha256=C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407
package_sha256_expected=C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407
package_sha256_match=yes
package_sha256sum_check=passed
package_extracted=true
source_zip_sha256=DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3
source_zip_sha256_expected=DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3
source_zip_sha256_match=yes
```

## Destructive Install Result

```text
remaining_amn2_processes=0
old_opt_amn2_quarantined=true
old_opt_amn2_quarantine_path=/opt/amn2.pre-p7-c004c-20260620T054656Z
clean_target_created=true
wipe_runtime_path_performed=true
base_packages_installed=true
python3_version=Python 3.12.3
venv_created=true
source_apply_status=passed
source_overlay_commit=55012958ff6b8338254f3f68dfe6779f4bc56f5d
package_apply_performed=true
env_written=true
servers_yml_written=true
secret_values_printed=false
settings_load_status=passed
web_admin_session_secure_flag=False
db_initialize_status=passed
db_present=True
db_bytes=147456
```

Safe env/settings flags were present and kept loopback/private defaults:

```text
telegram_token_presence=present
app_secret_presence=present
web_admin_username_presence=present
web_admin_hash_presence=present
web_admin_session_key_presence=present
vps_apply_enabled=false
local_agent_enabled=false
web_admin_host=127.0.0.1
web_admin_port=3030
server_name=local
```

## Runtime And Smoke

```text
web_runtime_start_attempted=true
web_pid=262994
web_login_loopback_http=200
web_runtime_status=passed
```

API loopback smoke:

```text
VPS verdict: pass
run_id: 20260620T054813Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260620T054813Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260620T054813Z.tar.gz
```

Post-install safe inventory:

```text
db_present=True
db_bytes=147456
users_count=0
devices_count=0
servers_count=1
api_tokens_count=2
admin_actions_count=6
```

Post-install listener state:

- AMN2 web listened on `127.0.0.1:3030`.
- No public AMN2 `3040`, `80` or `443` listener was exposed.

External closed probes:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Final Guard

```text
wipe_runtime_path_performed=true
old_opt_amn2_quarantined=true
clean_install_performed=true
package_apply_performed=true
service_restart_performed=true
bot_runtime_started=false
telegram_api_called=false
restore_apply_performed=false
archive_import_apply_performed=false
remote_backup_download_performed=false
public_exposure_performed=false
public_listener_change_performed=false
write_api_enablement_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
config_delivery_performed=false
secret_values_printed=false
p7_c004c_clean_installer_status=completed_clean_install_smoke
remote_safe_evidence_dir=/root/p7-c004c-clean-installer-20260620T054656Z
remote_clean_installer_exit_code=0
```

## Conclusion

`P7-C004c` closes the main clean-installer RC gap: AMN2 `5501295` is now
validated as a direct destructive clean install on the disposable VPS, with
fresh DB, loopback web runtime and API loopback smoke passing. The current
known-good VPS-smoked/package baseline remains `5501295`, now backed by direct
clean-install evidence rather than only clean `b121865` plus `5501295` overlay.
