# Phase 10 1c7fb78 private VPS schema and owner-shared rollout

Date: 2026-07-11.

Status: `completed-pass-with-verified-automatic-rollbacks`.

Exact approval consumed:

```text
APPROVE PHASE10_1C7FB78_PRIVATE_VPS_UPLOAD_SCHEMA_MIGRATION_DEVICE8_OWNER_SHARED_AND_CLONE_DB_API_WEB_SMOKE_WITH_ROLLBACK
```

## Bound Inputs

```text
source_commit=1c7fb789b1e4de09811f03e008cfad1fe6a7392c
package_sha256=AEEB5A5C81354D7631F14DF57D7422CF02C08157CB4075B4B37B5BFD2BE6015B
source_sha256=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
reconciliation_runner_sha256=D4566B42D6FCB7B6891F65826E0E302DF59CBEC49536D3AFC4A3A3ED789C7E72
final_private_orchestrator_sha256=ED2D22CD8A15D10FA8D2E647AF2687A228BEC568171E75B4112C8A5B09EA4459
source_overlay_before=34b3b43
source_overlay_after=1c7fb78
successful_run_id=20260711T154907Z
rollback_path=/root/amn2-rollbacks/1c7fb78-20260711T154907Z
```

All four uploaded files were mode `0600 root:root` and passed remote SHA256
verification before the web service was stopped. The package candidate and
rollback directories were new unique paths.

## Rollback Exercise

Five attempts stopped at progressively later safety checks. Every attempt used
a new candidate and rollback directory, restored the prior source marker, and
returned the private web service to active state.

```text
attempt_20260711T153032Z=offline_build_isolation_missing_setuptools|source_rollback_passed|production_db_untouched
attempt_20260711T153740Z=expected_apply_rc_intercepted_by_ERR_trap|source_rollback_passed|production_db_untouched
attempt_20260711T153932Z=clone_script_parent_traversal_denied|clone_reconciliation_passed|source_rollback_passed|production_db_untouched
attempt_20260711T154223Z=clone_api_smoke_passed|verdict_matcher_and_marker_mode_stop|source_rollback_passed|production_db_untouched
attempt_20260711T154632Z=source_clone_production_reconciliation_passed|web_http_readiness_race|source_and_sqlite_rollback_passed
pre_success_original_logical_db_digest_restored_each_time=true
pre_success_counts_restored=users_6|orders_8|devices_8|admin_actions_43
```

The VPS venv intentionally has no installed `setuptools` and no cached wheel.
Network installation remained disabled. The successful path accepted only the
exact known offline build-isolation diagnostic, then required direct imports
from `/opt/amn2/app/__init__.py`. No dependency download occurred.

The clone workspace was moved to an `amneziya`-owned mode `0700` directory
under `/tmp`; smoke logs were redirected there. The overlay marker was
normalized to `0640 root:amneziya` so the service user can read it. The final
web check waited for real HTTP `200`, not only systemd `active` state.

## Successful Clone Gate

Before production SQLite mutation, the verified backup was cloned and migrated
with the checksum-bound reconciliation runner.

```text
clone_schema_migration=passed
clone_owner_admin_flag=passed
clone_device8_assignment=owner_shared
clone_owner_reassigned=false
clone_admin_actions_delta=2
clone_integrity=ok
clone_foreign_key_issues=0
clone_server_db_sync=passed
clone_api_ready=passed
clone_api_smoke=passed
clone_auth_http=401_403_401
clone_listener=passed_loopback_only
clone_audit=passed
production_db_unchanged_before_reconciliation=true
temporary_clone_count_after_success=0
legacy_failed_clone_count_after_success=0
```

The safe clone smoke bundle was preserved inside the successful rollback
directory. Raw tokens, authorization headers and clone SQLite were not
published.

## Production Result

```text
db_integrity=ok
db_foreign_key_issues=0
users_count_before_after=6_6
orders_count_before_after=8_8
devices_count_before_after=8_8
admin_actions_count_before_after=43_45
plans.max_devices_column=present
devices.assignment_mode_column=present
configured_plan_quota_rows=0
device8_owner_matches_configured_admin=true
device8_owner_is_admin=true
device8_assignment_mode=owner_shared
device8_owner_reassigned=false
device8_linked_orders=0
device8_secret_peer_ip_material_unchanged=true
last_two_audit_actions=device.reconcile_assignment|grant_admin
```

The reconciliation did not change device 8 owner, peer public key, encrypted
client material, PSK, VPN IP, status, config version or config material status.
It added the two schema columns, set the existing configured-admin owner DB
flag, set device 8 assignment mode and wrote two safe audit events.

## Runtime Result

```text
marker_state=0640_root_amneziya
marker_service_readable=true
web_active=active
web_enabled=enabled
web_login_http=200
protected_route_http=303
web_listener=127.0.0.1_3030_only
api_3040_listener_count=0
public_3030_3040_listener=false
bot_active=inactive
bot_enabled=disabled
bot_process_count=0
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
awg_container_running=true
device8_runtime_peer_present=true
peer_mutation=false
config_generation=false
config_delivery=false
```

The successful rollback bundle is mode `0700 root:root` and contains the
tracked-source tar, prior marker, verified SQLite backup, clone safe smoke
bundle and safe reconciliation summaries.

## Remaining Product Work

The schema can now store per-plan quotas, but existing plan rows have no
`max_devices` value yet and therefore still fall back to the global setting.
The next product slice is:

```text
START_PHASE10_PLAN_DEVICE_QUOTA_ADMIN_UI_SLICE
```

That slice should expose safe plan quota management. A client plan for six
devices must create or permit six dedicated peers/configs; it must not reuse
the owner-shared profile.
