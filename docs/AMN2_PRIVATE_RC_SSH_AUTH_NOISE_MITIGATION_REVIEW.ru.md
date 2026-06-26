# PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence:

- `PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD`;
- `PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT`;
- `PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT`;
- `PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH`;
- `PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT`.

Live/VPS/SSH/config/Telegram/public gates этим review не открывались.

## Review verdict

```text
review_go=true
live_mitigation_go=false_without_new_exact_gate
telegram_operation_retry_go=false
current_blocker=ssh_connection_closed_before_remote_execution
target_vps=89.185.80.166
public_exposure_status=closed
config_delivery_status=not-approved
provider_rebuild_status=not-approved
```

Повторять Telegram operation helper сейчас не рекомендуется. Даже
single-session/no-SCP/LF-normalized вариант получил `ssh_exit_code=255` до
remote marker. Следующий шаг должен быть не очередным retry, а выбор стратегии
стабилизации доступа.

## Current evidence

```text
ssh_transport_small_commands=passed
ssh_single_session_diagnostic_remote_status=passed
ssh_single_session_diagnostic_helper_issue=crlf_exit_0_after_remote_success
telegram_single_session_operation_status=blocked-before-remote-execution
telegram_single_session_operation_exit_code=255
remote_marker_observed=false
server_auth_noise=heavy
maxstartups_evidence=false
oom_evidence=false
conntrack_evidence=false
kernel_kill_evidence=false
remote_load_recent=low
```

Auth noise from previous server-log diagnostic:

```text
journal_sshd_recent_connection_closed_count=34
journal_sshd_recent_failed_password_count=41
auth_log_recent_failed_password_count=40
auth_log_recent_pam_count=61
```

Later single-session diagnostic counters showed the noise continued:

```text
journal_sshd_recent_connection_closed_count=93
journal_sshd_recent_failed_password_count=125
auth_log_recent_failed_password_count=121
auth_log_recent_pam_count=180
```

## Interpretation

The available evidence supports this classification:

```text
root_cause_classification=ssh_transport_unstable_under_auth_noise_or_remote_session_pressure
bot_runtime_failure=false
amn2_source_head_mismatch=false
public_exposure_failure=false
```

This is still not enough to mutate SSH/firewall/auth safely. Any mitigation can
lock out the operator if applied casually, so each option needs its own exact
gate and ideally a rollback/provider-console boundary.

## Mitigation options

### Option A: provider-console read-only diagnostic

Recommended first if SSH keeps closing before commands.

Purpose:

- observe auth logs and sshd status without relying on SSH transport;
- confirm whether password brute-force/noise is the primary pressure;
- verify no AMN2 bot polling process is running;
- avoid auth/firewall mutation.

Exact future review:

```text
PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW
```

### Option B: key-based SSH access prep

Recommended before disabling password auth.

Purpose:

- create/verify operator key-based access path;
- test login with key;
- keep password auth unchanged until key path is proven;
- record rollback/console access.

Exact future review:

```text
PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_REVIEW
```

### Option C: SSH auth hardening

Only after key-based access or provider-console fallback is proven.

Possible future actions:

- disable root password login;
- disable password auth;
- move SSH from port 22;
- restrict SSH by allowlist;
- add rate limiting or fail2ban-like policy.

These are auth/network changes and are not approved by this review.

Exact future review:

```text
PRIVATE_RC_SSH_AUTH_HARDENING_GATE_REVIEW
```

### Option D: no-mutation backoff policy

Conservative short-term rule if no auth/network changes are desired:

```text
max_live_ssh_retry_per_gate=1
ssh_exit_255_after_remote_marker=false_requires_stop
ssh_exit_255_before_remote_marker=blocked-by-ssh-transport
minimum_backoff_minutes_before_new_gate=15
no_same_helper_retry_after_second_exit_255=true
```

This does not fix the cause, but prevents repeated noisy attempts.

## Recommended path

```text
recommended_next=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW
recommended_pair=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW+PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_REVIEW
telegram_operation_retry_go=false
```

If operator wants the least invasive path:

```text
recommended_minimal_path=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

If operator wants to continue toward reliable Telegram operation:

```text
recommended_practical_path=provider_console_readonly_then_key_based_access_prep
```

## Stop-lines

Without a new exact gate, do not:

- change `sshd_config`;
- change firewall/listener/TLS/proxy/Cloudflare/ngrok;
- change users, keys or auth policy;
- disable password auth;
- move SSH port;
- install/configure rate limiting;
- reboot/restore/import/rebuild;
- start Telegram polling;
- generate/deliver config;
- create peers;
- output secrets or payloads.
