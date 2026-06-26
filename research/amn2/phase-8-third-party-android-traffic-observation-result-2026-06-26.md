# Phase 8 third-party Android traffic observation result

Date: 2026-06-26.

Gate: `THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_HELPER_UPLOAD_RETRY_GATE`.

Status: `passed-server-side-observation`.

No config generation/delivery, peer creation, service start/restart/stop,
package upload/apply, public exposure, firewall/listener/TLS/proxy change,
Telegram live send/polling, restore/import/reboot or provider action was
performed.

## Linked handoff

```text
source_gate=THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE
source_run_id=20260625T193843Z
fresh_peer_public_key_fp=49e456e4edcb
fresh_vpn_ip=10.8.0.7
local_conf_file=third-party-android-device-2.conf
```

## Observation result

```text
run_id=20260626T042616Z
target_vps=89.185.80.166
fresh_peer_public_key_fp=49e456e4edcb
fresh_peer_found=yes
fresh_peer_index=4
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

## Public closure

```text
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
external_probe_3030=000
external_probe_3040=000
external_probe_80=000
external_probe_443=000
```

## Helper boundary

```text
temporary_helper_upload_allowed=true
temporary_helper_cleanup_required=true
temporary_helper_cleanup_status=passed
raw_wg_dump_output_performed=false
conf_payload_output_performed=false
qr_output_performed=false
vpn_import_link_output_performed=false
private_key_output_performed=false
preshared_key_output_performed=false
secret_values_printed=false
```

Previous failed attempts were classified as helper/SSH transport or quoting
issues, not dataplane failure:

```text
read_only_stdin_script_attempt=blocked-by-ssh-stdin-script-transport
small_command_retry=blocked-by-shell-quoting
python_c_retry2=blocked-by-ssh-command-transport
helper_upload_retry=passed
```

## Conclusion

Third-party Android proof is complete inside the private/operator RC boundary:
manual owner report passed, server-side handshake/endpoint/rx-tx passed, public
exposure remained closed, and no secret-bearing payload was printed.
