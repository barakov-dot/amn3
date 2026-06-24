# Phase 8 private RC DB/runtime observation result

Дата: 2026-06-24.

Итог:

```text
private_rc_db_runtime_observation_gate_status=blocked-by-ssh-transport-before-observation
gate_name=PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE
target_vps=89.185.80.166
remote_observation_started=false
db_runtime_observation_completed=false
db_root_cause_classification=not_observed
```

The gate was opened by the operator as read-only. Both the main helper and the
resume helper stopped before remote observation because SSH closed before the
first remote precheck output.

Safe evidence:

```text
main_run_id=20260624T190511Z
resume_run_id=20260624T190840Z
dry_probe_url_inspection=passed
public_closed_probes_before_status=passed
ssh_error=Connection closed by 89.185.80.166 port 22
```

Public exposure remained closed before observation:

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

Exact blocker:

```text
exact_blocker=ssh_transport_closed_before_remote_precheck
db_discrepancy_status=unresolved_due_to_ssh_transport_blocker
recommended_next=PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW
```
