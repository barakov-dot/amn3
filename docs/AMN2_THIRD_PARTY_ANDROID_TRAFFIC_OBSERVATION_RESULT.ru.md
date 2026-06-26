# THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION result

Дата: 2026-06-26.

Статус: `passed-server-side-observation`.

## Итог

```text
gate_name=THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_HELPER_UPLOAD_RETRY_GATE
run_id=20260626T042616Z
target_vps=89.185.80.166
fresh_peer_public_key_fp=49e456e4edcb
third_party_android_server_observation_status=passed
third_party_android_manual_acceptance_status=passed-by-third-party-operator-report
temporary_helper_cleanup_status=passed
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

Gate выполнил server-side observation через временный helper upload + cleanup,
потому что предыдущие read-only SSH attempts были заблокированы transport/helper
методом. Временный helper использовался только для read-only `awg0` observation
и был удален после выполнения.

## Safe server-side evidence

```text
container_present=true
container_state=running
live_interface=awg0
live_peer_count=6
awg_dump_status=passed
raw_wg_dump_output_performed=false
fresh_peer_found=yes
fresh_peer_index=4
fresh_peer_public_key_fp=49e456e4edcb
latest_handshake_epoch=1782448028
latest_handshake_age_s=23
transfer_rx_bytes=55600508
transfer_tx_bytes=132476207
endpoint_observed=yes
transfer_rx_gt_0=true
transfer_tx_gt_0=true
fresh_handshake_after=true
third_party_android_server_observation_status=passed
```

Public closed probes before helper upload:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

Public closed probes after helper cleanup:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_after_status=passed
```

## Boundary guard

```text
temporary_helper_upload_allowed=true
temporary_helper_cleanup_required=true
temporary_helper_cleanup_status=passed
config_generation_performed=false
config_delivery_performed=false
peer_creation_performed=false
service_start_restart_stop_performed=false
package_upload_apply_performed=false
public_exposure_performed=false
firewall_listener_tls_proxy_change_performed=false
telegram_live_send_performed=false
telegram_polling_started=false
raw_wg_dump_output_performed=false
conf_payload_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
private_key_output_performed=false
preshared_key_output_performed=false
secret_values_printed=false
```

## Previous helper attempts

Перед successful helper-upload retry были две неуспешные read-only попытки и
одна shell quoting попытка:

```text
third_party_android_traffic_observation_gate_status=blocked-by-ssh-stdin-script-transport
retry_small_command_status=blocked-by-shell-quoting
retry2_python_c_status=blocked-by-ssh-command-transport
final_helper_upload_retry_status=passed
```

Эти блокеры относятся к helper/SSH transport method, а не к Android или AWG
dataplane.

## Final conclusion

Third-party Android acceptance now has both:

```text
android_owner_manual_import_connect_traffic=passed
server_side_handshake_endpoint_rx_tx=passed
public_exposure_closed=passed
payload_secret_output_absent=passed
```

Private/operator RC limitation remains: this is a private/operator proof, not a
public launch, public config delivery, Telegram live delivery or production
rollout approval.
