# Next task — AMN2 Phase 12 Spain Migration

Current state: v7 тихая SCP upload/hash verification завершились. Затем
`install-bound` fail-closed до tombstone и любой AMN2 mutation: legacy
rollback receipt содержит плановый retained audit path
`/var/lib/amn2-spain-phase12-audit`, а прежняя проверка ошибочно считала его
collision. Foreign Spain service не останавливался и не изменялся; USA
остаётся rollback contour.

v8 разрешает только declared retained audit path; любой дополнительный
retained path остаётся fail-closed. Тест покрывает оба случая; тот же v8
validator прошёл на сохранённом sanitized Spain v7 evidence.

```text
package_sha256=3967208F804655CF6BDF8543D9B91E92A16373A952E5E9FF96DF80A7A6BAC3A2
package_bytes=139939840
manifest_sha256=3AF25ACA35E935833F4016A0732328060E6C4711C860936B6AB1A297CF076A9F
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=BC649AC0B5F4D64F350898E813D27D17B6013FDE564817961D5EE982BCE88E3D
executor_bytes=139882
runner_sha256=D4095801D4080B1BB01752EAD3C20BABF47903DBA05C07F4AB9BDC11DE1C2840
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_134_passed|saved_v7_evidence_precondition_pass
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
