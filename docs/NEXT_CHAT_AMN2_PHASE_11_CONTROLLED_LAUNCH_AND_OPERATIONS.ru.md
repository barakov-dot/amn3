# Следующий task: AMN2 Phase 11 Controlled Launch and Operations

## Post-release Spain fresh-start override 2026-07-19

```text
active_phase=Post-release controlled operations
phase11_status=completed-controlled-private-release|unchanged
amn2_source=51fdba29ee1b33442bd109a0d0611c4d1348f4da
spain_fresh_start=local_code_and_gates_ready|no_live_action
operator_config_identity=NEOBYATNAYA.NET|recipient_label|device_label|device_passport
delivery=admin_only|secret_safe_handoff|stable_request_replay
manifest=idempotent|normalized_duplicates_fail_before_mutation
ssh_trust=dedicated_ed25519|private_binding|independent_host_pin|required_before_preflight
readonly_gate=runner_sha_4000D3B21549EBF96C773DF476492A1C9D741D27DBAF73D5DB7008DD1F6513CF|remote_sha_5485260DF91713B742E45793C079F6A18BC1B83D54AF72556EB8E6A3CC0AB345|not_run
tests=amn2_scoped_210|amn2_full_1003_passed_1_skipped|amn3_scoped_21|amn3_full_184
security=amn2_20_of_20_findings_0|amn3_2_of_2_findings_0
spain_unrelated_service=must_preserve|fingerprint_before_after
usa_server=retained_untouched
production_awg=untouched
next=LOCAL_DEDICATED_SPAIN_SSH_ONBOARDING_THEN_SEPARATE_EXACT_READ_ONLY_PREFLIGHT
```

Не принимать Spain host key автоматически и не передавать пароль в чат,
командную строку, Git или evidence. До готовности private trust state запрещены
SSH preflight, установка, service mutation и перенос. Read-only preflight после
отдельного exact approval только инвентаризирует ОС, capacity, порты, Docker,
systemd, firewall, SSH policy и fingerprint постороннего сервиса. AWG не
останавливать и не изменять. Старые Phase 10/11 approvals не переиспользовать.

## Final closeout override 2026-07-18

```text
active_phase=Phase 11 Controlled Launch and Operations
phase_status=completed-controlled-private-release
release_gate=PHASE11_RELEASE_001|pass_after_this_commit_origin_readback
closeout_packet=docs/AMN2_PHASE_11_FINAL_CLOSEOUT_PACKET.ru.md
amn2_source=0b858c5cdbc5b565cc265966a2edfe2d339d65e0|clean|origin_sync
production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0|verified
telegram_002b=activation_and_66m13s_stability_pass|run_20260717T192602Z
bot=active_enabled_single_instance_restart_0_watchdog_healthy
telegram=identity_match_webhook_empty_backlog_0
web=active_enabled_http_ok_loopback_only
database=integrity_ok|fk_0|only_expected_first_admin_row_delta
awg=unchanged|running|restart_0|peer_set_unchanged
private_operator_only=true
public_write_config_peer_self_service=false
old_fallback=sealed_review_by_2026_08_01|not_release_blocker_while_sealed
second_vps=read_only_audit_only_before_user_repurpose|not_release_blocker_now
repeat_live_actions=prohibited_not_required
next=REVIEW_POST_RELEASE_DEVICE_001_READ_ONLY_OPERATOR_UX_SCOPE
```

Canonical release declaration is valid only after final tests, complete
security-diff review with findings `0`, sealed-snapshot equality with index
and commit tree, push and exact origin readback. No Phase 11 approval is
reusable. Future work requires a newly selected post-release product slice.

## Current continuation override 2026-07-17 after TELEGRAM-002B 66-minute stability pass

```text
active_phase=Phase 11 Controlled Launch and Operations
production_overlay=0b858c5|verified
telegram_002b_cleanup=pass|one_stale_first_admin_start_ack_only|backlog_0
telegram_002b_run_id=20260717T192602Z
telegram_002b_activation=pass|fresh_start_accepted|wide_header_confirmation_exact
telegram_002b_bot=active_enabled_single_instance_restart_0_watchdog_healthy
telegram_002b_telegram=identity_match|webhook_empty|backlog_0
telegram_002b_database=first_admin_user_row_only|integrity_ok|fk_0
telegram_002b_web=active_enabled_http_ok_loopback_only
telegram_002b_awg=unchanged
telegram_002b_postflight=pass
telegram_002b_operator_action=none|do_not_repeat_start
telegram_002b_stability=pass|elapsed_66m13s|final_postflight_20260717T203215Z
release_blocker=PHASE11_RELEASE_001_FINAL_CLOSEOUT_AND_PRIVATE_RELEASE_READINESS_DECISION_ONLY
second_vps=handover_audit_only_when_user_repurposes|not_release_blocker
old_fallback=retain_sealed_until_review_by_2026_08_01|not_release_blocker_while_sealed
automation_restore=pending_after_final_origin_verification|backup_sha256_BD8BB6253C31D6CF26E1FFA6F5B89B640FD48DF706DFEC26BB167180BA510EA6
next=SYNC_TEST_SECURITY_COMMIT_PUSH_VERIFY_ORIGIN_RESTORE_AUTOMATION_THEN_REVIEW_PHASE11_RELEASE_001
```

No repeat `/start`, stage, accept or cleanup is authorized or required.

## Previous continuation override 2026-07-17 after exact-one cleanup engineering

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|production_unchanged
production_overlay=0b858c5|verified
telegram_002b_preflight=failed_closed|reason_pending_updates_nonzero
telegram_002b_stage=false|accept=false|enable=false|postflight=false
telegram_002b_regular_bot=inactive_disabled_process_0
telegram_002b_2fdb_authority=stage_receipt_absent|unconsumed
telegram_002b_cleanup_scope=one_exact_private_first_admin_start|inspect_twice|one_offset|no_response
telegram_002b_cleanup_design=d474ff6|approved
telegram_002b_cleanup_remote_sha256=41F69F945F74647B441173B682277E0568DA81CC7F0B12EADD9BD534DB225242
telegram_002b_cleanup_runner_sha256=D3BD76119B35155AAB922E54C2E59F50B7D9D0B23C9B5AC2268887D8ADB70A1F
telegram_002b_cleanup_tests=focused_10_passed|canonical_128_passed|bash_n_pass|powershell_parse_pass|diff_check_pass
telegram_002b_cleanup_security=sealed_scan_59e7862ce73ab46179a01591f4533c8496f3b38d_20260717T183406Z|receipts_5_of_5|coverage_complete|findings_0|secret_matches_0
telegram_002b_cleanup_live=not_run|approval_not_consumed
web_database_awg=unchanged_from_failed_preflight_baseline
operator_instruction=DO_NOT_SEND_START_UNTIL_FRESH_STAGE_AWAITING_ADMIN_START
next=COMMIT_PUSH_ORIGIN_READBACK_THEN_ISSUE_EXACT_CLEANUP_LIVE_APPROVAL
```

После exact cleanup approval: `preflight -> cleanup -> independent backlog/
web/DB/AWG postflight -> existing 2FDB preflight/stage`. Только новый successful
stage может открыть свежий 240-second window и запросить `/start`.

## Current continuation override 2026-07-17 after `0b858c5` rollout pass

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|production_applied
production_overlay=0b858c5|verified
rollout_0b858c5=pass|run_20260717T081340Z|approval_consumed
rollout_0b858c5_package=sha256_7866bdd9febe1d6eea701b37a6e4206a8267766a56993f3c02a0c7b30c394b54|upload_exact_two_files|mode_0600
rollout_0b858c5_assets=canonical_square_verified|wide_language_header_verified|telegram_profile_unchanged
rollout_0b858c5_web=active_enabled_http_ok_loopback_only
rollout_0b858c5_bot=inactive_disabled_process_0|unit_env_unchanged|activation_false
rollout_0b858c5_db=integrity_ok|fk_0|tables_15|rows_88|file_logical_counts_hashes_unchanged
rollout_0b858c5_awg=running|restart_0|peers_12|container_and_peer_set_unchanged|mutation_false
rollout_0b858c5_rollback=retained_verified|not_needed
rollout_0b858c5_postflight=independent_pass
rollout_0b858c5_evidence=research/amn2/phase-11-0b858c5-combined-overlay-rollout-2026-07-17.md
second_vps=not_used|user_hold_through_weekend_then_repurpose
next=REVIEW_PHASE11_TELEGRAM_002B_PERSISTENT_BOT_ACTIVATION_GATE_WITHOUT_ACTIVATION
```

## Current continuation override 2026-07-17 after trusted transport hardening

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|local_fix_pending_origin_sync
production_overlay=801f8c3|unchanged
remote_executor_sha256=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72|unchanged
ssh_runner_sha256=654154AFF81425DE610817C9FF05FB2D976B2EA3A7843C9FC8F566269C94A6BE
trusted_transport=%WINDIR%/System32/OpenSSH|ssh_and_scp_absolute|helper_fail_closed
postfix_security=bare_calls_0|trusted_calls_3|coverage_pass
postfix_tests=focused_9_passed|canonical_95_passed|powershell_parse_pass|bash_n_pass|diff_check_pass
combined_package_live=upload_false|apply_false|regular_bot_inactive_disabled|telegram_profile_unchanged|web_db_unchanged|awg_untouched
approval_gate=PREPARED_NOT_CONSUMED|exact_remote_sha_and_trusted_transport_bound
approval_phrase=APPROVE_PHASE11_0B858C5_REMOTE_ORCHESTRATOR_SHA_A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72_TRUSTED_OPENSSH_ABSOLUTE_PATH_BOUND_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
next=WAIT_FOR_EXACT_APPROVAL_THEN_REVIEW_BOUNDED_LIVE_GATE_WITH_AWG_UNTOUCHED
```

## Current continuation override 2026-07-16 after combined package verification

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
production_overlay=801f8c3|unchanged
combined_package=prepared_verified_pushed|not_uploaded_not_applied
combined_package_outer=dist/amn2-combined-overlay-0b858c5.zip|bytes_9220155|sha256_7866bdd9febe1d6eea701b37a6e4206a8267766a56993f3c02a0c7b30c394b54|entries_4
combined_package_source=source_0b858c5|sha256_e03f13fd6a7bb5cbc5fcee7179f395ea8c2864ebceab01bc351c5904f3cff975|entries_383|delta_31|schema_none
combined_package_scope=canonical_square_logo|wide_language_header|telegram_002a_hardening|bot_activation_excluded
combined_package_tests=helper_markdown_5_passed|full_source_918_passed_1_skipped|bash_zip_hash_content_bindings_passed
combined_package_security=receipts_7_of_7|surfaces_5|findings_0|coverage_complete|snapshot_1b94685eea2da582efd72341869fccae1738d1a6ace588c612803f39fbafcc4e
combined_package_live=upload_false|apply_false|regular_bot_inactive_disabled|telegram_profile_unchanged|web_db_unchanged|awg_untouched
combined_package_gate=docs/AMN2_PHASE_11_0B858C5_COMBINED_OVERLAY_GATE.ru.md
recovery_001=retain_old_fallback_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_handover=final_read_only_audit_then_separately_approved_dedicated_staging_key_known_host_cleanup_only
next=REVIEW_0B858C5_COMBINED_PRIVATE_OVERLAY_LIVE_GATE_THEN_REQUIRE_EXACT_APPROVAL
```

## Current continuation override 2026-07-16 after wide language-selection header

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|0b858c5cdbc5b565cc265966a2edfe2d339d65e0|origin_sync|clean
production_overlay=801f8c3|unchanged
brand_001=square_canonical_logo_preserved|sha256_40acd9465dc9fda06644d2d829da996e1d9bf6c856e95298b624b31154fec791|not_deployed
brand_002=wide_language_selection_header_complete|commit_0b858c5|not_deployed
brand_002_asset=app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png|png_1672x941|bytes_2647131|sha256_bbddfa72d1d1fc37e412d2f4a9b4124001ff91fbd641635e31a47e008fc4611f
brand_002_scope=start_language_selector_only|square_assets_preserved|text_only_missing_asset_fallback
brand_002_tests=asset_green_3|handler_asset_green_47|scoped_61_passed|full_918_passed_1_skipped|compile_and_exact_wheel_asset_passed
brand_002_security=clean_diff_scan_complete|receipts_3_of_3|surfaces_4|findings_0|coverage_complete
brand_002_live=regular_bot_inactive_disabled|telegram_api_false|profile_unchanged|vps_false|provider_false|web_db_false|awg_untouched
telegram_002a=local_implementation_complete|contained_in_source_0b858c5|production_not_activated
recovery_001=retain_old_fallback_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_handover=final_read_only_audit_then_separately_approved_dedicated_staging_key_known_host_cleanup_only
next=PREPARE_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_VERIFY_ROLLBACK_GATE
```

## Current continuation override 2026-07-16 after TELEGRAM-002A local hardening

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|08c56f2beff65145380fdb3736d94c0709a2b33a|origin_sync|clean
production_overlay=801f8c3|unchanged
telegram_002a=local_implementation_complete|production_not_activated
telegram_002a_controls=fail_closed_admission_and_recheck|single_instance|allowed_updates|tasks_limit_8|overall_startup_max_120|systemd_start_135_watchdog_60
telegram_002a_tests=scoped_113_passed|full_915_passed_1_skipped|toolchain_compile_diff_passed
telegram_002a_security=clean_complete|receipts_15_of_15|findings_0|snapshot_da0f5ec50e574c749029210fe783b5dbc3a0ee97749b13ad44a8a83ddcc15105
telegram_002a_live=regular_bot_inactive_disabled|telegram_api_false|vps_false|web_db_false|awg_untouched
brand_001=contained_in_descendant_08c56f2|old_6abc620_package_not_current_combined_candidate|not_deployed
recovery_001=retain_old_fallback_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_handover=final_read_only_audit_then_separately_approved_dedicated_staging_key_known_host_cleanup_only
next=PREPARE_08C56F2_COMBINED_LOGO_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_PACKAGE_VERIFY_ROLLBACK_GATE
```

## Previous continuation override 2026-07-15 after fallback/VPS/logo package decision

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3|unchanged
recovery_001=retain_old_fallback_sealed_without_deletion|review_by_2026-08-01
second_vps=clean_ssh_only|amn2_no_longer_needed|user_hold_through_weekend_then_repurpose
second_vps_billing=paid_until_2026-08-12_23_18_25|590_rub_month|auto_renew_enabled_observed|no_mutation
second_vps_handover=final_read_only_audit_then_exact_local_staging_key_and_known_host_cleanup_only
brand_001=package_ready_6abc620|sha256_2683420dd7a705c96490dc1878d14d208986209bf8eb1b6e1b066d31b17932f5|not_deployed
brand_001_security=coverage_7_of_7|findings_0|snapshot_36d08ba1945558ee590e3c8d1057eeb37ad634141ae432cb070355ab242f38fb
brand_001_live=regular_bot_inactive_disabled|telegram_profile_unchanged|awg_untouched
telegram_002a=local_design_gate_next|implementation_not_started
next=REVIEW_AND_APPROVE_TELEGRAM_002A_FAIL_CLOSED_DESIGN_THEN_TDD_IMPLEMENTATION
```

## Previous continuation override 2026-07-15 after RESTORE-001A pass

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3
restore_001a=completed_pass|source_pin_801f8c3
restore_001a_approval=received|consumed
restore_001a_static=critical_contracts_passed|image_layers_6|compressed_6
restore_001a_awg=isolated_pass|restart_0|peers_12|full_config_peer_fidelity|default_route_false|host_ports_false
restore_001a_web_db=loopback_login_200_outbound_denied|integrity_and_counts_schema_file_hash_unchanged
restore_001a_cleanup=passed|second_vps_clean_ssh_only
restore_001a_production=unchanged|runtime_ops_pass|awg_running_restart_0_peers_12_same_set
restore_001a_evidence=research/amn2/phase-11-restore-001a-trusted-disposable-full-secret-rehearsal-2026-07-15.md
brand_001=local_source_complete|6abc620_pushed|production_not_deployed|profile_icon_not_applied
telegram_002=hold_disabled_go_local_hardening
recovery_001=retirement_decision_unblocked|destructive_delete_separate_gate
second_vps=restore_role_complete|safe_retirement_recommended|provider_delete_separate_gate
next=DECIDE_OLD_FALLBACK_AND_SECOND_VPS_SAFE_RETIREMENT_GATES_THEN_PREPARE_LOGO_ROLLOUT_AND_IMPLEMENT_TELEGRAM_002A
```

## Previous continuation override 2026-07-15

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3
restore_001a_source_pin=801f8c3|approval_scope_unchanged
restore_001a_gate=attempt_3_fail_closed|json_null_repotags_fix_verified|security_docs_commit_push_then_retry
restore_001a_approval=received|not_consumed
restore_001a_attempt_3=repo_tag_contract_invalid_before_ciphertext|cleanup_passed|reaudits_passed
restore_001a_diagnosis=repotags_key_present_json_null|config_and_6_oci_layers_canonical_self_bound|cleanup_passed
restore_001a_null_tag_fix=require_key|allow_null_empty_exact_canonical_singleton|missing_malformed_foreign_additional_duplicate_rejected
restore_001a_null_tag_tests=red_3_failed_expected|green_8_passed|recovery_50_passed|root_79_passed|compile_diff_passed
restore_001a_null_tag_security=independent_review|critical_0|important_0|minor_0|ready_yes
restore_001a_live_effect=bundle_false|secret_transfer_false|staging_mutation_false|awg_untouched|telegram_api_false
brand_001=local_source_complete|6abc620_pushed|production_not_deployed|profile_icon_not_applied
telegram_002=hold_disabled_go_local_hardening
recovery_001=retain_old_fallback_until_restore_001a
second_vps=clean_ssh_only|keep_temporarily_for_restore_001a|independent_dr_false
next=DOCS_COMMIT_PUSH_JSON_NULL_REPOTAGS_FIX_THEN_RETRY_APPROVED_RESTORE_001A
```

## Previous continuation override 2026-07-15

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3
restore_001a_source_pin=801f8c3|approval_scope_unchanged
restore_001a_gate=attempt_2_fail_closed|canonical_repotag_fix_verified|security_docs_commit_push_then_retry
restore_001a_approval=received|not_consumed
restore_001a_attempt_2=canonical_single_repo_tag_rejected_before_ciphertext|cleanup_passed|reaudits_passed
restore_001a_repo_tag_fix=empty_or_exact_singleton_expected_reference_only|foreign_additional_duplicate_rejected
restore_001a_repo_tag_tests=red_3_failed_expected|green_6_passed|recovery_48_passed|root_77_passed|compile_diff_passed
restore_001a_repo_tag_security=independent_review|critical_0|important_0|minor_0|ready_yes
restore_001a_live_effect=bundle_false|secret_transfer_false|staging_mutation_false|awg_untouched|telegram_api_false
brand_001=local_source_complete|6abc620_pushed|production_not_deployed|profile_icon_not_applied
telegram_002=hold_disabled_go_local_hardening
recovery_001=retain_old_fallback_until_restore_001a
second_vps=clean_ssh_only|keep_temporarily_for_restore_001a|independent_dr_false
next=DOCS_COMMIT_PUSH_CANONICAL_REPOTAG_FIX_THEN_RETRY_APPROVED_RESTORE_001A
```

## Previous continuation override 2026-07-15

```text
active_phase=Phase 11 Controlled Launch and Operations
amn2_source=codex-vps-test-prep|6abc620|origin_sync
production_overlay=801f8c3
restore_001a_source_pin=801f8c3|approval_scope_unchanged
restore_001a_gate=attempt_1_fail_closed|oci_config_path_fix_verified|commit_push_then_retry
restore_001a_approval=received|not_consumed
restore_001a_format=runtime_complete_v2|required_external_source_digest
restore_001a_security_blocker=P11_LEGACY_IMAGE_CONFIG_UNBOUND_001|fixed
restore_001a_security=complete_coverage|full_file_receipts_6_of_6|findings_0|snapshot_d56c7864892bdf6f024b1e701b93577a286f1f7d467d50fde2882437757ae12c
restore_001a_tests=runtime_15_passed|recovery_scoped_41_passed|root_70_passed|independent_verifier_35_passed
restore_001a_attempt_1=image_archive_config_digest_invalid|ciphertext_false|cleanup_passed|reaudits_passed
restore_001a_diagnosis=oci_blob_config_and_6_layers|safe|canonical_equal|cleanup_passed
restore_001a_fix=exact_legacy_or_oci_config_path|red_3|green_3|recovery_44|root_73
restore_001a_fix_security=complete_coverage|surfaces_4|sealed_9|findings_0|snapshot_b051261c4bf7061c72ffcd31b1f04d9da3b77bc3de4e54dfbbd325055dc69cc2
brand_001=local_source_complete|6abc620_pushed|production_not_deployed|profile_icon_not_applied
brand_001_tests=red_3_failed_expected|focused_58_passed|full_872_passed_1_skipped|security_findings_0
telegram_001=completed_pass
telegram_002=hold_disabled_go_local_hardening
ops_001=completed_healthy
recovery_001=retain_old_fallback_until_restore_001a
second_vps=clean_ssh_only|keep_temporarily_for_restore_001a|independent_dr_false
next=COMMIT_PUSH_OCI_CONFIG_PATH_FIX_THEN_RETRY_APPROVED_RESTORE_001A
```

Актуальный план по критичности:
`docs/AMN2_PHASE_11_CURRENT_PRIORITY_PLAN.ru.md`. Нижележащий original handoff
с `3c91601` сохранён как entry history и не должен переопределять этот блок.

Начать сообщением:

```text
AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_START
```

Copy-ready полный текст первого сообщения:
`docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md`.

## Сначала прочитать

- `docs/PROJECT_STATUS_CURRENT.ru.md` — первый control block;
- `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`;
- `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`;
- `docs/AMN2_PHASE_11_FIRST_MESSAGE.ru.md`;
- этот handoff;
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md` — только верхние overrides;
- `research/amn2/phase-10-3c91601-existing-client-post-deploy-acceptance-2026-07-14.md`;
- `research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md`;
- `research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md`.

## Current baseline

```text
active_phase=Phase 11 Controlled Launch and Operations
phase10_status=closed
amn2_branch=codex-vps-test-prep
amn2_head=3c91601
production_overlay=3c91601
web=active_enabled_http_200_loopback_only
awg=running_restart_count_0|12_peers
bot=inactive_disabled
api_3040_listener=0
write_gates=false_false
client_acceptance=passed_fresh_handshake_and_traffic
```

Phase 10 deployed Device Passport, Enrollment Ticket schema/contracts,
lifecycle, read-only drift/web diagnostics, cascade revoke, plan quota,
integration registry and Telegram read-only callbacks. New lifecycle tables are
empty until real product flows use them. Public enrollment, public API,
persistent bot runtime and live remediation are not open.

## First concrete gate

```text
GPT-5.6 SOL -> REVIEW_PHASE11_3C91601_PRIVATE_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_GATE
```

Review existing implementation/evidence first:

- `research/amn2/phase-10-private-telegram-controlled-polling-ttl-gate-review-2026-07-11.md`;
- `research/amn2/phase-10-telegram-single-admin-transient-smoke-runner-hardening-2026-07-11.md`;
- current `3c91601` bot/runtime code and tests;
- production baseline: regular bot unit inactive/disabled.

Do not start polling during review. If review passes, prepare a separate exact
live phrase for one configured-admin, message-only, internally TTL-bounded run
with safe backlog and rollback. Persistent activation is a later gate.

## Planned work map

### Now

- private Telegram single-admin transient smoke and later persistent-runtime
  decision;
- production runtime/recovery observation without stopping AWG;
- retirement decision for the old recovery bundle/key.

### Next

- Device Passport/lifecycle read-only operator UX;
- scoped private API-key integration operations;
- one-config-per-device/quota/owner-shared consistency;
- self-service Enrollment route only if explicitly required.

### Post-launch

- drift history/retention;
- gated reconciliation apply through OperationPlan;
- dynamic subnet source-of-truth/IPAM and then multi-VPS fleet work;
- restore apply single-flight/idempotency;
- published-release-triggered client reacceptance.

### Design-later

- web-admin 2FA;
- domain-zone exclusion policy;
- separate support/news bots;
- privacy-safe metrics expansion;
- OpenAPI grouping, DESIGN.md, naming and Russian-first docs polish.

Authoritative IDs, dependencies and exclusions are in
`docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`. Historical
`ideas/*` and `transfer-backlog.md` are inputs only; deduplicate before work.

## Safety reset

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Phase 10 approvals are consumed. Never print configs, QR, import payloads,
private keys, PSK, tokens, passwords or raw sensitive logs. Production VPN must
remain running; any separately approved service change must restore and verify
the prior baseline and notify the operator.

## Automation

The ACTIVE `amn2-upstream-orchestrator` resolves phase dynamically from the
first project control block. Legacy three-step weekly chain is PAUSED. After
the separate Phase 11 task exists, retarget the active heartbeat to that task
or retain its explicit dynamic-retarget behavior; it must not continue the
Phase 10 plan.

## Work style

Engineering/product evidence first, tests second, diff review third, status
sync fourth, commit/push last. Report commands as `Одиночная`, `Двойная`,
`Тройная`, `Четверная` and `Более — рекомендовано`, always beginning with
`GPT-5.6 SOL`.

## Handoff override — TELEGRAM-002B local gate complete 2026-07-17

```text
phase11_telegram_002b_status=READY_AWAITING_SEPARATE_EXACT_LIVE_APPROVAL
phase11_telegram_002b_remote_sha256=14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64
phase11_telegram_002b_tests=focused_18_passed|canonical_113_passed|bash_n_pass|powershell_parse_pass
phase11_telegram_002b_security=complete_coverage|reportable_findings_0
phase11_telegram_002b_live_action=false|regular_bot_inactive_disabled|telegram_profile_unchanged|awg_untouched
phase11_telegram_002b_evidence=research/amn2/phase-11-telegram-002b-staged-persistent-activation-gate-2026-07-17.md
phase11_telegram_002b_next=WAIT_FOR_SEPARATE_EXACT_LIVE_APPROVAL_THEN_REVIEW_BOUNDED_GATE
```

Prepared phrase (do not consume in this local task):

```text
APPROVE_PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_14747241F1A0E0545CF8B96329E90708F7CC80AF639872968DA03A1783200C64_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

## Correction override — preflight venv symlink binding

Первый preflight остановлен fail-closed на `/opt/amn2/venv/bin/python`, который
является symlink на executable target. Никаких stage/accept/bot/AWG действий не
было. После локального correction slice новая SHA-bound phrase будет:

```text
APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_3E6D42D6D7184BD7A05402585A85652C2319D1E0E9E8076217057AE5EE948881_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED
```

## Correction override — delayed sanitized journal receipt

SHA `3E6D42...` preflight прошёл, но disabled-first stage
`20260717T115918Z` остановился fail-closed до `/start`, потому что единичный
journal read опередил receipt ingest. Поздняя read-only проверка нашла exact
markers `1/1/1`, errors `0`; rollback и повторный preflight подтверждены.
Бот inactive/disabled, stale timer остановлен, AWG unchanged.

Локальный executor исправлен: bounded sanitized receipt retry максимум 15
секунд, exact run-id timer cleanup и обязательный nonzero exit после signal
rollback. Новый remote SHA:
`FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F`.
Post-fix focused `21 passed`, canonical `116 passed`, syntax pass; TERM
PoC exits `143` without resumed privileged mutation. Security rescan
completed `9/9` rows, closed both former candidates and produced
`0 reportable findings`.
Точная SHA-bound phrase до origin sync намеренно не публикуется:

```text
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

## Correction override — exact single-line admission receipt

FA3F fresh preflight прошёл. Disabled-first stage fail-closed остановился до
`/start`: producer `0b858c5` выводит admission/identity/webhook/backlog/
allowed-updates одной строкой, тогда как verifier после фильтрации требовал
backlog и allowed-updates в начале отдельных строк. Все 15 retry были
структурно неспособны пройти.

Independent postfailure preflight подтвердил rollback: bot
inactive/disabled/process 0, web healthy, DB `15/88` и прежний counts hash,
Telegram backlog 0, AWG running/restart 0/peers 12 и прежние hashes.

TDD fix принимает ровно одну полную каноническую fixed-string строку. Новый
remote SHA
`56BE81549B86B5DBF09AA23A8513E652F6AF344E88C131FC8EAA2D5D5403F2CE`,
runner SHA
`04DF10C9305CFA46843981A851A07B98B658A92859135A8180BCE15363F39951`.
Focused `21`, canonical `116`, syntax/diff checks PASS; Security diff
coverage `3/3`, findings `0`.

```text
phase11_telegram_002b_status=CORRECTED_AWAITING_COMMIT_PUSH_ORIGIN_READBACK
phase11_telegram_002b_fa3f_authority=consumed_and_invalidated
phase11_telegram_002b_new_approval=required
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

Следующий обязательный шаг: commit/push/readback correction slice, затем
выдать новую literal SHA-bound phrase и повторить полный bounded gate. Старые
1474/3E6D/FA3F phrases недействительны.

## Correction override — unbuffered persistent receipt

SHA `56BE8154...` literal approval была получена. Fresh preflight прошёл;
disabled-first stage снова fail-closed завершился до `/start`, accept/enable/
postflight не выполнялись. Независимый post-failure preflight подтвердил:
bot inactive/disabled/process 0, web/DB/Telegram baseline unchanged, AWG
running/restart 0/peers 12 и прежние hashes.

Exact `0b858c5` producer печатает receipt через default `print`, а production
unit не задаёт Python unbuffered mode. Correct line оставалась в stdout buffer
на время persistent polling. Исправление добавляет `PYTHONUNBUFFERED=1` в
атомарный snapshot/rollback-protected `.env` contract.

```text
phase11_telegram_002b_status=CORRECTED_UNBUFFERED_AWAITING_COMMIT_PUSH_ORIGIN_READBACK
phase11_telegram_002b_56be_authority=consumed_and_invalidated
phase11_telegram_002b_new_remote_sha256=E407421F358703C4D6FE1825EE46EFBC4E72C3840FEBAC89F131800F30DB412F
phase11_telegram_002b_new_runner_sha256=20944C777A5EAB534964577C8BD3F9B71C9ADAE8310E3C93F56EB70BE0EE86B5
phase11_telegram_002b_tests=focused_22_passed|canonical_117_passed|bash_n_pass|powershell_parse_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0|secret_patterns_0
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

Next: commit/push/readback, issue a new exact E407-bound literal approval,
then fresh preflight and one disabled-first stage. `/start` только после
`awaiting_admin_start=true`.

## Correction override — exact default-plan timestamp startup delta

E407 fresh preflight passed and the unbuffered admission receipt gate passed.
Stage then stopped fail-closed before `/start` because workflow bootstrap
updated an existing application row. Post-failure preflight proved bot
inactive/disabled, counts unchanged, Telegram backlog 0 and AWG unchanged.

Static evidence from exact `0b858c5` binds the delta to
`seed_default_plans -> upsert_plan -> updated_at=CURRENT_TIMESTAMP`. No blind
DB restore was run. The corrected gate hashes all rows after removing only
`plans.updated_at`, separately requires exact counts and unchanged first-admin
row, and freezes a post-start baseline before operator interaction.

```text
phase11_telegram_002b_status=CORRECTED_PLAN_TIMESTAMP_GATE_AWAITING_COMMIT_PUSH_ORIGIN_READBACK
phase11_telegram_002b_e407_receipt=pass|unbuffered_fix_effective
phase11_telegram_002b_e407_stage=fail_closed_before_operator_start|plan_timestamp_metadata_only
phase11_telegram_002b_e407_authority=consumed_and_invalidated
phase11_telegram_002b_new_remote_sha256=DF9E0BAD6359AD7F3100A7FBED5ED1223721C656086D0CADA72CA492BD10B396
phase11_telegram_002b_new_runner_sha256=16E6F846DEB3DC52838224E277D65AA2D0059D6288C827248607A7F6E5943CED
phase11_telegram_002b_tests=focused_23_passed|canonical_118_passed|bash_n_pass|powershell_parse_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0|secret_patterns_0
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_regular_bot=inactive_disabled|process_0
phase11_telegram_002b_awg=running|restart_0|peers_12|hashes_unchanged
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

Next: commit/push/readback, issue exact DF9E approval, fresh preflight/stage,
then request `/start` only after the stage explicitly passes.

## Correction override — expired stage window and safe admission category

DF9E run `20260717T150504Z` reached `awaiting_admin_start=true`; operator
interaction did not occur before the 240-second expiry. Automatic rollback
restored bot inactive/disabled. Two later preflights failed only inside the
sanitized Telegram probe while DB/AWG remained safe.

```text
phase11_telegram_002b_status=AWAITING_CLASSIFIED_PREFLIGHT_AFTER_EXPIRED_OPERATOR_WINDOW
phase11_telegram_002b_df9e_stage=pass|window_expired|rollback_pass
phase11_telegram_002b_operator_start=false|accept=false|enable=false|postflight=false
phase11_telegram_002b_repeat_preflight=failed_twice|category_hidden_by_old_runner
phase11_telegram_002b_classifier=fixed_allowlist|no_secret_or_update_content|no_acknowledgement
phase11_telegram_002b_new_remote_sha256=2FDBAD445F4EBDA4A94BE84CB4FF43D05AE458D68A78686490775B8F242A00E2
phase11_telegram_002b_new_runner_sha256=75B210410CFE45377857A02FAA43618EE26533259B15AB348693B5292091ED53
phase11_telegram_002b_tests=focused_23_passed|canonical_118_passed|syntax_pass|diff_check_pass
phase11_telegram_002b_security=complete_3_of_3|reportable_findings_0
approval_phrase=WITHHELD_UNTIL_TEST_SECURITY_COMMIT_PUSH_AND_ORIGIN_SYNC
```

Next: commit/push/readback, exact 2FDB approval and classified preflight. A
pending-update result requires a separate bounded cleanup approval.
