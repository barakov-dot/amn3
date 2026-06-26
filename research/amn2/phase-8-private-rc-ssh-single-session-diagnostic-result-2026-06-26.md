# Phase 8 private RC SSH single-session diagnostic result

Дата: 2026-06-26.

```text
gate_name=PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260626T175627
result=passed-with-helper-crlf-exit-issue
remote_single_session_status=passed
public_closed_probes_before_status=passed
public_closed_probes_after_manual_status=passed
source_overlay_match=yes
no_telegram_polling_process=true
telegram_operation_retry_precondition=ssh_single_session_diagnostic_passed
```

## Evidence

The remote read-only checks completed in one SSH session:

- `ssh_session_count=1`
- `single_session_diagnostic_status=passed`
- source overlay matched `187949bffb927a0a6d6c1f260fc0bb9ebb972447`
- `telegram_app_main_polling_process_count=0`
- `raw_log_output_performed=false`
- `ip_port_log_values_printed=false`

The wrapper still returned exit code `2` because stdin bash text contained CRLF
and `exit 0` became an invalid numeric argument. This does not invalidate the
remote evidence printed before the helper-side failure.

## Next

```text
recommended_next_review=PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW_REFRESH
helper_hardening_required=remote_stdin_bash_lf_normalization
```
