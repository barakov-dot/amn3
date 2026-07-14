# Следующий чат: AMN2 Phase 10 Product Recovery With Harness

## 3c91601 private VPS rollout completed 2026-07-14

Private package применён: production overlay теперь `3c91601`. Первый attempt
безопасно откатился до production migration из-за слишком широкого локального
evidence scan; второй run прошёл snapshot, clone migration/API smoke, exact
production migration и web activation. AWG не останавливался и не
перезапускался.

```text
rollout_status=completed_pass_with_verified_automatic_rollback
successful_run=20260714T101632Z
schema=3_new_tables|5_new_indexes|new_rows_zero|existing_rows_unchanged
production_api_smoke=false
web=active_enabled_http_200|downtime_55s
awg=running_restart_0|12_peers|peer_set_unchanged
bot=inactive_disabled
rollback=verified|/root/amn2-rollbacks/3c91601-20260714T101632Z
traffic=5s_zero_delta|latest_handshake_2026-07-13T21:44:30Z
next_command=GPT-5.6_SOL -> REVIEW_PHASE10_3C91601_POST_DEPLOY_ACCEPTANCE_AND_CLOSEOUT_READINESS
evidence=research/amn2/phase-10-3c91601-private-vps-rollout-2026-07-14.md
```

## 3c91601 exact rollout scope consumed 2026-07-14

Exact gate review завершён без обращения к VPS. Разрешённый после отдельной
точной фразы порядок: checksum-bound upload, tracked-source и SQLite snapshot,
миграция и API smoke только на clone DB, отдельный production schema checkpoint,
затем активация web с автоматическим rollback. Production API smoke запрещён.

```text
scope_status=approved_consumed_completed_pass
schema_delta=3_new_tables|5_new_indexes|new_rows_zero|existing_rows_unchanged
runtime_invariant=amnezia_awg2_never_stop_or_restart|web_only_brief_stop|bot_inactive_disabled
clone_only_writes=server_sync|temporary_api_tokens|read_audit
scope_tests=harness_passed|scoped_20_passed|root_43_passed|diff_check_passed
live_effect=source_applied|schema_migrated|web_active|awg_unchanged
exact_phrase=APPROVE PHASE10_3C91601_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_SNAPSHOT_CLONE_DB_MIGRATION_AND_WEB_ACTIVATION_WITH_ROLLBACK
evidence=research/amn2/phase-10-3c91601-private-vps-rollout-gate-review-2026-07-14.md
```

## 3c91601 private VPS package override 2026-07-14

Authoritative AMN2 source `3c91601` совпадает с origin. Private package собран
через `git archive`, проверен по exact entries/checksums/bindings/secret
boundaries, протестирован из extracted payload и теперь применён на VPS.

```text
package=dist/amn2-vps-update-and-smoke-kit-3c91601.zip
package_sha256=12E90EB54FCC374C84B6AA987C65E5644C4BD1B974089E81E16D00780389FB6E
source_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
tests=focused_237_passed_1_warning|full_870_passed_1_skipped_1_warning|tooling_23_passed|root_43_passed
review=passed|required_missing_0|forbidden_0|deleted_paths_0|secret_literal_files_0
harness=passed|all_stop_lines_false
live_upload=completed
live_apply=completed_verified
scope_record=completed_consumed
next_command=REVIEW_PHASE10_3C91601_POST_DEPLOY_ACCEPTANCE_AND_CLOSEOUT_READINESS
evidence=research/amn2/phase-10-3c91601-vps-package-prep-2026-07-14.md
```

Gate завершён через source/SQLite snapshots и clone DB. API loopback smoke
писал временные token/audit rows только в clone; production DB smoke, cascade
revoke и любые peer/config действия не выполнялись.

## Canonical hybrid recovery replacement override 2026-07-14

Остаточный DR-срез закрыт. Canonical writer исправляет newline metadata defect,
а live backup CLI больше не принимает symmetric key через stdin. Replacement
bundle зашифрован public-key hybrid envelope, локально проверен без записи
production plaintext, скопирован на `F:` без private key и прошёл sanitized
staging rehearsal. Production VPN и web во время работы не останавливались.

```text
run_id=20260714T045754Z
code_commits=dd87ea7|117b72c
artifact_sha256=2c618fa52aed038eb494a892480970795c554bddd6649156e1fe5a9c00e52280
encryption=rsa_oaep_sha256_wrapped_fernet
metadata_verification=passed|warnings_none
local_verification=passed|production_plaintext_written_false
second_copy=F:\AMN2-Recovery\20260714T045754Z|sha256_verified|private_key_not_copied
sanitized_staging=passed|sha256_d7845bdbd8623476bcfb81d6a602cfe8604aebd571a0ae38cc1c49bb36eab1d9|start_guard_64|ssh_only_after_cleanup
production_runtime=amnezia_awg2_running_restart_count_0|web_active_enabled|no_service_stop_or_restart
tests=focused_20_passed|root_43_passed|compile_passed|diff_review_passed
previous_copy=retained_as_fallback_pending_operator_retirement
next_dr_gate=full_secret_restore_apply_in_trusted_disposable_environment_only
launch_plan_change=false
evidence=research/amn2/phase-10-canonical-hybrid-recovery-replacement-2026-07-14.md
```

## Isolated restore rehearsal override 2026-07-13

Encrypted production bundle проверен локально без записи plaintext. На
изолированный staging передан только exact-allowlisted schema-only sanitized
fixture: DB содержит 12 tables и 0 rows, AWG material redacted, services
заблокированы. Verifier, systemd syntax и start guard прошли; remote tree
удалён, runtime не устанавливался, production VPS не использовался.

```text
run_id=20260713T215439Z
verifier_commit=f1ec6ca
local_verification=passed_with_warning
sanitized_staging_verification=passed
sanitized_sha256=ff10c841946c8fa5725ef974360bb987dad942e8353ac5fae09ab80e0dd1ae59
tests=focused_11_passed|root_34_passed|compile_passed|diff_review_passed
production_key_uploaded=false
production_plaintext_uploaded=false
production_vps_touched=false
staging_runtime_installed=false
staging_cleanup=passed|ssh_only_external_listener
metadata_writer_defect=missing_newline_source_overlay_container_name
next_dr_step=fix_metadata_writer_then_generate_and_verify_replacement_bundle
launch_plan_change=false
evidence=research/amn2/phase-10-isolated-restore-rehearsal-2026-07-13.md
```

## External full recovery backup override 2026-07-13

После provider incident создана первая полная внешняя recovery-копия. Она
включает консистентную SQLite DB, AMN2 runtime env/config, AWG persistent config
и server keys, container start file и systemd units. Bundle зашифрован до
скачивания, локально расшифрован только в памяти и проверен по manifest SHA-256,
SQLite integrity и recovery contracts. Recovery key хранится отдельно от
bundle, ограничен ACL текущего пользователя и не попадает в Git.
Вторая encrypted copy записана на отдельный removable media `F:`, проверена по
тому же SHA-256; recovery key на носитель не копировался.

```text
artifact=backups/amn2-recovery/amn2-recovery-20260713T153359Z.tar.gz.enc
sha256=3e2339fdbe7e78bcdd1ab90510e204acdffba0b09df5c4ae05dae64293136cb8
vpn_runtime_mutation=false
remote_temp_artifacts_removed=true
second_independent_copy=completed|F:\AMN2-Recovery\20260713T153359Z|sha256_verified|key_not_copied
restore_rehearsal=completed_safe_split_local_production_and_sanitized_staging
evidence=research/amn2/phase-10-external-full-recovery-backup-2026-07-13.md
```

## VPS recovery override 2026-07-13

Provider-side incident закрыт фактическим runtime evidence. SSH и ICMP
доступны; `amnezia-awg2` running с `restart_count=0`, `awg0` читается, web
active/enabled, bot корректно inactive/disabled. Оператор подключился последним
тестовым конфигом в официальном Amnezia Client. Десятисекундный агрегированный
замер показал положительную RX/TX дельту и свежий handshake. Codex не выполнял
VPS mutation при восстановлении.

```text
source_head=3c91601
vps_overlay=1c7fb78
vps_upload_pending=true_separate_gate
evidence=research/amn2/phase-10-vps-provider-recovery-and-live-traffic-2026-07-13.md
```

## Актуальный override 2026-07-12 после cascade revoke

```text
amn2_branch=codex-vps-test-prep
amn2_head=3c91601
lifecycle_commit=bdbf740
read_only_web_diagnostics_commit=956e76b
cascade_revoke_commit=3c91601
full_test_status=870_passed_1_skipped_1_warning
launch_plan_change=false
public_enrollment=false
live_drift_remediation=false
next_local_step=START_PHASE10_3C91601_VPS_PACKAGE_PREP_SLICE
evidence=research/amn2/phase-10-upstream-lifecycle-web-diagnostics-cascade-revoke-2026-07-12.md
```

VPS 2026-07-12 недоступен одновременно клиентам, по SSH/22 и ICMP. Ни
остановка, ни запуск runtime в этой работе не выполнялись. Последнее
подтвержденное состояние 2026-07-11: `amnezia-awg2` running, web active,
bot inactive/disabled. До восстановления host/provider connectivity нельзя
заявлять, что VPN runtime включен или проверен; bot не использовать для
восстановления VPN.

Дата: 2026-07-04.

## Актуальный override 2026-07-12

Исторический контекст ниже не переписывать. Текущий переносимый Phase 10
source head:

```text
amn2_branch=codex-vps-test-prep
amn2_head=e709746
status_branch=codex-spark-phase9-docs-sync
latest_product_slice=READ_ONLY_DESIRED_OBSERVED_DRIFT_DIAGNOSTICS
drift_commit=fc48a7e
device_passport_commit=a2cbcfa
enrollment_ticket_commit=e709746
full_test_status=864_passed_1_skipped_1_warning
evidence=research/amn2/phase-10-drift-device-passport-enrollment-ticket-2026-07-12.md
```

Реализовано локально:

- детерминированный read-only `ReconciliationSnapshot` с состояниями
  `aligned`, `missing_remote`, `unexpected_remote`, `stale_observation`,
  `observation_failed`, `unknown`;
- Device Passport со стабильным generated ID и без hardware fingerprint,
  posture или MDM заявлений;
- hash-only, TTL, single-use Device Enrollment Ticket с atomic claim и exact
  idempotent retry;
- raw enrollment token отсутствует в DB/log/audit/read metadata;
- drift auto-remediation, public enrollment route, VPS peer/config mutation и
  Telegram delivery не открыты.

Launch decision:

```text
read_only_drift=nearest-product-slice-after-authenticated-operator-surface-policy-binding
device_passport=local-persistence-ready-operator-view-pending
enrollment_ticket=local-service-only-public-route-disabled
enrollment_ticket_launch_blocking=false_when_self_service_not_required
drift_auto_remediation=false
next_local_step=START_PHASE10_E709746_VPS_PACKAGE_PREP_SLICE
```

VPS runtime note:

```text
last_verified_2026_07_11=overlay_1c7fb78|web_active_enabled|amnezia_awg2_running|bot_inactive_disabled
check_2026_07_12=ssh22_timeout|ping_timeout|no_runtime_change_performed
classification=management-transport-unreachable-runtime-not-reverified
runtime_restore_rule=after_any_test_stop_restore_original_runtime_verify_and_notify_operator
```

`amneziya-bot` не включать как способ восстановления VPN: он намеренно
inactive/disabled до отдельного polling gate. Уже выданные конфиги обслуживает
`amnezia-awg2`. При доступном SSH сначала read-only проверить container/web;
только реально остановленный production runtime возвращать в исходное
состояние и обязательно сообщать оператору результат.

## Команда для старта

```text
AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_START

Источник правды: repo/docs + current git workspace.
Не использовать старую broken Phase 9 thread history.

Цель: выйти из docs-only/hold цикла и продолжить product-work через harness.

Обязательный harness:
- scripts/phase9_progress_harness.py
- tests/test_phase9_progress_harness.py

Перед product next-command:
python scripts/phase9_progress_harness.py --next-command "<COMMAND>" --require-product-step

Перед закрытием product slice:
python scripts/phase9_progress_harness.py --require-product-diff

Если product work находится в worktrees/amn2-public-config-delivery-policy-contract:
python scripts/phase9_progress_harness.py --repo-root worktrees/amn2-public-config-delivery-policy-contract --require-product-diff
```

## Стоп-линии

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Без exact gate не выполнять live/VPS/SSH/Telegram/public/config/peer actions.
Не печатать secrets, config payloads, QR, `vpn://`, keys, PSK, tokens,
passwords, raw logs.

## Текущий переносимый контекст

```text
previous_phase=AMN2 Phase 9
previous_phase_closeout=AMN2 Phase 9/9.2
new_phase=AMN2 Phase 10 Product Recovery With Harness
phase10_execution_chat_required=true
phase10_entry_doc=docs/AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_ENTRY.ru.md
phase10_next_chat_doc=docs/NEXT_CHAT_AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS.ru.md
phase9_9_2_final_closeout_packet=docs/AMN2_PHASE_9_9_2_FINAL_CLOSEOUT_PACKET.ru.md
phase10_harness_script=scripts/phase9_progress_harness.py
phase10_harness_tests=tests/test_phase9_progress_harness.py
phase10_rule=no hold/await loop as next product step
phase10_docs_sync_policy=after product code/test evidence only
phase_change_automation_retarget_check=required
weekly_upstream_automations_phase=AMN2 Phase 10 Product Recovery With Harness
canonical_client_display_name=NeobyatnayaNET
canonical_client_display_name_alias=НеобъятнаяNET
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1|Сервер 3
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
```

## Первый шаг

```text
ТЕКУЩАЯ МОДЕЛЬ -> DECIDE_READ_ONLY_VPS_SOURCE_OVERLAY_UPLOAD_GATE_FOR_AMN2_4326CAE_OR_SELECT_NEXT_LOCAL_RUNTIME_SLICE
```

Почему именно он:

```text
config_share_restore_schema_index_declaration_contract_status=completed-product-fix-pushed
config_share_restore_schema_index_declaration_contract_commit=60b77fd
config_share_restore_schema_index_declaration_contract_test_status=scoped_pytest_66_passed
config_share_restore_schema_index_declaration_contract_extended_test_status=scoped_pytest_151_passed
phase10_client_display_name_root_cause_status=completed-product-policy-pushed
phase10_client_display_name_root_cause_commit=d2d3099
phase10_client_display_name_root_cause_test_status=scoped_pytest_14_passed
phase10_client_display_name_root_cause_result=amneziavpn_client_generated_server_n_standalone_awg_filename_stem
phase10_config_filename_canonicalization_status=completed-product-code-pushed
phase10_config_filename_canonicalization_commit=26bb22e
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
phase10_progress_harness_known_slice_registry_status=completed-local-code
phase10_progress_harness_known_slice_registry_commit=1e0d73d
phase10_progress_harness_known_slice_registry_push_status=done
phase10_progress_harness_known_slice_registry_result=require_known_registry_for_START_PHASE10_slice_commands
phase10_progress_harness_known_slice_registry_harness=next_command_pass|product_diff_pass
phase10_progress_harness_known_slice_registry_test_status=progress_harness_pytest_12_passed
phase10_amn2_4326cae_vps_package_prep_status=completed-local-package-ready-not-vps-smoked
phase10_amn2_4326cae_vps_package_prep_commit=69323ba
phase10_amn2_4326cae_vps_package_prep_amntwo_head=4326cae
phase10_amn2_4326cae_vps_package_prep_package=dist/amn2-vps-update-and-smoke-kit-4326cae.zip
phase10_amn2_4326cae_vps_package_prep_package_sha256=FEFD9D4AE91764AB9649284E26F0F303A2F43BAECD8A511B0E492E8D9315D2F1
phase10_amn2_4326cae_vps_package_prep_source_sha256=7F91506F2C652520940C79C951A3B329964956DD1E247152E34A0FB43BAAAB06
phase10_amn2_4326cae_vps_package_prep_verification=amn2_toolchain_ok|amn2_scoped_pytest_8_passed_1_warning|package_hygiene_passed|package_extract_passed|amn3_package_tests_4_passed|diff_check_passed
phase10_amn2_4326cae_vps_package_prep_live_upload_status=not-approved
```

Schema index verification, client compatibility branch integration и
fresh-installer recovery integration закрыты; progress harness больше не должен
принимать выдуманные `START_PHASE10_*_SLICE` команды как реальные срезы.
AMN2 `4326cae` package-prep закрыт как local-only package-ready-not-vps-smoked.
Следующий шаг - либо exact decision на read-only VPS source-overlay upload/smoke
для `dist/amn2-vps-update-and-smoke-kit-4326cae.zip`, либо выбрать следующий
локальный AMN2 runtime slice. Live upload/apply остается запрещен до отдельного
exact gate.
Docs sync оставлять только хвостом после code/test evidence.

## Automation Retarget Check

Перед первым Phase 10 product slice проверить active automations. Weekly
upstream refresh chain должна быть переведена с Phase 9 на Phase 10. Если
automation проснулась в старом Phase 9/9.2 thread, она должна выдать только
retarget notice и не продолжать старую фазу.

## Формат рекомендаций

Каждая рекомендация должна указывать модель:

```text
КОДЕКС SPARK -> <одна или несколько product/test команд>
GPT-5.5 -> <risk/exact-gate decision>
```

После выполнения выводить:

- результат;
- проверки;
- `Одиночная`;
- `Двойная`;
- `Тройная`;
- `Более`;
- рекомендованный следующий шаг.
