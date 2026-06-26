# Phase 8 private RC SSH server log diagnostic result

Дата: 2026-06-26.

Статус:

```text
gate_name=PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260626T173850
result=partial-useful-evidence-blocked-on-later-ssh-session
public_closed_probes_before_status=passed
remote_health_summary_status=passed
journal_sshd_recent_status=passed
auth_log_recent_status=passed
kernel_relevant_recent_status=blocked_connection_closed
secret_values_printed=false
```

## Safe facts

- Public probes to `3030`, `3040`, `80`, `443` returned `000`.
- SSH health summary completed.
- `sshd` listener was present; observed startup state was `0 of 10-100`.
- `journalctl -u ssh/-u sshd` and `/var/log/auth.log` showed heavy auth noise.
- No evidence was seen for `MaxStartups`, too many auth failures, kex exchange
  failure, timeout, OOM, killed process, segfault, memory or conntrack in the
  collected ssh/auth windows.
- The next SSH step closed with `Connection closed by 89.185.80.166 port 22`.

## Counts

```text
journal_connection_closed_count=34
journal_failed_password_count=41
journal_accepted_password_count=3
journal_pam_count=61
journal_maxstartups_count=0
journal_too_many_authentication_failures_count=0
journal_kex_exchange_identification_count=0
journal_timeout_count=0
journal_oom_count=0
journal_killed_process_count=0
journal_conntrack_count=0

auth_log_connection_closed_count=33
auth_log_disconnected_from_count=5
auth_log_failed_password_count=40
auth_log_accepted_password_count=3
auth_log_pam_count=61
auth_log_maxstartups_count=0
auth_log_timeout_count=0
auth_log_oom_count=0
auth_log_conntrack_count=0
```

## Interpretation

```text
blocker_class=intermittent-ssh-scp-transport-close-during-repeated-sessions
supporting_signal=heavy_external_auth_noise
not_proven=maxstartups_oom_conntrack_kernel_kill_timeout
telegram_operation_gate_status=blocked-by-ssh-transport
```

This should not be treated as an AMN2 bot/application failure. The immediate
blocking layer is transport reliability across repeated SSH/SCP sessions.

## Next

```text
recommended_next_record=PRIVATE_RC_TELEGRAM_OPERATION_BLOCKER_RECORD
recommended_next_review=PRIVATE_RC_SSH_TRANSPORT_STABILIZATION_REVIEW
```
