# AMN2 Phase 9 task matrix refresh

Дата: 2026-06-27
Статус: `completed-docs-only-task-matrix-refresh`
Основа: `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`, `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`.

Текущее состояние на 2026-06-27:

```text
phase9_entry_decision=completed
selected_lane=HARDENING_PRODUCTIZATION
final_status_refresh=completed-docs-only
final_status_commit=d70ed23
latest_known_docs_sync_commit=5bcbbc4
phase9_next_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
phase9_selected_next_track=generator-code implementation / Windows filename-basename policy
windows_filename_readiness_review=APPROVED_FOR_DOCS_AND_READ_ONLY_READINESS
windows_filename_readiness_review_doc=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW.ru.md
windows_filename_readiness_runbook=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md
windows_filename_readiness_result_template=docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md
windows_filename_readiness_candidate_repo=worktrees/amn2-public-config-delivery-policy-contract
windows_filename_readiness_candidate_branch=codex/public-config-delivery-policy-contract
windows_filename_readiness_candidate_path=worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py
windows_filename_readiness_inventory_scope=read-only
windows_filename_readiness_readonly_generator_code_repo_detected=true
windows_filename_readiness_current_filename_rule=Neobyatnaya-AMNZ-N.conf
windows_filename_implementation_local_status=completed-local-code
windows_filename_implementation_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
windows_filename_implementation_gate_decision=APPROVED_WITH_TEST_ENV_LIMITATION
windows_filename_implementation_tests_status=scoped_tests_not_run_pytest_missing
windows_filename_readiness_target_filename_rule=Neobyatnaya-AMNZ-N.conf
phase9_execution_go=false
phase9_config_generation=false
phase9_config_delivery=false
phase9_peer_creation=false
phase9_live_vps_ssh_telegram_public=false
phase9_canonical_naming=Neobyatnaya-AMNZ-N
phase9_windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
phase9_android_status=DOCUMENTED_LIMITATION
phase9_android_observed=Сервер 1
phase9_android_fallback=manual_rename
phase9_ios_status=not_proven/manual_rename_fallback
phase9_android_display_name_decision_commit=691790a
phase9_android_display_name_decision_status=DOCUMENTED_LIMITATION
phase9_android_display_name_observed=Сервер 1
phase9_android_display_name_pass_required=Neobyatnaya-AMNZ-N
phase9_android_display_name_pass_not_reached=true
phase9_android_display_name_gap=localized_SERVER1_client_display_name_compatibility_gap
phase9_android_display_name_fallback=manual_rename
phase9_android_display_name_windows_policy=filename/basename_Neobyatnaya-AMNZ-N.conf
phase9_android_display_name_ios_policy=not_proven_manual_rename_fallback
phase9_android_display_name_execution_go_after_result=false
phase9_platform_display_name_policy=windows_filename_based_android_ios_manual_rename_fallback
hardening_entry_gap_tasks_prep=completed
hardening_entry_review=completed-docs-only
public_launch_entry_review=completed_no_go_stay_in_hardening
public_launch_go=blocked
private_self_config_execution_approved=false
private_self_config_readiness_with_naming_review=completed-docs-only
private_self_config_readiness_with_naming_doc=docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md
ios_acceptance_decision_review=completed
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ssh_auth_noise_mitigation_review=completed
ssh_auth_hardening_gate_review=completed-docs-only
ssh_auth_hardening_gate_review_doc=docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
ssh_auth_hardening_gate_review_reviewed_by=ChatGPT 5.5
ssh_auth_hardening_future_exact_gate_required=true
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_review=completed
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
important_block_realization=completed-docs-only
telegram_operation_runbook_polish=completed
phase9_naming_docs_sync=completed-docs-only
private_rc_final_status_refresh_reflected=true
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Блокеры и разрешения из Phase 8 сохранены:
- `public_launch_status=not-approved`
- `config_delivery_status=not-approved`
- `peer_creation_status=not-approved`
- `production_rollout_status=not-approved`
- `public_self_service_config_delivery_status=not-approved`
- `telegram_profile_media_mutation_status=not-approved`

Принятая модель совместной работы:
- Документированные и локальные задачи делает `ChatGPT 5.3-Spark`
  (`Codex-Spark` в старой терминологии).
- Рискованные решения и выбор следующей дороги в Phase 9 делает `ChatGPT 5.5`.
- Если задача помечена как `requires_model_switch=true`, запрашиваем у тебя подтверждение перед запуском в другой модели.
- `requires_exact_named_gate=true` означает: задача допустима только после отдельного exact gate.

## Обязательная Phase 9 naming-доработка

`Neobyatnaya-AMNZ-N` считается canonical config/device name policy, а не
примером и не обходом. Phase 9 должна отдельно закрыть:

```text
canonical_config_device_name=Neobyatnaya-AMNZ-N
config_filename_policy=Neobyatnaya-AMNZ-N.conf
forbidden_generic_names=SERVER1,server1,third-party-android-device-N,android-device-N
app_display_name_issue=SERVER1_observed_after_import
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
private_self_config_readiness_with_naming_review=completed-docs-only
android_display_name_future_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_display_name_gate_review=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW.ru.md
android_display_name_gate_review_status=docs-prepared-and-review-decided
android_display_name_gate_decision_status=DOCUMENTED_LIMITATION
android_display_name_gate_execution_go=false
android_display_name_gate_runbook=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK.ru.md
android_display_name_gate_result_template=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md
android_display_name_gate_result=docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md
android_display_name_gate_docs_status=completed-docs-only
android_display_name_future_exact_gate_required=true
android_observed_display_name=Сервер 1
android_observed_display_name_classification=localized_SERVER1_documented_limitation
windows_amneziawg_display_name_strategy=filename_basename
windows_amneziawg_required_filename=Neobyatnaya-AMNZ-N.conf
android_display_name_strategy=manual_rename_fallback
ios_display_name_strategy=not_proven_manual_rename_fallback
```

Задача делится на два слоя:

- генерируемое имя config/device/file должно быть `Neobyatnaya-AMNZ-N`;
- отображаемое имя профиля/сервера в Android AmneziaWG после import не должно
  оставаться `SERVER1` без явного documented limitation/fallback.
- `SERVER1` считается клиентской несовместимостью отображения имени (`client display-name compatibility gap`) до отдельного
  acceptance по exact-gate, и не является разрешенным generic name.

Результат решения `ChatGPT 5.5`:

```text
android_display_name_pass=Neobyatnaya-AMNZ-N
android_display_name_documented_limitation=SERVER1/Сервер 1 как compatibility issue + manual rename fallback only
android_display_name_fail=generic_generated_name_or_filename_or_payload_secrets_output_or_peer_config_public_self_service_action
android_display_name_gate_next=awaiting_operator_exact_gate
```

Implementation policy:

```text
where_possible_implement_display_name=true
windows_amneziawg_implementation=filename_basename_Neobyatnaya-AMNZ-N
android_amnezia_implementation=not_supported_or_not_proven_keep_manual_rename
ios_amnezia_implementation=not_proven_keep_manual_rename
```

## Матрица задач

| Критичность | Задача | Рекомендуемый исполнитель | Codex может делать сам | Что требует согласия/переключения модели | Что требует exact named gate | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| Критично | `AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено docs-only: closed self/operator path выбран, public/self-service/config-for-everyone go=false |
| Критично | `AMN2_PHASE_9_CONFIG_PROFILE_NAMING_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Закрыто внутри combined review: `Neobyatnaya-AMNZ-N` обязателен, `SERVER1` трактуется как display-name gap |
| Критично | `AMN2_PHASE_9_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW` | ChatGPT 5.3-Spark | true | false | true (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`) | Артефакт подготовлен, решение 5.5 принято; ждем operator-confirmed execution |
| Критично | `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW` | ChatGPT 5.5 (decision only) | false | true (`requires_model_switch`) | true (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`) | Схема pass/fail и limitation/fallback зафиксирована |
| Критично | `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK` | ChatGPT 5.3-Spark | true | false | true (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`) | Подготовлен runbook проверки display-name после import |
| Критично | `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE` | ChatGPT 5.3-Spark | true | false | true (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`) | Подготовлен шаблон безопасной фиксации результата exact gate |
| Критично | `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT` | ChatGPT 5.3-Spark | true | false | false | Safe result recorded: `Сервер 1` -> documented limitation/manual rename |
| Критично | `AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS` | ChatGPT 5.3-Spark | true | false | false | Docs-only handoff выполнен; следующий трек задан: `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE` |
| Критично | `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE_REVIEW` | ChatGPT 5.3-Spark | true | false | false | Выполнена подтверждающая readiness-проверка: docs-only + read-only inventory (`worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`) |
| Критично | `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK` | ChatGPT 5.3-Spark | true | false | false | Подготовлен read-only inventory checklist для поиска generator-code точки filename-forming |
| Критично | `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE` | ChatGPT 5.3-Spark | true | false | false | Подготовлен шаблон фиксации read-only readiness результата |
| Критично | `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE` | ChatGPT 5.3-Spark | true | false | false | Локальная имплементация выполнена: `Neobyatnaya-AMNZ-N.conf` в `worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`; 5.5 decision: `APPROVED_WITH_TEST_ENV_LIMITATION`; scoped tests не запускались (`pytest` отсутствует) |
| Критично | `AMN2_PHASE_9_ANDROID_DISPLAY_NAME_GATE_RESULT_SYNC` | ChatGPT 5.3-Spark | true | false | false | `completed` (pair-sync): `PROJECT_STATUS_CURRENT` + `TASK_MATRIX_REFRESH`; результат `Сервер 1` зафиксирован как `DOCUMENTED_LIMITATION`, `production naming` остается `Neobyatnaya-AMNZ-N`, Android fallback `manual rename`, iOS not proven/manual rename fallback |
| Критично | `AMN2_PHASE_9_NAMING_DOCS_SYNC` | ChatGPT 5.3-Spark | true | false | false | Выполнено docs-only после 5.5 review; перед commit/push нужен safe scan |
| Критично | `AMN2_PHASE_9_ENTRY_DECISION` (lane уже выбран: `HARDENING_PRODUCTIZATION`) | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено, lane зафиксирован |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` (закрыт) | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено |
| Критично | `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW` (lane confirmed) | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнен: `public_launch_go=false`, продолжение на hardening lane |
| Критично | `AMN2_PHASE_9_FINAL_STATUS_REFRESH` | ChatGPT 5.3-Spark | true | false | false | Завершён и подтверждён (`259b742`) |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW_GAP_TASKS_PREP` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено: закрывает gap-prep и anti-loop rule |
| Критично | `AMN2_PHASE_9_CONFIG_DELIVERY_ENTRY_REVIEW` (если меняется lane в другой трек) | ChatGPT 5.5 | false | true (`requires_model_switch`) | true (`CONFIG_DELIVERY_GATE_REVIEW` exact) | Подготовить review bundle и запуск exact gate |
| Критично | `AMN2_PHASE_9_DR_ENTRY_REVIEW` (если меняется lane в другой трек) | ChatGPT 5.5 | false | true (`requires_model_switch`) | true (`RESTORE_IMPORT_DR_GATE_REVIEW` exact) | Подготовить DR-review и exact gate |
| Критично | `AMN2_PHASE_9_POST_SSH_AUTH_REVIEW_SYNC` | ChatGPT 5.3-Spark | true | false | false | Выполнить post-sync синхронизацию статусов после завершения SSH auth hardening review |
| Очень важно | `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Проверить актуальность условий lane и stop-lines |
| Очень важно | `AMN2_PHASE_9_PUBLIC_GATE_PREP_REFRESH` (`PUBLIC_EXPOSURE_GATE_REVIEW` при выборе lane 1) | ChatGPT 5.5 | false | true (`requires_model_switch`) | true (`PUBLIC_EXPOSURE_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_CONFIG_DELIVERY_GATE_PREP_REFRESH` (`CONFIG_DELIVERY_GATE_REVIEW` при lane 2) | ChatGPT 5.5 | false | true (`requires_model_switch`) | true (`CONFIG_DELIVERY_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_DR_GATE_PREP_REFRESH` (`RESTORE_IMPORT_DR_GATE_REVIEW` при lane 4) | ChatGPT 5.5 | false | true (`requires_model_switch`) | true (`RESTORE_IMPORT_DR` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` | ChatGPT 5.3-Spark | true | false | false | Держать ограничения по статусу и hold-правила |
| Очень важно | `AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH` | ChatGPT 5.3-Spark | true | false | false | Синхронизировать итоговый status после выбранного lane + review outcomes |
| Важно | `AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено: validated после passed no-long-SSH result |
| Важно | `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено: не blocker для hardening lane; SSH auth hardening review принят docs-only, execution только future exact gate |
| Важно | `AMN2_DB_AGGREGATE_COUNTS_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено: optional-confidence-not-hardening-blocker; live counts только через future exact gate |
| Важно | `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` | ChatGPT 5.5 | false | true (`requires_model_switch`) | false | Выполнено: `DefaultVPN failed-no-tested-import-path`; future exact gate для любых iOS claims |
| Важно | `AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION` | ChatGPT 5.5 | true | false | false | Выполнено docs-only, блоки сведены в единый hardening decision set |
| Просто | `NEXT_CHAT_AMN2_PHASE_9_SESSION` | ChatGPT 5.3-Spark | true | false | false | Сгенерировать/актуализировать next-chat sync с выбранным lane |
| Просто | `AMN2_PHASE_9_TASK_MATRIX_REFRESH` | ChatGPT 5.3-Spark | true | false | false | Завершён и обновлён после `AMN2_PHASE_9_FINAL_STATUS_REFRESH` |
| Просто | `PROJECT_STATUS_CURRENT.ru.md refresh` | ChatGPT 5.3-Spark | true | false | false | Синхронизировать текущий статус, оставляя hold до exact gate |
| Просто | `SECRET_POLLUTION_SCAN` (скан на `.conf`, `token`, `private key`, `PSK`, `qr`, `vpn://`) | ChatGPT 5.3-Spark | true | false | false | Выполнить перед любым следующим commit/push |

### Критичный gate-резюме до next chat

```text
critical_openers=AMN2_PHASE_9_HARDENING_ENTRY_REVIEW, AMN2_PHASE_9_ENTRY_DECISION, AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE
docs_only_openers=AMN2_PHASE_9_HARDENING_DOCS_PACKAGE, AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH, AMN2_HELPER_SSH_TRANSPORT_HARDENING, AMN2_HELPER_STYLE_HARDENING, AMN2_PHASE_9_FINAL_STATUS_REFRESH, AMN2_PHASE_9_TASK_MATRIX_REFRESH, AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW
android_display_name_gate_openers=AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW, AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK, AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE
live_openers=requires_operator_approval + exact_named_gate
post_review_sync_completed=AMN2_PHASE_9_POST_SSH_AUTH_REVIEW_SYNC
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Следующий шаг сейчас

- До operator-confirmed нового exact gate — `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
- На этом этапе ChatGPT 5.3-Spark выполняет docs-only sync (без live/VPS/SSH/Telegram/public):
  - `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` при изменении входных условий;
  - `AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW` выполнен для закрытого self/operator config path, `Neobyatnaya-AMNZ-N` и `SERVER1`;
  - повторный `AMN2_PHASE_9_TASK_MATRIX_REFRESH` при изменении статусов;
  - `AMN2_PHASE_9_FINAL_STATUS_REFRESH` при появлении новых фактов.
- Read-only readiness-инвентаризация для Windows filename/basename завершена:
  - целевой `generator-code` repository/ветка в `worktrees/amn2-public-config-delivery-policy-contract` подтверждена и уже изменена локально;
  - код для доработки filename применен в `worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`.
- Продолжить `AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_GATE` с `execution_go=false`, передав результаты `result_sync` 5.3-Spark в `docs-only` и далее на 5.5 для решения риск-модели и exact gate, если потребуется.
- `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE` сейчас статус: `execution_go=false`.
  При запросе оператора выполнить exact gate, и только по результату этого
  обновлять `private_self_config_execution_go`.
- Закрытые статусы по review:
  - `AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW`: `selected_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING`, `public_launch_go=false`, `public_self_service_go=false`, `private_self_config_execution_go=false`.
  - `AMN2_PHASE_9_CONFIG_PROFILE_NAMING_REVIEW`: covered by combined review; `SERVER1` is a display-name compatibility gap pending future exact gate.
  - `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`: `ssh_auth_hardening_execution=not-approved`, `future_exact_gate_required=true`.
  - `AMN2_DB_AGGREGATE_COUNTS_REVIEW`: `future_exact_gate_required_for_live_counts=true`.
  - `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW`: `ios_defaultvpn_status=failed-no-tested-import-path`, `public release claim deferred`.
- `AMN2_PHASE_9_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW`: future exact gate only; import и генерация конфига сейчас не выполняются.
- `AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW`: docs-only пакет review/runbook/result template подготовлен, выполнение exact gate делегировано 5.5 по запросу оператора.

## Правило по модели (соглашение с тобой)

- Если задача помечена `requires_model_switch=true`, это значит:
  - `ChatGPT 5.5` делает risk decision и exact-gate decision framing;
  - `ChatGPT 5.3-Spark` выполняет только docs-only sync после решения.
