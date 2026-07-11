# Phase 10 1c7fb78 private VPS schema and owner-shared rollout gate review

Date: 2026-07-11.

Decision: `APPROVED-CONSUMED-COMPLETED-PASS`.

This review performed local package/tooling verification and read-only VPS
preflight only. It did not upload a file, stop a service, migrate SQLite,
change device 8, apply a source overlay, start the bot or mutate a peer.

```text
phase9_progress_harness=14_passed|product_and_docs_scope_passed
```

## Inputs

```text
current_vps_overlay=34b3b43
candidate_source=1c7fb789b1e4de09811f03e008cfad1fe6a7392c
package_sha256=AEEB5A5C81354D7631F14DF57D7422CF02C08157CB4075B4B37B5BFD2BE6015B
source_sha256=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
reconciliation_runner_sha256=D4566B42D6FCB7B6891F65826E0E302DF59CBEC49536D3AFC4A3A3ED789C7E72
candidate_full_tests=823_passed_1_skipped_1_warning
```

There are no deleted source paths between `34b3b43` and `1c7fb78`. Unlike the
prior source-only gate, this candidate adds `plans.max_devices` and
`devices.assignment_mode`, so production schema migration is an explicit part
of the reviewed operation.

## Read-Only VPS Preflight

```text
source_overlay=34b3b43
web_active=active
web_enabled=enabled
web_login_http=200
web_loopback_3030=true
public_3030_3040_listener=false
bot_active=inactive
bot_enabled=disabled
bot_process_count=0
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
db_integrity=ok
db_foreign_key_issues=0
users_count=6
orders_count=8
devices_count=8
admin_actions_count=43
assignment_mode_column_present=false
plan_max_devices_column_present=false
root_free_bytes=3259731968
rollback_root=present_0700_root_root
candidate_remote_present=false
venv_python=3.12.3
```

The production logical SQLite digest was captured privately for before/after
verification. It is not a rollback substitute; a verified SQLite backup is
required before migration.

## Device 8 Reconciliation Preflight

```text
device8_exists=true
device8_status=active
device8_config_version=amneziawg_v2
device8_config_material_status=available
device8_linked_orders=0
device8_owner_status=active
device8_owner_is_admin=false
device8_current_owner_device_count=3
configured_admin_id_count=2
configured_admin_user_matches=1
active_configured_admin_user_matches=1
device8_owner_matches_configured_admin=true
configured_admin_db_flag=false
owner_reassignment_required=false
```

The safe production dry-run of the checksum-reviewed runner returned
`status=ready`, `database_mutation=false`, `peer_mutation=false`. Device 8
already belongs to the only active DB user matching configured admin IDs.
Therefore the live reconciliation must not change `devices.user_id`. It only
sets that existing owner row to `is_admin=1`, sets device 8 to
`assignment_mode=owner_shared`, and writes two audit events atomically.

The private runner was tested from a legacy schema through dry-run, apply and
idempotent retry. It refuses owner mismatch, multiple active configured-admin
matches, missing/inactive device, unexpected config state or any linked order.

## Exact Allowed Live Scope

Only after the exact phrase below:

1. Recheck local package, source and reconciliation-runner SHA256 values.
2. Repeat the read-only VPS baseline and stop on any drift from the conditions
   above.
3. Upload only the package ZIP, its checksum, the reconciliation runner and a
   checksum file to `/root`, mode `0600`; verify every remote checksum.
4. Create a unique mode `0700` rollback directory under
   `/root/amn2-rollbacks`.
5. Stop only `amneziya-web.service`; keep the bot inactive and disabled.
6. With writers stopped, create and verify a mode `0600` tracked-source tar,
   prior overlay marker, SQLite backup through the SQLite backup API, and a safe
   manifest.
7. Extract the package into a new mode `0700` directory and verify source commit
   and SHA bindings.
8. Apply source `1c7fb78` offline with `VPS_APPLY_ENABLED=false`,
   `OPERATOR_DEVICE_CREATE_ENABLED=false`, `PIP_NO_INDEX=1` and
   `PIP_DISABLE_PIP_VERSION_CHECK=1`.
9. Create a private SQLite clone from the verified backup. Run the
   reconciliation runner with `--apply` on the clone; require schema columns,
   unchanged user/order/device counts, device 8 owner admin, assignment
   `owner_shared`, exactly two audit rows, integrity `ok` and zero FK issues.
10. Run loopback API smoke only against that migrated clone, with both DB env
    variables bound to the clone.
11. Reconfirm production DB has not changed, then run the same checksum-bound
    runner once against production. Expected production changes are only two
    new columns, one owner admin flag, one device assignment value and two audit
    rows. User/order/device counts and device owner remain unchanged.
12. Start only `amneziya-web.service`. Verify active/enabled state, login HTTP
    `200`, protected route behavior, loopback-only `127.0.0.1:3030`, no public
    `3030/3040` listener, both write gates false and no bot process.
13. Verify read-only DB integrity/FK/counts/audit delta and that the existing
    device 8 runtime peer is still present. Do not regenerate or deliver a
    config and do not change peer keys, IP or AWG runtime.

## Stop And Rollback Criteria

Stop before apply on overlay/checksum drift, enabled write gate, active bot,
unexpected listener, insufficient disk, rollback verification failure,
candidate collision, DB integrity/FK issue, configured-admin mismatch, device
owner mismatch, linked order or changed device state.

Rollback after apply on source install/import failure, clone migration or API
smoke failure, unexpected production DB delta, reconciliation failure, web
startup/auth/listener failure, write-gate change, bot activation or runtime
peer disappearance.

Rollback restores both the tracked-source snapshot/overlay marker and the
verified SQLite backup before restarting the private web service. The bot stays
inactive and disabled throughout.

## Excluded

Peer creation/removal/change, config generation/delivery, Telegram API use,
polling/send, persistent bot activation, public exposure, firewall/TLS/reverse
proxy change, user-owner reassignment, order mutation, reboot and provider
action remain excluded.

## Exact Approval Phrase

```text
APPROVE PHASE10_1C7FB78_PRIVATE_VPS_UPLOAD_SCHEMA_MIGRATION_DEVICE8_OWNER_SHARED_AND_CLONE_DB_API_WEB_SMOKE_WITH_ROLLBACK
```

The exact phrase was received and consumed. Rollout completed on run
`20260711T154907Z`; evidence:
`research/amn2/phase-10-1c7fb78-private-vps-schema-owner-shared-rollout-2026-07-11.md`.
