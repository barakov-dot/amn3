# Next task — AMN2 Phase 12 Spain Migration

Current state: install-boundary local gate is prepared and awaits commit/push.
Do not repeat runs 001–009 or resource-confirmation runner retries. The package
and executor are checksum-bound as follows:

```text
package_sha256=F11C15E97DB21D7B5368AF6438F0BFB1032B2670BCD02DBB5078A8806DC55B44
package_bytes=139929600
manifest_sha256=2905EEEC24509260C36C0EE7F00F5827A0517929026C90BFE7CAB928DD91BD78
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=46F5F8B374F9EF4B804268AE6C83A0A86297825B37BCB563C9C597C1A637F12E
executor_bytes=139246
foreign_equality_policy=dynamic_persistent_v1
foreign_equality_receipt=persistent_equal|volatile_before_after_counts|all_volatile_allowed
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
