# PRIVATE_RC_FINAL_STATUS_SNAPSHOT

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence, final Android summary и release
limitations refresh. Live/VPS/config/Telegram/public gates не открывались.

## Короткий статус

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
android_private_operator_rc_proof=complete-with-explicit-limitations
public_launch_status=not-approved
public_exposure_status=closed-by-default
telegram_live_config_delivery_status=not-approved
telegram_private_operation_status=blocked-by-intermittent-ssh-transport
production_rollout_status=not-approved
hold_status=active
next_action_requires_exact_named_gate=true
latest_head=2dbd746
```

Человеческая формулировка:

AMN2 готов к закрытому private/operator RC с явными ограничениями. Android
часть внутри private/operator RC закрыта сильным evidence: P8-C001 Android
phone, P8-C003 Android projector limitation и third-party Android phone manual
плюс server-side proof. Публичный запуск и любые расширения не открыты.

## Что доказано

```text
amn2_runtime_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_current_head_smoke=P8-C002_passed
fresh_zero_rehearsal=P8-C003_passed
private_operator_session_0=passed-read-only
telegram_getme=passed
telegram_private_live_preview=passed-with-manual-operator-observation
telegram_private_operation=blocked-by-intermittent-ssh-transport
db_path_classification=passed-db-path-classified-with-aggregate-limitation
ssh_transport_small_commands=passed
ssh_server_log_diagnostic=partial-useful-evidence-blocked-on-later-ssh-session
ssh_transport_stabilization_review=completed-docs-only
ssh_single_session_diagnostic=passed-with-helper-crlf-exit-issue
telegram_operation_review_refresh=completed-docs-only
android_private_operator_rc_proof=complete-with-explicit-limitations
backup_create_verify=passed
public_closed_probes=passed_in_latest_relevant_gates
secret_payload_output_status=not-performed
```

Android evidence:

```text
p8_c001_android_phone_status=passed
p8_c003_android_projector_status=passed-with-projector-limitation
third_party_android_phone_status=passed-manual-and-server-side
third_party_android_fresh_peer_public_key_fp=49e456e4edcb
third_party_android_latest_handshake_age_s=23
third_party_android_endpoint_observed=yes
third_party_android_transfer_rx_bytes=55600508
third_party_android_transfer_tx_bytes=132476207
```

## Что разрешено

Разрешено в текущем статусе:

- закрытый private/operator RC;
- private/operator web/admin без public exposure;
- `.conf`-first private handoff только внутри явно открытых gates;
- Android AmneziaWG как основной мобильный кандидат внутри RC;
- операторская работа по docs/checklists/evidence без live gates;
- точечные будущие gates при явном запросе оператора.

## Что запрещено без нового exact gate

```text
live_vps_ssh_command=not-approved
package_upload_apply=not-approved
service_start_restart_stop=not-approved
public_exposure=not-approved
firewall_listener_tls_proxy_change=not-approved
config_generation_delivery=not-approved
new_peer_creation=not-approved
conf_qr_vpn_uri_key_psk_token_password_output=not-approved
telegram_polling_live_send=not-approved
telegram_profile_media_mutation=not-approved
restore_import_reboot=not-approved
provider_rebuild=not-approved
production_rollout=not-approved
```

## Что остается ограничением

```text
public_launch_status=not-approved
public_web_admin_api_status=not-approved
telegram_live_config_delivery_status=not-approved
telegram_private_operation_retry_status=blocked-until-ssh-transport-stabilization-review
telegram_private_operation_retry_precondition=ssh_single_session_diagnostic_passed
public_self_service_config_delivery_status=not-approved
qr_release_primary=false
full_vpn_uri_release_primary=false
ios_defaultvpn_status=experimental_unreliable
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_scale_rollout_status=not-approved
```

## Последние pushed heads

```text
2dbd746 Refresh private RC release limitations
cd36207 Add private RC final Android summary
a43a2ca Record third-party Android traffic observation
52efc55 Record third-party Android manual acceptance
6f2081f Record third-party Android handoff result
```

## Главные документы

```text
docs/AMN2_PRIVATE_RC_FINAL_STATUS_SNAPSHOT.ru.md
docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md
docs/AMN2_PRIVATE_RC_FINAL_ANDROID_SUMMARY.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
docs/AMN2_WAIT_FOR_OPERATOR_REQUEST_HOLD.ru.md
docs/NEXT_CHAT_AMN2_PRIVATE_RC_SESSION_0.ru.md
```

## Следующие gates menu

Ожидание:

```text
ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Live Telegram operation review, без запуска:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW
```

Реальный controlled Telegram bot operation:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE
```

SSH transport stabilization review before retrying Telegram operation:

```text
PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
```

Single-session SSH diagnostic recommended by stabilization review:

```text
PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
```

Refresh Telegram operation review before retry:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
```

New single-session Telegram operation gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
```

Новая приватная выдача `.conf`:

```text
PRIVATE_CONF_HANDOFF_GATE_REVIEW
```

Public exposure review:

```text
PUBLIC_EXPOSURE_GATE_REVIEW
```

Restore/import DR review:

```text
RESTORE_IMPORT_DR_GATE_REVIEW
```

Provider rebuild review:

```text
PROVIDER_REBUILD_GATE_REVIEW
```

## Рекомендация

Текущий рекомендуемый режим после Telegram operation blocker:

```text
recommended_next_step=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
```

Повторять Telegram operation execution нельзя до SSH stabilization review:

```text
recommended_live_next_review=blocked-until-ssh-transport-stabilization-review
```
