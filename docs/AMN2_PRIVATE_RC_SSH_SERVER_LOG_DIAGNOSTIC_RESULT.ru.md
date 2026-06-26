# PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT

Дата: 2026-06-26.

Статус:

```text
private_rc_ssh_server_log_diagnostic_gate_status=partial-useful-evidence-blocked-on-later-ssh-session
gate_name=PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260626T173850
public_closed_probes_before_status=passed
ssh_remote_health_summary_status=passed
ssh_journal_sshd_recent_status=passed
ssh_auth_log_recent_status=passed
ssh_kernel_relevant_recent_status=blocked_connection_closed
telegram_operation_status=blocked-by-intermittent-ssh-transport
public_exposure_performed=false
config_delivery_performed=false
telegram_polling_started=false
secret_values_printed=false
```

Gate был открыт оператором явно. Выполнялись только read-only SSH/log
observation и public closed probes. Не выполнялись package upload/apply,
service start/restart/stop, sshd/firewall/auth changes, public exposure, config
generation/delivery, peer creation, DB row dump/download/copy, Telegram
polling/live send, restore/import/reboot, provider rebuild или secret-bearing
output.

## 1. Что доказано

Public exposure перед SSH/log diagnostic оставался закрыт:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

Remote health summary прошел:

```text
ssh_remote_health_summary_exit_code=0
ssh_remote_health_summary_status=passed
remote_uid=0
remote_uname=Linux 6.8.0-111-generic x86_64
sshd_binary_present=true
sshd_listener_state=0_of_10_100_startups
```

В server-side SSH/auth logs есть сильный внешний auth-noise фон:

```text
journal_sshd_recent_raw_line_count=160
journal_sshd_recent_connection_closed_count=34
journal_sshd_recent_failed_password_count=41
journal_sshd_recent_accepted_password_count=3
journal_sshd_recent_pam_count=61
journal_sshd_recent_maxstartups_count=0
journal_sshd_recent_too_many_authentication_failures_count=0
journal_sshd_recent_kex_exchange_identification_count=0
journal_sshd_recent_timeout_count=0
journal_sshd_recent_oom_count=0
journal_sshd_recent_killed_process_count=0
journal_sshd_recent_conntrack_count=0
```

`/var/log/auth.log` подтвердил ту же картину:

```text
auth_log_recent_raw_line_count=160
auth_log_recent_connection_closed_count=33
auth_log_recent_disconnected_from_count=5
auth_log_recent_failed_password_count=40
auth_log_recent_accepted_password_count=3
auth_log_recent_pam_count=61
auth_log_recent_maxstartups_count=0
auth_log_recent_too_many_authentication_failures_count=0
auth_log_recent_kex_exchange_identification_count=0
auth_log_recent_timeout_count=0
auth_log_recent_oom_count=0
auth_log_recent_killed_process_count=0
auth_log_recent_conntrack_count=0
```

Логи показывают множество неуспешных попыток входа `root`, `admin`, `test` и
других пользователей с внешних адресов. IP/ports в evidence редактировались.
Успешные root-сессии оператора видны как `Accepted password` и затем штатное
закрытие `disconnected by user`.

## 2. Что заблокировалось

Последний шаг gate, `kernel_relevant_recent`, не выполнился:

```text
ssh_kernel_relevant_recent_blocker=connection_closed_before_or_during_command
ssh_kernel_relevant_recent_exit_code=255
```

Это повторяет наблюдавшийся ранее паттерн: несколько коротких SSH-команд могут
проходить, но последующая SSH/SCP-сессия иногда закрывается сервером до вывода
результата.

## 3. Интерпретация

Текущий blocker нельзя классифицировать как AMN2/Telegram/app failure.

Более точная классификация:

```text
blocker_class=intermittent-ssh-scp-transport-close-during-repeated-sessions
supporting_signal=heavy_external_auth_noise_in_sshd_auth_logs
not_supported=maxstartups_oom_conntrack_timeout_fatal
telegram_operation_blocker=ssh_transport_not_stable_enough_for_controlled_polling_gate
```

Важно: лог diagnostic не доказал `MaxStartups`, OOM, conntrack exhaustion,
kernel kill, fatal sshd error или timeout. Он доказал высокий шум в auth logs и
нестабильность серии SSH/SCP-сессий.

## 4. Impact на PRIVATE_RC_TELEGRAM_OPERATION_GATE

`PRIVATE_RC_TELEGRAM_OPERATION_GATE` остается заблокирован:

```text
private_rc_telegram_operation_gate_status=blocked-by-intermittent-ssh-transport
safe_cleanup_status=previously_no_polling_guard_passed_and_known_temp_helpers_cleaned
public_exposure_status=closed
config_delivery_status=not-performed
telegram_polling_status=not-approved-to-retry-until-ssh-transport-plan
```

Нельзя повторять controlled bot operation gate, пока не выбран отдельный план
для SSH-транспорта: single-session helper, provider console диагностика,
auth-noise mitigation review или другой exact gate.

## 5. Stop-lines

До нового exact gate нельзя:

- повторять `PRIVATE_RC_TELEGRAM_OPERATION_GATE`;
- запускать Telegram polling;
- выполнять service restart/stop/start;
- менять sshd_config/firewall/auth/users/keys;
- открывать public exposure;
- генерировать или доставлять config;
- создавать peer/config;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выполнять restore/import/reboot/provider action.

## 6. Рекомендация

Следующий безопасный шаг:

```text
PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD
```

Если оператор хочет продолжать root-cause диагностику SSH, следующий review:

```text
PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
```

Этот review должен выбрать один путь:

- single-session read-only diagnostic helper;
- provider console / out-of-band inspection;
- SSH auth-noise mitigation proposal;
- pause/backoff policy for repeated SSH gates.
