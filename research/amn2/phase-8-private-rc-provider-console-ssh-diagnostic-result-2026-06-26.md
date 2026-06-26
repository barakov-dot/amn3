# Phase 8 evidence: provider-console SSH diagnostic result

Date: 2026-06-26.

Status: `passed-minimal-manual-console-observation`.

No secrets, config payloads, private keys, PSK, tokens, passwords, QR, `vpn://`,
raw auth logs or raw process lists are recorded here.

## Safe operator-observed output

```text
provider_console_access_available=true
provider_console_type=QEMU_console
date_utc_output=Fri Jun 26 07:18:36 PM UTC 2026
uptime_output=up 18 days, 7:29, 2 users, load average 0.00, 0.00, 0.00
systemctl_is_active_ssh=active
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
pgrep_app_main_wc_l=0
no_telegram_polling_process=true
```

## Safety boundary

```text
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

## Classification

```text
provider_console_diagnostic_status=passed_minimal
auth_noise_counter_status=not_collected_due_to_no_paste_console
key_based_access_prep_unblocked=true
ssh_auth_hardening_unblocked=false
telegram_operation_retry_go=false
```
