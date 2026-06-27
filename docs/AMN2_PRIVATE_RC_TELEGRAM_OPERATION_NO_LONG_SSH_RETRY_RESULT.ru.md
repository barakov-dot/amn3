# PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_RESULT

Дата: 2026-06-27.

Статус: `passed-private-operator-no-config-delivery`.

Использован explicit gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE
```

Цель gate: controlled private/operator Telegram bot operation retry без
удержания SSH во время manual Telegram window. Использован key-based SSH,
short precheck, short polling start with remote self-stop watchdog, local
manual window without open SSH, short final stop/no-polling guard.

## Safe result

```text
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
run_id=20260627T051432Z
manual_window_seconds=120
remote_polling_ttl_seconds=150
key_path_preflight_status=passed
operator_public_key_fingerprint=SHA256:cNrkGhxuCg3lHXlSC+73/qVhJQDJSbJAqBnpJcHlG8c
operator_public_key_value_printed=false
private_key_output_performed=false
probe_url_shape_status=passed
public_closed_probes_before_status=passed
ssh_key_login_only=true
password_fallback_used=false
scp_helper_upload_performed=false
remote_temp_helper_file_created=false
source_overlay_match=yes
settings_load_status=passed
operator_admin_pair_present=yes
public_listener_guard_status=passed
telegram_app_main_polling_process_count_before=0
existing_bot_polling_process=absent
telegram_get_me_status=passed
bot_identity_safe=@NeobyatnayaAMNZ_bot
bot_polling_started=true
remote_watchdog_started=true
ssh_session_open_during_manual_window=false
local_manual_window_status=finished
operator_start_flow_observed=passed
partner_start_flow_observed=passed
config_delivery_attempted=false
telegram_app_main_polling_process_count_before_final=1
stop_only_amn2_app_main_polling_process_status=stopped
remaining_amn2_app_main_polling_process_count=0
final_no_polling_guard_status=passed
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Interpretation

No-long-SSH retry passed inside the private/operator boundary:

```text
telegram_operation_no_long_ssh_retry_status=passed
telegram_real_operation_status=passed-private-operator-no-config-delivery
telegram_private_live_preview_status=passed
telegram_no_polling_status=restored-and-proven
```

This proves the approved admin/operator Telegram `/start` flow in a controlled
window where no SSH session was held open during the manual Telegram action.
The gate also proved that controlled polling was stopped by the final guard and
that public probes remained closed before and after.

This does not approve config generation, config delivery, peer creation, public
launch, non-admin rollout, Telegram profile/media mutation, package apply,
service rollout, restore/import, reboot or provider rebuild.

## Stop-lines

Do not perform without a new exact gate:

- config generation or delivery;
- peer creation;
- public exposure;
- package upload/apply;
- service restart/start/stop outside an explicitly named controlled gate;
- Telegram profile/media mutation;
- Telegram broadcast/mass send;
- non-admin user rollout;
- SSH/firewall/auth/provider changes;
- restore/import/reboot/provider rebuild;
- output `.conf`, QR, `vpn://`, private key, PSK, token/password.

## Next status

```text
telegram_no_long_ssh_retry_status=passed
telegram_real_operation_status=passed-private-operator-no-config-delivery
telegram_cleanup_guard_required=false
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
recommended_next=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
