# AMN2 Phase 9 task matrix refresh

Дата: 2026-06-27
Статус: `completed-docs-only-task-matrix`
Основа: `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`, `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`.

Текущее состояние на 2026-06-27:

```text
phase9_entry_decision=passed
selected_lane=HARDENING_PRODUCTIZATION
hardening_entry_review=passed
public_launch_entry_review=completed_no_go_stay_in_hardening
public_launch_go=blocked
ios_acceptance_decision_review=passed
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ssh_auth_noise_mitigation_review=passed
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_review=passed
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
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

### Обновление после текущего блока (2026-06-27, Spark)

- `AMN2_PHASE_9_HARDENING_DOCS_PACKAGE` и `AMN2_PHASE_9_DOCS_SYNC_SECRET_SCAN_AND_COMMIT_PREP` — `completed-docs-only`, исполнитель `Codex-Spark`, без смены модели.
- `AMN2_PHASE_9_ENTRY_DECISION` / `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` — зафиксированы как `done`, исполнитель `GPT-5.5`, требуется подтвердить модель для повторного открытия/изменения.
- `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW` — выполнен как `completed-docs-only-no-go`, executor `GPT-5.5`; lane не меняется, продолжение на `HARDENING_PRODUCTIZATION`.
- Для дальнейших шагов в этой фазе продолжаем в этой сессии правило: по умолчанию выполняются только tasks с `Codex-Spark` + review/status sync (см. блок ниже `requires_model_switch`).

Короткое правило по моделям (после каждого блока):

```text
Spark-first задачи: docs/research/status обновления, helper-standards, helper hardening packages, обновление task matrix и next-chat.
GPT-5.5 задачи: новые entry-decisions, смена lane, policy/approach сдвиги, аргументация live gate selection.
Если в задаче `requires_model_switch=true` — просить подтверждение модели явно.
```

| Критичность | Задача | Рекомендуемый исполнитель | Codex может делать сам | Что требует согласия/переключения модели | Что требует exact named gate | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| Критично | `AMN2_PHASE_9_ENTRY_DECISION` (lane уже выбран: `HARDENING_PRODUCTIZATION`) | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено, lane зафиксирован |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` (закрыт) | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено |
| Критично | `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнен: `public_launch_go=false`, продолжение на hardening lane |
| Критично | `AMN2_PHASE_9_CONFIG_DELIVERY_ENTRY_REVIEW` (если меняется lane в другой трек) | GPT-5.5 | false | true (`requires_model_switch`) | false | Подготовить `CONFIG_DELIVERY_GATE_REVIEW`, затем exact gate для controlled delivery |
| Критично | `AMN2_PHASE_9_DR_ENTRY_REVIEW` (если меняется lane в другой трек) | GPT-5.5 | false | true (`requires_model_switch`) | false | Подготовить DR-review и exact `RESTORE_IMPORT_DR_GATE_REVIEW` |
| Очень важно | `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Проверить актуальность условий lane и stop-lines |
| Очень важно | `AMN2_PHASE_9_PUBLIC_GATE_PREP_REFRESH` (`PUBLIC_EXPOSURE_GATE_REVIEW` при выборе lane 1) | GPT-5.5 | false | true (`requires_model_switch`) | true (`PUBLIC_EXPOSURE_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_CONFIG_DELIVERY_GATE_PREP_REFRESH` (`CONFIG_DELIVERY_GATE_REVIEW` при lane 2) | GPT-5.5 | false | true (`requires_model_switch`) | true (`CONFIG_DELIVERY_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PHASE_9_DR_GATE_PREP_REFRESH` (`RESTORE_IMPORT_DR_GATE_REVIEW` при lane 4) | GPT-5.5 | false | true (`requires_model_switch`) | true (`RESTORE_IMPORT_DR_GATE` exact) | Подготовить review bundle и запуск exact gate |
| Очень важно | `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` | Codex-Spark | true | false | false | Обновить ограничения после выбранного lane и статуса |
| Очень важно | `AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH` | Codex-Spark | true | false | false | Уточнить итоговый статус после выбранного lane + review outcomes |
| Важно | `AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH` | GPT-5.5 | false | true (`requires_model_switch`) | false | Привести runbook в соответствие с no-long-SSH approach |
| Важно | `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: не blocker для current lane; execution только future exact gate |
| Важно | `AMN2_DB_AGGREGATE_COUNTS_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: optional-confidence-not-hardening-blocker; live counts only via future exact gate |
| Важно | `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` | GPT-5.5 | false | true (`requires_model_switch`) | false | Выполнено: iOS DefaultVPN failed-not-accepted; no tested config import path; future exact gate required for any iOS claims |
| Просто | `NEXT_CHAT_AMN2_PHASE_9_SESSION` | Codex-Spark | true | false | false | Сгенерировать next-chat sync с выбранным lane |
| Просто | `AMN2_PHASE_9_TASK_MATRIX_REFRESH` | Codex-Spark | true | false | false | Обновить в случае изменения риска/приоритетов и при следующем чекпоинте |
| Просто | `PROJECT_STATUS_CURRENT.ru.md refresh` | Codex-Spark | true | false | false | Синхронизировать текущий статус, оставив hold при отсутствии exact gate |
| Просто | `SECRET_POLLUTION_SCAN` (скан на `.conf`, `token`, `private key`, `PSK`, `qr`, `vpn://`) | Codex-Spark | true | false | false | Выполнить перед каждым commit / push |

### Критичный gate-резюме до next chat

```text
critical_openers=AMN2_PHASE_9_HARDENING_ENTRY_REVIEW, AMN2_PHASE_9_ENTRY_DECISION
docs_only_openers=AMN2_PHASE_9_HARDENING_DOCS_PACKAGE, AMN2_PHASE_9_TELEGRAM_OPERATION_RUNBOOK_POLISH, AMN2_HELPER_SSH_TRANSPORT_HARDENING, AMN2_HELPER_STYLE_HARDENING
live_openers=requires_operator_approval + exact_named_gate
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Следующий шаг сейчас

- До operator-confirmed нового exact gate — `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
- На этом этапе GPT-5.5 может выполнять только docs/review-only задачи (без live/VPS/SSH/Telegram/public):
  - `AMN2_PHASE_9_ENTRY_BRIEF_REVIEW` при изменении исходных условий;
  - `AMN2_PHASE_9_ENTRY_REVIEW`/`AMN2_PHASE_9_TASK_MATRIX_REFRESH` refresh.
- `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` закрыт:
  `ssh_auth_noise_observed=true`,
  `ssh_auth_hardening_execution_approved=false`,
  `ssh_auth_hardening_future_exact_gate_required=true`.
- `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` закрыт:
  `ios_defaultvpn_status=failed-not-accepted`,
  `ios_defaultvpn_config_import_status=failed-no-tested-import-path`,
  `ios_release_acceptance_status=deferred-not-hardening-blocker`.
- `AMN2_DB_AGGREGATE_COUNTS_REVIEW` закрыт:
  `db_aggregate_counts_status=optional-confidence-not-hardening-blocker`,
  `future_exact_gate_required_for_live_counts=true`.

## Правило по модели (соглашение с тобой)

- Если задача помечена `requires_model_switch=true`, сначала получаем явное подтверждение:
  `Подтверждаешь запускать эту задачу в GPT-5.5 или оставляем в Codex-Spark?`
