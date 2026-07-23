# Next task — AMN2 Phase 12 Spain Migration

Current state: v10 `install-bound` прошёл до intent `awg_image_loaded`
(`docker load`), но action не был committed. Automatic rollback удалил Docker
enable/start, все AMN2 units, DB/config/runtime objects. Receipt подтверждает:
AMN2 units inactive; foreign Spain service не останавливался и не изменялся;
USA остаётся rollback contour.

`manual-cleanup-bound` receipt=`passed`: CAS-verified retained
`/opt/amn2-spain-package` удалён, terminal ledger сохранён. Scoped read-only
receipt подтвердил inactive Docker/network/web/bot units. Foreign Spain
service не затрагивался.

Terminal recovery v2 удалил exact AMN2-owned contour `/etc/amn2-spain`,
`/opt/amn2-spain`, `/var/lib/amn2-spain*` и sealed Docker data-root. Immediate
read-only safety receipt подтвердил отсутствие package/runtime/path candidates
и inactive AMN2 Docker/network/web/bot units. Terminal ledger сохранён со
status=`manual_recovery_required`; foreign Spain service не останавливался и
не изменялся.

Первый terminal-recovery attempt fail-closed до delete: Linux scanner выдал
prefixed digest `sha256:<hex>`, а exact intent требует raw 64-hex. v2 исправил
digest и удалил contour, но затем fail-closed на старом equality adapter:
он ошибочно сравнивал owned `existing` inventory до/после. Новый executor
разрешает только этот expected AMN2 delta, по-прежнему требует persistent
foreign equality и записывает volatile fields. Его terminal-recovery receipt
mode строго verify-only: exact ledger обязан уже содержать все `removed`, иначе
он fail-closed без любой дополнительной mutation.

Первый receipt-only run остановился fail-closed на volatile raw nft hash между
двумя read-only samples; повторного удаления, AMN2 start или foreign-service
mutation не было. v3 сохраняет strict semantic firewall equality:
`backend=nft`, rule-count=`129`, semantic SHA=
`FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682`.
Raw counter/hash drift отдельно не является изменением firewall semantics.

v11 добавляет bounded category-only diagnostic для Docker image load. Он
сохраняет только allowlisted label (`no_space`, `archive`, `permission`,
`daemon_unavailable`, `layer_apply`, `unsupported` или exit code), никогда raw
stderr/output/secrets. Package/executor double-built byte-identical; package
verify и clean-room extract прошли.

```text
package_sha256=012CC689247DD411EACEF82882E5734A6BEC56C2FDE7D1F4224691E6CF457A47
package_bytes=139950080
manifest_sha256=1A394537C3F62626B19D21A2D33DBB087E5299C7726AD55783384FC95E7977D7
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=A22A05CF1D2D761C9FF80DA5F458C1C5FBE6AFDEF4476D57BEB8A3677E6731B3
executor_bytes=140908
runner_sha256=D6E639E9EA80D6D6ADA2D56BF443BE8710E8AE7C21CB6C1C0FC3860CDB3B8797
manual_cleanup=passed|package_tree_absent|terminal_ledger_preserved|units_inactive
manual_cleanup_executor_sha256=0E736B9DDF950DA050FE945F7D5F6D860F9C782A45066AE42429CCF56EF05585
manual_cleanup_executor_bytes=140277
terminal_recovery_nonce=e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd
terminal_recovery_transaction_sha256=C58ED7EC5EA40F47C7C65C4A6D4691667160F2444764679A285A9EE47BEC8788
terminal_recovery_capsule_sha256=FE7E203B3A772811489371C90CAB88E0247882882938045FD85D80709F6B63CC
terminal_docker_tree_sha256=2328DA44BF2BDF6FD831A1AA27B50DF5BCE8649FBBEF015808A01CCD389A1CF4
terminal_docker_tree=entries_916|bytes_41902300|mode_0710|block_rdev_64770|single_filesystem|nested_mounts_0
terminal_recovery_executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
terminal_recovery_executor_bytes=144710
terminal_recovery_runner_sha256=F5959D04CAE8E6BF534474D9CBD308228EF8B0EB424FDCC02F15DB6144BD1C89
terminal_recovery_attempt_v1=failed_closed_before_delete|linux_digest_prefix_mismatch|retained_objects_unchanged|opt_flock_available
terminal_recovery_attempt_v2=owned_terminal_contour_removed|equality_failed_closed_on_owned_inventory_comparator|foreign_untouched
terminal_recovery_receipt_attempt_v1=failed_closed_on_raw_firewall_projection_drift|no_additional_mutation
terminal_recovery_receipt_mode=verify_only|requires_exact_removed_ledger|no_repeat_deletion
terminal_recovery_v3_local_verification=148_passed|semantic_firewall_regression_red_green|executor_double_build_byte_identical|offline_zip_verify_passed|unsupported_mode_fail_closed|diff_check_passed
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_136_passed|package_bound_units_test_pass
spain_mutation=v10_attempt_rolled_back|manual_cleanup_package_tree_only|terminal_owned_contour_removed|no_active_amn2_runtime
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds, SOL
review, or security scans. Do not stop AWG. Do not stop or mutate the foreign
Spain service. Do not migrate/delete USA data.

Next gate: stage only Phase 12 files, commit and push current branch, verify
origin readback, then issue one exact checksum-bound terminal-recovery
receipt-only approval. Runner uploads only its executor, verifies its remote
SHA and can only validate the already-recorded `removed` contour and foreign
equality; it has no deletion branch. After a passed receipt, rebuild the
install package/executor and resume fresh install; no blind reuse of an old
install approval.
