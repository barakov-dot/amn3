# AMN2 Phase 9 Task Matrix Refresh

Дата: 2026-06-27
Run type: docs-only

## Input evidence

- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`

## Result

Подготовлена обновленная task matrix для Phase 9 с:

- русской критичностью (Критично / Очень важно / Важно / Просто)
- рекомендованным исполнителем (`Codex-Spark` или `GPT-5.5`)
- флагами `Codex может делать сам`
- флагами `requires_model_switch`
- пометкой `requires_exact_named_gate`
- явным `recommended next step`.

Ключевое состояние после последующего refresh:

```text
phase9_entry_decision=passed
selected_lane=HARDENING_PRODUCTIZATION
hardening_entry_review=passed
ios_acceptance_decision_review=passed
ios_release_acceptance_status=deferred-not-hardening-blocker
ssh_auth_noise_mitigation_review=passed
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_review=passed
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
```

`AMN2_PHASE_9_ENTRY_DECISION` больше не является следующим шагом: lane уже
выбран. Следующие live/mutating шаги требуют нового operator-confirmed exact
named gate.

## Output artifacts

- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`
- `docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`
- `docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md`
- `docs/NEXT_CHAT_AMN2_PHASE_9_IOS_DECISION.ru.md`

## Post-condition

Текущий default:

- `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`;
- no live/VPS/SSH/config/Telegram/public action without exact named gate;
- iOS release/support/config-delivery claims are not approved;
- SSH auth hardening execution is not approved without future exact gate;
- DB aggregate counts are optional confidence and not a hardening blocker.
