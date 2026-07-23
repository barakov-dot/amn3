# Next task — AMN2 Phase 12 Spain Migration

Current state: v10 `install-bound` прошёл до intent `awg_image_loaded`
(`docker load`), но action не был committed. Automatic rollback удалил Docker
enable/start, все AMN2 units, DB/config/runtime objects. Receipt подтверждает:
AMN2 units inactive; foreign Spain service не останавливался и не изменялся;
USA остаётся rollback contour.

Transaction terminal=`manual_recovery_required`: retained только
CAS-verified `/opt/amn2-spain-package`; обычный recovery специально запрещён.
Локально подготовлен отдельный checksum-bound `manual-cleanup-bound` runner:
проверяет terminal nonce, tombstone и CAS tree, затем удаляет исключительно
этот retained tree, сохраняет ledger и не запускает AMN2/Docker.

```text
package_sha256=105379D86CF0BD5D02C54F2369C8A9A14DF075DC33601E7225B016E5EDEBCBEC
package_bytes=139939840
manifest_sha256=2A505C1CB7B1A734FF411A283930E54BD52D82342F08A26B775E2B185EF5F04D
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=1A20220F4EA7F75931C72CA538EE20FB4097D866650730739B89E081846217BF
executor_bytes=140147
runner_sha256=0530C9FB53AB7FABA9C8DB5B40862D7109C375F24B4CE7401910B67682EE2F3C
manual_cleanup_nonce=e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd
manual_cleanup_executor_sha256=0E736B9DDF950DA050FE945F7D5F6D860F9C782A45066AE42429CCF56EF05585
manual_cleanup_executor_bytes=140277
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_136_passed|package_bound_units_test_pass
spain_mutation=v10_attempt_rolled_back|no_active_amn2_runtime
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds, SOL
review, or security scans. Do not stop AWG. Do not stop or mutate the foreign
Spain service. Do not migrate/delete USA data.

Next gate: stage only Phase 12 files, commit and push current branch, verify
origin readback, then issue one exact checksum-bound manual cleanup approval.
The cleanup runner uploads only the new executor, verifies its remote SHA,
executes `manual-cleanup-bound` with short-lived stdin intent and returns a
terminal cleanup receipt. If it fails, no retry occurs until its exact cause is
read-only classified. Only after a passed cleanup receipt may a new fresh
install package gate be considered.
