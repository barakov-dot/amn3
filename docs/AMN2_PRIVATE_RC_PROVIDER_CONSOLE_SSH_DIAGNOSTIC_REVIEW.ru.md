# PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence и результат
`PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT`.

Live/VPS/SSH/config/Telegram/public gates этим review не открывались.

## Review verdict

```text
review_go=true
execution_gate_go=conditional-go-with-explicit-operator-approval
target_vps=89.185.80.166
expected_amn2_head_if_observed=187949bffb927a0a6d6c1f260fc0bb9ebb972447
current_blocker=ssh_connection_closed_before_remote_execution
recommended_gate=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE
telegram_operation_retry_go=false
provider_mutation_go=false
public_exposure_status=closed
```

Причина review: SSH transport уже закрывался до remote marker даже в
single-session/no-SCP/LF-normalized helper. Следующий безопасный шаг - собрать
read-only evidence вне SSH-транспорта через provider console/VNC/serial panel,
если такая консоль доступна оператору.

## Что нужно проверить read-only

Проверять только безопасные aggregate/status поля:

```text
remote_utc=observed
uptime_load=observed
disk_free_summary=observed
memory_summary=observed
sshd_service_status=observed
sshd_listener_status=observed
recent_auth_noise_counters=observed
maxstartups_or_rate_limit_evidence=observed_or_absent
oom_kill_kernel_evidence=observed_or_absent
conntrack_or_network_pressure_evidence=observed_or_absent
amn2_runtime_path_presence=observed
amn2_source_marker_match=observed_if_safe
telegram_polling_process_count=observed_without_raw_process_dump
```

Не печатать:

- raw auth logs with IP/ports;
- raw process list;
- env values;
- DB rows;
- tokens/passwords/keys;
- `.conf`, QR, `vpn://`, private key, PSK.

## Allowed actions for future execution gate

Только внутри будущего exact gate:

- provider console/VNC/serial login by operator;
- read-only shell/status commands;
- redacted auth/sshd counters;
- read-only AMN2 source marker check;
- read-only no Telegram polling guard;
- optional local public closed probes from operator machine;
- safe evidence only.

## Forbidden actions

Запрещено:

- reboot/rebuild/restore/import;
- package upload/apply;
- service start/restart/stop;
- `sshd_config` changes;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- user/key/auth policy changes;
- public exposure;
- Telegram polling/live send/profile/media mutation;
- config generation/delivery;
- peer creation;
- DB row dump/download/copy;
- raw logs with IP/ports;
- secret-bearing output.

## Pass criteria

```text
provider_console_access_available=true
read_only_console_observation_completed=true
sshd_status_observed=true
auth_noise_counters_observed=true
kernel_oom_conntrack_summary_observed=true
amn2_source_marker_match=yes_or_not_observed_with_reason
telegram_polling_process_count=0_or_not_observed_with_reason
public_exposure_performed=false
mutation_performed=false
secret_values_printed=false
```

## Fail criteria / stop-lines

Stop immediately if:

- provider console is unavailable;
- provider panel requires reboot/rebuild/reset to access console;
- any proposed action changes SSH/firewall/auth/users/keys;
- raw logs would expose IP/ports beyond accepted redaction;
- any secret-bearing payload would be printed;
- AMN2 source marker mismatch is observed;
- Telegram polling process is unexpectedly running and cannot be classified
  read-only.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE

Открыть exact gate для provider-console read-only SSH diagnostic.

Использовать существующие Phase 8 evidence:
- PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT;
- PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW;
- PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head if observable:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Allowed:
- provider console/VNC/serial read-only observation by operator;
- uptime/load/disk/memory summary;
- sshd service/listener status observation;
- redacted sshd/auth log counters only;
- kernel OOM/conntrack/network-pressure counters only;
- read-only /opt/amn2 presence and source marker check if safe;
- read-only Telegram polling process count without raw process dump;
- optional public closed probes for 3030, 3040, 80, 443;
- safe evidence without secret-bearing payload.

Forbidden:
- reboot/restore/import/provider rebuild;
- package upload/apply;
- service start/restart/stop;
- sshd_config/firewall/listener/TLS/proxy/user/key/auth changes;
- public exposure;
- Telegram polling/live send/profile/media mutation;
- config generation or delivery;
- peer creation;
- DB row dump/download/copy;
- raw auth logs with IP/ports;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output.

Stop at first failed gate and report exact blocker.
```

## Recommendation

```text
recommended_next_step=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE
recommended_followup_review=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_REVIEW
telegram_operation_retry_go=false
```
