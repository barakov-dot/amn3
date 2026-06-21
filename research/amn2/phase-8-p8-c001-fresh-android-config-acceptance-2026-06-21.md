# Phase 8 P8-C001 fresh Android config acceptance attempt

Date: 2026-06-21.

Status: `passed-functional-android-acceptance-with-reconnect-sanity-compatible-awg-config`.

Target: disposable VPS `89.185.80.166`.

Scope: exact `P8-C001 fresh per-device Android config acceptance gate`.
One fresh Android peer/config was created through the AMN2 access/config/peer
path, copied to the operator-selected private local destination outside the
workspace, and observed with read-only server-side AWG counters. No `.conf`,
private key, PSK, QR, `vpn://`, token, secret-bearing screenshot or payload was
printed into evidence. No public exposure, Telegram live send, destructive
install, restore/import/reboot, provider mutation or extra peer creation was
performed.

## Create And Handoff Evidence

Run:

```text
run_id=20260621T111610Z
source_overlay_observed=6d5cf3ea929f26b6b352ad341bff1dd4bd5a8da5
listen_port=30001
server_public_key_fp=0bdc326c396a
live_runtime=docker
live_container=amnezia-awg2
live_config_path=/opt/amnezia/awg/awg0.conf
existing_live_peer_count=2
```

Fresh AMN2 path:

```text
server_db_sync_status=passed
server_public_key_source=live_awg0
server_public_key_value_printed=false
manual_access_request_status=created
order_id=5
approve_order_status=passed
fresh_device_id=1
fresh_peer_public_key_fp=6dabdb9a4d01
fresh_vpn_ip=10.8.0.4
config_version=amneziawg_v2
config_artifact_bytes=438
config_artifact_sha256=441acc4fcc83918bd03e3d0c004e22ada0caf49a20b52123b8838871f86ddd4c
config_payload_printed=false
private_key_output_performed=false
preshared_key_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
```

Post-create:

```text
live_peer_count_before=2
live_peer_count_after=3
fresh_peer_expected_count_delta=1
p8_c001_create_handoff_status=remote_artifact_ready_for_private_copy
remote_p8_c001_create_exit_code=0
scp_private_copy_exit_code=0
local_conf_count=1
local_conf_file=p8-c001-android-device-1.conf
local_conf_bytes=438
local_conf_sha256=441acc4fcc83918bd03e3d0c004e22ada0caf49a20b52123b8838871f86ddd4c
remote_cleanup_exit_code=0
p8_c001_private_handoff_status=completed_private_file_copied_secret_not_printed
```

## Server-Side Android Observation

Observation run:

```text
run_id=20260621T112402Z
fresh_peer_public_key_fp=6dabdb9a4d01
```

Baseline with Android VPN off:

```text
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=3
fresh_peer_found=yes
fresh_peer_index=1
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_before_exit_code=0
```

After Android traffic attempt:

```text
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=3
fresh_peer_found=yes
fresh_peer_index=3
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_after_android_traffic_exit_code=0
```

## Result

The fresh per-device AMN2 config creation and private handoff sub-step passed.

The Android acceptance gate did not pass in this observation window because the
fresh peer did not show a handshake, endpoint or traffic after the Android
traffic attempt.

## Replacement Fresh Config Attempt

The operator requested a fresh replacement config to exclude stale-file or
phone-side import ambiguity. A second fresh peer/config was created without
printing payload material:

```text
run_id=20260621T112936Z
source_overlay_observed=6d5cf3ea929f26b6b352ad341bff1dd4bd5a8da5
existing_live_peer_count=3
server_db_sync_status=passed
server_public_key_source=live_awg0
manual_access_request_status=created
order_id=6
approve_order_status=passed
fresh_device_id=2
fresh_peer_public_key_fp=594ba96e4f90
fresh_vpn_ip=10.8.0.5
config_version=amneziawg_v2
config_artifact_bytes=438
config_artifact_sha256=746b6166d53bbd97730b8343fd2660c667d6a84b0804b9fbed20b18a083e876e
live_peer_count_before=3
live_peer_count_after=4
scp_private_copy_exit_code=0
local_conf_file=p8-c001-android-device-2.conf
config_payload_printed=false
private_key_output_performed=false
preshared_key_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
```

The helper failed after the private copy because the local PowerShell
environment did not expose `Get-FileHash`; this happened after `scp` completed
and did not invalidate the copied private file. The helper was patched to use a
.NET SHA-256 fallback for future runs.

Replacement observation:

```text
observation_run_id=20260621T113559Z
fresh_peer_public_key_fp=594ba96e4f90
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=4
```

Baseline with Android VPN off:

```text
fresh_peer_found=yes
fresh_peer_index=4
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_before_exit_code=0
```

After Android traffic attempt:

```text
fresh_peer_found=yes
fresh_peer_index=3
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_after_android_traffic_exit_code=0
```

Replacement result:

```text
p8_c001_replacement_status=blocked-server-handshake-missing
primary_failure_class=server_handshake_missing
```

Android-side operator observation for the replacement file:

```text
android_import_status=passed
android_connect_status=failed_no_connected_state
android_error_payload_shared=false
secret_bearing_screenshot_shared=false
```

Safe metadata comparison against the Phase 7 diagnostic configs that previously
connected showed that endpoint, allowed IPs, DNS, persistent keepalive and the
server public key fingerprint matched, but the fresh AMN2 client AWG parameters
did not match the working Android config parameters.

Fresh AMN2 defaults observed in the generated replacement config:

```text
client_awg_jc=4
client_awg_jmin=40
client_awg_jmax=70
client_awg_s1=0
client_awg_s2=0
client_awg_s3=0
client_awg_s4=0
client_awg_h1=1
client_awg_h2=2
client_awg_h3=3
client_awg_h4=4
```

Working diagnostic config parameters:

```text
client_awg_jc=3
client_awg_jmin=10
client_awg_jmax=30
client_awg_s1=15
client_awg_s2=18
client_awg_s3=20
client_awg_s4=23
client_awg_h1=1020325451
client_awg_h2=3288052141
client_awg_h3=1766607858
client_awg_h4=2528465083
```

Root-cause hypothesis:

```text
primary_hypothesis=fresh_client_awg_parameter_mismatch_with_live_server
reason=android_import_passes_but_live_peer_never_observes_endpoint_handshake_or_traffic
```

Prepared retry:

```text
retry_gate=P8-C001R
retry_scope=render-compatible-config-for-existing-device-2-only
fresh_peer_public_key_fp=594ba96e4f90
new_order_created=false
new_device_created=false
peer_apply_performed=false
db_mutation_performed=false
public_exposure_performed=false
telegram_live_send_performed=false
payload_output_allowed=false
helper=tmp/p8_c001r_existing_device_compatible_config.ps1
```

P8-C001R phone-side observation after the compatible retry:

```text
observation_run_id=20260621T115206Z
fresh_peer_public_key_fp=594ba96e4f90
android_device_class=phone
android_app_status=connecting_without_connected_state
telegram_open_status=failed
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=4
```

Baseline with Android VPN off:

```text
fresh_peer_found=yes
fresh_peer_index=4
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_before_exit_code=0
```

After the phone attempted to connect and generate traffic:

```text
fresh_peer_found=yes
fresh_peer_index=3
latest_handshake_epoch=0
latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no
remote_after_android_traffic_exit_code=0
```

Additional operator observation:

```text
known_good_android_projector_with_existing_config_status=working_now
```

Interpretation of this latest observation:

```text
server_awg_runtime_status=alive
udp_30001_dataplane_status=working_for_known_good_android_projector
fresh_peer_594ba96e4f90_server_status=present_but_no_phone_endpoint_or_handshake
most_likely_failure_class=specific_phone_client_or_phone_network_path
```

After the phone OS update, the same fresh compatible device-2 config connected
successfully on the Android phone. The follow-up read-only server observation
captured a fresh handshake, endpoint and growing traffic counters for the fresh
peer. No `.conf`, private key, PSK, QR, `vpn://`, token, secret-bearing
screenshot or payload was printed into evidence.

Final acceptance observation:

```text
observation_run_id=20260621T122027Z
fresh_peer_public_key_fp=594ba96e4f90
android_device_class=phone
android_os_update_performed_by_operator=true
android_app_status=connected
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=4
```

Baseline note: the baseline was not a zero-counter/offline baseline because a
recent successful phone connection was already visible. It is still useful as a
safe before/after counter snapshot.

Baseline snapshot:

```text
fresh_peer_found=yes
fresh_peer_index=4
latest_handshake_epoch=1782044313
latest_handshake_age_s=132
transfer_rx_bytes=191124
transfer_tx_bytes=1487651
endpoint_observed=yes
remote_before_exit_code=0
```

After Android traffic attempt:

```text
fresh_peer_found=yes
fresh_peer_index=4
latest_handshake_epoch=1782044455
latest_handshake_age_s=45
transfer_rx_bytes=520504
transfer_tx_bytes=4609467
endpoint_observed=yes
remote_after_android_traffic_exit_code=0
```

Acceptance result:

```text
p8_c001_android_import_status=passed
p8_c001_android_connect_status=passed
p8_c001_android_traffic_status=passed
p8_c001_fresh_peer_handshake_status=passed
p8_c001_fresh_peer_counter_growth_status=passed
p8_c001_payload_output_status=not_performed
p8_c001_public_exposure_status=not_performed
p8_c001_telegram_live_send_status=not_performed
p8_c001_status=passed-functional-android-acceptance-with-compatible-awg-config
```

Reconnect sanity observation while the Android phone was still available:

```text
observation_run_id=20260621T122817Z
fresh_peer_public_key_fp=594ba96e4f90
android_reconnect_sanity_status=passed
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=4
```

Reconnect baseline:

```text
fresh_peer_found=yes
fresh_peer_index=1
latest_handshake_epoch=1782044816
latest_handshake_age_s=107
transfer_rx_bytes=5136612
transfer_tx_bytes=229495265
endpoint_observed=yes
remote_before_exit_code=0
```

After reconnect and Android traffic:

```text
fresh_peer_found=yes
fresh_peer_index=4
latest_handshake_epoch=1782044932
latest_handshake_age_s=18
transfer_rx_bytes=5318584
transfer_tx_bytes=230151167
endpoint_observed=yes
remote_after_android_traffic_exit_code=0
```

Reconnect counter delta:

```text
transfer_rx_delta_bytes=181972
transfer_tx_delta_bytes=655902
endpoint_observed_after=yes
fresh_handshake_after=yes
```

Current gate status:

```text
p8_c001_status=passed-functional-android-acceptance-with-reconnect-sanity-compatible-awg-config
phase8_launch_gate_status_after_p8_c001=android-acceptance-unblocked-package-and-persistence-gates-remain
primary_remaining_launch_blocker_after_p8_c001=package-current-head-and-persist-compatible-awg-defaults
p8_c001_interim_status_superseded_by_p8_c002=yes
```

## Interpretation

This evidence proves:

- AMN2 can create one fresh per-device Android config through the access/config
  path;
- fresh peers were applied to the live Docker-backed AWG runtime;
- the private handoff copied fresh `.conf` artifacts outside the workspace
  without payload output;
- Android AmneziaWG imported the fresh compatible `.conf`, connected, and
  generated traffic confirmed by fresh handshake and growing server counters;
- reconnect sanity passed for the same fresh peer;
- public exposure remained closed during the gate.

This evidence does not prove:

- current-head package/apply smoke;
- fresh-from-zero VPS reproducibility;
- iOS primary support, QR primary delivery or full `vpn://` primary delivery.

## Next Gate

The immediate next gate from `P8-C001` was:

```text
P8-C002 package/current-head smoke and compatible AWG defaults persistence gate
```

That follow-up gate passed later on 2026-06-21. Current next exact action:

```text
P8-C003 fresh-from-zero VPS rehearsal gate
```

Stop-line:

```text
Do not proceed to P8-C003 without a fresh exact destructive clean/fresh install
gate.
```
