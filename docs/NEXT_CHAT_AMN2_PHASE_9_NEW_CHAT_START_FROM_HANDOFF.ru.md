# Следующий чат: AMN2 Phase 9 старт из Phase 8 handoff

Дата: 2026-06-27.

## Команда для нового чата

```text
AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF

Модель: ChatGPT 5.3-Spark для текущего docs-only синхрона после решения.
ChatGPT 5.5 используется для отдельных exact gate решений (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`,
`AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE`) по запросу оператора.

Порядок выполнения для docs-only Spark-потока (по состоянию на этот handoff):
`NEXT_CHAT` -> `safe-scan` -> `git diff --check` -> `commit/push`,
только если в процессе синка появился новый артефакт для синхронизации в
`PROJECT_STATUS_CURRENT` / `AMN2_PHASE_9_TASK_MATRIX_REFRESH` /
`NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF`.

Использовать:
- docs/AMN2_PHASE_8_FINAL_HANDOFF_TO_PHASE_9_NEW_CHAT_SYNC.ru.md
- docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md
- docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md
- docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md
- docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
- docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md
- docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW.ru.md
- docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md
- docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md

Не открывать live/VPS/SSH/config/Telegram/public gates без отдельного exact
named gate.
Не менять VPS/config/auth/firewall/users/keys/ports.
Не выводить secrets, keys, tokens, configs или raw logs.

Цель:
- принять Phase 8 как закрытую;
- принять уже подготовленные Phase 9 docs/commits как existing material;
- принять решение 5.5 по `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE` и
  закрепить его в `status/matrix/next-chat`.
- оценить близость Phase 9 к закрытому self/operator config release, не к
  public release;
- добавить обязательную naming-доработку:
  имя config/device должно быть `Neobyatnaya-AMNZ-N`;
- отдельно разобрать проблему названия профиля в приложении:
  после import профиль/сервер сейчас отображается как `SERVER1`; надо определить,
  берёт ли Android AmneziaWG имя из filename, имени device, metadata или
  из дефолтного поведения app;
- зафиксировать решение 5.5: pass=`Neobyatnaya-AMNZ-N`, `SERVER1` — это только
  client display-name compatibility gap с fallback `manual rename`, всё остальное
  generic/name/fail.
- не повторять generic refresh без нового статуса;
- при необходимости отдельно решить судьбу локального draft:
  docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
```

## Стартовый контекст

```text
previous_chat_closure=Phase 8 final closeout/handoff
phase8_final_status=launch-ready-with-explicit-limitations
phase9_material_status=prepared-existing-material
branch=codex-spark-phase9-docs-sync
latest_known_pre_sync_commit=5bcbbc4
private_self_config_readiness_with_naming_review=completed-docs-only
android_display_name_gate_decision=DOCUMENTED_LIMITATION
android_display_name_gate_execution_go=false
android_display_name_next_step=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА_OR_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_observed_display_name=Сервер 1
windows_amneziawg_display_name_strategy=filename_basename
android_ios_display_name_strategy=manual_rename_fallback_until_supported_or_proven
ssh_auth_hardening_gate_review=completed-docs-only
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
current_model=ChatGPT 5.3-Spark
spark_docs_only_sync_mode=NEXT_CHAT_safe_scan_diffcheck_commit_push
spark_docs_only_sync_scope=PROJECT_STATUS_CURRENT_and_TASK_MATRIX_REFRESH_and_NEXT_CHAT
phase9_platform_display_name_implementation_readiness_doc=docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md
phase9_platform_display_name_implementation_next=generator_code_docs_ready
android_display_name_gate_result=DOCUMENTED_LIMITATION
android_display_name_gate_observed=Сервер 1
android_display_name_gate_next=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА_OR_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
execution_go_after_gate_result=false
android_display_name_gate_decision_status=DOCUMENTED_LIMITATION
android_display_name_gate_pass_not_reached=true
android_display_name_gate_pass_required=Neobyatnaya-AMNZ-N
android_display_name_gate_observed=Сервер 1
android_display_name_gate_observed_classification=localized_SERVER1_client_display_name_compatibility_gap
android_display_name_gate_production_naming=Neobyatnaya-AMNZ-N
android_display_name_gate_fallback=manual_rename
android_display_name_gate_windows_policy=filename/basename_Neobyatnaya-AMNZ-N.conf
android_display_name_gate_ios_policy=not_proven_manual_rename_fallback
android_display_name_gate_execution_go_after_result=false
next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
selected_next_track=generator-code / private self-config execution package prep
phase9_private_self_config_execution_readiness_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
phase9_private_self_config_execution_readiness_next=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
windows_filename_basename_readiness_status=APPROVED_FOR_DOCS_AND_READ_ONLY_READINESS
windows_filename_basename_readiness_review=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW.ru.md
windows_filename_basename_readiness_runbook=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md
windows_filename_basename_readiness_result_template=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md
windows_filename_basename_candidate_repo=worktrees/amn2-public-config-delivery-policy-contract
windows_filename_basename_candidate_path=worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py
windows_filename_basename_candidate_current=Neobyatnaya-AMNZ-N.conf
windows_filename_basename_candidate_target=Neobyatnaya-AMNZ-N.conf
windows_readiness_generator_code_repo_detected=true
windows_filename_basename_implementation_local_status=completed-local-code
windows_filename_basename_implementation_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
windows_filename_basename_implementation_gate_decision=APPROVED_WITH_TEST_ENV_LIMITATION
windows_filename_basename_implementation_test_status=pushed-with-runtime-export-guard-scoped-tests
windows_filename_basename_implementation_commit=3a6da8f
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
phase9_automation_intake_2026_06_28=P9-N007_docs-only_review-only
phase9_amnezia_client_watch=4.8.19.0_release_current_4.9.0.3_unreleased_watch
phase9_prvtpro_watch=v1.4.4_a62f958_carry-forward_no_new_launch_go
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
phase9_private_self_config_execution_readiness_decision=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
phase9_private_self_config_execution_readiness_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
phase9_private_self_config_execution_readiness_review_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE_REVIEW.ru.md
phase9_private_self_config_execution_readiness_runbook=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RUNBOOK.ru.md
phase9_private_self_config_execution_readiness_result_template=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT_TEMPLATE.ru.md
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
canonical_naming=Neobyatnaya-AMNZ-N
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
```

Phase 8 закрыта для private/operator RC. Android private/operator proof,
Telegram no-long-SSH proof, DB path existence classification и key-based SSH
prep уже зафиксированы. Public launch, config delivery, peer creation и
production rollout не разрешены.

## Что уже подготовлено для Phase 9

- Entry brief и lane candidates.
- Hardening/productization lane materials.
- Helper no-long-SSH standards.
- SSH auth-noise review как future exact gate boundary.
- DB aggregate counts как optional-confidence future gate.
- iOS DefaultVPN acceptance как failed-no-tested-import-path, без release claim.
- Private self-config readiness with naming review:
  `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md`.
  Первый трек подтвержден как `PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING`.
  `execution_go=false` до operator-confirmed exact gate.
- SSH auth hardening review:
  `docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md`. Review passed docs-only;
  execution approved now: false.
- Android display-name gate package docs:
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md`
  Docs-only артефакты и safe result подготовлены. Решение 5.5:
  pass=`Neobyatnaya-AMNZ-N`,
  limitation=`SERVER1`/`Сервер 1` documented с fallback `manual rename`,
  fail=`generic/production naming или payload/secrets action`.
- Platform display-name policy:
  Windows AmneziaWG standalone: реализуем через filename/basename
  `Neobyatnaya-AMNZ-N.conf`.
  Android/iOS Amnezia app: automatic display-name из `.conf` не доказан,
  оставляем `manual rename` fallback.
  Safe observation: `Observed display name = Сервер 1`.
  Implementation readiness handoff prepared: `docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md`.
- Windows filename/basename readiness (docs/read-only):
  - `docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW.ru.md`
  - `docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md`
  - `docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md`
  Read-only inventory обнаружил точку формирования `config_filename` в
  `worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`, и
  код уже локально переведен на canonical filename.
- Пакет для execution-readiness:
  - `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE_REVIEW.ru.md`
  - `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RUNBOOK.ru.md`
  - `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT_TEMPLATE.ru.md`

## Что считать истинно текущим сейчас (не как исторический passed)

- `android_display_name_gate_decision_status=DOCUMENTED_LIMITATION`
- `android_display_name_gate_pass_required=Neobyatnaya-AMNZ-N`
- `android_display_name_gate_pass_not_reached=true`
- `android_display_name_gate_observed=Сервер 1`
- `android_display_name_gate_observed_classification=localized_SERVER1_client_display_name_compatibility_gap`
- `android_display_name_gate_fallback=manual_rename`
- `android_display_name_gate_production_naming=Neobyatnaya-AMNZ-N`
- `android_display_name_gate_windows_policy=filename/basename_Neobyatnaya-AMNZ-N.conf`
- `android_display_name_gate_ios_policy=not_proven_manual_rename_fallback`
- `android_display_name_gate_execution_go_after_result=false`
- `windows_filename_readiness_status=APPROVED_FOR_DOCS_AND_READ_ONLY_READINESS`
- `windows_filename_readiness_inventory=read-only_completed`
- `windows_filename_readiness_candidate=worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`
- `windows_filename_readiness_generator_code_repo_detected=true`
- `windows_filename_basename_implementation_local_status=completed-local-code`
- `windows_filename_basename_implementation_gate_decision=APPROVED_WITH_TEST_ENV_LIMITATION`
- `windows_filename_basename_implementation_test_status=scoped_tests_not_run_pytest_missing`
- `phase9_automation_intake_2026_06_28=P9-N007_docs-only_review-only`
- `phase9_amnezia_client_watch=4.8.19.0_release_current_4.9.0.3_unreleased_watch`
- `phase9_prvtpro_watch=v1.4.4_a62f958_carry-forward_no_new_launch_go`

```text
next_phase_execution_gate_hold=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
execution_go_after_result=false
config_generation_delivery=not-approved
peer_creation=not-approved
public_launch=not-approved
```

## Обязательная naming-граница для config/self-use

Phase 9 должна считать `Neobyatnaya-AMNZ-N` не примером и не обходным путем, а
canonical naming policy для private/self/operator configs.

```text
canonical_config_device_name=Neobyatnaya-AMNZ-N
config_filename_policy=Neobyatnaya-AMNZ-N.conf
do_not_use_generic_names=true
forbidden_generic_names=SERVER1,server1,third-party-android-device-N,android-device-N
app_display_name_issue=SERVER1_observed_after_import
display_name_acceptance_required=true
server1_classification=client-display-name-product-compatibility-gap
android_display_name_future_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_display_name_pass=Neobyatnaya-AMNZ-N
android_display_name_documented_limitation=SERVER1_or_Сервер 1_as_client_display_name_gap_with_manual_rename_fallback
android_display_name_fail=generic_name_or_filename|payload_secrets_output|peer_config_public_self_service_action
android_display_name_execution_go=false
windows_amneziawg_display_name_strategy=filename_basename
windows_amneziawg_required_filename=Neobyatnaya-AMNZ-N.conf
android_display_name_strategy=manual_rename_fallback
ios_display_name_strategy=not_proven_manual_rename_fallback
```

Важно разделить два слоя:

- имя config/device/file должно формироваться как `Neobyatnaya-AMNZ-N`;
- имя, которое видит пользователь в Android AmneziaWG после import, должно быть
  проверено отдельно. Если клиент игнорирует filename и показывает `SERVER1` или
  `Сервер 1`,
  Phase 9 зафиксировала это как client display-name gap и фиксирует fallback
  `manual rename`.
- где можно задать имя без изменения payload, закладываем реализацию: для
  Windows AmneziaWG standalone это filename/basename `Neobyatnaya-AMNZ-N.conf`.
- для Android/iOS Amnezia app автоматическое display-name из `.conf` не
  подтверждено; оставляем documented limitation.

Первый Phase 9 практический трек должен быть ближе к private self-config
readiness, а не к public launch:

```text
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
first_track_review_status=completed-docs-only
public_launch_go=false
public_self_service_go=false
config_for_everyone_go=false
self_operator_config_review_required=true
private_self_config_execution_go=false
```

## Разделение задач по моделям

`ChatGPT 5.5`:

- выбирает Phase 9 lane и первый exact gate;
- решает, разрешать ли private self-config generation/handoff review;
- формирует risk/rollback/pass-fail/stop-lines для live/config gates;
- принимает решение по `SERVER1` display-name problem как product/compatibility
  issue;
- решает, нужен ли execution gate или только docs/local implementation prep.

`ChatGPT 5.3-Spark`:

- делает docs-only sync, status refresh, task matrix, NEXT_CHAT;
- готовит runbook/checklist после решения `ChatGPT 5.5`;
- делает local-only code/doc prep только без live/VPS/SSH/Telegram/public gate;
- выполняет safe scan, diff check, commit/push для docs-only changes;
- не принимает рискованные решения и не открывает exact gates сам.

## Локальный draft

В предыдущем workspace оставался untracked draft:

```text
docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
```

В этом sync он принят как docs-only review material. Он не открывает SSH/auth
execution и не разрешает mutation. Любая реальная SSH hardening execution
требует отдельный exact gate `AMN2_SSH_AUTH_HARDENING_EXECUTION_GATE`.

## Ограничения

Остается запрещено без exact gate:

- public launch/public exposure;
- config generation/delivery;
- peer creation;
- production rollout;
- SSH/auth/firewall/users/keys/ports changes;
- Telegram polling/live send;
- package upload/apply;
- service restart/start/stop;
- restore/import/reboot/provider action;
- `.conf`, QR, `vpn://`, private key, PSK, token/password или raw log output.

## Текущее рекомендованное решение

```text
recommended_first_decision=post_decision_sync_completed
recommended_model_for_risk_decision=ChatGPT 5.5
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
next_safe_docs_step=done-by-spark-sync
windows_filename_basename_implementation_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
windows_filename_basename_implementation_gate_decision=APPROVED_WITH_TEST_ENV_LIMITATION
windows_filename_basename_implementation_test_status=scoped_tests_not_run_pytest_missing
android_display_name_gate_decision=DOCUMENTED_LIMITATION
android_display_name_gate_pass=Neobyatnaya-AMNZ-N
android_display_name_gate_documented_limitation=SERVER1_or_Сервер 1_client_display_name_gap_with_manual_rename_fallback
android_display_name_gate_fail=generic_name_or_filename_or_payload_or_peer_public_action
android_display_name_gate_result=Сервер 1_documented_limitation
windows_amneziawg_next=implement_filename_basename_policy
android_ios_next=keep_manual_rename_fallback
execution_go=false_until_operator_exact_gate
next_execution_candidate_if_operator_requests=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Коротко для перехода в следующий чат (готовый текст)

**Важно:** решение `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE` принято как
`DOCUMENTED_LIMITATION` (не pass), потому что на одном контролируемом Android
отображение после import = `Сервер 1`.

**Ключевые факты для принятия:**
- `pass_required=Neobyatnaya-AMNZ-N`
- `pass_not_reached=true`
- `classification=localized_SERVER1_client_display_name_compatibility_gap`
- `android_fallback=manual_rename`
- `production_naming=Neobyatnaya-AMNZ-N`
- `execution_go_after_result=false`

**Где можно продолжать реализацию:**
- Windows: filename/basename `Neobyatnaya-AMNZ-N.conf`
- Android/iOS: keep manual rename fallback, automatic display-name пока не подтвержден.

**Для вставки в 5.5 (copy/paste):**
```text
AMN2_PHASE_9_ANDROID_DISPLAY_NAME_ACCEPTANCE_POST_DECISION_SYNC
Модель: ChatGPT 5.3-Spark / Codex docs-only.
decision_status=DOCUMENTED_LIMITATION
Observed display name=Сервер 1
pass_not_reached=true
pass_required=Neobyatnaya-AMNZ-N
classification=localized_SERVER1_client_display_name_compatibility_gap
execution_go_after_result=false
android_fallback=manual_rename
android_display_name_production_naming=Neobyatnaya-AMNZ-N
```
## P9_VALIDATION_AND_CONFIG_PATH_CHECKLIST_SYNC

Модель: ChatGPT 5.3-Spark / Codex docs-only.
Статус: docs-only checklist prepared и подготовлен к следующему sync.

Документ: `docs/AMN2_PHASE_9_VALIDATION_AND_CONFIG_PATH_CHECKLIST.ru.md`.

Следующий безопасный шаг по `NEXT_CHAT`:
- зафиксировать `phase9_validation_checklist_status=completed-docs-only` в статусных артефактах;
- выполнить `safe scan` и `git diff --check`;
- выполнить commit/push с `execution_go=false`, `config_generation=false`, `config_delivery=false`, `peer_creation=false`, `live_vps_ssh_telegram_public=false`.

## AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_FINAL_REVIEW_GATE

Модель: ChatGPT 5.3-Spark / Codex docs-only.

```text
task=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_FINAL_REVIEW_GATE
decision_status=APPROVED_NEXT_GATE_DOCS_ONLY
decision_confirmation=CONFIRMED_BY_5_5
next_gate=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
risk_model=display-name_gap_only_client_side; generation/display policy is canonical; no live/config/peer mutations
pass=canonical_naming_Must_Be_Neobyatnaya-AMNZ-N
android_limitation=Сервер 1 as documented client display-name compatibility gap + manual_rename fallback
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
ios_policy=not_proven_manual_rename_fallback
fail=generic naming as production naming|payload/secrets output|peer/config/public actions
stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
next_sync=PROJECT_STATUS_CURRENT / AMN2_PHASE_9_TASK_MATRIX_REFRESH / NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF
```

После sync:
- `safe scan` по обновленным docs;
- `git diff --check`;
- `commit/push`.

## AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE

Модель: ChatGPT 5.5.

```text
task=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
decision_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
decision_confirmation=CONFIRMED_BY_5_5
next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
risk_model=docs-only package prep only; no live/VPS/SSH/Telegram/public/config/peer scope until exact gate
pass=Neobyatnaya-AMNZ-N
android_limitation=Сервер 1 as documented client display-name compatibility gap + manual_rename fallback
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
ios_policy=not_proven_manual_rename_fallback
fail=generic naming as production naming|payload/secrets output|peer/config/public/self-service actions
stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
next_sync=PROJECT_STATUS_CURRENT / AMN2_PHASE_9_TASK_MATRIX_REFRESH / NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF
```

Для вставки в 5.5 (если нужно повторить):

```text
AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE
Модель: ChatGPT 5.5
decision_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
risk_model=docs-only package prep only
pass=Neobyatnaya-AMNZ-N
fail=generic naming as production naming|payload/secrets output|peer/config/public actions
stop_lines=execution_go=false|config_generation=false|config_delivery=false|peer_creation=false|live_vps_ssh_telegram_public=false
```

После sync:
- `safe scan` по обновленным docs;
- `git diff --check`;
- `commit/push`.
