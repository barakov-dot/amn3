# AMN2 Phase 9 hardening entry review gap tasks prep

Дата: 2026-06-27.
Модель: `GPT-5.5`.
Статус: `completed-docs-only-review`.

Этот документ закрывает подтвержденный `requires_model_switch=true` шаг
`AMN2_PHASE_9_HARDENING_ENTRY_REVIEW_GAP_TASKS_PREP`. Live/VPS/SSH/config/
Telegram/public gates не открывались.

## Scope

```text
task=AMN2_PHASE_9_HARDENING_ENTRY_REVIEW_GAP_TASKS_PREP
selected_lane=HARDENING_PRODUCTIZATION
review_only=true
live_execution_go=false
vps_ssh_telegram_public_gate_opened=false
config_delivery_go=false
peer_creation_go=false
production_rollout_go=false
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Что уже закрыто и не должно повторяться

Закрыто:
- `AMN2_PHASE_9_ENTRY_DECISION`: lane выбран как `HARDENING_PRODUCTIZATION`.
- `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW`: hardening lane разрешен только как
  docs/review/local-only контур.
- `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW`: public launch остается `blocked`.
- `AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION`: SSH auth hardening execution,
  DB live counts и iOS claims сведены в отдельные future-gate правила.
- `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`: execution не approved.
- `AMN2_DB_AGGREGATE_COUNTS_REVIEW`: optional confidence, не blocker.
- `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW`: iOS DefaultVPN failed-no-tested-import-path.
- `AMN2_PHASE_9_FINAL_STATUS_REFRESH` и `AMN2_PHASE_9_TASK_MATRIX_REFRESH`:
  актуальный статус и модельная матрица синхронизированы.

Не повторять без новых фактов:
- очередной generic final refresh;
- очередной task matrix refresh;
- новый next-chat только ради движения номера сессии;
- повторный review already-closed SSH/DB/iOS блоков.

## Реальные gaps

| Критичность | Gap | Исполнитель | Можно делать сейчас | Exact gate нужен | Решение |
| --- | --- | --- | --- | --- | --- |
| Критично | Первый конкретный hardening gate еще не выбран оператором | `GPT-5.5` | только review | true для execution | Подготовить один gate-review, не запускать execution |
| Критично | Любой live/VPS/SSH/Telegram/public шаг остается неавторизованным | оператор + exact gate | false | true | Держать hold |
| Очень важно | Telegram runbook нужно привести к no-long-SSH standard | `GPT-5.5` или `Codex-Spark` после review | done | false | Закрыто: runbook validated после passed no-long-SSH result |
| Очень важно | Helper standards должны запрещать long SSH/manual window внутри SSH | `Codex-Spark` | true | false | Уже частично закрыто, обновлять только при новых helper требованиях |
| Важно | iOS acceptance не имеет рабочего DefaultVPN path | `GPT-5.5` | review-only | true для claims/testing | Не делать release claim по iOS |
| Важно | SSH auth-noise mitigation не должен смешиваться с private RC closeout | `GPT-5.5` | review-only | true для execution | Future exact gate only |

## Anti-loop rule

```text
do_not_create_more_status_docs_unless_status_changes=true
next_docs_step_must_close_specific_gap=true
next_live_step_requires_exact_named_gate=true
spark_can_continue_only_if_task_is_docs_only_and_specific=true
model_switch_required_for_lane_or_gate_selection=true
```

Практически: если следующий шаг не меняет статус, не выбирает конкретный gate и
не закрывает конкретный runbook/helper gap, его не делаем.

## Recommended next step

```text
recommended_next=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
recommended_model=GPT-5.5
reason=all_current_docs_only_gaps_closed_or_future_exact_gate_bound
live_gate_required=false
```

Если оператор хочет идти к первому live hardening шагу, следующий docs-only
review-кандидат:

```text
candidate_next=AMN2_SSH_AUTH_HARDENING_GATE_REVIEW
recommended_model=GPT-5.5
execution_gate_required_after_review=true
live_execution_go=false
```

## Stop-lines

Без отдельного exact named gate нельзя:
- открывать public exposure;
- выполнять config generation/delivery;
- создавать peer/config;
- запускать Telegram polling/live send;
- выполнять package upload/apply;
- менять firewall/sshd/auth/users/keys;
- выполнять service start/restart/stop;
- выполнять restore/import/reboot/provider rebuild;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выводить raw DB rows, raw `wg dump`, raw process list, raw server logs.
