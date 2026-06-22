# Phase 8 P8-C003 fresh-from-zero VPS rehearsal

Date: 2026-06-22.

Status: `passed-fresh-zero-rehearsal-awaiting-final-freeze`.

Scope: exact named `P8-C003 fresh-from-zero VPS rehearsal` opened by the
operator for disposable VPS `89.185.80.166`. The gate allowed destructive clean
install of the AMN2 app runtime path `/opt/amn2`, package/apply of AMN2
`187949b`, fresh safe env/DB initialization, loopback web/API smoke, Telegram
`getMe` plus non-polling smoke, one fresh Android projector `.conf` private
handoff, backup create+verify and closed public probes.

Not opened: provider rebuild, reboot, restore/import, public exposure,
firewall/listener opening, Telegram live send/profile/media mutation, bot
polling, config payload output, QR output, `vpn://` output, private key/PSK or
token/password output.

## Gate Format

ЦЕЛЬ:
prove reproducible private/operator RC launch path from a fresh AMN2 runtime
install on the disposable VPS using current head `187949b`.

Что доказывает:
fresh AMN2 runtime install, package/source apply, private env/DB init, loopback
web/API, Telegram token/server-side bot surface, fresh Android projector config
handoff, backup evidence and closed public exposure can pass together.

Что не доказывает:
public launch, public web/admin exposure, iOS primary support, restore/import
DR, provider rebuild, Android phone acceptance inside this gate, or Telegram
on-device flow on the Android projector.

Влияние на близость запуска:
moves Phase 8 from `blocked-until-fresh-from-zero-vps-rehearsal` to
`fresh-from-zero-rehearsal-passed-awaiting-final-freeze`.

Следующий gate если passed:
`P8-SFINAL launch readiness freeze`.

Stop-line если failed:
stop at the first failed stage and do not compensate with ad hoc public
exposure, extra peer creation, restore/import, provider action or payload
output without a fresh exact gate.

## Inputs

AMN2 head:

```text
187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
```

Package:

```text
dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
source_zip_sha256=649EF03461555B13D8C4AF59709CEEC49F2300C395F69DCA982DF15732409313
```

Private inputs:

```text
telegram_token_available_privately=yes
web_admin_credentials_strategy=new_private_credentials
safe_env_strategy=generate_fresh_plus_private_inputs
private_handoff_destination_outside_workspace=yes
private_handoff_path=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
target_operator_telegram_id=provided-redacted
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
admin_telegram_ids_value_printed=false
secret_values_printed=false
```

Android acceptance limitation:

```text
android_phone_available=false
android_acceptance_device=android_projector
android_projector_telegram_required=false
fresh_android_traffic_source=browser_or_app
```

## Stage 1: Fresh Runtime Rehearsal

Run id:

```text
20260622T051333Z
```

Local safe transcript:

```text
tmp/p8-c003-fresh-zero-rehearsal-20260622T051333Z.log
```

Pre-destructive safe identity and dataplane checks:

```text
os_id=ubuntu
os_version_id=24.04
hostname_static=166780.ip-ptr.tech
old_source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
awg_dataplane_precheck=passed
live_interface=awg0
live_runtime=docker
live_container=amnezia-awg2
listen_port=30001
server_public_key_fp=0bdc326c396a
live_interface_address_present=true
existing_live_peer_count_before=4
web_admin_public_exposure_before=no
api_public_exposure_before=no
```

Package verification:

```text
package_uploaded=true
package_sha256_match=yes
package_sha256sum_check=passed
package_extracted=true
source_zip_sha256_match=yes
```

Destructive runtime rehearsal:

```text
app_runtime_stop_attempted=true
old_opt_amn2_quarantined=true
old_opt_amn2_quarantine_path=/opt/amn2.pre-p8-c003-20260622T051333Z
clean_target_created=true
wipe_runtime_path_performed=true
base_packages_installed=true
python3_version=Python 3.12.3
venv_created=true
source_apply_status=passed
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
package_apply_performed=true
```

Fresh env/DB:

```text
env_written=true
servers_yml_written=true
telegram_token_presence=present
web_admin_credentials_strategy=new_private_credentials
safe_env_strategy=generate_fresh_plus_private_inputs
server_public_key_value_printed=false
settings_load_status=passed
web_admin_host=127.0.0.1
web_admin_port=3030
server_name=local
vps_apply_enabled=False
telegram_token_present=True
db_initialize_status=passed
db_present=True
db_bytes=147456
secret_values_printed=false
```

Admin IDs note:

The original stage-1 helper printed `admin_telegram_ids_count=1` because its
count command did not add a trailing newline before `wc -l`. The follow-up
resume precheck used a corrected parser and verified the actual state:

```text
admin_telegram_ids_present=true
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
admin_telegram_ids_value_printed=false
```

## Runtime Smokes

Loopback web:

```text
loopback_web_start_performed=true
web_login_loopback_http=200
web_runtime_status=passed
```

Loopback API:

```text
VPS verdict: pass
api_ready_status=passed
api_smoke_status=passed
auth_status=passed
missing_bearer_http=401
wrong_scope_http=403
revoked_token_http=401
listener_status=passed
audit_status=passed
```

Telegram API and non-polling bot surface:

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
secret_values_printed=false
p8_c003_telegram_smoke_status=passed
```

## Fresh Android Projector Config

Fresh peer/config creation through AMN2 path:

```text
manual_access_request_status=created
order_id=1
approve_order_status=passed
fresh_device_id=1
fresh_peer_public_key_fp=d0ab128d6801
fresh_vpn_ip=10.8.0.6
config_version=amneziawg_v2
config_artifact_bytes=478
config_artifact_sha256=8cdbd038a484d2847cc9e7e2d548e54e3e6f0798cccc6e1128bfb440d269a195
config_payload_printed=false
private_key_output_performed=false
preshared_key_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
```

Post-create safe AWG observation:

```text
live_peer_count_before=4
live_peer_count_after=5
fresh_peer_expected_count_delta=1
p8_c003_create_handoff_status=remote_artifact_ready_for_private_copy
secret_values_printed=false
```

Private local handoff:

```text
local_private_artifact_dir=redacted
local_conf_count=1
local_conf_file=p8-c003-android-projector-device-1.conf
local_conf_bytes=478
local_conf_sha256=8CDBD038A484D2847CC9E7E2D548E54E3E6F0798CCCC6E1128BFB440D269A195
local_safe_manifest_present=true
conf_payload_printed=false
remote_private_artifact_cleanup_exit_code=0
```

## Backup Evidence

Current-state safe inventory before backup:

```text
db_present=True
db_bytes=147456
users_count=1
devices_count=1
servers_count=1
api_tokens_count=2
admin_actions_count=7
db_rows_printed=false
```

Backup create and verify:

```text
backup_create_exit_code=0
backup_create_status=passed
backup_verify_exit_code=0
backup_verify_status=passed
backup_artifact_basename=amneziya-backup-20260622T051654Z.tar.enc
backup_artifact_bytes=204900
backup_artifact_sha256=648fcb80148302cd9b37f05f70ad5b17fb0da9710d0d50361d3886c0e179cf58
backup_artifact_mode=600
backup_output_dir=/opt/amn2/backups/p8-c003-fresh-zero-20260622T051333Z
backup_artifact_count=1
backup_artifact_contents_printed=false
backup_mode_status=passed
```

## Android Projector Observation

Observation-only run used the already copied private `.conf`; it did not repeat
destructive install/apply, did not create another peer and did not copy config
payloads into evidence.

Local safe transcript:

```text
tmp/p8-c003-observation-only-20260622T051333Z.log
```

Precheck:

```text
admin_telegram_ids_present=true
admin_telegram_ids_count_actual=2
operator_admin_pair_present=yes
admin_telegram_ids_value_printed=false
fresh_peer_found=yes
p8_c003_observation_precheck_status=passed
```

Baseline note:

The baseline prompt asked the operator to keep the Android projector VPN off,
but the server snapshot already observed a fresh handshake and non-zero
counters. The acceptance proof therefore relies on the after-traffic snapshot
and positive counter deltas, not on a clean zero-counter off-baseline.

Baseline snapshot:

```text
label=before_android_projector
fresh_peer_found=yes
fresh_peer_index=6
fresh_peer_public_key_fp=d0ab128d6801
latest_handshake_epoch=1782153747
latest_handshake_age_s=38
transfer_rx_bytes=6265160
transfer_tx_bytes=12987459
endpoint_observed=yes
secret_values_printed=false
```

After Android projector browser/app traffic:

```text
label=after_android_projector_traffic
fresh_peer_found=yes
fresh_peer_index=6
fresh_peer_public_key_fp=d0ab128d6801
latest_handshake_epoch=1782153800
latest_handshake_age_s=87
transfer_rx_bytes=6887244
transfer_tx_bytes=21992210
endpoint_observed=yes
transfer_rx_delta_bytes=622084
transfer_tx_delta_bytes=9004751
fresh_handshake_after=True
endpoint_observed_after=yes
fresh_android_connect_status=passed_by_server_observation
fresh_android_traffic_status=passed_by_server_counter_growth
fresh_android_server_counter_growth=passed
```

This closes `P8-C003` Android projector acceptance with the explicit limitation
that the device was an Android projector, not an Android phone, and Telegram was
not available on-device. Android phone acceptance remains separately covered by
`P8-C001`.

## Closed Public Probes

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Final Guard

```text
fresh_install_status=passed
source_overlay_match=yes
fresh_env_db_init_status=passed
loopback_web_status=passed
loopback_api_smoke_status=passed
telegram_get_me_status=passed
telegram_polling_started=false
telegram_live_send_performed=false
backup_create_status=passed
backup_verify_status=passed
backup_artifact_mode_600_verified=true
public_exposure_performed=false
public_listener_change_performed=false
config_payload_output_performed=false
write_execution_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
reboot_performed=false
provider_action_performed=false
production_peer_user_mutation_performed=single_fresh_test_peer_only
secret_values_printed=false
```

Final status:

```text
p8_c003_status=passed-fresh-zero-rehearsal-observation-only-window
phase8_launch_gate_status=fresh-from-zero-rehearsal-passed-awaiting-final-freeze
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_traffic_source=browser_or_app
fresh_android_projector_limitation_recorded=true
secret_values_printed=false
recommended_next_gate=P8-SFINAL launch readiness freeze
```
