# Phase 8 private RC SSH transport diagnostic result

Дата: 2026-06-25.

Итог:

```text
private_rc_ssh_transport_diagnostic_gate_status=passed
gate_name=PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260625T130118Z
ssh_transport_status=passed
source_overlay_match=yes
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
```

Safe evidence:

```text
ssh_client_version=OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2
ssh_trivial_true_exit_code=0
ssh_trivial_true_status=passed
ssh_echo_command_status=passed
ssh_echo_command_exit_code=0
ssh_remote_shell_summary_status=passed
remote_pwd=/root
remote_uid=0
remote_uname=Linux 6.8.0-111-generic x86_64
opt_amn2_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
remote_private_rc_ssh_transport_diagnostic_status=passed
```

External closed probes before and after:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

Not performed:

```text
package_upload_apply_performed=false
service_start_restart_stop_performed=false
sshd_config_change_performed=false
firewall_change_performed=false
public_exposure_performed=false
config_generation_performed=false
config_delivery_performed=false
peer_creation_performed=false
db_row_dump_performed=false
db_download_copy_performed=false
telegram_polling_started=false
telegram_live_send_performed=false
restore_import_reboot_performed=false
provider_rebuild_performed=false
secret_values_printed=false
```

Classification:

```text
previous_db_observation_blocker_reclassified=large_stdin_or_helper_execution_method_issue
db_discrepancy_status=still_unresolved_but_retry_unblocked
recommended_next=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY
```
