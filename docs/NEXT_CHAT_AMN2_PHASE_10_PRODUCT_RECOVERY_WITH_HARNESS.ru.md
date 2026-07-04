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
new_phase=AMN2 Phase 10 Product Recovery With Harness
phase10_entry_doc=docs/AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_ENTRY.ru.md
phase10_next_chat_doc=docs/NEXT_CHAT_AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS.ru.md
phase10_harness_script=scripts/phase9_progress_harness.py
phase10_harness_tests=tests/test_phase9_progress_harness.py
phase10_rule=no hold/await loop as next product step
phase10_docs_sync_policy=after product code/test evidence only
canonical_client_display_name=NeobyatnayaNET
canonical_client_display_name_alias=НеобъятнаяNET
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1|Сервер 3
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
```

## Первый шаг

```text
ТЕКУЩАЯ МОДЕЛЬ -> START_PHASE10_CONFIG_FILENAME_CANONICALIZATION_FOR_STANDALONE_AWG_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE -> REVIEW_SELECTED_LOCAL_PRODUCT_SLICE_DIFF
```

Почему именно он:

```text
config_share_restore_schema_index_declaration_contract_status=completed-product-fix-pushed
config_share_restore_schema_index_declaration_contract_commit=60b77fd
config_share_restore_schema_index_declaration_contract_test_status=scoped_pytest_66_passed
config_share_restore_schema_index_declaration_contract_extended_test_status=scoped_pytest_151_passed
phase10_client_display_name_root_cause_status=completed-product-policy-pushed
phase10_client_display_name_root_cause_commit=d01cb7b
phase10_client_display_name_root_cause_test_status=scoped_pytest_14_passed
phase10_client_display_name_root_cause_result=amneziavpn_client_generated_server_n_standalone_awg_filename_stem
```

Schema index verification slice закрыт. Следующий шаг - выбрать следующий
Phase 10 product slice:
`START_PHASE10_CONFIG_FILENAME_CANONICALIZATION_FOR_STANDALONE_AWG_SLICE`.
Docs sync оставлять только хвостом после code/test evidence.

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
