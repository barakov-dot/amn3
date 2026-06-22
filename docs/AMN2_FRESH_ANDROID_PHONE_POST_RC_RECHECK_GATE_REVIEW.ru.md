# AMN2 fresh Android phone post-RC recheck gate review

Дата: 2026-06-22.

Статус:

```text
fresh_android_phone_post_rc_recheck_review_status=completed-docs-only
gate_name=FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE
gate_opened=false
live_vps_ssh_performed=false
config_generation_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
public_exposure_performed=false
secret_values_printed=false
```

Этот review использует только существующие Phase 8 evidence и результат
`PRIVATE_RC_OPERATOR_RUN_GATE`. Он не открывает live/VPS/config/Telegram/public
gates.

## 1. Цель gate

ЦЕЛЬ:
повторно подтвердить Android phone acceptance после private/operator RC session
0 и fresh-from-zero rehearsal, без public exposure и без Telegram live send.

Что доказывает:

- текущий private/operator RC runtime на VPS `89.185.80.166` способен выдать
  или использовать fresh Android phone `.conf` через контролируемый private
  handoff;
- Android phone импортирует `.conf` в AmneziaWG;
- Android phone подключается;
- browser/app traffic на телефоне дает fresh handshake, endpoint и рост
  counters на сервере;
- payload, keys, PSK, QR, `vpn://`, token/password не попадают в чат/evidence.

Что не доказывает:

- public launch readiness;
- public web/admin/API exposure;
- Telegram live delivery;
- bot polling;
- QR или полный `vpn://` как release-primary;
- iOS DefaultVPN release acceptance;
- restore/import DR;
- provider rebuild;
- production-scale rollout.

Влияние на близость запуска:

```text
private_operator_rc_confidence_after_pass=higher_mobile_confidence
public_launch_status_after_pass=still_not_approved_without_separate_public_gate
```

Следующий gate если passed:

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

или отдельный broader-launch review gate, если оператор запрашивает расширение.

Stop-line если failed:
остановиться на первом failed sub-gate, зафиксировать exact blocker и не
компенсировать failure public exposure, extra peer creation, Telegram live send,
QR/`vpn://`, restore/import, provider action или payload output без нового exact
named gate.

## 2. Target VPS review

```text
target_vps=89.185.80.166
target_review=passed
```

Основание:

- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `target_vps_match=yes`;
- public probes в session 0 вернули `000` для `3030`, `3040`, `80`, `443`;
- public exposure остается closed by default.

## 3. Expected AMN2 head review

```text
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
expected_amn2_head_review=passed
```

Основание:

- `P8-C002` package/current-head smoke passed на `187949b`;
- `P8-C003` fresh-from-zero rehearsal использовал `187949b`;
- `PRIVATE_RC_OPERATOR_RUN_GATE` подтвердил `source_overlay_match=yes`.

## 4. Evidence baseline

Android phone evidence до RC:

```text
p8_c001_status=passed-functional-android-acceptance-with-reconnect-sanity-compatible-awg-config
fresh_peer_public_key_fp=594ba96e4f90
android_device_class=phone
p8_c001_android_import_status=passed
p8_c001_android_connect_status=passed
p8_c001_android_traffic_status=passed
p8_c001_fresh_peer_handshake_status=passed
p8_c001_fresh_peer_counter_growth_status=passed
android_reconnect_sanity_status=passed
```

Post-RC limitation:

```text
p8_c003_status=passed-fresh-zero-rehearsal-observation-only-window
fresh_android_acceptance_device=android_projector
fresh_android_phone_available=false
fresh_android_projector_limitation_recorded=true
```

Session 0 result:

```text
private_rc_operator_run_gate_status=passed
phase8_private_operator_rc_session_0_status=passed-read-only
target_vps_match=yes
source_overlay_match=yes
telegram_get_me_status=passed
public_listener_guard_status=passed
```

## 5. Allowed actions review

Allowed only inside future `FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE`:

- read-only VPS precheck;
- target/source/runtime safe check;
- public closed probes for `3030`, `3040`, `80`, `443`;
- create exactly one fresh Android phone peer/config through AMN2
  AccessService/BotWorkflow path, only if the gate explicitly chooses fresh
  config creation;
- copy exactly one `.conf` to private local destination outside workspace;
- no payload output;
- read-only server-side AWG observation for the fresh peer fingerprint;
- Android phone import/connect/browser-or-app traffic manual acceptance;
- safe evidence only.

Not allowed:

- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- QR/`vpn://` output;
- `.conf` payload, private key, PSK, token/password output;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

Review:

```text
allowed_actions_review=passed
payload_boundary_review=passed
public_exposure_boundary_review=passed
telegram_boundary_review=passed
```

## 6. Private inputs readiness

Required at gate-open time:

```text
android_phone_available=yes
android_phone_has_amneziawg=yes
android_phone_can_import_private_conf=yes
android_phone_can_generate_browser_or_app_traffic=yes
private_handoff_destination_outside_workspace=yes
vps_ssh_access_available_privately=yes
target_operator_telegram_id_confirmed=yes
```

Private handoff boundary:

```text
private_handoff_path=C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
private_handoff_path_must_be_outside_workspace=true
conf_payload_printed=false
qr_output_performed=false
vpn_import_link_output_performed=false
private_key_output_performed=false
preshared_key_output_performed=false
```

Current review result:

```text
private_inputs_readiness_review=conditional-go
android_phone_available_now=false
gate_open_go=blocked-until-android-phone-available
```

## 7. Pass criteria

Gate passes only if all are true:

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

Gate fails on any one:

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

## 8. GO / NO-GO

```text
review_go=true
gate_open_go=conditional-no-go-until-android-phone-available
operator_can_open_gate_now=false
```

Причина:
план и критерии готовы, но Android phone сейчас недоступен. Открывать gate без
телефона бессмысленно: он завершится stop-line `android_phone_unavailable`.

## 9. Copy/paste command на момент появления телефона

Использовать только когда Android phone физически доступен и оператор готов
импортировать `.conf` в AmneziaWG:

```text
FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE

Открыть exact gate для post-RC Android phone recheck.

Использовать существующие Phase 8 evidence и session 0 result.
Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Android phone readiness:
- Android phone is physically available now.
- Android phone has AmneziaWG installed or can install it before import.
- Android phone can import a private `.conf` file.
- Android phone can generate browser/app traffic after connect.
- Telegram on-device is optional; browser/app traffic is accepted.

Private handoff boundary:
- Private local destination outside workspace:
  C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF
- Do not paste `.conf`, QR, vpn://, private key, PSK, token or password into
  chat/evidence.

Allowed only:
- read-only VPS precheck;
- current runtime/source head check without package apply;
- public closed probes for 3030, 3040, 80, 443;
- create exactly one fresh Android phone peer/config through AMN2 path;
- copy exactly one `.conf` to private handoff destination outside workspace;
- read-only server-side observation of the fresh peer;
- Android phone import/connect/browser-or-app traffic acceptance;
- safe evidence without secret-bearing payload.

Forbidden:
- destructive VPS/provider action;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- QR/vpn:// output;
- `.conf` payload output;
- private key/PSK/token/password output;
- restore/import/reboot;
- provider rebuild;
- production-scale rollout.

Stop at first failed gate and report the exact blocker.
```
