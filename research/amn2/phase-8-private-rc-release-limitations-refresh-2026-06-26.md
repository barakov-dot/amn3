# Phase 8 private RC release limitations refresh

Date: 2026-06-26.

Status: `completed-docs-only`.

No live VPS/SSH/config/Telegram/public gate was opened.

## Result

```text
release_limitations_refresh_status=completed-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
android_private_operator_rc_proof=complete-with-explicit-limitations
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_config_delivery_status=not-approved
production_rollout_status=not-approved
hold_status=active
next_action_requires_exact_named_gate=true
```

## Android proof refresh

```text
p8_c001_android_phone_status=passed
p8_c001_fresh_peer_public_key_fp=594ba96e4f90
p8_c003_android_projector_status=passed-with-projector-limitation
p8_c003_fresh_peer_public_key_fp=d0ab128d6801
third_party_android_phone_status=passed-manual-and-server-side
third_party_android_fresh_peer_public_key_fp=49e456e4edcb
third_party_android_latest_handshake_age_s=23
third_party_android_endpoint_observed=yes
third_party_android_transfer_rx_bytes=55600508
third_party_android_transfer_tx_bytes=132476207
```

## Still not approved

```text
public_launch_status=not-approved
public_web_admin_api_status=not-approved
telegram_live_send_status=not-approved
telegram_bot_polling_status=not-approved-by-refresh
telegram_live_config_delivery_status=not-approved
public_self_service_config_delivery_status=not-approved
new_peer_creation_without_exact_gate=not-approved
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_scale_rollout_status=not-approved
```

## Updated docs

```text
docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/NEXT_CHAT_AMN2_PRIVATE_RC_SESSION_0.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
```

## Hold

After this refresh, AMN2 remains in operator-request hold:

```text
hold_gate=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
hold_status=active
next_action_requires_exact_named_gate=true
```
