# PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD

Дата: 2026-06-26.

Статус: `recorded-docs-only`.

Использованы результаты:

- `PRIVATE_RC_TELEGRAM_OPERATION_GATE`;
- `PRIVATE_RC_TELEGRAM_OPERATION_POLLING_CLEANUP_GATE`;
- `PRIVATE_RC_TELEGRAM_OPERATION_SSH_RECOVERY_CLEANUP_GATE`;
- `PRIVATE_RC_TELEGRAM_OPERATION_NO_POLLING_GUARD_SIMPLE_GATE`;
- `PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE`;
- `PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_GATE`.

Live/VPS/config/Telegram/public gates этим документом не открывались.

## Итог

```text
private_rc_telegram_operation_gate_status=blocked-by-intermittent-ssh-transport
telegram_bot_application_failure=false
telegram_operation_scope_expanded=false
public_exposure_status=closed
config_delivery_performed=false
peer_creation_performed=false
secret_values_printed=false
```

## Что произошло

`PRIVATE_RC_TELEGRAM_OPERATION_GATE` был открыт оператором явно. Helper успел:

- пройти local dry probe URL inspection;
- загрузить temporary remote helper;
- подтвердить public closed probes before polling.

Затем remote start/precheck получил `Connection closed by 89.185.80.166 port 22`.

Resume обнаружил `existing_bot_polling_process=present`, но PID-файл текущего
run отсутствовал, поэтому второй polling-процесс не запускался.

Cleanup gate позже показал:

```text
amn2_app_main_polling_process_before_count=0
bot_polling_cleanup_status=no_matching_polling_process_found
previous_uploaded_helper_cleanup_status=passed
remaining_amn2_app_main_polling_process_count=0
final_no_polling_guard_status=passed
```

Технический `CRLF exit 0` issue в cleanup-helper был зафиксирован как helper
quality issue, не как VPS/app failure.

## SSH evidence

`PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE` 2026-06-26 подтвердил
нестабильность последовательных SSH-команд:

```text
ssh_trivial_true_status=passed
ssh_echo_command_status=passed
ssh_remote_summary=connection_closed
```

`PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_GATE` 2026-06-26 дал полезный
server-side evidence:

```text
journal_sshd_recent_connection_closed_count=34
journal_sshd_recent_failed_password_count=41
journal_sshd_recent_accepted_password_count=3
journal_sshd_recent_maxstartups_count=0
journal_sshd_recent_timeout_count=0
journal_sshd_recent_oom_count=0
journal_sshd_recent_conntrack_count=0
auth_log_recent_failed_password_count=40
auth_log_recent_pam_count=61
kernel_relevant_recent_status=blocked_connection_closed
```

Логи показывают сильный внешний SSH auth-noise фон и повторяющуюся
нестабильность последующих SSH/SCP-сессий. Они не доказывают `MaxStartups`,
OOM, conntrack exhaustion, fatal sshd error или AMN2 failure.

## Decision

```text
private_rc_telegram_operation_retry_go=false
reason=ssh_transport_not_stable_enough_for_controlled_polling_gate
required_before_retry=PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
```

Повторять `PRIVATE_RC_TELEGRAM_OPERATION_GATE` сейчас нельзя. Следующий шаг
должен быть review/diagnostic по SSH-транспорту, а не новый Telegram polling.

## Stop-lines

До нового exact gate нельзя:

- запускать Telegram polling;
- повторять `PRIVATE_RC_TELEGRAM_OPERATION_GATE`;
- запускать service start/restart/stop;
- выполнять package upload/apply;
- менять sshd_config/firewall/auth/users/keys;
- открывать public exposure;
- генерировать или доставлять config;
- создавать peer/config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выполнять restore/import/reboot/provider action.

## Next gates

Одиночный:

```text
PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
```

Парный:

```text
PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
+
HELPER_SSH_TRANSPORT_HARDENING
```

Тройной:

```text
PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
+
HELPER_SSH_TRANSPORT_HARDENING
+
PRIVATE_RC_FINAL_STATUS_REFRESH
```
