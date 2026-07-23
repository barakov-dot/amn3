# Next task — AMN2 Phase 12 Spain Migration

Current state: v6 тихая SCP upload завершилась, remote package/executor hashes
совпали. `install-bound` fail-closed в production preparation и automatic
rollback доказан read-only receipt: AMN2 units inactive, staging empty,
`/opt/amn2-spain-package` absent, transaction=`rolled_back`. Foreign Spain
service не останавливался и не изменялся; USA остаётся rollback contour.

Root cause: package-bound preparation импортировал `app.config.settings` до
установки pinned wheelhouse. На clean Spain отсутствуют system-site
`pydantic` и `pydantic_settings`. Локальный v7 откладывает этот import только
для package-bound path; source-only early validation сохранена.

```text
package_sha256=0752BD27A92B43BA804E094C4E6D2843460D78CD31DBD1B0F7481CDA4ADD35B6
package_bytes=139939840
manifest_sha256=79C92802B9D03D89702A3AE289619BFB701FFC0B94C5916F6E3A5B2014682A8B
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=3B076EE963DEFCAAE1BC488F71D9E1DE0870C041598E928B63A27E411EDE838F
executor_bytes=139848
runner_sha256=71D80808B494DABA1D8CB348CDEBA9C22FC5EA0FF4C85D1FD04E292A15349367
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_133_passed
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
