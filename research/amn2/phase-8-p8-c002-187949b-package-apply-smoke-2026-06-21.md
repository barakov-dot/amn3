# Phase 8 P8-C002 187949b package/current-head smoke

Date: 2026-06-21.

Status: `completed-package-current-head-smoke-compatible-awg-defaults-persisted`.

Target: disposable VPS `89.185.80.166`.

AMN2 source:

```text
branch=codex/phase7-current-fixes
commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
subject=Persist Android-compatible AWG defaults
previous_vps_smoked_package_head=6d5cf3ea929f26b6b352ad341bff1dd4bd5a8da5
```

## Scope

Opened exact named gate:

```text
P8-C002 package/current-head smoke and compatible AWG defaults persistence gate
```

Allowed inside the gate:

- upload and verify the `187949b` update/smoke package;
- apply tracked source overlay to `/opt/amn2`;
- persist the Android-accepted `CLIENT_AWG_*` defaults in the VPS runtime
  `.env` if old overrides exist;
- restart only the loopback web runtime;
- run loopback API smoke;
- run Telegram `getMe` plus non-polling dispatcher/user-flow surface smoke;
- create and verify backup evidence;
- confirm public external probes stay closed.

Not opened: public exposure, config delivery payload output, write execution
outside this package apply, installer executor, restore/import/reboot/download,
provider mutation, Local Agent mutation, Telegram polling/live send/profile/
media mutation, production peer/user mutation or secret-bearing evidence.

## Local Package Evidence

```text
package=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
package_bytes=8708274
source_zip=dist/amn2-codex-phase7-current-fixes-187949b-source.zip
source_sha256=649EF03461555B13D8C4AF59709CEEC49F2300C395F69DCA982DF15732409313
source_bytes=8757958
source_zip_entry_count=344
source_zip_forbidden_entries=0
package_entries=5
package_required_missing_count=0
package_hygiene_status=passed
```

Local verification before live apply:

```text
amn2_toolchain_check=passed
client_config_defaults_self_check=passed
py_compile_changed_files=passed
git_diff_check=passed
full_pytest_local_status=not_run_local_dev_deps_missing
```

## AMN2 Fix Summary

`187949b` persists the P8-C001 Android-accepted AWG client defaults in the
normal AMN2 runtime/package path:

```text
CLIENT_AWG_JC=3
CLIENT_AWG_JMIN=10
CLIENT_AWG_JMAX=30
CLIENT_AWG_S1=15
CLIENT_AWG_S2=18
CLIENT_AWG_S3=20
CLIENT_AWG_S4=23
CLIENT_AWG_H1=1020325451
CLIENT_AWG_H2=3288052141
CLIENT_AWG_H3=1766607858
CLIENT_AWG_H4=2528465083
```

The change covers `ClientConfigDefaults`, `Settings().client_config_defaults`,
`.env.example`, `deploy/examples/.env.production.example` and operator docs.
Existing env overrides remain supported.

## First Run Guard Failure

The first live run `20260621T125056Z` applied the source overlay and updated
all 11 safe non-secret `CLIENT_AWG_*` values, then stopped before runtime
smoke because the helper compared `H1-H4` as integers while `pydantic-settings`
returned numeric env values as strings:

```text
remote_p8_c002_exit_code=42
failure_class=helper_guard_type_mismatch
settings_client_awg_values_printed_correctly=true
secret_values_printed=false
```

The helper guard was fixed to compare normalized string values, and the final
run below completed successfully.

## VPS Evidence

Final transcript:
`C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p8-c002-187949b-package-apply-smoke-20260621T125410Z.log`.

Run id:

```text
run_id=20260621T125410Z
remote_p8_c002_exit_code=0
```

Package and source verification:

```text
package_sha256_match=yes
package_sha256sum_check=passed
package_extracted=true
source_zip_sha256_match=yes
source_update_status=passed
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
package_apply_performed=true
```

Runtime compatible AWG persistence:

```text
dotenv_compatible_awg_update_status=noop
dotenv_compatible_awg_keys_checked=11
dotenv_compatible_awg_keys_changed_count=0
settings_load_status=passed
settings_client_awg_jc=3
settings_client_awg_jmin=10
settings_client_awg_jmax=30
settings_client_awg_s1=15
settings_client_awg_s2=18
settings_client_awg_s3=20
settings_client_awg_s4=23
settings_client_awg_h1=1020325451
settings_client_awg_h2=3288052141
settings_client_awg_h3=1766607858
settings_client_awg_h4=2528465083
settings_client_awg_compatible=yes
dotenv_secret_values_printed=false
```

Loopback web/API smoke:

```text
loopback_web_restart_performed=true
web_login_loopback_http=200
web_runtime_status=passed
api_smoke_run_id=20260621T125617Z
VPS verdict=pass
server_db_sync_status=passed
api_ready_status=passed
api_smoke_status=passed
auth_status=passed
missing_bearer_http=401
wrong_scope_http=403
revoked_token_http=401
listener_status=passed
audit_status=passed
api_safe_evidence_dir=/opt/amn2/vps-smoke/api-loopback-20260621T125617Z
api_safe_bundle=/opt/amn2/vps-smoke/api-loopback-safe-evidence-20260621T125617Z.tar.gz
```

Telegram `getMe` and non-polling dispatcher/user-flow smoke:

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
p8_c002_telegram_smoke_status=passed
```

Backup create and verify:

```text
backup_create_status=passed
backup_verify_status=passed
backup_artifact_basename=amneziya-backup-20260621T125654Z.tar.enc
backup_artifact_bytes=218552
backup_artifact_sha256=c479c49161ed6e515682689b415598db709d975a6f6d425e015a53e95381edb9
backup_artifact_mode=600
backup_output_dir=/opt/amn2/backups/p8-c002-187949b-20260621T125410Z
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
source_overlay_match=yes
package_apply_performed=true
compatible_awg_defaults_persisted=true
loopback_web_restart_performed=true
loopback_api_smoke_passed=true
telegram_get_me_passed=true
bot_dispatcher_constructed=true
backup_create_performed=true
backup_verify_performed=true
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
p8_c002_187949b_package_apply_smoke_status=completed
remote_safe_evidence_dir=/opt/amn2/vps-smoke/p8-c002-187949b-package-apply-smoke-20260621T125410Z
```

## Result

`P8-C002` passed. Latest VPS-applied/package-smoked AMN2 head is now
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`.

The Phase 8 launch posture moves to:

```text
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
private_operator_rc_distance_to_launch=92_percent
next_gate=P8-C003 fresh-from-zero VPS rehearsal gate
```

Do not proceed to `P8-C003` until an exact destructive clean/fresh install gate
is opened.
