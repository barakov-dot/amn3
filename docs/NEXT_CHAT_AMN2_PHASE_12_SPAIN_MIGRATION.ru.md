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
v3 receipt=`passed`: recorded terminal contour verified removed,
foreign persistent equality=`true`, volatile counts=`0`.

v11 добавляет bounded category-only diagnostic для Docker image load. Он
сохраняет только allowlisted label (`no_space`, `archive`, `permission`,
`daemon_unavailable`, `layer_apply`, `unsupported` или exit code), никогда raw
stderr/output/secrets. Package/executor double-built byte-identical; package
verify и clean-room extract прошли.

```text
package_sha256=8975804C1D192F59FA94441A84DFCD7B5E0159505BBA5BE620B2FD23B675E154
package_bytes=139970560
manifest_sha256=B7124C5954D32E4FF08CA00E1897953651309BEB505E4067C2437ED946E26461
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
executor_bytes=144710
runner_sha256=139F74127C19C40153A5560C7F7ED73D82DFC88C5A64727CE12B399EAEEC40E2
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
terminal_recovery_receipt_v3=passed|verified_previously_removed_owned_objects|foreign_persistent_equal_true|volatile_before_0|volatile_after_0
terminal_recovery_receipt_mode=verify_only|requires_exact_removed_ledger|no_repeat_deletion
terminal_recovery_v3_local_verification=148_passed|semantic_firewall_regression_red_green|executor_double_build_byte_identical|offline_zip_verify_passed|unsupported_mode_fail_closed|diff_check_passed
fresh_install_upload_attempt=client_sftp_hung|terminated_local_before_executor|no_second_upload
fresh_install_remote_hash_attempt=failed_closed_before_executor|generic_upload_basename_vs_bound_temp_path
fresh_install_transport_policy=connect_timeout_20|server_alive_15x4|scp_hard_timeout_300_seconds
fresh_install_remote_temp_binding=package_to_amn2_spain_phase12_install_a_tar|executor_to_amn2_spain_phase12_executor_a_pyz
fresh_install_local_verification=package_executor_double_build_byte_identical|package_verify_passed|clean_room_extract_passed|source_55dc243_verified|scoped_151_passed|powershell_parse_passed
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
origin readback, then issue one fresh exact checksum-bound install approval.
The prior install approvals were consumed before executor invocation: first by
local SFTP transport hang, second by remote hash-path mismatch. They must not
be reused. Runner
uploads only the shown package/executor, verifies remote SHA, executes
install-bound with automatic rollback, and proves clean DB/zero peers/write
disabled/bot disabled/loopback web/AWG health/foreign equality. No blind reuse
of an old install approval.
