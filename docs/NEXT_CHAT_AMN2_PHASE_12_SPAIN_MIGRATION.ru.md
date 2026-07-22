# Next task — AMN2 Phase 12 Spain Migration

Current state: install-boundary local gate is prepared and awaits commit/push.
Do not repeat runs 001–009 or resource-confirmation runner retries. The package
and executor are checksum-bound as follows:

```text
package_sha256=936ACDFDE808A4A235659CF904BFF55F155DACF6655476FFEEAA1A5A646E2F59
package_bytes=139939840
manifest_sha256=B9DCC4BDB0847E1776976D2ADA676D179B9B5E5BC8F03874DBC175684C57114A
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=132464ECA59FAA8224B927479E423B72C2C5354700EF761FA6AA4102FDFA1611
executor_bytes=139710
foreign_equality_policy=dynamic_persistent_v1
foreign_equality_receipt=persistent_equal|volatile_before_after_counts|all_volatile_allowed|volatile_fields_bound_port_set_restart_count
firewall_equality=semantic_rebaseline_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
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
