# PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT

Дата: 2026-06-26.

Статус: `blocked-by-ssh-transport-before-remote-execution`.

Использован explicit gate:

```text
PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
```

Цель gate: controlled private/operator Telegram bot operation через один SSH
сеанс, без SCP/helper upload, без remote temp helper file, с автоматической
остановкой polling в конце.

## Safe result

```text
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
run_id=20260626T183902Z
manual_window_seconds=1800
probe_url_shape_status=passed
public_closed_probes_before_status=passed
ssh_single_session_telegram_operation_exit_code=255
remote_execution_started=false
remote_boundary_marker_observed=false
telegram_getme_in_this_gate=not_reached
bot_polling_started=false
manual_telegram_window_started=false
config_delivery_performed=false
peer_creation_performed=false
service_start_restart_stop_performed=false
public_exposure_before_status=closed
secret_values_printed=false
```

Exact blocker:

```text
exact_blocker=ssh_connection_closed_before_remote_script_output
ssh_error=Connection closed by 89.185.80.166 port 22
telegram_operation_application_failure=false
telegram_operation_status=not_proven_due_to_ssh_transport
```

## Interpretation

Этот результат не доказывает отказ AMN2 Telegram bot application. SSH
соединение закрылось до любого remote marker:

```text
first_remote_marker_expected=PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_GATE
first_remote_marker_observed=false
```

Следовательно:

- Telegram polling не стартовал;
- Telegram `getMe` внутри этого gate не выполнялся;
- ручное окно проверки не началось;
- config generation/delivery не выполнялись;
- peer creation не выполнялся;
- public exposure не открывался;
- service/package/provider действия не выполнялись.

## What remains true from earlier evidence

Ранее уже доказано:

```text
telegram_getme_previous_status=passed
private_rc_telegram_bot_live_preview_status=passed-with-manual-operator-observation
operator_start_flow_observed_previous=passed
bot_polling_start_stop_preview_previous=passed
ssh_single_session_diagnostic_previous_remote_status=passed
previous_no_telegram_polling_process=true
android_private_operator_rc_proof=complete-with-explicit-limitations
third_party_android_phone_status=passed-manual-and-server-side
```

Текущий blocker относится к SSH transport/auth-noise/remote session
stability, а не к Android evidence и не к уже пройденному Telegram live
preview.

## Stop-lines

До отдельного review/gate не повторять live Telegram operation execution:

```text
telegram_operation_retry_go=false
repeat_same_helper_go=false
repeat_single_session_helper_go=false
```

Не выполнять без нового exact gate:

- SSH auth/firewall/sshd changes;
- service start/restart/stop;
- package upload/apply;
- public exposure;
- config generation/delivery;
- peer creation;
- Telegram polling/live operation;
- provider rebuild/reboot/restore/import.

## Required next review

```text
required_next_review=PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW
recommended_operator_mode=hold_until_transport_strategy_is_selected
```
