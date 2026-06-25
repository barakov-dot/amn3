# AMN2 private RC SSH transport diagnostic result

Дата: 2026-06-25.

Статус:

```text
private_rc_ssh_transport_diagnostic_gate_status=passed
gate_name=PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE
target_vps=89.185.80.166
run_id=20260625T130118Z
expected_amn2_head_if_reached=187949bffb927a0a6d6c1f260fc0bb9ebb972447
ssh_transport_status=passed
previous_db_observation_blocker_reclassified=large_stdin_or_helper_execution_method_issue
public_launch_status=not-approved
```

Gate был открыт оператором явно. Выполнялись только read-only SSH diagnostics,
local dry probe URL inspection и public closed probes. Не выполнялись package
upload/apply, service start/restart/stop, sshd/firewall/auth changes, public
exposure, config generation/delivery, peer creation, DB row dump/download/copy,
Telegram polling/live send, restore/import/reboot, provider rebuild или
secret-bearing output.

## 1. Local result

SSH client:

```text
ssh_client_version=OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2
ssh_client_version_exit_code=0
ssh_client_version_status=observed
```

Dry probe URL inspection:

```text
probe_url=http://89.185.80.166:3030/login
probe_url=http://89.185.80.166:3040/api/servers
probe_url=http://89.185.80.166:80/
probe_url=https://89.185.80.166:443/
probe_url_shape_status=passed
```

## 2. Public exposure result

Before SSH diagnostic:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_before_status=passed
```

After SSH diagnostic:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
public_closed_probes_after_status=passed
```

`curl` reported empty reply / TLS handshake transport messages, but every
closed probe returned `000`, consistent with no public web/API exposure.

## 3. SSH command execution result

Trivial command:

```text
ssh_trivial_true_exit_code=0
ssh_trivial_true_status=passed
```

Echo command:

```text
ssh_echo_command_status=passed
ssh_echo_command_exit_code=0
```

Remote shell summary:

```text
ssh_remote_shell_summary_status=passed
remote_pwd=/root
remote_uid=0
remote_uname=Linux 6.8.0-111-generic x86_64
ssh_remote_summary_exit_code=0
```

## 4. AMN2 marker result

```text
opt_amn2_present=true
source_overlay_commit=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_expected_full=187949bffb927a0a6d6c1f260fc0bb9ebb972447
source_overlay_match=yes
source_marker_secret_values_printed=false
ssh_amn2_marker_exit_code=0
ssh_amn2_marker_status=passed
```

## 5. Final mutation/output guard

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
remote_private_rc_ssh_transport_diagnostic_status=passed
```

## 6. Interpretation

This result reclassifies the previous DB/runtime observation blocker:

```text
previous_exact_blocker=ssh_transport_closed_before_remote_precheck
ssh_transport_general_status=passed
likely_failure_layer=large_stdin_or_helper_execution_method
db_discrepancy_status=still_unresolved_but_retry_unblocked
```

The previous DB/runtime observation did not prove SSH transport failure in
general. It likely failed because of the helper execution method, such as large
stdin script piping or command construction. Small read-only SSH commands are
viable.

## 7. Next recommended gate

```text
PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY
```

Use the retry plan and prefer small read-only SSH commands rather than a large
stdin script.
