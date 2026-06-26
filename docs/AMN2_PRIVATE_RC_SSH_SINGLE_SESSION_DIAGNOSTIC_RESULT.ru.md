# PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT

Дата: 2026-06-26.

Статус:

```text
private_rc_ssh_single_session_diagnostic_gate_status=passed-with-helper-crlf-exit-issue
gate_name=PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260626T175627
remote_single_session_status=passed
wrapper_exit_status=failed_due_to_crlf_exit_0
public_closed_probes_before_status=passed
public_closed_probes_after_manual_status=passed
telegram_operation_retry_precondition=ssh_single_session_diagnostic_passed
public_exposure_performed=false
config_delivery_performed=false
telegram_polling_started=false
secret_values_printed=false
```

Gate был открыт оператором явно. Выполнялись local public closed probes и один
remote read-only SSH-сеанс. Не выполнялись package upload/apply, SCP/helper
upload, service start/restart/stop, sshd/firewall/auth changes, public exposure,
config generation/delivery, peer creation, DB row dump/download/copy, Telegram
polling/live send, restore/import/reboot, provider action или secret-bearing
output.

## 1. Public probes

Before single SSH session:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

After single SSH session, manually completed locally because wrapper stopped on
helper-side CRLF `exit 0`:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_after_manual_status=passed
```

## 2. Remote single-session evidence

Remote read-only checks completed inside one SSH session:

```text
ssh_session_count=1
single_session_diagnostic_status=passed
remote_uptime_pretty=up_2_weeks_4_days_6_hours_8_minutes
remote_loadavg=0.08_0.02_0.01
remote_uid=0
remote_uname=Linux 6.8.0-111-generic x86_64
sshd_binary_present=true
sshd_process_count=2
```

AMN2 source marker matched:

```text
opt_amn2_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_expected_full=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
source_overlay_match_required_status=passed
source_marker_secret_values_printed=false
```

Telegram polling guard passed:

```text
telegram_app_main_polling_process_count=0
no_telegram_polling_process=true
raw_process_list_output_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
```

## 3. SSH/auth counters

Single-session counters confirm heavy auth noise but no direct MaxStartups/OOM
or conntrack signal:

```text
journal_sshd_recent_raw_line_count=500
journal_sshd_recent_connection_closed_count=93
journal_sshd_recent_disconnected_from_count=27
journal_sshd_recent_failed_password_count=125
journal_sshd_recent_accepted_password_count=9
journal_sshd_recent_maxstartups_count=0
journal_sshd_recent_too_many_authentication_failures_count=0
journal_sshd_recent_kex_exchange_identification_count=0
journal_sshd_recent_timeout_count=0
journal_sshd_recent_pam_count=179

auth_log_recent_raw_line_count=500
auth_log_recent_connection_closed_count=93
auth_log_recent_disconnected_from_count=29
auth_log_recent_failed_password_count=121
auth_log_recent_accepted_password_count=9
auth_log_recent_pam_count=180
auth_log_recent_maxstartups_count=0
auth_log_recent_timeout_count=0

kernel_recent_raw_line_count=1
kernel_recent_oom_count=0
kernel_recent_killed_process_count=0
kernel_recent_segfault_count=0
kernel_recent_conntrack_count=0
kernel_recent_tcp_count=0
raw_log_output_performed=false
ip_port_log_values_printed=false
```

## 4. Helper issue

Wrapper returned non-zero after the remote gate had already printed
`single_session_diagnostic_status=passed`:

```text
helper_issue=crlf_in_stdin_bash_script_exit_0
observed_error=bash_line_181_exit_0_numeric_argument_required
ssh_single_session_remote_checks_exit_code=2
remote_gate_result_before_error=passed
```

Interpretation: this is a helper serialization issue, not a remote SSH/app
failure. Future PowerShell helpers that pipe bash to `ssh ... bash -s` must
normalize remote script text to LF before piping:

```text
remote_stdin_bash_lf_normalization_required=true
```

## 5. Decision

Single-session strategy is validated:

```text
single_session_strategy_status=validated
telegram_operation_retry_precondition=ssh_single_session_diagnostic_passed
telegram_operation_retry_direct_go=false
recommended_next_review=PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
```

Do not immediately retry the old Telegram operation helper. Refresh the review
first so the next Telegram operation design uses a single-session/no-SCP model
and includes LF normalization.

## 6. Stop-lines

До нового exact gate нельзя:

- запускать Telegram polling;
- повторять старый `PRIVATE_RC_TELEGRAM_OPERATION_GATE` helper;
- использовать SCP/helper upload для Telegram operation;
- выполнять package upload/apply;
- выполнять service start/restart/stop;
- менять sshd_config/firewall/auth/users/keys;
- открывать public exposure;
- генерировать или доставлять config;
- создавать peer/config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выполнять restore/import/reboot/provider action.

## 7. Next gates

Одиночный:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
```

Парный:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
+
HELPER_SSH_TRANSPORT_HARDENING
```

Тройной:

```text
PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
+
HELPER_SSH_TRANSPORT_HARDENING
+
PRIVATE_RC_FINAL_STATUS_REFRESH
```
