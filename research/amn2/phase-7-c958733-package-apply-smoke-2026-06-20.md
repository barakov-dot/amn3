# Phase 7 P7-C009 c958733 package apply + loopback/Telegram/backup smoke

Date: 2026-06-20.

Status: `completed-c958733-package-apply-loopback-telegram-backup-smoke`.

Target: disposable VPS `89.185.80.166`.

AMN2 source: `c9587332d425583ed627899d7fa950756b64c4dc`
(`Harden security-sensitive operations`).

## Scope

Opened exact named gate:

```text
P7-C009 c958733 package apply + loopback/Telegram/backup smoke gate
```

Allowed inside the gate:

- upload and verify the `c958733` update/smoke package;
- apply tracked source overlay to `/opt/amn2`;
- restart only loopback web runtime;
- run loopback API smoke;
- run Telegram `getMe` plus non-polling dispatcher/user-flow surface smoke;
- create and verify backup evidence;
- confirm public external probes stay closed.

Not opened: public exposure, config delivery payload output, write execution,
installer executor, restore/import/reboot/download, provider mutation, Local
Agent mutation, Telegram polling/live send/profile/media mutation or
secret-bearing evidence.

## Local Package Evidence

```text
package: dist/amn2-vps-update-and-smoke-kit-c958733.zip
package_sha256=B9C299DE16041570068EAFE77B0ED95F86A56FDB07E85A2D3AA061A5C971DB6A
source_zip: dist/amn2-codex-vps-test-prep-c958733-source.zip
source_sha256=E0F2F823CF4E29B52404E634BA11961B3C2B85604C04498CC3D752DD5DAB6E0B
package_entries=5
package_required_missing_count=0
source_entries=343
forbidden_source_entries=0
package_hygiene_status=passed
```

## VPS Evidence

Transcript:
`C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p7-c009-c958733-package-apply-smoke-20260620T115618Z.log`.

Run id: `20260620T115618Z`.

```text
package_sha256_match=yes
package_sha256sum_check=passed
source_zip_sha256_match=yes
source_update_status=passed
source_overlay_commit=c9587332d425583ed627899d7fa950756b64c4dc
source_overlay_match=yes
package_apply_performed=true
loopback_web_restart_performed=true
web_pid=267909
web_login_loopback_http=200
web_runtime_status=passed
```

Loopback API smoke passed:

```text
VPS verdict: pass
run_id: 20260620T115704Z
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260620T115704Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260620T115704Z.tar.gz
```

`api-server.log` remains excluded from evidence unless manually redacted.

Telegram token was used only for `getMe`. Token value was not printed.

```text
telegram_get_me_status=passed
telegram_api_status=ok
bot_identity_present=yes
bot_identity_safe=@NeobyatnayaAMNZ_bot
telegram_proxy_status=disabled
bot_dispatcher_construct_status=passed
bot_router_count=1
bot_message_handler_count=4
bot_callback_handler_count=18
user_flow_callback_surface_count=11
admin_flow_callback_surface_count=6
bot_polling_started=false
telegram_live_send_performed=false
config_delivery_payload_output_performed=false
telegram_smoke_exit_code=0
p7_c009_telegram_smoke_status=passed
```

Backup create and verify passed, and the post-fix artifact mode was verified as
`0600`.

```text
backup_create_status=passed
backup_verify_status=passed
backup_artifact_basename=amneziya-backup-20260620T115741Z.tar.enc
backup_artifact_bytes=204900
backup_artifact_sha256=89052625d4f72908c8548bb1879a1aa5597d7a4620341202dab2957f4827afab
backup_artifact_mode=600
backup_output_dir=/opt/amn2/backups/p7-c009-c958733-20260620T115618Z
backup_artifact_count=1
backup_artifact_contents_printed=false
backup_mode_status=passed
```

Public probes remained closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

Final guard:

```text
loopback_api_smoke_passed=true
telegram_get_me_passed=true
bot_dispatcher_constructed=true
backup_artifact_mode_600_verified=true
public_exposure_performed=false
public_listener_change_performed=false
config_delivery_payload_output_performed=false
write_execution_performed=false
write_api_enablement_performed=false
actual_install_executor_invoked=false
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
provider_action_performed=false
remote_backup_download_performed=false
local_agent_mutation_performed=false
production_peer_user_mutation_performed=false
secret_values_printed=false
p7_c009_c958733_package_apply_smoke_status=completed
remote_p7_c009_exit_code=0
remote_safe_evidence_dir=/opt/amn2/vps-smoke/p7-c009-c958733-package-apply-smoke-20260620T115618Z
```

## Result

`c958733` is now the latest package-applied and VPS-smoked AMN2 head on the
disposable VPS for the private/operator RC lane.

The system remains loopback-only, Telegram-first for users, and operator web
access stays private by VPS IP plus loopback/SSH tunnel. Public web exposure,
write execution, config delivery payload output and restore/import/reboot
remain separate exact named gates.
