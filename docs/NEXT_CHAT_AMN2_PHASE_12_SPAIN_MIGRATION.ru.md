# Next task — AMN2 Phase 12 Spain Migration

Current state: v8 тихая SCP upload/hash verification завершились. `install-bound`
прошёл precondition, затем fail-closed после `package_verified_remote` в
pre-write production preparation. Receipt доказывает automatic rollback:
transaction=`rolled_back`, все AMN2 units inactive, owned `/opt` и staging
absent; `capsule_committed` и install actions отсутствуют. Foreign Spain
service не останавливался и не изменялся; USA остаётся rollback contour.

v9 сохраняет весь install contract, но заменяет generic preparation wrapper
на bounded safe cause label (`BackendError`/`PackageVerificationError`). Это
нужно для одного следующего checksum-bound run без слепого повторения; любые
небезопасные строки остаются generic class label.

```text
package_sha256=C519CFBA6DAB59FE281B0EBBDF3D9D7639C295D6EFDC3EF6E8B5BE64A4D89519
package_bytes=139939840
manifest_sha256=7D9426141B2ADA655D8B9CD4A65D12BFC105C90B2232E2E4B88C359A7282913D
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=90042FBA4AB896FF7F9E822680270569E280426BCDC12B6F4A102DC6C58C43E2
executor_bytes=140091
runner_sha256=6B44E93D474F8C2365C909AE47BDDE78332569902812DF87EBE75DCF1150321C
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_135_passed|safe_preparation_cause_test_pass
spain_mutation=false
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds, SOL
review, or security scans. Do not stop AWG. Do not stop or mutate the foreign
Spain service. Do not migrate/delete USA data.

Next gate: stage only Phase 12 files, commit and push current branch, verify
origin readback, then issue one new exact checksum-bound install approval for
the v7 hashes above. The install runner must upload only package/executor,
verify remote hashes, execute `install-bound`, automatically rollback on any
failure, and record persistent/volatile foreign equality.
