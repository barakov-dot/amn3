# PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_RESULT

Дата: 2026-06-27.

Статус: `blocked-during-manual-window-after-polling-started-cleanup-required`.

Использован explicit gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_RETRY_GATE
```

Цель gate: controlled private/operator Telegram bot operation retry через уже
доказанный key-based SSH path, один SSH-сеанс, без password fallback,
SCP/helper upload и remote temp helper file.

## Safe result

```text
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
run_id=20260626T194933Z
manual_window_seconds=1800
key_path_preflight_status=passed
operator_public_key_fingerprint=SHA256:cNrkGhxuCg3lHXlSC+73/qVhJQDJSbJAqBnpJcHlG8c
operator_public_key_value_printed=false
private_key_output_performed=false
probe_url_shape_status=passed
public_closed_probes_before_status=passed
ssh_key_login_only=true
password_fallback_used=false
ssh_session_count=1
scp_helper_upload_performed=false
remote_temp_helper_file_created=false
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
settings_load_status=passed
operator_admin_pair_present=yes
public_listener_guard_before_polling=passed
existing_bot_polling_process=absent
telegram_get_me_status=passed
telegram_api_status=ok
bot_identity_safe=@NeobyatnayaAMNZ_bot
bot_polling_started=true
manual_window_status=started
ssh_key_path_retry_remote_exit_code=-1
public_closed_probes_after_status=passed
secret_values_printed=false
```

## Exact blocker

```text
exact_blocker=ssh_connection_closed_by_remote_host_during_manual_window_after_polling_started
ssh_error=Connection to 89.185.80.166 closed by remote host
telegram_operation_status=not_passed_cleanup_required
telegram_application_failure=false
config_delivery_performed=false
peer_creation_performed=false
public_exposure_status=closed_before_and_after
```

## Interpretation

Этот результат доказывает больше, чем предыдущий single-session blocker:

- key-based SSH path реально дошел до remote execution;
- AMN2 source/runtime head совпал;
- settings/env checks прошли без secret output;
- Telegram `getMe` прошел;
- до старта polling не было существующего AMN2 `app.main` polling процесса;
- controlled polling был запущен;
- manual Telegram window началось.

Но gate не прошел, потому что SSH-сеанс закрылся во время manual window до
штатной остановки polling и final no-polling guard. Поэтому статус не может
быть `passed` до отдельного cleanup/no-polling доказательства.

## Required cleanup

Следующее действие должно быть отдельным exact gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE
```

Цель: key-based SSH no-polling guard; если найден AMN2 `python -m app.main`
polling process с cwd `/opt/amn2`, остановить только его, затем подтвердить
`remaining_amn2_app_main_polling_process_count=0`.

## Stop-lines

До cleanup/no-polling guard нельзя:

- повторять Telegram operation retry;
- считать Telegram operation passed;
- выполнять config generation/delivery;
- создавать peer/config;
- открывать public exposure;
- делать service restart/package apply/provider actions;
- выполнять SSH hardening/firewall/auth changes;
- выводить secrets/payloads.

## Next exact gates

Одиночный:

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE
```

Парный:

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE
+
PRIVATE_RC_FINAL_STATUS_REFRESH
```

Тройной:

```text
PRIVATE_RC_TELEGRAM_OPERATION_KEY_PATH_CLEANUP_GUARD_GATE
+
PRIVATE_RC_FINAL_STATUS_REFRESH
+
NEXT_CHAT_SYNC_AND_PUSH
```
