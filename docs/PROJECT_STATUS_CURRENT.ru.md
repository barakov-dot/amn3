# Текущий override 2026-07-23: Phase 12 bounded install transport local gate

Checksum-bound terminal recovery v2 действительно удалил только exact
AMN2-owned terminal contour: `/opt/amn2-spain`, `/etc/amn2-spain`,
`/var/lib/amn2-spain*` и sealed Docker data-root. Immediate read-only safety
receipt подтвердил отсутствие `/opt/amn2-spain-package`, AMN2 paths/runtime и
четырёх AMN2 units (`is-active` exit=`4`). Terminal ledger остался
`manual_recovery_required`. Foreign Spain service не останавливался и не
изменялся; USA остаётся rollback contour.

Тот же run завершился fail-closed после удаления на ошибке старого equality
adapter: он требовал равенство `existing` inventory до/после, хотя terminal
recovery обязан удалить именно этот AMN2 inventory. Это не новая Spain
mutation. Новый executor разделяет owned delta и foreign equality: он требует
пустой AMN2 candidate inventory (кроме retained audit ledger), сравнивает OS,
Docker, firewall, listeners/routes/addresses и persistent foreign projection,
а `restart_count`/`bound_port_set` только фиксирует как volatile.

Первый receipt-only run остановился fail-closed на raw firewall hash между
двумя read-only samples. Это ожидаемо volatile для nft counters и уже не
является authoritative comparator: текущая Phase 12 policy закрепляет
`backend=nft`, rule-count=`129` и semantic SHA. v3 executor сравнил именно
эти stable fields и прошёл: `recovery_action=verified_previously_removed_owned_objects`,
foreign persistent equality=`true`, volatile counts=`0`. Повторного удаления,
AMN2 start или foreign-service mutation не было.

Первый approved install attempt не дошёл до executor: локальный `scp`/SFTP
transport завис без CPU и внешней TCP-сессии, поэтому был завершён только
локально после пяти минут. Второй upload не запускался; installer, AMN2 и
foreign service не были вызваны. Новый launcher ограничивает connect/liveness
и общий SCP upload 300 секундами, после чего fail-closed завершает только
локальный transport.

Fresh install package и executor дважды собраны byte-equal из тех же
sealed inputs; штатный no-follow clean-room verify/extract и source expansion
подтвердили source commit `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
Следующий gate: commit/push/origin readback, затем один exact checksum-bound
install approval. Он допускает только upload package/executor, remote hash
verification, install-bound и automatic rollback; foreign service immutable,
USA остаётся rollback contour.

```text
active_phase=AMN2 Phase 12 Spain Migration|terminal_recovery_receipt_only_gate
terminal_recovery_v2_live_outcome=owned_terminal_contour_removed|receipt_failed_closed_on_owned_inventory_comparator
terminal_recovery_live_safety=package_absent|opt_etc_var_owned_paths_absent|docker_root_absent|amn2_units_inactive|terminal_ledger_manual_recovery_required
terminal_recovery_receipt_attempt_v1=failed_closed_on_raw_firewall_projection_drift|no_additional_mutation
terminal_recovery_receipt_v3=passed|verified_previously_removed_owned_objects|foreign_persistent_equal_true|volatile_before_0|volatile_after_0
terminal_recovery_receipt_executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
terminal_recovery_receipt_executor_size=144710
terminal_recovery_receipt_runner_sha256=F5959D04CAE8E6BF534474D9CBD308228EF8B0EB424FDCC02F15DB6144BD1C89
terminal_recovery_receipt_local_verification=tests_148_passed|semantic_firewall_regression_red_green|executor_double_build_byte_equal|offline_zip_verify_passed|unsupported_mode_fail_closed|diff_check_passed
fresh_install_package_sha256=8975804C1D192F59FA94441A84DFCD7B5E0159505BBA5BE620B2FD23B675E154
fresh_install_package_size=139970560
fresh_install_manifest_sha256=B7124C5954D32E4FF08CA00E1897953651309BEB505E4067C2437ED946E26461
fresh_install_executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
fresh_install_executor_size=144710
fresh_install_runner_sha256=581C156D0A4ED838DA50388468A324D882BEA5E658E318A5226F2EEFFB408F56
fresh_install_upload_attempt=client_sftp_hung|terminated_local_before_executor|no_second_upload
fresh_install_transport_policy=connect_timeout_20|server_alive_15x4|scp_hard_timeout_300_seconds
fresh_install_local_verification=package_executor_double_build_byte_equal|package_verify_passed|clean_room_extract_passed|source_55dc243_verified|scoped_151_passed|powershell_parse_passed
terminal_recovery_nonce=E022F0B87A972F2256ACD7800A4999553A8CEEA2396A2644908F43C93A82FEBD
terminal_recovery_transaction_sha256=C58ED7EC5EA40F47C7C65C4A6D4691667160F2444764679A285A9EE47BEC8788
terminal_recovery_capsule_sha256=FE7E203B3A772811489371C90CAB88E0247882882938045FD85D80709F6B63CC
terminal_docker_tree_sha256=2328DA44BF2BDF6FD831A1AA27B50DF5BCE8649FBBEF015808A01CCD389A1CF4
spain_unrelated_service=untouched
usa_rollback_contour=unchanged
next_gate=commit_push_origin_readback_then_exact_checksum_bound_install_approval
```

`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся нетронутым.

# Предыдущий override 2026-07-23: Phase 12 terminal recovery cleanup local gate

v10 checksum-bound install дошёл до intent `awg_image_loaded` (`docker load`),
который не был committed. Automatic rollback удалил Docker enable/start, все
AMN2 units, DB, configs и runtime trees. Read-only safety receipt подтверждает:
все AMN2 units inactive; foreign Spain service не останавливался и не
изменялся. Единственный retained object — CAS-verified package tree
`/opt/amn2-spain-package`; ledger terminal=`manual_recovery_required`, поэтому
обычный recovery намеренно отказывается его удалять.

`manual-cleanup-bound` executor выполнен: short-lived
canonical stdin intent привязан к exact terminal nonce и SHA executor; перед
удалением он повторно проверяет ledger/tombstone и каждый CAS-объект retained
tree. Receipt=`passed`; `/opt/amn2-spain-package` отсутствует, terminal ledger
сохранён. AMN2 Docker/network/web/bot inactive; foreign service не затронут.

Остался только sealed AMN2-owned rollback contour: `/etc/amn2-spain`,
`/opt/amn2-spain`, `/var/lib/amn2-spain*` и exact Docker data-root. Read-only
no-follow receipt для data-root: `916` entries, `41902300` bytes, mode=`0710`,
один root-owned `0600`, single-link block inode rdev=`64770`; все entries на
одном filesystem, nested mounts=`0`. Cleanup policy снова проверяет весь
canonical tree SHA дважды перед unlink; non-block special files, mode/owner/link
drift и foreign filesystem остаются fail-closed. Foreign Spain service не
останавливается и не изменяется.

Первый terminal-recovery attempt остановился до удаления: Linux scanner вернул
`sha256:<hex>`, тогда как intent корректно требует raw `<hex>`. Read-only
receipt подтвердил неизменность всех nine retained objects, terminal ledger и
available `/opt` flock. v2 приводит Linux digest к raw 64-hex форме; новый
executor/runner checksum-bound заново и не переиспользует прежнее approval.

v11 сохраняет безопасный cause label для следующего `docker image load`:
`no_space`, `archive`, `permission`, `daemon_unavailable`, `layer_apply`,
`unsupported` или numeric `exit_code`. Raw stderr, command output и secrets
не записываются и не выводятся. Новый package/executor double-built
byte-identical; package verify и clean-room extract прошли.

v8 upload/hash verification завершились; `install-bound` прошёл precondition
и дошёл до `package_verified_remote`, затем fail-closed остановился в
pre-write production preparation. Automatic rollback receipt подтверждён:
transaction=`rolled_back`, все AMN2 units inactive, owned `/opt` и staging
absent. До `capsule_committed` и любых install actions дело не дошло, поэтому
foreign service не изменялся. Старый wrapper скрыл controlled внутреннюю
причину. v9 меняет только этот failure receipt: безопасно выводит bounded
Backend/PackageVerification cause label, не добавляя mutation.
v9 safe cause receipt установил root cause: standalone executor читал systemd
units из absent workspace path. v10 передаёт verified `content` root и читает
package units только из `content/units`; source-mode fallback сохранен. v10
package/executor double-build, verifier и clean-room extract прошли; scoped=`136 passed`.
Dynamic equality policy неизменна: persistent foreign identities должны
совпасть, volatile identities фиксируются receipt; `restart_count` и
`bound_port_set` volatile. Любое расхождение stable persistent fields
по-прежнему fail-closed; foreign service не останавливается и не изменяется.

```text
active_phase=AMN2 Phase 12 Spain Migration|terminal_recovery_cleanup_local_gate
phase12_package_archive_sha256=012CC689247DD411EACEF82882E5734A6BEC56C2FDE7D1F4224691E6CF457A47
phase12_package_archive_size=139950080
phase12_manifest_sha256=1A394537C3F62626B19D21A2D33DBB087E5299C7726AD55783384FC95E7977D7
phase12_resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
phase12_executor_sha256=A22A05CF1D2D761C9FF80DA5F458C1C5FBE6AFDEF4476D57BEB8A3677E6731B3
phase12_executor_size=140908
phase12_install_runner_sha256=D6E639E9EA80D6D6ADA2D56BF443BE8710E8AE7C21CB6C1C0FC3860CDB3B8797
phase12_manual_cleanup_nonce=e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd
phase12_manual_cleanup_executor_sha256=0E736B9DDF950DA050FE945F7D5F6D860F9C782A45066AE42429CCF56EF05585
phase12_manual_cleanup_executor_size=140277
phase12_manual_cleanup_local_verification=focused_contracts_4_passed|executor_double_build_byte_identical
phase12_manual_cleanup_outcome=passed|package_tree_absent|terminal_ledger_preserved|amn2_units_inactive
phase12_v10_install_outcome=automatic_runtime_rollback|manual_recovery_required|retained_package_tree_cleaned
phase12_terminal_recovery_nonce=e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd
phase12_terminal_recovery_transaction_sha256=C58ED7EC5EA40F47C7C65C4A6D4691667160F2444764679A285A9EE47BEC8788
phase12_terminal_recovery_capsule_sha256=FE7E203B3A772811489371C90CAB88E0247882882938045FD85D80709F6B63CC
phase12_terminal_docker_tree_sha256=2328DA44BF2BDF6FD831A1AA27B50DF5BCE8649FBBEF015808A01CCD389A1CF4
phase12_terminal_docker_tree=entries_916|bytes_41902300|mode_0710|block_rdev_64770|single_filesystem|nested_mounts_0
phase12_terminal_recovery_executor_sha256=A7F8465D56E76AFA96A8825BB12CCF66757DCC487BFCE28CE479CC3B50135FAF
phase12_terminal_recovery_executor_size=144052
phase12_terminal_recovery_runner_sha256=1FF164521C2C1C6A1606F5F9BC95FAF0DBD00F715069F2CB0A75AF3C07ECDB19
phase12_terminal_recovery_attempt_v1=failed_closed_before_delete|linux_digest_prefix_mismatch|retained_objects_unchanged|opt_flock_available
phase12_terminal_recovery_v2_local_verification=145_passed|executor_double_build_byte_identical|offline_verify_passed|diff_check_passed
phase12_v11_docker_load_diagnostic=allowlisted_stderr_category_only|raw_stderr_false
phase12_foreign_equality_policy=dynamic_persistent_v1
phase12_precondition_receipt=records_persistent_equality_and_volatile_before_after_counts
phase12_v6_install_outcome=rolled_back_before_amnezia_units_or_owned_paths
phase12_v7_install_outcome=precondition_failed_before_tombstone_or_amnezia_mutation|declared_retained_audit_path
phase12_v8_install_outcome=rolled_back_after_package_verified_remote_before_capsule_or_install_actions|foreign_untouched
phase12_v10_local_verification=double_build|package_verify|clean_room_extract|scoped_136_passed
phase12_firewall_semantic_rebaseline=nft|rule_count_129|semantic_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
phase12_scoped_tests=136_passed
phase12_package_executor_reproducible=byte_identical_double_builds
phase12_clean_room_verify_extract=passed
spain_mutation=v10_attempt_rolled_back|manual_cleanup_package_tree_only|no_active_amn2_runtime
spain_unrelated_service=untouched
usa_rollback_contour=unchanged
next_gate=commit_push_origin_readback_then_exact_terminal_recovery_cleanup_approval
```

`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся нетронутым.

# Архивный override 2026-07-21: Phase 12 checksum-bound package gate ready; awaiting separate read-only approval

Phase 12 local package gate завершён без SSH и без Spain mutation. Готовые
package и standalone executor собраны дважды byte-identical, offline
clean-room verify/extract прошёл, а независимый GPT-5.6 SOL review дал `GO`
без reportable findings. Повторять runs 001–009, builds, tests или review не
нужно. Следующий live gate — только отдельный checksum-bound read-only
resource confirmation; upload, install и любая mutation по-прежнему запрещены.

```text
active_phase=AMN2 Phase 12 Spain Migration|package_gate_ready
phase12_package_archive_sha256=76F941869C8985A1C01C904314D033D95205C7C25BF1D9F46E795A3A389C5EA9
phase12_package_archive_size=139909120
phase12_manifest_sha256=B21B00A20B939B1A3B83E6CE32EFC37138C4A8E72110379D3FA0A49BD8C1E69A
phase12_resource_plan_sha256=F313D5943E2EC142051735F0EF98CAEE6A453751E76BC7281830F5A2B44D8A0C
phase12_executor_sha256=CFDC31A2D2576AECEB0630302B382DBD131508A6C9CA64FF59A2DD930D4DA23E
phase12_executor_size=109116
phase12_package_executor_reproducible=byte_identical_double_builds
phase12_clean_room_verify_extract=passed
phase12_independent_review=GO|no_reportable_findings
phase12_next_live_gate=separate_exact_read_only_resource_confirmation_approval
spain_mutation=false
spain_unrelated_service=untouched
production_awg=untouched
```

`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся нетронутым.

# Текущий override 2026-07-21: Spain preflight 009 passed; Phase 12 migration entry ready

Финальный single-use outcome `spain-fresh-20260721-009` завершился успешно.
Checksum-bound runner записал sanitized evidence SHA-256
`8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8`.
Run 009 consumed и не повторяется.

```text
active_phase=Post-release controlled operations|ready_for_phase12_spain_migration
phase11_status=completed-controlled-private-release|unchanged
spain_run_009=passed|approval_consumed|never_repeat
spain_run_009_claim=present
spain_run_009_success_evidence=present|sanitized|schema_v1
spain_run_009_failure_evidence=absent
spain_os=linux
spain_capacity=cpu_1|memory_kib_984564|root_disk_bytes_10479628288
spain_docker=absent|phase12_install_required
spain_systemd=present
spain_firewall=nft|rules_129
spain_listening_ports=tcp_22_53_443_8080_10050|udp_53_443
spain_unrelated_fingerprint_entries=148|baseline_sealed_for_post_install_equality
spain_preflight_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
fresh_install_gate=ready_for_separate_phase12_exact_approval
next_phase=AMN2 Phase 12 Spain Migration
```

Preflight pass не разрешает install. Phase 12 должна выбрать conflict-free
AMN2 names, Docker network, VPN subnet и ports, не используя занятые ports;
установить Docker как отдельную allowlisted mutation; сохранить и после каждого
этапа точно сравнить unrelated-service fingerprint. USA остаётся rollback
contour до полного Spain acceptance и реальной выдачи новых конфигов.

Phase 12/13 пакет:

- `docs/AMN2_PHASE_12_SPAIN_MIGRATION_FIRST_MESSAGE.ru.md`;
- `docs/AMN2_PHASE_12_SPAIN_MIGRATION_ENTRY.ru.md`;
- `docs/NEXT_CHAT_AMN2_PHASE_12_SPAIN_MIGRATION.ru.md`;
- `docs/AMN2_PHASE_13_POST_MIGRATION_CONTINUATION_FIRST_MESSAGE.ru.md`.

`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся нетронутым.

# Текущий override 2026-07-21: run 008 доказал CRLF stdin defect; финальный run 009 готовится

Literal approval `spain-fresh-20260721-008` использована один раз. Outcome
создал claim и остановился fail-closed до sanitized evidence: PowerShell native
object pipeline добавил Windows CRLF после LF-terminated probe, а remote Bash
увидел отдельный carriage return после последней строки. Probe-файл проверен:
`434 LF`, `0 CRLF`, последний byte `0A`; Spain VPS не является источником CR.

Локальная TDD-коррекция заменяет object pipeline на exact byte forwarding через
redirected `StandardInput.BaseStream`. Проверенные probe bytes читаются из того
же checksum-validated stream, command-line arguments экранируются по Windows
CreateProcess rules, stdout/stderr остаются только в памяти.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_008=fail_closed|approval_consumed|never_repeat
spain_run_008_claim=present
spain_run_008_failure_evidence=absent
spain_run_008_success_evidence=absent
spain_run_008_root_cause=local_powershell_pipeline_appended_crlf
spain_exact_byte_transport=implemented_locally|tdd_verified
spain_next_outcome_run=spain-fresh-20260721-009|not_created|not_run|approval_required|final_allowed_attempt
spain_immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=26ED19344B9E7F56069BFEBAC9864BB5779B413767312B4AAB411B7DBF859D76
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=focused_33_passed|full_209_passed
remaining_live_attempt_cap=run_009_only_then_stop_and_switch_approach
fresh_install_gate=blocked_until_run_009_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Run `009` — последний разрешённый preflight attempt. При любом неуспехе новые
runner/retry не создаются: дальнейшая диагностика только через provider console
или иной согласованный подход. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`
остаётся нетронутым.

# Текущий override 2026-07-21: safe envelope rejection diagnostic готов для run 008

Локальная TDD-коррекция завершена. Строгий failure-envelope parser не
ослаблен: если prefix присутствует, но parser отклоняет envelope, runner
сохраняет только `classification=envelope_rejected`, `stage=unavailable`,
безопасный process exit и одну allowlisted причину. Raw OpenSSH output и
разобранные remote values не сохраняются.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_envelope_rejection_diagnostic=implemented_locally|tdd_red_green_verified
spain_envelope_rejection_allowlist=prefix_count|shape|stage|exit|stage_exit_mapping|unavailable
spain_next_outcome_run=spain-fresh-20260721-008|not_created|not_run|approval_required
spain_immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=C4F00EC9E0C53D9B9582B083ED8598BD3CB3F7DC202AA638AF7B197F8B730652
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=focused_30_passed|full_206_passed
remaining_live_attempt_cap=run_008_then_at_most_one_proven_fix_run_009
fresh_install_gate=blocked_until_run_008_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Run `008` ещё не создан и не выполнялся. Он требует отдельной exact single-use
approval после commit/push/origin readback. Если `008` докажет конкретную
исправимую причину, допускается максимум один новый `009`; иначе диагностика
переносится в provider console/другой подход. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`
остаётся нетронутым.

# Текущий override 2026-07-21: Spain run 007 fail-closed на envelope rejection

Literal approval для `spain-fresh-20260720-007` использована ровно один раз.
Runner получил как минимум одну строку с failure prefix, но строгий parser
отклонил envelope до построения sanitized failure JSON. Outcome содержит claim;
success evidence и failure evidence отсутствуют. Raw OpenSSH output намеренно
не сохранён, поэтому stage/exit/subreason не утверждаются и retry запрещён.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_007=fail_closed|approval_consumed|never_repeat
spain_run_007_classification=envelope_rejected
spain_run_007_prefix=present
spain_run_007_parser_result=rejected
spain_run_007_stage=not_proven
spain_run_007_exit=not_proven
spain_run_007_claim=present
spain_run_007_failure_evidence=absent
spain_run_007_success_evidence=absent
spain_next_outcome_run=spain-fresh-20260721-008|required_after_safe_envelope_rejection_diagnostic
fresh_install_gate=blocked_until_new_preflight_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Локальный synthetic test подтвердил, что PowerShell корректно передаёт exact
prefix/envelope и сохраняет process exit; следовательно, generic stream/cast
дефект не воспроизведён. Нужен отдельный fail-closed diagnostic contract,
который различит safe причины parser rejection без raw values. До него SSH не
выполнять. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся нетронутым.

# Предыдущий override 2026-07-20: Spain transport subreason diagnostic готов для run 007

Локальная TDD-коррекция завершена. Runner будущего outcome `007` получает
OpenSSH output только во временную память, при `exit=255` возвращает ровно одну
allowlisted transport category и очищает raw values до создания sanitized
failure evidence. Unknown, ambiguous и non-255 inputs остаются `unavailable`.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_transport_subreason_diagnostic=implemented_locally|tdd_red_green_verified
spain_transport_capture=in_memory_only|cleared_before_evidence_write
spain_transport_subreason_allowlist=connect_timeout|connection_refused|no_route|name_resolution|host_key|authentication|remote_closed|remote_reset
spain_next_outcome_run=spain-fresh-20260720-007|not_created|not_run|approval_required
spain_immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=9A6BCA57930A685B6D8B997E85972336A37F289D7D39073058EDAD4625DC34A3
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=focused_29_passed|full_205_passed
fresh_install_gate=blocked_until_run_007_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Run `007` ещё не создан и не выполнялся. Новая exact single-use approval
действительна только после commit/push/origin readback этой версии. Runs
`001`–`006` не повторять. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся
вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain run 006 fail-closed на transport boundary

Literal approval для `spain-fresh-20260720-006` использована ровно один раз.
Checksum-bound runner создал claim, но не получил remote failure envelope:
sanitized evidence содержит только `classification=transport`,
`stage=unavailable`, `subreason=unavailable`, `exit=255`. Поэтому Spain OS,
capacity, ports, Docker, systemd, firewall, SSH policy, clock и unrelated
service не подтверждены этим run; повтор и blind remediation запрещены.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_006=fail_closed|approval_consumed|never_repeat
spain_run_006_classification=transport
spain_run_006_stage=unavailable
spain_run_006_subreason=unavailable
spain_run_006_exit=255
spain_run_006_claim=present
spain_run_006_failure_evidence=present|sanitized
spain_run_006_success_evidence=absent
spain_next_outcome_run=spain-fresh-20260720-007|required_after_transport_diagnostic
spain_immutable_trust_bundle=spain-fresh-20260720-001
fresh_install_gate=blocked_until_new_preflight_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Нужен отдельный local-only transport diagnostic contract, который даст
allowlisted subreason без raw OpenSSH output/private target disclosure. До
этого SSH не выполнять. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся
вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain render subreason diagnostic готов для run 006

Локальная TDD-коррекция для render stage завершена: probe до JSON rendering
проверяет только существующие зависимости `sha256sum`, `cut`, `tr`, `awk`,
`sort`, `paste` и выдаёт safe пары `render/81..86`. Runner принимает только
точные пары и сохраняет лишь allowlisted `subreason`, без raw command output,
private target или иных remote values. `spain-fresh-20260720-006` ещё не
создан и не выполнялся; run `005` остаётся consumed и не повторяется.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_render_subreason_diagnostic=implemented_locally|tdd_red_green_verified
spain_render_subreason_allowlist=sha256sum|cut|tr|awk|sort|paste
spain_render_subreason_exit_allowlist=81|82|83|84|85|86
spain_next_outcome_run=spain-fresh-20260720-006|not_created|not_run|approval_required
spain_immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=FF9D9B731A2AEE12C7E1A98CA0AACB8B533F051D666E1D4C4352BFDE0F6B143D
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=focused_28_passed|full_204_passed
fresh_install_gate=blocked_until_run_006_success
spain_mutation=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
```

Новая exact single-use approval может быть выдана только после commit/push,
origin readback и final diff/security review этой локальной коррекции.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain run 005 fail-closed на render stage

Literal approval для `spain-fresh-20260720-005` использована ровно один раз.
Checksum-bound read-only probe дошёл до удалённого render stage и завершился
sanitized failure: `classification=remote_probe`, `stage=render`,
`subreason=unavailable`, `exit=127`. Claim и failure evidence присутствуют,
success evidence отсутствует; runner/probe/source bindings совпали. Retry
запрещён.

Локальная проверка reviewed remote probe показывает, что render stage собирает
redacted JSON через shell helpers и внешние утилиты; текущий sanitized envelope
не раскрывает, какая именно команда отсутствует. Требуется отдельный локальный
stage-coded diagnostic contract для render subreason без raw output/private
values, затем новый outcome run `spain-fresh-20260720-006` и новая exact
single-use read-only approval. Fresh-install/Phase12 migration gate остаётся
закрытым до успешного Spain preflight.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_004=fail_closed|approval_consumed|never_repeat
spain_empty_cgroup_correction=implemented|tdd_red_green_verified
spain_run_005=fail_closed|approval_consumed|never_repeat
spain_run_005_classification=remote_probe
spain_run_005_stage=render
spain_run_005_subreason=unavailable
spain_run_005_exit=127
spain_run_005_claim=present
spain_run_005_failure_evidence=present|sanitized
spain_run_005_success_evidence=absent
spain_next_outcome_run=spain-fresh-20260720-006|required_after_render_diagnostic
spain_immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=B45764A57E4258C8DD1AFC1570FE5F4359C755C146449225EAC0B74044E3F3F1
runner_sha256=B42EEE2ED6D63DDC81BCDAF337B9A1581757C8B1E5B1475FACFF69322DD75C82
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
correction_commit=34628ddb0dd32022609313c1b4c54d31295edab8|origin_verified
tests=focused_27_passed|full_203_passed|bash_powershell_parse_pass
security=codex_diff_scan_complete|reportable_findings_0|secret_matches_0
fresh_install_gate=blocked_until_new_preflight_success
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=DESIGN_RENDER_STAGE_SUBREASON_DIAGNOSTIC_THEN_NEW_EXACT_PREFLIGHT_006_GATE
```

Run `005` повторять нельзя. Новая authority появится только после отдельного
render diagnostic correction, commit/push/origin readback и возврата новой
полностью совпадающей literal approval для нового outcome. Runs `001`–`005` не
повторять; blind remediation запрещён.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain run 004 fail-closed на пустом cgroup process list

Literal approval для `spain-fresh-20260720-004` использована ровно один раз.
Checksum-bound read-only probe дошёл до systemd port collector и завершился
sanitized failure: `classification=remote_probe`,
`stage=systemd_cgroup_ports`, `subreason=pid`, `exit=76`. Claim и failure
evidence присутствуют, success evidence отсутствует; runner/probe/source
bindings совпали. Retry запрещён.

Локальная Bash reproduction доказала root cause без нового SSH: here-string с
пустым результатом `cgroup.procs` выполняет одну `while read`-итерацию с пустым
значением. Collector ошибочно классифицирует штатный cgroup без живых процессов
как invalid PID. Требуется отдельный TDD correction contract: zero process rows
должны давать полный пустой port set, а любая непустая строка по-прежнему должна
быть строго числовым PID и fail-closed при нарушении.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_004=fail_closed|approval_consumed|no_retry
spain_run_004_classification=remote_probe
spain_run_004_stage=systemd_cgroup_ports
spain_run_004_subreason=pid
spain_run_004_exit=76
spain_run_004_claim=present
spain_run_004_failure_evidence=present|sanitized
spain_run_004_success_evidence=absent
spain_bindings=runner_match|remote_match|source_match
root_cause=empty_cgroup_procs_here_string_synthetic_empty_pid_iteration
fresh_install_gate=blocked_until_corrected_preflight_pass
spain_install_restart_stop_config=false
spain_unrelated_service=read_only_observation_only|no_mutation
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=DESIGN_EMPTY_CGROUP_PROCS_ZERO_LIVE_PID_SUCCESS_CONTRACT_THEN_NEW_EXACT_GATE
```

Private target/login, unit/PID/FD/path/socket values, raw SSH output, keys,
host-pin bytes и configs не добавлены в Git/evidence.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain cgroup-port subreason gate готов для run 004

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Причина fail-closed run `003`
локально разложена на шесть безопасных подпричин без раскрытия unit, PID, FD,
пути, socket inode или raw output. Remote collector теперь вызывается напрямую,
а не через command substitution, и возвращает либо нормализованный port set,
либо одно allowlisted состояние: `cgroup_procs`, `pid`, `fd_directory`,
`fd_readlink`, `socket_table`, `socket_parse`.

Runner принимает эти значения только как точные пары
`systemd_cgroup_ports/exit=75..80`, сохраняет в failure evidence только
allowlisted `subreason` и отклоняет неизвестную пару. Он checksum-bound к новым
probe bytes и к отдельному single-use outcome `spain-fresh-20260720-004`;
immutable trust bundle остаётся `spain-fresh-20260720-001`.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_003=fail_closed|approval_consumed|no_retry
spain_subreason_diagnostic=implemented_locally|verified
spain_subreason_allowlist=cgroup_procs|pid|fd_directory|fd_readlink|socket_table|socket_parse
spain_subreason_exit_allowlist=75|76|77|78|79|80
spain_next_outcome_run=spain-fresh-20260720-004|not_created|not_run
spain_immutable_trust_bundle=spain-fresh-20260720-001
spain_runner_sha256=E3A252F0FD62757419BA0E66746DC44AD8F7F5FC4A4149674B822E09CAEFA6E8
spain_remote_probe_sha256=59826109915A5D21C0B14775392205B672DD33E82AFAA4FB61A49C802A135623
spain_runner_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=spain_preflight_focused_27_passed|root_full_203_passed|bash_powershell_parse_pass|diff_check_pass
security=independent_diff_review_medium_1_closed|fixed_snapshot_clean|reportable_findings_0|secret_matches_0
spain_network_contact_after_run_003=false
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=COMMIT_PUSH_VERIFY_ORIGIN_THEN_ISSUE_EXACT_SINGLE_USE_SPAIN_PREFLIGHT_004_APPROVAL
```

До возврата буквальной approval для run `004` запрещены SSH, outcome creation,
install, remediation и любые изменения сервисов. Private target, login,
unit/PID/FD/path/socket values, raw diagnostics, key/host-pin bytes и конфиги в
Git/evidence не добавлены. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся
вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain run 003 fail-closed на systemd cgroup ports

Literal approval для `spain-fresh-20260720-003` использована ровно один раз.
Local binding, keypair и host pin прошли, SSH выполнил checksum-bound read-only
probe. Probe остановился fail-closed и создал только sanitized failure evidence:
`classification=remote_probe`, `stage=systemd_cgroup_ports`, `exit=1`.
Runner/probe/source bindings совпали; success evidence отсутствует.

Текущий envelope безопасно локализует collector group, но не различает внутри
него cgroup.procs, disappearing PID/FD, readlink и socket-table failures.
Поэтому retry и blind remediation запрещены; требуется новый локальный
subreason diagnostic contract и отдельная будущая approval.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_003=fail_closed|approval_consumed
spain_run_003_classification=remote_probe
spain_run_003_stage=systemd_cgroup_ports
spain_run_003_exit=1
spain_run_003_claim=present
spain_run_003_failure_evidence=present|sanitized
spain_run_003_success_evidence=absent
spain_bindings=runner_match|remote_match|source_match
spain_retry=false|new_contract_and_exact_approval_required
spain_install_restart_stop_config=false
spain_unrelated_service=read_only_observation_only|no_mutation
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=DESIGN_SYSTEMD_CGROUP_PORTS_SUBREASON_DIAGNOSTIC_WITHOUT_LIVE_ACTION
```

Private target, login, unit names, PID/FD data, raw SSH output, key/host-pin
bytes и конфиги не добавлены в Git/evidence.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain LocalAppData binding correction готова для run 003

Literal approval для `spain-fresh-20260720-002` была использована ровно один
раз. Runner остановился fail-closed до outcome claim и до SSH: защищённая
LocalAppData-копия `target.env` сохраняла старый workspace `SSH_KEY_PATH` и не
совпала с новым dedicated key path. Run `002` не повторялся.

После отдельного approval изменено только private поле `SSH_KEY_PATH`.
Target/user/expected host pin и bytes private/public key и known-hosts сохранены;
старый binding оставлен как protected backup. Owner/ACL/no-reparse, binding,
keypair и host-pin локально проверены без SSH. Runner переведён на новый
single-use outcome `spain-fresh-20260720-003`.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_run_002=fail_closed_before_outcome_and_ssh|approval_consumed
spain_run_002_cause=localappdata_binding_old_workspace_key_path
spain_run_002_outcome=absent
spain_binding_correction=ssh_key_path_only|verified|protected_backup_retained
spain_binding_preserved=target|user|host_pin|private_public_key_and_known_hosts_bytes
spain_next_outcome_run=spain-fresh-20260720-003|not_created|exact_approval_required
spain_runner_sha256=A27CC666EF47D6AF5983217169CFB3002F41E5A70DAF625EE3A422DAFB59FAEE
spain_remote_probe_sha256=3C8B341EC813776733835D39193F451E4FC21665851E1DCDADEFE69AD9D9BA0D
tests=spain_preflight_focused_24_passed|root_full_200_passed|bash_powershell_parse_pass|diff_check_pass
security=independent_diff_review_clean|reportable_findings_0|stale_run_fail_closed
spain_network_contact_run_002=false
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=COMMIT_PUSH_VERIFY_ORIGIN_THEN_ISSUE_EXACT_SINGLE_USE_SPAIN_PREFLIGHT_003_APPROVAL
```

Private target/login/key/host-key bytes не добавлены в Git или evidence.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain MainPID fallback correction готов локально

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Последний Spain outcome run
`spain-fresh-20260720-001` остаётся consumed и immutable. Его stage-coded
failure receipt безопасно локализовал причину: активный сторонний systemd unit
имел пустой `ControlGroup` и `MainPID=0`, то есть был one-shot service без
живого процесса, а старый probe ошибочно требовал cgroup.

Локально реализован и проверен corrected resolver: непустой `ControlGroup`
сохраняет прежний путь; `MainPID=0` получает явный статус
`active_exited_no_live_process`; `MainPID>0` использует строгий procfs parser,
проверяет canonical systemd unit id и стабильность PID/starttime/cgroup до
признания port evidence полным. Security review дополнительно закрыл PID reuse
и локальную ACL/reparse race: новый outcome `spain-fresh-20260720-002`
создаётся отдельно от immutable trust bundle `001`, после current-user-only
из заранее подготовленного current-user-only `%LOCALAPPDATA%\AMN2` trust root;
runner до любого trust read проверяет owner/ACL/no-reparse всей private chain.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_trust_bundle=spain-fresh-20260720-001|immutable|consumed
spain_next_outcome_run=spain-fresh-20260720-002|not_created|exact_approval_required
spain_mainpid_fallback=local_implementation_verified|live_not_run
spain_mainpid_zero=active_exited_no_live_process|no_false_ports
spain_mainpid_live=canonical_unit_bound|starttime_and_cgroup_stable|fail_closed_71_74
spain_outcome_root=localappdata_current_user_only_parent_chain|no_reparse|create_new
spain_runner_sha256=ACA990D94D2730ADBE022F44A3EBFCD3ABD6FE14A598889244DD80038D60B76F
spain_remote_probe_sha256=3C8B341EC813776733835D39193F451E4FC21665851E1DCDADEFE69AD9D9BA0D
spain_runner_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tdd=mainpid_and_procfs_red_green|new_outcome_red_green|security_regressions_red_green
tests=spain_preflight_focused_24_passed|root_full_200_passed|bash_powershell_parse_pass|diff_check_pass
security=independent_fixed_snapshot_review_clean|remote_2_of_2|runner_2_of_2|reportable_findings_0
spain_network_contact_after_run_001=false
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=COMMIT_PUSH_VERIFY_ORIGIN_THEN_ISSUE_EXACT_SINGLE_USE_SPAIN_PREFLIGHT_002_APPROVAL
```

Evidence:
`docs/POST_RELEASE_SPAIN_SYSTEMD_MAINPID_FALLBACK_IMPLEMENTATION_EVIDENCE.ru.md`.
Старые approvals не разрешают новый запуск. Private target, login, key,
host-key line, raw diagnostics и конфиги в Git/evidence не добавлялись.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-20: Spain stage-coded diagnostic gate готов локально

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Вторая отдельно разрешённая Spain
read-only попытка также завершилась fail-closed до evidence: SSH вернул
ненулевой status, а прежний runner намеренно не сохранял raw stderr/stdout и не
мог различить transport от конкретного collector. Approval исчерпан, retry не
выполнялся.

Локально реализован отдельный stage-coded diagnostic contract. Remote failure
передаёт только allowlisted stage и exit code; runner фиксирован на exact trust
run id, создаёт single-use claim до SSH и атомарно записывает либо success
evidence, либо sanitized failure evidence. Никакой live-запуск новым кодом не
производился.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_trust_run_id=spain-fresh-20260720-001|exact_required
spain_preflight_attempt_1=fail_closed_before_evidence|approval_consumed
spain_preflight_attempt_2=fail_closed_before_evidence|approval_consumed|unclassified_nonzero_ssh
spain_preflight_success_evidence=absent
spain_preflight_failure_evidence=absent|new_contract_not_run
spain_preflight_outcome_claim=absent|new_contract_not_run
spain_stage_diagnostic=local_implementation_verified|live_not_run
spain_failure_envelope=allowlisted_stage|exit_1_255|no_raw_stderr_or_command
spain_single_use=fixed_trust_run_id|create_new_claim|success_failure_mutually_exclusive
spain_runner_sha256=E754737965E994FE1C2E828785345E3078E2716514BA33EA84688176304B4CF1
spain_remote_probe_sha256=16CE3F9E14A72DFB0DC957B2A1CA13F1ADBCA72F41C60FC2D4DD9904D3E74CD6
spain_runner_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tdd=bash_red_green|runner_red_green|mixed_envelope_red_green|explicit_exit_red_green
tests=spain_preflight_focused_16_passed|root_full_192_passed|bash_powershell_parse_pass|diff_check_pass
security=scan_ee02fcd_bf33180_20260720T090425Z|coverage_3_of_3|deferred_0|findings_0
spain_network_contact_after_attempt_2=false
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=COMMIT_PUSH_VERIFY_ORIGIN_THEN_ISSUE_SEPARATE_EXACT_STAGE_DIAGNOSTIC_APPROVAL
```

Evidence:
`docs/POST_RELEASE_SPAIN_PREFLIGHT_STAGE_DIAGNOSTIC_IMPLEMENTATION_EVIDENCE.ru.md`.
Design `f5e22e4` и implementation plan `ee02fcd` исполнены локально. Старые
approvals не разрешают новый запуск. Private target, login, key, host-key line и
raw remote diagnostics в Git/evidence не добавлялись.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Текущий override 2026-07-20: Spain read-only preflight fail-closed, corrected gate ожидает новый approval

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Первый отдельно разрешённый Spain
read-only preflight был запущен ровно один раз и завершился fail-closed до
создания evidence: обязательный `nft list ruleset` вернул безопасное
диагностическое предупреждение в stderr, которое Windows PowerShell преобразовал
в terminating `NativeCommandError`. Повторный SSH-запуск не выполнялся.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_trust_run_id=spain-fresh-20260720-001|unchanged
spain_preflight_attempt_1=fail_closed_before_evidence|approval_consumed
spain_preflight_attempt_1_evidence=absent
spain_preflight_attempt_1_cause=nft_diagnostic_stderr_to_powershell_native_command_error
spain_remote_probe_correction=exact_nft_stderr_suppression_only|nonzero_status_preserved|set_e_preserved
spain_runner_sha256=E2A00A9FDF3C1176300CA2B75ED3BDB9EEF6A62A7E8CAB9609C3414C120B14A8
spain_remote_probe_sha256=4B73C2E892D9BF64F7A3F2840DB22C6124A990506DA8A8558E5D59E9510A4AF3
spain_runner_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=spain_preflight_focused_9_passed|root_full_185_passed|bash_powershell_parse_pass|diff_check_pass
security=scan_8291665_3731823_20260720T074034Z|coverage_3_of_3|findings_0
spain_preflight_retry=false|new_exact_approval_required_after_origin_sync
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
telegram=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=COMMIT_PUSH_VERIFY_ORIGIN_THEN_ISSUE_NEW_EXACT_READ_ONLY_PREFLIGHT_APPROVAL
```

Evidence:
`docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_NFT_STDERR_CORRECTION_EVIDENCE.ru.md`.
Исправление подавляет только stderr точной диагностической команды `nft list
ruleset`; её ненулевой код возврата по-прежнему закрывает remote probe через
`set -euo pipefail`. Старый literal approval повторно использовать нельзя.
Private target, login, key и host-key line в Git/evidence не добавлялись.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Текущий override 2026-07-20: dedicated Spain SSH trust state полностью подготовлен

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Реальный Windows OpenSSH integration
test выявил и закрыл две fail-closed несовместимости локального onboarding:
передачу пустой passphrase в `ssh-keygen` и допустимый comment в выводе
`ssh-keygen -y`. Dedicated Spain key создан локально, защищён ACL и исключён из
Git. Оператор установил public key через provider console и передал out-of-band
host-key evidence; private binding и strict host pin локально созданы только
после точного совпадения fingerprint. SSH-соединение со Spain не выполнялось.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_trust_run_id=spain-fresh-20260720-001
spain_dedicated_key=prepared_local|ed25519|acl_current_user_only|git_ignored
spain_operator_public_key_fingerprint=SHA256:22zMZFDsPF5SrU5tiF7k27aWvXEMmXwyjqw+CSyYqns
spain_provider_console_public_key=installed|operator_evidence_received
spain_private_target_binding=prepared_local|four_line_schema|acl_current_user_only
spain_independent_host_pin=verified_local|fingerprint_exact_match|strict_known_hosts_ready
spain_onboarding_sha256=EB725B63723949D6EFF71C691C31695FBEDA44B555F6F3591C6E426263E3DCD2
spain_runner_sha256=0F27113DEA48F8F4443CDCA6628F5D6527E7036F407447B6288595AD0FCCF5AC
spain_remote_probe_sha256=5485260DF91713B742E45793C079F6A18BC1B83D54AF72556EB8E6A3CC0AB345
spain_runner_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
tests=spain_focused_22_passed|root_full_185_passed|powershell_parse_pass
security=scan_2071578_b7eaf7d_20260720T055655Z|coverage_4_of_4|findings_0
spain_network_contact=false
spain_preflight=false|exact_approval_required
spain_install_restart_stop_config=false
spain_unrelated_service=untouched
production_awg=untouched
protected_monitor_baseline=untouched
next=ISSUE_EXACT_READ_ONLY_PREFLIGHT_APPROVAL_THEN_AFTER_LITERAL_APPROVAL_RUN_ONCE
```

Evidence:
`docs/POST_RELEASE_SPAIN_SSH_WINDOWS_COMPATIBILITY_EVIDENCE.ru.md`.
Private key, target address, login и host-key line не входят в Git или evidence.
Старый approval, связанный с AMN2 `51fd...`, недействителен. Новый literal
approval связан с runner `0F2711...`, remote probe `548526...` и source
`55dc243...`; без его отдельного возврата SSH запрещён.

# Предыдущий override 2026-07-20: indefinite multi-slot operator issuance готова локально

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Локальный операторский контур для
новых Spain-конфигов теперь поддерживает несколько бессрочных неназначенных
access slots одному получателю без фиктивных Device Passports.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
operator_unassigned_slots=local_implementation_verified|live_not_run
amn2_source=codex-vps-test-prep|55dc243b8e6c6bdb57f8301b56326e4cd4072d19
default_expiry=indefinite|duration_days_null|expires_at_null
multi_slot=quantity_1_100|expanded_cap_100|stable_01_04_naming
identity=NEOBYATNAYA.NET-recipient-sequence|physical_device_unknown_allowed
passport=none_until_explicit_later_assignment
idempotency=request_fingerprint|exact_replay|safe_receipts
admission=full_batch_quota_and_filename_collision_before_mutation
lifecycle=independent_disable_revoke|remote_first|partial_failure_explicit
later_assignment=one_passport|stored_fingerprint|peer_ip_filename_unchanged
cli=dry_run_mutation_free|apply_configured_admin_and_exact_live_gate
target_binding=name_host_ssh_port_endpoint_vpn_port
amn2_tests=focused_61_passed|full_1029_passed_1_skipped_1_preexisting_warning
amn2_security=diff_check_pass|added_line_secret_matches_0|reportable_findings_0
spain_network_contact=false
spain_install_restart_stop_config=false
production_bot_web_database=not_contacted|unchanged
production_awg=untouched
protected_monitor_baseline=untouched
next=PUSH_VERIFY_AMN2_AMN3_THEN_PREPARE_DEDICATED_SPAIN_TRUST_STATE
```

Evidence:
`docs/POST_RELEASE_OPERATOR_UNASSIGNED_SLOTS_IMPLEMENTATION_EVIDENCE.ru.md`.
Никакие конфиги ещё не генерировались и Spain не контактировалась. Следующий
live шаг требует отдельного exact approval после private SSH trust onboarding.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Текущий override 2026-07-19: Spain fresh-start issuance и read-only gate готовы локально

Phase 11 остаётся закрытой как `completed-controlled-private-release`; работа
идёт в post-release controlled operations. Для будущего чистого развёртывания
на Spain подготовлены локальная операторская выдача новых конфигов и отдельный
fail-closed контур доверия к VPS. Живой Spain preflight и установка не запускались.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
spain_fresh_start=local_implementation_ready|live_not_run
amn2_source=codex-vps-test-prep|51fdba29ee1b33442bd109a0d0611c4d1348f4da
spain_operator_issuance=recipient_and_device_label|canonical_neobyatnaya_net_identity|device_passport|admin_only_delivery
spain_manifest=idempotent|normalized_duplicate_rejected_before_mutation|stable_request_replay
spain_ssh_onboarding=dedicated_ed25519|private_target_binding|independent_host_key_pin|local_only
spain_readonly_preflight=checksum_bound_runner_and_remote_probe|exact_amn2_source|approval_required|not_run
spain_runner_sha256=4000D3B21549EBF96C773DF476492A1C9D741D27DBAF73D5DB7008DD1F6513CF
spain_remote_probe_sha256=5485260DF91713B742E45793C079F6A18BC1B83D54AF72556EB8E6A3CC0AB345
amn2_tests=scoped_210_passed|full_1003_passed_1_skipped_1_preexisting_warning
amn3_tests=spain_scoped_21_passed|full_184_passed
amn2_security=final_scan_20260719T_final_8b28903_51fdba2|coverage_20_of_20|findings_0|snapshot_6728b518df4b1596417791e1846b81a0c5117e93d45d9ca3be18241dac30d7c9
amn3_security=final_scan_20260719T_final_a3c63a4_20ee9a6|coverage_2_of_2|findings_0|snapshot_a3d734713e4ba006977a49afd36053f5d556fa3591438519435ab8592dd100c4
spain_network_contact=false
spain_install_restart_stop_config=false
spain_private_credentials_in_git=false
spain_unrelated_service=preserve_and_fingerprint_before_after|identity_private
usa_source_server=retained_untouched
production_bot_web_database=unchanged
production_awg=untouched
protected_monitor_baseline=untouched
next=PREPARE_DEDICATED_SPAIN_TRUST_STATE_THEN_REQUIRE_EXACT_READ_ONLY_PREFLIGHT_APPROVAL
```

Следующий операционный шаг не является установкой AMN2. Сначала локально
создаётся отдельный Spain SSH key, оператор через provider console добавляет
только его public key, а host key сверяется по независимому каналу. Лишь после
этого может быть отдельно разрешён checksum-bound read-only preflight.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Текущий override 2026-07-19: POST-RELEASE-API-001 live acceptance passed

Phase 11 остаётся закрытой как `completed-controlled-private-release`.
Отдельно авторизованный single-use `POST-RELEASE-API-001` gate прошёл на
production source `0b858c5`; все smoke-записи были только в disposable clone.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
post_release_api_001=live_acceptance_pass
post_release_api_001_remote_sha256=6D4F801D7A0235C62E8F558B9D9F82DF676F672C0F7972A30F4362BCA12C9526
post_release_api_001_source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
post_release_api_001_authority=exact_literal_match|single_use_consumed
post_release_api_001_preflight=pass|write_gates_false_false|production_3040_absent
post_release_api_001_auth=missing_401|invalid_401|cross_scope_403_403
post_release_api_001_smoke=six_routes|api_read_6|api_write_0|ttl_used|revoked
post_release_api_001_cleanup=listener_0|process_0|clone_0|state_0
post_release_api_001_independent_postflight=pass|production_3040_absent
post_release_api_001_live_origin_sync=amn3_218a6a82c53a04ad5a394bdf048d3b43bbac32b9|verified
production_database=unchanged
production_bot_web=unchanged
production_awg=untouched|observed_unchanged
public_write_config_peer_self_service=closed
post_release_api_001_evidence=research/amn2/post-release-api-001-live-gate-2026-07-19.md
post_release_next=REVIEW_NEXT_POST_RELEASE_GATE_BY_CRITICALITY
```

Persistent API service и public listener не создавались. Повторный `run`
запрещён single-use receipt. Не выполнялись blind remediation, DB restore,
service restart, Telegram action, AWG mutation или повтор Phase 10/11 rollout.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-18: POST-RELEASE-API-001 local gate ready

Phase 11 остаётся закрытой как `completed-controlled-private-release`.
`POST-RELEASE-API-001` реализован и полностью проверен локально; SSH и live
gate не запускались, production не контактировался.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
post_release_api_001=local_executor_ready|live_not_run
post_release_api_001_source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
post_release_api_001_written_spec=3a3af86b70c21c0e5c4883839bb95d523cc242fb|approval_8b28903
post_release_api_001_plan=78bfd9881a4c6201449aee11be61c0e52730fb01
post_release_api_001_remote_sha256=6D4F801D7A0235C62E8F558B9D9F82DF676F672C0F7972A30F4362BCA12C9526
post_release_api_001_contract=clone_db|loopback_3040|scoped_token|ttl_revoke|six_route_audit|mandatory_cleanup
post_release_api_001_tdd=red_observed|focused_15_passed|root_full_163_passed
post_release_api_001_security=scan_efb532b_20260718T140745Z|coverage_4_of_4_complete|deferred_0|findings_0
post_release_api_001_origin_sync=amn2_8b28903f72510f21181eacfe9689fa6a405a6516|amn3_cfb589bb9404383cd4fb646fc19a002866fd644f|verified
post_release_api_001_live=false
production_api_3040_listener=unchanged_absent
production_database=not_contacted|unchanged
production_bot_web=not_contacted|unchanged
production_awg=untouched
public_write_config_peer_self_service=closed
post_release_api_001_evidence=research/amn2/post-release-api-001-local-gate-2026-07-18.md
post_release_next=REQUIRE_SEPARATE_EXACT_LIVE_APPROVAL_BEFORE_ANY_PREFLIGHT_OR_RUN
```

Runner связан с точными Bash-байтами, trusted absolute OpenSSH, единственным
known-host target, ordinal approval и single-use receipt. Remote executor
работает с read-only source и private clone, слушает только
`127.0.0.1:3040`, проверяет scoped access/audit/revoke и обязан удалить весь
transient state до независимого postflight. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`
остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-18: TELEGRAM-GROUP-ICON-001 local gate ready

Phase 11 остаётся закрытой как `completed-controlled-private-release`.
Post-release `TELEGRAM-GROUP-ICON-001` реализован и статически проверен только
локально. Живая фотография production Telegram-группы не менялась.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
post_release_device_001=local_implementation_and_verification_pass|production_not_deployed
telegram_group_icon_001=local_fail_closed_executor_ready|live_unchanged
telegram_group_icon_001_source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
telegram_group_icon_001_remote_sha256=F533CF7EFCB49EE494CE1E75B80F4CCC6EA6C06D2DB46D72669AC6FC23BA623F
telegram_group_icon_001_asset_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
telegram_group_icon_001_modes=fingerprint_read_only|preflight_exact_approval|apply_single_use_exact_approval
telegram_group_icon_001_tdd=red_13_failed|focused_20_passed|root_full_148_passed
telegram_group_icon_001_security=scan_d6236ce_20260718T102337Z|coverage_3_of_3_complete|deferred_0|findings_0
telegram_group_icon_001_live=false
telegram_api_called=false
messages_sent=0
production_bot_web_database=not_contacted|unchanged
production_awg=untouched
public_write_config_peer_self_service=closed
telegram_group_icon_001_evidence=research/amn2/post-release-telegram-group-icon-001-local-gate-2026-07-18.md
telegram_group_icon_001_origin_sync=amn3_450795b2b2b5fdf14763f7e310eac9a0eeaa0e73|amn2_227cbdcf85e2c84998282f7ceaa769aad71ba94a|verified
telegram_group_icon_001_fingerprint=failed_closed|gate_rejected|telegram_api_false|mutation_false
telegram_group_icon_001_target_input=missing_or_invalid|blind_remediation_forbidden
post_release_next=PREPARE_PRIVATE_TARGET_JSON_OUTSIDE_GIT_THEN_AUTHORIZE_ROOT_ONLY_PROVISIONING_AND_REPEAT_READ_ONLY_FINGERPRINT
```

Исполнитель связан с exact source SHA, private target fingerprint и будущим
отдельным literal live approval. Он сохраняет прежнюю фотографию, вооружает
rollback240 до единственного `setChatPhoto`, повторно проверяет bot/DB/web/AWG
invariants и удаляет private state только после успешного postflight. Raw
target и token не входят в Git или evidence. `preflight` и `apply` ещё не
запускались. После origin sync единственный read-only `fingerprint` остановился
fail-closed на private target contract до Telegram action path. Живых API
вызовов и mutations не было. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`
остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-18: post-release DEVICE-001 local readiness

Phase 11 остаётся закрытой как `completed-controlled-private-release`.
Post-release slice `DEVICE-001` локально реализован и проверен в AMN2 на
`e564b95e799fefa71599438a731e3f172a50c224`; в production он не развёрнут.

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
post_release_device_001=local_implementation_and_verification_pass
post_release_device_001_source=codex-vps-test-prep|e564b95e799fefa71599438a731e3f172a50c224
post_release_device_001_routes=/device-passports|/device-passports/{device_id}
post_release_device_001_access=session_authenticated|read_only|bounded_100
post_release_device_001_policy=web.device_passports.index|web.device_passports.detail
post_release_device_001_focused_tests=74_passed|1_warning
post_release_device_001_full_tests=928_passed|1_skipped|1_warning
post_release_device_001_security=complete_9_of_9|findings_0|deferred_0
post_release_device_001_deployment=false
public_write_config_peer_self_service=closed
production_bot_web_database=not_contacted|unchanged
production_awg=untouched
telegram_group_icon_001=live_unchanged|separate_local_executor_and_exact_approval_required
post_release_evidence=research/amn2/phase-12-device-001-read-only-operator-ux-2026-07-18.md
post_release_next=WRITE_TELEGRAM_GROUP_ICON_001_TDD_PLAN_THEN_IMPLEMENT_LOCAL_FAIL_CLOSED_EXECUTOR
```

Новые страницы показывают только безопасную проекцию существующих Device
Passports. Они не открывают POST/write, enrollment, raw config, private key,
PSK, enrollment token или config/peer delivery. Живая иконка Telegram-группы
ещё не менялась. Для неё нельзя переиспользовать Phase 11 approvals.
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope и нетронутым.

# Предыдущий override 2026-07-18: Phase 11 controlled private release closeout

`PHASE11-RELEASE-001` завершает Phase 11 как
`completed-controlled-private-release`. Declaration вступает в силу только
после fresh tests, complete security-diff review с findings `0`, equality
sealed scan snapshot с index и commit tree, commit, push и exact trusted-origin
readback commit, содержащего canonical closeout packet.

```text
active_phase=Phase 11 Controlled Launch and Operations
phase_status=completed-controlled-private-release
phase11_release_001=pass_after_this_commit_origin_readback
phase11_closeout_packet=docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md
phase11_closeout_evidence=research/amn2/phase-11-final-closeout-controlled-private-release-2026-07-18.md
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|clean|origin_sync
production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0|verified
phase11_telegram_002b=activation_and_stability_pass|run_20260717T192602Z|elapsed_66m13s
production_bot=active_enabled_single_instance_restart_0_watchdog_healthy
production_telegram=identity_match_webhook_empty_backlog_0
production_web=active_enabled_http_ok_loopback_only
production_database=integrity_ok|fk_0|only_expected_first_admin_row_delta
production_awg=unchanged|running|restart_0|peer_set_unchanged
release_boundary=private_operator_only|public_write_config_peer_self_service_closed
repeat_start_cleanup_stage_accept_rollout_restore=false
phase11_recovery_001=retain_sealed|review_by_2026_08_01|not_release_blocker_while_sealed
phase11_second_vps=read_only_handover_audit_only_before_user_repurpose|not_release_blocker_now
phase11_automation=amn2_upstream_orchestrator_active_current_task_original_weekly_contract
legacy_upstream_chain=paused_paused_paused
phase11_next=REVIEW_POST_RELEASE_DEVICE_001_READ_ONLY_OPERATOR_UX_SCOPE
```

Canonical packet сохраняет post-release P1–P3 roadmap, но не повышает его до
launch blocker. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне
scope и нетронутым. No Phase 11 live approval is reusable.

# Предыдущий override 2026-07-17: TELEGRAM-002B 66-minute stability прошла

После exact-one cleanup Telegram backlog стал `0`, при этом response/workflow и
production DB/web/AWG mutations отсутствовали. Fresh `2FDB...` preflight и
disabled-first stage открыли run `20260717T192602Z`. Первый configured admin
отправил один новый `/start` и подтвердил exact wide language header. Accept
включил persistent bot, отменил rollback timer и прошёл независимый postflight.

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|production_unchanged
production_overlay=0b858c5|verified
phase11_telegram_002b_cleanup_preflight=pass
phase11_telegram_002b_cleanup=pass|ack_exact_one_stale_private_first_admin_start_only|no_response
phase11_telegram_002b_cleanup_post=backlog_0|database_unchanged|web_healthy|bot_inactive_disabled|awg_unchanged
phase11_telegram_002b_fresh_preflight=pass|identity_match|webhook_empty|backlog_0|ownership_probe_empty
phase11_telegram_002b_stage=pass|run_id_20260717T192602Z|active_disabled|autorollback_240
phase11_telegram_002b_accept=pass|first_admin_start_accepted|wide_header_confirmation_exact
phase11_telegram_002b_service=active_enabled_single_instance|restart_0|watchdog_healthy
phase11_telegram_002b_database=first_admin_user_row_only|integrity_ok|fk_0
phase11_telegram_002b_web=active_enabled_http_ok_loopback_only
phase11_telegram_002b_awg=unchanged
phase11_telegram_002b_postflight=pass|identity_match|webhook_empty|backlog_0
phase11_telegram_002b_stability=pass|elapsed_66m13s|final_postflight_20260717T203215Z
phase11_telegram_002b_operator_action=none|do_not_repeat_start
phase11_release_blocker=PHASE11_RELEASE_001_FINAL_CLOSEOUT_AND_PRIVATE_RELEASE_READINESS_DECISION_ONLY
phase11_second_vps=handover_audit_only_at_user_repurpose|not_current_release_blocker
phase11_recovery_001=retain_sealed|review_by_2026_08_01|not_release_blocker_while_sealed
phase11_automation=temporary_stability_prompt|restore_after_final_origin_verification|backup_sha256_BD8BB6253C31D6CF26E1FFA6F5B89B640FD48DF706DFEC26BB167180BA510EA6
phase11_next=SYNC_TEST_SECURITY_COMMIT_PUSH_VERIFY_ORIGIN_RESTORE_AUTOMATION_THEN_REVIEW_RELEASE_001
```

`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` остаётся вне scope. Legacy
three-step upstream chain остаётся PAUSED. Повторный `/start` не требуется.

# Предыдущий override 2026-07-17: TELEGRAM-002B exact-one stale-start cleanup готов локально

User-issued `2FDB...` approval был использован только для fresh classified
preflight. Production checks прошли до Telegram admission, затем gate
остановился fail-closed с `pending_updates_nonzero`. `stage` не вызывался и
single-use stage receipt отсутствует. Bot остался inactive/disabled; DB/web/AWG
baseline не изменён.

Design и written spec отдельно одобрены. TDD добавил самостоятельный remote
cleanup executor и checksum-bound runner, не изменяя байты существующего
activation executor. В ходе runtime-compatibility review обнаружено и по TDD
исправлено сравнение aiogram `ContentType.TEXT`: enum напрямую равен `"text"`,
но `str(enum)` не равен. После fix runner пересвязан к финальному SHA.

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|production_unchanged
production_overlay=0b858c5|verified
phase11_telegram_002b_blocker=pending_updates_nonzero|preflight_fail_closed
phase11_telegram_002b_stage=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_regular_bot=inactive_disabled_process_0
phase11_telegram_002b_database=integrity_ok|fk_0|tables_15|rows_88
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
phase11_telegram_002b_existing_remote_sha256=2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2
phase11_telegram_002b_existing_runner_sha256=75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53
phase11_telegram_002b_existing_stage_authority=unconsumed
phase11_telegram_002b_cleanup_design=docs/superpowers/specs/2026-07-17-phase11-telegram-002b-stale-start-single-update-cleanup-design.ru.md|commit_d474ff6|approved
phase11_telegram_002b_cleanup_plan=docs/superpowers/plans/2026-07-17-phase11-telegram-002b-stale-start-single-update-cleanup.ru.md|commit_940d07c
phase11_telegram_002b_cleanup_remote_sha256=41F69F945F74647B441173B682277E0568DA81CC7F0B12EADD9BD534DB225242
phase11_telegram_002b_cleanup_runner_sha256=D3BD76119B35155AAB922E54C2E59F50B7D9D0B23C9B5AC2268887D8ADB70A1F
phase11_telegram_002b_cleanup_contract=exact_one_private_first_admin_start|double_nonadvancing_inspection|single_advancing_offset|concurrent_update_preserved|no_response
phase11_telegram_002b_cleanup_tdd=red_9_failed_1_passed|remote_green_8_passed_2_deselected|aiogram_red_1_failed_9_passed|final_green_10_passed
phase11_telegram_002b_cleanup_tests=focused_10_passed|canonical_128_passed|bash_n_pass|powershell_parse_pass|diff_check_pass
phase11_telegram_002b_cleanup_static_scans=forbidden_operations_0|high_confidence_secret_matches_0
phase11_telegram_002b_cleanup_security=scan_59e7862ce73ab46179a01591f4533c8496f3b38d_20260717T183406Z|snapshot_48bc1e5a1e775a2b97c75c30c83938d4fc79f07da281b328df0640c532db7564|worklist_5_of_5|coverage_complete|findings_0
phase11_telegram_002b_cleanup_live=not_run|telegram_ack_false|vps_mutation_false
phase11_telegram_002b_cleanup_approval=prepared_in_runner|must_not_issue_or_use_before_origin_sync
phase11_next=COMMIT_PUSH_ORIGIN_READBACK_THEN_ISSUE_EXACT_CLEANUP_LIVE_APPROVAL
```

До отдельного exact live cleanup approval Telegram queue не подтверждается и
не очищается. Новый `/start` отправлять только после будущего successful
`2FDB...` stage с `awaiting_admin_start=true`.

# Предыдущий override 2026-07-16: combined overlay `0b858c5` prepared, verified and pushed

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
production_overlay=801f8c3|unchanged
phase11_package_0b858c5=prepared_verified_pushed|not_uploaded_not_applied
phase11_package_0b858c5_outer=dist/amn2-combined-overlay-0b858c5.zip|bytes_9220155|sha256_7866bdd9febe1d6eea701b37a6e4206a8267766a56993f3c02a0c7b30c394b54|entries_4
phase11_package_0b858c5_source=amn2-codex-vps-test-prep-0b858c5-source.zip|bytes_9277869|sha256_e03f13fd6a7bb5cbc5fcee7179f395ea8c2864ebceab01bc351c5904f3cff975|entries_383|comment_full_commit
phase11_package_0b858c5_delta=801f8c3_to_0b858c5|paths_31|deleted_app_web_static_brand_full_jpg_only|schema_delta_none
phase11_package_0b858c5_contents=canonical_square_logo|wide_language_header|telegram_002a_hardening|forbidden_0|unsafe_names_0|symlinks_0
phase11_package_0b858c5_tests=helper_markdown_5_passed|bash_syntax_passed|archive_and_binding_passed|full_source_918_passed_1_skipped_1_known_warning
phase11_package_0b858c5_security=scan_32d68a4_20260716T123509Z|snapshot_1b94685eea2da582efd72341869fccae1738d1a6ace588c612803f39fbafcc4e|receipts_7_of_7|surfaces_5|coverage_complete|findings_0
phase11_package_0b858c5_live=upload_false|extract_false|apply_false|vps_false|telegram_api_false|regular_bot_inactive_disabled|profile_unchanged|web_db_unchanged|provider_false|awg_untouched
phase11_package_0b858c5_gate=docs/AMN2_PHASE_11_0B858C5_COMBINED_OVERLAY_GATE.ru.md
phase11_package_0b858c5_evidence=research/amn2/phase-11-0b858c5-combined-overlay-package-prep-2026-07-16.md
phase11_recovery_001=retain_sealed_without_deletion|do_not_open_copy_move_or_delete|review_no_later_than_2026-08-01
phase11_second_vps=amn2_no_longer_needed|clean_ssh_only|user_hold_through_weekend_then_repurpose|final_read_only_handover_audit_pending
phase11_next=REVIEW_0B858C5_COMBINED_PRIVATE_OVERLAY_EXACT_LIVE_GATE
```

# Текущий override 2026-07-16: wide language-selection header completed and pushed

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
production_overlay=801f8c3|unchanged
phase11_brand_001=square_canonical_logo_preserved|bot_and_web_sha256_40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791|production_not_deployed
phase11_brand_002=language_selection_wide_header_complete_local|commit_0b858c5|origin_sync|production_not_deployed
phase11_brand_002_asset=app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png|png_1672x941|bytes_2647131|sha256_bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f
phase11_brand_002_scope=telegram_start_language_selector_only|square_web_and_canonical_assets_preserved|text_only_missing_asset_fallback
phase11_brand_002_tdd=asset_red_expected|handler_red_expected|asset_green_3|handler_asset_green_47|scoped_61_passed|full_918_passed_1_skipped_1_known_warning|compile_passed|wheel_exact_asset_passed
phase11_brand_002_security=clean_diff_scan_complete|full_file_receipts_3_of_3|surfaces_4|findings_0|coverage_complete
phase11_brand_002_live=telegram_api_false|regular_bot_inactive_disabled|profile_unchanged|vps_false|provider_false|web_db_false|awg_untouched
phase11_telegram_002a=local_implementation_complete|contained_in_source_0b858c5|production_not_activated
phase11_next_package=prepare_exact_0b858c5_combined_square_logo_wide_language_header_and_telegram_hardening_private_overlay|verify_checksum_contents_rollback|no_upload_without_exact_gate
phase11_recovery_001=retain_sealed_without_deletion|do_not_open_copy_move_or_delete|review_no_later_than_2026-08-01
phase11_second_vps=amn2_no_longer_needed|clean_ssh_only|user_hold_through_weekend_then_repurpose|final_read_only_handover_audit_pending
phase11_design=docs/superpowers/specs/2026-07-16-phase11-language-selection-wide-header-design.ru.md|english_peer_present
phase11_plan=docs/superpowers/plans/2026-07-16-phase11-language-selection-wide-header.ru.md|english_peer_present
phase11_next=PREPARE_0B858C5_COMBINED_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

# Текущий override 2026-07-16: TELEGRAM-002A local hardening completed and pushed

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|08c56f2beff65145380fdb3736d94c0709a2b33a|origin_sync|clean
production_overlay=801f8c3|unchanged
phase11_telegram_002a=local_implementation_complete|commit_08c56f2|production_not_activated
phase11_telegram_002a_controls=identity_webhook_backlog_ownership_recheck|single_instance_lock|allowed_message_callback|tasks_concurrency_8|overall_startup_timeout_max_120|systemd_start_135_watchdog_60
phase11_telegram_002a_tdd=red_3_failed_expected|green_14_passed|scoped_113_passed|full_915_passed_1_skipped_1_known_warning|toolchain_compile_diff_passed
phase11_telegram_002a_security=clean_scan_complete|full_file_receipts_15_of_15|findings_0|snapshot_da0f5ec50e574c749029210fe783b5dbc3a0ee97749b13ad44a8a83ddcc15105
phase11_telegram_002a_live=regular_bot_inactive_disabled|telegram_api_false|profile_unchanged|vps_false|provider_false|web_db_false|awg_untouched
phase11_telegram_002a_ssh_prerequisite=before_future_vps_write_activation_use_tested_service_readable_non_home_key_and_known_hosts_path|retain_ProtectHome_true
phase11_brand_001=integrated_in_descendant_08c56f2|old_logo_only_package_not_current_combined_candidate|production_not_deployed
phase11_next_package=prepare_exact_08c56f2_combined_logo_and_telegram_hardening_private_overlay|verify_checksum_contents_rollback|no_upload_without_exact_gate
phase11_recovery_001=retain_sealed_without_deletion|do_not_open_copy_move_or_delete|review_no_later_than_2026-08-01
phase11_second_vps=amn2_no_longer_needed|clean_ssh_only|user_hold_through_weekend_then_repurpose|final_read_only_handover_audit_pending
phase11_evidence=research/amn2/phase-11-telegram-002a-local-persistent-admission-unit-hardening-2026-07-16.md
phase11_next=PREPARE_08C56F2_COMBINED_PRIVATE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
```

# Предыдущий override 2026-07-15: fallback retained, second VPS handover and logo package ready

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3|unchanged
phase11_recovery_001=retain_sealed_without_deletion|do_not_open_copy_move_or_delete|review_no_later_than_2026-08-01
phase11_second_vps=amn2_no_longer_needed|clean_ssh_only|user_hold_through_weekend|then_repurpose_for_other_functionality
phase11_second_vps_billing=provider_display_paid_until_2026-08-12_23_18_25|590_rub_current_monthly_period|auto_renew_enabled_observed
phase11_second_vps_mutation=provider_false|billing_false|remote_false|production_false|awg_false
phase11_second_vps_handover=final_read_only_audit_then_remove_only_dedicated_staging_ssh_key_and_known_host_after_separate_exact_approval
phase11_second_vps_gate=docs/AMN2_PHASE_11_SECOND_VPS_AMN2_HANDOVER_GATE.ru.md
phase11_brand_001=source_6abc620|private_overlay_package_ready|not_uploaded|not_applied
phase11_brand_001_package=dist/amn2-canonical-logo-overlay-6abc620.zip|sha256_2683420dd7a705c96490dc1878d14d208986209bf8eb1b6e1b066d31b17932f5
phase11_brand_001_tests=focused_26_passed|source_delta_14_passed|bash_zip_diff_toolchain_passed
phase11_brand_001_security=complete_coverage_7_of_7|findings_0|snapshot_36d08ba1945558ee590e3c8d1057eeb37ad634141ae432cb070355ab242f38fb
phase11_brand_001_live=production_801f8c3|regular_bot_inactive_disabled|telegram_profile_unchanged|awg_untouched
phase11_brand_001_gate=docs/AMN2_PHASE_11_6ABC620_CANONICAL_LOGO_OVERLAY_GATE.ru.md
phase11_telegram_002a=local_design_gate_next|implementation_not_started|production_bot_inactive_disabled
phase11_next=REVIEW_AND_APPROVE_TELEGRAM_002A_FAIL_CLOSED_DESIGN_THEN_TDD_IMPLEMENTATION
```

# Предыдущий override 2026-07-15: RESTORE-001A full-secret disposable rehearsal passed

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3|unchanged
phase11_restore_001a=completed_pass
phase11_restore_001a_approval=received|consumed
phase11_restore_001a_bundle=amn2_full_recovery_v2|encrypted_sha256_22fc6fcdf94405187db448d3ffd97a170829aaf3a64794cae416e05a8ac490ff
phase11_restore_001a_static=critical_contracts_passed|source_801f8c3|image_layers_6|compressed_6
phase11_restore_001a_stream=passed|bytes_20118420|local_plaintext_false|private_key_transferred_false
phase11_restore_001a_awg=passed|internal_network|default_route_false|host_ports_false|running_restart_0_peers_12|keys_psk_allowedips_interface_config_match
phase11_restore_001a_web=passed|loopback_only|login_200|outbound_denied
phase11_restore_001a_database=integrity_ok|counts_schema_values_file_hash_unchanged
phase11_restore_001a_bot=not_started|telegram_api_false
phase11_restore_001a_cleanup=passed|plaintext_source_database_awg_runtime_removed|packages_versions_marks_listeners_docker_restored
phase11_restore_001a_second_vps=post_audit_pass|ssh_only|docker_absent|amn2_absent|artifacts_0|failed_units_0
phase11_restore_001a_production_reaudit=runtime_contract_passed|ops_health_passed|web_healthy|bot_inactive_disabled|database_ok|awg_running_restart_0_peers_12_same_set
phase11_restore_001a_security=scoped_tests_and_allowlisted_diagnostics_passed|new_reportable_findings_0
phase11_restore_001a_evidence=research/amn2/phase-11-restore-001a-trusted-disposable-full-secret-rehearsal-2026-07-15.md
phase11_recovery_001=retirement_decision_unblocked|destructive_delete_not_executed
phase11_second_vps=restore_role_complete|safe_retirement_gate_recommended|provider_delete_not_executed
phase11_brand_001=local_source_complete_6abc620|production_not_deployed|telegram_profile_photo_unchanged
phase11_telegram_002a=next_local_engineering_hardening|production_bot_inactive_disabled
phase11_next=DECIDE_OLD_FALLBACK_AND_SECOND_VPS_SAFE_RETIREMENT_GATES_THEN_PREPARE_LOGO_ROLLOUT_AND_IMPLEMENT_TELEGRAM_002A
```

# Предыдущий override 2026-07-15: RESTORE-001A attempt 4 OCI gzip layer double-binding fix verified

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_restore_001a_source_pin=801f8c3|approval_scope_unchanged
phase11_restore_001a_attempt_4=fail_closed_before_ciphertext|image_archive_layer_digest_mismatch
phase11_restore_001a_attempt_4_diagnosis=oci_layers_6|raw_blob_path_digest_match_6|gzip_6|decompressed_diffid_match_6|raw_diffid_match_0
phase11_restore_001a_attempt_4_sizes=decompressed_total_26048512|max_layer_7688192|per_layer_limit_67108864|total_limit_134217728
phase11_restore_001a_attempt_4_cleanup=production_private_run_cleanup_passed|diagnostic_cleanup_passed|ciphertext_created_false|secret_transfer_false|staging_mutation_false
phase11_restore_001a_attempt_4_reaudit=runtime_contract_passed|ops_health_passed|overlay_801f8c3|web_healthy|bot_inactive_disabled|database_ok|awg_running_restart_0_peers_12_same_set|telegram_api_false
phase11_restore_001a_gzip_fix=oci_raw_blob_sha_to_path_digest|stream_gzip_uncompressed_sha_to_rootfs_diffid|legacy_raw_diffid_preserved
phase11_restore_001a_gzip_limits=per_layer_64m|cumulative_128m|invalid_unsupported_or_oversize_fail_closed
phase11_restore_001a_gzip_tdd=red_3_failed_expected|corrupt_deflate_red_1_failed_expected|focused_9_passed|recovery_57_passed|root_86_passed|compile_passed|diff_check_passed
phase11_restore_001a_binding_preserved=config_path_self_hash|canonical_executable_config|amd64_linux|ordered_rootfs_diffids|compressed_blob_and_uncompressed_layer_bytes
phase11_restore_001a_gzip_security=initial_important_zlib_normalization_and_minor_cumulative_test_fixed|rereview_critical_0_important_0_minor_0|ready_yes
phase11_restore_001a_approval=received|not_consumed
phase11_restore_001a_live_effect=bundle_false|secret_transfer_false|staging_mutation_false|services_unchanged|awg_untouched
phase11_restore_001a_next=DOCS_STATUS_COMMIT_PUSH_THEN_RETRY_ALREADY_APPROVED_801F8C3_GATE
phase11_restore_001a_gzip_evidence=research/amn2/phase-11-restore-001a-oci-gzip-layer-double-binding-fix-2026-07-15.md
```

# Предыдущий override 2026-07-15: RESTORE-001A attempt 3 JSON-null RepoTags fix verified

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_restore_001a_source_pin=801f8c3|approval_scope_unchanged
phase11_restore_001a_attempt_3=fail_closed_before_ciphertext|image_archive_repo_tag_contract_invalid
phase11_restore_001a_attempt_3_diagnosis=manifest_repotags_key_present|json_null|tag_count_0|config_and_6_layers_canonical_self_bound
phase11_restore_001a_attempt_3_cleanup=production_private_run_cleanup_passed|diagnostic_cleanup_passed|ciphertext_created_false|secret_transfer_false|staging_mutation_false
phase11_restore_001a_attempt_3_reaudit=runtime_contract_passed|ops_health_passed|overlay_801f8c3|web_healthy|bot_inactive_disabled|database_ok|awg_running_restart_0_peers_12_same_set|telegram_api_false
phase11_restore_001a_null_tag_fix=require_repotags_key|allow_json_null_or_empty_or_exact_singleton_canonical|missing_malformed_foreign_additional_duplicate_rejected
phase11_restore_001a_null_tag_tdd=red_3_failed_expected|green_8_passed|recovery_50_passed|root_79_passed|compile_passed|diff_check_passed
phase11_restore_001a_binding_preserved=config_path_self_hash|canonical_executable_config|amd64_linux|ordered_rootfs_diffids|every_layer_byte
phase11_restore_001a_null_tag_security=independent_security_focused_review|critical_0|important_0|minor_0|ready_yes
phase11_restore_001a_approval=received|not_consumed
phase11_restore_001a_live_effect=bundle_false|secret_transfer_false|staging_mutation_false|services_unchanged|awg_untouched
phase11_restore_001a_next=DOCS_STATUS_COMMIT_PUSH_THEN_RETRY_ALREADY_APPROVED_801F8C3_GATE
phase11_restore_001a_null_tag_evidence=research/amn2/phase-11-restore-001a-json-null-repotags-compatibility-fix-2026-07-15.md
```

# Предыдущий override 2026-07-15: RESTORE-001A attempt 2 canonical RepoTags compatibility fix verified

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_restore_001a_source_pin=801f8c3|approval_scope_unchanged
phase11_restore_001a_attempt_2=fail_closed_before_ciphertext|immutable_image_archive_unexpectedly_contains_repo_tags
phase11_restore_001a_attempt_2_root_cause=docker_save_by_image_id_preserves_single_canonical_local_repo_tag
phase11_restore_001a_attempt_2_cleanup=production_private_run_cleanup_passed|ciphertext_created_false|secret_transfer_false|staging_mutation_false
phase11_restore_001a_attempt_2_reaudit=runtime_contract_passed|ops_health_passed|overlay_801f8c3|web_healthy|bot_inactive_disabled|database_ok|awg_running_restart_0_peers_12_same_set|telegram_api_false
phase11_restore_001a_repo_tag_fix=allow_only_empty_or_exact_singleton_expected_reference|foreign_additional_duplicate_tags_rejected
phase11_restore_001a_repo_tag_tdd=red_3_failed_expected|green_6_passed|recovery_48_passed|root_77_passed|compile_passed|diff_check_passed
phase11_restore_001a_binding_preserved=config_path_self_hash|canonical_executable_config|amd64_linux|ordered_rootfs_diffids|every_layer_byte
phase11_restore_001a_repo_tag_security=independent_security_focused_review|critical_0|important_0|minor_0|ready_yes
phase11_restore_001a_approval=received|not_consumed
phase11_restore_001a_live_effect=bundle_false|secret_transfer_false|staging_mutation_false|services_unchanged|awg_untouched
phase11_restore_001a_next=DOCS_STATUS_COMMIT_PUSH_THEN_RETRY_ALREADY_APPROVED_801F8C3_GATE
phase11_restore_001a_repo_tag_evidence=research/amn2/phase-11-restore-001a-canonical-repotag-compatibility-fix-2026-07-15.md
```

# Предыдущий override 2026-07-15: RESTORE-001A OCI Config-path fix verified and clean-scanned

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_restore_001a_source_pin=801f8c3|approval_scope_unchanged
phase11_restore_001a_diagnosis=production_docker_save_oci_blob_layout|config_and_6_layers|safe_self_bound|cleanup_passed
phase11_restore_001a_root_cause=validator_legacy_config_filename_only|correct_oci_blob_rejected_before_identity_checks
phase11_restore_001a_fix=exact_legacy_or_oci_config_path_allowlist|no_fallback|all_existing_hash_platform_rootfs_layer_checks_preserved
phase11_restore_001a_tdd=red_3_failed_expected|green_3_passed|recovery_44_passed|root_73_passed|compile_passed
phase11_restore_001a_security=complete_coverage|full_file_receipts_1_of_1|surfaces_4|sealed_artifacts_9|findings_0|deferred_0
phase11_restore_001a_security_snapshot=b051261c4bf7061c72ffcd31b1f04d9da3b77bc3de4e54dfbbd325055dc69cc2
phase11_restore_001a_approval=received|not_consumed
phase11_restore_001a_live_effect=diagnostic_read_only|bundle_false|secret_transfer_false|staging_mutation_false|services_unchanged|awg_untouched
phase11_restore_001a_next=COMMIT_PUSH_THEN_RETRY_ALREADY_APPROVED_801F8C3_GATE
phase11_restore_001a_oci_fix_evidence=research/amn2/phase-11-restore-001a-oci-config-path-compatibility-fix-2026-07-15.md
```

# Предыдущий override 2026-07-15: canonical logo source integrated; RESTORE-001A attempt 1 failed closed

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3|unchanged
phase11_brand_001=completed_local_source|commit_6abc620|pushed|not_deployed
phase11_brand_001_assets=bot_start_header_and_web_login_dashboard|png_1254x1254|canonical_sha256_40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791
phase11_brand_001_tests=tdd_red_3_failed_expected|focused_58_passed|full_872_passed_1_skipped
phase11_brand_001_security=complete_coverage|surfaces_3|sealed_artifacts_9|findings_0|deferred_0
phase11_brand_001_live=telegram_api_false|profile_icon_not_applied|bot_not_started_enabled|vps_not_contacted|awg_untouched
phase11_brand_001_production=requires_separate_package_rollout_gate_after_restore_pin_is_released
phase11_restore_001a_source_pin=801f8c3|approval_scope_unchanged_by_source_head_6abc620
phase11_restore_001a_attempt_1=fail_closed_before_ciphertext|image_archive_config_digest_invalid
phase11_restore_001a_cleanup=production_private_run_cleanup_passed|ciphertext_created_false|secret_transfer_false|staging_mutation_false
phase11_restore_001a_reaudit=runtime_contract_passed|ops_health_passed|production_services_and_awg_invariants_passed
phase11_restore_001a_approval=received|not_consumed
phase11_restore_001a_next=SANITIZED_CONFIG_PATH_FORMAT_DIAGNOSIS_THEN_TDD_FIX_TEST_SECURITY_DOCS_COMMIT_PUSH_AND_RETRY
phase11_brand_001_evidence=research/amn2/phase-11-canonical-bot-logo-local-integration-2026-07-15.md
```

# Предыдущий override 2026-07-15: RESTORE-001A security blocker fixed and clean rescan passed

    active_phase=Phase 11 Controlled Launch and Operations
    phase11_restore_001a_gate=approved_pending_docs_commit_push_and_live_retry
    phase11_restore_001a_approval=received|not_consumed
    phase11_restore_001a_security_blocker=P11_LEGACY_IMAGE_CONFIG_UNBOUND_001|fixed
    phase11_restore_001a_binding=canonical_executable_config_sha256|amd64|linux|rootfs_diff_ids|layer_bytes
    phase11_restore_001a_tests=tdd_red_confirmed|runtime_15_passed|recovery_scoped_41_passed|root_70_passed|independent_verifier_35_passed
    phase11_restore_001a_clean_scan=complete_coverage|full_file_receipts_6_of_6|findings_0|sealed_artifacts_5
    phase11_restore_001a_clean_snapshot=d56c7864892bdf6f024b1e701b93577a286f1f7d467d50fde2882437757ae12c
    phase11_restore_001a_production_compat=canonical_config_arch_os_match|values_not_emitted|temp_cleanup_passed
    phase11_restore_001a_live_effect=none|production_and_staging_restore_not_run|awg_untouched|regular_bot_inactive_disabled
    phase11_restore_001a_next=DOCS_STATUS_SYNC_COMMIT_PUSH_THEN_RETRY_ALREADY_APPROVED_LIVE_GATE
    phase11_restore_001a_retirement=old_fallback_and_second_vps_delete_remain_separate_exact_gates
    phase11_restore_001a_evidence=research/amn2/phase-11-legacy-image-config-binding-security-fix-2026-07-15.md

# Предыдущий override 2026-07-14: RESTORE-001A runtime-complete v2 gate ready

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_restore_001a_gate=reviewed_ready_awaiting_exact_approval
phase11_restore_001a_required_format=amn2-full-recovery-v2|generic_v1_or_v2_report_not_gate_evidence
phase11_restore_001a_source=801f8c3|archive_files_328|expanded_bytes_11001389|sha256_6c58c33fc5b152114f651cece46cd99955758198e25e67e3c422ed5ca1f8166e
phase11_restore_001a_payload=canonical_v1_plus_source_archive_plus_offline_docker_image_plus_exact_runtime_json
phase11_restore_001a_verifier=required_v2_and_external_source_digest|explicit_gate_attestation
phase11_restore_001a_tests=focused_35_passed|root_64_passed|harness_20_passed|compile_passed|real_source_archive_passed
phase11_restore_001a_security=complete_coverage|findings_0|snapshot_db1b5700bd929212e25868dbf26a90c53f917dd3a0f39b23dcb02ddaa7e66702
phase11_restore_001a_live_effect=none|production_not_contacted|staging_not_contacted|secret_transfer_false
phase11_restore_001a_awg=untouched|live_gate_requires_identity_restart_peer_set_invariant
phase11_restore_001a_cleanup=mandatory_on_pass_or_fail|staging_returns_ssh_only_clean
phase11_restore_001a_retirement=old_fallback_and_provider_delete_remain_separate_exact_gates
phase11_restore_001a_approval=not_received|not_consumed
phase11_restore_001a_exact_phrase=APPROVE PHASE11_RESTORE_001A_801F8C3_RUNTIME_COMPLETE_V2_CANONICAL_BUNDLE_CREATE_VERIFY_COPY_AND_TRUSTED_DISPOSABLE_FULL_SECRET_RESTORE_WITH_STAGING_DOCKER_INSTALL_TRANSIENT_NETWORK_ISOLATED_AWG12_AND_LOOPBACK_WEB_VERIFY_MANDATORY_SECRET_RUNTIME_CLEANUP_REAUDIT_AND_PRODUCTION_AWG_UNTOUCHED
phase11_next=OPERATOR_EXACT_APPROVAL_FOR_PHASE11_RESTORE_001A
phase11_parallel_product_followup=TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING
phase11_restore_001a_evidence=research/amn2/phase-11-restore-001a-runtime-complete-v2-gate-review-2026-07-14.md
```

# Текущий override 2026-07-14: second VPS retained temporarily for RESTORE-001A

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_second_vps_audit=completed_pass|keep_temporarily_for_restore_001a
phase11_second_vps_current=ubuntu_24_04|ssh_key_only|ufw_deny_incoming|external_ssh_only|failed_units_0
phase11_second_vps_clean=amn2_tree_0|amn2_units_0|containers_0|recovery_or_amn2_artifacts_0
phase11_second_vps_role=trusted_disposable_functional_restore_only|production_dependency_false
phase11_second_vps_dr_independence=false|same_provider_as_production
phase11_second_vps_retention=until_restore_001a_and_cleanup_or_next_billing_cutoff_review
phase11_second_vps_long_term_fleet=false_until_ipam_and_fleet_decision
phase11_second_vps_provider_mutation=false|billing_mutation=false|secret_transfer=false
phase11_second_vps_retirement=after_restore_pass_or_decline|repeat_clean_audit|exact_provider_delete_gate|then_local_staging_key_cleanup
phase11_next=REVIEW_PHASE11_RESTORE_001A_CANONICAL_FULL_SECRET_DISPOSABLE_REHEARSAL_GATE
phase11_parallel_product_followup=TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING
phase11_current_priority_plan=docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md
phase11_second_vps_evidence=research/amn2/phase-11-second-vps-retention-audit-after-p0-2026-07-14.md
```

# Текущий override 2026-07-14: RECOVERY-001 old fallback retained conditionally

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_recovery_001=decision_complete|retain_sealed_conditionally|deletion_false
phase11_recovery_001_old=workspace_and_external_ciphertext_hash_match|key_present_separate_acl_private
phase11_recovery_001_canonical=external_ciphertext_hash_match|private_key_separate_acl_private|metadata_and_critical_contracts_passed
phase11_recovery_001_reason=canonical_full_secret_restore_apply_not_yet_rehearsed|old_legacy_fallback_still_useful
phase11_recovery_001_retirement_prerequisite=PHASE11_RESTORE_001A_CANONICAL_FULL_SECRET_TRUSTED_DISPOSABLE_REHEARSAL_PASS
phase11_recovery_001_future_delete=separate_exact_destructive_gate|old_workspace_ciphertext|old_external_ciphertext_receipts|old_symmetric_key
phase11_recovery_001_canonical_delete=false|move=false|rotate=false
phase11_recovery_001_production_effect=none|awg_untouched|services_unchanged|restore_not_run
phase11_recovery_001_next=AUDIT_SECOND_VPS_RETENTION_AFTER_P0
phase11_recovery_001_evidence=research/amn2/phase-11-recovery-001-old-bundle-key-retention-decision-2026-07-14.md
```

# Текущий override 2026-07-14: OPS-001 runtime/recovery health passed

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_ops_001=completed_healthy|observation_2026-07-14T18:02:04Z
phase11_ops_001_runtime=overlay_801f8c3|web_active_enabled_restart_0|bot_inactive_disabled|failed_units_0|ntp_yes
phase11_ops_001_network=3030_loopback_only|3040_80_443_absent
phase11_ops_001_capacity=disk_used_71_percent_available_2888376_kb|memory_available_505188_of_984560_kb|load1_0.07
phase11_ops_001_journal=32_err_alert_24h|amn2_0|docker_0|ssh_30|resource_exhaustion_0|raw_rows_not_emitted
phase11_ops_001_database=hashes_unchanged|integrity_ok|fk_0|tables_15|rows_88
phase11_ops_001_rollback=801f8c3_success_bundle_present_0700|required_7_present|snapshot_integrity_ok_fk_0
phase11_ops_001_canonical_recovery=external_copy_3_exact_files|ciphertext_hash_match|private_key_like_0
phase11_ops_001_awg=never_stopped_restarted_recreated|restart_0|peers_12|set_unchanged
phase11_ops_001_next=DECIDE_PHASE11_RECOVERY_001_OLD_BUNDLE_KEY_RETENTION
phase11_ops_001_evidence=research/amn2/phase-11-ops-001-compact-runtime-recovery-health-2026-07-14.md
```

# Текущий override 2026-07-14: persistent private Telegram bot stays disabled

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_telegram_002=decision_complete|hold_disabled|go_local_hardening
phase11_telegram_002_source_production=801f8c3|origin_sync|production_overlay_match
phase11_telegram_002_runtime=regular_bot_inactive_disabled_process_0|telegram_api_not_called
phase11_telegram_002_blockers=full_dispatcher_direct_polling|no_identity_webhook_backlog_admission|production_db_rw|watchdog_none|unit_sandbox_incomplete
phase11_telegram_002_write_boundary=write_gates_false_false_block_live_apply_but_not_local_sqlite_workflows
phase11_telegram_002_unit=restart_on_failure_5s|start_limit_5_per_10s|runtime_infinity|no_watchdog_notify
phase11_telegram_002_tests=bot_settings_systemd_186_passed|read_only_production_review_passed
phase11_telegram_002_awg=never_stopped_restarted_recreated|restart_0|peers_12|set_unchanged
phase11_telegram_002_activation=false|no_approval_phrase_prepared
phase11_telegram_002_followup=TELEGRAM_002A_LOCAL_PERSISTENT_ADMISSION_AND_UNIT_HARDENING
phase11_next=COLLECT_PHASE11_OPS_001_COMPACT_RUNTIME_RECOVERY_HEALTH_EVIDENCE
phase11_telegram_002_evidence=research/amn2/phase-11-801f8c3-persistent-private-telegram-bot-service-decision-2026-07-14.md
```

# Текущий override 2026-07-14: 801f8c3 transient Telegram smoke passed

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_telegram_001_smoke=completed-pass|run_20260714T174239Z
phase11_telegram_001_approval=received|consumed
phase11_telegram_001_actor=first_configured_admin_private|accepted_exact_start
phase11_telegram_001_identity=matched_prior_sanitized_getMe_binding
phase11_telegram_001_updates=message_only|one_response_sent|backlog_0_to_1_to_0|callbacks_false
phase11_telegram_001_data=production_db_unchanged_integrity_ok_fk_0|clone_only_changed_counts_unchanged
phase11_telegram_001_runtime=transient_unit_stopped_collected|private_clone_removed
phase11_telegram_001_regular_bot=inactive_disabled_process_0|persistent_activation_false
phase11_telegram_001_web=active_enabled_http_ok_loopback_only|api_3040_listener_0
phase11_telegram_001_awg=never_stopped_restarted_recreated|restart_0|running|peers_12|set_unchanged
phase11_telegram_001_prepare_retry=first_noexec_stop_before_telegram|cleanup_audit_pass|bash_retry_pass
phase11_telegram_001_security=no_token_admin_id_message_config_or_private_target_emitted
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|persistent_bot_public_false
phase11_next=REVIEW_PHASE11_TELEGRAM_002_PERSISTENT_PRIVATE_BOT_SERVICE_DECISION
phase11_telegram_001_smoke_evidence=research/amn2/phase-11-801f8c3-private-telegram-transient-smoke-2026-07-14.md
```

# Текущий override 2026-07-14: 801f8c3 transient Telegram smoke gate ready

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_telegram_001_gate=reviewed-ready-awaiting-exact-approval
phase11_telegram_001_source=codex-vps-test-prep|801f8c3|origin_sync|clean
phase11_telegram_001_production=overlay_801f8c3|source_hashes_match|web_private_healthy
phase11_telegram_001_actor=first_of_2_configured_admins|id_private_not_emitted
phase11_telegram_001_identity=bound_to_prior_sanitized_getMe_evidence
phase11_telegram_001_data=sqlite_online_backup_clone_0600_in_private_run_dir_0700|production_db_read_only
phase11_telegram_001_runtime=transient_only|internal_ttl_120|RuntimeMaxSec_180|Restart_no|TimeoutStopSec_15|KillMode_control_group
phase11_telegram_001_updates=message_only|exact_start|backlog_0_to_1_to_0|one_start_response|callbacks_false
phase11_telegram_001_regular_bot=inactive_disabled_before_after|persistent_activation_false
phase11_telegram_001_awg=must_remain_running|never_stop_restart_recreate|identity_restart_peer_set_invariant
phase11_telegram_001_tests=focused_21_passed|bot_settings_184_passed|read_only_vps_preflight_passed
phase11_telegram_001_live_effect=none|telegram_api_not_called|polling_not_started
phase11_telegram_001_approval=not_received|not_consumed
phase11_telegram_001_exact_phrase=APPROVE PHASE11_801F8C3_PRIVATE_TELEGRAM_FIRST_CONFIGURED_ADMIN_TRANSIENT_START_SMOKE_AND_ONE_RESPONSE_ON_CLONE_DB_TTL120_WATCHDOG180_BACKLOG_0_1_0_CLEANUP_WITH_REGULAR_BOT_DISABLED_AND_AWG_UNTOUCHED
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_telegram_public_false
phase11_next=OPERATOR_EXACT_APPROVAL_FOR_PHASE11_801F8C3_TRANSIENT_TELEGRAM_SMOKE
phase11_telegram_001_gate_evidence=research/amn2/phase-11-801f8c3-private-telegram-single-admin-transient-smoke-live-gate-review-2026-07-14.md
```

# Текущий override 2026-07-14: 801f8c3 private overlay rollout completed

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_801f8c3_rollout=completed-pass|run_20260714T165948Z
phase11_801f8c3_approval=received|consumed
phase11_801f8c3_production=overlay_801f8c3|web_active_enabled_http_ok_loopback_only
phase11_801f8c3_delta=exact_2_paths|schema_none|db_migration_none
phase11_801f8c3_database=file_logical_counts_hashes_unchanged|integrity_ok|fk_0|tables_15|rows_88
phase11_801f8c3_bot=inactive|disabled|process_0|telegram_not_called
phase11_801f8c3_awg=never_stopped_restarted_recreated|restart_0|running|peers_12|set_unchanged
phase11_801f8c3_rollback=first_run_20260714T165601Z_verified_pass|successful_run_bundle_retained
phase11_801f8c3_postflight=passed|write_gates_false_false|api_3040_listener_0
phase11_801f8c3_excluded=schema|api_smoke|telegram_polling_send|bot_enable_start|peer_config|public|reboot_provider
phase11_telegram_001=overlay_prerequisite_completed|transient_smoke_not_started|separate_exact_gate_required
phase11_upstream_automation=amn2-upstream-orchestrator_active_retargeted_current_phase11_task|legacy_chain_paused
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_telegram_public_false
phase11_next=REVIEW_PHASE11_801F8C3_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
phase11_801f8c3_rollout_evidence=research/amn2/phase-11-801f8c3-private-overlay-rollout-2026-07-14.md
```

# Текущий override 2026-07-14: 801f8c3 private overlay gate ready

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_801f8c3_rollout_gate=reviewed-ready-awaiting-exact-approval
phase11_801f8c3_package_commit=4166dd6|origin_sync
phase11_801f8c3_package_sha256=693DF74192E55A2231F45C0ADF153B745C7D2AF8EDEDA67830D02CB620A4C3FF
phase11_801f8c3_source_sha256=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
phase11_801f8c3_apply_sha256=85AE2C0E5A1E949529342AF2939A577AE23B3924653A344E1E77465B898E56AF
phase11_801f8c3_runbook_sha256=923DBB704BDDF464DEB1D3037703B58AF8B102CFCC3A174509A05FB3FB4B42CC
phase11_801f8c3_allowed_live=package_fetch_verify|ssh_preflight|upload|web_brief_stop|source_sqlite_snapshot|offline_source_apply|web_start_verify|automatic_rollback
phase11_801f8c3_forbidden_live=schema_migration|api_smoke|telegram_polling_send|bot_enable_start|peer_config|public|reboot_provider
phase11_801f8c3_awg=must_remain_running|restart_count_unchanged|peer_count_and_set_unchanged
phase11_801f8c3_approval=not_received|not_consumed
phase11_801f8c3_exact_phrase=APPROVE_PHASE11_801F8C3_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_AWG_UNTOUCHED
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
phase11_next=OPERATOR_EXACT_APPROVAL_FOR_PHASE11_801F8C3_PRIVATE_OVERLAY
phase11_801f8c3_gate_evidence=research/amn2/phase-11-801f8c3-private-overlay-rollout-gate-review-2026-07-14.md
```

# Текущий override 2026-07-14: 801f8c3 private Telegram overlay package ready

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_801f8c3_package_status=completed-local-ready-not-uploaded
phase11_801f8c3_source=codex-vps-test-prep|801f8c3406121549eb6a19150be009cfc0ea88d0|origin_sync|clean
phase11_801f8c3_production=overlay_3c91601|live_effect_none
phase11_801f8c3_package=dist/amn2-private-telegram-smoke-overlay-801f8c3.zip|bytes_8794194|sha256_693DF74192E55A2231F45C0ADF153B745C7D2AF8EDEDA67830D02CB620A4C3FF
phase11_801f8c3_source_zip=bytes_8851677|entries_371|sha256_B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
phase11_801f8c3_package_contents=4_entries|source_zip|source_checksum|bound_apply|runbook
phase11_801f8c3_delta=2_paths|54_insertions|1_deletion|schema_none|db_migration_none
phase11_801f8c3_apply=sha256_85AE2C0E5A1E949529342AF2939A577AE23B3924653A344E1E77465B898E56AF|canonical_binding_only
phase11_801f8c3_runbook=sha256_923DBB704BDDF464DEB1D3037703B58AF8B102CFCC3A174509A05FB3FB4B42CC
phase11_801f8c3_tests=packaged_focused_21_passed|packaged_bot_settings_184_passed|compileall_passed|tooling_root_23_passed|harness_passed
phase11_801f8c3_security=forbidden_0|required_missing_0|secret_literals_0|preexisting_low_entropy_doc_placeholders_2_classified
phase11_801f8c3_runtime_boundary=awg_untouched|telegram_not_called|vps_ssh_not_called|regular_bot_inactive_disabled_baseline
phase11_801f8c3_live_gate=not_approved|not_consumed
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
phase11_next=REVIEW_PHASE11_801F8C3_PRIVATE_OVERLAY_ROLLOUT_GATE_AND_PREPARE_EXACT_APPROVAL
phase11_801f8c3_package_evidence=research/amn2/phase-11-801f8c3-private-telegram-overlay-package-prep-2026-07-14.md
```

# Текущий override 2026-07-14: Phase 11 Telegram smoke pre-ack hardening

```text
active_phase=Phase 11 Controlled Launch and Operations
phase11_telegram_001_review_3c91601=stop-pre_ack_filtered_update_ack_race
phase11_telegram_001_hardening=completed-tested-committed-pushed
phase11_telegram_001_source=codex-vps-test-prep|801f8c3|origin_sync
phase11_telegram_001_production=overlay_3c91601|live_polling_not_started|live_gate_not_ready
phase11_telegram_001_fix=pre_ack_webhook_clear|pending_exactly_1|ack_selected_start|post_ack_pending_0
phase11_telegram_001_boundary=one_configured_admin|exact_start|message_only|clone_writes_only|ttl_max_120
phase11_telegram_001_watchdog=runtime_max_180|restart_no|timeout_stop_15|kill_mode_control_group|future_exact_gate
phase11_telegram_001_tests=focused_21_passed|bot_settings_184_passed|compile_passed|diff_check_passed
phase11_telegram_001_runtime=regular_bot_inactive_disabled_baseline|persistent_activation_false
phase11_telegram_001_live_effect=none|telegram_api_not_called|vps_ssh_not_called|awg_untouched
phase11_upstream_automation=amn2-upstream-orchestrator_active_retargeted_current_phase11_task|legacy_chain_paused
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
phase11_next=PREPARE_PHASE11_801F8C3_PRIVATE_TELEGRAM_SMOKE_OVERLAY_PACKAGE_AND_ROLLOUT_GATE
phase11_telegram_001_evidence=research/amn2/phase-11-3c91601-private-telegram-single-admin-transient-smoke-gate-review-2026-07-14.md
```

# Текущий override 2026-07-14: Phase 10 closed, Phase 11 handoff ready

```text
active_phase=Phase 11 Controlled Launch and Operations
phase10_status=closed-completed-product-recovered-deployed-accepted
phase10_final_source=codex-vps-test-prep|3c91601|origin_sync|clean
phase10_final_vps=overlay_3c91601|web_active_200|awg_running_restart_0|12_peers
phase10_final_client_acceptance=passed|handshake_2026-07-14T11:29:53Z|rx_205184|tx_7176839
phase10_final_remainders=none_product_package_schema_acceptance
phase10_final_tests=amn2_870_passed_1_skipped_1_warning|root_20_and_43_passed|harness_passed
phase10_closeout_packet=docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md
phase11_entry=docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md
phase11_handoff=docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md
phase11_first_message=docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md
phase11_start_phrase=AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START
phase11_first_command=GPT-5.6_SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
phase11_stop_lines=execution_go_false|config_generation_false|config_delivery_false|peer_creation_false|live_vps_ssh_telegram_public_false
phase11_upstream_automation=amn2-upstream-orchestrator_active_dynamic|legacy_chain_paused
phase10_closeout_evidence=research/amn2/phase-10-final-closeout-phase11-handoff-2026-07-14.md
```

# Текущий override 2026-07-14: 3c91601 existing-client acceptance passed

```text
phase10_3c91601_existing_client_acceptance=passed-fresh-handshake-and-traffic
phase10_3c91601_acceptance_window=2026-07-14T11:30:40Z_to_11:31:40Z
phase10_3c91601_acceptance_handshake=2026-07-14T11:29:53Z|later_confirmed_2026-07-14T11:39:06Z
phase10_3c91601_acceptance_traffic=rx_205184|tx_7176839
phase10_3c91601_acceptance_peers=12_stable|set_unchanged
phase10_3c91601_runtime=overlay_3c91601|web_active_200|awg_running_restart_0
phase10_3c91601_database=integrity_ok|fk_0|hashes_unchanged|counts_unchanged
phase10_3c91601_external_remainder=closed
phase10_3c91601_product_package_schema_remainder=none_identified
phase10_3c91601_closeout_readiness=ready-for-final-packet
phase10_3c91601_formally_closed=false-until-closeout-packet
phase10_3c91601_next=PREPARE_PHASE10_FINAL_CLOSEOUT_PACKET_AND_PHASE11_HANDOFF
phase10_3c91601_acceptance_evidence=research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md
```

# Текущий override 2026-07-14: 3c91601 post-deploy closeout readiness review

```text
phase10_3c91601_closeout_review=completed-technical-ready-client-acceptance-pending
phase10_3c91601_source=3c91601|origin_match|clean
phase10_3c91601_runtime=overlay_3c91601|web_active_200|awg_running_restart_0|peers_12_set_unchanged
phase10_3c91601_database=integrity_ok|fk_0|schema_3_tables_5_indexes|existing_counts_unchanged
phase10_3c91601_rollback=present|hashes_verified
phase10_3c91601_observation=2026-07-14T11:18:03Z_to_11:19:04Z|61s|rx_0|tx_0
phase10_3c91601_latest_handshake=2026-07-13T21:44:30Z|not_post_rollout_fresh
phase10_3c91601_product_remainder=none_identified
phase10_3c91601_exact_remainder=one_existing_client_connect_then_read_only_handshake_traffic_verify
phase10_3c91601_new_config_required=false
phase10_3c91601_next=VERIFY_ONE_EXISTING_CLIENT_POST_3C91601_HANDSHAKE_AND_TRAFFIC_READ_ONLY
phase10_3c91601_closeout_evidence=research/amn2/phase-10-3c91601-post-deploy-acceptance-closeout-readiness-2026-07-14.md
```

# Текущий override 2026-07-14: 3c91601 private VPS rollout completed

```text
phase10_3c91601_rollout_status=completed-pass-with-verified-automatic-rollback
phase10_3c91601_approval=consumed
phase10_3c91601_runs=20260714T101311Z_rollback_pass|20260714T101632Z_rollout_pass
phase10_3c91601_vps_overlay=3c91601
phase10_3c91601_schema=3_new_tables|5_new_indexes|new_rows_0|existing_rows_unchanged|integrity_ok|fk_0
phase10_3c91601_clone=exact_migration_pass|api_smoke_pass|safe_evidence_scan_pass|removed
phase10_3c91601_production_api_smoke=false
phase10_3c91601_runtime=web_active_enabled_http_200|bot_inactive_disabled|write_gates_false
phase10_3c91601_awg=never_stopped_or_restarted|running|restart_count_0|12_peers|peer_set_unchanged
phase10_3c91601_web_downtime_seconds=55
phase10_3c91601_rollback=/root/amn2-rollbacks/3c91601-20260714T101632Z|0700_root_root|hashes_verified
phase10_3c91601_post_traffic=5s_delta_0_0|latest_handshake_2026-07-13T21:44:30Z|fresh_client_acceptance_pending
phase10_3c91601_excluded=peer_config_telegram_public_reboot_provider_enrollment_revoke
phase10_3c91601_next=review_post_deploy_acceptance_and_phase10_closeout_readiness
phase10_3c91601_rollout_evidence=research/amn2/phase-10-3c91601-private-vps-rollout-2026-07-14.md
```

# Текущий override 2026-07-14: 3c91601 exact rollout scope consumed

```text
phase10_3c91601_rollout_scope_status=approved-consumed-completed-pass
phase10_3c91601_rollout_scope=checksum_upload|tracked_source_snapshot|sqlite_backup|clone_schema_migration|clone_api_smoke|production_schema_checkpoint|web_activation|automatic_rollback
phase10_3c91601_schema_delta=3_tables|5_indexes|existing_rows_unchanged|new_rows_zero
phase10_3c91601_runtime_invariant=amnezia_awg2_never_stopped_or_restarted|peer_set_unchanged|web_only_brief_stop|bot_inactive_disabled
phase10_3c91601_clone_boundary=all_api_token_server_sync_audit_writes_clone_only|production_api_smoke_forbidden
phase10_3c91601_rollback=remove_exact_tracked_roots_then_restore_source_and_marker|verified_sqlite_restore_after_checkpoint|web_recovery|awg_untouched
phase10_3c91601_scope_tests=harness_passed_all_stop_lines_false|scoped_20_passed|root_43_passed|diff_check_passed
phase10_3c91601_exact_phrase=APPROVE PHASE10_3C91601_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_SNAPSHOT_CLONE_DB_MIGRATION_AND_WEB_ACTIVATION_WITH_ROLLBACK
phase10_3c91601_live_effect=package_uploaded|source_applied|schema_migrated|web_activated|awg_unchanged
phase10_3c91601_next=post_deploy_acceptance_and_closeout_readiness_review
phase10_3c91601_rollout_evidence=research/amn2/phase-10-3c91601-private-vps-rollout-gate-review-2026-07-14.md
```

# Текущий override 2026-07-14: 3c91601 private VPS package applied

```text
phase10_3c91601_package_status=completed-uploaded-applied-verified
phase10_3c91601_source=codex-vps-test-prep|3c916015c10add37886370d04af70f0343f7f691|origin_0_0|clean
phase10_3c91601_vps_base=before_1c7fb78|after_3c91601|runtime_verified
phase10_3c91601_package=dist/amn2-vps-update-and-smoke-kit-3c91601.zip
phase10_3c91601_package_bytes=8800099
phase10_3c91601_package_sha256=12E90EB54FCC374C84B6AA987C65E5644C4BD1B974089E81E16D00780389FB6E
phase10_3c91601_source_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
phase10_3c91601_contents=package_5|source_371_entries_328_files_43_dirs|required_missing_0|forbidden_0|mismatches_0
phase10_3c91601_delta=32_paths|12_added|20_modified|0_deleted|4240_insertions|62_deletions
phase10_3c91601_tests=focused_237_passed_1_warning|full_870_passed_1_skipped_1_warning|tooling_23_passed|root_43_passed|compile_passed
phase10_3c91601_review=checksums_bindings_lf_bash_markdown_secret_scan_diff_passed
phase10_3c91601_harness=next_command_passed|product_diff_passed|all_stop_lines_false
phase10_3c91601_live_effect=uploaded_applied|clone_smoke_pass|schema_pass|web_active|awg_unchanged
phase10_3c91601_package_followup=rollout_completed_post_deploy_acceptance_pending
phase10_3c91601_evidence=research/amn2/phase-10-3c91601-vps-package-prep-2026-07-14.md
```

# Текущий override 2026-07-14: canonical hybrid recovery replacement

```text
phase10_recovery_replacement_status=completed-generated-downloaded-verified-rehearsed
phase10_recovery_replacement_run_id=20260714T045754Z
phase10_recovery_replacement_code_commits=dd87ea7|117b72c
phase10_recovery_replacement_format=amn2-full-recovery-v1|rsa_oaep_sha256_wrapped_fernet
phase10_recovery_replacement_artifact=backups/amn2-recovery/20260714T045754Z/amn2-recovery-20260714T045754Z.hybrid.enc
phase10_recovery_replacement_bytes=19220
phase10_recovery_replacement_sha256=2c618fa52aed038eb494a892480970795c554bddd6649156e1fe5a9c00e52280
phase10_recovery_replacement_metadata=passed|warnings_none|newline_defect_closed
phase10_recovery_replacement_verify=decrypt_passed|13_files|12_manifest_entries|sqlite_ok|12_awg_peers|12_peer_psks|systemd_contract_passed
phase10_recovery_replacement_secret_boundary=private_key_local_acl_only|private_key_not_transferred|production_plaintext_not_written|live_symmetric_stdin_removed
phase10_recovery_replacement_runtime=amnezia_awg2_running_restart_count_0|web_active_enabled|bot_inactive_disabled|no_service_stop_or_restart
phase10_recovery_replacement_remote_cleanup=production_temp_removed|staging_temp_removed
phase10_recovery_replacement_second_copy=F:\AMN2-Recovery\20260714T045754Z|sha256_verified|private_key_not_copied
phase10_recovery_replacement_sanitized=sha256_d7845bdbd8623476bcfb81d6a602cfe8604aebd571a0ae38cc1c49bb36eab1d9|14_files|13_manifest_entries|sqlite_12_tables_0_rows
phase10_recovery_replacement_staging=verify_extract_passed|systemd_analyze_passed|start_guard_exit_64|runtime_not_installed|ssh_only_after_cleanup
phase10_recovery_replacement_tests=focused_20_passed|root_43_passed|compile_passed|diff_review_passed
phase10_recovery_previous_copy=retained_with_key_as_fallback_pending_operator_retirement
phase10_recovery_replacement_launch_plan_change=false
phase10_recovery_replacement_live_restore_apply=false
phase10_recovery_replacement_evidence=research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md
```

# Текущий override 2026-07-13: isolated restore rehearsal completed

```text
phase10_restore_rehearsal_status=completed-safe-split-local-production-and-sanitized-staging
phase10_restore_rehearsal_run_id=20260713T215439Z
phase10_restore_rehearsal_code_commit=f1ec6ca
phase10_restore_rehearsal_local=encrypted_hash_and_decrypt_passed|production_plaintext_written_false|13_files|12_manifest_entries|sqlite_ok|12_awg_peers|12_peer_psks|systemd_contract_passed
phase10_restore_rehearsal_sanitized=sha256_ff10c841946c8fa5725ef974360bb987dad942e8353ac5fae09ab80e0dd1ae59|14_files|13_manifest_entries|sqlite_12_tables_0_rows|exact_safe_contract_passed
phase10_restore_rehearsal_staging=45.95.232.7|ubuntu_24_04|key_only_ssh|ufw_default_deny|ssh_only_external_listener
phase10_restore_rehearsal_runtime=systemd_analyze_passed|start_guard_exit_64|runtime_not_installed|services_not_started|remote_tree_removed
phase10_restore_rehearsal_secret_boundary=production_key_not_uploaded|production_plaintext_not_uploaded|schema_only_fixture
phase10_restore_rehearsal_production_effect=none|production_vps_not_contacted
phase10_restore_rehearsal_tests=focused_11_passed|root_34_passed|compile_passed|diff_review_passed
phase10_restore_rehearsal_warning=backup_metadata_writer_missing_newline_between_source_overlay_and_container_name
phase10_restore_rehearsal_next=fix_metadata_writer_and_generate_new_verified_immutable_bundle|keep_existing_bundle_until_replacement_verified
phase10_restore_rehearsal_launch_plan_change=false
phase10_restore_rehearsal_live_restore_apply=false
phase10_restore_rehearsal_evidence=research/amn2/phase-10-isolated-restore-rehearsal-2026-07-13.md
```

# Текущий override 2026-07-13: external full recovery backup

```text
phase10_external_recovery_backup_status=completed-created-downloaded-decrypted-verified
phase10_external_recovery_backup_format=amn2-full-recovery-v1|fernet_encrypted_tar_gz
phase10_external_recovery_backup_artifact=backups/amn2-recovery/amn2-recovery-20260713T153359Z.tar.gz.enc
phase10_external_recovery_backup_bytes=19000
phase10_external_recovery_backup_sha256=3e2339fdbe7e78bcdd1ab90510e204acdffba0b09df5c4ae05dae64293136cb8
phase10_external_recovery_backup_scope=consistent_sqlite|app_env|servers_yml|source_marker|awg0_config|awg_server_keys|container_start|systemd_units|safe_metadata
phase10_external_recovery_backup_verify=decrypt_passed|13_files|12_sha256_checks|sqlite_integrity_ok|awg_contract_passed|host_runtime_contract_passed
phase10_external_recovery_backup_key_storage=separate_user_profile_directory|current_user_acl_only|not_git
phase10_external_recovery_backup_remote_cleanup=encrypted_copy_removed|plaintext_stage_removed|key_removed
phase10_external_recovery_backup_runtime_effect=none|amnezia_awg2_running_restart_count_0|post_backup_traffic_positive
phase10_external_recovery_backup_git_guard=backups_directory_ignored
phase10_external_recovery_backup_second_copy=completed_removable_media_f|fat32|artifact_encrypted|sha256_verified|key_not_copied
phase10_external_recovery_backup_second_copy_path=F:\AMN2-Recovery\20260713T153359Z
phase10_external_recovery_backup_residual=isolated_rehearsal_completed|metadata_writer_fix_and_corrected_bundle_pending
phase10_external_recovery_backup_evidence=research/amn2/phase-10-external-full-recovery-backup-2026-07-13.md
```

# Текущий override 2026-07-13: VPS provider recovery confirmed

```text
phase10_vps_incident_status=recovered-provider-side
phase10_vps_recovery_date=2026-07-13
phase10_vps_recovery_transport=ssh22_reachable|icmp_reachable
phase10_vps_recovery_runtime=overlay_1c7fb78|amnezia_awg2_running_restart_count_0|awg0_readable|web_active_enabled|bot_inactive_disabled
phase10_vps_recovery_peer_summary=12_peers|1_handshake_ever|fresh_handshake_confirmed
phase10_vps_recovery_traffic_sample_10s=rx_delta_144512|tx_delta_1266159
phase10_vps_recovery_operator_acceptance=latest_test_config_connected_in_official_amnezia_client
phase10_vps_recovery_mutations_by_codex=false
phase10_current_source_head=3c91601
phase10_vps_overlay_update_status=not_uploaded_still_1c7fb78
phase10_vps_recovery_evidence=research/amn2/phase-10-vps-provider-recovery-and-live-traffic-2026-07-13.md
```

# Текущий override 2026-07-12: lifecycle, web diagnostics, cascade revoke

```text
active_phase=Phase 10 product recovery with progress harness
phase10_current_source_branch=codex-vps-test-prep
phase10_current_source_head=3c91601
phase10_latest_product_step=PHYSICAL_DEVICE_CASCADE_REVOKE_SECURITY_HARDENING
phase10_latest_product_commit=3c91601
phase10_enrollment_lifecycle_status=completed-tested-reviewed-pushed-local-only
phase10_enrollment_lifecycle_commit=bdbf740
phase10_enrollment_lifecycle=issued|claimed|config_ready|delivered|acceptance_verified
phase10_enrollment_lifecycle_evidence=timestamp|safe_duration_ms|failure_stage|secret_free_evidence
phase10_read_only_admin_web_diagnostics_status=completed-tested-reviewed-pushed
phase10_read_only_admin_web_diagnostics_commit=956e76b
phase10_read_only_admin_web_diagnostics=desired|observed|drift|freshness|reason|recommended_action|evidence_count|no_apply
phase10_cascade_revoke_status=completed-tested-reviewed-pushed-security-fix
phase10_cascade_revoke_commit=3c91601
phase10_cascade_revoke=operation_plan_remote_first|tickets|delivery_links|assignments|remote_peer|stale_reconnect_blocked
phase10_security_fix=local_only_device_delete_refused_when_remote_apply_closed
phase10_latest_tests=lifecycle_17_passed|web_drift_security_55_passed_1_warning|cascade_3_passed|expanded_106_passed_1_warning|revoke_regression_20_passed|full_870_passed_1_skipped_1_warning
phase10_latest_diff_review=passed
phase10_upstream_forced_scan_2026_07_12=prvtpro_kyoresuas_amnezia_no_relevant_delta_vs_2026_07_11
phase10_launch_plan_change=false
phase10_enrollment_launch_blocking=false_when_self_service_not_required
phase10_enrollment_public_route=false
phase10_drift_auto_remediation=false
phase10_live_remediation=false
phase10_vps_runtime_check_2026_07_12=confirmed_client_outage|ssh22_timeout|ping_timeout|provider_or_host_recovery_required|no_runtime_change_performed
phase10_vps_runtime_last_verified=2026-07-11|overlay_1c7fb78|web_active_enabled|amnezia_awg2_running|bot_inactive_disabled
phase10_next_local_step=START_PHASE10_3C91601_VPS_PACKAGE_PREP_SLICE
phase10_latest_evidence=research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md
```

# Текущий override 2026-06-09

## Текущий контрольный срез (актуализировано 2026-07-12)

Phase 9 старт из Phase 8 handoff принят. Phase 8 закрыта, уже подготовленные
Phase 9 docs/commits остаются existing material, первый Phase 9 трек
подтвержден как private/self config readiness with naming, без открытия
live/config/public execution.

```text
current_chat_state=Phase 10 product recovery active
phase8_final_status=launch-ready-with-explicit-limitations
phase9_material_status=prepared-existing-material
phase9_continuation_chat_required=false_current_chat_started
active_phase=Phase 10 product recovery with progress harness
next_phase=Phase 10 controlled package rollout and dedicated-device lifecycle
phase10_execution_chat_required=false_current_chat_active
selected_lane=HARDENING_PRODUCTIZATION
phase10_transition_status=active-product-tested-status-synced
phase10_transition_doc=docs/AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_ENTRY.ru.md
phase10_next_chat_handoff=docs/NEXT_CHAT_AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS.ru.md
phase9_9_2_final_closeout_packet=docs/AMN2_PHASE_9_9_2_FINAL_CLOSEOUT_PACKET.ru.md
phase10_progress_harness_script=scripts/phase9_progress_harness.py
phase10_progress_harness_tests=tests/test_phase9_progress_harness.py
phase10_progress_harness_policy=require-product-step-before-next-product-command
phase10_docs_sync_policy=after-product-code-test-evidence-only
phase10_first_product_step=completed
phase10_first_product_reason=config_share_restore_schema_index_declaration_contract_test_status_scoped_pytest_66_passed_product_fix_pushed
phase10_latest_product_step=READ_ONLY_DESIRED_OBSERVED_DRIFT_DIAGNOSTICS
phase10_latest_product_commit=fc48a7e
phase10_latest_product_push_status=done
phase10_current_source_branch=codex-vps-test-prep
phase10_current_source_head=e709746
phase10_latest_engineering_check=DEVICE_PASSPORT_AND_ENROLLMENT_LOCAL_SERVICE_CONTRACTS
phase10_latest_engineering_check_commit=e709746
phase10_read_only_drift_status=completed-code-tested-reviewed-pushed-local-only
phase10_read_only_drift_commit=fc48a7e
phase10_read_only_drift_result=deterministic_desired_observed_drift|aligned_missing_remote_unexpected_remote_stale_observation_observation_failed_unknown|safe_evidence|safe_next_action|no_auto_remediation
phase10_device_passport_status=completed-code-tested-reviewed-pushed-local-only
phase10_device_passport_commit=a2cbcfa
phase10_device_passport_result=generated_stable_device_id|owner_platform_official_client_import_schema|sha256_config_fingerprint|last_seen_acceptance|dynamic_reconciliation_snapshot|no_hardware_fingerprint_posture_mdm_claims
phase10_device_enrollment_ticket_status=completed-local-service-only-route-disabled-not-launch-blocking
phase10_device_enrollment_ticket_commit=e709746
phase10_device_enrollment_ticket_result=one_time_raw_display|hash_and_safe_prefix_only|ttl_single_use_default|revoke|atomic_claim|idempotent_exact_retry|uniform_unavailable_error|raw_token_absent_from_db_logs_audit_read_metadata
phase10_device_identity_tests=drift_scoped_16_passed|passport_schema_security_79_passed|enrollment_focused_9_passed|expanded_127_passed|full_864_passed_1_skipped_1_warning|diff_review_passed
phase10_device_identity_evidence=research/amn2/phase-10-drift-device-passport-enrollment-ticket-2026-07-12.md
phase10_drift_launch_inclusion=nearest-read-only-product-slice-requires-operator-surface-binding-no-apply
phase10_enrollment_launch_inclusion=non-blocking-when-self-service-onboarding-is-out-of-scope
phase10_enrollment_public_route=false
phase10_drift_auto_remediation=false
phase10_44287d4_package_eligibility=blocked-superseded-by-source-head-e709746
phase10_vps_runtime_check_2026_07_12=management-transport-unreachable-ssh22-timeout-ping-timeout-no-runtime-change
phase10_vps_runtime_last_verified=2026-07-11|overlay_1c7fb78|web_active_enabled|amnezia_awg2_running|bot_inactive_disabled
phase10_vps_runtime_restore_policy=after_any_test_stop_restore_original_production_runtime_verify_and_notify_operator
phase10_upstream_orchestrator_test_status=completed-integrated-into-phase10
phase10_upstream_orchestrator_test_date=2026-07-11
phase10_upstream_orchestrator_test_baseline=ecf8563
phase10_upstream_contract_hardening_branch=codex/phase10-upstream-contract-hardening
phase10_upstream_contract_hardening_commit=dc0ed92
phase10_upstream_contract_hardening_status=completed-integrated-tested-reviewed-pushed
phase10_upstream_contract_hardening_result=awg_h_uint32_or_range_shape|non_overlapping_h1_h4|settings_defaults_render_input_bound|working_defaults_unchanged
phase10_upstream_contract_hardening_tests=focused_56_passed|expanded_123_passed_1_warning|full_840_passed_1_skipped_1_warning|python_3_12_13_compile_and_runtime_smoke_passed
phase10_upstream_contract_hardening_integration=ff_only_dc0ed92_then_ascii_lexical_review_fix_44287d4
phase10_upstream_contract_hardening_integration_tests=focused_57_passed|expanded_124_passed_1_warning|full_841_passed_1_skipped_1_warning|python_3_12_13_compile_and_runtime_smoke_passed|diff_review_passed
phase10_upstream_contract_hardening_candidate_status=integrated-do-not-reoffer-dc0ed92
phase10_upstream_contract_hardening_live_actions=false
phase10_upstream_contract_hardening_evidence=research/amn2/phase-10-upstream-orchestrator-test-and-awg2-contract-hardening-2026-07-11.md
phase10_launch_plan_change=false
phase10_dynamic_subnet_source_of_truth=post-launch-candidate
phase10_android_tv_reacceptance_trigger=next-published-amnezia-client-release-only
phase10_restore_single_flight_idempotency=required-when-restore-apply-reopens
phase10_launch_scope_exclusions=warp|nginx|marketplace|public_tunnels|broad_multi_protocol_parity
phase10_plan_device_quota_admin_ui_status=completed-code-tested-reviewed-pushed-local-only
phase10_plan_device_quota_admin_ui_result=authenticated_plans_view|set_or_clear_max_devices|effective_min_with_global_limit|csrf|validation|audit|strict_surface_policy
phase10_plan_device_quota_admin_ui_tests=new_6_passed|expanded_69_passed|security_38_passed|full_829_passed_1_skipped_1_warning|diff_review_passed
phase10_plan_device_quota_admin_ui_vps_status=not_uploaded_current_overlay_1c7fb78
phase10_plan_device_quota_admin_ui_evidence=research/amn2/phase-10-plan-device-quota-admin-ui-2026-07-11.md
phase10_ecf8563_vps_package_status=completed-local-package-ready-not-vps-smoked
phase10_ecf8563_vps_package=dist/amn2-vps-update-and-smoke-kit-ecf8563.zip
phase10_ecf8563_vps_package_sha256=0AE0B2EC04986B0475647C0971D49F712A173840404D0F359CB1C98A9BD59DDE
phase10_ecf8563_source_sha256=15AA131EAA1B3B878ADB6D0FB04ED8DF3114D08641966EFC018D6E528D6CE990
phase10_ecf8563_vps_package_contents=package_entries_5|source_entries_361|source_files_318|source_dirs_43|required_missing_0|forbidden_entries_0|content_mismatches_0
phase10_ecf8563_vps_package_tests=focused_38_passed_1_warning|full_829_passed_1_skipped_1_warning|tooling_5_passed|orchestration_20_passed|offline_fallback_regression_passed|bash_syntax_passed|shell_lf_no_bom|markdown_hygiene_passed
phase10_ecf8563_vps_package_harness=tests_15_passed|product_only_scope_passed|all_stop_lines_false
phase10_ecf8563_vps_package_vps_status=not_uploaded_current_overlay_1c7fb78
phase10_ecf8563_vps_package_eligibility=blocked-superseded-by-integrated-source-head-44287d4
phase10_ecf8563_vps_package_evidence=research/amn2/phase-10-ecf8563-vps-package-prep-2026-07-11.md
phase10_config_assignment_policy=dedicated_device_default|owner_shared_admin_only
phase10_client_device_quota=min_MAX_DEVICES_PER_USER_and_plans.max_devices
phase10_client_multi_device_rule=one_peer_and_one_conf_per_physical_device
phase10_owner_shared_rule=one_peer_unbounded_physical_count_not_server_enforceable
phase10_config_assignment_tests=scoped_128_passed_1_skipped_1_warning|full_823_passed_1_skipped_1_warning|web_7_passed_1_warning|diff_review_passed
phase10_config_assignment_vps_overlay=smoke_pass_1c7fb78_web_active
phase10_1c7fb78_vps_package_status=completed-live-smoke-pass
phase10_1c7fb78_vps_package=dist/amn2-vps-update-and-smoke-kit-1c7fb78.zip
phase10_1c7fb78_vps_package_sha256=AEEB5A5C81354D7631F14DF57D7422CF02C08157CB4075B4B37B5BFD2BE6015B
phase10_1c7fb78_source_sha256=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
phase10_1c7fb78_package_contents=package_entries_5|source_entries_359|source_files_316|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_1c7fb78_package_tests=toolchain_ok|focused_131_passed_1_skipped_1_warning|full_823_passed_1_skipped_1_warning|tooling_4_ok|bash_syntax_passed|markdown_hygiene_passed
phase10_1c7fb78_package_evidence=research/amn2/phase-10-1c7fb78-vps-package-prep-2026-07-11.md
phase10_1c7fb78_rollout_gate_review_status=approved-consumed-completed-pass
phase10_1c7fb78_rollout_preflight=overlay_34b3b43|web_active_200_private|bot_inactive_disabled|dual_write_gates_false|db_integrity_ok|schema_columns_absent|rollback_ready
phase10_device8_owner_shared_result=passed|owner_matches_single_active_configured_admin_user|db_admin_flag_true|assignment_owner_shared|linked_orders_0|owner_reassignment_false|peer_mutation_false
phase10_device8_reconciliation_runner_sha256=D4566B42D6FCB7B6891F65826E0E302DF59CBEC49536D3AFC4A3A3ED789C7E72
phase10_1c7fb78_rollout_gate_evidence=research/amn2/phase-10-1c7fb78-private-vps-schema-owner-shared-rollout-gate-review-2026-07-11.md
phase10_1c7fb78_rollout_exact_phrase=APPROVE PHASE10_1C7FB78_PRIVATE_VPS_UPLOAD_SCHEMA_MIGRATION_DEVICE8_OWNER_SHARED_AND_CLONE_DB_API_WEB_SMOKE_WITH_ROLLBACK
phase10_1c7fb78_rollout_run_id=20260711T154907Z
phase10_1c7fb78_rollout_rollback_path=/root/amn2-rollbacks/1c7fb78-20260711T154907Z
phase10_1c7fb78_rollout_result=source_1c7fb78|schema_migrated|clone_api_smoke_pass|production_counts_6_8_8|audit_43_45|device8_owner_shared|owner_admin_true|owner_reassigned_false|peer_unchanged|web_200_303|bot_inactive_disabled
phase10_1c7fb78_rollout_recovery=5_verified_automatic_rollbacks_before_6th_success
phase10_1c7fb78_rollout_evidence=research/amn2/phase-10-1c7fb78-private-vps-schema-owner-shared-rollout-2026-07-11.md
phase10_plan_device_quota_rows_configured=0_global_fallback_active
phase10_telegram_admin_integration_status=completed-code-tested-pushed-local-only
phase10_telegram_admin_integration_status_base=4cf93f8
phase10_telegram_admin_integration_status_result=callback_registered|admin_authorized|typed_hash_free_allowlist|lifecycle_read_only|no_mutations|count_only_safe_audit|secret_adjacent_surface_policy
phase10_telegram_admin_integration_status_test_status=red_import_errors|focused_140_passed|expanded_241_passed_1_warning|full_796_passed_1_skipped_1_warning
phase10_telegram_admin_integration_status_harness=tests_12_passed|product_and_docs_scope_passed
phase10_telegram_admin_integration_status_evidence=research/amn2/phase-10-telegram-admin-integration-credential-status-2026-07-10.md
phase10_telegram_admin_integration_status_live_actions=false
phase10_telegram_admin_integration_status_vps_overlay=6f475e6_34b3b43_not_uploaded
phase10_telegram_admin_integration_status_bot_runtime=not_started
phase10_34b3b43_vps_package_prep_status=completed-local-package-ready-not-vps-smoked
phase10_34b3b43_vps_package=dist/amn2-vps-update-and-smoke-kit-34b3b43.zip
phase10_34b3b43_vps_package_sha256=385EAC3DC53B9E9C1EA35F168B01D545177FEC459D948239F93B4D40A64D499C
phase10_34b3b43_source_package=dist/amn2-vps-update-and-smoke-kit-34b3b43/amn2-codex-vps-test-prep-34b3b43-source.zip
phase10_34b3b43_source_package_sha256=97D7676B9C349877A8A51C971599C0C886616E9BBB6472749C0C695209BE5179
phase10_34b3b43_vps_package_contents=package_entries_5|source_entries_355|source_files_312|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_34b3b43_vps_package_verification=toolchain_3_12_13_ok|focused_184_passed|full_796_passed_1_skipped_1_warning|tooling_2_passed|checksums_matched|bindings_passed|shell_lf_no_bom
phase10_34b3b43_vps_package_evidence=research/amn2/phase-10-34b3b43-vps-package-prep-2026-07-11.md
phase10_34b3b43_vps_package_live_actions=false
phase10_34b3b43_vps_package_vps_overlay_status=smoke_pass_34b3b43_web_active
phase10_34b3b43_private_vps_upload_gate_review_status=approved-consumed-completed-pass
phase10_34b3b43_private_vps_upload_gate_review_result=checksum_bound_upload|preapply_tracked_source_snapshot|sqlite_backup|dual_write_gates_false|read_only_smoke|web_only_restart|automatic_rollback_scope|bot_stays_stopped
phase10_34b3b43_private_vps_upload_gate_review_evidence=research/amn2/phase-10-34b3b43-private-vps-source-overlay-upload-gate-review-2026-07-11.md
phase10_34b3b43_private_vps_upload_gate_review_live_actions=approved-and-completed
phase10_34b3b43_private_vps_upload_gate_exact_phrase=APPROVE_PHASE10_34B3B43_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_AND_READ_ONLY_SMOKE_WITH_ROLLBACK
phase10_34b3b43_vps_source_overlay_before=6f475e6
phase10_34b3b43_vps_source_overlay_after=34b3b43
phase10_34b3b43_vps_rollback_bundle=verified_private_source_snapshot_and_sqlite_backup
phase10_34b3b43_vps_rollback_bundle_path=/root/amn2-rollbacks/34b3b43-20260711T054507Z
phase10_34b3b43_vps_source_update_run_id=20260711T054627Z
phase10_34b3b43_vps_api_smoke_run_id=20260711T054705Z
phase10_34b3b43_vps_api_smoke_result=server_db_sync_passed|api_passed|auth_401_403_401|listener_passed|audit_passed
phase10_34b3b43_web_activation_status=passed-private-loopback
phase10_34b3b43_web_activation_runtime=systemd_active_amneziya_user|login_200|registry_unauth_303|listener_127_0_0_1_3030|public_listener_false
phase10_34b3b43_web_activation_dual_gate_state=vps_apply_safe|operator_device_create_safe
phase10_34b3b43_bot_runtime=inactive-disabled-nonpolling-diagnostic-pass
phase10_34b3b43_vps_activation_evidence=research/amn2/phase-10-34b3b43-vps-source-overlay-web-activation-2026-07-11.md
phase10_private_telegram_bot_runtime_gate_review_status=approved-consumed-nonpolling-diagnostic-pass-persistent-activation-stopped
phase10_private_telegram_bot_runtime_readiness=unit_loaded_template_match|inactive_disabled|identity_match|webhook_false|pending_0|dual_write_gates_safe
phase10_private_telegram_bot_runtime_risk=autostart_risk_resolved|controlled_polling_requires_separate_ttl_gate
phase10_private_telegram_bot_runtime_safe_baseline=users_6|orders_8|pending_orders_0|devices_8|admin_actions_43
phase10_private_telegram_bot_runtime_gate_review_live_actions=false
phase10_private_telegram_bot_runtime_gate_review_evidence=research/amn2/phase-10-private-telegram-bot-runtime-gate-review-2026-07-11.md
phase10_private_telegram_nonpolling_exact_phrase=APPROVE_PHASE10_PRIVATE_TELEGRAM_GETME_AND_BACKLOG_CHECK_NO_POLLING
phase10_private_telegram_nonpolling_diagnostic_status=completed-pass
phase10_private_telegram_nonpolling_diagnostic_result=getme_pass|getwebhookinfo_pass|identity_match|webhook_false|pending_0|db_counts_unchanged|no_polling
phase10_private_telegram_nonpolling_diagnostic_live_actions=approved_unit_disable_and_telegram_getme_getwebhookinfo_only
phase10_private_telegram_nonpolling_diagnostic_runtime=bot_inactive_disabled|bot_process_false|web_active_login_200|public_listener_false
phase10_private_telegram_nonpolling_diagnostic_evidence=research/amn2/phase-10-private-telegram-getme-backlog-check-2026-07-11.md
phase10_private_telegram_controlled_polling_status=hardening-completed-pushed-not-packaged-not-live
phase10_private_telegram_controlled_polling_gate_review_status=completed-stop-direct-runtime-approve-local-hardening
phase10_private_telegram_controlled_polling_gate_review_result=full_dispatcher_risk|start_mutates_production_db|outer_ttl_insufficient|transient_systemd_supported
phase10_private_telegram_controlled_polling_gate_review_preflight=overlay_34b3b43|bot_inactive_disabled|web_active_200|db_integrity_ok|systemd_255
phase10_private_telegram_controlled_polling_gate_review_tests=focused_pytest_12_passed
phase10_private_telegram_controlled_polling_gate_review_live_actions=read_only_vps_preflight_only|telegram_api_false|polling_false
phase10_private_telegram_controlled_polling_gate_review_evidence=research/amn2/phase-10-private-telegram-controlled-polling-ttl-gate-review-2026-07-11.md
phase10_private_telegram_single_admin_smoke_hardening_status=completed-tested-reviewed-pushed-local-only
phase10_private_telegram_single_admin_smoke_hardening_commit=4e44c5d
phase10_private_telegram_single_admin_smoke_hardening_result=configured_admin_only|clone_db_only|message_only|exact_start_only|unexpected_unacked|pre_post_backlog_zero|internal_ttl_120|sanitized_output
phase10_private_telegram_single_admin_smoke_hardening_tests=focused_14_passed|combined_24_passed|bot_settings_178_passed|full_810_passed_1_skipped_1_warning|python_3_12_13
phase10_private_telegram_single_admin_smoke_hardening_harness=tests_14_passed|product_and_docs_scope_passed
phase10_private_telegram_single_admin_smoke_hardening_live_actions=false
phase10_private_telegram_single_admin_smoke_hardening_vps_overlay=34b3b43_4e44c5d_not_uploaded
phase10_private_telegram_single_admin_smoke_hardening_evidence=research/amn2/phase-10-telegram-single-admin-transient-smoke-runner-hardening-2026-07-11.md
phase10_4e44c5d_vps_package_prep_status=completed-local-package-ready-not-vps-smoked
phase10_4e44c5d_vps_package=dist/amn2-vps-update-and-smoke-kit-4e44c5d.zip
phase10_4e44c5d_vps_package_sha256=28447A7385A24BC01221DED073FAE1B4C6E583BBD6824F64E4D2DF4D0B294F13
phase10_4e44c5d_source_package=dist/amn2-vps-update-and-smoke-kit-4e44c5d/amn2-codex-vps-test-prep-4e44c5d-source.zip
phase10_4e44c5d_source_package_sha256=4E34EB736775749467BDD5E0DA20758F46B8F10224871091C96778E960A040FA
phase10_4e44c5d_vps_package_contents=package_entries_5|source_entries_357|source_files_314|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_4e44c5d_vps_package_verification=python_3_12_13|focused_24_passed|full_810_passed_1_skipped_1_warning|tooling_2_passed|checksums_matched|content_matched|bindings_passed|shell_lf_no_bom|bash_syntax_passed
phase10_4e44c5d_vps_package_harness=tests_14_passed|package_product_and_docs_scope_passed
phase10_4e44c5d_vps_package_live_actions=false
phase10_4e44c5d_vps_package_vps_overlay_status=not_uploaded_current_34b3b43
phase10_4e44c5d_vps_package_evidence=research/amn2/phase-10-4e44c5d-vps-package-prep-2026-07-11.md
phase10_4e44c5d_private_vps_upload_gate_review_status=approved-conditional-awaiting-exact-live-phrase
phase10_4e44c5d_private_vps_upload_gate_review_result=checksum_bound_upload|web_stop_before_snapshot|tracked_source_snapshot|sqlite_backup|offline_apply|clone_db_api_smoke|production_db_unchanged|web_only_start|automatic_rollback_scope|bot_stays_disabled
phase10_4e44c5d_private_vps_upload_gate_review_preflight=overlay_34b3b43|web_active_200_private|bot_inactive_disabled|dual_write_gates_false|db_integrity_ok|disk_ok|rollback_root_ready|candidate_absent
phase10_4e44c5d_private_vps_upload_gate_review_harness=tests_14_passed|docs_only_review_scope_passed
phase10_4e44c5d_private_vps_upload_gate_review_live_actions=read_only_vps_preflight_only|upload_false|apply_false|restart_false|telegram_api_false
phase10_4e44c5d_private_vps_upload_gate_review_evidence=research/amn2/phase-10-4e44c5d-private-vps-source-overlay-upload-gate-review-2026-07-11.md
phase10_4e44c5d_private_vps_upload_gate_exact_phrase=APPROVE_PHASE10_4E44C5D_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_AND_CLONE_DB_API_WEB_SMOKE_WITH_ROLLBACK
phase10_android_tv_device8_preacceptance_status=closed-superseded-by-cross-client-pass
phase10_android_tv_device8_preacceptance_runtime=docker_amnezia_awg2_running|initial_peer_present|initial_endpoint_false|initial_handshake_false|initial_rx_0|initial_tx_0
phase10_android_tv_device8_initial_failure=official_amneziavpn_connecting_without_connected_state
phase10_android_tv_control_profile=device1_endpoint_true|handshake_age_90s|rx_positive|tx_positive
phase10_android_tv_control_comparison=official_client_android_tv_network_vps_dataplane_confirmed_healthy
phase10_android_tv_device8_root_cause=active_phase10_branch_omitted_187949b_android_compatible_awg_defaults
phase10_android_tv_device8_recovery_commit=60d8cc9
phase10_android_tv_device8_recovery_tests=scoped_87_passed_1_skipped_1_warning|full_811_passed_1_skipped_1_warning|diff_review_passed
phase10_android_tv_device8_recovery_result=known_working_endpoint_key_identity_peer_fields_preserved|11_awg_fields_corrected|no_peer_server_runtime_mutation
phase10_android_tv_device8_original_private_config=private-artifacts/phase10/android-tv-single/20260707T200605Z/Neobyatnaya-AMNZ-N-android-tv-01.conf
phase10_android_tv_device8_private_config=private-artifacts/phase10/android-tv-corrected/20260711T125600Z/Neobyatnaya-AMNZ-N-android-tv-01-compatible.conf
phase10_android_tv_device8_corrected_sha256=916B08317819CE4C147B39C91C513F6DCF8DB59A1850EEA0774BFDB91CA193BD
phase10_android_tv_device8_recovery_evidence=research/amn2/phase-10-android-tv-device8-compatible-config-recovery-2026-07-11.md
phase10_android_tv_device8_acceptance=passed_official_amneziavpn_standard_conf|endpoint_present|handshake_age_93s|rx_3382412|tx_134118669
phase10_ios_defaultvpn_acceptance=passed_standard_conf|handshake_age_9s|rx_4169240|tx_149555536
phase10_windows_11_amneziavpn_acceptance=passed_standard_conf|handshake_age_46s|rx_4478716|tx_153445786
phase10_cross_client_config=private-artifacts/phase10/cross-client-acceptance/20260711T134917Z/Neobyatnaya.NET.conf
phase10_cross_client_display_name=filename_stem_passed_android_tv_and_windows_11
phase10_native_vpn_json_status=import_pass_connect_failed_spinning_without_error_not_recommended
phase10_shared_owner_observation=android_tv_and_ios_overlap_worked|not_concurrency_scale_guarantee
phase10_android_tv_device8_next_step=COMPLETE_NO_REPEAT_CONNECTION_LOOP
phase10_device8_assignment_reconciliation=completed_owner_shared_existing_owner_admin_flag_synced
phase10_private_telegram_next_gate=START_PHASE10_E709746_VPS_PACKAGE_PREP_SLICE
phase10_telegram_admin_server_status_route_status=completed-code-tested-pushed-local-only
phase10_telegram_admin_server_status_route_base=1c7b5b2
phase10_telegram_admin_server_status_route_result=callback_registered|admin_authorized|typed_api_safe_allowlist|stored_health_only|operator_locale|count_only_safe_audit|surface_policy_bound
phase10_telegram_admin_server_status_route_test_status=red_import_errors|focused_135_passed|expanded_217_passed_1_warning|full_790_passed_1_skipped_1_warning
phase10_telegram_admin_server_status_route_harness=tests_12_passed|product_and_docs_scope_passed
phase10_telegram_admin_server_status_route_evidence=research/amn2/phase-10-telegram-admin-server-status-route-2026-07-10.md
phase10_telegram_admin_server_status_route_live_actions=false
phase10_telegram_admin_server_status_route_vps_overlay=6f475e6_4cf93f8_not_uploaded
phase10_telegram_admin_server_status_route_bot_runtime=not_started
phase10_telegram_admin_traffic_route_status=completed-code-tested-pushed-local-only
phase10_telegram_admin_traffic_route_base=e73343b
phase10_telegram_admin_traffic_route_result=callback_registered|admin_authorized|local_active_device_snapshots|operator_locale|count_only_safe_audit|surface_policy_bound
phase10_telegram_admin_traffic_route_test_status=red_import_error|focused_129_passed|expanded_228_passed|full_784_passed_1_skipped_1_warning
phase10_telegram_admin_traffic_route_harness=tests_12_passed|product_and_docs_scope_passed
phase10_telegram_admin_traffic_route_evidence=research/amn2/phase-10-telegram-admin-traffic-route-completion-2026-07-10.md
phase10_telegram_admin_traffic_route_live_actions=false
phase10_telegram_admin_traffic_route_vps_overlay=6f475e6_1c7b5b2_not_uploaded
phase10_telegram_admin_traffic_route_bot_runtime=not_started
phase10_telegram_operator_read_only_status_status=completed-code-tested-pushed-local-only
phase10_telegram_operator_read_only_status_base=6f475e6
phase10_telegram_operator_read_only_status_result=authorized_aggregate_local_db_status|admin_locale|safe_audit|actual_vps_write_gate|no_ssh|no_secret_fields
phase10_telegram_operator_read_only_status_test_status=red_import_error|scoped_116_passed|expanded_197_passed|full_780_passed_1_skipped_1_warning
phase10_telegram_operator_read_only_status_harness=tests_12_passed|post_commit_amn3_product_diff_guard_expected_docs_only
phase10_telegram_operator_read_only_status_evidence=research/amn2/phase-10-telegram-operator-read-only-status-2026-07-10.md
phase10_telegram_operator_read_only_status_live_actions=false
phase10_telegram_operator_read_only_status_vps_overlay=6f475e6_e73343b_not_uploaded
phase10_telegram_operator_read_only_status_bot_runtime=not_started
phase10_integration_api_key_registry_status=completed-code-tested-pushed-local-gate
phase10_integration_api_key_registry_base=3ed20ab
phase10_integration_api_key_registry_result=typed_integration_identity|explicit_purpose|scoped_expiring_hash_only_credentials|private_issue_rotate_revoke|safe_audit|legacy_migration
phase10_integration_api_key_registry_test_status=red_import_error|scoped_73_passed_1_warning|expanded_388_passed_1_warning|full_774_passed_1_skipped_1_warning
phase10_integration_api_key_registry_evidence=research/amn2/phase-10-integration-api-key-registry-2026-07-10.md
phase10_integration_api_key_registry_live_actions=false
phase10_integration_api_key_registry_vps_overlay=smoke_pass_6f475e6_web_active
phase10_client_display_name_root_cause_status=completed-product-policy-pushed
phase10_client_display_name_root_cause_commit=d2d3099
phase10_client_display_name_root_cause_push_status=done
phase10_client_display_name_root_cause_test_status=scoped_pytest_14_passed
phase10_client_display_name_root_cause_result=amneziavpn_client_generated_server_n_standalone_awg_filename_stem
phase10_config_filename_canonicalization_status=completed-product-code-pushed
phase10_config_filename_canonicalization_commit=26bb22e
phase10_config_filename_canonicalization_push_status=done
phase10_config_filename_canonicalization_test_status=scoped_pytest_18_passed
phase10_config_filename_canonicalization_result=neobyatnayanet_conf_filename_for_standalone_awg_android_windows
phase10_rebase_client_compatibility_branch_status=completed-rebased-and-pushed
phase10_rebase_client_compatibility_branch_base=amn2/codex-vps-test-prep@471bca8
phase10_rebase_client_compatibility_branch_commits=d2d3099,26bb22e
phase10_rebase_client_compatibility_branch_test_status=scoped_pytest_22_passed
phase10_client_compatibility_broad_regression_status=completed-product-contract-fix-pushed
phase10_client_compatibility_broad_regression_commit=d61c6be
phase10_client_compatibility_broad_regression_test_status=scoped_pytest_130_passed
phase10_client_compatibility_direct_merge_status=completed-fast-forward-merged-and-pushed
phase10_client_compatibility_direct_merge_target=amn2/codex-vps-test-prep
phase10_client_compatibility_direct_merge_head=d61c6be
phase10_client_compatibility_direct_merge_test_status=post_merge_scoped_pytest_130_passed
phase10_fresh_installer_recovery_status=completed-fast-forward-merged-and-pushed
phase10_fresh_installer_recovery_branch=codex/dirty-main-amn2-fresh-installer-recovery
phase10_fresh_installer_recovery_head=4326cae
phase10_fresh_installer_recovery_target=amn2/codex-vps-test-prep
phase10_fresh_installer_recovery_test_status=post_merge_scoped_pytest_164_passed
phase10_fresh_installer_current_source_head_preflight_status=completed-local-code
phase10_fresh_installer_current_source_head_preflight_commit=ad30363
phase10_fresh_installer_current_source_head_preflight_push_status=done
phase10_fresh_installer_current_source_head_preflight_worktree=C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-recovery-rebase-probe
phase10_fresh_installer_current_source_head_preflight_result=current_source_head_reported_separately_from_prebuilt_artifact_head
phase10_fresh_installer_current_source_head_preflight_harness=next_command_pass|product_diff_pass
phase10_fresh_installer_current_source_head_preflight_test_status=scoped_pytest_38_passed|progress_harness_pytest_6_passed
phase10_fresh_installer_current_source_head_preflight_diff_status=git_diff_check_passed
phase10_web_integration_status_fresh_installer_source_head_visibility_status=completed-local-code
phase10_web_integration_status_fresh_installer_source_head_visibility_commit=ced54a5
phase10_web_integration_status_fresh_installer_source_head_visibility_push_status=done
phase10_web_integration_status_fresh_installer_source_head_visibility_result=integration_status_page_shows_current_source_head_prebuilt_artifact_head_and_package_status
phase10_web_integration_status_fresh_installer_source_head_visibility_harness=next_command_pass|product_diff_pass
phase10_web_integration_status_fresh_installer_source_head_visibility_test_status=scoped_pytest_38_passed
phase10_p6_i007_interactive_cli_output_status=completed-local-code
phase10_p6_i007_interactive_cli_output_commit=774631d
phase10_p6_i007_interactive_cli_output_push_status=done
phase10_p6_i007_interactive_cli_output_result=fresh_install_wizard_collects_defaults_on_eof_without_failing_and_outputs_safe_local_plan
phase10_p6_i007_interactive_cli_output_harness=next_command_pass|product_diff_pass
phase10_p6_i007_interactive_cli_output_test_status=scoped_pytest_8_passed
phase10_progress_harness_clean_tree_closure_signal_status=completed-local-code
phase10_progress_harness_clean_tree_closure_signal_result=require_product_diff_clean_tree_output_explicitly_marks_valid_next_command_as_not_closure_evidence
phase10_progress_harness_clean_tree_closure_signal_harness=product_diff_pass
phase10_progress_harness_clean_tree_closure_signal_test_status=progress_harness_pytest_7_passed
phase10_progress_harness_concrete_slice_guard_status=completed-local-code
phase10_progress_harness_concrete_slice_guard_result=require_product_step_rejects_select_next_start_selected_run_scoped_placeholder_without_concrete_slice
phase10_progress_harness_concrete_slice_guard_harness=placeholder_next_command_fail|concrete_slice_next_command_pass|product_diff_pass
phase10_progress_harness_concrete_slice_guard_test_status=progress_harness_pytest_8_passed
phase10_progress_harness_command_hints_status=completed-local-code
phase10_progress_harness_command_hints_result=placeholder_rejection_includes_copyable_concrete_slice_hint
phase10_progress_harness_command_hints_harness=placeholder_next_command_fail_with_hint|concrete_command_hints_slice_pass|product_diff_pass
phase10_progress_harness_command_hints_test_status=progress_harness_pytest_9_passed
phase10_progress_harness_scoped_tests_guard_status=completed-local-code
phase10_progress_harness_scoped_tests_guard_result=require_scoped_tests_for_start_slice_commands
phase10_progress_harness_scoped_tests_guard_test_status=progress_harness_pytest_10_passed
phase10_progress_harness_known_slice_registry_status=completed-local-code
phase10_progress_harness_known_slice_registry_commit=1e0d73d
phase10_progress_harness_known_slice_registry_push_status=done
phase10_progress_harness_known_slice_registry_result=require_known_registry_for_START_PHASE10_slice_commands
phase10_progress_harness_known_slice_registry_harness=next_command_pass|product_diff_pass
phase10_progress_harness_known_slice_registry_test_status=progress_harness_pytest_12_passed
phase10_amn2_4326cae_vps_package_prep_status=completed-read-only-vps-smoke-pass
phase10_amn2_4326cae_vps_package_prep_commit=69323ba
phase10_amn2_4326cae_vps_package_prep_amntwo_head=4326cae
phase10_amn2_4326cae_vps_package_prep_package=dist/amn2-vps-update-and-smoke-kit-4326cae.zip
phase10_amn2_4326cae_vps_package_prep_package_sha256=FEFD9D4AE91764AB9649284E26F0F303A2F43BAECD8A511B0E492E8D9315D2F1
phase10_amn2_4326cae_vps_package_prep_source_zip=dist/amn2-vps-update-and-smoke-kit-4326cae/amn2-codex-vps-test-prep-4326cae-source.zip
phase10_amn2_4326cae_vps_package_prep_source_sha256=7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
phase10_amn2_4326cae_vps_package_prep_verification=amn2_toolchain_ok|amn2_scoped_pytest_8_passed_1_warning|package_hygiene_passed|package_extract_passed|amn3_package_tests_4_passed|diff_check_passed
phase10_amn2_4326cae_vps_package_prep_live_upload_status=approved-and-completed-read-only
phase10_amn2_4326cae_vps_package_prep_vps_gate_approval=APPROVE_READ_ONLY_VPS_SOURCE_OVERLAY_UPLOAD_GATE_FOR_AMN2_4326CAE
phase10_amn2_4326cae_vps_package_prep_source_overlay_before=187949bffb927a0a6d6c1f260fc0bb9ebb972447
phase10_amn2_4326cae_vps_package_prep_source_overlay_after=4326cae
phase10_amn2_4326cae_vps_package_prep_source_update_run_id=20260707T195143Z
phase10_amn2_4326cae_vps_package_prep_api_smoke_run_id=20260707T195217Z
phase10_amn2_4326cae_vps_package_prep_api_smoke_status=read_only_vps_smoke_pass_checked_routes_6_listener_audit_passed
phase10_amn2_4326cae_vps_package_prep_safe_evidence=research/amn2/phase-10-4326cae-read-only-vps-source-overlay-smoke-2026-07-07.md
phase10_amn2_4326cae_vps_package_prep_vps_gate_next=SELECT_NEXT_PHASE10_PRODUCT_SLICE_AFTER_AMN2_4326CAE_VPS_SMOKE_PASS
phase10_android_tv_single_peer_config_status=server-side-prepared-awaiting-device-acceptance
phase10_android_tv_single_peer_config_gate=CREATE_ONE_ANDROID_TV_PEER_AND_GENERATE_LOCAL_CONFIG_FOR_EXISTING_AMN2_VPS
phase10_android_tv_single_peer_config_run_id=20260707T200605Z
phase10_android_tv_single_peer_config_device_id=8
phase10_android_tv_single_peer_config_device_name=Neobyatnaya-AMNZ-N-android-tv-01
phase10_android_tv_single_peer_config_vpn_ip=10.8.0.13
phase10_android_tv_single_peer_config_version=amneziawg_v2
phase10_android_tv_single_peer_config_material_status=available
phase10_android_tv_single_peer_config_peer_apply_status=passed
phase10_android_tv_single_peer_config_docker_restart_status=passed
phase10_android_tv_single_peer_config_working_proven=false
phase10_android_tv_single_peer_config_handshake_seen=false
phase10_android_tv_single_peer_config_rx_bytes=0
phase10_android_tv_single_peer_config_tx_bytes=0
phase10_android_tv_single_peer_config_owner_selection=existing_active_user
phase10_android_tv_single_peer_config_owner_is_admin=false
phase10_android_tv_single_peer_config_owner_decision=leave_current_provisional_until_device_acceptance
phase10_android_tv_single_peer_config_owner_mutation_status=not_performed
phase10_android_tv_single_peer_config_owner_recheck_trigger=android_tv_import_connect_acceptance
phase10_android_tv_single_peer_config_linked_order_count=0
phase10_android_tv_single_peer_config_admin_action_count=0
phase10_android_tv_single_peer_config_supported_access_service_path_used=false
phase10_android_tv_single_peer_config_gate_scope_consumed=true
phase10_android_tv_single_peer_config_global_peer_creation_after=false
phase10_android_tv_single_peer_config_global_config_generation_after=false
phase10_android_tv_single_peer_config_global_config_delivery_after=false
phase10_android_tv_single_peer_config_local_acl_status=hardened_owner_system_administrators_only
phase10_android_tv_single_peer_config_remote_permissions_status=private_files_0600_gate_script_0700
phase10_android_tv_single_peer_config_local_path=private-artifacts/phase10/android-tv-single/20260707T200605Z/Neobyatnaya-AMNZ-N-android-tv-01.conf
phase10_android_tv_single_peer_config_safe_evidence=research/amn2/phase-10-android-tv-single-peer-config-2026-07-07.md
phase10_5_6_sol_audit_packet=research/amn2/phase-10-5-6-sol-audit-packet-2026-07-10.md
phase10_operator_single_device_create_hardening_status=completed-code-merged-and-pushed
phase10_operator_single_device_create_hardening_base=4326cae
phase10_operator_single_device_create_hardening_feature_branch=codex/phase10-operator-single-device-create
phase10_operator_single_device_create_hardening_commit=e7f6246
phase10_operator_single_device_create_hardening_target=amn2/codex-vps-test-prep
phase10_operator_single_device_create_hardening_result=explicit_active_owner|authorized_admin|common_access_service|local_or_remote_execution|atomic_posix_0600_artifact|safe_partial_failure_reconciliation
phase10_operator_single_device_create_hardening_test_status=focused_31_passed_1_skipped|expanded_90_passed_1_skipped|full_766_passed_1_skipped_1_warning|post_merge_31_passed_1_skipped
phase10_operator_single_device_create_hardening_hygiene=toolchain_ok|file_hygiene_3_passed|diff_check_passed|secret_safe_cli_dry_run_passed
phase10_operator_single_device_create_hardening_evidence=research/amn2/phase-10-operator-single-device-create-hardening-2026-07-10.md
phase10_operator_single_device_create_hardening_live_actions=false
phase10_operator_single_device_create_hardening_vps_overlay_status=current_4326cae_e7f6246_not_uploaded
phase10_e7f6246_vps_package_prep_status=completed-local-package-ready-not-vps-smoked
phase10_e7f6246_vps_package=dist/amn2-vps-update-and-smoke-kit-e7f6246.zip
phase10_e7f6246_vps_package_sha256=17988115CEBD7CA5D924300506259CE4DB7161DBB1980D248892E4A7CF7DA72E
phase10_e7f6246_source_package=dist/amn2-vps-update-and-smoke-kit-e7f6246/amn2-codex-vps-test-prep-e7f6246-source.zip
phase10_e7f6246_source_package_sha256=FE980BDBC209ED339B33231BCABD42000E2DA6910791DAA8ABA85620A099B0EE
phase10_e7f6246_vps_package_contents=package_entries_5|source_files_305|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_e7f6246_vps_package_verification=toolchain_ok|focused_31_passed_1_skipped|full_766_passed_1_skipped_1_warning|checksums_matched|test_extract_passed|bindings_passed|shell_lf_no_bom
phase10_e7f6246_vps_package_evidence=research/amn2/phase-10-e7f6246-vps-package-prep-2026-07-10.md
phase10_e7f6246_vps_package_live_actions=false
phase10_e7f6246_vps_package_vps_overlay_status=smoke_pass_e7f6246
phase10_e7f6246_vps_source_overlay_smoke_status=read-only-vps-smoke-pass
phase10_e7f6246_vps_source_overlay_before=4326cae
phase10_e7f6246_vps_source_overlay_after=e7f6246
phase10_e7f6246_vps_source_update_run_id=20260710T072516Z
phase10_e7f6246_vps_api_smoke_run_id=20260710T072545Z
phase10_e7f6246_vps_smoke_result=server_db_sync_passed|api_passed|auth_401_403_401|listener_passed|audit_passed|operator_create_cli_available
phase10_e7f6246_vps_smoke_apply_state=false_or_unset
phase10_e7f6246_vps_smoke_evidence=research/amn2/phase-10-e7f6246-read-only-vps-source-overlay-smoke-2026-07-10.md
phase10_operator_device_create_web_ui_status=completed-vps-activated-private-loopback
phase10_operator_device_create_web_ui_base=e7f6246
phase10_operator_device_create_web_ui_commit=466e0bc
phase10_operator_device_create_web_ui_policy_test_followup_commit=3ed20ab
phase10_operator_device_create_web_ui_target=amn2/codex-vps-test-prep
phase10_operator_device_create_web_ui_result=private_user_detail_form|dry_run_no_side_effects|common_access_service|dual_default_false_apply_gate|csrf_and_admin_actor|safe_artifact_metadata|partial_failure_fixed_409|surface_policy_bound
phase10_operator_device_create_web_ui_test_status=red_5_failed|focused_5_passed|expanded_99_passed_1_skipped_1_warning|security_38_passed_1_warning|full_772_passed_1_skipped_1_warning|final_41_passed_1_warning
phase10_operator_device_create_web_ui_hygiene=toolchain_ok|diff_check_passed|cached_check_passed|file_hygiene_passed|config_payload_html_false
phase10_operator_device_create_web_ui_evidence=research/amn2/phase-10-operator-device-create-web-ui-2026-07-10.md
phase10_operator_device_create_web_ui_live_actions=false
phase10_operator_device_create_web_ui_vps_overlay_status=smoke_pass_3ed20ab_web_active
phase10_3ed20ab_vps_package_prep_status=completed-local-package-ready-not-vps-smoked
phase10_3ed20ab_vps_package=dist/amn2-vps-update-and-smoke-kit-3ed20ab.zip
phase10_3ed20ab_vps_package_sha256=8B16853A7BCD9DC012A851C1174A9CB743A2A531369B96F7238BC6719B0D80D8
phase10_3ed20ab_source_package=dist/amn2-vps-update-and-smoke-kit-3ed20ab/amn2-codex-vps-test-prep-3ed20ab-source.zip
phase10_3ed20ab_source_package_sha256=F2F6AC74FD9311E72B9098DD2472841DFB8CAE804D5901A3DDD0F38CB3DE1066
phase10_3ed20ab_vps_package_contents=package_entries_5|source_entries_349|source_files_306|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_3ed20ab_vps_package_verification=toolchain_ok|focused_41_passed_1_warning|full_772_passed_1_skipped_1_warning|checksums_matched|test_extract_passed|bindings_passed|dual_gate_false|shell_lf_no_bom
phase10_3ed20ab_vps_package_evidence=research/amn2/phase-10-3ed20ab-vps-package-prep-2026-07-10.md
phase10_3ed20ab_vps_package_live_actions=false
phase10_3ed20ab_vps_package_vps_overlay_status=smoke_pass_3ed20ab
phase10_3ed20ab_vps_source_overlay_smoke_status=read-only-vps-smoke-pass
phase10_3ed20ab_vps_source_overlay_before=e7f6246
phase10_3ed20ab_vps_source_overlay_after=3ed20ab
phase10_3ed20ab_vps_source_update_run_id=20260710T081550Z
phase10_3ed20ab_vps_api_smoke_run_id=20260710T081622Z
phase10_3ed20ab_vps_api_smoke_result=server_db_sync_passed|api_passed|auth_401_403_401|listener_passed|audit_passed
phase10_3ed20ab_web_activation_status=passed-private-loopback
phase10_3ed20ab_web_activation_permission_repair=targeted_group_access_source_venv_env_servers|runtime_dirs_owned_by_amneziya
phase10_3ed20ab_web_activation_stale_process=old_root_manual_process_graceful_term
phase10_3ed20ab_web_activation_runtime=systemd_active_amneziya_user|login_200|operator_route_unauth_303|route_mounted_yes|listener_127_0_0_1_3030
phase10_3ed20ab_web_activation_dual_gate_state=vps_apply_safe_or_unset|operator_device_create_safe_or_unset
phase10_3ed20ab_web_activation_local_tunnel=active_local_127_0_0_1_3030_login_200
phase10_3ed20ab_vps_activation_evidence=research/amn2/phase-10-3ed20ab-vps-source-overlay-web-activation-2026-07-10.md
phase10_6f475e6_vps_package_prep_status=completed-live-smoke-pass
phase10_6f475e6_vps_package=dist/amn2-vps-update-and-smoke-kit-6f475e6.zip
phase10_6f475e6_vps_package_sha256=0B67CD3AB4ABFC2F74772B7D3F247D9730136DA5AB571E890F3A77D2873939BC
phase10_6f475e6_source_package=dist/amn2-vps-update-and-smoke-kit-6f475e6/amn2-codex-vps-test-prep-6f475e6-source.zip
phase10_6f475e6_source_package_sha256=BEDFDBE04CA40DA21A51B1ACAB4C0C21BD7F5EC408A77D1223664EAAAF673FFF
phase10_6f475e6_vps_package_contents=package_entries_5|source_entries_349|source_files_306|source_dirs_43|required_missing_0|forbidden_entries_0
phase10_6f475e6_vps_package_verification=toolchain_ok|focused_73_passed_1_warning|full_774_passed_1_skipped_1_warning|tooling_2_passed|checksums_matched|bindings_passed|dual_gate_false|shell_lf_no_bom
phase10_6f475e6_vps_package_evidence=research/amn2/phase-10-6f475e6-vps-package-prep-2026-07-10.md
phase10_6f475e6_vps_package_live_actions=false
phase10_6f475e6_vps_package_vps_overlay_status=smoke_pass_6f475e6
phase10_6f475e6_vps_source_overlay_before=3ed20ab
phase10_6f475e6_vps_source_overlay_after=6f475e6
phase10_6f475e6_vps_source_update_run_id=20260710T172523Z
phase10_6f475e6_vps_api_smoke_run_id=20260710T172557Z
phase10_6f475e6_vps_api_smoke_result=server_db_sync_passed|api_passed|auth_401_403_401|listener_passed|audit_passed
phase10_6f475e6_web_activation_status=passed-private-loopback
phase10_6f475e6_web_activation_runtime=systemd_active_amneziya_user|login_200|registry_unauth_303|registry_route_true|rotate_route_true|integration_columns_true|listener_127_0_0_1_3030
phase10_6f475e6_web_activation_dual_gate_state=vps_apply_safe_or_unset|operator_device_create_safe_or_unset
phase10_6f475e6_web_activation_local_tunnel=active_local_127_0_0_1_3030_login_200
phase10_6f475e6_vps_activation_evidence=research/amn2/phase-10-6f475e6-vps-source-overlay-web-activation-2026-07-10.md
phase10_android_tv_import_connect_status=pending_physical_device
phase10_next_product_step=WAIT_FOR_PHASE10_PRIVATE_TELEGRAM_GETME_AND_BACKLOG_CHECK_EXACT_APPROVAL
phase10_next_product_reason=runtime_readiness_passed_but_persistent_activation_is_stopped_until_nonpolling_getme_webhook_and_pending_count_diagnostic_proves_a_safe_empty_backlog
phase10_weekly_upstream_scan_2026_07_10_status=completed_read_only
phase10_weekly_upstream_scan_2026_07_10_kyoresuas=96a1f54_unchanged_typed_api_taxonomy_signal
phase10_weekly_upstream_scan_2026_07_10_prvtpro=dd8bda3_v1.5.0_new_release_api_tokens_admin_bot_multi_instance_backup_migration_nginx_warp_signals
phase10_weekly_upstream_scan_2026_07_10_accept=integration_registry|telegram_operator_candidate|multi_instance_ipam_candidate|backup_migration_preflight_candidate
phase10_weekly_upstream_scan_2026_07_10_reject=gpl_code_templates_managers|admin_equivalent_bearer|public_tunnels|raw_config_editor|live_mutations
phase10_weekly_automation_handoff_2026_07_05_status=completed
phase10_weekly_automation_handoff_2026_07_05_items=prvtpro-weekly-upstream-refresh|weekly-kyoresuas-upstream-refresh|amnezia-weekly-upstream-refresh
phase10_weekly_automation_handoff_2026_07_05_result=all_three_processed_stop_lines_remain_closed
phase10_weekly_automation_next_scheduled_run=next_week_regular_schedule_week_of_2026_07_12
phase10_weekly_upstream_scan_2026_07_05_status=completed_read_only
phase10_weekly_upstream_scan_2026_07_05_result=no_actionable_product_delta
phase10_weekly_upstream_scan_2026_07_05_prvtpro=v1.4.4_still_latest_carry_forward
phase10_weekly_upstream_scan_2026_07_05_kyoresuas=repo_alive_api_taxonomy_signal_no_new_phase10_trigger
phase10_weekly_upstream_scan_2026_07_05_amnezia_client=4.8.19.0_still_latest
phase10_weekly_upstream_scan_2026_07_05_amneziawg_android=2.0.1_still_latest_awg2_signal_only
phase10_forbidden_loop_next_step=CONFIRM_HOLD_STATE|READY_FOR_OPERATOR_NEXT_DOCS_REQUEST|AWAIT_OPERATOR_EXACT_CMD
phase9_entry_decision_status=completed
helper_hardening_status=completed-docs-only
no_long_ssh_pattern=status=standardized
phase9_latest_known_pre_sync_commit=5bcbbc4
phase8_to_phase9_handoff_doc=docs/AMN2_PHASE_8_FINAL_HANDOFF_TO_PHASE_9_NEW_CHAT_SYNC.ru.md
next_chat_handoff=docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md
next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
selected_next_track=generator-code readiness / private self-config execution package prep
windows_filename_basename_implementation_readiness_review=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW.ru.md
windows_filename_basename_implementation_readiness_runbook=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md
windows_filename_basename_implementation_readiness_result_template=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md
windows_filename_basename_readiness_status=APPROVED_FOR_DOCS_AND_READ_ONLY_READINESS
windows_filename_basename_readonly_scope=read-only_inventory
windows_filename_basename_inventory_found_generator_code_repo=true
windows_filename_basename_candidate_repo=worktrees/amn2-public-config-delivery-policy-contract
windows_filename_basename_candidate_branch=codex/public-config-delivery-policy-contract
windows_filename_basename_candidate_path=worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py
windows_filename_basename_candidate_current_filename=Neobyatnaya-AMNZ-N.conf
windows_filename_basename_local_implementation_status=completed-local-code
windows_filename_basename_implementation_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
windows_filename_basename_implementation_gate_decision=APPROVED_WITH_TEST_ENV_LIMITATION
windows_filename_basename_local_implementation_test_status=pushed-with-runtime-export-guard-scoped-tests
windows_filename_basename_local_implementation_commit=3a6da8f
runtime_config_path_manager_export_guard_status=completed-local-code
runtime_config_path_manager_export_guard_commit=990a376
runtime_config_path_manager_export_guard_branch=codex/public-config-delivery-policy-contract
runtime_config_path_manager_export_guard_push_status=done
runtime_config_path_manager_export_guard_test_status=scoped_pytest_7_passed
runtime_config_path_manager_export_guard_contract=runtime_config_path_missing_without_raw_path
runtime_config_path_manager_export_guard_safe_metadata=runtime_config_path_status_only
xray_runtime_validation_snapshot_status=completed-local-code
xray_runtime_validation_snapshot_commit=fdc431d
xray_runtime_validation_snapshot_branch=codex/public-config-delivery-policy-contract
xray_runtime_validation_snapshot_push_status=done
xray_runtime_validation_snapshot_test_status=scoped_pytest_14_passed
xray_runtime_validation_snapshot_runtime_type=xray_docker
xray_runtime_validation_snapshot_capabilities=detect,status,validation
xray_runtime_validation_snapshot_live_actions=false
server_config_numeric_range_validation_status=completed-local-code
server_config_numeric_range_validation_commit=5b1d34a
server_config_numeric_range_validation_branch=codex/public-config-delivery-policy-contract
server_config_numeric_range_validation_push_status=done
server_config_numeric_range_validation_test_status=scoped_pytest_19_passed
server_config_numeric_range_validation_fields=ssh.port|vpn.port|vpn.max_devices
server_config_numeric_range_validation_live_actions=false
server_config_host_path_validation_status=completed-local-code
server_config_host_path_validation_commit=876ce32
server_config_host_path_validation_branch=codex/public-config-delivery-policy-contract
server_config_host_path_validation_push_status=done
server_config_host_path_validation_test_status=scoped_pytest_24_passed
server_config_host_path_validation_fields=ssh.host|vpn.endpoint_host|runtime.config_path
server_config_host_path_validation_live_actions=false
server_config_network_cidr_validation_status=completed-local-code
server_config_network_cidr_validation_commit=6e0bbe2
server_config_network_cidr_validation_branch=codex/public-config-delivery-policy-contract
server_config_network_cidr_validation_push_status=done
server_config_network_cidr_validation_test_status=scoped_pytest_28_passed
server_config_network_cidr_validation_fields=vpn.network_cidr|vpn.server_address|vpn.dns|vpn.allowed_ips
server_config_network_cidr_validation_live_actions=false
server_config_identifier_validation_status=completed-local-code
server_config_identifier_validation_commit=0129fc9
server_config_identifier_validation_branch=codex/public-config-delivery-policy-contract
server_config_identifier_validation_push_status=done
server_config_identifier_validation_test_status=scoped_pytest_33_passed
server_config_identifier_validation_fields=server.name|server.location|vpn.interface|runtime.service_name|runtime.container_name
server_config_identifier_validation_live_actions=false
server_config_unique_server_name_status=completed-local-code
server_config_unique_server_name_commit=d1c2bc3
server_config_unique_server_name_branch=codex/public-config-delivery-policy-contract
server_config_unique_server_name_push_status=done
server_config_unique_server_name_test_status=scoped_pytest_34_passed
server_config_unique_server_name_contract=duplicate_server_name_rejected_before_select_server
server_config_unique_server_name_live_actions=false
server_config_enum_validation_status=completed-local-code
server_config_enum_validation_commit=c7e5dbb
server_config_enum_validation_branch=codex/public-config-delivery-policy-contract
server_config_enum_validation_push_status=done
server_config_enum_validation_test_status=scoped_pytest_37_passed
server_config_enum_validation_fields=ssh.auth.type|firewall.provider|runtime.type
server_config_enum_validation_live_actions=false
config_delivery_template_unknown_placeholder_guard_status=completed-local-code
config_delivery_template_unknown_placeholder_guard_commit=eeef841
config_delivery_template_unknown_placeholder_guard_branch=codex/public-config-delivery-policy-contract
config_delivery_template_unknown_placeholder_guard_push_status=done
config_delivery_template_unknown_placeholder_guard_test_status=scoped_pytest_28_passed
config_delivery_template_unknown_placeholder_guard_contract=unknown_delivery_placeholder_rejected_before_package_build
config_delivery_template_unknown_placeholder_guard_live_actions=false
config_delivery_template_empty_message_guard_status=completed-local-code
config_delivery_template_empty_message_guard_commit=a674db2
config_delivery_template_empty_message_guard_branch=codex/public-config-delivery-policy-contract
config_delivery_template_empty_message_guard_push_status=done
config_delivery_template_empty_message_guard_test_status=scoped_pytest_29_passed
config_delivery_template_empty_message_guard_contract=empty_delivery_message_rejected_before_package_build
config_delivery_template_empty_message_guard_live_actions=false
config_template_override_empty_config_guard_status=completed-local-code
config_template_override_empty_config_guard_commit=ac298c2
config_template_override_empty_config_guard_branch=codex/public-config-delivery-policy-contract
config_template_override_empty_config_guard_push_status=done
config_template_override_empty_config_guard_test_status=scoped_pytest_19_passed
config_template_override_empty_config_guard_contract=empty_client_config_rejected_before_delivery_package_build
config_template_override_empty_config_guard_live_actions=false
config_share_token_atomic_redeem_status=completed-local-code
config_share_token_atomic_redeem_commit=62d01d9
config_share_token_atomic_redeem_branch=codex/public-config-delivery-policy-contract
config_share_token_atomic_redeem_push_status=done
config_share_token_atomic_redeem_test_status=scoped_pytest_40_passed
config_share_token_atomic_redeem_contract=hash_only_expiry_checked_one_time_atomic_download_count_increment
config_share_token_atomic_redeem_live_actions=false
config_share_redeem_decision_adapter_status=completed-local-code
config_share_redeem_decision_adapter_commit=9555f4c
config_share_redeem_decision_adapter_branch=codex/public-config-delivery-policy-contract
config_share_redeem_decision_adapter_push_status=done
config_share_redeem_decision_adapter_test_status=scoped_pytest_43_passed
config_share_redeem_decision_adapter_contract=hash_only_lookup_policy_decision_then_atomic_redeem_without_consuming_invalid_requests
config_share_redeem_decision_adapter_live_actions=false
config_share_redeem_db_row_status_join_status=completed-local-code
config_share_redeem_db_row_status_join_commit=548618a
config_share_redeem_db_row_status_join_branch=codex/public-config-delivery-policy-contract
config_share_redeem_db_row_status_join_push_status=done
config_share_redeem_db_row_status_join_test_status=scoped_pytest_69_passed
config_share_redeem_db_row_status_join_contract=requested_device_auth_lookup_includes_db_device_server_status_before_atomic_redeem
config_share_redeem_db_row_status_join_live_actions=false
config_share_redeem_audit_event_no_payload_logging_status=completed-local-code
config_share_redeem_audit_event_no_payload_logging_commit=83d8331
config_share_redeem_audit_event_no_payload_logging_branch=codex/public-config-delivery-policy-contract
config_share_redeem_audit_event_no_payload_logging_push_status=done
config_share_redeem_audit_event_no_payload_logging_test_status=scoped_pytest_72_passed
config_share_redeem_audit_event_no_payload_logging_contract=allowed_denied_redeem_audit_events_use_safe_metadata_without_token_hash_or_config_payload
config_share_redeem_audit_event_no_payload_logging_live_actions=false
config_share_redeem_rate_limit_policy_boundary_status=completed-local-code
config_share_redeem_rate_limit_policy_boundary_commit=56e49ff
config_share_redeem_rate_limit_policy_boundary_branch=codex/public-config-delivery-policy-contract
config_share_redeem_rate_limit_policy_boundary_push_status=done
config_share_redeem_rate_limit_policy_boundary_test_status=scoped_pytest_75_passed
config_share_redeem_rate_limit_policy_boundary_contract=pre_token_lookup_rate_limit_boundary_records_safe_attempts_without_token_hash_or_config_payload
config_share_redeem_rate_limit_policy_boundary_live_actions=false
config_share_redeem_rate_limit_repository_persistence_status=completed-local-code
config_share_redeem_rate_limit_repository_persistence_commit=b8fb466
config_share_redeem_rate_limit_repository_persistence_branch=codex/public-config-delivery-policy-contract
config_share_redeem_rate_limit_repository_persistence_push_status=done
config_share_redeem_rate_limit_repository_persistence_test_status=scoped_pytest_78_passed
config_share_redeem_rate_limit_repository_persistence_contract=sqlite_scope_attempts_denied_window_blocks_without_token_hash_or_config_payload
config_share_redeem_rate_limit_repository_persistence_live_actions=false
config_share_redeem_public_route_block_contract_status=completed-local-code
config_share_redeem_public_route_block_contract_commit=3ad001f
config_share_redeem_public_route_block_contract_branch=codex/public-config-delivery-policy-contract
config_share_redeem_public_route_block_contract_push_status=done
config_share_redeem_public_route_block_contract_test_status=scoped_pytest_92_passed
config_share_redeem_public_route_block_contract_contract=public_token_config_share_download_policy_remains_blocked_future_and_unmounted
config_share_redeem_public_route_block_contract_live_actions=false
config_share_token_backup_redaction_contract_status=completed-local-code
config_share_token_backup_redaction_contract_commit=5aecfed
config_share_token_backup_redaction_contract_branch=codex/public-config-delivery-policy-contract
config_share_token_backup_redaction_contract_push_status=done
config_share_token_backup_redaction_contract_test_status=scoped_pytest_101_passed
config_share_token_backup_redaction_contract_contract=backup_manifest_excludes_usable_share_hashes_create_restore_block_usable_hashes_without_dangerous_mode
config_share_token_backup_redaction_contract_live_actions=false
config_share_restore_dangerous_mode_gate_contract_status=completed-local-code
config_share_restore_dangerous_mode_gate_contract_commit=ca4aa7c
config_share_restore_dangerous_mode_gate_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_dangerous_mode_gate_contract_push_status=done
config_share_restore_dangerous_mode_gate_contract_test_status=scoped_pytest_104_passed
config_share_restore_dangerous_mode_gate_contract_contract=restore_usable_share_hashes_dangerous_mode_gate_closed_not_implemented_cli_flag_absent
config_share_restore_dangerous_mode_gate_contract_live_actions=false
config_share_restore_history_contract_status=completed-local-code
config_share_restore_history_contract_commit=380f3a3
config_share_restore_history_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_history_contract_push_status=done
config_share_restore_history_contract_test_status=scoped_pytest_108_passed
config_share_restore_history_contract_contract=restore_allows_expired_revoked_exhausted_share_records_as_history_only_while_usable_hashes_remain_blocked
config_share_restore_history_contract_live_actions=false
config_share_restore_policy_shape_validation_contract_status=completed-local-code
config_share_restore_policy_shape_validation_contract_commit=6387e9e
config_share_restore_policy_shape_validation_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_policy_shape_validation_contract_push_status=done
config_share_restore_policy_shape_validation_contract_test_status=scoped_pytest_110_passed
config_share_restore_policy_shape_validation_contract_contract=backup_restore_rejects_malformed_config_share_token_policy_shape_before_backup_or_target_write
config_share_restore_policy_shape_validation_contract_live_actions=false
config_share_restore_timestamp_shape_validation_contract_status=completed-local-code
config_share_restore_timestamp_shape_validation_contract_commit=52c5340
config_share_restore_timestamp_shape_validation_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_timestamp_shape_validation_contract_push_status=done
config_share_restore_timestamp_shape_validation_contract_test_status=scoped_pytest_112_passed
config_share_restore_timestamp_shape_validation_contract_contract=backup_restore_rejects_malformed_config_share_token_timestamps_before_history_classification_or_target_write
config_share_restore_timestamp_shape_validation_contract_live_actions=false
config_share_restore_scope_metadata_shape_validation_contract_status=completed-local-code
config_share_restore_scope_metadata_shape_validation_contract_commit=f815ed2
config_share_restore_scope_metadata_shape_validation_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_scope_metadata_shape_validation_contract_push_status=done
config_share_restore_scope_metadata_shape_validation_contract_test_status=scoped_pytest_120_passed
config_share_restore_scope_metadata_shape_validation_contract_contract=backup_restore_rejects_malformed_config_share_token_scope_metadata_before_history_classification_or_target_write
config_share_restore_scope_metadata_shape_validation_contract_live_actions=false
config_share_restore_token_identity_metadata_validation_contract_status=completed-local-code
config_share_restore_token_identity_metadata_validation_contract_commit=bb9ce25
config_share_restore_token_identity_metadata_validation_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_token_identity_metadata_validation_contract_push_status=done
config_share_restore_token_identity_metadata_validation_contract_test_status=scoped_pytest_130_passed
config_share_restore_token_identity_metadata_validation_contract_contract=backup_restore_rejects_malformed_config_share_token_identity_metadata_before_history_classification_or_target_write
config_share_restore_token_identity_metadata_validation_contract_live_actions=false
config_share_restore_foreign_key_integrity_contract_status=completed-local-code
config_share_restore_foreign_key_integrity_contract_commit=af7dde9
config_share_restore_foreign_key_integrity_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_foreign_key_integrity_contract_push_status=done
config_share_restore_foreign_key_integrity_contract_test_status=scoped_pytest_132_passed
config_share_restore_foreign_key_integrity_contract_contract=backup_create_restore_reject_foreign_key_integrity_violations_before_backup_or_target_write
config_share_restore_foreign_key_integrity_contract_live_actions=false
config_share_restore_schema_foreign_key_declaration_contract_status=completed-local-code
config_share_restore_schema_foreign_key_declaration_contract_commit=6a1ca94
config_share_restore_schema_foreign_key_declaration_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_foreign_key_declaration_contract_push_status=done
config_share_restore_schema_foreign_key_declaration_contract_test_status=scoped_pytest_134_passed
config_share_restore_schema_foreign_key_declaration_contract_contract=backup_create_restore_reject_missing_config_share_owner_foreign_key_declaration_before_backup_or_target_write
config_share_restore_schema_foreign_key_declaration_contract_live_actions=false
config_share_restore_schema_check_constraint_declaration_contract_status=completed-local-code
config_share_restore_schema_check_constraint_declaration_contract_commit=52f673e
config_share_restore_schema_check_constraint_declaration_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_check_constraint_declaration_contract_push_status=done
config_share_restore_schema_check_constraint_declaration_contract_test_status=scoped_pytest_136_passed
config_share_restore_schema_check_constraint_declaration_contract_contract=backup_create_restore_reject_missing_config_share_check_constraint_declarations_before_backup_or_target_write
config_share_restore_schema_check_constraint_declaration_contract_live_actions=false
config_share_restore_schema_unique_constraint_declaration_contract_status=completed-local-code
config_share_restore_schema_unique_constraint_declaration_contract_commit=4cf1e85
config_share_restore_schema_unique_constraint_declaration_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_unique_constraint_declaration_contract_push_status=done
config_share_restore_schema_unique_constraint_declaration_contract_test_status=scoped_pytest_138_passed
config_share_restore_schema_unique_constraint_declaration_contract_contract=backup_create_restore_reject_missing_config_share_primary_key_or_token_hash_unique_declarations_before_backup_or_target_write
config_share_restore_schema_unique_constraint_declaration_contract_live_actions=false
config_share_restore_schema_required_columns_declaration_contract_status=completed-local-code
config_share_restore_schema_required_columns_declaration_contract_commit=1f0343d
config_share_restore_schema_required_columns_declaration_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_required_columns_declaration_contract_push_status=done
config_share_restore_schema_required_columns_declaration_contract_test_status=scoped_pytest_140_passed
config_share_restore_schema_required_columns_declaration_contract_contract=backup_create_restore_reject_missing_config_share_tokens_required_columns_before_backup_or_target_write
config_share_restore_schema_required_columns_declaration_contract_live_actions=false
config_share_restore_schema_column_declaration_shape_contract_status=completed-local-code
config_share_restore_schema_column_declaration_shape_contract_commit=101da38
config_share_restore_schema_column_declaration_shape_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_column_declaration_shape_contract_push_status=done
config_share_restore_schema_column_declaration_shape_contract_test_status=scoped_pytest_142_passed
config_share_restore_schema_column_declaration_shape_contract_contract=backup_create_restore_reject_weakened_config_share_tokens_column_declaration_shape_before_backup_or_target_write
config_share_restore_schema_column_declaration_shape_contract_live_actions=false
config_share_restore_schema_index_declaration_contract_status=completed-product-fix-pushed
config_share_restore_schema_index_declaration_contract_commit=60b77fd
config_share_restore_schema_index_declaration_contract_branch=codex/public-config-delivery-policy-contract
config_share_restore_schema_index_declaration_contract_push_status=done
config_share_restore_schema_index_declaration_contract_test_status=scoped_pytest_66_passed
config_share_restore_schema_index_declaration_contract_extended_test_status=scoped_pytest_151_passed
config_share_restore_schema_index_declaration_contract_fix=ignore_sqlite_index_xinfo_auxiliary_rows_key_0
config_share_restore_schema_index_declaration_contract_contract=backup_create_restore_reject_missing_config_share_tokens_index_declaration_shape_before_backup_or_target_write
config_share_restore_schema_index_declaration_contract_live_actions=false
android_multi_device_private_config_execution_gate_status=prepared-docs-only
android_multi_device_private_config_execution_gate=ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_3_TO_5
android_multi_device_private_config_execution_device_count_range=3-5
android_multi_device_private_config_execution_review_doc=docs/AMN2_PHASE_9_ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_GATE_REVIEW.ru.md
android_multi_device_private_config_execution_runbook_doc=docs/AMN2_PHASE_9_ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_RUNBOOK.ru.md
android_multi_device_private_config_execution_result_template_doc=docs/AMN2_PHASE_9_ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_RESULT_TEMPLATE.ru.md
android_multi_device_private_config_execution_local_artifact_root=private-artifacts/phase9/android-multi-device/<run_id>/
android_multi_device_private_config_execution_local_artifact_root_gitignored=true
android_multi_device_private_config_execution_filename_policy=Neobyatnaya-AMNZ-N-android-01.conf..Neobyatnaya-AMNZ-N-android-05.conf
android_multi_device_private_config_execution_status=completed-private-operator-only
android_multi_device_private_config_execution_run_id=20260628T231440
android_multi_device_private_config_execution_result_doc=docs/AMN2_PHASE_9_ANDROID_MULTI_DEVICE_PRIVATE_CONFIG_EXECUTION_RESULT.ru.md
android_multi_device_private_config_execution_device_count=5
android_multi_device_private_config_execution_config_files_generated=true
android_multi_device_private_config_execution_peer_apply_performed=true
android_multi_device_private_config_execution_qr_files_generated=false
android_multi_device_private_config_execution_vpn_import_links_generated=false
android_multi_device_private_config_execution_config_delivery_performed=false
android_multi_device_private_config_execution_generated_config_local_path=private-artifacts/phase9/android-multi-device/20260628T231440/generated-configs/
android_multi_device_private_config_execution_payload_output_to_chat=blocked
android_multi_device_private_config_execution_next_step=MANUAL_OPERATOR_ANDROID_IMPORT_REVIEW_OR_PREPARE_SAFE_STATUS_SYNC
phase9_client_display_name_policy_refresh_status=prepared-docs-only
phase9_client_display_name_policy_refresh_doc=docs/AMN2_PHASE_9_CLIENT_DISPLAY_NAME_POLICY_REFRESH.ru.md
phase9_client_display_name_target=NeobyatnayaNET
phase9_client_display_name_cyrillic_alias=НеобъятнаяNET
phase9_client_display_name_suffix_policy=none
phase9_client_display_name_manual_rename_required=true
phase9_client_display_name_android_observed=Сервер 1|Сервер 3
phase9_client_display_name_windows_manual_rename_observed=true
phase9_client_display_name_tv_projector_status=done
phase9_client_display_name_operator_review_partial_status=03-04-auto_name_server1;05-windows_manual_rename
phase9_android_import_last_sync_step=MANUAL_OPERATOR_ANDROID_IMPORT_REVIEW_OR_PREPARE_SAFE_STATUS_SYNC
phase9_android_import_review_or_prepare_safe_status_sync_executed=true
phase9_automation_intake_2026_06_28=P9-N007_docs-only_review-only
phase9_amnezia_client_watch=4.8.19.0_release_current_4.9.0.3_unreleased_watch
phase9_android_server1_upstream_signal=client_display_name_behavior_reinforced
phase9_prvtpro_watch=v1.4.4_a62f958_carry-forward_no_new_launch_go
private_self_config_readiness_with_naming_review=completed-docs-only
private_self_config_readiness_with_naming_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
canonical_naming=Neobyatnaya-AMNZ-N
canonical_client_display_name=NeobyatnayaNET
canonical_client_display_name_alias=НеобъятнаяNET
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
private_self_config_execution_go=false
phase9_private_self_config_execution_readiness_gateway=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
phase9_private_self_config_execution_readiness_gate_decision=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
phase9_private_self_config_execution_readiness_gate_confirmed_by=ChatGPT 5.5
phase9_private_self_config_execution_readiness_next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
phase9_private_self_config_execution_readiness_review_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE_REVIEW.ru.md
phase9_private_self_config_execution_readiness_runbook=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RUNBOOK.ru.md
phase9_private_self_config_execution_readiness_result_template=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT_TEMPLATE.ru.md
phase9_private_self_config_execution_readiness_pass=Neobyatnaya-AMNZ-N
phase9_private_self_config_execution_readiness_fail=generic naming as production naming|payload/secrets output|peer/config/public/self-service actions
phase9_private_self_config_execution_readiness_stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
phase9_private_self_config_execution_readiness_risk_model=docs-only execution package prep approved; live changes blocked
phase9_private_self_config_execution_readiness_android=Сервер 1 as documented client display-name compatibility gap
phase9_private_self_config_execution_readiness_android_fallback=manual_rename
phase9_private_self_config_execution_readiness_windows=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
phase9_private_self_config_execution_readiness_ios=not_proven/manual_rename_fallback
phase9_private_self_config_execution_package_prep_status=prepared-docs-only
phase9_private_self_config_execution_package_prep_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
phase9_private_self_config_execution_package_prep_result_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT.ru.md
phase9_private_self_config_execution_package_prep_artifacts_present=true
phase9_private_self_config_execution_package_prep_artifacts_missing=none
phase9_private_self_config_execution_package_prep_safe_scan_status=passed_before_commit_9fb6196
phase9_private_self_config_execution_package_prep_diffcheck_status=passed_before_commit_9fb6196
phase9_private_self_config_execution_package_prep_commit=9fb6196
phase9_private_self_config_execution_package_prep_push_status=done
phase9_private_self_config_execution_package_prep_origin_sync=true
phase9_private_self_config_execution_package_prep_post_push_refresh_status=prepared-docs-only
phase9_5_5_hold_confirmation_status=matched-docs-only
phase9_5_5_hold_confirmation_next_docs_only_step=CONFIRM_HOLD_STATE
phase9_5_5_hold_confirmation_stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
phase9_5_5_current_chat_match_status=matched-docs-only
phase9_5_5_current_chat_match_source=current_chat_operator_mediated_5_5_codex_spark
phase9_5_5_current_chat_match_conflict_status=none
phase9_5_5_matched_hold_status_refresh_status=prepared-docs-only
phase9_5_5_matched_hold_status_refresh_next_docs_only_step=REVIEW_PROPOSED_DOCS_CHANGES
phase9_current_chat_model_switch_packet_status=matched-docs-only
phase9_current_chat_model_switch_external_chat_required=false
phase9_current_chat_model_switch_5_5_match_status=matched
phase9_current_chat_model_switch_codex_spark_compare_status=matched
phase9_current_chat_model_switch_conflict_status=none
phase9_current_chat_model_switch_status_refresh_status=prepared-docs-only
phase9_current_chat_model_switch_status_refresh_next_docs_only_step=REVIEW_PROPOSED_DOCS_CHANGES
phase9_untracked_plan_file_review_status=reviewed-docs-only
phase9_untracked_plan_file=docs/superpowers/plans/2026-06-27-amn2-phase9-android-display-name-gate-prep.md
phase9_untracked_plan_file_decision=removed-local-only
phase9_untracked_plan_file_stage_status=not-staged
phase9_untracked_plan_file_commit_status=not-committed-untracked-local-cleanup
phase9_untracked_plan_review_status_refresh_status=prepared-docs-only
phase9_untracked_plan_review_status_refresh_next_docs_only_step=REVIEW_PROPOSED_DOCS_CHANGES
phase9_package_prep_recovery_working_tree_status=clean
phase9_package_prep_recovery_latest_commit=1ca1dae
phase9_package_prep_recovery_origin_sync=true
phase9_package_prep_recovery_status_refresh_status=prepared-docs-only
phase9_package_prep_recovery_status_refresh_next_docs_only_step=REVIEW_PROPOSED_DOCS_CHANGES
android_display_name_future_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_display_name_gate_review_doc=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW.ru.md
android_display_name_gate_review_runbook=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK.ru.md
android_display_name_gate_review_result_template=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md
android_display_name_gate_result_doc=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md
android_display_name_gate_docs_status=completed-docs-only
android_display_name_gate_docs_decision_status=decision-approved-by-5_5
android_display_name_gate_pass=Neobyatnaya-AMNZ-N
android_display_name_gate_documented_limitation=SERVER1_as_client_display_name_compatibility_gap_with_manual_rename_fallback
android_display_name_gate_fail=generic_generated_name_or_filename|SERVER1_as_production_naming|payload_secrets_output|peer_config_public_self_service_action
android_display_name_gate_execution_go=false
android_display_name_gate_next=platform_policy_docs_sync
android_display_name_observed=Сервер 1
android_display_name_gate_result=DOCUMENTED_LIMITATION
android_display_name_gate_decision_status=DOCUMENTED_LIMITATION
android_display_name_pass_not_reached=true
android_display_name_observed_classification=localized_SERVER1_client_display_name_compatibility_gap
android_display_name_result_sync=completed_pair_docs_matrix_next_chat
android_display_name_pair_sync_by=ChatGPT 5.3-Spark
android_display_name_pair_sync_doc_scope=PROJECT_STATUS_CURRENT_and_TASK_MATRIX_REFRESH_and_NEXT_CHAT
android_display_name_pair_sync_next_chat_status=awaiting_or_completed_in_docs_mode
android_display_name_production_naming=Neobyatnaya-AMNZ-N
android_display_name_fallback=manual_rename
android_display_name_pass_required=Neobyatnaya-AMNZ-N
android_tv_amneziavpn_display_name_policy=standard_conf_filename_stem_proven
ios_defaultvpn_display_name_policy=not_observed_connection_and_traffic_only
android_display_name_execution_go_after_result=false
windows_amneziavpn_display_name_strategy=standard_conf_filename_stem_proven
windows_amneziavpn_canonical_filename=Neobyatnaya.NET-device_id.conf
phase9_platform_display_name_implementation_readiness_doc=docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md
phase9_platform_display_name_implementation_handoff=prepared_docs_only_for_generator_code
platform_display_name_generator_code_handoff_mode=docs_only_with_task_list_and_constraints
platform_display_name_implementation_scope=android_tv_and_windows_standard_conf_filename_stem|ios_name_not_observed
android_display_name_strategy=standard_conf_filename_stem
ios_display_name_strategy=not_observed_no_claim
server1_display_name_issue=resolved_for_verified_standard_conf_path
phase9_validation_config_path_checklist=completed-docs-only
phase9_validation_config_path_checklist_doc=docs/AMN2_PHASE_9_VALIDATION_AND_CONFIG_PATH_CHECKLIST.ru.md
phase9_validation_checklist_status=documented-limitations-accepted-with-hold
phase9_xray_validation_watch=amnezia-client_d8b8590
phase9_xray_runtime_validation_snapshot=completed-local-code
phase9_server_config_numeric_range_validation=completed-local-code
phase9_server_config_host_path_validation=completed-local-code
phase9_server_config_network_cidr_validation=completed-local-code
phase9_server_config_identifier_validation=completed-local-code
phase9_server_config_unique_server_name=completed-local-code
phase9_server_config_enum_validation=completed-local-code
phase9_config_delivery_template_unknown_placeholder_guard=completed-local-code
phase9_config_delivery_template_empty_message_guard=completed-local-code
phase9_config_template_override_empty_config_guard=completed-local-code
phase9_runtime_config_path_checklist_watch=runtime_path_discovery_guard_completed_local
ssh_auth_hardening_gate_review=completed-docs-only
ssh_auth_hardening_gate_review_doc=docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
ios_defaultvpn_default_status=passed-first-connect-and-traffic-reconnect-soak-pending
ssh_auth_no_hardening_execution=not-approved
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
important_block_realization_status=completed-docs-only
public_launch_status=not-approved
config_delivery_status=not-approved
peer_creation_status=not-approved
production_rollout_status=not-approved
telegram_profile_media_mutation_status=not-approved
restore_import_status=not-proven
provider_rebuild_status=not-proven
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
next_step=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
```

Ключевые ограничения в этом срезе:

- Не открывать live/VPS/SSH/config/Telegram/public action без fresh exact named gate.
- iOS DefaultVPN standard `.conf` first-connect и трафик подтверждены; reconnect
  и long-session soak остаются отдельной проверкой.
- Не запускать любые новые `peer creation`, `config delivery`, `production rollout`.
- Перед каждым commit/push выполнить SECRET_POLLUTION_SCAN и local markdown/diff clean checks.
- Real-device Android TV и Windows 11 AmneziaVPN подтвердили display name из
  filename stem обычного `.conf`; рабочее наблюдаемое имя:
  `Neobyatnaya-AMNZ-N-android-tv-01`. Native `.vpn` JSON импортировался, но не
  подключился, поэтому не является production naming/config path.
- Platform naming implementation: `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE`
  закрыт как `APPROVED_WITH_TEST_ENV_LIMITATION`: Windows AmneziaWG standalone
  использует filename/basename strategy `Neobyatnaya-AMNZ-N.conf`.
  Android TV и Windows official AmneziaVPN теперь также подтверждены через
  standard `.conf` filename stem. iOS display name отдельно не наблюдался;
  соединение и трафик DefaultVPN подтверждены. Текущий AMN2 full suite:
  `823 passed, 1 skipped, 1 warning`.
- Automation intake 2026-06-28 accounted as `P9-N007` docs-only/review-only:
  Amnezia `4.9.0.3` is unreleased watch-only, current release remains
  `4.8.19.0`, Android AmneziaWG remains `2.0.1`; `SERVER1` / `Сервер 1`
  reinforced as client display-name behavior, not production naming.
  PRVTPRO `v1.4.4` / `a62f958` remains carry-forward input; public tunnels
  stay hybrid-only/gated and do not approve public exposure.

Phase 9 `AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW`
completed on 2026-06-27 as `completed-docs-only-review`. Document:
`docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md`.
It accepts Phase 8 as closed, accepts prepared Phase 9 material, confirms the
first track as `PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING`, fixes
`Neobyatnaya-AMNZ-N` as canonical config/device/file naming policy, classifies
`SERVER1` as Android AmneziaWG display-name compatibility gap, and keeps real
config generation/import behind future exact gate
`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`. No live/VPS/SSH/config/
Telegram/public execution, peer/config creation, public/self-service delivery,
VPS/auth/firewall/users/keys/ports mutation or secret-bearing output was
performed.

Phase 9 Android display-name safe observation recorded on 2026-06-27 as
`completed-safe-result`. Result:
`docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md`.
Observed display name: `Сервер 1`. Classification:
`documented_limitation`, localized `SERVER1` / client display-name compatibility
gap. Canonical naming remains `Neobyatnaya-AMNZ-N`. Windows AmneziaWG standalone
should use filename/basename strategy with required filename
`Neobyatnaya-AMNZ-N.conf`; Android/iOS Amnezia app keep manual rename fallback
unless a future exact gate proves automatic display-name support. No config
payload, QR, import URI, keys, PSK, token/password, raw logs, peer/config
creation, public/self-service action or VPS/SSH/Telegram/public execution was
performed.

Phase 9 `AMN2_SSH_AUTH_HARDENING_GATE_REVIEW` accepted on 2026-06-27 as
`completed-docs-only-review`. Document:
`docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md`. It keeps SSH auth hardening
as future optional hardening only; current execution remains not approved and
requires `AMN2_SSH_AUTH_HARDENING_EXECUTION_GATE` before any SSH/auth/firewall/
users/keys/ports mutation.

Phase 8 final private/operator RC closeout completed on 2026-06-27 as
`completed-docs-only-final-closeout`. Closeout:
`docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-final-closeout-2026-06-27.md`.
Final status: `phase8_final_status=launch-ready-with-explicit-limitations`,
`private_operator_rc_launch_ready=true`,
`android_private_operator_rc_proof=complete-with-explicit-limitations`,
`telegram_private_operator_rc_proof=completed-no-config-delivery`,
`db_runtime_path_classification=resolved-for-path-existence`, and
`ssh_key_based_access_status=passed`. Public launch, public exposure, config
delivery, peer creation, public self-service config delivery, restore/import,
provider rebuild and production-scale rollout remain not approved. Phase 9
entry brief prepared docs-only:
`docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md` with candidate lanes
`PUBLIC_LAUNCH_READINESS`, `CONTROLLED_CONFIG_DELIVERY`,
`HARDENING_PRODUCTIZATION`, and `DR_RELIABILITY`. Default remains
`ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`; any live/config/public/VPS action still requires a
fresh exact named gate.

Phase 9 hardening docs package prep completed on 2026-06-27 as
`completed-docs-only`. Bundle:
`docs/AMN2_PHASE_9_HARDENING_DOCS_PACKAGE.ru.md`. Evidence:
`research/amn2/phase-9-hardenings-docs-package-2026-06-27.md`.
Lane is fixed to `HARDENING_PRODUCTIZATION` via
`docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md`; hardening preps ready:
`docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`,
`docs/AMN2_HELPER_STYLE_HARDENING.ru.md`,
`docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`,
`docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING.ru.md`,
`docs/AMN2_TELEGRAM_OPERATION_RUNBOOK_POLISH.ru.md`,
`docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`,
`docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md`.
Critical limitations remain unchanged:
`public_launch_status=not-approved`,
`config_delivery_status=not-approved`,
`peer_creation_status=not-approved`,
`production_rollout_status=not-approved`,
`public_self_service_config_delivery_status=not-approved`,
`restore_import_status=not-proven`,
`provider_rebuild_status=not-proven`.
Current active next-chat handoff: `docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_5.ru.md`.

Phase 9 `AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION` completed on 2026-06-27 as
`completed-docs-only`. Realization doc:
`docs/AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION.ru.md`. Evidence:
`research/amn2/phase-9-important-block-realization-2026-06-27.md`. The block
turns three important reviews into operational rails for the current
`HARDENING_PRODUCTIZATION` lane: SSH auth-noise hardening execution remains
not approved and requires future `AMN2_SSH_AUTH_HARDENING_GATE_REVIEW`; DB
aggregate counts remain `optional-confidence-not-hardening-blocker` and live
counts require future `AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE_REVIEW`; iOS
DefaultVPN remains `failed-not-accepted` / `failed-no-tested-import-path` and
any iOS acceptance or config delivery claim requires future
`AMN2_IOS_ACCEPTANCE_GATE_REVIEW`. No live/VPS/SSH/DB/config/Telegram/public
gate was opened by this realization.

Phase 9 `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` completed on 2026-06-27 as
`completed-docs-only-review`. Review:
`docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`. Evidence:
`research/amn2/phase-9-ios-acceptance-decision-review-2026-06-27.md`.
Operator clarification: iOS DefaultVPN is `failed-not-accepted`; AMN2 configs
are not added by QR or by any tested non-QR path. This is not a blocker for
the current `HARDENING_PRODUCTIZATION` lane, but iOS release/support/config
delivery claims remain forbidden until a future exact iOS acceptance gate.
No live/VPS/SSH/config/Telegram/public gate was opened for this decision.

Phase 9 `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` completed on 2026-06-27 as
`completed-docs-only-review`. Review:
`docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`. Evidence:
`research/amn2/phase-9-ssh-auth-noise-mitigation-review-2026-06-27.md`.
Heavy SSH auth-noise remains observed, but execution is not approved for the
current hardening lane: no `sshd_config`, firewall, users, keys, password auth,
root login, SSH port, rate limiting, service or provider mutation without a
future exact gate and rollback/provider-console boundary. Current safe policy:
key-based short SSH operations and no long SSH manual windows.

Phase 9 `AMN2_DB_AGGREGATE_COUNTS_REVIEW` completed on 2026-06-27 as
`completed-docs-only-review`. Review:
`docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md`. Evidence:
`research/amn2/phase-9-db-aggregate-counts-review-2026-06-27.md`.
Phase 8 already resolved DB runtime path existence at
`/opt/amn2/data/amneziya.sqlite3`; aggregate counts remain
`optional-confidence-not-hardening-blocker`. No live DB/VPS/SSH observation,
DB row dump, DB copy/download, config generation/delivery or public exposure
was opened by this review. Future live counts require a separate exact gate.

Phase 8 `PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW` completed on 2026-06-26 as
`completed-docs-only`. Review:
`docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-telegram-operation-gate-review-2026-06-26.md`.
Verdict: `review_go=true`,
`execution_gate_go=conditional-go-with-explicit-operator-approval`.
Prepared future exact gate `PRIVATE_RC_TELEGRAM_OPERATION_GATE` for controlled
private/operator Telegram bot operation: read-only prechecks, public closed
probes, Telegram `getMe`, exactly one controlled polling process, live replies
only to approved admin/operator chats, manual UX check, stop polling at end, and
final no-polling/no-public-exposure guard. Config generation/delivery, peer
creation, public exposure, package apply, broad service restart, Telegram
profile/media mutation, broadcast/mass send, DB row dump/download/copy and
secret-bearing output remain forbidden. No live VPS/SSH/config/Telegram/public
gate was opened for this review.

Phase 8 `PRIVATE_RC_FINAL_STATUS_SNAPSHOT` completed on 2026-06-26 as
`completed-docs-only`. Snapshot:
`docs/AMN2_PRIVATE_RC_FINAL_STATUS_SNAPSHOT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-final-status-snapshot-2026-06-26.md`.
Final status remains `launch-ready-with-explicit-limitations` with active
operator hold. Android private/operator RC proof is complete with explicit
limitations; public launch, public exposure, Telegram live config delivery,
public/self-service config delivery, new peer/config creation without exact
gate, restore/import, provider rebuild and production-scale rollout remain not
approved. Recommended next step is `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`; if live operation
is desired, start with `PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW`, not
execution. No live VPS/SSH/config/Telegram/public gate was opened for this
snapshot.

Phase 8 `PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` completed on 2026-06-26 as
`completed-docs-only`, followed by active `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА` hold.
Refresh doc: `docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md`.
Evidence:
`research/amn2/phase-8-private-rc-release-limitations-refresh-2026-06-26.md`.
Updated `docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md` and
`docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md` to reflect the new Android
proof: P8-C001 Android phone passed, P8-C003 remains Android projector
fresh-zero proof with explicit limitation, and third-party Android phone passed
manual + server-side proof. Public launch, public exposure, Telegram live
config delivery, public/self-service config delivery, new peer/config creation
without exact gate, iOS release acceptance, restore/import DR, provider rebuild
and production-scale rollout remain not approved. No live VPS/SSH/config/
Telegram/public gate was opened for this refresh. Next action requires an exact
named gate from the operator.

Phase 8 `PRIVATE_RC_FINAL_ANDROID_SUMMARY` completed on 2026-06-26 as
`completed-docs-only`. Summary:
`docs/AMN2_PRIVATE_RC_FINAL_ANDROID_SUMMARY.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-final-android-summary-2026-06-26.md`.
Final Android private/operator RC status is
`passed-with-explicit-limitations`: P8-C001 Android phone acceptance passed
with reconnect sanity; P8-C003 Android projector fresh-zero proof passed with
explicit projector limitation; third-party Android phone proof passed with both
manual owner report and server-side handshake/endpoint/rx-tx observation
(`fresh_peer_public_key_fp=49e456e4edcb`, `latest_handshake_age_s=23`,
`endpoint_observed=yes`, `rx=55600508`, `tx=132476207`). This strengthens
private/operator RC Android confidence but does not approve public launch,
public exposure, Telegram live config delivery, public/self-service config
delivery, iOS release acceptance, restore/import DR, provider rebuild or
production-scale rollout. No live VPS/SSH/config/Telegram/public gate was
opened for this summary.

Phase 8 `THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_HELPER_UPLOAD_RETRY_GATE`
passed on 2026-06-26 as `passed-server-side-observation`. Result:
`docs/AMN2_THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-third-party-android-traffic-observation-result-2026-06-26.md`.
Linked peer fp `49e456e4edcb`; server-side observation found the fresh peer,
`latest_handshake_age_s=23`, `endpoint_observed=yes`,
`transfer_rx_bytes=55600508`, `transfer_tx_bytes=132476207`,
`fresh_handshake_after=true`, and
`third_party_android_server_observation_status=passed`. Public probes to
`3030`, `3040`, `80` and `443` remained `000` before and after; temporary
helper cleanup passed. No config generation/delivery, peer creation, service
start/restart/stop, package upload/apply, public exposure, firewall/listener/
TLS/proxy change, Telegram live send/polling, raw `wg dump`, `.conf`, QR,
`vpn://`, private key, PSK, token/password output, restore/import/reboot or
provider action was performed. Third-party Android proof now has both manual
owner report and server-side handshake/rx-tx evidence.

Phase 8 third-party Android manual acceptance was recorded on 2026-06-26 as
`passed-by-third-party-operator-report`. Result:
`docs/AMN2_THIRD_PARTY_ANDROID_MANUAL_ACCEPTANCE_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-third-party-android-manual-acceptance-result-2026-06-26.md`.
Linked handoff: `THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE`, run id
`20260625T193843Z`, fresh peer fp `49e456e4edcb`, file
`third-party-android-device-2.conf`. Operator relayed the Android owner's safe
report: config imported, connection works, traffic works fast. No config
payload, QR, `vpn://`, private key, PSK, token/password or screenshot payload
was shared. No live VPS/SSH/config/Telegram/public gate was opened for this
manual record. Server-side handshake/rx-tx observation remains available via
future exact gate `THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_GATE` if stronger
evidence is required.

Phase 8 `THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE` completed on 2026-06-25 as
`completed-private-file-copied-secret-not-printed`. Result:
`docs/AMN2_THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-third-party-android-config-handoff-result-2026-06-25.md`.
Run id `20260625T193843Z`; target VPS `89.185.80.166`; source overlay matched
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`; third-party Telegram ID was not
required for private file handoff. Exactly one fresh peer/config was created
through AMN2 path: `fresh_peer_public_key_fp=49e456e4edcb`,
`fresh_vpn_ip=10.8.0.7`, peer count `5 -> 6`. Local private `.conf` artifact:
`third-party-android-device-2.conf`, bytes `478`, sha256
`ce431c29b5b7dae010bb91c429d4f401f048893c356498ba6f2d65e99b224db4`. No config
payload, QR, `vpn://`, private key, PSK, token or password was printed; no
Telegram live send/polling, public exposure, destructive install,
restore/import/reboot, provider action or extra peer creation was performed.
Next exact gate after third-party manual import/connect/traffic attempt:
`THIRD_PARTY_ANDROID_TRAFFIC_OBSERVATION_GATE`.

Phase 8 `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА` hold recorded on 2026-06-25 as
`active-hold`. Hold doc: `docs/AMN2_WAIT_FOR_OPERATOR_REQUEST_HOLD.ru.md`.
Evidence:
`research/amn2/phase-8-wait-for-operator-request-hold-2026-06-25.md`.
AMN2 remains `launch-ready-with-explicit-limitations`; public launch, config
delivery, Telegram live send and live VPS actions remain not approved. Next
action requires an explicit exact named gate from the operator. No live VPS/SSH,
config, Telegram or public gate was opened.

Phase 8 third-party Android config handoff review completed on 2026-06-25 as
docs-only. Review:
`docs/AMN2_THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE_REVIEW.ru.md`. Evidence:
`research/amn2/phase-8-third-party-android-config-handoff-review-2026-06-25.md`.
Result: `review_go=true`,
`gate_open_go=conditional-go-when-third-party-android-phone-is-available`.
Recommended handoff model is operator-mediated private `.conf` handoff to
`C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF`. Third-party Telegram ID is not
required for file handoff; it is required only if the execution helper must bind
the AMN2 order to a Telegram identity. Unrelated old Telegram IDs must not be
reused. Future execution gate is `THIRD_PARTY_ANDROID_CONFIG_HANDOFF_GATE`.
No live VPS/SSH/config/Telegram/public gate was opened; no peer/config was
created; no secret-bearing payload was output.

Phase 8 `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY` completed on 2026-06-25
as `passed-db-path-classified-with-aggregate-limitation`. Result:
`docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_RETRY_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-db-runtime-observation-retry-result-2026-06-25.md`.
Small read-only SSH commands confirmed source overlay
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`, `.env` key presence,
`DATABASE_PATH=data/amneziya.sqlite3`, resolved DB path
`/opt/amn2/data/amneziya.sqlite3`, DB existence `true`, size `147456`, mode
`600`, and exactly one DB candidate at `data/amneziya.sqlite3`. This
reclassifies the earlier Telegram live preview `db_present=false` as helper
observation issue, not runtime DB absence. Aggregate counts were not completed
because two helper attempts hit Windows SSH shell/SQL quoting issues; no DB
rows were printed and no DB copy/download occurred. No package apply, service
start/restart/stop, public exposure, config generation/delivery, peer creation,
Telegram polling/live send, restore/import/reboot, provider rebuild or
secret-bearing output was performed. No new blocker inside current
private/operator RC limitations.

Phase 8 `PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_GATE` passed on 2026-06-25.
Result: `docs/AMN2_PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_RESULT.ru.md`.
Evidence:
`research/amn2/phase-8-private-rc-ssh-transport-diagnostic-result-2026-06-25.md`.
Target VPS `89.185.80.166` accepted small read-only SSH commands: `true`,
`echo`, safe remote summary and `/opt/amn2` source marker read all passed.
Source overlay matched AMN2
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`; public probes to `3030`, `3040`,
`80` and `443` stayed closed as `000` before and after. This reclassifies the
previous DB/runtime observation blocker from general SSH transport failure to a
likely large-stdin/helper-execution-method issue. DB discrepancy remains
unresolved but retry is now unblocked via small read-only SSH commands. No
package apply, service start/restart/stop, sshd/firewall/auth change, public
exposure, config generation/delivery, peer creation, DB row dump/download/copy,
Telegram polling/live send, restore/import/reboot, provider rebuild or
secret-bearing output was performed. Recommended next exact gate:
`PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE_RETRY`.

Phase 8 private RC SSH/DB/partner review package completed on 2026-06-25 as
docs-only. New docs:
`docs/AMN2_PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW.ru.md`,
`docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_RETRY_PLAN.ru.md`, and
`docs/AMN2_PRIVATE_RC_TELEGRAM_PARTNER_ADMIN_PREVIEW_REVIEW.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-ssh-db-partner-review-package-2026-06-25.md`.
The package responds to the latest DB/runtime observation blocker
`ssh_transport_closed_before_remote_precheck` and the Telegram live preview
limitation `partner_start_flow_observed=not_reported`. It prepares future exact
gates for SSH transport diagnostic, DB/runtime observation retry after SSH
diagnostic, and partner/admin Telegram preview. No live VPS/SSH command,
package apply, service start/restart/stop, public exposure, config
generation/delivery, Telegram polling/live send, restore/import/reboot,
provider rebuild, production peer/user mutation or secret-bearing output was
performed.

Phase 8 `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE` was opened on 2026-06-24 and
ended as `blocked-by-ssh-transport-before-observation`. Result:
`docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-db-runtime-observation-result-2026-06-24.md`.
Both the main helper and resume helper completed local dry probe URL inspection
and confirmed public probes to `3030`, `3040`, `80` and `443` as `000`, but SSH
closed before the first remote precheck output:
`Connection closed by 89.185.80.166 port 22`. Therefore DB/runtime state was
not observed and the earlier discrepancy remains unresolved:
`PRIVATE_RC_OPERATOR_RUN_GATE` saw `db_present=true`, while
`PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` saw `db_present=false`. No package
apply, service start/restart/stop, public exposure, config generation/delivery,
peer creation, DB row dump/download/copy, Telegram polling/live send,
restore/import/reboot, provider rebuild or secret-bearing output was performed.
Recommended next exact gate: `PRIVATE_RC_SSH_TRANSPORT_DIAGNOSTIC_REVIEW`.

Phase 8 private RC DB/runtime observation review completed on 2026-06-24 as
docs-only. Review:
`docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_REVIEW.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-db-runtime-observation-review-2026-06-24.md`.
The review prepares future exact gate `PRIVATE_RC_DB_RUNTIME_OBSERVATION_GATE`
to investigate why `PRIVATE_RC_OPERATOR_RUN_GATE` saw `db_present=true` while
`PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` saw `db_present=false`. Result:
`review_go=true`, `gate_open_go=conditional-go-with-explicit-operator-approval`.
No live VPS/SSH command, package apply, service restart, public exposure,
config generation/delivery, Telegram polling/live send, restore/import/reboot,
provider rebuild, production peer/user mutation or secret-bearing output was
performed.

Phase 8 `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE` passed on 2026-06-24 as
`passed-with-manual-operator-observation`. Result:
`docs/AMN2_PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-telegram-bot-live-preview-result-2026-06-24.md`.
Target VPS `89.185.80.166` matched expected AMN2 runtime/source head
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`; Telegram `getMe` passed; exactly
one controlled bot polling process started; operator `/start` flow passed;
polling was stopped; public probes to `3030`, `3040`, `80` and `443` stayed
closed as `000` before and after. No package apply, broad service restart,
public exposure, config generation/delivery, peer creation, Telegram
profile/media mutation, restore/import/reboot, provider rebuild or
secret-bearing output occurred. Limitations: partner/admin `/start` was not
reported, `db_present=false` was observed in this helper run, and public launch
plus config delivery remain not approved without separate exact gates.

Phase 8 private RC Telegram bot live preview review/runbook prepared on
2026-06-24 as docs-only. Review:
`docs/AMN2_PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE_REVIEW.ru.md`. Runbook:
`docs/AMN2_PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_RUNBOOK.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-telegram-bot-live-preview-review-runbook-2026-06-24.md`.
Future exact gate: `PRIVATE_RC_TELEGRAM_BOT_LIVE_PREVIEW_GATE`. Review result:
`review_go=true`, `gate_open_go=conditional-go-with-explicit-operator-approval`,
`operator_can_open_gate_now=true`. The plan records target VPS
`89.185.80.166`, expected AMN2 head
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`, allowed Telegram actions, two-admin
operator boundary, DB mutation boundary for admin test chats only, config
delivery stop-lines, controlled polling start/stop criteria, public exposure
closed criteria, pass/fail criteria and copy/paste gate text. No live VPS/SSH
command, Telegram polling, Telegram live send, config generation/delivery,
public exposure, package apply, service restart, restore/import/reboot,
provider rebuild, production peer/user mutation or secret-bearing output was
performed.

Phase 8 fresh Android phone post-RC recheck review/runbook prepared on
2026-06-22 as docs-only. Review:
`docs/AMN2_FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW.ru.md`. Runbook:
`docs/AMN2_FRESH_ANDROID_PHONE_POST_RC_RECHECK_RUNBOOK.ru.md`. Evidence:
`research/amn2/phase-8-fresh-android-phone-post-rc-recheck-review-runbook-2026-06-22.md`.
The future exact gate is `FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE`. Review
result: `review_go=true`,
`gate_open_go=conditional-no-go-until-android-phone-available`,
`operator_can_open_gate_now=false`. The plan records target VPS
`89.185.80.166`, expected AMN2 head
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`, private handoff boundary
`C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF`, Android phone readiness inputs,
import/connect/traffic pass criteria, server-side observation criteria,
stop-lines and copy/paste gate text for the moment when the phone is physically
available. No live VPS/SSH command, config generation/delivery, Telegram live
send, public exposure, package apply, service restart, restore/import/reboot,
provider rebuild, production peer/user mutation or secret-bearing output was
performed.

Phase 8 helper style hardening завершен 2026-06-22 как local-only. Документ:
`docs/AMN2_HELPER_STYLE_HARDENING.ru.md`. Безопасный шаблон helper-а:
`docs/templates/amn2_safe_gate_helper_template.ps1`. Evidence:
`research/amn2/phase-8-helper-style-hardening-2026-06-22.md`. Шаг переводит
session 0 helper issues в обязательные правила: PowerShell helper prompts
должны быть ASCII-only, либо `.ps1` должен быть UTF-8 with BOM; interpolated
probe URLs должны использовать `${TargetIp}:PORT` или `$($TargetIp):PORT`;
перед выдачей helper-а оператору обязательны parse check и probe URL dry
inspection. Live VPS/SSH command, package apply, service restart, public
exposure, config delivery, Telegram live send, bot polling,
restore/import/reboot, provider rebuild, production peer/user mutation и
secret-bearing output не выполнялись. Recommended next state остается
`ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`; practical next state при появлении Android phone
остается `FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW`.

Phase 8 private RC next-chat sync completed on 2026-06-22 as docs-only.
Handoff: `docs/NEXT_CHAT_AMN2_PRIVATE_RC_SESSION_0.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-next-chat-sync-2026-06-22.md`. It prepares a
short next-chat starting point after `PRIVATE_RC_OPERATOR_RUN_GATE` and session
0 closeout, with latest heads, final `passed-read-only` status, proven/unproven
scope, stop-lines and next exact gates menu. No live VPS/SSH command, package
apply, service restart, public exposure, config delivery, Telegram live send,
bot polling, restore/import/reboot, provider rebuild, production peer/user
mutation or secret-bearing output was performed. Recommended default next step:
`ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`; recommended practical next step if Android phone is
available: `FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW`.

Phase 8 private RC session 0 closeout completed on 2026-06-22 as docs-only.
Closeout: `docs/AMN2_PRIVATE_RC_SESSION_0_CLOSEOUT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-session-0-closeout-2026-06-22.md`. It closes
the first private/operator RC session 0 as `passed-read-only`, records what was
proven by `PRIVATE_RC_OPERATOR_RUN_GATE`, what remains unproven, helper issues
for future scripts and the next exact gates menu. No live VPS/SSH command,
package apply, service restart, public exposure, config delivery, Telegram
live send, bot polling, restore/import/reboot, provider rebuild, production
peer/user mutation or secret-bearing output was performed in the closeout step.
Recommended next step: `PRIVATE_RC_NEXT_CHAT_SYNC`.

Phase 8 `PRIVATE_RC_OPERATOR_RUN_GATE` passed on 2026-06-22 as the first
private/operator RC session 0 read-only run. Result:
`docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_RESULT.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-operator-run-gate-result-2026-06-22.md`.
Target VPS `89.185.80.166` matched, source overlay matched AMN2
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`, loopback web health returned
`200`, API listener was not running and was not started, public listener guard
passed, Telegram `getMe` passed for `@NeobyatnayaAMNZ_bot`, and corrected
external probes to `3030`, `3040`, `80`, and `443` returned `000`.
No package apply, service restart, public exposure, config generation/delivery,
Telegram live send, bot polling, restore/import/reboot, provider rebuild,
production peer/user mutation or secret-bearing output was performed. Helper
issues were recorded for future scripts: Windows PowerShell UTF-8-without-BOM
mojibake and `$TargetIp:PORT` interpolation causing malformed probe URLs until
rerun with `${TargetIp}`.

Phase 8 private RC operator run gate review completed on 2026-06-22 as
docs-only. Review:
`docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_REVIEW.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-operator-run-gate-review-2026-06-22.md`.
The review checks the `PRIVATE_RC_OPERATOR_RUN_GATE` proposal for target VPS,
expected AMN2 head, allowed actions, stop-lines, private inputs readiness and
pass/fail criteria. Result: `review_go=true`, `gate_open_go=conditional-go`,
`operator_run_gate_opened=false`. Opening the gate still requires explicit
operator request plus private input confirmation at run time. No live VPS/SSH
command, destructive action, package apply, service restart, public exposure,
config delivery, Telegram live send, bot polling, restore/import/reboot,
provider mutation, production peer/user mutation or secret-bearing output was
performed.

Phase 8 private RC session 0 plan plus operator run gate proposal prepared on
2026-06-22 as docs-only. Plan:
`docs/AMN2_PRIVATE_RC_SESSION_0_PLAN.ru.md`. Proposal:
`docs/AMN2_PRIVATE_RC_OPERATOR_RUN_GATE_PROPOSAL.ru.md`. Evidence:
`research/amn2/phase-8-private-rc-session-0-plan-and-gate-proposal-2026-06-22.md`.
This prepares the first private/operator RC session and a future exact
`PRIVATE_RC_OPERATOR_RUN_GATE` with pass criteria, stop-lines and copy/paste
gate text. The gate was not opened. No live VPS/SSH command, destructive
action, package apply, service restart, public exposure, config delivery,
Telegram live send, bot polling, restore/import/reboot, provider mutation,
production peer/user mutation or secret-bearing output was performed. Next
recommended operator choice: review the proposal or explicitly open
`PRIVATE_RC_OPERATOR_RUN_GATE`.

Phase 8 wait-for-operator-request state activated on 2026-06-22 as
`active-wait-operator-request-docs-only`. Wait document:
`docs/AMN2_PRIVATE_OPERATOR_RC_WAIT_OPERATOR_REQUEST.ru.md`. Evidence:
`research/amn2/phase-8-rc-wait-operator-request-2026-06-22.md`. This records
the Russian operator command `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`: use existing Phase 8
evidence only, open nothing live/destructive/config/Telegram/public, and do
the next action only after an explicit named gate from the operator. No live
VPS/SSH command, destructive action, package apply, service restart, public
exposure, config delivery, Telegram live send, bot polling, restore/import/
reboot, provider mutation, production peer/user mutation or secret-bearing
output was performed.

Phase 8 explicit wait state activated on 2026-06-22 as
`active-wait-exact-named-gate-docs-only`. Wait document:
`docs/AMN2_PRIVATE_OPERATOR_RC_WAIT_EXACT_GATE.ru.md`. Evidence:
`research/amn2/phase-8-rc-wait-exact-named-gate-2026-06-22.md`. This records
the Russian operator command `ОЖИДАНИЕ_ТОЧНОГО_ИМЕНОВАННОГО_GATE`: use existing
Phase 8 evidence only, do not open live/destructive/config/Telegram
send/public exposure gates, and keep AMN2 at private/operator RC
`launch-ready-with-explicit-limitations` until the operator explicitly requests
a concrete named gate. No live VPS/SSH command, destructive action, package
apply, service restart, public exposure, config delivery, Telegram live send,
bot polling, restore/import/reboot, provider mutation, production peer/user
mutation or secret-bearing output was performed.

Phase 8 private/operator RC ready hold activated on 2026-06-22 as
`active-private-operator-rc-ready-hold-docs-only`. Hold document:
`docs/AMN2_PRIVATE_OPERATOR_RC_READY_HOLD.ru.md`. Evidence:
`research/amn2/phase-8-rc-ready-hold-2026-06-22.md`. AMN2 is held at
`phase8_final_status=launch-ready-with-explicit-limitations` with
`private_operator_rc_launch_ready=true`, `public_launch_status=not-approved`
and `remaining_blockers_inside_listed_limitations=none`. No live VPS/SSH
command, destructive action, package apply, service restart, public exposure,
config delivery, Telegram live send, bot polling, restore/import/reboot,
provider mutation, production peer/user mutation or secret-bearing output was
performed. Exit from hold requires a fresh exact named gate.

Phase 8 private/operator RC closeout completed on 2026-06-22 as
`completed-private-operator-rc-closeout-docs-only`. Closeout:
`docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md`. Evidence:
`research/amn2/phase-8-rc-closeout-2026-06-22.md`. It uses existing Phase 8
evidence only and records final private/operator RC status, pushed heads at
closeout start, package index, next-chat starting point, explicit limitations
and `remaining_blockers_inside_listed_limitations=none`. It carries forward
`phase8_final_status=launch-ready-with-explicit-limitations`,
`private_operator_rc_launch_ready=true`, `public_launch_status=not-approved`
and `blocked_with_exact_remaining_blockers=false`. No live VPS/SSH command,
destructive action, package apply, public exposure, config delivery, Telegram
live send, bot polling, restore/import/reboot, provider mutation, production
peer/user mutation or secret-bearing output was performed in the closeout
step. Next recommended state is `P8-RC-READY-HOLD` unless the operator opens a
fresh exact named gate for broader action.

Phase 8 private/operator RC final package completed on 2026-06-22 as
`completed-private-operator-rc-final-package-docs-only`. Final package index:
`docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md`. Evidence:
`research/amn2/phase-8-rc-final-package-2026-06-22.md`. It uses only existing
Phase 8 evidence and points to the operator handoff, operator run checklist,
evidence list, exact limitations and future exact gates. It carries forward
`phase8_final_status=launch-ready-with-explicit-limitations`,
`private_operator_rc_launch_ready=true`, `public_launch_status=not-approved`
and `blocked_with_exact_remaining_blockers=false`. No live VPS/SSH command,
destructive action, package apply, public exposure, config delivery, Telegram
live send, bot polling, restore/import/reboot, provider mutation, production
peer/user mutation or secret-bearing output was performed in the final package
step. Next recommended docs-only step is `P8-RC-CLOSEOUT`.

Phase 8 private/operator RC run checklist completed on 2026-06-22 as
`completed-private-operator-rc-run-checklist-docs-only`. Checklist:
`docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md`. Evidence:
`research/amn2/phase-8-rc-operator-run-checklist-2026-06-22.md`. It uses only
existing Phase 8 evidence and records what to check before operating, how to
keep public exposure closed, where private handoff artifacts live, Telegram and
config delivery boundaries, backup/restore boundaries and exact future gates
for broader action. No live VPS/SSH command, destructive action, package apply,
public exposure, config delivery, Telegram live send, bot polling,
restore/import/reboot, provider mutation, production peer/user mutation or
secret-bearing output was performed in the checklist step. Next recommended
docs-only step is `P8-RC-FINAL-PACKAGE`.

Phase 8 private/operator RC handoff completed on 2026-06-22 as
`completed-private-operator-rc-handoff-docs-only`. Operator-facing handoff:
`docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md`. Evidence:
`research/amn2/phase-8-rc-handoff-2026-06-22.md`. It carries forward
`phase8_final_status=launch-ready-with-explicit-limitations`,
`private_operator_rc_launch_ready=true`, `public_launch_status=not-approved`
and `blocked_with_exact_remaining_blockers=false`. It records the allowed
private/operator RC scope, exact limitations, stop-lines and future exact gates
for public exposure, Telegram live delivery, config delivery, restore/import DR
and production rollout. No live VPS/SSH command, destructive action, package
apply, public exposure, config delivery, Telegram live send, bot polling,
restore/import/reboot, provider mutation, production peer/user mutation or
secret-bearing output was performed in the handoff step.

Phase 8 `P8-SFINAL` launch readiness freeze completed on 2026-06-22 as
`launch-ready-with-explicit-limitations`. Evidence:
`research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md`.
Final verdict:
`private_operator_rc_launch_ready=true`,
`phase8_final_status=launch-ready-with-explicit-limitations`,
`phase8_launch_gate_status=closed-for-private-operator-rc-with-limitations`,
`public_launch_status=not-approved`, and
`blocked_with_exact_remaining_blockers=false`. This is a private/operator RC
readiness freeze, not a public launch approval. The decision is based on
`P8-C001` fresh Android phone acceptance, `P8-C002` current-head package smoke
for AMN2 `187949b`, and `P8-C003` fresh-from-zero VPS rehearsal on disposable
VPS `89.185.80.166`. Exact limitations remain: `P8-C003` Android acceptance
used an Android projector with browser/app traffic, while Android phone
acceptance remains separate `P8-C001` evidence; public exposure is closed by
default; Telegram `getMe` plus non-polling smoke passed, but Telegram live
send/profile/media mutation and bot polling were not performed; `.conf` is the
release-primary handoff artifact, while QR and full `vpn://` are not
release-primary; iOS DefaultVPN remains experimental/unreliable; backup
create+verify passed but restore/import DR is not proven. No live VPS/SSH
command, destructive action, package apply, public exposure, config delivery,
Telegram live send, restore/import/reboot, provider mutation, production
peer/user mutation or secret-bearing output was performed in `P8-SFINAL`.

Phase 8 `P8-C003` fresh-from-zero VPS rehearsal passed on 2026-06-22 for
disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md`.
The operator opened the exact destructive gate for AMN2
`187949bffb927a0a6d6c1f260fc0bb9ebb972447`; package SHA256
`7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82` matched.
The rehearsal performed destructive clean install of `/opt/amn2`, quarantined
the previous runtime path, applied the `187949b` source overlay, generated fresh
safe env/DB values plus private operator inputs, verified two Telegram bot
admins without printing IDs in evidence, ran loopback web/API smoke, Telegram
`getMe` plus non-polling dispatcher/user-flow smoke, created one fresh Android
projector peer/config through the AMN2 path, privately handed off one `.conf`
outside the workspace, created and verified a backup artifact with mode `600`,
and kept public probes to `3030`, `3040`, `80` and `443` closed as `000`.
Fresh Android projector server observation for peer fingerprint
`d0ab128d6801` showed endpoint `yes`, fresh handshake and counter growth:
`rx_delta=622084`, `tx_delta=9004751`. No `.conf`, QR, `vpn://`, private key,
PSK, token, password or secret-bearing payload was printed; no public exposure,
Telegram live send/profile/media mutation, bot polling, restore/import,
reboot or provider mutation was performed. `P8-C003` used an Android projector
with browser/app traffic, not an Android phone; Android phone acceptance remains
the separate `P8-C001` evidence. Phase 8 launch gate is now
`fresh-from-zero-rehearsal-passed-awaiting-final-freeze`; recommended next gate
is `P8-SFINAL launch readiness freeze`. Private/operator RC distance is roughly
`98_percent` until the final freeze records the exact launch verdict and
limitations.

Phase 8 `P8-C003` readiness confirmation completed on 2026-06-21 as
`completed-readiness-confirmation-go-with-limitation-no-live-action`. Evidence:
`research/amn2/phase-8-p8-c003-readiness-confirmation-2026-06-21.md`.
Telegram token availability was confirmed privately; web/admin credentials
strategy is `new_private_credentials`; safe env strategy is
`generate_fresh_plus_private_inputs`; private handoff path is
`C:\Users\SooL\Documents\AMN2-PRIVATE-HANDOFF`. Android phone is not available
for `P8-C003`; Android projector is available, has browser/app traffic, has no
Telegram, and on-device Telegram is not required because Telegram is separately
smoked server-side through `getMe` plus non-polling dispatcher/user-flow
surface. This is `p8_c003_readiness_status=go-with-limitation`, not launch
readiness and not a destructive approval. No live VPS/SSH command, destructive
clean/install action, package upload/apply, public exposure, Telegram API/live
send, config delivery, restore/import/reboot, provider mutation, production
peer/user mutation or secret-bearing output was performed. Launch remains
`blocked-until-fresh-from-zero-vps-rehearsal` until the operator explicitly
opens `P8-C003`.

Phase 8 `P8-S002` fresh-from-zero preflight ledger completed on 2026-06-21 as
docs-only preparation, and `P8-C003` destructive gate proposal was prepared but
not opened. Evidence:
`research/amn2/phase-8-p8-s002-fresh-from-zero-preflight-ledger-2026-06-21.md`
and
`research/amn2/phase-8-p8-c003-destructive-gate-proposal-2026-06-21.md`.
The ledger records the criticality/size task matrix, package inputs for
AMN2 `187949b`, readiness checklist, pass criteria and stop-lines. The proposal
contains copy/paste operator gate text and future helper confirmation strings
for `P8-C003`. No live VPS/SSH command, destructive clean/install action,
package upload/apply, public exposure, Telegram API/live send, config delivery,
restore/import/reboot, provider mutation, production peer/user mutation or
secret-bearing output was performed. Launch remains
`blocked-until-fresh-from-zero-vps-rehearsal` until the operator explicitly
opens `P8-C003`.

Phase 8 `P8-C002` package/current-head smoke and compatible AWG defaults
persistence gate completed on 2026-06-21 for disposable VPS `89.185.80.166`.
Evidence:
`research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md`.
AMN2 `codex/phase7-current-fixes` was packaged/applied at
`187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults`.
The package/source SHA checks passed, `/opt/amn2` source overlay matched
`187949b`, Android-compatible `CLIENT_AWG_*` defaults were persisted in the
normal runtime/package path, loopback web/API smoke passed, Telegram `getMe`
plus non-polling dispatcher/user-flow smoke passed, backup create+verify passed
with artifact mode `600`, and public probes to `3030`, `3040`, `80` and `443`
remained closed. No `.conf`, private key, PSK, QR, `vpn://`, token,
secret-bearing screenshot or payload was printed into evidence; no public
exposure, Telegram live send, restore/import/reboot or provider mutation was
performed. Latest VPS-applied/package-smoked AMN2 head is now `187949b`.
Phase 8 launch gate status is now
`blocked-until-fresh-from-zero-vps-rehearsal`; private/operator RC distance is
roughly `92_percent`. Next exact gate: `P8-C003 fresh-from-zero VPS rehearsal
gate`.

Phase 8 `P8-C001` fresh per-device Android config acceptance passed
functionally with reconnect sanity on 2026-06-21 for disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md`.
Fresh AMN2 peer/device `2` with public-key fingerprint `594ba96e4f90` was
created/applied through the AMN2 access/dataplane path, privately handed off as
a `.conf` outside the workspace, then accepted on Android AmneziaWG after a
phone OS update and compatible AWG client config render. Final read-only
server observation showed `endpoint_observed=yes`, fresh handshake age `45s`,
and counter growth from `rx=191124/tx=1487651` to
`rx=520504/tx=4609467`. A reconnect sanity observation then showed
`endpoint_observed=yes`, fresh handshake age `18s`, and counter growth from
`rx=5136612/tx=229495265` to `rx=5318584/tx=230151167`. No `.conf`, private
key, PSK, QR, `vpn://`, token, secret-bearing screenshot or payload was printed
into evidence; no public exposure, Telegram live send, destructive install,
restore/import/reboot or provider mutation was performed. Phase 8 launch gate
was then `android-acceptance-unblocked-package-and-persistence-gates-remain`;
that interim blocker was superseded by the successful `P8-C002` package/current
head smoke recorded above.

Phase 7 mobile/dataplane closeout completed on 2026-06-21 as
`completed-mobile-dataplane-observed-old-matched-config-diagnostic-only`.
Evidence:
`research/amn2/phase-7-mobile-dataplane-closeout-c011f2-2026-06-21.md`.
`P7-C011f2` used a corrected read-only AWG parser and showed live `awg0` on UDP
`30001`, server public key fingerprint `0bdc326c396a`, live peer
`a6a551084fad` with fresh handshake and growing transfer counters, and operator
observation that Android connected instantly. The old matched configs from
`C:\temp` are diagnostic proof only and must not become release delivery
artifacts. Phase 8 status is now `phase8-prep-ready`, but launch remains
`blocked-until-fresh-per-device-android-config-acceptance`.

Phase 7 Android acceptance contract was updated locally on 2026-06-21 from the
clean AMN2 worktree
`C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current` at
`471bca8 Downgrade DefaultVPN iOS compatibility`. Evidence:
`research/amn2/phase-7-android-acceptance-contract-471bca8-2026-06-21.md`.
AMN2 now machine-reports Android AmneziaWG as a supported candidate with
`acceptance_status=pending_real_device_acceptance` and
`release_primary_allowed=false`; QR and full `vpn://` are not release-primary;
Windows desktop remains accepted by operator observation only. Focused
verification passed with `9 passed`; syntax verification passed. No live
VPS/SSH, package apply, config delivery, Telegram action, restore/import/reboot,
provider mutation, write execution or secret-bearing output was performed.

Phase 7 `P7-C010f` Windows desktop path acceptance record completed on
2026-06-20 as
`completed-windows-desktop-path-accepted-operator-observation-no-live-action`.
Evidence:
`research/amn2/phase-7-windows-desktop-path-acceptance-2026-06-20.md`.
Operator observation: the previously issued Windows configuration works
clearly on Windows desktop. This confirms the desktop/server base path is not
globally broken, but it does not close mobile acceptance: iPhone DefaultVPN
remains experimental/unreliable, QR remains non-primary, full `vpn://`
one-click copy remains impractical for real payload length, and Android
AmneziaWG is still pending real-device acceptance. No live VPS/SSH, Telegram
action, config/QR/import-link output, restore/import/reboot, provider mutation,
write execution or secret-bearing evidence was performed.

Phase 7 `P7-C010d` iOS/Android client compatibility diagnostic completed on
2026-06-20 as `completed-compatibility-policy-update-no-live-apply`. Evidence:
`research/amn2/phase-7-ios-android-client-compatibility-diagnostic-471bca8-2026-06-20.md`.
AMN2 was advanced to `471bca8 Downgrade DefaultVPN iOS compatibility`:
DefaultVPN iOS is no longer treated as the primary/recommended iOS path and is
marked experimental/unreliable after the P7-C010c real-device failure. Latest
VPS-smoked/package head remains `6d5cf3e` until a new package/apply gate is
opened. Next recommended gate is Android AmneziaWG real-device acceptance.

Phase 7 `P7-C010b/P7-C010c` mobile Telegram UX live acceptance found a
real-device UX blocker on 2026-06-20: one-click copy for the full config import
link is not available/practical, QR did not open/import through the tested
phone flows, and iPhone DefaultVPN failed functional acceptance in the latest
`6d5cf3e` retest: first-connect was slow, reconnect loops appeared after
toggling VPN off/on, and the tunnel did not provide expected connectivity
(`Telegram` stayed unavailable).
Evidence:
`research/amn2/phase-7-mobile-telegram-ux-failure-conf-first-fix-6d5cf3e-2026-06-20.md`.
Root cause: real AMN2 `vpn://` import links are normally too long for Telegram
copy-text buttons, and QR over the custom `vpn://` deep link is not a reliable
camera/client import path. AMN2 was advanced to `6d5cf3e Make Telegram config
delivery conf-first`: `.conf` is now the primary install path, QR is generated
from raw `.conf` payload for in-app VPN scanners, and copy/QR limitations are
explained to the user. `P7-C010c` package/apply smoke for `6d5cf3e` passed on
the disposable VPS, including loopback API smoke, Telegram getMe/non-polling
smoke, backup create+verify and closed public probes. However, real-device
mobile acceptance still failed for QR and iPhone DefaultVPN. Phase 8 should not
start until `P7-C010d` client compatibility diagnostic identifies a reliable
mobile path or an explicit narrower launch policy is accepted.

Phase 7 `P7-C010a` Mobile Telegram UX acceptance plan for AMN2 `c958733` was
completed on 2026-06-20 as
`completed-mobile-telegram-ux-acceptance-plan-no-live-action`. Evidence:
`research/amn2/phase-7-mobile-telegram-ux-acceptance-plan-c958733-2026-06-20.md`.
This adjusts the practical release posture: Phase 7 remains
`rc_ready_paused_private_operator_lane`, but Phase 8 should wait for real-device
Telegram UX acceptance or an explicit documented non-QR fallback policy. The
pending acceptance checks are one-click copy, QR readability on iPhone and
Android, and fallback `.conf` import. No live VPS/SSH command, Telegram token
use/API call/live send, config/QR/import-link payload output, public exposure,
write execution, restore/import/reboot, provider mutation, Local Agent mutation
or secret-bearing output was performed.

Phase 7 S-final next-chat handoff for AMN2 `c958733` was completed on
2026-06-20 as
`completed-s-final-next-chat-handoff-c958733-no-live-action`. Evidence:
`research/amn2/phase-7-s-final-next-chat-handoff-c958733-2026-06-20.md`.
It is the compact starting point for the next chat: current state is
`rc_ready_paused_private_operator_lane`; users are Telegram-first; operator
web/admin remains private by VPS IP plus loopback/SSH tunnel; public exposure,
public API exposure, write execution, restore/import/reboot, provider mutation,
config delivery payload output and Telegram live send/profile/media mutation
remain stop-lines requiring fresh exact named gates.

Phase 7 final RC freeze/status pass for AMN2 `c958733` was completed on
2026-06-20 as
`completed-rc-ready-paused-state-c958733-no-live-action`. Evidence:
`research/amn2/phase-7-final-rc-freeze-status-c958733-2026-06-20.md`. Frozen
state is `rc_ready_paused_private_operator_lane`: latest VPS-smoked/package
head is `c958733`, current VPS source overlay is
`c9587332d425583ed627899d7fa950756b64c4dc`, web/admin remains loopback-only,
public exposure and public API exposure are not opened, `VPS_APPLY_ENABLED=false`,
users are Telegram-first, and operator web/admin remains private by VPS IP plus
loopback/SSH tunnel. No live VPS/SSH command, package upload/apply, service
restart, public exposure, config delivery, write execution, restore/import/
reboot, provider mutation, Local Agent mutation, Telegram action or
secret-bearing output was performed in the freeze pass.

Phase 7 `P7-C009` c958733 package apply + loopback/Telegram/backup smoke was
completed on 2026-06-20 for AMN2
`c9587332d425583ed627899d7fa950756b64c4dc` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-c958733-package-apply-smoke-2026-06-20.md`. Package
`dist/amn2-vps-update-and-smoke-kit-c958733.zip` sha256
`B9C299DE16041570068EAFE77B0ED95F86A56FDB07E85A2D3AA061A5C971DB6A` and source
zip sha256 `E0F2F823CF4E29B52404E634BA11961B3C2B85604C04498CC3D752DD5DAB6E0B`
were verified. Live source overlay updated `/opt/amn2` to `c958733`, loopback
web restart passed, API loopback smoke returned `VPS verdict: pass`, Telegram
`getMe` and non-polling dispatcher/user-flow smoke passed for
`@NeobyatnayaAMNZ_bot`, backup create and verify passed with artifact mode
`600`, and external probes to public `3030`, `3040`, `80` and `443` stayed
`000`. No public exposure, config delivery payload output, write execution,
actual installer executor, restore/import/reboot/download, provider mutation,
Local Agent mutation, Telegram polling/live send/profile/media mutation or
secret-bearing output was performed. Current latest VPS-smoked/package head is
now `c958733`.

Phase 7 Codex Security post-fix validation was completed on 2026-06-20 for
AMN2 `c958733 Harden security-sensitive operations`. Evidence:
`research/amn2/phase-7-codex-security-postfix-c958733-2026-06-20.md`.
AMN2 branch `codex-vps-test-prep` was pushed from `5501295` to
`c9587332d425583ed627899d7fa950756b64c4dc`. Fixed security-sensitive
operations: CLI live peer apply/revoke now requires `VPS_APPLY_ENABLED=true`;
Telegram admin delivery-failure fallback no longer sends secret-bearing config
payloads/import links to admin chat; SMTP `STARTTLS` uses an explicit verifying
SSL context; backup artifacts are chmodded to `0600`; debug snapshot port greps
validate numeric ports and avoid `bash -lc` string execution. Verification:
focused pytest `95 passed`; full pytest `729 passed` with one unrelated
FastAPI/TestClient deprecation warning; Codex Security post-fix scan
`b9106c1d-1f68-493a-91a6-2698303da56e` completed with `0` reportable findings.
No live VPS/SSH, package apply, restart, public exposure, config delivery,
write execution, restore/import/reboot, provider mutation, Local Agent
mutation, Telegram send/profile/media mutation or secret-bearing output was
performed in that security-validation step. The follow-up `c958733` VPS
package/apply smoke was later completed by `P7-C009`.

Phase 7 `P7-C008a` Telegram token reconciliation and user-flow smoke completed
on 2026-06-20 for AMN2 `5501295` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-telegram-token-reconciliation-user-flow-smoke-5501295-2026-06-20.md`.
The earlier `P7-C008` attempt was blocked by an invalid Telegram token, then
`P7-C008a` safely updated the VPS `.env` through operator-secret handoff with a
rollback copy, did not print the token, verified Telegram `getMe`, and
constructed the non-polling bot/user-flow surface. Source overlay matched
`55012958ff6b8338254f3f68dfe6779f4bc56f5d`; web/admin remained loopback-only;
`VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`. No polling, live
Telegram send, identity/profile/media mutation, config delivery payload output,
write execution, public exposure, restore/import/reboot, provider mutation or
secret-bearing output was performed. External probes to public `3030`, `3040`,
`80` and `443` returned `000`.

Phase 7 Telegram-first/operator-web policy was completed on 2026-06-20 as
`completed-docs-only-telegram-first-operator-web-policy`. Evidence:
`research/amn2/phase-7-telegram-first-operator-web-policy-2026-06-20.md`.
Decision: AMN2 private/operator RC does not require public web-admin exposure,
DNS domain, trusted public TLS or reverse-proxy publication. The user-facing RC
channel is Telegram-first; the operator web/admin channel remains operator-only
by VPS IP plus loopback/SSH tunnel or equivalent private access. `P7-C002`
public web exposure is deferred/not required for private/operator RC. `P7-C007`
Telegram identity/profile/media remains deferred. A future Telegram user-flow
smoke should be a separate exact named live Telegram gate, not an implicit
permission from this docs-only policy. No live VPS/SSH command, public
exposure, Telegram token use/API call/live send/profile/media mutation or
secret-bearing output was performed.

Phase 7 `P7-C004d + P7-C006b` post-direct-clean login and backup gate was
completed on 2026-06-20 as
`completed-login-verified-backup-create-verify` for AMN2 `5501295` on
disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-post-direct-clean-login-backup-5501295-2026-06-20.md`.
Loopback admin login passed after the direct clean installer RC: `GET /login`
returned `200`, `POST /login` returned `303`, dashboard after login returned
`200` and the login form was absent. Backup create and verify passed for the
current clean state; artifact stayed on the VPS at
`/opt/amn2/backups/p7-c006b-post-direct-clean-5501295-20260620T061005Z`,
basename `amneziya-backup-20260620T061102Z.tar.enc`, bytes `204900`, sha256
`f8e0591db75e8ec9ce58f4fa9d71972d577e1ec103194d1943a626aa9b156b97`, mode
`644`. External probes to public `3030`, `3040`, `80` and `443` stayed `000`.
No restore/import/reboot, provider mutation, remote backup download, service
restart, public exposure, config delivery, write execution, Local Agent
mutation, production peer/user mutation, Telegram action or secret-bearing
output was performed.

Phase 7 `P7-C004c` direct clean installer execution gate was completed on
2026-06-20 as `completed-direct-clean-install-5501295-loopback-smoke` for AMN2
`5501295` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-direct-clean-installer-5501295-2026-06-20.md`. The
verified `5501295` package/source was uploaded and checked, current `/opt/amn2`
was moved to `/opt/amn2.pre-p7-c004c-20260620T054656Z`, clean `/opt/amn2` was
created, source overlay became
`55012958ff6b8338254f3f68dfe6779f4bc56f5d`, fresh safe `.env` and placeholder
`servers.yml` were written, DB initialization passed, loopback web returned
`/login=200`, and API loopback smoke returned `VPS verdict: pass` with run_id
`20260620T054813Z`. External probes to public `3030`, `3040`, `80` and `443`
stayed `000`. No provider rebuild, reboot, restore/import, remote backup
download, public exposure, config delivery, write API enablement, Local Agent
mutation, production peer/user mutation, Telegram action or secret-bearing
output was performed. This closes the direct clean-installer RC gap for the
current `5501295` head.

Phase 7 final RC freeze/status pass was completed on 2026-06-20 as
`completed-rc-ready-paused-state-no-live-action` for AMN2 `5501295`. Evidence:
`research/amn2/phase-7-final-rc-freeze-status-5501295-2026-06-20.md`.
The frozen state is `rc_ready_paused_private_operator_lane`: latest
VPS-smoked/package head is `5501295 Add P7 install write contour`, current VPS
source overlay is `5501295`, web/admin remains loopback-only on
`127.0.0.1:3030`, public exposure is not opened, `VPS_APPLY_ENABLED=false`,
the scoped `install:write` contour is audit-only/blocked by apply-disabled,
current-state backup create+verify is complete, known-device operator-local
private config handoff is complete for devices 1 and 2, and `P7-C007` Telegram
identity/profile/media is deferred as not required for private RC. No live
VPS/SSH command, package apply, restart, public exposure, config delivery,
write execution, restore/import/reboot, provider mutation, Local Agent
mutation, Telegram action or secret-bearing output was performed in the freeze
pass. Remaining approved work is residual `P7-C006`
restore/import/download/reboot/DR/provider-restore scope only, plus watch-only
intake.

Phase 7 `P7-C007` Telegram identity/profile/media decision was completed on
2026-06-20 as
`completed-deferred-not-required-for-private-rc-no-telegram-action`. Evidence:
`research/amn2/phase-7-telegram-defer-private-rc-2026-06-20.md`. Telegram
identity/profile/media mutation is deferred and is not a blocker for the
private/operator RC lane. No Telegram token use, Telegram API call, live bot
send, profile/media mutation, media upload, credential handoff, live VPS/SSH
command or secret-bearing output was performed. Future Telegram identity,
profile or media work would require a new exact named gate. Remaining approved
Phase 7 work is residual `P7-C006`
restore/import/download/reboot/DR/provider-restore scope only, plus watch-only
intake.

Phase 7 `P7-C006` current-state backup-only evidence gate was completed on
2026-06-20 as
`completed-current-state-backup-only-create-verify-no-restore-import-reboot`
for AMN2 `5501295` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-current-state-backup-only-5501295-2026-06-20.md`.
Source overlay matched `5501295`; DB aggregate counts were users `0`, devices
`0`, servers `1`, API tokens `8`, admin actions `14`; backup create and verify
passed; artifact stayed on the VPS at
`/opt/amn2/backups/p7-c006-current-state-5501295-20260620T050111Z`, basename
`amneziya-backup-20260620T050141Z.tar.enc`, bytes `218552`, sha256
`1412e6791ba03e0f955d46e988357274a413d0afc96a2e72c1b6077624554bb2`, mode
`600`. External probes to `3030`, `3040`, `80` and `443` stayed `000`. No
restore/import/reboot, provider mutation, remote backup download, service
restart, public exposure, config delivery, write execution, Local Agent
mutation, Telegram action or secret-bearing output was performed. Remaining
Phase 7 exact gates are residual `P7-C006` restore/import/download/reboot/DR/
provider-restore scopes only, plus watch-only intake.

Phase 7 `P7-C006a + watch-only status hygiene` was completed on 2026-06-20 as
`completed-provider-console-evidence-inconclusive-watch-hygiene-no-mutation`.
Evidence:
`research/amn2/phase-7-provider-backup-restore-point-watch-hygiene-2026-06-20.md`.
The operator-provided provider-console screenshot for VPS `89.185.80.166`
showed successful backup creation, failed move to internal storage and
successful backup deletion on 2026-06-15, so provider restore-point availability
is not confirmed and must not be used as a restore prerequisite. No provider
mutation, restore/import/reboot, remote backup download, live VPS/SSH command or
secret-bearing output was performed. Watch-only release check still observes
`amnezia-client 4.8.19.0` and `amneziawg-android 2.0.1`; these remain
signals-only and do not authorize live/config/write/restore/Telegram actions.

Phase 7 `P7-C005` write API / install mutation gate was completed on
2026-06-20 as `completed-scoped-write-contour-smoked` for AMN2
`55012958ff6b8338254f3f68dfe6779f4bc56f5d` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-write-install-mutation-contour-5501295-2026-06-20.md`.
AMN2 branch `codex-vps-test-prep` was advanced from `b121865` to `5501295`
(`Add P7 install write contour`) and pushed. Local full suite returned
`726 passed, 1 StarletteDeprecationWarning`. Package
`dist/amn2-vps-update-and-smoke-kit-5501295.zip` sha256
`C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407` and source
zip sha256 `DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3`
were verified. Live apply updated `/opt/amn2` source overlay to `5501295`,
loopback web restart passed, baseline API loopback smoke returned `VPS verdict:
pass`, and the scoped write route smoke passed: `server:read` token got `403`,
`install:write` token got `202`, route status was
`recorded_blocked_by_vps_apply_disabled`, audit action was `api_write`, audit
metadata was secret-safe, and external probes to `3030`, `3040`, `80` and
`443` stayed `000`. The route is audit-only while `VPS_APPLY_ENABLED=false`;
no actual installer executor, public exposure, config delivery,
restore/import/reboot, Local Agent mutation, Telegram action or secret-bearing
output was performed. This was later followed by current-state `P7-C006`
backup-only evidence and the `P7-C007` private-RC deferral decision. Remaining
approved Phase 7 live/mutation work is residual `P7-C006` scope only;
`P7-C006a` provider restore-point confirmation was later closed as inconclusive
docs-only evidence.

Phase 7 `P7-C005 + P7-C006 + P7-C007` post-clean read-only rebaseline was
completed on 2026-06-19 as
`completed-post-clean-read-only-rebaseline-no-mutation` for AMN2 `b121865` on
disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-post-clean-write-backup-telegram-read-only-rebaseline-b121865-2026-06-19.md`.
The clean `P7-C004b` install remained active with source overlay
`b121865f488821f6fc471c9529fb26e5d7992515`, web loopback on
`127.0.0.1:3030`, no public API listener on `3040`, no public `80/443`
listeners and external probes to `3030`, `3040`, `80` and `443` returning
`000`. Public API route inventory is read-only with `write_api_route_count=0`;
DB aggregate counts after clean install are users `0`, devices `0`, servers
`1`, API tokens `2` and admin actions `6`. Backup help probing was safe, no
backup was created, and Telegram token presence was checked without token use
or Telegram API call. No write API enablement, install mutation,
backup/restore/import/reboot, remote backup download, service restart, public
exposure, config delivery, Local Agent mutation, production peer/user mutation,
Telegram action or secret-bearing output was performed. This was later
superseded for `P7-C005` by the 2026-06-20 scoped write contour and for
`P7-C007` by the private-RC deferral decision; residual `P7-C006` scopes require
exact named gates only. Provider restore-point confirmation `P7-C006a` was
later completed as inconclusive docs-only evidence.

Phase 7 `P7-C004b` destructive clean installer execution was completed on
2026-06-19 as `completed-clean-install-loopback-smoke` for AMN2 `b121865` on
disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-destructive-clean-installer-execution-b121865-2026-06-19.md`.
The operator opened the exact destructive gate and entered the final
destructive phrase. The old `/opt/amn2` was moved to
`/opt/amn2.pre-p7-c004b-20260619T173819Z`, clean `/opt/amn2` was installed from
the verified `b121865` package/source, `.env` and `servers.yml` were
regenerated without secret output, DB initialization passed, loopback web
returned `/login=200`, API loopback smoke returned `VPS verdict: pass`, and
external probes to `3030`, `3040`, `80` and `443` stayed `000`. No provider
rebuild, reboot, restore/import, remote backup download, public exposure,
config delivery, write API, Local Agent mutation, production peer/user
mutation, Telegram action or secret-bearing output was performed. This was
later followed by `P7-C005` scoped write contour completion, current-state
`P7-C006` backup evidence and the `P7-C007` private-RC deferral decision;
residual `P7-C006` scopes remain exact named gates only.

Phase 7 `P7-C004a` destructive clean installer pre-cutover guard was completed
on 2026-06-19 as `ready-for-final-destructive-stop-line-no-apply` for AMN2
`b121865` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-destructive-clean-installer-precutover-guard-b121865-2026-06-19.md`.
Local package/source checksums matched, remote source overlay matched `b121865`,
the `P7-C006` backup artifact was present with matching sha256 and
`pre_cutover_blocker_count=0`. No wipe, reinstall, package apply, service
restart, provider action, restore/import/reboot, public exposure, write API,
Local Agent mutation, production peer/user mutation, Telegram action or
secret-bearing output was performed.

Phase 7 `P7-C006` backup-only evidence gate was completed on 2026-06-19 as
`completed-backup-only-create-verify-no-restore-import-reboot` for AMN2
`b121865` on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-backup-only-evidence-b121865-2026-06-19.md`. Backup
create and verify passed after diagnosing env propagation for `APP_SECRET_KEY`;
the backup artifact stayed on the VPS and was not downloaded. No restore apply,
archive import, reboot, destructive migration, public exposure, write API,
Local Agent mutation, production peer/user mutation, Telegram action or
secret-bearing output was performed.

Phase 7 watch-only intake cycle closeout was completed on 2026-06-19 as
`completed-watch-only-intake-cycle-complete-no-live-action`. Evidence:
`research/amn2/phase-7-watch-only-intake-cycle-complete-2026-06-19.md`.
Current observed client signals remain `amnezia-client 4.8.19.0` and
`amneziawg-android 2.0.1`; no live action, mutation, upstream/GPL code copy or
new implementation task was created.

Phase 7 watch-only intake after critical preflights was completed on 2026-06-19
as `completed-watch-only-intake-after-critical-preflights-no-live-action`.
Evidence:
`research/amn2/phase-7-watch-only-intake-after-critical-preflights-2026-06-19.md`.
No live action, mutation, secret-bearing output or new implementation task was
created.

Phase 7 `P7-C005 + P7-C006 + P7-C007` write/backup/Telegram read-only preflight
was completed on 2026-06-19 as `completed-read-only-preflight-no-mutation`.
Evidence:
`research/amn2/phase-7-write-backup-telegram-read-only-preflight-2026-06-19.md`.
This pass reviewed existing local readiness evidence only; no live VPS command,
SSH command or external API call was run. At that time `P7-C005` was still
blocked by RC policy, public write routes disabled, `VPS_APPLY_ENABLED=false`
and `LOCAL_AGENT_ENABLED=false`; this was later superseded by the 2026-06-20
scoped write contour on `5501295`. `P7-C006` remains blocked for live backup,
restore apply, archive import, remote backup download and reboot. At that time
`P7-C007` was blocked for Telegram token use, live bot send, profile/media
mutation and media upload; it was later deferred as not required for private RC.
No backup archive create, restore/import apply, Telegram action, secret
publication or upstream/GPL code copy was performed.

Phase 7 `P7-C003` target-specific operator-local private handoff for
`TARGET_USER_ID=1` / `TARGET_DEVICE_ID=2` was completed on 2026-06-19 as
`completed-private-file-copied-secret-not-printed` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-config-delivery-private-handoff-device2-b121865-2026-06-19.md`.
The config was rendered on the VPS to a root-only temp file, copied by SCP to the
operator-selected local private destination outside the workspace and removed
from the VPS. Remote/local metadata matched: `artifact_bytes=438`, sha256
`87b5a41c665b593b72740b00422416ef73dc0d7a58ca928ea52c6722c0e5cbb3`. No config
payload, `.conf` contents, QR, `vpn://` payload, client private key, PSK, raw
token, cookie, authorization header, `.env`, `servers.yml` or rollback file was
printed or attached to evidence. No SMTP/Telegram send, public config link
issue/redeem, write API enablement, install mutation, Local Agent mutation,
`.env` mutation, service restart, public exposure, secret publication or
upstream/GPL code copy was performed. Together with the earlier
`TARGET_DEVICE_ID=1` handoff, both known active target devices from the
2026-06-19 inventory have completed private-file handoff. Resend/revocation,
SMTP/Telegram delivery, public/self-service links and new target devices remain
separate exact gates.

Phase 7 `P7-C003` target-specific operator-local private handoff for
`TARGET_USER_ID=1` / `TARGET_DEVICE_ID=1` was completed on 2026-06-19 as
`completed-private-file-copied-secret-not-printed` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-config-delivery-private-handoff-device1-b121865-2026-06-19.md`.
The config was rendered on the VPS to a root-only temp file, copied by SCP to the
operator-selected local private destination outside the workspace and removed
from the VPS. Remote/local metadata matched: `artifact_bytes=438`, sha256
`7ca64dd57a7467c4817e846a11d56d861013921c1db3f6ac020f7ca355dfdb83`. No config
payload, `.conf` contents, QR, `vpn://` payload, client private key, PSK, raw
token, cookie, authorization header, `.env`, `servers.yml` or rollback file was
printed or attached to evidence. No SMTP/Telegram send, public config link
issue/redeem, write API enablement, install mutation, Local Agent mutation,
`.env` mutation, service restart, public exposure, secret publication or
upstream/GPL code copy was performed. `TARGET_DEVICE_ID=2`, resend/revocation,
SMTP/Telegram delivery and public/self-service links remain separate exact
gates.

Phase 7 `P7-C003` target inventory for operator-local handoff was completed on
2026-06-19 as `completed-read-only-target-inventory-no-delivery` on disposable
VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-config-delivery-target-inventory-b121865-2026-06-19.md`.
Source overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`.
Runtime stayed loopback-only; `/login=200`, `/=303`, and external probes to
`3030`, `3040`, `80` and `443` returned `000`. Safe inventory found one active
user and two active devices: valid next target pairs are
`TARGET_USER_ID=1 TARGET_DEVICE_ID=1` and
`TARGET_USER_ID=1 TARGET_DEVICE_ID=2`; both devices have
`config_material_status=available` and `config_version=amneziawg_v2`. No config
delivery, `.conf`/QR/`vpn://` output, client secret output, SMTP/Telegram send,
public config link issue/redeem, write API enablement, install mutation, Local
Agent mutation, `.env` mutation, service restart, public exposure, secret
publication or upstream/GPL code copy was performed.

Phase 7 `P7-C003` operator-local config delivery guard was opened by the
operator and completed on 2026-06-19 as
`blocked-pending-target-and-private-handoff-no-delivery` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-config-delivery-operator-local-guard-b121865-2026-06-19.md`.
Source overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`.
Channel is now selected as `operator-local`. Loopback web checks returned
`/login=200` and `/=303`; external probes to `3030`, `3040`, `80` and `443`
returned `000`. Safe route inventory found five config-related web/admin routes;
DB aggregate counts showed `users_count=1`, `devices_count=2`, `servers_count=1`.
Delivery remains blocked until exact target user/device, private artifact
destination and one-time delivery/revocation policy are selected. No config
delivery, `.conf`/QR/`vpn://` output, client secret output, SMTP/Telegram send,
public config link issue/redeem, write API enablement, install mutation, Local
Agent mutation, `.env` mutation, service restart, public exposure, secret
publication or upstream/GPL code copy was performed.

Phase 7 `P7-C003 + P7-C005` config/write read-only preflight was completed on
2026-06-19 as `completed-read-only-preflight-blocked-no-delivery-no-write`.
Evidence:
`research/amn2/phase-7-config-write-read-only-preflight-2026-06-19.md`.
This pass used local docs/evidence/package notes only; no live VPS/SSH command
was run. At that time `P7-C003` was blocked because the delivery channel
decision was missing, SMTP config / attachment policy were not ready and no
secret-safe operator-local delivery policy was selected. The later `P7-C003`
operator-local guard selected `operator-local` as the current channel but left
real delivery blocked pending target/private handoff. At that time `P7-C005`
was still blocked by read-only RC policy, prior `write_api_route_count=0`,
`VPS_APPLY_ENABLED=false` and `LOCAL_AGENT_ENABLED=false`; this was later
superseded by the 2026-06-20 scoped write contour on `5501295`. No config delivery,
`.conf`/QR/`vpn://` output, SMTP/Telegram config send, tokenized redeem, write
API enablement, install mutation, Local Agent mutation, peer/user mutation,
secret publication or upstream/GPL code copy was performed.

Phase 7 `P7-C002d` IP-only public exposure risk guard was opened by the operator
and completed on 2026-06-19 as
`blocked-pending-design-or-explicit-risk-acceptance-not-exposed` on disposable
VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-ip-only-public-exposure-risk-guard-b121865-2026-06-19.md`.
Source overlay marker confirmed `b121865f488821f6fc471c9529fb26e5d7992515`.
Runtime stayed loopback-only on `127.0.0.1:3030`; public `3040/80/443`
listeners were absent. Safe env flags: admin/session secrets present, public URL
fields missing, `VPS_APPLY_ENABLED=false`, `LOCAL_AGENT_ENABLED=false`.
Blockers: `ufw_inactive_for_public_exposure`,
`no_reverse_proxy_binary_for_admin_exposure`,
`ip_only_public_admin_has_no_trusted_dns_tls` and
`public_admin_over_ip_requires_explicit_risk_acceptance`.
`ip_only_public_apply_allowed=false`. No service restart, `.env` mutation,
package install, reverse proxy/TLS/firewall apply, public listener change,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 watch-only intake current signals was refreshed on 2026-06-19 as
docs-only/watch-only work. Evidence:
`research/amn2/phase-7-watch-only-intake-current-signals-2026-06-19.md`.
Current official watch remains `amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1`. PRVTPRO remains upstream idea source only with no
GPL code copy; KYORESUAS remains API taxonomy signal only. Local automation
configs for `prvtpro-weekly-upstream-refresh`, `weekly-kyoresuas-upstream-refresh`
and `amnezia-weekly-upstream-refresh` remain present and unchanged since
2026-06-14; no new local automation output was found. No new AMN2
implementation task was created. No live VPS command, SSH command, `.env`
mutation, package install, service restart, reverse proxy/TLS/firewall apply,
public listener change, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed.

Phase 7 `P7-C002e + watch-only` Public URL env reconciliation gate was opened
by the operator and completed on 2026-06-19 as `completed-live-env-reconcile-not-exposed`
on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-public-url-env-reconciliation-b121865-2026-06-19.md`.
Remote source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`.
`PUBLIC_BASE_URL`, `PUBLIC_DOMAIN` and `WEB_PUBLIC_BASE_URL` were removed from
live `.env`; safe summary shows each removed once. A rollback copy was created
on the VPS and must not be posted because it contains secrets. Post-state safe
flags: `APP_SECRET_KEY=present`, `WEB_ADMIN_USERNAME=present`,
`WEB_ADMIN_PASSWORD_HASH=present`, `WEB_ADMIN_SESSION_SECRET=present`,
`PUBLIC_BASE_URL=missing`, `PUBLIC_DOMAIN=missing`,
`WEB_PUBLIC_BASE_URL=missing`, `VPS_APPLY_ENABLED=false`,
`LOCAL_AGENT_ENABLED=false`. Runtime stayed loopback-only: loopback `/login=200`,
root `/=303`, listener `127.0.0.1:3030`, no listener on `3040`; external probes
to `3030`, `3040`, `80` and `443` returned `000`. No service restart, reverse
proxy, TLS, firewall, public listener, public web/API exposure, config delivery,
write API, Local Agent mutation, backup/import/reboot, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
The settings probe `app.settings` failure is classified as a verifier-path issue:
remote package has no `app.settings`; runtime probes passed.

Phase 7 watch-only intake current signals was completed on 2026-06-18 as
docs-only/watch-only work. Evidence:
`research/amn2/phase-7-watch-only-intake-current-signals-2026-06-18.md`.
Current official watch remains `amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1`. PRVTPRO remains upstream idea source only with no
GPL code copy; KYORESUAS remains API taxonomy signal only. Local automation
configs for `prvtpro-weekly-upstream-refresh`, `weekly-kyoresuas-upstream-refresh`
and `amnezia-weekly-upstream-refresh` remain present and unchanged since
2026-06-14; no new local automation output was found. No new AMN2
implementation task was created. No live VPS command, SSH command, `.env`
mutation, package install, service restart, reverse proxy/TLS/firewall apply,
public listener change, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed.

Phase 7 watch-only intake correction was completed on 2026-06-18 as
docs-only/watch-only work. Evidence:
`research/amn2/phase-7-watch-only-intake-correction-2026-06-18.md`. This pass
corrects the watch-only/status hygiene wording that previously recorded obsolete
`amneziawg-android 2.0.0`. Current official GitHub watch keeps
`amnezia-vpn/amnezia-client` `4.8.19.0` and
`amneziawg-android` `2.0.1` as watch-only client compatibility signals. No live
VPS command, SSH command, `.env` mutation, package install, service restart,
reverse proxy/TLS/firewall apply, public listener change, public exposure,
config delivery, write API, Local Agent mutation, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 `P7-S005 + P7-I012` docs quality audit and IP-only env reconciliation
planning was completed on 2026-06-18 as docs-only/status work. Evidence:
`research/amn2/phase-7-docs-quality-audit-ip-env-reconcile-2026-06-18.md`.
The audit corrected two navigation risks from recent Phase 7 edits: the current
workspace is AMN3 evidence repo `barakov-dot/amn3` on latest pushed `master`,
while AMN2 package/source truth remains `barakov-dot/amn2`
`codex-vps-test-prep` at `b121865`; and public URL fields left in live `.env`
by `P7-C002a` are now explicitly treated as inert prerequisite residue after
the later IP-only policy decision. New inactive proposal:
`P7-C002e Public URL env reconciliation gate`, important gated, live `.env`
hygiene only, no public listener/reverse proxy/TLS/firewall/config delivery.
No live VPS command, SSH command, `.env` mutation, package install, service
restart, reverse proxy/TLS/firewall apply, public listener change, public
exposure, config delivery, write API, Local Agent mutation, backup/import/
reboot, destructive action, Telegram action, secret publication or upstream/GPL
code copy was performed.

Phase 7 watch-only intake + status hygiene was completed on 2026-06-18 as
docs-only/watch-only work. Evidence:
`research/amn2/phase-7-watch-only-intake-status-hygiene-2026-06-18.md`. Current
official GitHub watch keeps `amnezia-vpn/amnezia-client` `4.8.19.0` as a client
compatibility signal. Its temporary `amneziawg-android 2.0.0` wording is
superseded by the later correction evidence, and current status/navigation keeps
`amneziawg-android 2.0.1` as latest. PRVTPRO remains upstream idea source
only with no GPL code copy; KYORESUAS remains API taxonomy signal only. Local
automation configs remain present and watch-only; no new automation-generated
output newer than the 2026-06-14 Phase 7 intake evidence was found in the local
workspace. `P7-I011` remains canonical: AMN2 uses VPS IP + SSH tunnel to
loopback web/admin by default, without DNS-domain trusted TLS cutover. No live
VPS command, SSH command, `.env` mutation, package install, service restart,
reverse proxy/TLS/firewall apply, public listener change, public exposure,
config delivery, write API, Local Agent mutation, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 `P7-I011` IP-only exposure policy decision was completed on 2026-06-18
as local-only/docs/status work. Evidence:
`research/amn2/phase-7-ip-only-exposure-policy-decision-2026-06-18.md`. The
operator explicitly decided not to use a DNS domain for AMN2 and to use only the
VPS IP. Therefore `P7-C002c` DNS/domain/trusted TLS prerequisite is closed as
`operator_declined_dns_domain`. The selected default access policy is VPS IP for
SSH/operator targeting plus loopback web/admin `127.0.0.1:3030` through SSH
tunnel. Public web/admin exposure, trusted TLS cutover, reverse proxy, firewall,
public listener, public API, config delivery and write API remain not opened.
Any future IP-only public web/admin exposure requires a separate exact named
risk-acceptance gate. No live VPS command, SSH command, `.env` mutation, package
install, service restart, reverse proxy/TLS/firewall apply, public listener
change, config delivery, write API, Local Agent mutation, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 `P7-N005` client compatibility watch refresh for Amnezia client
`4.8.19.0` was activated from the requested `P7-C002c + P7-N005` pair and
completed on 2026-06-18 as local-only/docs/tests/watch-only work. Evidence:
`research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`.
`P7-C002c` was not executed live because an exact named live prerequisite gate
and operator-provided DNS FQDN were not supplied; this state was later
superseded by `P7-I011` operator no-domain policy. Current official GitHub
watch keeps `amnezia-vpn/amnezia-client` release `4.8.19.0` as the latest
client-compatibility signal; a later watch-only/status hygiene pass corrected
current `amneziawg-android` wording, and the latest correction keeps `2.0.1`. No
config artifact, QR, `vpn://`, SMTP delivery, public redeem
route, client-secret output or Telegram config send was enabled. No live VPS
command, SSH command, `.env` mutation, reverse proxy/TLS/firewall apply, public
exposure, config delivery, write API, Local Agent mutation, backup/import/
reboot, destructive action, Telegram action, secret publication or upstream/GPL
code copy was performed.

Phase 7 `P7-C002c + watch-only intake` DNS/domain/TLS prerequisite staging and
watch-only upstream/client intake was completed on 2026-06-18 as
`watch-only-intake-complete-p7-c002c-input-required`. Evidence:
`research/amn2/phase-7-dns-domain-tls-prereq-watch-intake-2026-06-18.md`.
`P7-C002c` was not executed live because an exact named live prerequisite gate
and operator-provided DNS FQDN were not supplied. Local automation configs for
`prvtpro-weekly-upstream-refresh`, `weekly-kyoresuas-upstream-refresh` and
`amnezia-weekly-upstream-refresh` remain active; no new local automation output
newer than the 2026-06-14 Phase 7 intake evidence was found. Current official
GitHub watch saw `amnezia-vpn/amnezia-client` release `4.8.19.0` from
2026-06-15 as a client-compatibility signal only. A later watch-only/status
hygiene pass corrected current `amneziawg-android` latest-release endpoint
observation back to `2.0.1`. No live VPS command, SSH command, `.env` mutation, reverse
proxy/TLS/firewall apply, public exposure, config delivery, write API, Local
Agent mutation, backup/import/reboot, destructive action, Telegram action,
secret publication or upstream/GPL code copy was performed. New inactive
proposal from this pass, `P7-N005` client compatibility watch refresh for
Amnezia client `4.8.19.0`, was later activated and completed in
`research/amn2/phase-7-client-compatibility-watch-refresh-4-8-19-2026-06-18.md`.
The DNS-domain input-required state was later superseded by `P7-I011` operator
no-domain policy.

Phase 7 `P7-C002` public cutover gate for AMN2 `b121865` was opened by the
operator and stopped by read-only guard on 2026-06-18 as
`blocked-by-domain-tls-plan-not-exposed` on disposable VPS `89.185.80.166`.
Evidence:
`research/amn2/phase-7-public-cutover-guard-b121865-2026-06-18.md`. Remote
source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`; web stayed
loopback-only on `127.0.0.1:3030`; loopback `/login` returned `200`; loopback
root returned `303`; external probes to `3030`, `3040`, `80` and `443`
returned `000`. Admin credentials and public URL fields were present, but
`PUBLIC_BASE_URL`/`PUBLIC_DOMAIN` were IP-based; guard blocker:
`trusted_tls_requires_dns_domain_not_ip`. Reverse proxy and certbot tooling were
missing. No package install, service restart, `.env` mutation, reverse proxy
apply, TLS issue, firewall change, public listener change, public web/API
exposure, config delivery, write API enablement, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
`P7-I011` later closed the DNS/domain path by operator policy; `P7-C002d` was
later opened and blocked IP-only exposure. Next default action is
operator-only/watch-only unless a new post-`P7-C002d` risk-design gate is
explicitly opened.

Phase 7 `P7-C002b` public exposure runtime reload and loopback login
verification for AMN2 `b121865` was opened by the operator and completed on
2026-06-18 as `runtime-login-verified-not-exposed` on disposable VPS
`89.185.80.166`. Evidence:
`research/amn2/phase-7-public-exposure-runtime-login-verify-b121865-2026-06-18.md`.
Remote source overlay remains `b121865f488821f6fc471c9529fb26e5d7992515`.
Manual loopback runtime was restarted after `P7-C002a`; the first immediate
HTTP probe hit a short pre-bind readiness window, then recovery showed web
listening on `127.0.0.1:3030`. Final live login flow returned
`GET /login=200`, `POST /login=303`, `Location=/` and dashboard `200`;
password contract check matched the submitted username/password to the live
`.env` hash without printing secrets. External probes to `3030`, `3040`, `80`
and `443` returned `000`. No reverse proxy apply, TLS issue, firewall change,
public listener change, public web/API exposure, config delivery, write API
enablement, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `P7-C002` remains a critical named gate
for a separate exact public cutover gate only.

Phase 7 `P7-C002a` public exposure admin/domain prerequisite for AMN2 `b121865`
was opened by the operator and completed on 2026-06-14 as live `.env`
admin/domain prerequisite mutation on disposable VPS `89.185.80.166`. Evidence:
`research/amn2/phase-7-public-exposure-admin-domain-prereq-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`.
Pre-mutation flags showed `WEB_ADMIN_USERNAME=missing`, public base/domain URL
missing and `WEB_ADMIN_PASSWORD_HASH=present`. The gate updated only `.env`
admin/domain fields; post-mutation flags showed `WEB_ADMIN_USERNAME=present`,
`WEB_ADMIN_PASSWORD_HASH=present`, `PUBLIC_BASE_URL=present`,
`PUBLIC_DOMAIN=present`, `WEB_PUBLIC_BASE_URL=present`, `VPS_APPLY_ENABLED=false`
and `LOCAL_AGENT_ENABLED=false`. Verdict:
`public_exposure_precondition_status=ready_for_operator_cutover_plan`, with
`public_exposure_apply_allowed=false`. No service restart, reverse proxy apply,
TLS certificate issue, firewall change, public listener change, public web/API
exposure, config delivery, write API enablement, backup/import/reboot,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 `P7-C002` public exposure gate for AMN2 `b121865` was opened by the
operator and completed on 2026-06-14 as read-only pre-cutover on disposable VPS
`89.185.80.166`, with outcome `blocked-by-preconditions`. Evidence:
`research/amn2/phase-7-public-exposure-gate-precutover-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`; web
remained loopback-only on `127.0.0.1:3030`; external probes to `3030`, `3040`,
`80` and `443` returned `000`; reverse proxy binaries/services were absent or
inactive; `ufw` was inactive; `WEB_ADMIN_USERNAME=missing`; public domain/base
URL was missing; `VPS_APPLY_ENABLED=false`; `LOCAL_AGENT_ENABLED=false`. No
reverse proxy install/apply, TLS certificate issue, firewall change, public
listener change, public web/admin exposure, public API exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. Later `P7-C002a` supplied
admin/domain prerequisites and `P7-C002b` verified runtime/login on loopback;
actual public cutover remains a separate critical named gate.

Phase 7 `P7-S004 + watch-only intake check + operator named-gate menu review`
was completed on 2026-06-14 as docs-only/watch-only work. Evidence:
`research/amn2/phase-7-final-freeze-watch-menu-2026-06-14.md`. Phase 7
local-only expansion is now frozen before any named gate. The evidence index
and next-chat handoff show the watch-only intake check and an operator
named-gate menu for `P7-C002`...`P7-C007`. No live VPS command, SSH command,
package upload/apply/rebuild on VPS, service restart/deploy, public exposure,
config delivery, write API enablement, Local Agent mutation, backup/import/
reboot, production peer/user mutation, destructive action, Telegram token use,
live bot send, Telegram profile/media mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 `P7-N004 + watch-only automation/client refresh intake + named-gate dry
checklist review + final RC notes polish` was completed on 2026-06-14 as
local-only/docs/watch-only work. Evidence:
`research/amn2/phase-7-evidence-watch-drycheck-rcnotes-2026-06-14.md`. Added
`docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md`, recorded that upstream automations
remain watch-only intake, added named-gate dry checklist review and polished
AMN2 `docs/RELEASE_NOTES_RC_SKELETON.ru.md` so `b121865` is the latest
known-good VPS-smoked/package baseline while public/config/write/backup/
destructive/Telegram gates remain unopened. No live VPS command, SSH command,
package upload/apply/rebuild on VPS, service restart/deploy, public exposure,
config delivery, write API enablement, Local Agent mutation, backup/import/
reboot, production peer/user mutation, destructive action, Telegram token use,
live bot send, Telegram profile/media mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 `P7-S003` final RC handoff/status compression was completed on
2026-06-14 as AMN3 docs-only work. Evidence:
`research/amn2/phase-7-final-rc-handoff-compression-2026-06-14.md`.
`docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md` is now a compact handoff
with short start block, current state, approved remaining plan, RC Gate Matrix
summary, exact named gate policy and recommendation rhythm. No live VPS
command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram token use, live bot send, Telegram profile/media
mutation, secret publication or upstream/GPL code copy was performed.
`P7-S003` is removed from the active Phase 7 plan.

Phase 7 `P7-I010` release candidate gate matrix consolidation was completed on
2026-06-14 as AMN3 local-only docs/tests work. Evidence:
`research/amn2/phase-7-rc-gate-matrix-consolidation-2026-06-14.md`.
`docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md` now contains `RC Gate Matrix`,
which separates completed local-only structural tasks, active critical named
gates, watch-only intake and inactive structural proposals. The matrix maps
`P7-C002`...`P7-C007` to readiness source, current blocker/status and allowed
next action. No live VPS command, SSH command, package upload/apply/rebuild on
VPS, service restart/deploy, public exposure, config delivery, write API
enablement, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram token use, live bot send, Telegram
profile/media mutation, secret publication or upstream/GPL code copy was
performed. `P7-I010` is removed from the active Phase 7 plan.

Phase 7 `P7-I009` Telegram identity/profile/media prerequisite checklist was
completed on 2026-06-14 as AMN2 local-only code/tests/docs and AMN3
evidence/status work. Evidence:
`research/amn2/phase-7-telegram-identity-readiness-2026-06-14.md`. AMN2 fresh
installer manifest and `/api/integration/status` now expose
`telegram_identity_readiness` with schema
`telegram-identity-profile-media-prerequisite-checklist.v1`, status
`readiness_checklist_ready`, target gate `P7-C007`, Telegram API disabled,
token use disabled, profile mutation disabled, media mutation disabled and live
bot send disabled. Required checklists cover identity scope decision,
credential handoff/storage policy, profile/media asset planning, operator
preview/rollback and post-mutation relock audit. Verification: RED focused `3
failed, 29 passed, 1 StarletteDeprecationWarning`; focused GREEN `32 passed, 1
StarletteDeprecationWarning`; expanded `38 passed, 1
StarletteDeprecationWarning`; full AMN2 suite `741 passed, 1
StarletteDeprecationWarning`. No live VPS command, SSH command, package
upload/apply/rebuild on VPS, service restart/deploy, public exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram token use, live bot
send, Telegram profile/media mutation, secret publication or upstream/GPL code
copy was performed. `P7-I009` is removed from the active Phase 7 plan.

Phase 7 `P7-I008` backup/restore/import prerequisite checklist was completed
on 2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-backup-restore-import-readiness-2026-06-14.md`. AMN2
fresh installer manifest and `/api/integration/status` now expose
`backup_restore_import_readiness` with schema
`backup-restore-import-prerequisite-checklist.v1`, status
`readiness_checklist_ready`, target gate `P7-C006`, live backup disabled,
restore apply disabled, archive import disabled and reboot disabled. Required
checklists cover backup scope, encryption/retention policy, restore preview
safety, import source validation and disaster-recovery drill planning.
Verification: RED focused `3 failed, 27 passed, 1 StarletteDeprecationWarning`;
focused GREEN `30 passed, 1 StarletteDeprecationWarning`; expanded `36 passed,
1 StarletteDeprecationWarning`; full AMN2 suite `739 passed, 1
StarletteDeprecationWarning`. No live VPS command, SSH command, package
upload/apply/rebuild on VPS, service restart/deploy,
public exposure, config delivery, write API enablement, Local Agent mutation,
backup archive create, restore apply, archive import apply, reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `P7-I008` is removed from the active
Phase 7 plan.

Phase 7 `P7-I007` write API scope/implementation decision was completed on
2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-write-api-scope-decision-2026-06-14.md`. AMN2 fresh
installer manifest and `/api/integration/status` now expose
`write_api_scope_decision` with schema `write-api-scope-decision.v1`, status
`decision_ready`, target gate `P7-C005` and selected RC policy
`keep_public_api_read_only_for_rc`. Write API, public write routes, Local Agent
mutation and production peer/user mutation remain disabled; deferred options
require `P7-C005`. Verification: RED focused `3 failed, 25 passed, 1
StarletteDeprecationWarning`; focused GREEN `28 passed, 1
StarletteDeprecationWarning`; expanded `34 passed, 1 StarletteDeprecationWarning`;
full AMN2 suite `737 passed, 1 StarletteDeprecationWarning`. No live VPS
command, SSH command, package
upload/apply/rebuild on VPS, service restart/deploy, public exposure, config
delivery, write API enablement, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. `P7-I007` is removed from
the active Phase 7 plan.

Phase 7 `P7-I006` config delivery channel readiness was completed on
2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-config-delivery-channel-readiness-2026-06-14.md`. AMN2
fresh installer manifest and `/api/integration/status` now expose
`config_delivery_channel_readiness` with schema
`config-delivery-channel-readiness.v1`, status `readiness_design_ready`, target
gate `P7-C003`, live delivery disabled and checklists for SMTP/operator-local
channel decision, secret-safe evidence protocol, client import matrix, one-time
delivery policy and delivery revocation story. API/rendered-plan views redact
exact forbidden evidence marker names to count/policy while the local manifest
keeps the full validation contract. Verification: RED focused `3 failed, 23
passed, 1 StarletteDeprecationWarning`; focused GREEN `26 passed, 1
StarletteDeprecationWarning`; expanded `32 passed, 1 StarletteDeprecationWarning`;
full AMN2 suite `735 passed, 1 StarletteDeprecationWarning`. No live VPS
command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I006` is removed from the active Phase 7 plan.

Phase 7 `P7-I005` public exposure readiness/design was completed on 2026-06-14
as AMN2 local-only code/tests/docs and AMN3 evidence/status work. Evidence:
`research/amn2/phase-7-public-exposure-readiness-design-2026-06-14.md`. AMN2
fresh installer manifest and `/api/integration/status` now expose
`public_exposure_readiness_design` with schema
`public-exposure-readiness-design.v1`, status `readiness_design_ready`, target
gate `P7-C002`, live exposure disabled and checklists for admin credential
contract, domain/TLS/reverse-proxy plan, firewall/listener plan, external probe
matrix and rollback-to-loopback. Blocked actions remain public listener change,
firewall apply, reverse proxy apply, TLS certificate issue, public OpenAPI
publication and direct public API `3040`. Verification: RED focused `3 failed,
21 passed, 1 StarletteDeprecationWarning`; focused GREEN `24 passed, 1
StarletteDeprecationWarning`; expanded `30 passed, 1 StarletteDeprecationWarning`.
No live VPS command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I005` is removed from the active Phase 7 plan.

Phase 7 `P7-I004` public/config/write prerequisite split was completed on
2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-public-config-write-prerequisite-split-2026-06-14.md`.
AMN2 fresh installer manifest and `/api/integration/status` now expose
`public_config_write_prerequisite_split` with schema
`public-config-write-prerequisite-split.v1`, status
`blocked_by_preconditions`, source evidence
`research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`,
and three readiness tracks: `P7-C002` public exposure readiness, `P7-C003`
config delivery channel readiness and `P7-C005` write API scope decision.
Blocked actions remain public listener changes, domain/TLS/reverse proxy apply,
config artifact output, write route enablement, `VPS_APPLY_ENABLED=true`, Local
Agent mutation and live peer/user mutation. Verification: RED focused `3
failed, 19 passed, 1 StarletteDeprecationWarning`; focused GREEN `22 passed, 1
StarletteDeprecationWarning`; expanded `28 passed, 1 StarletteDeprecationWarning`.
No live VPS command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API enablement, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed. `P7-I004` is removed from the active Phase 7 plan.

Phase 7 `P7-C002 + P7-C003 + P7-C005` public/config/write gate for AMN2
`b121865` was opened and completed on 2026-06-14 as read-only preflight on
disposable VPS `89.185.80.166`, with outcome `blocked-by-preconditions`.
Evidence:
`research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`.
Remote source overlay was `b121865f488821f6fc471c9529fb26e5d7992515`; web
runtime remained `127.0.0.1:3030`; loopback `/login` returned `200`; external
probes to `3030`, `3040`, `80` and `443` returned `000`. Safe env summary:
`APP_SECRET_KEY=present`, `WEB_ADMIN_USERNAME=missing`,
`WEB_ADMIN_PASSWORD_HASH=present`, `VPS_APPLY_ENABLED=false`,
`EMAIL_CONFIG_ATTACHMENTS_ENABLED=unset`, SMTP config missing and
`LOCAL_AGENT_ENABLED=false`. Public API route inventory was read-only and
`write_api_route_count=0`. Web admin has local operator write/config routes, but
they remain loopback-only and were not invoked by Codex. No public exposure,
domain/TLS/reverse proxy/firewall change, public OpenAPI publication, config
delivery, `.conf`, QR, `vpn://`, write API route enablement, `/api/clients`
CRUD, Local Agent mutation, `VPS_APPLY_ENABLED=true`, live peer/user mutation,
backup/import/reboot, destructive action, secret-bearing evidence publication
or upstream/GPL code copy was performed. `P7-C002`, `P7-C003` and `P7-C005`
remain critical gates, now with explicit blockers.

Phase 7 `P7-C001` live package/apply/smoke for AMN2 `b121865` was completed on
2026-06-14 on disposable VPS `89.185.80.166` as `live-update-smoke-pass`.
Evidence: `research/amn2/phase-7-live-update-smoke-b121865-2026-06-14.md`.
Package `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
`364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, was
uploaded, remote checksum-verified and applied as a source overlay. Remote
source commit is `b121865f488821f6fc471c9529fb26e5d7992515`;
`source_update_status=passed`; API loopback smoke returned `VPS verdict: pass`;
auth/listener/audit passed; negative auth checks returned `401/403/401`; API
listener was loopback-only on `127.0.0.1:3040`; web login returned `200` on
loopback `127.0.0.1:3030`; external probes to `3030`, `3040`, `80` and `443`
returned `000`. This was later superseded by `P7-C005` on `5501295`; current
latest VPS-smoked/package head is now `5501295 Add P7 install write contour`.
`b121865` remains the completed clean-installer baseline, and `0de7a77` remains
earlier history/rollback evidence. `P7-C001` is removed from the active Phase 7 plan.
No public exposure, config delivery, write API production opening, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram identity/profile/media mutation, secret publication or
upstream/GPL code copy was performed.

Phase 7 `P7-S001` next-chat/status hygiene was completed on 2026-06-14 as
AMN3 docs-only work. Evidence:
`research/amn2/phase-7-next-chat-status-hygiene-2026-06-14.md`. Phase 7
handoff/status/backlog/context/transfer docs showed that the default local-only
RC readiness queue was closed. After `P7-C001`, active Phase 7 work is limited
to critical named gates `P7-C002` through `P7-C007` and watch-only monitoring.
No live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 `P7-N001 + P7-N003 + P7-X001` automation intake, client compatibility
watch refresh and clean installer operator copy polish was completed on
2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-automation-client-watch-copy-polish-2026-06-14.md`.
Weekly upstream-refresh automations remain intake-only signals; AMN2 now exposes
`CLIENT_COMPATIBILITY_WATCH` through integration status without opening config
delivery; clean installer prompts are Russian-first while stable answer values
remain unchanged. Focused RED returned one expected import error; focused GREEN
returned `10 passed, 1 StarletteDeprecationWarning`; expanded suite returned
`68 passed, 1 StarletteDeprecationWarning`; final full AMN2 suite returned
`729 passed, 1 StarletteDeprecationWarning`. `P7-N001`, `P7-N003` and
`P7-X001` are removed from the active Phase 7 plan. No live VPS command, SSH
command, package upload/apply on VPS, service restart/deploy, public exposure,
public OpenAPI publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 `P7-M003 + P7-N002 + P7-S002` multi-instance/IPAM incorporation,
API/docs taxonomy RC drift check and release notes skeleton was completed on
2026-06-14 as AMN2 local-only code/tests/docs and AMN3 evidence/status work.
Evidence:
`research/amn2/phase-7-multi-instance-taxonomy-release-notes-2026-06-14.md`.
AMN2 fresh installer now exposes `multi_instance_ipam_rc_decision`, rendered
plans include `multi-instance-ipam-rc-decision`, integration status exposes
`api_docs_taxonomy_rc_drift_check`, and AMN2 docs include
`docs/RELEASE_NOTES_RC_SKELETON.ru.md` without declaring a public release.
Focused RED returned `3 failed, 15 passed, 1 StarletteDeprecationWarning`;
focused GREEN returned `18 passed, 1 StarletteDeprecationWarning`; expanded
suite returned `56 passed, 1 StarletteDeprecationWarning`; final full AMN2
suite returned `728 passed, 1 StarletteDeprecationWarning`. `P7-M003`,
`P7-N002` and `P7-S002` are removed from the active Phase 7 plan. No live VPS
command, SSH command, package upload/apply on VPS, service restart/deploy,
public exposure, public OpenAPI publication, config delivery, write API, Local
Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

Phase 7 `P7-I002 + P7-M002 + P7-I003` clean installer RC checklist/security
contract was completed on 2026-06-14 as AMN2 local-only code/tests/docs and
AMN3 evidence/status work. Evidence:
`research/amn2/phase-7-clean-installer-rc-checklist-security-contract-2026-06-14.md`.
AMN2 fresh installer now exposes `clean_installer_rc_acceptance`, package
asset/runbook path verification for the `b121865` package, package-local helper
default bindings and `secret_input_contract` with field-only secret-bearing
answer rejection. TDD evidence: RED focused `6 failed, 10 passed`, GREEN
focused `16 passed`, expanded `52 passed`, regression verification `17 passed,
1 StarletteDeprecationWarning`, final full AMN2 suite `727 passed, 1
StarletteDeprecationWarning`. `P7-I002`, `P7-M002` and `P7-I003` are removed
from the active Phase 7 plan. No live VPS command, SSH command, package
upload/apply on VPS, service restart/deploy, public exposure, public OpenAPI
publication, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 7 `P7-I001 + P7-M001` current-head package/preflight for AMN2 `b121865`
was completed on 2026-06-14 as AMN3 local-only package/preflight work.
Evidence:
`research/amn2/phase-7-current-head-package-preflight-b121865-2026-06-14.md`.
Built `dist/amn2-vps-update-and-smoke-kit-b121865.zip`, sha256
`364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849`, from source
zip `dist/amn2-codex-vps-test-prep-b121865-source.zip`, sha256
`D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647`. AMN2
focused RC suite returned `56 passed, 1 StarletteDeprecationWarning`; full AMN2
suite returned `724 passed, 1 StarletteDeprecationWarning`; AMN3 package tests
returned `4 tests OK`. At that step `b121865` was
package-ready-not-vps-smoked and known-good VPS-smoked/package baseline remained
`0de7a77 Polish fresh installer preflight planning`; this was later superseded
by `P7-C001`. `P7-I001` and `P7-M001` are removed from the active Phase 7 plan.
No live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 7 transition packet was prepared on 2026-06-14 as AMN3 docs-only/local-only
work. Evidence: `research/amn2/phase-7-transition-packet-2026-06-14.md`.
Phase 7 name/status: `Release Candidate Readiness / Clean Installer RC`,
`pre-release / release-candidate readiness`. Added
`docs/NEXT_CHAT_AMN2_PHASE_7_RELEASE_CANDIDATE.ru.md` and
`docs/PHASE_7_RELEASE_CANDIDATE_PLAN.ru.md`. AMN2 current head remains
`b121865 Add multi instance conflict model`; latest VPS-smoked/package head
remains `0de7a77 Polish fresh installer preflight planning`. Default Phase 7
lane is local-only/docs/tests/security/package-preflight; no VPS/SSH access is
needed by default. Existing weekly upstream-refresh automations were updated to
Phase 7 context. No live VPS command, SSH command, package rebuild/apply on VPS,
service restart/deploy, public exposure, public OpenAPI publication, config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

Phase 6 final closeout + clean-installer next-phase entry + current VPS
known-good snapshot/runbook was completed on 2026-06-14 as AMN3
docs-only/local-only work. Evidence:
`research/amn2/phase-6-final-closeout-known-good-snapshot-2026-06-14.md`.
Decision: Phase 6 default lane is closed, default local queue is empty and the
project remains private/operator-only. AMN2 current head is `b121865 Add multi
instance conflict model`, pushed to `amn2/codex-vps-test-prep`; latest
VPS-smoked/package head remains `0de7a77 Polish fresh installer preflight
planning`. Current disposable VPS `89.185.80.166` known-good evidence remains
`research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md`. Any future
live update from `0de7a77` to `b121865` requires a separate named live
package/apply/smoke gate. Remaining public/config/write/backup/destructive/Local
Agent/Telegram identity gates remain deferred and not active. No live VPS
command, SSH command, package rebuild/apply on VPS, service restart/deploy,
public exposure, public OpenAPI publication, config delivery, write API, Local
Agent mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed.

After Phase 6 `P6-M005` multi-instance/port/IPAM conflict model was completed
on 2026-06-14 as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-multi-instance-ipam-conflict-model-2026-06-14.md`.
AMN2 branch `codex-vps-test-prep` advanced to `b121865 Add multi instance
conflict model` and was pushed to `amn2/codex-vps-test-prep`. The slice adds
`capability_registry.multi_instance_conflict_model` and doc
`docs/MULTI_INSTANCE_IPAM_CONFLICT_MODEL.ru.md`; live multi-instance apply,
runtime config write, firewall change, peer migration, config delivery and
service restart remain blocked. Verification: RED `3 failed, 4 passed, 1
StarletteDeprecationWarning`, focused `7 passed, 1 StarletteDeprecationWarning`,
expanded `27 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `724
passed, 1 StarletteDeprecationWarning`, `git diff --check` and staged check
passed. No live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. Latest VPS-smoked/package head remains
`0de7a77`; AMN2 `b121865` is local-only and not package-rebuilt/VPS-smoked.
Next recommendation: Phase 6 final closeout + clean-installer next-phase entry
+ current VPS known-good snapshot/runbook.

After Phase 6 `FI-M004 + P6-N005` was completed on 2026-06-14 as AMN2
local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-installer-preflight-taxonomy-guards-2026-06-14.md`.
AMN2 branch `codex-vps-test-prep` advanced to `4cde273 Add installer preflight
taxonomy guards` and was pushed to `amn2/codex-vps-test-prep`. The slice adds
fresh-installer package asset path preflight, rendered
`package-asset-path-preflight` phase and public docs/API route-order drift guard.
Verification: RED `3 failed, 15 passed`, focused `18 passed`, expanded
`26 passed, 1 StarletteDeprecationWarning`, full AMN2 suite `723 passed, 1
StarletteDeprecationWarning`, `git diff --check` and staged check passed. No
live VPS command, SSH command, package rebuild/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. Latest VPS-smoked/package head remains
`0de7a77`; AMN2 `4cde273` is local-only and not package-rebuilt/VPS-smoked.
Next recommendation: Phase 6 final closeout + clean-installer next-phase entry
+ current VPS known-good snapshot/runbook. Optional alternative: `P6-M005`
local-only multi-instance/port/IPAM conflict model.

After Phase 6 automation intake aggregation + closeout readiness review was
completed on 2026-06-14 as AMN3 local-only/docs-only work. Evidence:
`research/amn2/after-phase-6-automation-intake-aggregation-closeout-readiness-2026-06-14.md`.
PRVTPRO heartbeat output was available and normalized into
`research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md`.
KYORESUAS and Amnezia final automation reports were not found in the current
AMN2 thread or local AMN3 evidence, so they are explicitly marked
`missing-input`; direct public GitHub metadata refresh produced
`research/upstreams/kyoresuas-amnezia-api-github-watch-2026-06-14.md` and
`research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-14.md`.
New non-live candidates: `FI-M004` package asset path preflight
(`package/preflight only`), `P6-M005` multi-instance/port/IPAM conflict model
(`local-only/docs/tests`) and `P6-N005` OpenAPI/taxonomy route-order drift guard
(`local-only/docs/tests`). AmneziaWG Android `2.0.1` is watch-only. Closeout
readiness: Phase 6 can proceed to final closeout; optional pre-closeout bundle
is `FI-M004 + P6-N005`. No live VPS command, SSH command, package rebuild/apply
on VPS, service restart/deploy, public exposure, config delivery, write API,
Local Agent mutation, backup/import/reboot, production peer/user mutation,
destructive action, Telegram action, secret publication or upstream/GPL code
copy was performed.

After Phase 6 automation intake audit + upstream refresh aggregation plan was
completed on 2026-06-14 as AMN3 local-only/docs-only work. Evidence:
`research/amn2/after-phase-6-automation-intake-audit-plan-2026-06-14.md`.
Created `docs/AMN2_AUTOMATION_INTAKE_AGGREGATION_PLAN.ru.md` with the required
intake card format, priority labels, gate labels, deduplication statuses and
audit steps for the three weekly upstream-refresh automations. The plan records
that PRVTPRO, KYORESUAS and Amnezia remain separate heartbeat automations with
separate target thread bindings, while the AMN2 thread is the decision lane.
The current known PRVTPRO heartbeat report is treated as input, but KYORESUAS
and Amnezia aggregator outputs are not assumed. No live VPS command, SSH
command, package rebuild/apply on VPS, service restart/deploy, public exposure,
config delivery, write API, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action,
secret-bearing evidence publication or upstream/GPL code copy was performed.
Next recommendation: wait for KYORESUAS and Amnezia outputs, then run
`Automation intake aggregation + Phase 6 closeout readiness review`.

Phase 6 `P6-C010` live update/smoke for AMN2 `0de7a77` was completed on
2026-06-14 as `live-update-smoke-pass` on disposable VPS `89.185.80.166`.
Evidence: `research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md`.
Built package `dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, was
uploaded, checksum-verified and extracted. Source overlay updated `/opt/amn2`
to `0de7a77f3eb09d23dc2785d402bc51c2b5eb7835`; source update run_id
`20260614T062734Z` passed. The manual web/bot runtime was minimally restarted
so it loaded the overlaid source; web remained bound to `127.0.0.1:3030`.
Read-only API smoke on temporary loopback `127.0.0.1:3040` passed with run_id
`20260614T063327Z`, auth/listener/audit `passed`, and negative auth checks
`401/403/401`. Final remote listener snapshot showed only `127.0.0.1:3030`,
with `3040/80/443` absent; external probes returned `000`. `VPS_APPLY_ENABLED=false`
remained explicit. No public exposure change, config delivery, write API
production opening, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive cleanup/reinstall, provider-side destructive
action, Telegram identity/profile mutation, live bot send by Codex,
secret-bearing evidence publication or upstream/GPL code copy was performed.
`P6-C010` is removed from active Phase 6 plan. Latest VPS-smoked/package head
is now `0de7a77`.

After Phase 6 next-chat handoff refresh + live gate checklist grooming for
`0de7a77` was completed on 2026-06-14 as AMN3 docs-only/local-only work.
Evidence:
`research/amn2/after-phase-6-next-chat-live-gate-checklist-0de7a77-2026-06-14.md`.
Updated `docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md` with the current source of
truth, exact future gate phrase, package/source checksums, stop criteria and
forbidden surfaces. No live VPS command, SSH command, package upload/apply on
VPS, service restart/deploy, public exposure, config delivery, write API, Local
Agent mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. `P6-C010` remains closed until the exact named gate phrase is given.

After Phase 6 local package build/preflight for `0de7a77` was completed on
2026-06-14 as AMN3 local package work. Evidence:
`research/amn2/after-phase-6-package-preflight-0de7a77-2026-06-14.md`. Built
`dist/amn2-vps-update-and-smoke-kit-0de7a77.zip`, sha256
`7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B`, from
source zip `dist/amn2-codex-vps-test-prep-0de7a77-source.zip`, sha256
`B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295`. Package
hygiene passed with `kit_entries=5`, `source_entries=342`,
`forbidden_source_entries=0`, shell scripts LF/no-BOM, operator doc markdown
hygiene, package checksum and test-extract. Verification returned full AMN2
suite `721 passed, 1 StarletteDeprecationWarning`, AMN3 package/apply-script and
markdown hygiene tests `4 tests OK`, and `git diff --check` passed. No live VPS
command, SSH command, package upload/apply on VPS, service restart/deploy,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
AMN2 `0de7a77` is package-ready-not-vps-smoked; latest VPS-smoked head remains
`c46f664`. Next recommendation: next-chat handoff refresh, or a separate named
live apply/smoke gate for `0de7a77` if the operator chooses.

After Phase 6 `FI-X001 + current-head package preflight planning` was completed
on 2026-06-14 as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-copy-package-preflight-2026-06-14.md`.
AMN2 branch `codex-vps-test-prep` advanced to `0de7a77 Polish fresh installer
preflight planning` and was pushed to `amn2/codex-vps-test-prep`. The slice
changes fresh installer prompts to Russian-first copy while preserving stable
technical IDs, adds `fresh-install-package-preflight.v1`, records target
preflight head `ff77d4c`, latest VPS-smoked head `c46f664`, and keeps package
build, live apply and live smoke disabled by default. Verification returned RED
`3 failed, 9 passed`, focused `12 passed`, full AMN2 suite `721 passed, 1
StarletteDeprecationWarning`, and `git diff --check` / staged checks passed. No
live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. Latest VPS-smoked/package head remains `c46f664`; AMN2 `0de7a77` is
local-only and not package-rebuilt/VPS-smoked. Next recommendation: local
package build/preflight for `0de7a77` without live apply/smoke, or a separate
named live gate if the operator chooses.

After Phase 6 `P6-C001 + P6-C002` docs-only checklist refresh was completed on
2026-06-13 as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-public-config-gate-checklist-refresh-2026-06-13.md`.
AMN2 branch `codex-vps-test-prep` advanced to `ff77d4c Add public config gate
checklist` and was pushed to `amn2/codex-vps-test-prep`. The slice adds
`docs/PUBLIC_CONFIG_GATE_CHECKLIST.ru.md` plus
`build_public_config_gate_checklist()`, records `public_exposure_enabled=false`
and `config_delivery_enabled=false`, and blocks public listener exposure,
public OpenAPI publication, short config-link issue/redeem, QR, VPN import
link, `.conf`, Telegram live config send and Local Agent config mutation without
the correct named gate. Verification returned focused `4 passed`, full AMN2
suite `720 passed, 1 StarletteDeprecationWarning`, and `git diff --check`
passed. No live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed. `P6-C001` and `P6-C002` remain critical gated/deferred for actual
public exposure and actual config delivery. Latest VPS-smoked/package head
remains `c46f664`; AMN2 `ff77d4c` is local-only and not
package-rebuilt/VPS-smoked. Next recommendation: `FI-X001 + current-head package
preflight planning for ff77d4c` as local-only docs/tests/package hygiene,
without live apply.

After Phase 6 `FI-N001 + FI-N002 + FI-S001` fresh installer evidence readiness
was completed on 2026-06-13 as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-evidence-readiness-2026-06-13.md`.
AMN2 branch `codex-vps-test-prep` advanced to `525a9cd Add fresh installer
evidence readiness` and was pushed to `amn2/codex-vps-test-prep`. The slice
adds `fresh-install-evidence.v1`, smoke/evidence template, report-only
existing-server reconciliation input and `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`.
Verification returned RED `3 failed, 8 passed`, focused `13 passed`, full AMN2
suite `719 passed, 1 StarletteDeprecationWarning`, and `git diff --check` /
`git diff --cached --check` passed. No live VPS command, SSH command, live
smoke execution, package apply/rebuild on VPS, service restart/deploy, public
exposure, config delivery, write API, Local Agent mutation, backup/import/reboot,
production peer/user mutation, destructive action, Telegram action, secret
publication or upstream/GPL code copy was performed. `FI-N001`, `FI-N002` and
`FI-S001` are removed from the active recommendation. Latest VPS-smoked/package
head remains `c46f664`; AMN2 `525a9cd` is local-only and not
package-rebuilt/VPS-smoked. Next operator-requested item:
`P6-C001 + P6-C002` docs-only checklist refresh, without opening public/config
gates.

After Phase 6 `FI-M001 + FI-M002 + FI-M003` fresh installer readiness planning
was completed on 2026-06-13 as AMN2 local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-readiness-planning-2026-06-13.md`.
AMN2 branch `codex-vps-test-prep` advanced to `7416fb0 Add fresh installer
readiness planning` and was pushed to `amn2/codex-vps-test-prep`. The slice
adds `fresh-install-readiness.v1`, target OS/runtime preflight matrix, runtime
mode decision and package hygiene checklist to the fresh installer plan.
Verification returned RED `2 failed, 6 passed`, focused `10 passed`, full AMN2
suite `716 passed, 1 StarletteDeprecationWarning`, and `git diff --check` /
`git diff --cached --check` passed. No live VPS command, SSH command, target
diagnostic execution, package apply/rebuild on VPS, service restart/deploy,
public exposure, config delivery, write API, Local Agent mutation,
backup/import/reboot, production peer/user mutation, destructive action,
Telegram action, secret publication or upstream/GPL code copy was performed.
`FI-M001`, `FI-M002` and `FI-M003` are removed from the active recommendation.
Latest VPS-smoked/package head remains `c46f664`; AMN2 `7416fb0` is local-only
and not package-rebuilt/VPS-smoked. Next recommendation:
`FI-N001 + FI-N002 + FI-S001` as local-only docs/test evidence readiness.

After Phase 6 `FI-I001 + FI-I002 + FI-I003` fresh installer question model,
plan renderer and secret handoff binding were completed on 2026-06-13 as AMN2
local-only code/tests/docs. Evidence:
`research/amn2/after-phase-6-fresh-installer-plan-renderer-2026-06-13.md`.
AMN2 branch `codex-vps-test-prep` advanced to `de635a0 Add fresh installer
plan renderer` and was pushed to `amn2/codex-vps-test-prep`. The slice adds
versioned fresh-install question/answer schemas, a redacted rendered plan,
named-gate mapping for `P6-C001`, `P6-C002`, `P6-C003` and `P6-C007`, secret
handoff protocol binding, docs `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`, and
`scripts/test.ps1` as the canonical Windows/Codex Desktop test wrapper for
CPython 3.12 + `.codex_deps`. Verification returned RED manifest/doc tests,
focused `8 passed`, full AMN2 suite `714 passed, 1 StarletteDeprecationWarning`,
and `git diff --cached --check` passed. No live VPS command, SSH command,
package apply/rebuild on VPS, service restart/deploy, public exposure, config
delivery, write API, Local Agent mutation, backup/import/reboot, production
peer/user mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed. `FI-I001`, `FI-I002` and `FI-I003` are
removed from the active recommendation. Latest VPS-smoked/package head remains
`c46f664`; AMN2 `de635a0` is local-only and not package-rebuilt/VPS-smoked.
Next recommendation: `FI-M001 + FI-M002 + FI-M003` as local-only installer
preflight/runtime/package planning.

Phase 6 `P6-S004` closeout packet + next-chat handoff + fresh installer backlog grooming was completed on 2026-06-13 as AMN3 docs-only work. Evidence: `research/amn2/phase-6-closeout-next-chat-fresh-installer-backlog-2026-06-13.md`. Added `docs/NEXT_CHAT_AMN2_AFTER_PHASE_6.ru.md` and `docs/AMN2_FRESH_INSTALLER_BACKLOG.ru.md`, synchronized the Phase 6 handoff/status/context/backlog, closed the Phase 6 default lane and organized future clean-installer candidates under `FI-*` IDs. Public/self-service launch remains not opened; remaining work is gated/deferred. Its recommended local-only bundle `FI-I001 + FI-I002 + FI-I003` was completed after Phase 6 in AMN2 `de635a0`; the current recommendation is `FI-M001 + FI-M002 + FI-M003`. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed.

Phase 6 `P6-X003` package runbook escaping hygiene was completed on 2026-06-13 as AMN3 local-only docs/tooling hygiene. Evidence: `research/amn2/phase-6-package-runbook-escaping-hygiene-2026-06-13.md`. Added `scripts/check_markdown_hygiene.py` and `tests/test_markdown_hygiene.py` to catch accidental ASCII control characters in generated Markdown/operator docs. Verification returned RED failure while the tool was missing, GREEN `2 tests OK`, and a diagnostic run against the already-smoked unpacked `c46f664` operator doc failed with five expected findings. The already-smoked `c46f664` zip/package artifact was not rebuilt, repacked or altered. No live VPS command, SSH command, package apply, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive action, Telegram action, secret publication or upstream/GPL code copy was performed. `P6-X003` is removed from active Phase 6 plan.

Phase 6 `P6-C009` live update/smoke for AMN2 `c46f664` was completed on 2026-06-13 as `live-update-smoke-pass`. Evidence: `research/amn2/phase-6-live-update-smoke-c46f664-2026-06-13.md`; package preflight evidence: `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built and applied `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`, from source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Source overlay updated `/opt/amn2` from `b3102db250da7ca9aef78ca095602187d0efc462` to `c46f664762d7774756b88db8d4e1ebc038b20bb5`; source update run_id `20260613T173232Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T173738Z` passed with auth/listener/audit `passed`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C009` is removed from active Phase 6 plan. Latest VPS-smoked/package head is now `c46f664`. Follow-up added: `P6-X003` package runbook escaping hygiene.

Phase 6 `P6-C008` current-head package refresh/preflight for AMN2 `c46f664` was completed on 2026-06-13 as AMN3 local package work with current-head smoke plan and named live gate checklist. Evidence: `research/amn2/phase-6-current-head-package-preflight-c46f664-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`, package sha256 `5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE`, from source zip `dist/amn2-codex-vps-test-prep-c46f664-source.zip`, source sha256 `5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248`. Package hygiene passed with `kit_entries=5`, `source_entries=337`, `forbidden_source_entries=0`, shell scripts LF/no-BOM and commit bindings present. AMN2 focused suite returned `11 passed, 1 StarletteDeprecationWarning`, AMN2 toolchain check passed, and AMN3 apply-script regression returned `2 tests OK`. No live VPS command, SSH command, package upload/apply on VPS, source overlay on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram identity mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C008` is removed from active Phase 6 plan. `c46f664` is package-ready locally and not VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Future live apply/smoke is tracked as `P6-C009` and remains critical gated/deferred until the exact named phrase is provided.

Phase 6 `P6-N001` public docs/API taxonomy and `P6-C007` checklist-only were completed on 2026-06-13 as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-public-taxonomy-cleanup-checklist-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `c46f664 Add public taxonomy cleanup checklist` and was pushed to `amn2/codex-vps-test-prep`. The slice adds a machine-checkable public docs/API taxonomy boundary, keeps publication/public API flags disabled, adds a destructive cleanup/reinstall checklist with execution flags disabled, and exposes both through API/web integration status. `P6-C001` remains required before any public publication; `P6-C007` remains required before cleanup/reinstall/destructive execution. Verification returned focused `11 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check `AMN2 toolchain ok: CPython 3.12.x`, `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-N001` is removed from active Phase 6 plan. `P6-C007` remains critical gated/deferred. AMN2 current head `c46f664` is not package-rebuilt or VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Next recommendation: `P6-C008` current-head package refresh/preflight for `c46f664`, or a separately named live/public/destructive gate if the operator chooses.

Phase 6 `P6-I007` fresh-install wizard/bootstrap automation was completed on 2026-06-13 as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-fresh-install-wizard-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `60d2570 Add fresh install wizard boundary` and was pushed to `amn2/codex-vps-test-prep`. The slice adds `app.services.fresh_install_wizard`, CLI commands `python -m app.cli install wizard --pretty` and `python -m app.cli install plan --answers fresh-install-answers.json --pretty`, docs `docs/FRESH_INSTALL_WIZARD.ru.md`, and API/web integration-status visibility. The wizard only collects operator answers and emits a local-only dry-run plan; public exposure, config delivery, write API and destructive cleanup answers become stop-lines requiring `P6-C001`, `P6-C002`, `P6-C003` or `P6-C007`. Verification returned focused `14 passed, 1 StarletteDeprecationWarning`, security/hygiene `26 passed`, toolchain check `AMN2 toolchain ok: CPython 3.12.x`, `git diff --check` and staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I007` is removed from active Phase 6 plan. `P6-C007` remains critical gated/deferred. AMN2 current head `60d2570` is not package-rebuilt or VPS-smoked; latest VPS-smoked/package head remains `b3102db`. Its next recommendation was completed by `P6-N001` + `P6-C007` checklist-only.

Phase 6 `P6-C002-design` + `P6-I006` config-link/entitlement boundary was completed on 2026-06-13 as AMN2 local-only code/tests/docs. Evidence: `research/amn2/phase-6-config-link-entitlement-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `d96112c Add config link entitlement boundary` and was pushed to `amn2/codex-vps-test-prep`. The slice adds a tokenized config-link boundary with runtime/config delivery disabled by default, opaque random token model, hash-at-rest storage, one-time 15 minute TTL and Telegram one-tap copy policy; adds a commercial entitlement/audit boundary with payment provider disabled, entitlement write API disabled, automatic activation disabled, config delivery decoupled from payment and manual review required; adds blocked-future surface policies for entitlement manual review, config-link issue and public token redeem; updates API/web integration status to latest VPS-smoked head `b3102db` and next local recommendation `P6-I007`. Verification on bundled CPython 3.12.13 returned `37 passed, 1 StarletteDeprecationWarning`; `git diff --check` passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, real config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, payment provider integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I006` is removed from active/proposed plan. `P6-C002` remains critical gated/deferred for real config delivery, public token redeem, token issue runtime and secret-bearing config output. AMN2 current head `d96112c` is not package-rebuilt or VPS-smoked; latest VPS-smoked/package head remains `b3102db`.

Phase 6 operator proposal added `P6-I007` Interactive fresh-install wizard/bootstrap automation as a very-important local-only task and `P6-C007` Destructive cleanup/reinstall gate for the current working VPS as critical gated/deferred work. The current working server was identified by the operator as `89.185.80.166`. `P6-I007` is scoped to local-only code/docs/tests for a future question-and-answer installer with safe defaults, preflight validation, dry-run output and operator-provided secrets. `P6-C007` is deferred until the operator explicitly decides to assemble/test the clean installer and requires a separate named destructive gate, explicit retention/data-loss decision and stop criteria. No live VPS command, SSH command, cleanup, reinstall, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, Telegram action, secret publication or upstream/GPL code copy was performed by adding this plan item.

Phase 6 `P6-C006` live update/smoke for AMN2 `b3102db` was completed on 2026-06-13 as `live-update-smoke-pass`. Evidence: `research/amn2/phase-6-live-update-smoke-b3102db-2026-06-13.md`; package preflight evidence: `research/amn2/phase-6-final-vps-refresh-package-b3102db-2026-06-13.md`. Built and applied `dist/amn2-vps-update-and-smoke-kit-b3102db.zip`, sha256 `B4C3FF33FD0A721C97A83EA8AF08D5E5B6EA5E8D1862EEB63494E8842D56A21B`, from source zip `dist/amn2-codex-vps-test-prep-b3102db-source.zip`, sha256 `72342DB625D53AE2F6B68835A1FC4E080684A4A1E9018E791820899BB9A09778`. Source overlay updated `/opt/amn2` from `2215761` to `b3102db250da7ca9aef78ca095602187d0efc462`; source update run_id `20260613T154511Z` passed; manual web/bot runtime was restarted with web bound to `127.0.0.1:3030`; read-only API smoke run_id `20260613T154826Z` passed with auth/listener/audit `passed`. A first smoke attempt was blocked because the default server name `debian-vps-1` was absent and this target uses `local`; the successful smoke explicitly used `AMN2_SERVER_NAME=local`. Final remote listener snapshot showed only `127.0.0.1:3030`, with `3040/80/443` absent; external probes returned `000`; `VPS_APPLY_ENABLED=false` remained explicit. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, public exposure change, Telegram token use by Codex, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C006` is removed from the active Phase 6 plan. Next recommendation: `P6-C002 + P6-I006` as local-only design/implementation for short one-tap tokenized config-link boundary plus commercial entitlement/audit boundary.

Phase 6 `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary, `P6-X001` Public product copy polish and `P6-X002` Brand/media consistency were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-client-compatibility-copy-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `b3102db Add client compatibility delivery boundary` and was pushed to `amn2/codex-vps-test-prep`; this head is now also the latest VPS-smoked/package head after `P6-C006`. The slice adds explicit client roles for iOS DefaultVPN as the primary RF-available iOS path, iOS AmneziaWG/Apple as an installed/legacy path, and Android AmneziaWG as a separate supported path; aligns Telegram delivery copy, web Config templates copy, API/web `/integration-status`, README and setup docs; keeps `.conf` as the first fallback; and records short one-tap tokenized config delivery links as part of `P6-C002`. Verification returned RED client/status tests, focused `26 passed, 1 warning`, expanded `290 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No config delivery, write API, public exposure, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M004`, `P6-X001` and `P6-X002` are removed from the active Phase 6 plan.

Phase 6 field diagnostic on 2026-06-13 added `P6-M004` iOS AmneziaWG import/connectivity diagnostic boundary as an important active task and `P6-C006` Final VPS package refresh/apply gate as critical gated/deferred work. Evidence: `research/amn2/phase-6-ios-amneziawg-field-diagnostic-2026-06-13.md`. Local-only review of the user-provided iPhone AmneziaWG log/screenshots showed the existing profile starts the tunnel and sends handshake traffic, but receives zero bytes, keeps `last_handshake_time_sec=0`, and times out after 12 seconds on the observed 2026-06-13 attempts. This points more toward reachability/live server/UDP/firewall/endpoint-port/server-key/peer-applied-state than local config syntax, but proof requires a separate named live diagnostic gate. A separate reported issue remains: new QR/`vpn://` import is not accepted by the iPhone AmneziaWG app. `P6-M004` must distinguish iOS DefaultVPN as the primary RF-available path, iOS AmneziaWG as an installed/legacy-client path, and Android AmneziaWG as a separate supported-client path. `P6-C006` is reserved for the end of Phase 6: package rebuild/apply, service restart, live bot verification and VPS smoke only after explicit named approval. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Its next recommendation was completed by `P6-M004` + `P6-X001` + `P6-X002`.

Phase 6 `P6-N004` Aggregate telemetry retention/redaction policy and `P6-S002` Recurring upstream refresh incorporation were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-telemetry-retention-upstream-refresh-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `a9f53d7 Add telemetry retention refresh policy` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `a9f53d7` is not package-rebuilt or VPS-smoked. The slice adds a retention/redaction and upstream refresh incorporation manifest, keeps raw telemetry export and upstream refresh live actions blocked, records weekly watcher outputs as candidate rows/evidence only, and exposes the safe boundary through integration status. Verification returned RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `68 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-N004` and `P6-S002` are removed from the active Phase 6 plan. Its next recommendation was completed by `P6-M004` + `P6-X001` + `P6-X002`; `P6-N001` remains conditional on public docs approval.

Phase 6 `P6-S003` Project operating system extraction template was completed as AMN3 docs-only work on 2026-06-13. Evidence: `research/amn2/phase-6-project-operating-system-template-2026-06-13.md`. Created clean reusable templates `docs/templates/PROJECT_OPERATING_SYSTEM_TEMPLATE.ru.md` and `docs/templates/NEXT_PROJECT_BOOTSTRAP.ru.md` to preserve the AMN2/AMN3 project-memory method for a future clean project: source of truth, safety boundaries, priority active plan, standing rules, verification/evidence policy, decision log, release/deploy state and next-chat packet. No AMN2 runtime code, live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-S003` is removed from the active Phase 6 plan. Its next recommendation was completed by `P6-N004` + `P6-S002`.

Phase 6 `P6-M003` attach-existing-server reconciliation boundary and `P6-S001` release checklist/changelog were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-reconciliation-release-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `3e1f4cc Add reconciliation release boundary` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `3e1f4cc` is not package-rebuilt or VPS-smoked. The slice adds a report-only attach-existing-server reconciliation and release checklist manifest, keeps live reconciliation, local device creation, peer removal, server config overwrite, package apply/rebuild on VPS, public exposure, config delivery, write API, Local Agent mutation and production peer/user mutation blocked, and exposes the safe boundary through integration status. Verification returned RED `1 error, 1 warning`, focused `11 passed, 1 warning`, expanded `81 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M003` and `P6-S001` are removed from the active Phase 6 plan. Standing-rule addition: `P6-N004` Aggregate telemetry retention/redaction policy is added as a normal-priority Phase 6 task. Its next recommendation was refined to `P6-N004 + P6-S002`.

Phase 6 `P6-M002` health/status polling scheduler boundary and `P6-N002` admin analytics privacy boundary were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-privacy-status-analytics-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `8f4ac6a Add privacy status analytics boundary` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `8f4ac6a` is not package-rebuilt or VPS-smoked. The slice adds an aggregate-only health/status and admin analytics manifest, keeps live probes, raw command output, endpoint/export detail, per-peer health fields and per-user/per-peer analytics detail blocked, sanitizes API integration-status sensitive marker-name lists to counts, adds blocked-future surface policy entries and exposes the safe boundary through integration status. Verification returned RED `1 error, 1 warning`, focused `33 passed, 1 warning`, expanded `65 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M002` and `P6-N002` are removed from the active Phase 6 plan. Its next recommendation was completed by `P6-M003` + `P6-S001`.

Phase 6 `P6-I005` Telegram bot profile/icon apply gates were completed as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-telegram-profile-icon-gate-policy-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `19f3422 Add Telegram profile icon gate policy` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `19f3422` is not package-rebuilt or VPS-smoked. The slice adds a safe profile-icon apply gate manifest for access/support/news bots, records allowed default work as local validation/registry/checklist/safe evidence only, keeps Telegram API profile mutation, BotFather/manual mutation by Codex, live bot send and Telegram token use blocked, adds blocked-future surface policy entries, and exposes the safe gate through integration status. Verification returned RED `6 failed, 27 passed, 1 warning`, focused `33 passed, 1 warning`, expanded `83 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I005` is removed from the active Phase 6 plan. Its next recommendation was completed by `P6-M002` + `P6-N002`.

Phase 6 `P6-I003` payments/manual approval boundary and `P6-I004` support/news bot production split were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-commercial-bot-productization-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `0c6aa7c Add commercial bot productization boundary` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `0c6aa7c` is not package-rebuilt or VPS-smoked. The slice adds a safe productization manifest, keeps payment processor/webhook/automatic entitlement/config delivery on payment blocked, records manual approval as required, records future support/news bots as blocked-future with separate token/runtime requirements, adds blocked-future surface policy entries, and exposes the safe boundary through integration status. Verification returned RED `1 error, 1 warning`, focused `29 passed, 1 warning`, expanded `81 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, payment processor integration, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I003` and `P6-I004` are removed from the active Phase 6 plan. Proposed candidate: `P6-I006` Commercial entitlement/audit boundary, not active until accepted. Next recommendation: `P6-I005` Telegram bot profile/icon apply gates as local-only/docs/tests planning without Telegram identity mutation, live bot send, config/write/public/live gates.

Phase 6 `P6-M001` multi-server/multi-protocol capability registry and `P6-N003` integration status current-head alignment were completed together as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-capability-registry-integration-status-alignment-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced through `4bb7364 Align integration status capability registry` to `3118b43 Make integration status source head dynamic` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `3118b43` is not package-rebuilt or VPS-smoked. The slice adds a safe capability registry to `/api/integration/status` and web `/integration-status`, records current implemented capability as single-server operator control for `amneziawg` on Docker, keeps future `wireguard`/`xray` protocol managers blocked-future with no upstream/GPL code copy, and separates current branch head from latest VPS-smoked/package head via local git with `unknown` fallback outside a checkout. Verification returned RED `3 failed, 5 passed, 1 warning`, focused `8 passed, 1 warning`, expanded `46 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-M001` and `P6-N003` are removed from the active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 `P6-I002` user self-service surface separation was completed as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-user-self-service-surface-boundary-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `b676e1b Add self-service surface boundary` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `b676e1b` is not package-rebuilt or VPS-smoked. The slice adds `self-service` as a distinct blocked-future surface in `app/security/surface_policy.py`, records future `/self-service` dashboard, config delivery and device revoke policies, requires separate self-service auth plus own-account/device boundaries, and verifies no `/self-service*` routes are mounted in the current web/admin app. Verification returned RED `4 failed, 23 passed`, focused `27 passed`, expanded `43 passed, 1 warning`, and AMN2 `git diff --check` plus staged check passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I002` is removed from the active Phase 6 plan. Next recommendation: `P6-I003` Payments/manual approval boundary if commercial access is enabled as local-only/docs/tests planning without opening public/payment-processor/config/write/live gates.

Phase 6 `P6-I001` scoped API tokens production implementation was completed as AMN2 local-only code/tests/docs on 2026-06-13. Evidence: `research/amn2/phase-6-scoped-api-tokens-production-implementation-2026-06-13.md`. AMN2 branch `codex-vps-test-prep` advanced to `0b3ac1f Add API token production policy` and was pushed to `amn2/codex-vps-test-prep`; latest VPS-smoked/package head remains `2215761 Polish operator web admin UX`, and `0b3ac1f` is not package-rebuilt or VPS-smoked. The slice adds a machine-checkable production token policy manifest, keeps allowed route token scopes to `server:read`/`metrics:read`, records blocked future/config/write/backup/Local Agent scopes, enforces a 30-day max TTL for route-connected tokens, aligns the disabled web/admin token form with the same TTL and updates token policy docs. Verification returned focused `18 passed, 1 warning`, expanded `59 passed, 1 warning`, and AMN2 `git diff --check` passed. No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-I001` is removed from the active Phase 6 plan. Its next recommendation was completed by `P6-I002`.

Phase 6 `P6-C005` production security review gate was completed as AMN3 local/docs/security review on 2026-06-13. Evidence: `research/amn2/phase-6-production-security-review-gate-2026-06-13.md`. Decision: `production-security-review-complete-for-planning`; public/self-service launch remains `no-go` until separate named gates. Reviewed AMN3 Phase 6 safety docs and AMN2 controls for public exposure, read-only API/scoped tokens, web/admin state changes, config delivery, Local Agent, backup/restore/import, Telegram bot identity/media, logs/audit/evidence and upstream/license boundary. Focused AMN2 local security regression suite on CPython 3.12.13 returned `98 passed, 1 warning` (`StarletteDeprecationWarning`). No live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. `P6-C005` is removed from the active Phase 6 plan. Follow-up added: `P6-N003` Integration status current-head alignment, normal local-only code/tests/docs.

Phase 5 operator-only pilot handoff was prepared on 2026-06-11 at `docs/NEXT_CHAT_AMN2_PHASE_5_OPERATOR_PILOT.ru.md`. At handoff time it carried remaining Phase 4 conditional directions into Phase 5 with explicit priorities: `P4-PRVTPRO-REFRESH-003` as normal/design-boundary-only, write API/config delivery/public exposure as critical gated work, and `VPS-REBUILD-001` as separate destructive `defer`. `P4-PRVTPRO-REFRESH-003` was later closed in Phase 5 through the AMN3 boundary and `P5-L001` local cached display. Existing upstream heartbeat automations `amnezia-weekly-upstream-refresh`, `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` were updated for Phase 5 prompts without creating duplicates. Because they are heartbeat/thread automations, the new Phase 5 chat should verify whether they post into the intended thread and retarget the same IDs if needed.

Phase 5 `P5-S003` carried-items active-plan cleanup was completed as AMN3 docs-only housekeeping on 2026-06-12. Evidence: `research/amn2/phase-5-carried-items-active-plan-cleanup-2026-06-12.md`. The slice keeps closed carried items visible with their source phase and gate labels, but removes wording that made them look like active pending work. `P4-PRVTPRO-REFRESH-003` is now consistently described as carried from Phase 4, closed in Phase 5: design boundary closed in AMN3, local cached display implemented by `P5-L001`, and live probes/actions still gated. No AMN2 runtime code, live VPS command, SSH command, package apply/rebuild on VPS, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

Phase 5 `P5-C007` live update/smoke for AMN2 `9bff807` was completed on the disposable test VPS on 2026-06-12. Evidence: `research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md`. Package upload/checksum/extract passed, source overlay updated `/opt/amn2` from `de25576` to `9bff807a1d8fcceb833c1ef864064d2af6aaaff1`, read-only API smoke passed with run_id `20260612T184701Z`, and web/bot services are active after restart with loopback `/login` returning `200`. Final remote listener snapshot showed only `127.0.0.1:3030`; `3040`, `80` and `443` were absent as remote listeners. `VPS_APPLY_ENABLED=false` remained explicit. Findings: SSH transport was intermittently flaky during banner exchange; web readiness needed a repeat check after ten seconds; external HTTP probes for public `3030/3040` timed out, while public TCP/HTTP-80 behavior appeared outside AMN2 because remote `ss` showed no `80/443` listener. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, public exposure change or secret-bearing evidence publication was performed.

Phase 5 `P5-O001` operator-only post-update UI smoke for AMN2 `9bff807` was completed as a named gate on 2026-06-12 with decision `needs-fix`. Evidence: `research/amn2/phase-5-operator-post-update-ui-smoke-9bff807-2026-06-12.md`. The operator manually authenticated through an SSH local port forward, and Codex sampled authenticated GET navigation for `/`, `/users`, `/servers`, `/orders`, `/logs`, `/settings`, `/config-templates`, `/api-readiness`, `/integration-status`, `/api-tokens` and `/devices/disabled`. No write action, config delivery, token issue/revoke, Local Agent mutation, package apply/rebuild, service restart/deploy, public exposure change, backup/import/reboot, Telegram action or secret-bearing evidence publication was performed. Findings: several authenticated web/admin surfaces still expose create/write/config/token controls during operator-only smoke, visible menu/section/table copy is still mixed Russian/English, the resource/user display should use `AmneziyaDA` as the resource name with the user shown below it, and dashboard summary cards should center their numeric count and entity label in a two-line layout. These findings were addressed locally by `P5-O002`.

Phase 5 `P5-O002` web-admin gated-action and Russian-first UX cleanup was completed as AMN2 local-only implementation/test work on 2026-06-12 in commit `2215761 Polish operator web admin UX`, pushed to `amn2/codex-vps-test-prep`. Evidence: `research/amn2/phase-5-web-admin-gated-action-russian-ux-2026-06-12.md`. The slice changes the web/admin brand/title suffix to `AmneziyaDA`, makes the sampled authenticated web/admin menu and pages Russian-first, centers dashboard summary cards as two-line count/entity labels, removes active user/server create links from the operator-only list pages, and disables token issue/revoke plus config-template save/reset controls with named-gate notes. Verification: focused `tests/web/test_operator_ui_p5_o002.py` returned `4 passed, 1 warning`; expanded web regression returned `90 passed, 1 warning`; AMN2 `git diff --check` and staged `git diff --cached --check` passed; a temporary local browser smoke on `127.0.0.1:13031` confirmed login, `AmneziyaDA`, Russian-first headings, `1|пользователь`, `1|сервер`, `1|заявка`, `1|устройство`, no active `/users/new` or `/servers/new` links, and disabled token/template submit buttons. No live VPS command, SSH command, package apply/rebuild on VPS, source-overlay update, service restart/deploy, public exposure change, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Its current-head package rebuild recommendation was completed by `P5-C009`.

Phase 5 `P5-C010` live update/smoke for AMN2 `2215761` was completed on the disposable test VPS on 2026-06-13. Evidence: `research/amn2/phase-5-live-update-smoke-2215761-2026-06-13.md`. Package upload/checksum/extract passed, source overlay updated `/opt/amn2` from `9bff807` to `221576169a84bbf662114c564e83c41fba0091b5`, read-only API smoke passed with run_id `20260613T045107Z`, and web/bot services are active after restart with loopback `/login` returning `200`. Final remote listener snapshot showed only `127.0.0.1:3030`; `3040`, `80` and `443` were absent as remote listeners. `VPS_APPLY_ENABLED=false` remained explicit. Findings: SSH transport still showed intermittent access behavior before succeeding with the dedicated target key; external HTTP probes returned empty reply/`000`, while remote listener evidence showed AMN2 did not bind public ports. No config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, public exposure change or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-D001`.

Phase 5 `P5-D001` operator-only pilot acceptance and Phase 6 entry decision was completed as AMN3 docs-only decision work on 2026-06-13. Evidence: `research/amn2/phase-5-operator-pilot-acceptance-phase-6-entry-2026-06-13.md`; Phase 6 handoff: `docs/NEXT_CHAT_AMN2_PHASE_6_PRODUCTIZATION.ru.md`. Decision: `operator-only-pilot-accepted` for the current private/operator-only baseline. AMN2 `2215761` is the current branch head and latest VPS-smoked package/source head; Phase 5 default queue is empty. Phase 6 is `planning-ready only`: public/self-service/productization work may start with a separate security review gate, but public exposure, config delivery, write API, backup/import/reboot, Local Agent write/config routes, destructive rebuild and production peer/user mutation remain not executed and gated. No live VPS command, SSH command, package apply/rebuild, service restart/deploy, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Next recommendation: `P6-C005` Production security review gate as local/docs/security review work.

Phase 5 `P5-C009` current-head package rebuild for AMN2 `2215761` was completed as AMN3 local package work on 2026-06-13. Evidence: `research/amn2/phase-5-current-head-package-rebuild-2215761-2026-06-13.md`. Built `dist/amn2-vps-update-and-smoke-kit-2215761.zip`, package sha256 `6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44`, source zip `dist/amn2-codex-vps-test-prep-2215761-source.zip`, source sha256 `825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B`. Verification: initial system `python` toolchain check failed on Python 3.14.3 as expected, CPython 3.12.13 toolchain check passed, full AMN2 pytest returned `675 passed, 1 warning`, AMN2 `git diff --check` passed, and package hygiene/test-extract passed with `package_entries=5`, `source_files=275`, required entries present, forbidden source entries absent and shell scripts LF/no-BOM. Status at rebuild time was `package-ready-not-vps-smoked`; this was later superseded by `P5-C010` live update/smoke for the same AMN2 head. No live VPS command, SSH command, package apply/rebuild on VPS, source-overlay update, service restart/deploy, public exposure change, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

Phase 5 `P5-C008` current-head package rebuild for AMN2 `9bff807` was completed as AMN3 local package work on 2026-06-12. Evidence: `research/amn2/phase-5-current-head-package-rebuild-9bff807-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-9bff807.zip`, package sha256 `882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9`, source zip `dist/amn2-codex-vps-test-prep-9bff807-source.zip`, source sha256 `5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD`. Verification: the initial system `python` toolchain check failed on Python 3.14.3 as expected, CPython 3.12.13 toolchain check passed, full AMN2 pytest returned `671 passed, 1 warning`, AMN2 `git diff --check` passed, and package hygiene/test-extract passed with `package_entries=5`, `source_files=274`, required entries present, forbidden source entries absent and shell scripts LF/no-BOM. Status at rebuild time was `package-ready-not-vps-smoked`; this was later superseded by `P5-C007` live update/smoke for the same AMN2 head. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

Phase 5 `P5-L002` and `P5-L001` were completed as AMN2 local-only implementation work on 2026-06-12 in commit `9bff807 Add local bot media and status summaries`, pushed to `amn2/codex-vps-test-prep`. Evidence: `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`. `P5-L002` adds local CLI validation/stage/select/manifest support for access/support/news bot media with `start_header` local runtime mapping and `profile_icon` staged-for-operator metadata only. `P5-L001` adds a private web/admin `Read-only server summary` from cached DB health data only. Verification: RED checks failed as expected before implementation, focused final suite returned `71 passed, 1 warning`, full AMN2 suite returned `671 passed, 1 warning`, and git hygiene checks passed. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Because AMN2 advanced to `9bff807`, the previous `dd0dd44` package is superseded as current-head package evidence; the required replacement package was built later in `P5-C008`.

Phase 5 `P5-C006` current-head package rebuild for AMN2 `dd0dd44` was completed as AMN3 local package work on 2026-06-12. Evidence: `research/amn2/phase-5-current-head-package-rebuild-dd0dd44-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip`, package sha256 `BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D`, source zip `dist/amn2-codex-vps-test-prep-dd0dd44-source.zip`, source sha256 `E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1`. Verification: AMN2 toolchain check passed, full AMN2 pytest returned `664 passed, 1 warning`, `git diff --check` passed, package hygiene/test-extract passed with `package_entries=5`, `source_files=271`, required entries present, forbidden source entries absent and shell scripts LF/no-BOM. The kit was tightened so apply uses the full source commit binding and the runbook explicitly states it does not authorize live VPS apply. Status was `package-ready-not-vps-smoked`; latest VPS-smoked source overlay remains `de25576`. It is now superseded as current-head package evidence by AMN2 `9bff807`. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

Phase 5 carried item `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX boundary was completed as AMN3 docs-only design work on 2026-06-12, then its safe local display was implemented by `P5-L001` in AMN2 commit `9bff807`. Boundary doc: `docs/AMN2_READ_ONLY_SERVER_STATUS_LATENCY_UX_BOUNDARY.ru.md`; evidence: `research/amn2/phase-5-prvtpro-server-status-latency-boundary-2026-06-12.md` and `research/amn2/phase-5-local-bot-media-and-status-summaries-2026-06-12.md`. The closed item remains recorded as carried from Phase 4 with `normal` importance. Live probes, SSH, health/sync actions, public exposure, config delivery, write API, Local Agent mutation, raw logs and secret/user/peer fields remain behind separate gates.

Phase 5 `P5-N003` client/platform compatibility refresh was completed as AMN2 local-only plus AMN3 evidence work on 2026-06-12. Evidence: `research/amn2/phase-5-client-platform-compatibility-refresh-2026-06-12.md`; upstream note: `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-12.md`. AMN2 branch `codex-vps-test-prep` advanced to `dd0dd44 Refresh client platform guidance` and was pushed. The slice refreshes AmneziaVPN Linux platform guidance after current upstream metadata showed release `4.8.18.0` assets include generic `linux_x64.tar`: AMN2 now says Linux x64 tar is available but distro-specific Linux packages are not promised. Focused verification: RED `2 failed, 3 passed`; GREEN focused compatibility/bot-delivery `13 passed`; `git diff --check` and staged `git diff --cached --check` passed. Full AMN2 suite was not run for this narrow wording/matrix slice. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed. Its next recommendation was completed by `P4-PRVTPRO-REFRESH-003`.

Phase 5 `P5-N001` operator docs cleanup was completed as AMN3 docs-only housekeeping on 2026-06-12. Evidence: `research/amn2/phase-5-operator-docs-cleanup-2026-06-12.md`. The slice removed stale active references to already closed Phase 5 gate slices, refreshed the operator smoke/evidence rules, updated the forward plan, next-chat handoff, current status, context import and transfer backlog, and keeps `P5-N001` out of the active plan. No AMN2 runtime code, live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-N003`.

Phase 5 `P5-C004` secret handoff protocol was completed as AMN3 docs-only work on 2026-06-12. Protocol: `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`; evidence: `research/amn2/phase-5-secret-handoff-protocol-2026-06-12.md`. The protocol defines `regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets`, secret classes, allowed/forbidden channels, safe evidence summary fields, `.env`/`servers.yml` private-file boundaries, stop lines and related named gates. It also links the fresh deploy runbook to this protocol. No AMN2 runtime code, live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-N001`.

Phase 5 `P5-C005` source-overlay permission preservation fix was completed as AMN3 local package tooling/test work on 2026-06-12. Evidence: `research/amn2/phase-5-source-overlay-permission-preservation-2026-06-12.md`. `scripts/vps/amn2_apply_source_zip.sh` no longer streams tar rooted at staging `.` into `/opt/amn2`; it overlays staging children with Python, preserves target-root metadata, normalizes copied source dirs/files to service-readable group permissions and records `permission_strategy=target-root-metadata-preserved`. Added regression test `tests/test_amn2_apply_source_zip.py`; verification `python -m unittest discover -s tests -p test_amn2_apply_source_zip.py -v` returned `2 passed`. The historical `dist/amn2-vps-update-and-smoke-kit-de25576.zip` remains the immutable P5-C003 evidence artifact; the corrected-script rebuild requirement was later satisfied by `P5-C006` for AMN2 `dd0dd44`. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-C004`.

Phase 5 `P5-C003` live rollout for AMN2 `de25576` was completed on the disposable test VPS on 2026-06-12. Evidence: `research/amn2/phase-5-live-rollout-de25576-2026-06-12.md`. Package upload and checksum passed, source overlay updated `/opt/amn2` from `f7f6131` to `de2557639cd3853e6973002be3cab24033d2f722`, read-only loopback API smoke passed with run_id `20260612T054913Z`, and web/bot services are active with `/login` returning `200` on loopback. Final listener snapshot showed only `127.0.0.1:3030`; `3040`, `80` and `443` were absent after smoke. `VPS_APPLY_ENABLED=false` remained explicit. The gate found two follow-ups: set `AMN2_SERVER_NAME=local` for this target's smoke runs, and fix source-overlay permission preservation because the inherited apply script temporarily changed `/opt/amn2` source permissions to `root:root 700`; live permissions were repaired to `root:amneziya` service-mode values. No public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action or secret-bearing evidence publication was performed. Its next recommendation was completed by `P5-C005`.

Phase 5 `P5-C001` current-head package rebuild was completed as AMN3 local-only package work on 2026-06-12. Evidence: `research/amn2/phase-5-current-head-package-rebuild-2026-06-12.md`. Built `dist/amn2-vps-update-and-smoke-kit-de25576.zip` from AMN2 `de2557639cd3853e6973002be3cab24033d2f722`; package sha256 `B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87`; source sha256 `CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC`; package hygiene/test-extract passed with `package_entries=5`, `source_entries=313` and `forbidden_source_entries=0`. AMN2 verification: `python -m app.toolchain check` passed and full pytest returned `664 passed, 1 warning`. Its next recommendation was completed by `P5-C003`.

Phase 5 `P5-C002` VPS retention decision was completed as AMN3 docs-only on 2026-06-12. Evidence: `research/amn2/phase-5-vps-retention-disposable-test-server-2026-06-12.md`. The operator clarified that the current target server is a disposable test VPS created for testing with Codex and project-completion work, has no important data to preserve, and may lose current state within an explicitly opened named gate. This closes the retention/snapshot blocker for the current test VPS, but does not by itself authorize live VPS commands, SSH, package apply, service restart/deploy, wipe/reinstall, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production peer/user mutation. Its next recommendation was completed by `P5-C001`.

Phase 5 `P5-S002` Удалять устаревшие рекомендации после каждого закрытого slice was completed as AMN3 docs-only housekeeping on 2026-06-12. Evidence: `research/amn2/phase-5-active-plan-stale-recommendation-cleanup-2026-06-12.md`. The slice removes stale active-plan/recommendation references after `P5-X002` and `P5-X001`, records simple/cosmetic groups as empty, and leaves only conditional/gated Phase 5 work. No AMN2 runtime, tests, templates, bot delivery code, web panel code, database or package artifact changed. Verification: stale recommendation scan produced no active stale matches after cleanup, `git diff --check` passed. No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its later conditional path was completed through `P5-C002`, `P5-C001`, `P5-C003`, `P5-C005`, `P5-C004` and `P5-N001`.

Phase 5 `P5-X001` Полировка Russian-first микротекстов was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-russian-first-microtexts-2026-06-11.md`. AMN2 branch `codex/bot-labels-russian-copy`, commit `de25576`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice translates the most visible bot/admin template, bot tariff/device duration and web-panel operator-boundary microtexts to Russian-first wording while preserving stable technical IDs and user-provided tariff names. Verification: RED `7 failed, 23 passed, 1 warning`, focused `30 passed, 1 warning`, bot/web slice `152 passed, 1 warning`, full AMN2 suite `664 passed, 1 warning`, `git diff --check` passed. No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-S002`.

Phase 5 `P5-X002` Единообразие bot button labels and captions was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-bot-labels-captions-2026-06-11.md`. AMN2 branch `codex/bot-labels-russian-copy`, commit `fed832c`, was fast-forwarded into `amn2/codex-vps-test-prep` as part of the `de25576` push. The slice clarifies `.conf`, QR and `vpn://` delivery captions/messages in Russian-first copy without changing config generation, QR payloads, Telegram keyboard behavior or transport behavior. Verification: RED `2 failed, 6 passed`, focused `43 passed`, bot suite `105 passed`, combined final full AMN2 suite at `de25576` `664 passed, 1 warning`, `git diff --check` passed. No live Telegram send, Telegram token use, real config delivery, live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-X001`.

Phase 5 `P5-N002` Полировка текста веб-панели для service-mode и external-only устройств was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-web-panel-service-mode-copy-2026-06-11.md`. AMN2 branch `codex/web-panel-service-external-copy`, commit `17454e9`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice clarifies `/integration-status` operator-only boundary, `/servers/{id}` read-only health/sync action notes, and `/users/{id}` `external_only` device wording without changing routes, actions, permissions, config generation or delivery behavior. Verification: RED `3 failed, 1 passed, 1 warning`, focused `4 passed, 1 warning`, web slice `47 passed, 1 warning`, full AMN2 suite `664 passed, 1 warning`, `git diff --check` passed. No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-X002`.

Phase 5 `P5-M006` Одно нажатие для копирования import-ссылки в Telegram was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-telegram-import-link-copy-2026-06-11.md`. AMN2 branch `codex/telegram-copy-import-link`, commit `ad6aa1b`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice keeps the `vpn://` import link as a separate Telegram message and adds an inline `Скопировать ссылку` copy button only when the exact full link fits Telegram `copy_text` payload limits. Over-limit raw `vpn://` links keep visible text plus `.conf`/QR fallback and do not receive a misleading copy button. Verification: RED `3 failed, 40 passed` as expected, focused `43 passed`, related bot/config suite `108 passed`, full AMN2 suite `664 passed, 1 warning`, `git diff --check` passed. No live Telegram send, Telegram token use, real config delivery, live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-N002`.

Phase 5 `P5-M002` QA клиентских инструкций доставки конфигурации was completed as AMN3 docs-only/local-only on 2026-06-11. QA doc: `docs/AMN2_CLIENT_CONFIG_DELIVERY_QA.ru.md`; evidence: `research/amn2/phase-5-client-config-delivery-qa-2026-06-11.md`. It defines safe Telegram `.conf`/QR/`vpn://` review for Android/iOS/Desktop, redacted evidence policy, pass/fallback/stop criteria and the operator requirement that the import link may be sent as a separate message but must copy to clipboard with one tap. Current AMN2 plain text `vpn://` delivery was not treated as satisfying that one-tap copy requirement; its next recommendation was completed by `P5-M006` Telegram import link copy affordance. No AMN2 runtime code, bot handler, keyboard, template, config generator, test change, live Telegram send, Telegram token use, real config delivery, public exposure, live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed during `P5-M002`.

Phase 5 `P5-M004` граница ассета шапки веб-панели was completed as AMN3 docs-only/local-only on 2026-06-11. Boundary doc: `docs/AMN2_WEB_ADMIN_HEADER_ASSET_BOUNDARY.ru.md`; evidence: `research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md`. It assigns `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` to the web/admin product surface only, keeps it out of access/support/news bots and Telegram profile icons, records Russian-first active-plan naming, and preserves operator-only web/admin mode: loopback `127.0.0.1:3030`, SSH local port forward, no direct public `3030`, no public API `3040`, no domain/Caddy/HTTPS cutover by default. No AMN2 runtime code, asset copy, upload handler, static route, template change, web/admin runtime change, public exposure, live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-M002` QA клиентских инструкций доставки конфигурации.

Phase 5 `P5-M005` bot media asset upload/apply boundary was completed as AMN3 docs-only/local-only on 2026-06-11. Boundary doc: `docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md`; evidence: `research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md`. It defines the future operator-only local validation/registry model for access/support/news bot media, separates `start_header` local runtime assets from `profile_icon` Telegram identity, and keeps any Bot API or manual profile-icon apply behind a named Telegram identity gate. No AMN2 runtime code, upload handler, web route, CLI command, asset copy, Telegram API call, Telegram token use, live bot send, bot profile icon/avatar mutation, live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-M004` Граница ассета шапки веб-панели.

Phase 5 `P5-M001` support/news bot asset inventory was completed as AMN3 docs-only/local-only on 2026-06-11. Inventory doc: `docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md`; evidence: `research/amn2/phase-5-support-news-bot-asset-inventory-2026-06-11.md`. It records that current AMN2 only tracks `NEOBYATNAYA-AMNZ-BOT.png` for the existing access bot, while `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png`, `NEOBYATNAYA-AMNZ-NEWS-BOT.png` and `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` remain planning-only references. Future support/news bots require separate tokens, runtime decisions, command boundaries and local tests; they must not issue configs, mutate peers/users, expose private state or reuse the access-bot runtime by default. Bot media is split into AMN2 runtime header images and Telegram profile icons/avatars; header upload can be future local-only operator registry work, while profile icon apply is live Telegram identity mutation requiring a named gate. No AMN2 runtime code, asset copy, live Telegram send, bot profile icon/avatar mutation, live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-M005` Bot media asset upload/apply boundary.

Phase 5 `P5-M003` AMN3 evidence discipline was completed as AMN3 docs-only/local-only on 2026-06-11. Discipline doc: `docs/AMN3_PHASE5_EVIDENCE_DISCIPLINE.ru.md`; evidence: `research/amn2/phase-5-amn3-evidence-discipline-2026-06-11.md`. It defines scope classes, required evidence file naming, closeout packet fields, status/backlog/forward-plan/next-chat/context sync, active-plan cleanup, safe evidence policy, verification minimums and stop conditions for Phase 5. No live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-M001` Support/news bot asset inventory.

Phase 5 `P5-I004` operator-only smoke checklist was completed as AMN3 docs-only/local-only on 2026-06-11. Checklist: `docs/AMN2_OPERATOR_ONLY_SMOKE_CHECKLIST.ru.md`; evidence: `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`. It defines safe checklist fields for web/admin loopback, bot dry/local behavior, the six private/local read-only API routes, no-public-exposure checks and stop lines for write/config/public/destructive/live actions. No live VPS command, SSH command, service restart, deploy, package apply/rebuild, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed. Its next recommendation was completed by `P5-M003` AMN3 evidence discipline. Automation startup note: `amnezia-weekly-upstream-refresh` was retargeted to this Phase 5 thread; the app rejected attaching additional active heartbeat automations to the same thread, so `prvtpro-weekly-upstream-refresh` and `weekly-kyoresuas-upstream-refresh` remain on their prior thread bindings unless the operator chooses a separate consolidation policy.

Phase 4 main-chat handoff is prepared at `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`, with research note `research/amn2/phase-4-unified-product-gate-handoff-2026-06-09.md`. Phase 4 accepts the Phase 3 service-mode loopback baseline as closed and starts as a local/read-only unified product gate for AMN2/API, target VPS, PRVTPRO/Web Panel and KYORESUAS/API coordination. It does not authorize new live commands, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation.

Phase 4 bot config delivery localization and DefaultVPN UX fix was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-4-bot-config-delivery-localization-2026-06-11.md`; upstream reference: `research/upstreams/amnezia-vpn-client-defaultvpn-refresh-2026-06-11.md`. AMN2 branch `codex/bot-russian-config-delivery`, commit `908cafc`, was also fast-forwarded into `codex-vps-test-prep` and pushed. The slice makes Telegram config delivery Russian-first, sends `vpn://` and app links as separate messages, uses device-name-based config filenames, labels `.conf` and QR captions in Russian, and avoids promising universal DefaultVPN in-app QR compatibility. Its initial `Neobyatnaya-AMNZ-{order_id}` naming was superseded by the later device sequence slice below. Verification: focused bot/config suite `62 passed`, email regression `15 passed, 1 warning`, full AMN2 suite `630 passed, 1 warning`, `git diff --check` passed. No live VPS command, SSH command, live bot restart/deploy, real config delivery by Codex, production mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed. Operational note: earlier VPS rebuild package evidence is based on AMN2 `1508e3c`; any future VPS package apply/rebuild must rebuild from the selected current AMN2 head and rerun source/package precheck first.

Phase 4 device sequence and external import visibility was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-4-device-sequence-external-import-2026-06-11.md`. AMN2 branch `codex/device-sequence-existing-peers`, commit `59bc266`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice changes bot-approved device names to a shared `Neobyatnaya-AMNZ` sequence seeded after the four existing test configs, adds local external-only device import/backfill, shows imported devices in bot and web/admin user detail, and blocks resend/secrets/email-config for records that lack original client config material. Verification: focused suite `171 passed, 1 warning`, full AMN2 suite `644 passed, 1 warning`, `git diff --check` and staged `git diff --cached --check` passed. No live VPS command, SSH command, service restart, real config delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed. Its next safe local-only recommendation, `P4-AMNEZIA-REFRESH-002`, was later completed as the compatibility matrix slice below.

Phase 4 `P4-AMNEZIA-REFRESH-002` client import compatibility matrix was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-4-amnezia-client-compatibility-matrix-2026-06-11.md`. AMN2 branch `codex/amnezia-client-compatibility-matrix`, commit `d2e234f`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice adds a machine-checkable matrix for `.conf`, `vpn://`, QR `vpn://` payload, DefaultVPN reliability, standalone AmneziaWG clients and current AmneziaVPN release/platform constraints, then includes safe Russian compatibility guidance in the bot app-links message. Verification: focused suite `69 passed`, full AMN2 suite `650 passed, 1 warning`, `git diff --check` and staged `git diff --cached --check` passed. No live VPS command, SSH command, service restart, deploy, real config delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed. The bot asset gap found by this slice was superseded by later completed `P4-BOT-ONBOARDING-001`.

Phase 4 `P4-BOT-ONBOARDING-001` bot onboarding language/header was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-4-bot-onboarding-language-header-2026-06-11.md`. AMN2 branch `codex/bot-onboarding-language-header`, commit `137d471`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice adds the supplied `NEOBYATNAYA-AMNZ-BOT.png` as the access-bot header, sends it on `/start`, shows `🌐 Выберите язык / Choose your language:` with `🇷🇺 Русский` and `🇬🇧 English`, persists `users.locale` with Russian default and renders the selected main menu locale. Support/news/admin images were recorded for future planning only, not enabled in the current bot runtime. Verification: RED import errors as expected before implementation, focused `5 passed`, full AMN2 suite `654 passed, 1 warning`, staged `git diff --cached --check` passed. No live VPS command, SSH command, service restart, deploy, real config delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed. Its next recommendation was completed by the Phase 5 runtime/toolchain slice below.

Phase 5 `P5-I003` runtime/toolchain standardization was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md`. AMN2 branch `codex/runtime-toolchain-standardization`, commit `578d91e`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice pins `pyproject.toml` to `>=3.12,<3.13`, adds `app.toolchain` with `python -m app.toolchain check`, documents CPython 3.12.x bootstrap in `docs/RUNTIME_TOOLCHAIN.ru.md`, and codifies one local `.venv` per worktree so Windows sandbox runs no longer depend on a neighboring worktree environment. Verification: RED failed on missing `app.toolchain` as expected, focused `4 passed`, runtime/hygiene regression `19 passed`, full AMN2 suite `658 passed, 1 warning`, `git diff --check` and staged `git diff --cached --check` passed. No live VPS command, SSH command, service restart, deploy, package apply, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream code copy was performed. Python 3.14 remains a separate future upgrade gate, not enabled by this slice.

Phase 5 `P5-I002` external-only backfill rehearsal was completed in AMN2 on 2026-06-11. Evidence: `research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md`. AMN2 branch `codex/external-only-backfill-rehearsal`, commit `23f18ef`, was fast-forwarded into `amn2/codex-vps-test-prep` and pushed. The slice adds `python -m app.cli device backfill-external` for JSON-based dry-run and apply-to-copy rehearsal of old externally issued test devices. Dry-run does not create or mutate `--db-copy`; apply writes only to the operator-specified local DB copy; imported rows remain `config_material_status=external_only`, config resend is unavailable, and secret-bearing input fields are rejected before any DB write. Verification: RED failed on missing `run_device_backfill_external` as expected, focused `6 passed`, related bot/web/config suite `58 passed, 1 warning`, full AMN2 suite `662 passed, 1 warning`, `git diff --check` and staged `git diff --cached --check` passed. No live VPS command, SSH command, service restart, deploy, package apply, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream code copy was performed. Its next recommendation was completed by `P5-I004` operator-only smoke checklist.

Phase 4 first local-only slice `P4-C009` web-panel user/config visibility was implemented locally on 2026-06-09. Evidence: `research/amn2/phase-4-web-panel-user-config-visibility-implementation-2026-06-09.md`. Root cause: `/users` lists local AMN2 DB users/devices only; live VPS peers created outside AMN2 are surfaced through server peer-sync/read-only inventory, not automatic user/config backfill. Local AMN2 tests passed focused verification with `26 passed, 1 warning`; no live VPS commands or write/config/token/sync/apply/revoke/backup/import/reboot actions were performed.

Phase 4 second local-only slice `P4-I002` service-mode/read-only status wording was implemented locally on 2026-06-09. Evidence: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-service-mode-status-wording`, commit `83f6d28`, updates `/integration-status` to report `service_mode_loopback_ready` and show a `Service-mode boundary` panel for loopback-only web/admin `127.0.0.1:3030`, SSH tunnel access, absent/closed public API `3040`, absent TCP `80/443`, deferred domain/HTTPS cutover and `VPS_APPLY_ENABLED=false`. Focused verification passed with `7 passed, 1 warning`; no live VPS commands or write/config/token/sync/apply/revoke/backup/import/reboot actions were performed. Historical next-step note was superseded by later route/secret work and `P4-I001` closure.

Phase 4 route/secret gate planning was completed as AMN3 docs-only on 2026-06-09. Evidence: `research/amn2/phase-4-route-secret-gate-plan-2026-06-09.md`. It consolidates route/auth binding, secret inventory, token lifecycle, public config policy, manager config export, backup/import policy and service-mode status baselines into a mandatory proposal/checklist before future API route expansion. It does not authorize AMN2 code changes, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or live VPS commands.

Phase 4 `P4-I003` read-only API/status schema maturity design was completed as AMN3 docs-only on 2026-06-09. Evidence: `research/amn2/phase-4-read-only-api-status-design-2026-06-09.md`. It binds the next safe AMN2 local implementation slice to the existing six read-only API routes, `server:read`/`metrics:read` scope split, safe `api_read` audit metadata, forbidden-marker checks, `checked_routes=6` and the service-mode boundary in `/api/integration/status`. It does not authorize AMN2 code changes by itself, live VPS commands, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation. Next recommendation: prepare the AMN2 local implementation plan for schema/docs/tests only.

Phase 4 `P4-I003` AMN2 local implementation plan was completed as AMN3 docs-only on 2026-06-09. Plan: `docs/superpowers/plans/2026-06-09-amn2-p4-i003-read-only-api-status-schema.md`. It defines branch `codex/phase-4-read-only-api-status-schema` and restricts execution to API runtime bindings, route drift tests, read-only API/status contract tests, safe audit checks and AMN2 docs. It does not run AMN2 code changes yet, live VPS commands, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation. Next recommendation: execute this AMN2 local plan.

Phase 4 `P4-I003` read-only API/status schema implementation was completed locally in AMN2 on 2026-06-09. Evidence: `research/amn2/phase-4-read-only-api-status-schema-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-read-only-api-status-schema`, commit `b71b8f4`, adds `API_RUNTIME_ROUTE_BINDINGS`, route drift tests, read-only API/status contract tests, updated service-mode API expectations and AMN2 policy docs. Verification: RED failed on missing binding as expected; final focused suite passed with `56 passed, 1 warning`; `git diff --check` passed. No live VPS commands, new routes, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed. Follow-up endpoint taxonomy / route-policy docs alignment was selected next.

Phase 4 `P4-I004` endpoint taxonomy / route-policy docs alignment was completed locally in AMN2 on 2026-06-09. Evidence: `research/amn2/phase-4-endpoint-taxonomy-route-policy-docs-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-endpoint-taxonomy-route-policy-docs`, commit `acf39f8`, adds `docs/API_ENDPOINT_TAXONOMY.ru.md` and links route/auth, token policy and phase map docs to the private/local taxonomy for the same six read-only `/api/*` routes. Verification: `git diff --check` passed, forbidden enabled-marker scan passed with no matches, focused policy/contract regression passed with `33 passed, 1 warning`. No live VPS commands, runtime route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed. Follow-up aggregate metrics privacy boundary visibility was selected next.

Phase 4 `P4-N003` aggregate metrics privacy boundary was completed locally in AMN2 on 2026-06-09. Evidence: `research/amn2/phase-4-aggregate-metrics-privacy-boundary-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-aggregate-metrics-privacy-boundary`, commit `8b6aef8`, adds an additive safe `privacy` marker to `GET /api/metrics/summary`: `aggregate_only=true`, `per_peer_fields=false`, `per_user_fields=false`, `public_exposure=false`. The route remains `metrics:read`, aggregate-only and local/private by policy. Verification: RED failed on the missing privacy marker as expected; extended focused regression passed with `50 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, token lifecycle actions, backup/import/reboot or production peer/user mutation were performed. Follow-up `P4-I005` was selected and completed next.

Phase 4 `P4-I005` API token lifecycle boundary was completed locally in AMN2 on 2026-06-09. Evidence: `research/amn2/phase-4-api-token-lifecycle-boundary-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-api-token-lifecycle-boundary`, commit `22061ea`, adds an additive safe `api_token_lifecycle_boundary` marker to `GET /api/integration/status`: route-connected tokens require explicit expiry, secrets are one-time display only, storage is `sha256_digest_only`, allowed scopes remain `metrics:read`/`server:read`, config/write/destructive scope classes remain blocked, owner status is enforced, revoke is idempotent, rotation is create-new-then-revoke-old, and production token mutation is false. Verification: RED failed on the missing lifecycle marker as expected; extended focused regression passed with `59 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route count changes, token issue/revoke/rotate API routes, production token mutation, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot or production peer/user mutation were performed. Follow-up `P4-N004` was selected and completed next.

Phase 4 `P4-N004` bot/admin read-only labels was completed locally in AMN2 on 2026-06-09. Evidence: `research/amn2/phase-4-bot-admin-read-only-labels-implementation-2026-06-09.md`. AMN2 branch `codex/phase-4-bot-admin-read-only-labels`, commit `c9829b7`, adds service-mode SSH tunnel/loopback and gated write/config/public labels to web admin navigation, clarifies users/servers empty states as local AMN2 records versus live VPS inventory, and marks bot admin traffic/users views as aggregate/local. Verification: RED failed on the missing labels as expected; extended regression passed with `238 passed, 1 warning`; `git diff --check` and marker scan passed. No live VPS commands, route changes, callback changes, POST behavior changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-N001` was selected and completed next.

Phase 4 `P4-N001` docs/status drift synchronization was completed as AMN3 docs-only/local-only on 2026-06-09. Evidence: `research/amn2/phase-4-docs-status-drift-sync-2026-06-09.md`. The sync aligned the active candidate registry, transfer backlog, current status, next-chat packet, Phase 4 handoff, active plan and context import after `P4-N004`; earlier next-step recommendations inside old evidence files were classified as historical chronology. No AMN2 code, live VPS commands, route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-N002` was selected and completed next.

Phase 4 `P4-N002` protocol manager interface checklist was completed as AMN3 docs-only/local-only on 2026-06-09. Evidence: `research/amn2/phase-4-protocol-manager-interface-checklist-2026-06-09.md`. The checklist maps PRVTPRO manager-architecture ideas onto existing AMN2 `RemoteOperation`/`OperationPlan`, partial-failure and `ConfigExportResult` baselines, requiring explicit capabilities, gate class, risk/secret classification, fake-runner tests, safe metadata and license boundaries before any future manager/plugin implementation. No AMN2 code, live VPS commands, route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-X003` was selected and completed next.

Phase 4 `P4-X003` Russian-first operator docs polish was completed as AMN3 docs-only/local-only on 2026-06-09. Evidence: `research/amn2/phase-4-russian-first-operator-docs-polish-2026-06-09.md`. The polish updates active Phase 4 operator-facing handoff/status/plan headings and copy-paste next-chat wording to Russian-first style while preserving technical IDs, route names, gates, file paths and safety boundaries. No AMN2 code, live VPS commands, route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-X002` was selected and completed next.

Phase 4 `P4-X002` API/status/gate naming cleanup was completed as AMN3 docs-only/local-only on 2026-06-09. Evidence: `research/amn2/phase-4-api-status-gate-naming-cleanup-2026-06-09.md`. The cleanup defines active Phase 4 meanings for `service-mode`, `loopback-only`, `SSH tunnel`, `local-only`, `read-only`, `requires VPS gate`, `blocked`, `deferred`, `public exposure` and `config delivery` while preserving technical IDs, route names and safety boundaries. No AMN2 code, live VPS commands, route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-X001` was selected and completed next.

Phase 4 `P4-X001` read-only API docs grouping polish was completed as AMN3 docs-only/local-only on 2026-06-09. Evidence: `research/amn2/phase-4-read-only-api-docs-grouping-polish-2026-06-09.md`. The polish groups the current six private/local read-only API routes for operator/integrator navigation: server inventory/status (`GET /api/servers`, `GET /api/servers/{server_name}/summary`), integration/service boundary (`GET /api/integration/status`), Local Agent runtime summary (`GET /api/local-agent/runtime/summary`) and aggregate metrics (`GET /api/metrics/summary`, `GET /api/users/summary`). Scope split remains `server:read` and `metrics:read`; `checked_routes` remains six. No AMN2 code, live VPS commands, route changes, public OpenAPI/docs exposure, public API `3040`, direct public web/admin `3030`, config delivery, `/api/clients` CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Follow-up `P4-I001` closure was selected and completed next.

Phase 4 `P4-I001` second read-only UX pass was closed as AMN3 docs-only decision on 2026-06-10. Evidence: `research/amn2/phase-4-p4-i001-read-only-ux-pass-closure-2026-06-10.md`. The second pass was not run and no new page-level findings were collected; this records the operator decision to close the optional fallback so Phase 4 does not keep returning to it. Existing safe evidence and local/default slices (`P4-C009`, `P4-I002`, `P4-N004`, `P4-X003`, `P4-X002`, `P4-X001`) are treated as sufficient for the current boundary. No AMN2 code, live VPS commands, SSH-tunnel browser review, public exposure, config delivery, write CRUD, Local Agent mutations, backup/import/reboot, token issue/revoke/rotate API routes or production peer/user mutation were performed. Default local-only Phase 4 implementation queue is now closed except minimal maintenance; any VPS/live/public/write/config direction requires a separate named gate/decision first.

Phase 4 `P4-NG` Named Gate / Write API Readiness was started as AMN3 docs-only planning on 2026-06-10. Plan: `docs/superpowers/plans/2026-06-10-p4-ng-named-gate-write-api-readiness.md`. Charter/evidence: `research/amn2/phase-4-ng-gate-charter-and-plan-2026-06-10.md`. `NG-C001` named gate charter and `NG-C002` safety boundary restatement are closed and removed from the active plan. Follow-up `NG-C003` and `NG-C004` were selected and completed next. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. `NG-V001` read-only VPS baseline gate later gained the `NG-SC001` Codex Security checkpoint and was closed as `go`; write API live work remains blocked until a separate `P4-NG-WRITE-API-LIVE-GATE`.

Phase 4 `NG-C003` secrets policy and `NG-C004` go/no-go format were completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-secrets-policy-go-no-go-format-2026-06-10.md`. Reusable template: `research/amn2/phase-4-ng-named-gate-evidence-template-2026-06-10.md`. `NG-S003` reusable named-gate evidence template was also closed because the template is required for `NG-C003` and `NG-C004`. The template allows only boolean/status summaries and safe aggregate counts, forbids secret-bearing output, and requires exactly one `go_no_go_decision: go | no-go | defer`. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `NG-C005` was selected and completed next.

Phase 4 `NG-C005` write API live-block assertion was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-write-api-live-block-assertion-2026-06-10.md`. It records `live_write_authorized: no` and requires every future write API design or implementation slice to state its live-write status explicitly. The selected next slice was `WAPI-V001` write API threat model, docs-only, with `live_write_authorized: no`. No AMN2 code, live VPS command, SSH command, route expansion, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-V001` was selected and completed next.

Phase 4 `WAPI-V001` write API threat model was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-v001-write-api-threat-model-2026-06-10.md`. It defines protected assets, trust boundaries, threat classes and required future test classes for `/api/clients`, peer lifecycle, config delivery coupling, token scopes, audit, idempotency, locking and partial failures. It explicitly carries KYORESUAS refresh signals for operation lock/serialization, atomic config write, `active|disabled` plus `expiresAt` lifecycle wording, QR/`vpn://` secret-read tests, rate-limit/Helmet-style public hardening and setup resilience without copying upstream code. It keeps `live_write_authorized: no`; no runtime route expansion, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-V002` was selected and completed next.

Phase 4 `WAPI-V002` write API route taxonomy was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-v002-write-api-route-taxonomy-2026-06-10.md`. It classifies future route groups (`clients`, `peers`, `configs`, `operations`, `audit_status`), candidate route names, route classes, minimal scopes, side effects, named gates and required tests before any implementation. It keeps `live_write_authorized: no`; candidate names are planning placeholders only, and no runtime route expansion, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-V003` was selected and completed next.

Phase 4 `WAPI-V003` local fake-runner contract was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-v003-local-fake-runner-contract-2026-06-10.md`. It defines future fake-runner inputs, outputs, operation intents, deterministic failure modes, audit-safe metadata and RED test requirements for create/disable/revoke/sync/retry operation plans. It keeps `live_write_authorized: no`; no runner code, runtime route expansion, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-V004` was selected and completed next.

Phase 4 `WAPI-V004` idempotency, locking and partial-failure model was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-v004-idempotency-locking-partial-failure-model-2026-06-10.md`. It defines request idempotency keys, per-target locks, retry behavior, conflict statuses, partial-failure vocabulary and safe mapping from historical VPS evidence (`dry-run-only-pass`, single-disposable-peer `verified-live`, service-mode loopback baseline) without treating that evidence as current live/write permission. It keeps `live_write_authorized: no`; no runtime route expansion, fake-runner code, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-V005` was selected and completed next.

Phase 4 `WAPI-V005` write API audit/redaction requirements was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-v005-write-api-audit-redaction-requirements-2026-06-10.md`. It defines required safe audit fields, forbidden secret-bearing fields, redaction rules, event types, audit failure behavior and RED test requirements before any write API route, fake-runner or audit schema implementation. It keeps `live_write_authorized: no`; historical VPS evidence may be referenced only as safe labels/status vocabulary, not as command output, endpoint data or current live permission. No runtime route expansion, audit schema implementation, fake-runner code, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-I004` was selected and completed next.

Phase 4 `WAPI-I004` operation status model was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-i004-operation-status-model-2026-06-10.md`. It consolidates `WAPI-V004` status vocabulary and `WAPI-V005` audit/redaction constraints into safe operation status fields, canonical statuses, reason codes, transition rules, visibility tiers and RED test requirements. It keeps `live_write_authorized: no`; historical VPS evidence may appear only as safe status labels and never as command output, endpoint data, logs or current permission. No runtime route expansion, operation status schema implementation, operation queue implementation, fake-runner code, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, token issue/revoke/rotate API route or production peer/user mutation was performed. Follow-up `WAPI-I003` was selected and completed next.

Phase 4 `WAPI-I003` scoped write-token model was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-i003-scoped-write-token-model-2026-06-10.md`. It defines future minimal scope classes, proposed scoped write/config/operation permissions, forbidden broad scope patterns, safe token lifecycle boundaries and RED test requirements. It keeps `live_write_authorized: no`; prior VPS evidence does not grant write scopes, config scopes or live-runner permission. No runtime route expansion, token issue/revoke route, token storage change, fake-runner code, AMN2 code, live VPS command, SSH command, public exposure, config delivery, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `WAPI-I002` was selected and completed next.

Phase 4 `WAPI-I002` config delivery decoupling was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-i002-config-delivery-decoupling-2026-06-10.md`. It defines that future client/peer creation may return only safe operation/client metadata and must not return `.conf`, QR, `vpn://`, archives, share/download links or other secret-bearing config artifacts. Config delivery remains behind separate `P4-NG-CONFIG-DELIVERY-GATE`; live write remains behind `P4-NG-WRITE-API-LIVE-GATE`. No runtime route expansion, config delivery route, token issue/revoke route, fake-runner code, AMN2 code, live VPS command, SSH command, public exposure, config generation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `WAPI-I001` was selected and completed next.

Phase 4 `WAPI-I001` `/api/clients` design without live CRUD was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-i001-clients-design-without-live-crud-2026-06-10.md`. It defines candidate client list/detail/create/update/disable/revoke route contracts, safe client metadata fields, forbidden secret-bearing fields, idempotency/lock requirements, scope rules, audit/status binding and RED test requirements. It keeps `live_write_authorized: no`, runtime `/api/clients` routes absent, config delivery separate, and live peer mutation gated. No AMN2 code, runtime route expansion, `/api/clients` CRUD, fake-runner code, operation queue, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `WAPI-I005` was selected and completed next.

Phase 4 `WAPI-I005` web-panel gated action labels was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-wapi-i005-web-panel-gated-action-labels-2026-06-10.md`. It defines future label vocabulary for read-only metadata, local planning, dry-run, deferred named gates, blocked config delivery, blocked live write, blocked public exposure and destructive actions, plus required RED tests before any AMN2 panel implementation. It keeps `live_write_authorized: no`; labels are not authorization and do not unlock behavior. No AMN2 code, template change, route behavior change, runtime route expansion, `/api/clients` CRUD, fake-runner code, operation queue, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-N003` was selected and completed next.

Phase 4 `NG-N003` operation queue design after write API contract was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-n003-operation-queue-design-2026-06-10.md`. It defines future queue/cancel/retry/status semantics, safe queue entity fields, forbidden secret-bearing fields, lifecycle boundaries, idempotency/lock rules, retry/cancel constraints, visibility limits, panel label mapping and RED test requirements. It keeps `live_write_authorized: no`. No AMN2 code, runtime route expansion, queue implementation, worker implementation, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-N002` was selected and completed next.

Phase 4 `NG-N002` health/status polling design was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-n002-health-status-polling-design-2026-06-10.md`. It defines future polling tiers, safe aggregate status fields, forbidden secret-bearing and peer/user leakage fields, status vocabulary, staleness behavior, polling modes, route boundary, operation queue binding and RED test requirements. It keeps `live_write_authorized: no`. No AMN2 code, runtime route expansion, polling scheduler, collector, worker, real target polling, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-N001` was selected and completed next.

Phase 4 `NG-N001` attach-existing-server read-only reconciliation gate design was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-n001-attach-existing-server-read-only-reconciliation-gate-design-2026-06-10.md`. It defines safe read-only reconciliation phases, report fields, forbidden secret/peer/user leakage fields, status vocabulary, attach/backfill boundaries, conflict handling, health/status binding, operation queue binding and RED test requirements. It keeps `live_write_authorized: no`. No AMN2 code, runtime route expansion, reconciliation implementation, attach/import/backfill implementation, real target detection, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-N004` was selected and completed next.

Phase 4 `NG-N004` candidate registry update after every gate decision was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-n004-candidate-registry-update-2026-06-10.md`. It synchronized the candidate registry with closed `NG-N003`, `NG-N002` and `NG-N001` boundaries, specifically linking `P4-N006` operation queue/background jobs to `NG-N003` while preserving implementation, write and VPS gates; `P4-I007` health/status polling remains bound to `NG-N002`; `P4-N005` attach-existing-server reconciliation remains bound to `NG-N001`. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-S001` was selected and completed next.

Phase 4 `NG-S001` keep AMN3 status/transfer current was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-s001-status-transfer-sync-2026-06-10.md`. It synchronized `docs/PROJECT_STATUS_CURRENT.ru.md` and `research/amn2/transfer-backlog.md` after the closed normal P4-NG queue (`NG-N003`, `NG-N002`, `NG-N001`, `NG-N004`) and kept the active recommendation aligned to the remaining simple handoff work. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-ups `NG-S002` and `NG-S004` were selected and completed next.

Phase 4 `NG-S002` keep next-chat handoff current and `NG-S004` maintain visible active plan were completed together as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-s002-next-chat-handoff-sync-2026-06-10.md` and `research/amn2/phase-4-ng-s004-visible-active-plan-maintenance-2026-06-10.md`. They synchronized `docs/NEXT_CHAT_AMN2_PHASE_4_UNIFIED_PRODUCT_GATE.ru.md`, removed closed simple tasks from the visible active plan, and left only `NG-V001` plus cosmetic docs tasks active at that point. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-X003` was selected and completed next.

Phase 4 `NG-X003` stale wording cleanup was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-x003-stale-wording-cleanup-2026-06-10.md`. It removed stale active-next wording after the simple-task closure, marked `NG-X003` as closed in the P4-NG visible plan, and updated the next recommendation to `NG-X001` gate naming consistency. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-X001` was selected and completed next.

Phase 4 `NG-X001` gate naming consistency was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-x001-gate-naming-consistency-2026-06-10.md`. It aligned stage-level P4-NG gate labels to `P4-NG-*`, including write-live, config-delivery, public-exposure, local-implementation, polling and attach/backfill gates. It did not rename `NG-*`, `WAPI-*`, `P4-*` task ids, route names, branch names, file paths or historical candidate ids. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Follow-up `NG-X002` was selected and completed next.

Phase 4 `NG-X002` Russian-first operator wording polish was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-x002-russian-first-operator-wording-polish-2026-06-10.md`. It made active P4-NG operator-facing headings and next-step wording Russian-first while preserving technical ids, route names, gate names, file paths, branch names and candidate ids. No AMN2 code, runtime route expansion, candidate implementation, reconciliation implementation, attach/import/backfill implementation, operation queue implementation, polling scheduler, collector, worker, `/api/clients` CRUD, token issue/revoke route, config delivery route, live VPS command, SSH command, public exposure, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. Активной docs-only cosmetic рекомендации больше нет; `NG-V001` later gained the `NG-SC001` Codex Security preflight and was closed as `go`.

Phase 4 `NG-SC001` Codex Security VPS risk checkpoint was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/phase-4-ng-sc001-codex-security-vps-risk-checkpoint-2026-06-10.md`. It adds a required `Codex Security` threat-model checkpoint before `NG-V001` and any future destructive VPS rebuild gate, including `security_risk_decision: go | no-go | defer`, protected assets, trust boundaries, read-only baseline risks, fresh-rebuild risks and severity calibration. No AMN2 code, runtime route expansion, live VPS command, SSH command, reinstall/rebuild, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production peer/user mutation was performed. `NG-V001` was later closed as `go`; destructive rebuild is now tracked by separate `VPS-REBUILD-001` and remains blocked until final destructive approval.

Phase 4 `NG-V001` read-only VPS baseline gate was completed as `go` on 2026-06-10. Evidence: `research/amn2/phase-4-ng-v001-read-only-vps-baseline-gate-2026-06-10.md`. Safe summary confirms SSH transport ok, `amneziya-web` and `amneziya-bot` active/enabled, loopback `/login` returned HTTP 200, listener `3030` is loopback-only, public API `3040` absent, TCP `80/443` absent, `VPS_APPLY_ENABLED=false`, and no secret-bearing evidence was published. No package apply, service restart/enable/disable, firewall/reverse proxy edit, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or fresh VPS rebuild was performed. `NG-V001` is removed from the active plan; fresh VPS rebuild is now tracked by separate `VPS-REBUILD-001` as `defer` with no destructive action authorized.

Phase 4 `VPS-REBUILD-001` fresh VPS rebuild gate was opened as AMN3 docs-only preflight on 2026-06-10. Evidence: `research/amn2/vps-rebuild-001-fresh-vps-rebuild-gate-2026-06-10.md`; plan: `docs/superpowers/plans/2026-06-10-vps-rebuild-001-fresh-vps-rebuild.md`. Status: `opened-defer-awaiting-final-destructive-approval`; `security_risk_decision: defer`; `go_no_go_decision: defer`. Novice-safe preflight selected `data_retention_decision=preserve_snapshot_required`, `snapshot_or_backup_decision=provider_snapshot_required`, and `secret_transfer_policy=regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets`; source candidate is `1508e3c4a100b76815b29f91757290f1266f813d`; package is `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`; final destructive phrase is `not_sent`. No live VPS command, SSH command, wipe, reinstall, package apply, service stop/restart/enable/disable, firewall/reverse proxy edit, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation or secret publication was performed. Before any destructive action, the gate requires a retention-path decision, stop-criteria review and the exact final phrase `GO VPS-REBUILD-001 WIPE TARGET`.

Phase 4 `VPS-REBUILD-001` source/package precheck was completed locally on 2026-06-10. Evidence: `research/amn2/vps-rebuild-001-source-package-precheck-2026-06-10.md`. AMN2 source candidate is `1508e3c4a100b76815b29f91757290f1266f813d` on `codex-vps-test-prep`, clean and tracking `amn2/codex-vps-test-prep`. Focused local verification passed with `30 passed, 1 warning`; AMN2 remained clean. At source-precheck time, package build was still pending; later `research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md` superseded that package-pending state. Neighboring Phase 4 branches were classified as candidate inputs only; do not auto-merge them into the first rebuild package. No live VPS command, SSH command, package apply, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 `VPS-REBUILD-001` package build/hygiene was completed locally on 2026-06-10. Evidence: `research/amn2/vps-rebuild-001-package-build-hygiene-2026-06-10.md`. Built `dist/amn2-vps-update-and-smoke-kit-1508e3c.zip`, sha256 `03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3`, with source zip `dist/amn2-codex-vps-test-prep-1508e3c-source.zip`, sha256 `0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E`. Package hygiene passed: `package_entries=5`, `source_entries=302`, `forbidden_source_entries=0`, required entries passed, BOM/shell CRLF checks passed and test extraction passed. Status is only `package-ready-not-vps-smoked`; no live VPS command, SSH command, package apply, wipe/reinstall, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed. Remaining `VPS-REBUILD-001` blockers: retention-path decision and stop-criteria review before any final destructive phrase.

Phase 4 `VPS-REBUILD-001` provider snapshot confirmation was opened as docs-only operator-confirmation step on 2026-06-10. Evidence: `research/amn2/vps-rebuild-001-provider-snapshot-confirmation-2026-06-10.md`. Current status: `provider_snapshot_confirmation=defer`; `provider_backup_plan_enabled=yes`; `backup_frequency=monthly`; `backup_created_now=unknown`; `backup_restorable=yes_after_backup_created`; `delete_actions_planned=no`; `provider_portal_action_by_codex=no`; `live_commands_run=no`; `ssh_commands_run=no`; `go_no_go_decision=defer`. The operator enabled a monthly backup plan, but a created/restorable backup was not confirmed yet, and no deletion is planned. No live VPS command, SSH command, provider action by Codex, package apply, wipe/reinstall, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 `VPS-FRESH-DEPLOY-001` clean server readiness checklist was completed as AMN3 docs-only on 2026-06-10. Evidence: `research/amn2/vps-fresh-deploy-001-readiness-checklist-2026-06-10.md`; plan: `docs/superpowers/plans/2026-06-10-vps-fresh-deploy-001-readiness.md`. Result: `fresh_deploy_possible_from_repo_package=yes-with-operator-provided-secrets`; `bare_os_deploy_smoked=no`; `current_vps_disposable_decision=not-set`; `data_loss_acceptance_required_before_wipe=yes`; `delete_actions_planned=no`; `destructive_action_authorized=no`. This clarifies that source/package readiness can continue without waiting for provider backup, while target secrets, local DB/runtime state, peer config material and provider backup history are not rebuildable from repo/package alone. No live VPS command, SSH command, provider action by Codex, wipe/reinstall, package apply, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed. `VPS-REBUILD-001` still requires a retention-path decision, stop-criteria review and exact final destructive phrase before any destructive action.

Phase 4 `VPS-FRESH-DEPLOY-002` clean Ubuntu runbook was completed as AMN3 docs-only on 2026-06-11. Runbook: `docs/AMN2_FRESH_DEPLOY_FROM_ZERO_RUNBOOK.ru.md`; evidence: `research/amn2/vps-fresh-deploy-002-clean-ubuntu-runbook-2026-06-11.md`; plan: `docs/superpowers/plans/2026-06-11-vps-fresh-deploy-002-clean-ubuntu-runbook.md`. The runbook updates the old target-server prep flow for the current `1508e3c` package/source, no-domain service-mode, loopback web/admin `127.0.0.1:3030`, SSH tunnel access and `VPS_APPLY_ENABLED=false`. It explicitly separates rebuildable AMN2 app/service-mode state from operator-required secrets, local DB/runtime state, Amnezia keys/peers/configs and provider backup history. No live VPS command, SSH command, provider action by Codex, wipe/reinstall, package apply, service change, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production mutation or secret publication was performed.

Phase 4 PRVTPRO upstream refresh was recorded as AMN3 docs-only candidate intake on 2026-06-10. Evidence: `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-10.md`; candidate registry: `research/amn2/phase-4-candidate-registry-2026-06-09.md`. PRVTPRO/Amnezia-Web-Panel remains GPL-3.0 research-only: no code, templates, UI, manager implementations or workflows are copied. `P4-PRVTPRO-REFRESH-002` expiration-field contract tests were completed as AMN2 local-only in branch `codex/phase-4-prvtpro-expiration-contracts`, commit `b2eceeb111a0a27e41daf7b9ae7c79b5a0195e51`; evidence: `research/amn2/phase-4-prvtpro-expiration-contract-tests-implementation-2026-06-10.md`. `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status was completed as AMN2 local-only in branch `codex/phase-4-prvtpro-build-status`, commit `dc7966628e490da018f55fafe0fc559b44cc1dfa`; evidence: `research/amn2/phase-4-prvtpro-build-status-implementation-2026-06-10.md`. Both local-only branches were merged into AMN2 `codex-vps-test-prep` and pushed, new base head `1508e3c4a100b76815b29f91757290f1266f813d`; merge evidence: `research/amn2/phase-4-prvtpro-local-slices-merge-2026-06-10.md`. `P4-PRVTPRO-REFRESH-004` API taxonomy/OpenAPI grouping was completed as AMN3 docs-only policy support; evidence: `research/amn2/phase-4-prvtpro-api-taxonomy-openapi-grouping-2026-06-10.md`. `P4-PRVTPRO-REFRESH-003` read-only server status/latency UX is also closed: carried from Phase 4, design boundary closed in AMN3, local cached display implemented by `P5-L001`; live probes/actions remain gated. Hybrid-only items are AdGuard Home integration, SOCKS5 service manager, Xray migration/attach existing install and multi-protocol capability registry. Negative controls remain: no admin-equivalent Bearer token model, public panel, config delivery, reboot, backup, import or server cleanup without a separate named gate. Активных P4-NG задач больше нет after `NG-V001`; fresh VPS rebuild is tracked by separate `VPS-REBUILD-001` and remains blocked until final destructive approval.

Latest target VPS current mode: Phase 3 service-mode web/bot is enabled and active, but only as loopback/tunnel operation. Web/admin listens on `127.0.0.1:3030`, operator access is SSH tunnel only, no domain is planned, Caddy/HTTPS public cutover is deferred indefinitely, direct/public `3030` is closed by loopback bind, public API `3040` is absent/closed, TCP `80/443` are absent, and target `.env` explicitly keeps `VPS_APPLY_ENABLED=false`. Current peer scope is `live_peer_count=2`: `Neobyatnaya-AMNZ-1` and `Neobyatnaya-AMNZ-2` remain approved test peers; `Neobyatnaya-AMNZ-3` and `Neobyatnaya-AMNZ-4` are revoked. Web-panel unauth smoke and authenticated read-only overview smoke passed; no POST/write/config delivery/token issue/revoke/sync was performed. This does not unlock API route expansion, API `config:read`, `/api/clients` write CRUD, public config delivery, Local Agent mutations, backup/import/reboot, public API `3040`, public web/admin `3030`, Caddy/HTTPS or production peer writes.

Service-mode web-panel read-only UX review passed on 2026-06-09 as `passed-minimal-safe-summary`. Evidence: `research/amn2/service-mode-web-panel-read-only-ux-review-evidence-2026-06-09.md`. Operator confirmed service baseline, reviewed authenticated overview pages through SSH tunnel, and reported no write/config delivery/API token issue-revoke/sync-health/backup-import-reboot actions and no secrets published. Detailed page-by-page UX findings were not returned.

Target VPS Phase 3A.1 phone live test peer gate passed on 2026-06-09. One operator-approved test peer for phone/desktop client testing is intentionally left enabled. The first live apply attempt failed before remote mutation because the local test VPN IP input was invalid; verification showed no partial peer in persistent config or live interface and peer count remained `0`. After selecting a free VPN IP without publishing it, repeat dry-run apply/revoke passed, live apply passed, client config was regenerated from live AWG2 parameters with absent `I1`-`I5` fields removed, and client handshake/RX/TX passed. Final safe snapshot: `live_peer_count=1`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, service-mode not enabled. Evidence: `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`.

Target VPS Phase 3A.2 test peers batch gate passed on 2026-06-09. Three additional operator-approved test-zone peers were created and left enabled; secret-bearing configs/QRs were generated and downloaded through a private operator channel and were not published to chat or GitHub. Final safe snapshot: `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, service-mode not enabled. Evidence: `research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md`.

Target VPS Phase 3B.0 service-mode read-only precheck passed on 2026-06-09. Source overlay remains `f7f6131`, Docker runtime is running, `live_peer_count=4`, TCP `3030/3040` are absent, `VPS_APPLY_ENABLED=false`, web/bot service templates are present, web template binds `127.0.0.1:3030`, required bot/web secrets are present as markers only, and no `amneziya-web`/`amneziya-bot` systemd unit is installed, enabled or active. A named peer activity sample for `Neobyatnaya-AMNZ-1..4` returned `not-yet` at that moment. Evidence: `research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md`.

Target VPS Phase 3A critical manual-mode cleanup passed on 2026-06-09. Before cleanup, the target remained at `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, and the four named test peers sampled as `not-yet`. Secret-bearing delivery artifacts from the phone/test peer gate directories and root delivery archive location were removed: client `.conf`, QR/PNG and delivery archive files now count `0`. Monitoring key files were intentionally retained so the four test peers can still be checked by friendly number. Post-cleanup control confirmed `live_peer_count=4`, TCP `3030/3040` absent and `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md`.

Target VPS Phase 3A protocol identity check passed on 2026-06-09 after the operator reported that imported client configs did not visibly advertise "Amnezia 2.0". The downloaded config metadata for `Neobyatnaya-AMNZ` and `Neobyatnaya-AMNZ-2..4` shows all 11 core AmneziaWG fields present and `I1`-`I5` absent; live server config metadata matches the same shape. Numbered peer monitoring showed `Neobyatnaya-AMNZ-2=connected-with-traffic`, while `1`, `3` and `4` were `not-yet` at that sample. This supports UI/label ambiguity rather than a wrong plain-WireGuard or Amnezia 1/1.5 export. No regenerate/re-delivery gate is required on this evidence alone. Evidence: `research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md`.

Target VPS Phase 3A manual-runtime field test reached `partial-pass` on 2026-06-09. A read-only numbered live snapshot during real usage showed `live_peer_count=4`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, and `connected_with_traffic_count=3`: `Neobyatnaya-AMNZ-1`, `-2` and `-3` were `connected-with-traffic`, while `-4` remained `not-yet`. This proves live manual-runtime connectivity for three of four approved test peers. Evidence: `research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md`.

Target VPS Phase 3A revoke-by-number runbook is prepared but not executed. It documents a safe dry-run and explicit-confirmation live revoke flow for exactly one `Neobyatnaya-AMNZ-N` test peer, with numbered key resolution, pre/post peer count checks, `3030/3040` checks, and `VPS_APPLY_ENABLED=false` reset. It does not authorize any revoke by default. Runbook: `docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md`.

Target VPS Phase 3A revoke-by-number gate for `Neobyatnaya-AMNZ-3` passed on 2026-06-09. Dry-run confirmed the target was present in persistent config and live interface, had `connected-with-traffic`, and advertised the expected remote-state-write/container-restart markers. Live revoke removed only `Neobyatnaya-AMNZ-3` from persistent and live state: `live_peer_count` changed from `4` to `3`, `target_in_persistent_after=no`, `target_in_live_after=no`, TCP `3030/3040` remained absent, and `VPS_APPLY_ENABLED` was reset to `false`. Evidence: `research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md`.

Post-revoke numbered snapshot kept the same safe state: `live_peer_count=3`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, `Neobyatnaya-AMNZ-3=not-found-on-server`, and remaining peers `1`, `2`, `4` were initially `not-yet` pending fresh reconnect after Docker restart. A later reconnect snapshot after user activity showed `Neobyatnaya-AMNZ-1=traffic-seen`, `Neobyatnaya-AMNZ-2=traffic-seen`, `Neobyatnaya-AMNZ-3=not-found-on-server`, and `Neobyatnaya-AMNZ-4=not-yet`. This proves manual reconnect/traffic for two remaining peers after the #3 revoke; automatic reconnect remains unproven unless a separate disruption test is approved.

Target VPS Phase 3 revoke-by-number gate for unused `Neobyatnaya-AMNZ-4` passed on 2026-06-09. Dry-run confirmed #4 was present in persistent and live state with `target_status_before=not-yet`, and advertised the expected remote-state-write/container-restart markers. Live revoke removed #4 from both persistent config and live interface: `live_peer_count` changed from `3` to `2`, `target_in_persistent_after=no`, `target_in_live_after=no`, web/bot remained active, loopback `/login` returned `200`, TCP `3030` remained loopback-only, TCP `80`, `443` and `3040` remained absent, and `VPS_APPLY_ENABLED` was reset to false with explicit `.env` false. Evidence: `research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md`.

Post-revoke #4 numbered snapshot confirmed `live_peer_count=2`, web/bot active, loopback `/login=200`, TCP `3030` loopback-only, TCP `80/443/3040` absent and explicit `.env` `VPS_APPLY_ENABLED=false`. `Neobyatnaya-AMNZ-3` and `Neobyatnaya-AMNZ-4` were `not-found-on-server`; `Neobyatnaya-AMNZ-1` and `-2` were `not-yet` in this immediate sample pending client reconnect after the Docker/AWG restart, with earlier Phase 3 evidence already showing traffic for both.

Target VPS Phase 3B0 service-mode preflight completed read-only on 2026-06-09 as `needs-fix-before-B1`. Good: source overlay `f7f6131`, Docker runtime running, `live_peer_count=3`, TCP `3030/3040` absent, `VPS_APPLY_ENABLED=false`, web/bot templates present, web template binds `127.0.0.1:3030`, no systemd units installed/enabled/active, imports pass. Blockers before `systemctl enable --now`: the `amneziya` service user/group is absent while templates use `User=amneziya`; effective settings show `WEB_ADMIN_ENABLED=False`; `ADMIN_TELEGRAM_IDS` is absent; reverse proxy choice is undecided for any later HTTPS cutover. Evidence: `research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md`.

Target VPS Phase 3B0.1 prep and B0 repeat completed on 2026-06-09. B0.1 created the `amneziya` service user, set `.env` group/mode for that service group, enabled web/admin in effective settings on loopback, preserved `VPS_APPLY_ENABLED=false`, set admin Telegram IDs privately on the VPS, and fixed `/opt/amn2` group access so the service user can read app/venv/env and write data/logs. No systemd unit was installed or started, and reverse proxy was unchanged. Repeated B0 is now `ready-for-B1-loopback-systemd`: `live_peer_count=3`, TCP `3030/3040` absent, templates good, no units installed/active, settings as `amneziya` pass, imports pass. Evidence: `research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md`.

Target VPS Phase 3B1 loopback-only systemd gate passed on 2026-06-09 after a short readiness investigation. Initial B1 installed/enabled `amneziya-web` and `amneziya-bot` and both units were active, but the immediate web probe returned `curl_rc_7` with `tcp_3030_after=absent`, so B1 was treated as `needs-investigation`. Follow-up bounded diagnostics showed both units enabled/active with `Result=success`, `NRestarts=0`, web listening on `127.0.0.1:3030`, `/login` returning `200`, TCP `3040` absent, reverse proxy unchanged, and `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md`.

Target VPS Phase 3B2.0 reverse proxy preflight completed read-only on 2026-06-09. Web/bot systemd remained enabled/active, loopback `/login` returned `200`, TCP `3030` was loopback-only, TCP `3040` absent, TCP `80/443` absent, nginx/Caddy/certbot were not installed, no Docker proxy candidate was running, UFW was inactive, no writes were performed and reverse proxy remained unchanged. Evidence: `research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md`.

Target VPS Phase 3B2.1 reverse proxy readiness completed read-only on 2026-06-09 as `blocked-before-public-cutover`. Web/bot remained enabled/active, loopback `/login` returned `200`, TCP `3030` remained loopback-only, TCP `3040`, `80` and `443` remained absent, and Caddy/nginx/certbot package candidates were available. The selected public host syntax was valid, but DNS returned no A/AAAA records from the VPS and therefore could not be proven to point at the target route source. The read-only check also did not prove an explicit `.env` `VPS_APPLY_ENABLED=false` line, so a small baseline-fix gate is required before Caddy/HTTPS. Evidence: `research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md`.

Target VPS no-domain service-mode access path selected on 2026-06-09. The operator confirmed that current access is IP-only and no domain is available, so public HTTPS reverse proxy cutover is deferred. The selected safe access path is SSH local port forwarding from the operator workstation to loopback web/admin `127.0.0.1:3030`, opened in an external browser rather than Codex preview. Evidence: `research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md`; runbook: `docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md`.

Target VPS no-domain SSH tunnel access passed on 2026-06-09. The operator opened the web/admin panel through an SSH local port forward in an external browser. Control snapshot confirmed `amneziya-web=active`, `amneziya-bot=active`, loopback `/login=200`, remote `3030` loopback-only, remote `3040` absent, and explicit `.env` `VPS_APPLY_ENABLED=false`. Evidence: `research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md`.

Target VPS web-panel tunnel smoke passed read-only on 2026-06-09. Through the SSH local port forward, `/login` returned HTTP `200` with a login form and password field, `/` redirected to `/login`, sampled protected GET routes redirected to `/login` with HTTP `303`, the login response contained no obvious secret/error markers, and local `127.0.0.1:3040` did not accept a connection. No credentials were submitted, no POST route was called, no config delivery was requested, and no write operation was performed. Evidence: `research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md`.

Target VPS second Telegram admin ID add passed on 2026-06-09. One additional Telegram admin ID was added privately on the VPS, leaving configured admin count at `2` without publishing raw IDs. `VPS_APPLY_ENABLED=false` remained explicit in `.env`. After restarting `amneziya-bot` and `amneziya-web`, loopback `/login` had a short readiness window and then returned `200`; final state was bot/web active, TCP `3030` loopback-only and TCP `3040` absent. Evidence: `research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md`.

Target VPS second admin bot read-only check was skipped by operator decision on 2026-06-09 to save time. The second admin ID remains configured and counted, but this record does not independently prove that the second admin opened `/start`, saw admin mode, or opened read-only bot admin sections. Evidence: `research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md`.

Target VPS authenticated web-panel tunnel smoke passed read-only on 2026-06-09. The operator logged into the web/admin panel through the SSH local port forward in an external browser and sampled overview GET pages only. `/`, `/users`, `/servers`, `/orders`, `/logs`, `/settings`, `/config-templates`, `/api-readiness`, `/integration-status`, `/api-tokens` and `/devices/disabled` all returned HTTP `200` without redirect. No POST route was called, no settings were saved, no token was issued/revoked, no sync/health operation was run, and no config delivery was requested. Evidence: `research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md`.

Target VPS Phase 3 final safety snapshot passed on 2026-06-09 with source-overlay git metadata unavailable in that specific check. Runtime remained Docker with `live_peer_count=3`; `Neobyatnaya-AMNZ-1` and `-2` were `traffic-seen`, `-3` was `not-found-on-server`, and `-4` was `not-yet`. Web/bot systemd units were enabled/active, loopback `/login` returned `200`, TCP `3030` was loopback-only, TCP `80`, `443` and `3040` were absent, explicit `.env` `VPS_APPLY_ENABLED=false` was present, production write surfaces/config delivery remained closed, and reverse proxy/public HTTPS remained disabled. Evidence: `research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md`.

This still does not execute HTTPS reverse proxy/public cutover, public API `3040`, direct public web/admin `3030`, production peer/user mutation beyond the two remaining approved test peers, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent write/config mutations, backup/import/reboot routes, or secret-bearing evidence publication. B2 reverse proxy/public HTTPS remains a separate explicit gate.

# Historical Override 2026-06-07

`amn2/codex-vps-test-prep` VPS-smoked source overlay is now `f7f6131 Update integration status for c92 manual prelaunch`. The app-code read-only slice `62ff184 Update controlled prod status visibility` first passed real VPS git-checkout smoke on `/opt/amn2-git`, then AMN3 package `42ffa65` was applied to `/opt/amn2` through the safe source-overlay update flow and passed read-only loopback API smoke on 2026-06-07. The safety follow-up package `c92bd1a` passed source-overlay update/read-only loopback smoke on `/opt/amn2`, and the status-alignment package `f7f6131` has now also passed read-only loopback smoke.

The current VPS production source overlay is now `f7f6131 Update integration status for c92 manual prelaunch`. Previous source overlay `c92bd1a Bind web admin systemd to loopback` remains the web-admin loopback/manual-runtime baseline from 2026-06-07. `42ffa65 Record git checkout smoke status` remains historical status-visibility smoke baseline from 2026-06-07. `c8a6363 Add Local Agent runtime summary mapper` remains historical smoke-passed baseline from 2026-06-06. Current evidence: `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`; prior c92 source-overlay evidence: `research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md`; prior 42 source-overlay evidence: `research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md`; prior git-checkout evidence: `research/amn2/controlled-prod-status-visibility-git-checkout-smoke-2026-06-07.md`.

Latest AMN2 repository head and current proven `/opt/amn2` source overlay are both `f7f6131`. This remains read-only status visibility only; it does not unlock write/API/config/backup/agent/service-mode gates. Evidence: `research/amn2/manual-prelaunch-integration-status-2026-06-07.md` and `research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md`.

AMN3 update+smoke kit for `f7f6131` is now `read-only-vps-smoke-pass`. It aligned `/api/integration/status` and the web integration status page with the accepted manual-runtime state and kept `VPS_APPLY_ENABLED=false`.

Repeat confirmation: the same `42ffa65` source overlay passed another read-only loopback API smoke with `run_id=20260607T165807Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/controlled-prod-status-visibility-vps-repeat-smoke-2026-06-07.md`.

Post-smoke safety follow-up is now complete for the read-only gate. Purpose: keep web/admin backend on `127.0.0.1:3030` for approved HTTPS reverse proxy mode before controlled production launch. This does not open public API `3040`, direct public web/admin `3030`, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent mutations, backup/import/reboot, or new live peer operations.

Validation VPS manual runtime gate also passed after the `c92bd1a` smoke: backup create/verify passed, safe preflight passed, API smoke-cycle summary passed with six read-only routes, manual web and bot processes are present, `/login` returned `200`, web/admin is loopback-only on `127.0.0.1:3030`, direct public web `3030` is not exposed, public API `3040` is not exposed, `systemd` is not used, and `VPS_APPLY_ENABLED=false`.

```text
dist/amn2-vps-update-and-smoke-kit-c92bd1a.zip
package sha256: EC48DBA7C91F189512AB77EB5490432C85DA79F987068A98C1CC7F3082387F12
source zip: dist/amn2-codex-vps-test-prep-c92bd1a-source.zip
source sha256: 272CC013A416937AAA2256A1643B2C77F707874D28FDCB2EA16534E349DD4FC2
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T182118Z
api_smoke_run_id: 20260607T182131Z
checked_routes: 6
routes: servers, integration_status, local_agent_runtime_summary, server_summary, metrics_summary, users_summary
route_status_codes: all 200
forbidden_markers: none
listener: 127.0.0.1:3040 loopback-only
auth: missing bearer 401, wrong scope 403, revoked token 401
audit: safe
web systemd template: ExecStart uses web serve --host 127.0.0.1 --port 3030
operator doc: dist/amn2-vps-update-and-smoke-kit-c92bd1a/AMN2_VPS_UPDATE_AND_SMOKE_c92bd1a.ru.md
package evidence: research/amn2/web-admin-loopback-systemd-vps-package-2026-06-07.md
VPS smoke evidence: research/amn2/web-admin-loopback-systemd-vps-smoke-evidence-2026-06-07.md
manual prelaunch evidence: research/amn2/c92bd1a-manual-prelaunch-evidence-2026-06-07.md
latest AMN2 repository head: f7f6131 Update integration status for c92 manual prelaunch
latest AMN2 head status: read-only status visibility, VPS source-overlay-smoked
latest AMN2 head evidence: research/amn2/manual-prelaunch-integration-status-2026-06-07.md
status-alignment package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
status-alignment package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
status-alignment source zip: dist/amn2-codex-vps-test-prep-f7f6131-source.zip
status-alignment source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status-alignment package status: read-only-vps-smoke-pass
status-alignment VPS smoke: passed
status-alignment source update run_id: 20260607T203721Z
status-alignment api smoke run_id: 20260607T203730Z
status-alignment latest repeat api smoke run_id: 20260607T204300Z
status-alignment smoke evidence: research/amn2/f7f6131-status-alignment-vps-smoke-evidence-2026-06-07.md
status-alignment operator doc: dist/amn2-vps-update-and-smoke-kit-f7f6131/AMN2_VPS_UPDATE_AND_SMOKE_f7f6131.ru.md
status-alignment evidence: research/amn2/f7f6131-status-alignment-vps-package-2026-06-07.md
manual runtime status: passed
manual runtime mode: manual
systemd web/bot: not-used
web process: present
bot process: present
web login: 200
web direct public 3030: no
api public 3040: no
backup verified: backups/amneziya-backup-20260607T195851Z.tar.enc
api smoke cycle: passed, checked_routes=6, forbidden_markers_count=0
VPS_APPLY_ENABLED: false
```

AMN3 source-overlay gate result:

```text
dist/amn2-vps-update-and-smoke-kit-42ffa65.zip
package sha256: 5B43B467E014E87FEC1E49E8D9A8B7A2FBF841541BE88FDC6768097806240E39
source zip: dist/amn2-codex-vps-test-prep-42ffa65-source.zip
source sha256: 8A5B83D9AB95BE4230AAC221CE0321A37EF37E4E4B6EAB5EDECAE3C98A944829
status: read-only-vps-smoke-pass
source_update_run_id: 20260607T165559Z
api_smoke_run_id: 20260607T165625Z
latest_repeat_api_smoke_run_id: 20260607T165807Z
checked_routes: 6
listener: 127.0.0.1:3040 loopback-only
auth: missing bearer 401, wrong scope 403, revoked token 401
audit: safe
operator doc: dist/amn2-vps-update-and-smoke-kit-42ffa65/AMN2_VPS_UPDATE_AND_SMOKE_42ffa65.ru.md
package evidence: research/amn2/controlled-prod-status-visibility-vps-package-2026-06-07.md
VPS smoke evidence: research/amn2/controlled-prod-status-visibility-vps-smoke-evidence-2026-06-07.md
```

New target VPS bootstrap 2026-06-08 first passed as `partial-pass`: base OS packages, Docker runtime with no containers, `/opt/amn2` venv, `f7f6131` source overlay, Python dependencies, DB schema init, partial loopback API `/api/servers` probe with token revoke, and encrypted backup create/verify passed. Evidence: `research/amn2/target-server-bootstrap-evidence-2026-06-08.md`.

Target VPS AWG2 runtime gate 2026-06-09 is now `read-only-smoke-pass`: `amnezia-awg2` Docker runtime was built and started, real target `servers.yml` was created on the VPS through a secret-safe channel, AMN2 loader accepted it, and official read-only API loopback smoke passed with `run_id=20260609T043158Z`, `checked_routes=6`, auth `401/403/401`, listener passed and audit passed. Evidence: `research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md`.

Target VPS live peer gate 2026-06-09 is now `verified-live`: exactly one disposable test peer passed dry-run apply/revoke, live apply/sync/revoke/sync, ended with peer count `0`, and post-gate read-only API loopback smoke passed with `run_id=20260609T045546Z`, `checked_routes=6`. Evidence: `research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md`.

Target VPS manual web/bot gate 2026-06-09 is now `passed`: Telegram bot token is present on the VPS and `bot check-network` passed for `@NeobyatnayaAMNZ_bot`; web admin password hash and session secret are present; a temporary manual web/admin process returned `/login` HTTP `200` on `127.0.0.1:3030`, then was stopped. Final snapshot: AWG2 container running, peer count `0`, TCP `3030` absent, TCP `3040` absent. Evidence: `research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md`.

Next gate: keep the new target VPS as verified for the remote peer apply/revoke primitive and manual web/bot readiness, then choose the next layer deliberately: stay in manual runtime mode for product/API work, or run a separate service-mode gate if `systemd`/HTTPS reverse proxy deployment is desired. This still does not unlock public API `3040`, direct public web/admin `3030`, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent mutations, backup/import/reboot, or production peer operations.

# Historical Override 2026-06-06

Historical 2026-06-06 source-overlay head was `c8a6363 Add Local Agent runtime summary mapper`. AMN3 update+smoke package for that source overlay is `c8a6363` and passed real VPS read-only smoke on 2026-06-06, `run_id=20260606T202040Z`. `32d01fd` is now the historical prior VPS-smoked runtime/source, `run_id=20260606T185114Z`; `1a193b9` is the previous historical runtime/source before that.

Read-only integration status update 2026-06-06: `32d01fd` updates `/api/integration/status` to report `read_only_vps_smoked`, Phase 2 `verified_live`, and controlled-prod readiness pending without enabling write routes or write operations. AMN3 evidence is `research/amn2/integration-status-controlled-prod-update-2026-06-06.md`. The previous local-only operation-contract fast-forward remains recorded at `research/amn2/remote-partial-failure-contract-2026-06-06.md`.

Local Agent runtime summary 2026-06-06: local-only AMN2 feature branch `codex/local-agent-runtime-summary` was created from `32d01fd`, verified locally, fast-forward merged into `codex-vps-test-prep`, pushed at `c8a6363 Add Local Agent runtime summary mapper`, packaged, and read-only VPS-smoked. It adds only a pure controller-safe mapper and focused tests; no API route, web route, CLI command or live write operation. Evidence is `research/amn2/local-agent-runtime-summary-implementation-2026-06-06.md` and `research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md`.

```text
AMN3 package for historical 2026-06-06 source overlay: dist/amn2-vps-update-and-smoke-kit-c8a6363.zip
sha256: 027ECC1BAD7321FCCD61A4CCCA3AC9F06AAA9AC6A3D7115B4813253D19C2CFBF
source zip: dist/amn2-codex-vps-test-prep-c8a6363-source.zip
source sha256: E1E198979D988B3A5AA038CF732B8DCDBE854C48A6D381FADBA05BFDEE0251C6
package evidence: research/amn2/local-agent-runtime-summary-vps-package-2026-06-06.md
package status: read-only-vps-smoke-pass
local verification: focused 7 passed; adjacent smoke/security 26 passed; package SHA/source SHA/no-BOM/no-forbidden-source-entry/test-extract checks passed
package evidence: research/amn2/local-agent-runtime-summary-vps-package-2026-06-06.md
VPS result for c8a6363: read-only-vps-smoke-pass, run_id 20260606T202040Z
VPS smoke evidence: research/amn2/local-agent-runtime-summary-vps-smoke-evidence-2026-06-06.md
previous VPS-smoked runtime/source: 32d01fd, run_id 20260606T185114Z, evidence research/amn2/integration-status-controlled-prod-update-2026-06-06.md
previous VPS-smoked runtime/source: 1a193b9, run_id 20260606T154636Z, evidence research/amn2/remote-partial-failure-contract-vps-smoke-evidence-2026-06-06.md
controlled prod readiness: controlled-prod-ready
controlled prod access path: approved HTTPS reverse proxy; public API 3040 not exposed
controlled prod recovery path: known
controlled prod runbook: docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
controlled prod evidence: research/amn2/controlled-prod-readiness-2026-06-06.md
controlled prod reverse proxy confirmation: research/amn2/controlled-prod-reverse-proxy-confirmation-2026-06-07.md
controlled prod final decision: research/amn2/controlled-prod-ready-2026-06-07.md
controlled prod next chat: docs/NEXT_CHAT_AMN2_CONTROLLED_PROD_DECISION.ru.md
previous VPS-smoked source: 568c611, run_id 20260605T162742Z, evidence research/amn2/phase-2-post-psk-stdin-vps-smoke-evidence-2026-06-05.md
docs-only cleanup: 6b5b5b7 Document stdin PSK peer apply
local-only contract merge: 1a193b9 Add remote partial failure contract
read-only integration status update: 32d01fd Update integration status for controlled prod
stable Local Agent runtime summary merge: c8a6363 Add Local Agent runtime summary mapper
```

Phase 2 live single disposable test peer apply/revoke is verified-live on stable `7764ae7`; `568c611` adds safer `--preshared-key-stdin` handling and passed read-only VPS update/smoke.

```text
AMN3 evidence: research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md
result: verified-live
scope: exactly one disposable test peer apply/sync/revoke/sync
```

This does not unlock broad write API, public/self-service config delivery, API `config:read`, `/api/clients` CRUD, backup/import/reboot routes, Local Agent mutations or public web/API exposure. Older `c92bd1a`, `42ffa65`, `c8a6363`, `32d01fd`, `294803e`, `7764ae7`, `568c611` and `1a193b9` package blocks below are historical evidence; `f7f6131` is the current VPS-smoked runtime/source baseline.
# Текущее состояние проекта

Дата: 2026-06-02.

Этот snapshot фиксирует текущее состояние после verified live VPS cycle, серии local-only hardening slices в `amn2`, сборки VPS install package и перехода API-направления в активную ветку `codex/read-only-api-route-shell`.

## Что учтено при обновлении

Проанализированы локальные Codex-сессии проекта с `VPS-OPS-LAB` и `Amneziya`, включая:

- ранний Amneziya planning/provisioning чат;
- `Подготовка запуска на VPS`;
- `VPS-тест Amneziya`;
- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`;
- `VPN Ops Lab - KYORESUAS-API`;
- task/review-чаты Local Amnezia Agent first slice;
- task/review-чаты Local Agent production wiring;
- live VPS completion / verified tag / migration-to-lab чаты;
- Route/Auth/Operation Policy Matrix task/review;
- Redaction Coverage task/review;
- Config Delivery Integrity evidence;
- Public Token Safety task/review;
- Remote Operation contract / partial-failure / dry-run-audit slices;
- Local Agent hardening task/review;
- Web Panel Safe Improvements task/review;
- Scoped API Token Storage task/review;
- Route/Auth Binding Tests, API Token Lifecycle Gate and SSH Host Key Verifier task/review;
- VPS install package / installer fallback fix;
- KYORESUAS API priority plan и последующую ветку read-only API route shell;
- pre-VPS matrix comments from `codex/local-agent-production-wiring`;
- текущий `MAIN - VPN Ops Lab` coordination chat.

Нерелевантные сессии из других рабочих папок, например `ISP-NEW`, не включались в состояние этого проекта.

## AMN3 / VPS Ops Lab

Локальный checkout:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

GitHub remote:

```text
https://github.com/barakov-dot/amn3.git
```

Текущая ветка:

```text
master
```

AMN3 package state reviewed in this status refresh:

```text
master; verify exact current head with git log -1 after package publish
```

`master` должен быть синхронизирован с `origin/master` после каждого package publish.

Последние AMN3 pushes, учтенные в этом snapshot:

```text
25e02e9 Add VPS install package
87da41d Fix VPS installer user creation fallback
7fc3aee Set KYORESUAS API integration priority
8b4cc81 Refresh project coordination state
2b845cb Make API smoke skip server preflight by default
```

Актуальный install/update package для стабильного `amn2` baseline `294803e`:

```text
dist/amn2-vps-install-294803e.zip
sha256: 9B561FBF9C1ACDE403CFF6DA3A49544074457D3089FF8A8D0859B0CEBBBB1501
dist/amn2-vps-update-and-smoke-kit-294803e.zip
sha256: 702BAD7EBD69F80FC75FD31648383258B6C042BD51B801BC72BE2FD125813CE2
```

Package note: install/update packages include `amn2_api_loopback_smoke.sh` version `2026-06-04.2`; the package contains the merged API/web-panel slice (`API readiness` and `API tokens` web-admin pages), performs DB-only server config sync from `servers.yml` into SQLite before route smoke, and keeps `server preflight` as a separate SSH/server dry-run gate, not the API smoke path.

Дополнительный соседний AMN3 push, который не слит в `master`, но учтен в этом snapshot:

```text
origin/codex/local-agent-production-wiring -> d5f30c6 Clarify pre-VPS matrix baseline
artifact: docs/AMN3_PRE_VPS_LOCAL_STATUS_MATRIX.ru.md
status: branch-only pre-VPS matrix; использовать как комментарий/сверку, не как production gate
```

AMN3 является coordination/knowledge repo: research, design specs, implementation plans, transfer notes и gate для переноса идей в production.

Production-код остается в `amn2`.

## Production baseline: `amn2`

Локальный checkout:

```text
C:\Users\SooL\Documents\Amneziya
```

GitHub remote:

```text
https://github.com/barakov-dot/amn2.git
```

Стабильная production baseline ветка:

```text
codex-vps-test-prep
```

Актуальный head:

```text
294803e Add API readiness and token web pages
```

Стабильная baseline-ветка `amn2/codex-vps-test-prep` теперь содержит проверенный live VPS behavior contract, merged read-only API route shell и web-admin API readiness/token lifecycle pages.

Текущая активная рабочая ветка `Amneziya` для установки/API debug:

```text
codex/read-only-api-route-shell
head: 2010d60 Add API VPS smoke evidence template
remote: amn2/codex/read-only-api-route-shell
status: merged into `codex-vps-test-prep` at `5f12736`, local worktree clean
```

Эту ветку использовали в чате `Переводим AMN на API` для VPS install/update smoke и исправления ошибок. Актуальный real VPS loopback API-only smoke прошел 2026-06-03 с `run_id=20260603T112418Z`: DB-only server config sync выполнен, preflight `skipped`, API/auth/scope/revoke/listener/audit `passed`, `VPS_APPLY_ENABLED=false`, raw token/header/hash/config/keys/PSK не публиковались. Evidence: `research/amn2/api-vps-smoke-evidence-2026-06-03.md`. Предыдущий historical pass 2026-06-02 остается в `research/amn2/api-vps-smoke-evidence-2026-06-02.md`. После evidence ветка fast-forward merged в stable `codex-vps-test-prep` и запушена как production head `5f12736`. Главный coordination-chat не должен открывать параллельную API-реализацию; следующий API/web-panel slice `API readiness/status` + `API token lifecycle` UI выполнен в `amn2/codex/api-web-panel-finish`, затем fast-forward merged в stable `codex-vps-test-prep` и запушен как production head `294803e`.

После scoped API token storage в `codex-vps-test-prep` уже вошли Route/Auth Binding Tests, API Token Lifecycle Gate и SSH Host Key Verifier через PR #4, PR #5 и PR #6. Эти срезы остаются local-gate-complete: без новых live VPS calls, без включения remote writes и без расширения `/api/*` routes до отдельного gate.

Проверенная stable-точка live VPS cycle:

```text
vps-live-cycle-verified -> d6eda20 Document verified VPS live cycle
```

Основной handoff production-репозитория:

```text
docs/NEXT_CHAT_HANDOFF.ru.md
```

Последние зафиксированные local-only проверки по свежим gate-срезам `amn2`:

```text
Route/Auth Binding Tests: focused 22 passed; full 549 passed
API Token Lifecycle Gate stacked: focused 56 passed; full 555 passed
SSH Host Key Verifier: focused 29 passed; full 550 passed
Remote Operation VPS-gate candidate: focused 71 passed; full 603 passed; VPS Phase 2 verified-live on current stable `7764ae7`
Post dry-run read-only integration status: focused 31 passed; full 610 passed
Secret Inventory Registry: focused 64 passed; full 591 passed
Read-only API route shell: full 588 passed
```

Ожидаемое предупреждение: `StarletteDeprecationWarning` от `httpx` / `starlette.testclient`.

## Verified live VPS cycle

На живом VPS подтверждено:

- approve заявки в Telegram создает рабочий peer;
- клиентский config подключается;
- web panel показывает working config сразу после approve;
- `Run peer sync` подтверждает live-состояние;
- внешние peer, созданные в приложении Amnezia, не удаляются и отображаются отдельно;
- missing local device можно добавить в AmneziaWG;
- `Disable VPN` и `Enable VPN` работают;
- выборочное удаление устройства работает;
- Docker runtime apply/revoke прошел живую проверку;
- AmneziaWG 2.0 template/defaults приведены к рабочему формату.

Это закрывает прежний пункт `live VPS retest` как основной риск. Новый retest нужен только после изменений в apply/revoke/config/sync логике.

## Что продолжаем теперь

API-readiness audit выполнен в AMN3:

```text
research/amn2/api-readiness-audit-after-live-baseline.md
```

Основной порядок слияния API, web panel и operations зафиксирован:

```text
docs/AMN2_MAIN_MERGE_ROADMAP.ru.md
```

Первый выбранный safe slice уже перенесен в `amn2`:

```text
Route/Auth/Operation Policy Matrix for current amn2 surfaces
```

Смысл slice: не добавлять новый production API сразу, а сначала сделать machine-checkable policy/contract для текущих web, bot, Local Agent и remote-operation surfaces: actors, auth, risk class, secret class, audit, idempotency, dry-run/apply, rollback/recovery и live-retest trigger.

Этот slice остался без live VPS calls, без новых config/API/write endpoints и без копирования upstream code.

После него локально выполнены и запушены в `amn2` следующие local-only / candidate slices:

- Redaction Coverage: `94ad807 Document secret-bearing delivery artifacts`;
- Config Delivery Integrity evidence: verified at `94ad807`;
- Public Token Safety: `dfe27ee Harden public email token safety`;
- Remote Operation state-changing contract / partial-failure / dry-run-audit: VPS-gate candidate `codex/remote-operation-vps-gate-prep` updated on top of `294803e`, head `7281254`, runbook `research/amn2/vps-gate-remote-operation-dry-run-audit.md`, package `dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip`;
- Local Agent Hardening: `c5d7eb6 Harden Local Agent audit contract`;
- Web Panel Safe Improvements: `22dfc37 Clarify web panel operation gates`;
- Scoped API Token Storage: `1fdcde5 Add scoped API token storage contract`.
- Route/Auth Binding Tests: branch `amn2/codex/route-auth-binding-tests`, commit `f9d2c79 Bind route inventory to surface policies`.
- API Token Lifecycle Gate: branch `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0 Add API token lifecycle gate`.
- SSH Host Key Identity Verifier: branch `amn2/codex/ssh-host-key-identity-verifier`, commit `dd20364 Add SSH host key verifier`, merged to `codex-vps-test-prep` via PR #6; later read-only API route shell fast-forward moved current production head to `5f12736`.
- Manager Config Export Contract: branch `amn2/codex/manager-config-export-contract`, commit `4d4e7a4 Add manager config export contract`; local-only no-route typed export adapter, без public/self-service endpoint, API `config:read` и Local Agent `/configs`.
- Public/Self-service Config Delivery Policy: branch `amn2/codex/public-config-delivery-policy-contract`, commit `2ef3af7 Add config share policy contract`; local-only no-route share-token/policy contract, без public download route, self-service download route, API `config:read` и Local Agent `/configs`.
- Backup/Import Policy Contract: branch `amn2/codex/backup-import-policy-contract`, head `afb2702 Tighten backup import preview type contract` with foundation commit `d2c160b`; local-only no-route backup mode registry, secret field policy and restore/import preview contract, без web/API backup routes, restore apply, import apply или live VPS calls.
- Secret Inventory Registry: branch `amn2/codex/secret-inventory-registry`, commit `9ce42f4 Add secret inventory registry`; local-only machine-checkable secret inventory, без `.env` чтения, DB access, routes, secret-bearing output или live VPS calls.
- Packaging discovery fix: branch `amn2/codex/read-only-api-route-shell`, commit `e99d5f3 Fix editable install package discovery`; исправляет editable install/package discovery перед VPS install package smoke.
- Read-only API route shell: branch `amn2/codex/read-only-api-route-shell`, commits `6534ac4`, `9cccdc2`, `b37103a`, `2010d60`, `5f12736`; добавлены loopback-safe read-only `/api/*` routes, token smoke CLI, local API smoke readiness, `amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md`, AMN3 operator script `scripts/vps/amn2_api_loopback_smoke.sh` и update+smoke kit `dist/amn2-vps-update-and-smoke-kit-5f12736.zip`; full local suite `588 passed`, expected `StarletteDeprecationWarning`; latest real VPS API-only smoke passed 2026-06-03, `run_id=20260603T112418Z`, evidence `research/amn2/api-vps-smoke-evidence-2026-06-03.md`; fast-forward merged into `codex-vps-test-prep` at production head `5f12736`.
- Post Dry-Run Read-Only Integration Status: branch `amn2/codex/post-dry-run-read-only-integration`, commit `55a7ed6 Add post dry-run integration status`; добавлены web-admin `/integration-status`, API `GET /api/integration/status` под `server:read`, общий local-only `integration_status` service, route policy/binding tests и `docs/API_TOKEN_POLICY.ru.md` update; focused `31 passed`, full `610 passed`; Phase 2 live single disposable peer apply/revoke passed later on current stable `7764ae7`.

Решение по соседним чатам:

- `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`: широкие research-задачи поставить на паузу; оставить как targeted-input для web-panel UX, config delivery integrity, route taxonomy, scoped API tokens и dangerous-action patterns.
- `VPN Ops Lab — KYORESUAS-API`: уже переведен из reference-only в собственную `amn2` implementation lane на ветке `codex/read-only-api-route-shell`; upstream code не копируем, `/clients` write CRUD, `config:read`, backup/import/reboot не открываем.
- `Переводим AMN на API`: использовать как рабочий чат для установки на сервер, loopback API smoke и исправления ошибок по ветке `codex/read-only-api-route-shell`.
- Соседние направления, которые требуют SSH/sync/config/runtime writes, все еще можно переводить к интеграционным решениям только после controlled real VPS evidence: сначала read-only/dry-run, затем single peer apply/revoke по отдельному подтверждению.

## Что не делать первым

Не расширять production API за пределы уже сделанного read-only aggregate route shell.

Не копировать upstream code.

Не трогать live VPS из lab-чата.

Не считать старые заметки `implemented-needs-live-retest` актуальными: они исторические, live baseline уже подтвержден.

## Связанные документы

Главный migration handoff:

```text
docs/NEXT_CHAT_AFTER_AMN2_VPS_LIVE.ru.md
```

API/upstream start:

```text
docs/NEXT_CHAT_KYORESUAS_API.ru.md
research/upstreams/kyoresuas-amnezia-api.md
```

`amn2` transfer context:

```text
research/amn2/README.md
research/amn2/transfer-backlog.md
research/amn2/remote-operations-inventory.md
research/amn2/config-delivery-inventory.md
research/amn2/route-auth-machine-checkable-tests-plan.md
research/amn2/backup-import-dangerous-api-design.md
research/amn2/manager-config-export-contract.md
research/amn2/manager-config-export-contract-implementation.md
research/amn2/public-self-service-config-delivery-policy.md
research/amn2/public-config-delivery-policy-contract-implementation.md
research/amn2/backup-import-policy-contract-implementation.md
research/amn2/secret-inventory-registry-implementation.md
research/amn2/kyoresuas-api-integration-priority-plan.md
amn2/docs/API_VPS_SMOKE_EVIDENCE.ru.md
amn2/docs/API_TOKEN_POLICY.ru.md
```

Pre-VPS support package:

```text
research/amn2/vps-gate-evidence-checklist.md
research/amn2/post-vps-gate-merge-decision.md
research/amn2/docker-manager-design-note.md
research/amn2/ssh-host-key-enrollment-design.md
research/amn2/neighbor-chat-vps-gate-handoff.md
research/amn2/read-only-metrics-privacy-classification.md
research/amn2/local-agent-runtime-metadata-alignment.md
research/amn2/api-token-rotation-revoke-policy.md
research/amn2/post-dry-run-read-only-integration-implementation.md
```

Existing unification design:

```text
docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md
```

## Local Agent baseline status

Local Agent first slice:

```text
status: merged into codex-vps-test-prep via PR #2
commits: 3119ee6, ac2baa8
```

Local Agent production wiring:

```text
status: merged into codex-vps-test-prep via PR #3
head: 8697b60 Document Local Agent production wiring
```

Локальная проверка показала, что эти commits уже содержались в production baseline после `91aeb3e`. Позднее Local Agent получил hardening commit `c5d7eb6`: repository-backed audit sink для allowed read routes, safe `/agent/version` metadata и тесты, что raw bearer token не попадает в audit. Runtime metadata boundary для будущего controller summary зафиксирован в `research/amn2/local-agent-runtime-metadata-alignment.md`; token lifecycle boundary - в `research/amn2/api-token-rotation-revoke-policy.md`, а local-only lifecycle gate выполнен в `amn2/codex/api-token-lifecycle-gate-stacked`, commit `256d0c0`. Следующий Local Agent slice не должен добавлять clients/configs/write routes.

## Рекомендуемый порядок

1. Не открывать второй параллельный API shell: read-only API route shell уже прошел local suite, real VPS loopback smoke и fast-forward merge в stable `codex-vps-test-prep`.
2. API/web-panel implementation slice выполнен, запушен, fast-forward merged в `codex-vps-test-prep` и повторно проверен на stable checkout: commit `294803e Add API readiness and token web pages`; focused `39 passed`, full `594 passed`.
3. VPS API/web-panel gate для production head `294803e` пройден 2026-06-04: API loopback smoke `run_id=20260604T102355Z`, `server_db_sync_status=passed`, API/auth/scope/revoke/listener/audit `passed`, web-admin `API readiness` и `API tokens` routes доступны. Evidence: `research/amn2/api-web-panel-vps-evidence-2026-06-04.md`.
4. Remote-operation VPS gate branch обновлена поверх stable head `294803e`: `codex/remote-operation-vps-gate-prep`, head `7281254`; focused `71 passed`, full `603 passed`; AMN3 package `dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip`.
5. Controlled real VPS verification gate Phase 1 для `codex/remote-operation-vps-gate-prep` пройден 2026-06-04 как `dry-run-only-pass`: API sanity, read-only server check, traffic dry-run, apply-peer dry-run metadata и revoke-peer dry-run metadata passed. Evidence: `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`.
6. Controlled real VPS verification gate Phase 2 пройден 2026-06-05 на current stable `7764ae7` как `verified-live` для ровно одного disposable test peer apply/sync/revoke/sync. Evidence: `research/amn2/phase-2-live-vps-gate-evidence-2026-06-05.md`.
7. Любой API/web/agent route, который вызывает SSH, syncs peers, emits config или меняет runtime state, остается отдельным gated slice; Phase 2 не открывает broad write lifecycle.
7. Route/Auth binding tests, scoped API token lifecycle, secret inventory, public config policy and backup/import policy остаются обязательными baselines перед дальнейшим route expansion.
8. `/clients` write CRUD, API `config:read`, public config delivery, backup/import/reboot, public docs/metrics, domain exclusions и 2FA не открывать до отдельного решения.

## Route/Auth/Operation Policy Matrix Plan

Статус: `implemented-in-amn2-local-commit`.

Новый AMN3 artifact:

```text
docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md
```

Production branch:

```text
codex-vps-test-prep
```

Production commit:

```text
d1d9690 Add route auth operation policy matrix
```

Создано в `amn2`:

- `app/security/surface_policy.py`
- `tests/security/test_surface_policy.py`
- `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

Проверка:

```text
focused policy/agent/server tests: 46 passed
web/bot smoke tests: 85 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Новые API endpoints не добавлялись. Новые write/config delivery flows не включались.

Обновленный порядок:

1. `amn2` commit `d1d9690` запушен в remote branch `codex-vps-test-prep`.
2. Следующий local-only slice выбран и выполнен: redaction coverage.
3. Следующий local-only slice проверен: config delivery integrity.

## Redaction Coverage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
94ad807 Document secret-bearing delivery artifacts
```

Production commits:

```text
75c235a Expand redaction primitive coverage
fc73929 Add config delivery redaction coverage
f62d5d6 Harden config email audit coverage
eb735e2 Harden remote output redaction coverage
94ad807 Document secret-bearing delivery artifacts
```

Проверка:

```text
focused redaction/security/delivery/remote/docs tests: 61 passed, 1 StarletteDeprecationWarning
full local suite: 528 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет live apply/revoke/config/sync behavior, поэтому VPS gate не нужен.

## Config Delivery Integrity Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head used for verification:

```text
94ad807 Document secret-bearing delivery artifacts
```

Relevant production commits already present in branch:

```text
952cc49 Add config delivery artifact metadata
4b19cd3 Add config delivery utf8 artifact tests
fc73929 Add config delivery redaction coverage
```

Проверка:

```text
tests/bot/test_delivery.py tests/services/test_config_delivery.py tests/vpn/test_config_templates.py -v
result: 16 passed

full local suite at same head: 528 passed, 1 StarletteDeprecationWarning
```

Покрыто: `.conf` UTF-8 bytes, QR payload equality, `vpn://` round-trip, non-ASCII fixture, `client-config-secret` metadata and redaction behavior for text diagnostics.

Live VPS не трогался. Slice не меняет live templates/defaults или apply/sync behavior, поэтому VPS gate не нужен.

## Public Token Safety Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
dfe27ee Harden public email token safety
```

Покрыто:

- `create_email_token` теперь отклоняет `ttl_minutes <= 0`;
- raw token хранится/сравнивается через hash-only contract;
- public verify/recover tokens не взаимозаменяемы по `purpose`;
- expired verify/recover codes отклоняются;
- denial response не возвращает сырой token;
- wrong-purpose/expired tokens не consumed.

Проверка:

```text
tests/services/test_email_tokens.py tests/web/test_email_delivery.py -q --basetemp tmp\pytest-public-token
result: 14 passed, 1 StarletteDeprecationWarning

full local suite:
535 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не меняет peer apply/revoke/config/sync/runtime behavior, поэтому VPS gate не нужен.

## Local Agent Hardening Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
c5d7eb6 Harden Local Agent audit contract
```

Покрыто:

- `agent serve` подключает repository-backed audit sink;
- allowed read routes пишут `local_agent_read` в `admin_actions`;
- audit metadata содержит route, scope, risk class, token id/owner и result без raw bearer token;
- `/agent/version` отдает `runtime_contract_version`, `first_slice_routes` и `write_enabled=false`;
- first-slice boundary остается без `/agent/clients`, `/agent/configs`, backup/restore/reboot и write lifecycle.

Проверка:

```text
RED:
tests/agent/test_api.py::test_health_and_version_return_secret_free_metadata
tests/agent/test_cli.py::test_run_agent_server_records_allowed_read_audit_in_database
result: 2 failed as expected

focused agent/security tests:
64 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет локальный agent audit/version contract и docs, но не делает real agent deployment, controller-to-agent calls, peer apply/revoke/config/sync/runtime writes; VPS gate не нужен.

## Web Panel Safe Improvements Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
22dfc37 Clarify web panel operation gates
```

Покрыто:

- server health action помечен как read-only: stores health status only, no VPS changes;
- peer sync action помечен как read-only compare: does not add or remove peers;
- add missing local device confirmation явно говорит, что это live VPS write и должен идти через VPS gate;
- config templates page помечает real `.conf`, QR и `vpn://` payloads как secret-bearing delivery artifacts;
- user/device dangerous confirmations уточняют local DB status/data changes и VPS write только при `VPS_APPLY_ENABLED=true`.

Проверка:

```text
RED:
tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions
tests/web/test_servers.py::test_server_sync_run_displays_peer_inventory_report
tests/web/test_config_templates.py::test_config_templates_page_lists_versions_placeholders_and_safe_preview
tests/web/test_users.py::test_user_detail_marks_dangerous_actions_with_confirmation
result: 4 failed as expected

GREEN focused slice:
same 4 tests
result: 4 passed, 1 StarletteDeprecationWarning

focused web/security suite:
tests/web/test_servers.py tests/web/test_users.py tests/web/test_config_templates.py tests/web/test_email_delivery.py tests/security/test_surface_policy.py
result: 75 passed, 1 StarletteDeprecationWarning

full local suite:
536 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice меняет UI wording/templates и web tests, но не меняет peer apply/revoke/config/sync/runtime behavior; VPS gate не нужен.

## Scoped API Token Storage Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex-vps-test-prep
```

Production head after push:

```text
1fdcde5 Add scoped API token storage contract
```

Покрыто:

- `app.services.api_tokens` добавляет hash-only API token contract;
- raw token возвращается только через `ApiTokenIssue.raw_token` в момент выдачи;
- safe metadata содержит `raw_token_display=one-time` и не содержит raw token/hash;
- first-slice scopes ограничены `server:read` и `metrics:read`;
- `config:read`, write scopes и destructive scopes отклоняются;
- `api_tokens` table хранит `token_hash`, sorted `scopes_json`, owner metadata, `expires_at`, `revoked_at`, `last_used_at`;
- auth проверяет token exists, not revoked, not expired, required scope;
- docs фиксируют, что `/api/*` routes не добавлены.

Проверка:

```text
RED:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 1 import error as expected

GREEN focused slice:
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
result: 6 passed

focused security/db/services suite:
tests/services/test_api_tokens.py tests/db/test_repositories.py tests/agent/test_auth.py tests/security/test_surface_policy.py tests/test_file_hygiene.py
result: 54 passed

full local suite:
542 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice добавляет local storage/auth contract и docs, но не добавляет API routes, не делает peer apply/revoke/config/sync/runtime writes и не читает live VPS; VPS gate для самого slice не нужен.

## Manager Config Export Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/manager-config-export-contract
```

Production commit:

```text
4d4e7a4 Add manager config export contract
```

Покрыто:

- local-only `ConfigExportRequest` / `ConfigExportResult` / `ConfigExportArtifact` contract;
- adapter from current `DeviceConfigDelivery` / `ConfigDeliveryPackage`;
- typed artifacts for `.conf`, QR payload/PNG, `vpn://` import URI and delivery message;
- safe metadata boundary без raw `.conf`, QR payload, QR PNG/base64, `vpn://`, private key и PSK;
- safe categories for unsupported artifact, unsupported target client and exporter signature mismatch.

Проверка:

```text
focused config/security/delivery suite:
40 passed

full local suite:
560 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public/self-service config endpoint, `/api/*` route, API `config:read`, Local Agent `/configs`, новые QR/import behavior или storage raw config в БД; VPS gate для самого slice не нужен.

## Public/Self-service Config Delivery Policy Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
2ef3af7 Add config share policy contract
```

Покрыто:

- local-only hash-only share-token lifecycle and policy service;
- `config_share_tokens` table and repository create/auth lookup/use/revoke contract;
- blocked future `SurfacePolicy` entries for self-service and public share config download;
- required expiry, purpose `config_share`, resource binding, one-time/max-download denial, revoke and generic public denial;
- safe audit metadata and redacted backup metadata with `restore-disabled`.

Проверка:

```text
focused config/token/security/db suite:
94 passed

full local suite:
577 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет public download route, self-service config download route, `/api/*`, API `config:read`, Local Agent `/configs`, generated config persistence, новые QR/import behavior или live VPS calls; VPS gate для самого slice не нужен.

## Config Share Token Atomic Redeem Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
62d01d9 Add config share token atomic redeem
```

Покрыто:

- `redeem_config_share_token_for_auth` выполняет hash-only lookup и consume в одном DB operation;
- expired/revoked/download-limit tokens не redeem;
- successful redeem immediately increments `download_count` and stores safe usage metadata;
- повторный one-time redeem возвращает `None`;
- raw token не хранится и не выводится.

Проверка:

```text
RED:
tests/db/test_repositories.py::test_redeem_config_share_token_for_auth_is_one_time_and_atomic
result: failed as expected because Repository had no redeem method

focused config-share/db/security suite:
40 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Redeem Decision Adapter Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
9555f4c Add config share redeem decision adapter
```

Покрыто:

- `redeem_config_share_download` converts raw token to hash immediately;
- adapter performs hash-only auth lookup and policy decision before consuming;
- invalid device/artifact request does not consume a one-time token;
- allowed decision performs atomic redeem;
- redeem race returns denied `download_limit_reached`;
- safe audit metadata excludes raw token, token hash and config payload.

Проверка:

```text
RED:
tests/services/test_config_share_tokens.py
result: import error as expected because redeem_config_share_download did not exist

focused config-share/db/security suite:
43 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Redeem DB Row Status Join Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
548618a Add config share redeem row status join
```

Покрыто:

- `get_config_share_token_for_auth` принимает `requested_device_id`;
- auth lookup возвращает реальные `device_status` и `server_status` из DB row/JOIN;
- multi-bound token lookup использует статус именно requested device;
- inactive device/server denial происходит before atomic consume;
- unbound device request остается `resource_not_bound` и не маскируется inactive-status deny;
- raw token/config payload не сохраняются и не выводятся.

Проверка:

```text
RED:
tests/db/test_repositories.py::test_config_share_token_auth_lookup_includes_bound_device_and_server_status
tests/db/test_repositories.py::test_config_share_token_auth_lookup_prefers_requested_device_status
result: failed as expected because auth row did not expose device_status/server_status and did not accept requested_device_id

focused config-share/db/security suite:
69 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Redeem Audit Event No-Payload Logging Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
83d8331 Add config share redeem audit events
```

Покрыто:

- `redeem_config_share_download` принимает optional `audit_store`;
- allowed и denied decisions пишутся как `config.share.download_allowed` /
  `config.share.download_denied`;
- audit target привязан к owner user и requested device;
- audit metadata строится только через `safe_audit_metadata`;
- raw token, token hash, `.conf`, QR/import URI, `vpn://`, private keys, PSK
  и config payload не попадают в audit metadata;
- SQLite integration test подтверждает запись safe event в `admin_actions`.

Проверка:

```text
RED:
tests/services/test_config_share_tokens.py::test_redeem_config_share_download_records_allowed_audit_without_payloads
tests/services/test_config_share_tokens.py::test_redeem_config_share_download_records_denied_audit_without_payloads_or_consume
result: failed as expected because audit_store was not accepted yet

focused config-share/db/security suite:
72 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Redeem Rate Limit Policy Boundary Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
56e49ff Add config share redeem rate limit boundary
```

Покрыто:

- `redeem_config_share_download` принимает optional `rate_limit_store`;
- rate-limit check выполняется before token lookup;
- blocked attempt не делает token lookup и не consumes token;
- blocked attempt возвращает generic public denial без раскрытия token validity;
- allowed/denied attempts записываются в rate-limit store safe metadata only;
- raw token, token hash, QR/import URI, `vpn://`, private keys, PSK и config
  payload не попадают в rate-limit/audit metadata.

Проверка:

```text
RED:
tests/services/test_config_share_tokens.py::test_redeem_config_share_download_rate_limit_blocks_before_token_lookup
tests/services/test_config_share_tokens.py::test_redeem_config_share_download_records_safe_rate_limit_attempt_on_denied_request
result: failed as expected because rate_limit_store was not accepted yet

focused config-share/db/security suite:
75 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Redeem Rate Limit Repository Persistence Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
b8fb466 Add config share redeem rate limit persistence
```

Покрыто:

- добавлена SQLite table `config_share_redeem_attempts`;
- добавлен индекс по `scope_key` и `attempted_at`;
- `Repository.record_config_share_redeem_attempt` сохраняет safe attempt metadata;
- `Repository.is_config_share_redeem_rate_limited` блокирует после 5 denied
  attempts за 10 минут;
- allowed и старые attempts не блокируют scope;
- repository-backed rate-limit blocks before consume and keeps generic denial;
- raw token, token hash, QR/import URI, `vpn://`, private keys, PSK и config
  payload не сохраняются.

Проверка:

```text
RED:
tests/db/test_repositories.py::test_config_share_redeem_rate_limit_persists_safe_attempts_and_blocks_scope
tests/db/test_repositories.py::test_config_share_redeem_rate_limit_ignores_allowed_and_old_attempts
result: failed as expected because repository persistence methods were missing

focused config-share/db/security suite:
78 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Public Route Block Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
3ad001f Add config share public route block contract
```

Покрыто:

- `public_token.config_share_download.blocked` остаётся `blocked-future`;
- policy не включает новое поведение;
- FastAPI web route inventory не содержит public config-share download route;
- policy теперь ссылается на route-binding contract test;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/security/test_surface_policy_bindings.py::test_public_config_share_download_route_stays_unmounted
result: failed as expected because the blocked-future policy had no route-binding contract test_ref

focused config-share/db/security/web suite:
92 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Token Backup Redaction Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
5aecfed Add config share backup redaction guard
```

Покрыто:

- backup manifest декларирует exclusion для usable config-share token hashes;
- `BackupService.create()` блокирует database с usable config-share token hashes;
- `BackupService.restore()` блокирует archive с usable config-share token hashes
  до появления explicit dangerous mode;
- legacy backup manifests без нового exclusion остаются verify-compatible;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_verify_and_restore_requires_secret
tests/backup/test_backup_service.py::test_backup_create_rejects_usable_config_share_token_hashes
tests/backup/test_backup_service.py::test_restore_rejects_usable_config_share_token_hashes_before_writing_target
tests/backup/test_backup_service.py::test_verify_accepts_legacy_manifest_excludes_without_share_token_hashes
result: failed as expected because manifest exclusion and create/restore guards were missing, and legacy manifest compatibility needed explicit handling

focused backup/config-share/db/security suite:
101 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Dangerous Mode Gate Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
ca4aa7c Add config share restore dangerous mode gate
```

Покрыто:

- добавлен закрытый gate metadata
  `CONFIG_SHARE_RESTORE_USABLE_TOKEN_HASHES_DANGEROUS_MODE`;
- `BackupService.restore(..., restore_usable_config_share_tokens=True)` явно
  отклоняется, потому что dangerous mode gate ещё не implemented;
- target DB не создаётся при попытке включить dangerous mode;
- CLI restore не exposes dangerous-mode флаг;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_restore_usable_config_share_tokens_dangerous_mode_gate_is_closed
tests/backup/test_backup_service.py::test_restore_rejects_explicit_share_token_dangerous_mode_before_writing_target
result: failed as expected because the gate metadata and explicit restore parameter were missing

focused backup/config-share/db/security suite:
104 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore History Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
380f3a3 Add config share restore history contract
```

Покрыто:

- добавлен явный restore history policy contract для config-share records;
- usable share-token hashes остаются blocked без dangerous mode;
- expired/revoked/exhausted config-share records разрешены для restore только как
  non-usable historical metadata;
- restore сохраняет historical rows без открытия dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_config_share_restore_history_policy_documents_allowed_non_usable_states
result: failed as expected because the restore history policy method was missing

focused backup/config-share/db/security suite:
108 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Policy Shape Validation Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
6387e9e Add config share restore policy shape guard
```

Покрыто:

- backup create валидирует shape config-share token policy перед сборкой backup;
- backup restore валидирует shape config-share token policy до записи target DB;
- malformed one-time policy shape отклоняется как invalid policy shape, а не
  классифицируется как historical metadata;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_malformed_config_share_token_policy_shape
tests/backup/test_backup_service.py::test_restore_rejects_malformed_config_share_token_policy_shape_before_writing_target
result: failed as expected because malformed policy shape was not rejected

focused backup/config-share/db/security suite:
110 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Timestamp Shape Validation Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
52c5340 Add config share restore timestamp shape guard
```

Покрыто:

- backup create валидирует config-share `expires_at` даже для revoked rows;
- backup restore валидирует config-share `revoked_at` до записи target DB;
- malformed timestamp metadata не может обойти validation через
  history-only классификацию;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_malformed_config_share_token_expires_at_even_when_revoked
tests/backup/test_backup_service.py::test_restore_rejects_malformed_config_share_token_revoked_at_before_writing_target
result: failed as expected because malformed timestamp metadata was not rejected

focused backup/config-share/db/security suite:
112 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Scope Metadata Shape Validation Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
f815ed2 Add config share restore scope metadata guard
```

Покрыто:

- backup create валидирует config-share scope metadata до сборки backup;
- backup restore валидирует config-share scope metadata до записи target DB;
- malformed `bound_device_ids_json`, `bound_server_ids_json`,
  `allowed_artifact_kinds_json` и `target_client` не маскируются как
  history-only metadata;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_malformed_config_share_token_scope_metadata
tests/backup/test_backup_service.py::test_restore_rejects_malformed_config_share_token_scope_metadata_before_writing_target
result: failed as expected because malformed scope metadata was not rejected before dangerous-mode guard

focused backup/config-share/db/security suite:
120 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Token Identity Metadata Validation Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
bb9ce25 Add config share restore identity metadata guard
```

Покрыто:

- backup create валидирует config-share token identity metadata до сборки backup;
- backup restore валидирует config-share token identity metadata до записи target DB;
- malformed `id`, `token_hash`, `token_prefix`, `created_by_actor`,
  `owner_user_id` не маскируются как history-only metadata;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_malformed_config_share_token_identity_metadata
tests/backup/test_backup_service.py::test_restore_rejects_malformed_config_share_token_identity_metadata_before_writing_target
result: failed as expected because malformed identity metadata was not rejected before dangerous-mode guard

focused backup/config-share/db/security suite:
130 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Foreign Key Integrity Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
af7dde9 Add config share restore foreign key guard
```

Покрыто:

- backup create проверяет SQLite foreign key integrity до сборки backup;
- backup restore проверяет SQLite foreign key integrity до записи target DB;
- broken historical config-share records не принимаются как валидная история,
  если нарушены связи с родительскими таблицами;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_foreign_key_integrity_violations
tests/backup/test_backup_service.py::test_restore_rejects_foreign_key_integrity_violations_before_writing_target
result: failed as expected because foreign key violations were not rejected before backup/target DB write

focused backup/config-share/db/security suite:
132 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Schema Foreign Key Declaration Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
6a1ca94 Add config share restore foreign key schema guard
```

Покрыто:

- backup create проверяет наличие FK declaration
  `config_share_tokens.owner_user_id -> users.id` до сборки backup;
- backup restore проверяет тот же schema contract до записи target DB;
- backup DB с пересозданной `config_share_tokens` без owner FK не принимается
  как валидная history-only база;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_missing_config_share_owner_foreign_key_declaration
tests/backup/test_backup_service.py::test_restore_rejects_missing_config_share_owner_foreign_key_declaration_before_writing_target
result: failed as expected because missing FK declaration was not rejected before backup/target DB write

focused backup/config-share/db/security suite:
134 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Schema Check Constraint Declaration Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
52f673e Add config share restore check schema guard
```

Покрыто:

- backup create проверяет наличие `CHECK` declarations для
  `config_share_tokens.purpose`, `max_downloads`, `download_count` до сборки
  backup;
- backup restore проверяет тот же schema contract до записи target DB;
- backup DB с валидными строками, но ослабленной `config_share_tokens` schema,
  не принимается как полноценная history-only база;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_missing_config_share_check_constraint_declarations
tests/backup/test_backup_service.py::test_restore_rejects_missing_config_share_check_constraint_declarations_before_writing_target
result: failed as expected because missing CHECK declarations were not rejected before backup/target DB write

focused backup/config-share/db/security suite:
136 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Schema Unique Constraint Declaration Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
4cf1e85 Add config share restore unique schema guard
```

Покрыто:

- backup create проверяет, что `config_share_tokens.id` остаётся primary key
  до сборки backup;
- backup create проверяет, что `config_share_tokens.token_hash` остаётся
  unique constraint/index;
- backup restore проверяет тот же token-identity schema contract до записи
  target DB;
- backup DB с валидными строками, но ослабленной `config_share_tokens` identity
  schema, не принимается как полноценная history-only база;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_missing_config_share_unique_constraint_declarations
tests/backup/test_backup_service.py::test_restore_rejects_missing_config_share_unique_constraint_declarations_before_writing_target
result: failed as expected because missing PK/UNIQUE declarations were not rejected before backup/target DB write

focused backup/config-share/db/security suite:
138 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Required Columns Schema Declaration Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
1f0343d Add config share restore required columns guard
```

Покрыто:

- backup create проверяет, что optional history table `config_share_tokens`
  сохраняет полный набор required columns до сборки backup;
- backup restore проверяет тот же required-columns schema contract до записи
  target DB;
- backup DB с валидными FK/CHECK/UNIQUE declarations, но ослабленной
  `config_share_tokens` schema без required column, не принимается как
  полноценная history-only база;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_missing_config_share_required_column_declarations
tests/backup/test_backup_service.py::test_restore_rejects_missing_config_share_required_column_declarations_before_writing_target
result: failed as expected because missing config_share_tokens required columns were not rejected before backup/target DB write

focused backup/config-share/db/security suite:
140 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Config Share Restore Column Declaration Shape Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/public-config-delivery-policy-contract
```

Production commit:

```text
101da38 Add config share restore column declaration guard
```

Покрыто:

- backup create проверяет declaration shape колонок optional history table
  `config_share_tokens` до сборки backup;
- backup restore проверяет тот же column declaration shape contract до записи
  target DB;
- backup DB с полным набором колонок и валидными FK/CHECK/UNIQUE declarations,
  но ослабленным типом/default/NOT NULL shape, не принимается как полноценная
  history-only база;
- usable share-token hashes остаются blocked без dangerous mode;
- public/self-service config delivery remains not-approved.

Проверка:

```text
RED:
tests/backup/test_backup_service.py::test_backup_create_rejects_weakened_config_share_column_declaration_shape
tests/backup/test_backup_service.py::test_restore_rejects_weakened_config_share_column_declaration_shape_before_writing_target
result: failed as expected because weakened config_share_tokens column declaration shape was not rejected before backup/target DB write

focused backup/config-share/db/security suite:
142 passed
```

Live VPS не трогался. Slice не добавляет public download route,
self-service config download route, `/api/*`, API `config:read`, Local Agent
`/configs`, generated config persistence, новые QR/import behavior или live VPS
calls; VPS gate для самого slice не нужен.

## Backup/Import Policy Contract Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/backup-import-policy-contract
```

Production head:

```text
afb2702 Tighten backup import preview type contract
```

Покрыто:

- local-only backup mode registry для `metadata-export`, `redacted-backup` и `encrypted-full-backup`;
- secret field policy для token hashes, peer private key, PSK, admin password hash, `.conf`, QR payload/PNG и `vpn://`;
- safe policy manifest без raw secret values;
- restore/import preview-only contract with `apply_allowed=false` and `side_effects=[]`;
- blocked future `SurfacePolicy` entries для backup/export, restore preview/apply и import preview/apply.

Проверка:

```text
RED:
tests/backup/test_backup_policy.py tests/security/test_surface_policy.py
result: 1 import error as expected

focused backup/security/agent suite:
61 passed

full local suite:
584 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не добавляет web/API backup routes, Local Agent `/backup` или `/restore`, restore apply, import apply, backup-before-write mutation или live VPS calls; VPS gate для самого slice не нужен.

## Secret Inventory Registry Slice

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/secret-inventory-registry
```

Production commit:

```text
9ce42f4 Add secret inventory registry
```

Покрыто:

- `app.security.secret_inventory` как machine-checkable registry secret-bearing state;
- `SecretInventoryEntry` с secret class, storage surface, backup/restore defaults, route exposure и safe metadata policy;
- lookup/filter helpers;
- safe manifest без secret values;
- cross-check, что backup policy secret sources покрыты inventory.

Проверка:

```text
RED:
tests/security/test_secret_inventory.py
result: 1 import error as expected

focused security/backup/token suite:
64 passed

full local suite:
591 passed, 1 StarletteDeprecationWarning
```

Live VPS не трогался. Slice не читает `.env`, не подключается к БД, не добавляет routes, secret-bearing output, backup export, restore/import apply или live VPS calls; VPS gate для самого slice не нужен.

## Remote Operation Dry-run/Audit Slice

Статус: `implemented-pushed-local-gate-complete`.

Production worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-vps-gate-prep
```

Production branch:

```text
codex/remote-operation-vps-gate-prep
```

Production commits:

```text
c249bd0 Add state-changing operation metadata
8af6b5e Add remote partial failure model
b7a12ca Add remote operation dry-run metadata
aca6663 Add VPS gate handoff for remote ops
262d70f Merge current VPS test prep into remote operation gate
7281254 Merge stable API web panel baseline into remote operation gate
```

Покрыто:

- `RemoteOperationRunner.plan()` возвращает `consistency_status=dry-run` для state-changing операций без SSH;
- `OperationPlan.to_safe_metadata()` не публикует command strings и redacts audit/rollback/idempotency metadata;
- `apply-peer` и `revoke-peer` dry-run preview показывает operation ID, risk class, side effects и rollback note без PSK/private config;
- `docs/RUNTIME_REGISTRY.ru.md` и `docs/RUNTIME_REGISTRY.en.md` фиксируют local gate перед real VPS.

Проверка:

```text
focused remote-operation/runtime tests: 71 passed, 1 PytestCacheWarning
full local suite: 603 passed, 1 warning
```

Real VPS Phase 1 read-only/dry-run gate пройден 2026-06-04 как `dry-run-only-pass`: source overlay `7281254` verified, API loopback sanity passed, read-only server check passed, traffic dry-run passed, apply/revoke dry-run metadata passed. Live `--apply`/`--revoke --apply` не запускались. Evidence: `research/amn2/remote-operation-vps-gate-evidence-2026-06-04.md`.

## Local Gate / Live VPS Gate

Новый порядок проверки разделен на два контура.

Локально можно делать:

- policy/inventory-only registry;
- redaction coverage;
- config delivery artifact tests;
- web/bot smoke через TestClient;
- Local Agent read-only/auth/token hardening на fake/local runtime;
- scoped API token storage/auth tests без `/api/*` routes;
- remote operation contracts на fake SSH;
- docs/status/backlog updates.

На real VPS проверяем только после локально зеленого slice, если он меняет:

- peer apply/revoke;
- disable/enable/delete;
- add missing local device;
- remove unknown remote peer;
- peer sync classification;
- config templates/defaults, которые попадут в рабочий client config;
- Docker AmneziaWG write/reload/restart behavior;
- реальный Local Agent deployment или controller-to-agent calls.

Следующий рекомендуемый шаг для текущего git head `c8a6363`: продолжить только read-only next slice после `controlled-prod-ready`. Phase 2 single disposable peer apply/revoke уже verified-live, а `c8a6363` уже прошел real VPS read-only smoke; write lifecycle, config delivery API, Local Agent mutation routes, backup/import/reboot и public API `3040` остаются заблокированы до отдельных gates.

## AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_FINAL_REVIEW_GATE (docs-only continuation)

```text
phase9_private_self_config_readiness_final_review_status=APPROVED_NEXT_GATE_DOCS_ONLY
phase9_private_self_config_readiness_final_review_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_FINAL_REVIEW_GATE
phase9_private_self_config_readiness_final_review_decision=APPROVED_NEXT_GATE_DOCS_ONLY
phase9_private_self_config_readiness_final_review_confirmation=CONFIRMED_BY_5_5
phase9_private_self_config_readiness_final_review_next=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
phase9_private_self_config_readiness_final_review_pass=Neobyatnaya-AMNZ-N_only
phase9_private_self_config_readiness_final_review_limit=SERVER1_or_Сервер1_is_client_display_name_gap_manual_rename_only
phase9_private_self_config_readiness_final_review_fail=generic_naming_as_production_naming|payload_secrets_output|peer_config_public_self_service_action
phase9_private_self_config_readiness_final_review_stop_lines=execution_go=false|peer_creation=false|config_generation=false|config_delivery=false|live_vps_ssh_telegram_public=false
phase9_private_self_config_readiness_final_review_risk_model=docs-only_ready_when_named_gap_isolated_from_generation_delivery
phase9_private_self_config_readiness_final_review_android=Сервер 1
phase9_private_self_config_readiness_final_review_android_fallback=manual_rename
phase9_private_self_config_readiness_final_review_windows=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
phase9_private_self_config_readiness_final_review_ios=not_proven_manual_rename_fallback
```

## AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE (docs-only package prep continuation)

```text
phase9_private_self_config_execution_readiness_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
phase9_private_self_config_execution_readiness_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
phase9_private_self_config_execution_readiness_decision=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
phase9_private_self_config_execution_readiness_confirmation=CONFIRMED_BY_5_5
phase9_private_self_config_execution_readiness_next=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
phase9_private_self_config_execution_readiness_review_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE_REVIEW.ru.md
phase9_private_self_config_execution_readiness_runbook=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RUNBOOK.ru.md
phase9_private_self_config_execution_readiness_result_template=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT_TEMPLATE.ru.md
phase9_private_self_config_execution_readiness_risk_model=docs-only package prep; no live/VPS/SSH/Telegram/public/peer/config actions yet
phase9_private_self_config_execution_readiness_pass=Neobyatnaya-AMNZ-N
phase9_private_self_config_execution_readiness_fail=generic naming as production naming|payload/secrets output|peer/config/public/self-service action
phase9_private_self_config_execution_readiness_stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
phase9_private_self_config_execution_readiness_android=Сервер 1
phase9_private_self_config_execution_readiness_android_classification=localized_SERVER1_client_display_name_compatibility_gap
phase9_private_self_config_execution_readiness_windows=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
phase9_private_self_config_execution_readiness_ios=not_proven/manual_rename_fallback
```

## AMN2 Phase 11 — trusted transport hardening 2026-07-17

Текущий локальный slice закрывает security boundary в Phase 11 runner после
diff-review: `ssh.exe` и `scp.exe` больше не разрешаются через ambient PATH.
Оба бинарника привязаны к абсолютной системной директории OpenSSH
`%WINDIR%\System32\OpenSSH`; отсутствие файла, относительный путь или путь
вне trusted OpenSSH identity завершают runner fail-closed до запуска процесса.

```text
phase11_0b858c5_remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
phase11_0b858c5_ssh_runner_sha256=654154AFF81425DE610817C9FF05FB2D976B2EA3A7843C9FC8F566269C94A6BE
phase11_0b858c5_transport=ssh_absolute|scp_absolute|helper_path_guard|bare_calls_0
phase11_0b858c5_security_rescan=postfix_pass|trusted_calls_3|new_reportable_findings_0
phase11_0b858c5_tests=focused_9_passed|canonical_95_passed|powershell_parse_pass|bash_n_pass|diff_check_pass
phase11_0b858c5_live=upload_false|apply_false|rollback_false|telegram_api_false|regular_bot_disabled|web_db_unchanged|awg_untouched
phase11_0b858c5_approval=previous_phrase_superseded|fresh_phrase_prepared_not_consumed
phase11_0b858c5_evidence=research/amn2/phase-11-remote-orchestrator-byte-binding-fix-2026-07-17.md
phase11_0b858c5_next=WAIT_FOR_EXACT_APPROVAL_THEN_REVIEW_BOUNDED_LIVE_GATE_WITH_AWG_UNTOUCHED
```

Посторонний `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не изменялся и не
включался. VPS, SSH, AWG, Telegram, bot, database и provider mutation не
выполнялись.

## AMN2 Phase 11 — fresh trusted transport approval gate 2026-07-17

После origin-synced hardening подготовлена новая literal approval-фраза. Она
привязывает remote orchestrator SHA и trusted absolute OpenSSH contract;
runner SHA хранится отдельно как evidence и не включается самоссылочно в
собственную строку approval.

```text
phase11_0b858c5_approval_gate=READY_AWAITING_EXACT_APPROVAL|not_consumed
phase11_0b858c5_approval_phrase=APPROVE_PHASE11_0B858C5_REMOTE_ORCHESTRATOR_SHA_A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72_TRUSTED_OPENSSH_ABSOLUTE_PATH_BOUND_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
phase11_0b858c5_approval_effect=private_overlay_upload_web_freeze_snapshot_offline_apply_verify_and_rollback_only|regular_bot_disabled|telegram_profile_unchanged|awg_untouched
phase11_0b858c5_forbidden=telegram_002b_activation|profile_media_mutation|schema_write|provider_mutation|awg_service_peer_config_mutation
phase11_0b858c5_gate_evidence=research/amn2/phase-11-0b858c5-trusted-transport-approval-gate-2026-07-17.md
```

До отдельного сообщения оператора, дословно равного phrase выше, runner не
запускается; VPS, SSH, Telegram, bot, database, provider и AWG не трогаются.

## AMN2 Phase 11 — `0b858c5` combined overlay rollout pass 2026-07-17

Exact trusted-transport approval получена и потреблена один раз. Bounded
transaction `20260717T081340Z` обновила только tracked source overlay и
private web runtime. Automatic rollback не понадобился; проверенный rollback
bundle сохранён.

```text
phase11_0b858c5_rollout=PASS|run_20260717T081340Z|approval_consumed
phase11_0b858c5_before=801f8c3
phase11_0b858c5_after=0b858c5
phase11_0b858c5_package=sha256_7866bdd9febe1d6eea701b37a6e4206a8267766a56993f3c02a0c7b30c394b54|exact_two_files|mode_0600|remote_receipt_pass
phase11_0b858c5_source=commit_0b858c5cdbc5b565cc265966a2edfe2d339d65e0|delta_31_exact
phase11_0b858c5_assets=canonical_square_verified|wide_language_header_verified|telegram_profile_unchanged
phase11_0b858c5_web=active_enabled_http_ok_loopback_only
phase11_0b858c5_bot=inactive_disabled_process_0|unit_env_unchanged|activation_false
phase11_0b858c5_db=integrity_ok|fk_0|tables_15|rows_88|file_logical_counts_hashes_unchanged
phase11_0b858c5_awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged|mutation_false
phase11_0b858c5_rollback=retained_verified|not_needed
phase11_0b858c5_postflight=independent_new_session_pass
phase11_0b858c5_second_vps=not_used
phase11_0b858c5_provider_mutation=false
phase11_0b858c5_next=REVIEW_PHASE11_TELEGRAM_002B_PERSISTENT_BOT_ACTIVATION_GATE_WITHOUT_ACTIVATION
phase11_0b858c5_rollout_evidence=research/amn2/phase-11-0b858c5-combined-overlay-rollout-2026-07-17.md
```

Telegram API/profile mutation, persistent bot install/enable/start, database
write/migration, provider action, peer/config change и любые AWG actions не
входили в consumed approval и не выполнялись.

## AMN2 Phase 11 — TELEGRAM-002B staged persistent activation local closeout 2026-07-17

Локальная design/TDD/implementation часть выполнена и подготовлена к отдельному
live gate. Реальный SSH/VPS/Telegram/systemd запуск, production DB write,
regular bot activation, provider mutation и AWG action не выполнялись.

```text
phase11_telegram_002b_status=READY_AWAITING_SEPARATE_EXACT_LIVE_APPROVAL
phase11_telegram_002b_source_overlay=0b858c5
phase11_telegram_002b_remote_sha256=14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64
phase11_telegram_002b_runner_sha256=4038FD648F6834AF03A1D44BCD1E0CA63B78FC41CCB48A24D9245B1166FA53B7
phase11_telegram_002b_tests=focused_18_passed|canonical_113_passed|bash_n_pass|powershell_parse_pass
phase11_telegram_002b_security=complete_coverage|reportable_findings_0
phase11_telegram_002b_live_action=false
phase11_telegram_002b_regular_bot=inactive_disabled
phase11_telegram_002b_telegram_profile=unchanged
phase11_telegram_002b_db_live_write=false
phase11_telegram_002b_provider_mutation=false
phase11_telegram_002b_awg=untouched
phase11_telegram_002b_evidence=research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md
phase11_telegram_002b_next=WAIT_FOR_SEPARATE_EXACT_LIVE_APPROVAL_THEN_REVIEW_BOUNDED_GATE
```

Prepared phrase (not consumed):

```text
APPROVE_PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

## AMN2 Phase 11 — TELEGRAM-002B preflight correction override 2026-07-17

Первый literal-approved preflight дошёл до production executor и остановился
fail-closed только потому, что `/opt/amn2/venv/bin/python` является обычным
venv symlink. Source/unit/env/overlay marker присутствуют; stage, accept,
regular bot start и AWG mutation не выполнялись. Executor исправлен локально:
`readlink -f` должен привести Python к regular executable target.

```text
phase11_telegram_002b_preflight=fail_closed|venv_symlink_target_binding_only
phase11_telegram_002b_stage=false|accept=false|postflight=false
phase11_telegram_002b_awg=untouched
phase11_telegram_002b_new_remote_sha256=3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881
phase11_telegram_002b_new_approval=required|old_sha_phrase_invalidated
phase11_telegram_002b_evidence=research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md
```

Новая approval-фраза публикуется только после локального тест/security/commit/
push closeout этого correction slice.

## AMN2 Phase 11 — TELEGRAM-002B journal-ingest correction override 2026-07-17

Corrected preflight прошёл. Disabled-first stage run `20260717T115918Z`
остановился fail-closed до сообщения оператора: очищенный admission receipt
появился в journald после одноразовой проверки. Диагностика затем подтвердила
marker counts admission/pending/allowed-updates `1/1/1`, errors `0`, rollback
receipt и повторный безопасный preflight. `/start` не отправлялся.

```text
phase11_telegram_002b_stage=fail_closed_before_operator_start|run_20260717T115918Z
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_rollback=receipt_present|stale_timer_stopped_after_safe_state_check
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_awg=running|restart_0|peers_12|unchanged
phase11_telegram_002b_journal_correction=bounded_sanitized_receipt_retry_15s|exact_run_timer_cleanup
phase11_telegram_002b_new_remote_sha256=FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F
phase11_telegram_002b_new_runner_sha256=F478A883ADE570D7A594F04B91062E1A1275467AFFE3D71877BE441D87FDA137
phase11_telegram_002b_signal_fix=rollback_then_nonzero_exit|no_stage_or_accept_resume
phase11_telegram_002b_signal_poc=term_exit_143|no_privileged_mutation_or_stage_pass
phase11_telegram_002b_tests=focused_21_passed|canonical_116_passed|bash_n_pass|powershell_parse_pass
phase11_telegram_002b_security=complete_9_of_9|former_candidates_closed|reportable_findings_0
phase11_telegram_002b_security_report=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\135955aa9fdf078708d02bf5848c030fac350db4_20260717T131800Z\report.md
phase11_telegram_002b_new_approval=required|all_earlier_sha_phrases_invalidated
phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
```

Новая exact phrase публикуется только после test/security/commit/push
closeout этого correction slice.

## AMN2 Phase 11 — TELEGRAM-002B exact single-line receipt correction override 2026-07-17

Буквальная FA3F approval была получена. Fresh production preflight прошёл.
Disabled-first stage остановился fail-closed до `/start` на структурной
несовместимости journal receipt verifier. Независимый повторный preflight
подтвердил автоматический rollback и прежний production baseline.

```text
phase11_telegram_002b_fa3f_preflight=PASS
phase11_telegram_002b_fa3f_stage=FAIL_CLOSED_BEFORE_OPERATOR_START|sanitized_receipt_shape_mismatch
phase11_telegram_002b_operator_start=false
phase11_telegram_002b_accept=false|enable=false|postflight=false
phase11_telegram_002b_postfailure_preflight=PASS
phase11_telegram_002b_web=active_enabled_http_ok_loopback_only
phase11_telegram_002b_db=integrity_ok|fk_0|tables_15|rows_88|counts_hash_FEDD60460F70DB5DE23EB0566A68AF772C0351242A8712B37C3F19A1C53CADF1
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_telegram=identity_match|webhook_empty|backlog_0
phase11_telegram_002b_awg=running|restart_0|peers_12|container_hash_267BD715ED6B788FFAE1E59B3E7741ED6932756D25A00C5B7AAAC7492796C79B|peer_set_hash_E42E1176843B82A748081EDDB8E45A9852C1627A13BC08B9F69A4E4C70B81BB5
phase11_telegram_002b_root_cause=0b858c5_single_line_receipt|split_line_anchor_verifier
phase11_telegram_002b_new_remote_sha256=56BE81549B86B5DBF09AA23A8513E652F6AF344E88C131FC8EAA2D5D5403F2CE
phase11_telegram_002b_new_runner_sha256=04DF10C9305CFA46843981A851A07B98B658A92859135A8180BCE15363F39951
phase11_telegram_002b_tests=focused_21_passed|canonical_116_passed|bash_n_pass|powershell_parse_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0
phase11_telegram_002b_security_report=C:\Users\SooL\AppData\Local\Temp\codex-security-scans\VPS-OPS-LAB\73207d114977189974b5aacea532c5c8466f64ce_20260717T141444Z\report.md
phase11_telegram_002b_fa3f_authority=consumed_and_invalidated_by_changed_remote_bytes
phase11_telegram_002b_new_approval=required
phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
phase11_telegram_002b_next=TEST_DOCS_COMMIT_PUSH_ORIGIN_READBACK_THEN_ISSUE_NEW_EXACT_APPROVAL
```

Production AWG не останавливался и не изменялся. Provider, Telegram profile и
production peer/config mutations не выполнялись.

## AMN2 Phase 11 — TELEGRAM-002B expired operator window classification 2026-07-17

DF9E preflight/stage прошли, но run `20260717T150504Z` истёк без `/start`.
Automatic rollback вернул bot inactive/disabled/process 0; DB counts, web и
AWG baseline сохранены. Два последующих preflight завершились только внутри
обезличенного Telegram admission probe.

```text
phase11_telegram_002b_df9e_stage=PASS|AWAITING_START_THEN_EXPIRED
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_rollback=PASS|bot_inactive_disabled_process_0
phase11_telegram_002b_repeat_preflight=TELEGRAM_FAILED_TWICE|OLD_BYTES_HIDE_CATEGORY
phase11_telegram_002b_db=integrity_ok|fk_0|tables_15|rows_88
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
phase11_telegram_002b_classifier=fixed_reason_allowlist|no_secret_or_update_content|no_acknowledgement
phase11_telegram_002b_new_remote_sha256=2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2
phase11_telegram_002b_new_runner_sha256=75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53
phase11_telegram_002b_tests=focused_23_passed|canonical_118_passed|syntax_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0
phase11_telegram_002b_next=COMMIT_PUSH_READBACK_THEN_2FDB_CLASSIFIED_PREFLIGHT
phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
```

До classified preflight `/start` не отправлять. AWG не останавливать.

## AMN2 Phase 11 — TELEGRAM-002B unbuffered receipt correction override 2026-07-17

Полученная literal SHA `56BE8154...` authority была использована. Fresh
production preflight прошёл; disabled-first stage остановился fail-closed до
операторского `/start` на отсутствующем sanitized receipt. Accept, enable и
postflight не выполнялись. Independent post-failure preflight подтвердил
автоматический rollback и прежний production baseline.

Root cause по точному source archive `0b858c5`: `app.main` использует default
`print` для receipt, unit запускает Python без unbuffered mode, а persistent
polling не завершает процесс и не сбрасывает stdout buffer. Correction
добавляет `PYTHONUNBUFFERED=1` в существующий atomic `.env` contract, который
уже включён в snapshot и metadata-preserving rollback.

```text
phase11_telegram_002b_56be_preflight=PASS
phase11_telegram_002b_56be_stage=FAIL_CLOSED_BEFORE_OPERATOR_START|STDOUT_BUFFERED
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_postfailure_preflight=PASS
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_web=active_enabled_http_ok_loopback_only
phase11_telegram_002b_db=integrity_ok|fk_0|tables_15|rows_88|counts_hash_unchanged
phase11_telegram_002b_telegram=identity_match|webhook_empty|backlog_0
phase11_telegram_002b_awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged
phase11_telegram_002b_root_cause=default_print|systemd_no_unbuffered_mode|persistent_stdout_buffer
phase11_telegram_002b_new_remote_sha256=E407421F358703C4D6FE1825EE46EFBC4E72C3840FEBAC89F131800F30DB412F
phase11_telegram_002b_new_runner_sha256=20944C777A5EAB534964577C8BD3F9B71C9ADAE8310E3C93F56EB70BE0EE86B5
phase11_telegram_002b_tests=focused_22_passed|canonical_117_passed|syntax_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0|secret_patterns_0
phase11_telegram_002b_56be_authority=consumed_and_invalidated_by_changed_remote_bytes
phase11_telegram_002b_new_approval=required
phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
phase11_telegram_002b_next=DOCS_COMMIT_PUSH_ORIGIN_READBACK_THEN_ISSUE_NEW_EXACT_APPROVAL
```

AWG не останавливался и не изменялся; provider, Telegram profile, web source и
production peer/config mutations не выполнялись.

## AMN2 Phase 11 — TELEGRAM-002B exact plan-timestamp startup gate 2026-07-17

E407 literal authority была получена. Fresh preflight прошёл; исправленный
unbuffered admission receipt появился и был принят. Stage затем остановился
fail-closed до `/start`, поскольку startup изменил application-row. Accept,
enable и postflight не выполнялись. Independent post-failure preflight
подтвердил bot inactive/disabled/process 0, integrity/FK/counts baseline,
Telegram backlog 0 и неизменный AWG.

Exact source trace: `create_workflow()` вызывает `seed_default_plans()`, а
`upsert_plan()` обновляет `plans.updated_at=CURRENT_TIMESTAMP` при каждом
conflict. Это ожидаемое metadata-only изменение уже сохранено; слепое DB
restore запрещено и не выполнялось. Correction позволяет только этот столбец,
требует неизменности всех остальных данных и запечатывает post-start baseline
до первого admin `/start`.

```text
phase11_telegram_002b_e407_preflight=PASS
phase11_telegram_002b_e407_receipt=PASS|UNBUFFERED_FIX_EFFECTIVE
phase11_telegram_002b_e407_stage=FAIL_CLOSED_BEFORE_OPERATOR_START|DEFAULT_PLAN_UPDATED_AT
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_postfailure_preflight=PASS
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_db=integrity_ok|fk_0|tables_15|rows_88|plan_timestamp_metadata_only
phase11_telegram_002b_telegram=identity_match|webhook_empty|backlog_0
phase11_telegram_002b_awg=running|restart_0|peers_12|container_and_peer_set_hashes_unchanged
phase11_telegram_002b_startup_delta_contract=plans_updated_at_only_or_unchanged|counts_exact|first_admin_exact|post_start_baseline_sealed
phase11_telegram_002b_new_remote_sha256=DF9E0BAD6359AD7F3100A7FBED5ED1223721C656086D0CADA72CA492BD10B396
phase11_telegram_002b_new_runner_sha256=16E6F846DEB3DC52838224E277D65AA2D0059D6288C827248607A7F6E5943CED
phase11_telegram_002b_tests=focused_23_passed|canonical_118_passed|syntax_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0|secret_patterns_0
phase11_telegram_002b_e407_authority=consumed_and_invalidated_by_changed_remote_bytes
phase11_telegram_002b_new_approval=required
phase11_telegram_002b_approval_phrase=WITHHELD_UNTIL_ORIGIN_SYNC
phase11_telegram_002b_next=DOCS_COMMIT_PUSH_ORIGIN_READBACK_THEN_ISSUE_DF9E_EXACT_APPROVAL
```

AWG, provider, Telegram profile, web source и peer configuration не
изменялись.
