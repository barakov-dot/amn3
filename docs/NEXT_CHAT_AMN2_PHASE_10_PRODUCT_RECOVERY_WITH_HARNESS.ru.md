# Следующий чат: AMN2 Phase 10 Product Recovery With Harness

Дата: 2026-07-04.

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
ТЕКУЩАЯ МОДЕЛЬ -> SELECT_NEXT_REAL_PHASE10_PRODUCT_SLICE_AFTER_PROGRESS_HARNESS_KNOWN_SLICE_REGISTRY -> START_PHASE10_<KNOWN_REAL_TOPIC>_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE
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
```

Schema index verification, client compatibility branch integration и
fresh-installer recovery integration закрыты; progress harness больше не должен
принимать выдуманные `START_PHASE10_*_SLICE` команды как реальные срезы.
Следующий шаг - выбрать следующий известный real Phase 10 product slice:
`SELECT_NEXT_REAL_PHASE10_PRODUCT_SLICE_AFTER_PROGRESS_HARNESS_KNOWN_SLICE_REGISTRY`.
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
