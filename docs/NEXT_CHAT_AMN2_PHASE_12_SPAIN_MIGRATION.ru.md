# Next task — AMN2 Phase 12 Spain Migration

Current state: install-boundary local gate is prepared and awaits commit/push.
Do not repeat runs 001–009 or resource-confirmation runner retries. The package
and executor are checksum-bound as follows:

```text
package_sha256=91E1B2CB276DEF68F57255F57476814B6D1F5EF829AD2BF0A2E3F678CBA2B24B
package_bytes=139929600
manifest_sha256=FF2D828CD103315E2CED3AB7337B387BB21BFFE6429F72D35AA7562326F7FB94
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=02BFF28EA2C658CE4EA446835184DD32C7AB4B887B9D0F9132C189F4FBB1CFB3
executor_bytes=139389
foreign_equality_policy=dynamic_persistent_v1
foreign_equality_receipt=persistent_equal|volatile_before_after_counts|all_volatile_allowed|volatile_fields_bound_port_set_restart_count
spain_mutation=false
```

The next live action, after commit/push/origin readback and literal approval,
is only checksum-bound upload of package/executor and remote `install-bound`.
It must verify remote hashes, use in-memory preconditions, perform automatic
rollback on failure, and record persistent/volatile foreign equality. No
foreign service stop/mutation; USA remains rollback contour.

Start from `docs/AMN2_PHASE_12_SPAIN_MIGRATION_FIRST_MESSAGE.ru.md` and treat
`docs/AMN2_PHASE_12_SPAIN_MIGRATION_ENTRY.ru.md` as the mandatory contract.

Current state: checksum-bound Phase 12 package gate is locally ready. Do not
repeat its builds, tests, SOL review, runs 001–009, or security scan. Complete
the minimal commit/push/origin readback, then issue a separate exact
read-only resource-confirmation approval. Do not upload, install, or mutate
Spain before that approval.

```text
COMMIT_PUSH_VERIFY_ORIGINS -> ISSUE_SEPARATE_EXACT_PHASE12_READ_ONLY_RESOURCE_CONFIRMATION_APPROVAL -> STOP
```

Do not install or alter Spain until the new literal approval is supplied. Do
not repeat Phase 11 preflight. Do not stop AWG on Spain or USA.
