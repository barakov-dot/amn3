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

Остаточный rollback contour не является install state: exact AMN2-owned
`/etc/amn2-spain`, `/opt/amn2-spain`, `/var/lib/amn2-spain*` и Docker data-root
ещё сохранены в terminal ledger. Fresh no-follow read-only receipt: Docker-root
`916` entries, `41902300` bytes, mode `0710`, один root-owned `0600`
single-link block inode rdev `64770`, one filesystem, nested mounts `0`.
Новый executor перепроверяет canonical tree SHA дважды; он удаляет только этот
sealed contour, сохраняет terminal ledger и не трогает foreign service.

Первый terminal-recovery attempt fail-closed до delete: Linux scanner выдал
prefixed digest `sha256:<hex>`, а exact intent требует raw 64-hex. Read-only
receipt подтвердил, что retained paths/ledger не изменились и `/opt` flock
available. v2 заменяет только этот digest format; прежний approval недействителен.

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
terminal_recovery_executor_sha256=A7F8465D56E76AFA96A8825BB12CCF66757DCC487BFCE28CE479CC3B50135FAF
terminal_recovery_executor_bytes=144052
terminal_recovery_runner_sha256=1FF164521C2C1C6A1606F5F9BC95FAF0DBD00F715069F2CB0A75AF3C07ECDB19
terminal_recovery_attempt_v1=failed_closed_before_delete|linux_digest_prefix_mismatch|retained_objects_unchanged|opt_flock_available
terminal_recovery_v2_local_verification=145_passed|executor_double_build_byte_identical|offline_verify_passed|diff_check_passed
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_136_passed|package_bound_units_test_pass
spain_mutation=v10_attempt_rolled_back|manual_cleanup_package_tree_only|no_active_amn2_runtime
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds, SOL
review, or security scans. Do not stop AWG. Do not stop or mutate the foreign
Spain service. Do not migrate/delete USA data.

Next gate: stage only Phase 12 files, commit and push current branch, verify
origin readback, then issue one exact checksum-bound terminal-recovery cleanup
approval. Runner uploads only its executor, verifies its remote SHA, rechecks
the sealed Docker tree and removes only the verified AMN2 residual contour.
After a passed cleanup receipt, rebuild the install package/executor and resume
fresh install; no blind reuse of an old install approval.
