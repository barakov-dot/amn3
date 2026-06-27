# AMN2 Phase 9 entry decision

Дата: 2026-06-27.
Вход: `PRIVATE_RC_PHASE_8` финал + `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`.

```text
gate_name=AMN2_PHASE_9_ENTRY_DECISION
executor_model=GPT-5.5
decision=lane_selected
selected_lane=HARDENING_PRODUCTIZATION
decision_status=passed-with-defaults-preserved
```

## Краткое обоснование

Phase 8 private/operator RC закрыт с явными ограничениями:
- public launch = `not-approved`;
- config delivery = `not-approved`;
- peer creation = `not-approved`;
- production rollout = `not-approved`;
- public self-service = `not-approved`;
- Telegram profile/media mutation = `not-approved`;
- restore/import/provider rebuild = `not-proven`.

Поэтому как следующий шаг выбран lane:
`HARDENING_PRODUCTIZATION`.

Этот lane усиливает эксплуатацию и качество без перехода в публичные/конфиг-доставочные/раскатные изменения.

## Что разрешено в рамках выбранного lane

Разрешено (doc/review only):
- `SSH_AUTH_NOISE_MITIGATION_REVIEW`;
- `DB_AGGREGATE_COUNTS_REVIEW`;
- `TELEGRAM_OPERATION_RUNBOOK_POLISH`;
- `AMN2_PHASE_9_TASK_MATRIX_REFRESH` при изменении оценки риска;
- `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH`.

Запрещено:
- прямой public launch;
- config delivery / self-service configs;
- peer creation вне отдельного exact named gate;
- production rollout / restore / import / provider rebuild;
- Telegram profile/media mutation;
- Telegram polling/live send;
- package upload/apply/live VPS mutation без exact gate.

## stop lines на входе в hardening lane

До выполнения соответствующего exact gate из selected lane:
- никаких live/VPS/SSH/config/Telegram/public действий;
- никаких изменений firewall/sshd/auth/users/keys;
- никаких сервисных restarts кроме явно оговоренных в рамках отдельного hardening gate;
- никаких секретов в payload;
- никаких `.conf`, QR, `vpn://`, private key, PSK, token output.

## recommended next step

1. Подтвердить hold: до operator-confirmed exact gate продолжать только docs/review-only.
2. После подтверждения первого hardening exact gate:
   - выполнить его строго по отдельному `named gate`;
   - затем обновить `AMN2_PHASE_9_ENTRY_BRIEF` / `AMN2_PHASE_9_TASK_MATRIX_REFRESH`.
3. Подготовить `AMN2_PHASE_9_ENTRY_BRIEF_REFRESH` с итогом lane и обновлёнными стоп-линиями при любом изменении условий.

## Exact named gate status

```text
requires_exact_named_gate_for_live_steps=true
live_steps_deferred=true
next_later_gate_pending=operator_confirmed_hardening_exact_gate
```
