# Phase 8 fresh Android phone post-RC recheck review and runbook

Дата: 2026-06-22.

Статус:

```text
fresh_android_phone_post_rc_recheck_review_status=completed-docs-only
fresh_android_phone_post_rc_recheck_runbook_status=prepared-docs-only
gate_name=FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE
gate_opened=false
live_vps_ssh_performed=false
config_generation_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот шаг использует только существующие Phase 8 evidence и session 0 result. Он
не открывает live/VPS/config/Telegram/public gates.

## Documents

```text
review_doc=docs/AMN2_FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW.ru.md
runbook_doc=docs/AMN2_FRESH_ANDROID_PHONE_POST_RC_RECHECK_RUNBOOK.ru.md
```

## Basis

До RC Android phone был подтвержден в `P8-C001`:

```text
p8_c001_status=passed-functional-android-acceptance-with-reconnect-sanity-compatible-awg-config
fresh_peer_public_key_fp=594ba96e4f90
p8_c001_android_import_status=passed
p8_c001_android_connect_status=passed
p8_c001_android_traffic_status=passed
p8_c001_fresh_peer_handshake_status=passed
p8_c001_fresh_peer_counter_growth_status=passed
android_reconnect_sanity_status=passed
```

После fresh-from-zero rehearsal `P8-C003` Android acceptance был выполнен на
projector, не на phone:

```text
p8_c003_status=passed-fresh-zero-rehearsal-observation-only-window
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_projector_limitation_recorded=true
```

Session 0 read-only result:

```text
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
target_vps_match=yes
source_overlay_match=yes
public_listener_guard_status=passed
telegram_get_me_status=passed
```

## Review result

```text
review_go=true
gate_open_go=conditional-no-go-until-android-phone-available
operator_can_open_gate_now=false
android_phone_available_now=false
```

Причина:
план и criteria готовы, но Android phone сейчас недоступен. Gate нужно
открывать только когда телефон физически доступен.

## Required future gate inputs

```text
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
private_handoff_path=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
target_operator_telegram_id_default=132756019
admin_telegram_ids_count_expected=2
android_phone_available=yes
android_phone_amneziawg_available=yes
android_phone_browser_or_app_traffic_available=yes
```

## Pass criteria

```text
target_vps_match=yes
source_overlay_match=yes
public_closed_probes_status=passed
fresh_android_phone_conf_handoff_status=completed_private_file_copied_secret_not_printed
android_phone_import_status=passed
android_phone_connect_status=passed
android_phone_traffic_status=passed
fresh_peer_found=yes
endpoint_observed_after=yes
fresh_handshake_after=yes
transfer_rx_delta_bytes_gt_0=true
transfer_tx_delta_bytes_gt_0=true
secret_values_printed=false
public_exposure_performed=false
telegram_live_send_performed=false
bot_polling_started=false
```

## Stop-lines

```text
android_phone_unavailable=true
private_handoff_path_inside_workspace=true
conf_payload_printed=true
qr_or_vpn_link_output_performed=true
fresh_peer_missing=true
latest_handshake_after=never
endpoint_observed_after=no
transfer_counter_growth_missing=true
public_probe_not_closed=true
telegram_live_send_detected=true
```

## Next recommendation

Default while phone is absent:

```text
ANDROID_PHONE_BLOCKER_HOLD
```

When phone appears:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE
```
