# AMN2 Phase 9 task matrix refresh

Дата: 2026-06-27
Статус: `completed-docs-only-task-matrix-refresh`
Основа: `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`, `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`.

Текущее состояние на 2026-06-27:

```text
phase9_entry_decision=passed
selected_lane=HARDENING_PRODUCTIZATION
final_status_refresh=passed
final_status_commit=d70ed23
latest_docs_sync_commit=d70ed23
hardening_entry_gap_tasks_prep=passed
hardening_entry_review=passed
public_launch_entry_review=completed_no_go_stay_in_hardening
public_launch_go=blocked
ios_acceptance_decision_review=passed
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ssh_auth_noise_mitigation_review=passed
ssh_auth_hardening_gate_review=prepared
ssh_auth_hardening_gate_review_reviewed_by=GPT-5.5
ssh_auth_hardening_future_exact_gate_required=true
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_review=passed
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
important_block_realization=completed-docs-only
telegram_operation_runbook_polish=passed
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
- Документированные и локальные задачи делает `Codex-Spark`.
- Рискованные решения и выбор следующей дороги в Phase 9 делает `GPT-5.5`.
- Если задача помечена как `requires_model_switch=true`, запрашиваем у тебя подтверждение перед запуском в другой модели.
- `requires_exact_named_gate=true` означает: задача допустима только после отдельного exact gate.

## Матрица задач

| Критичность | Задача | Рекомендуемый исполнитель | Codex может делать сам | Что требует согласия/переключения модели | Что требует exact named gate | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| Критично | `AMN2_PHASE_9_ENTRY_DECISION` (lane уже выбран: `HARDENING_PRODUCTIZATION`) | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено, lane зафиксирован |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` (закрыт) | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено |
| Критично | `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW` (lane confirmed) | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнен: `public_launch_go=false`, продолжение на hardening lane |
| Критично | `AMN2_PHASE_9_FINAL_STATUS_REFRESH` | Codex-Spark | true | false | false | Завершён и подтверждён (`259b742`) |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW_GAP_TASKS_PREP` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: закрывает gap-prep и anti-loop rule |
| Критично | `AMN2_PHASE_9_CONFIG_DELIVERY_ENTRY_REVIEW` (если меняется lane в другой трек) | GPT-5.5 | false | true (`requires_model_switch`) | true (`CONFIG_DELIVERY_GATE_REVIEW` exact) | Подготовить review bundle и запуск exact gate |
| Критично | `AMN2_PHASE_9_DR_ENTRY_REVIEW` (если меняется lane в другой трек) | GPT-5.5 | false | true (`requires_model_switch`) | true (`RESTORE_IMPORT_DR_GATE_REVIEW` exact) | Подготовить DR-review и exact gate |
| Критично | `AMN2_PHASE_9_POST_SSH_AUTH_REVIEW_SYNC` | Codex-Spark | true | false | false | Выполнить post-sync синхронизацию статусов после завершения SSH auth hardening review |
| Очень важно | `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Проверить актуальность условий lane и stop-lines |
| Очень важно | `AMN2_PHASE_9_PUBLIC_GATE_PREP_REFRESH` (`PUBLIC_EXPOSURE_GATE_REVIEW` при выборе lane 1) | GPT-5.5 | false | true (`requires_model_switch`) | true (`PUBLIC_EXPOSURE_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_CONFIG_DELIVERY_GATE_PREP_REFRESH` (`CONFIG_DELIVERY_GATE_REVIEW` при lane 2) | GPT-5.5 | false | true (`requires_model_switch`) | true (`CONFIG_DELIVERY_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_DR_GATE_PREP_REFRESH` (`RESTORE_IMPORT_DR_GATE_REVIEW` при lane 4) | GPT-5.5 | false | true (`requires_model_switch`) | true (`RESTORE_IMPORT_DR` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` | Codex-Spark | true | false | false | Держать ограничения по статусу и hold-правила |
| Очень важно | `AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH` | Codex-Spark | true | false | false | Синхронизировать итоговый status после выбранного lane + review outcomes |
| Важно | `AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: validated после passed no-long-SSH result |
| Важно | `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: не blocker для hardening lane; execution только future exact gate |
| Важно | `AMN2_DB_AGGREGATE_COUNTS_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: optional-confidence-not-hardening-blocker; live counts только через future exact gate |
| Важно | `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: `DefaultVPN failed-no-tested-import-path`; future exact gate для любых iOS claims |
| Важно | `AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION` | GPT-5 | true | false | false | Выполнено docs-only, блоки сведены в единый hardening decision set |
| Просто | `NEXT_CHAT_AMN2_PHASE_9_SESSION` | Codex-Spark | true | false | false | Сгенерировать/актуализировать next-chat sync с выбранным lane |
| Просто | `AMN2_PHASE_9_TASK_MATRIX_REFRESH` | Codex-Spark | true | false | false | Завершён и обновлён после `AMN2_PHASE_9_FINAL_STATUS_REFRESH` |
| Просто | `PROJECT_STATUS_CURRENT.ru.md refresh` | Codex-Spark | true | false | false | Синхронизировать текущий статус, оставляя hold до exact gate |
| Просто | `SECRET_POLLUTION_SCAN` (скан на `.conf`, `token`, `private key`, `PSK`, `qr`, `vpn://`) | Codex-Spark | true | false | false | Выполнить перед любым следующим commit/push |

### Критичный gate-резюме до next chat

```text
critical_openers=AMN2_PHASE_9_HARDENING_ENTRY_REVIEW, AMN2_PHASE_9_ENTRY_DECISION
docs_only_openers=AMN2_PHASE_9_HARDENING_DOCS_PACKAGE, AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH, AMN2_HELPER_SSH_TRANSPORT_HARDENING, AMN2_HELPER_STYLE_HARDENING, AMN2_PHASE_9_FINAL_STATUS_REFRESH, AMN2_PHASE_9_TASK_MATRIX_REFRESH
live_openers=requires_operator_approval + exact_named_gate
post_review_sync_completed=AMN2_PHASE_9_POST_SSH_AUTH_REVIEW_SYNC
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Следующий шаг сейчас

- До operator-confirmed нового exact gate — `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
- На этом этапе GPT-5.5 выполняет только docs/review-only (без live/VPS/SSH/Telegram/public):
  - `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` при изменении входных условий;
  - повторный `AMN2_PHASE_9_TASK_MATRIX_REFRESH` при изменении статусов;
  - `AMN2_PHASE_9_FINAL_STATUS_REFRESH` при появлении новых фактов.
- Закрытые статусы по review:
  - `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`: `ssh_auth_hardening_execution=not-approved`, `future_exact_gate_required=true`.
  - `AMN2_DB_AGGREGATE_COUNTS_REVIEW`: `future_exact_gate_required_for_live_counts=true`.
  - `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW`: `ios_defaultvpn_status=failed-no-tested-import-path`, `public release claim deferred`.

## Правило по модели (соглашение с тобой)

- Если задача помечена `requires_model_switch=true`, сначала получаем явное подтверждение:
  `Подтверждаешь запускать задачу в GPT-5.5 или оставляем в Codex-Spark?`
