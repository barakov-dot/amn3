# PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_RESULT

Дата: 2026-06-26.

Статус: `passed-minimal-manual-console-observation`.

Результат получен оператором через provider/QEMU console, не через SSH. Codex
не выполнял live VPS команд и не открывал SSH/Telegram/public gates.

## Safe observed result

```text
gate_name=PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE
target_vps=89.185.80.166
provider_console_access_available=true
provider_console_read_only_diagnostic_status=completed_operator_side_minimal
provider_console_type=QEMU_console
remote_utc=Fri Jun 26 07:18:36 PM UTC 2026
uptime_observed=true
remote_uptime=up_18_days_7h29m
remote_loadavg=0.00_0.00_0.00
sshd_status=active
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
telegram_app_main_polling_process_count=0
no_telegram_polling_process=true
provider_mutation_performed=false
reboot_restore_import_rebuild_performed=false
service_start_restart_stop_performed=false
sshd_config_change_performed=false
firewall_auth_user_key_change_performed=false
public_exposure_performed=false
telegram_polling_started=false
config_generation_delivery_performed=false
peer_creation_performed=false
secret_values_printed=false
```

## Interpretation

Provider console diagnostic proves:

- provider/QEMU console access works;
- host is responsive from console;
- ssh service is active;
- AMN2 source marker matches expected `187949b...`;
- no AMN2 Telegram `app.main` polling process is running;
- no provider/sshd/firewall/service/config/public mutation was performed.

Auth-noise aggregate counters were not collected because the QEMU console does
not support paste, and the operator switched to a minimal manual command set.
This is acceptable for unblocking the next prep gate because console fallback is
available and no polling/source mismatch blocker was observed.

## Next gate

```text
recommended_next_gate=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE
key_based_access_prep_go=conditional-go-with-explicit-operator-approval
ssh_auth_hardening_go=false
telegram_operation_retry_go=false
```
