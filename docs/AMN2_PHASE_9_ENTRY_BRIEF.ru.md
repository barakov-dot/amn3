# AMN2 Phase 9 entry brief

Дата: 2026-06-27.

Статус: `prepared-docs-only`.

Этот brief готовит вход в следующую фазу после закрытия Phase 8
private/operator RC. Live/VPS/SSH/config/Telegram/public gates не открывались.

## Откуда стартуем

```text
previous_phase=Phase 8 private/operator RC
previous_phase_status=closed-launch-ready-with-explicit-limitations
target_vps=89.185.80.166
amn2_runtime_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
android_proof=complete-with-explicit-limitations
telegram_proof=completed-no-config-delivery
public_launch_status=not-approved
config_delivery_status=not-approved
production_rollout_status=not-approved
```

## Выбор lane для следующей фазы

### Критично

Выбрать один главный lane, чтобы не смешивать несовместимые риски:

```text
lane_1=PUBLIC_LAUNCH_READINESS
lane_2=CONTROLLED_CONFIG_DELIVERY
lane_3=HARDENING_PRODUCTIZATION
lane_4=DR_RELIABILITY
```

### Очень важно

Если цель - публичный запуск:

```text
next_phase_recommended_lane=PUBLIC_LAUNCH_READINESS
must_prepare_review=PUBLIC_EXPOSURE_GATE_REVIEW
must_keep_config_delivery_separate=true
must_keep_production_rollout_separate=true
```

Если цель - выдавать конфиги пользователям:

```text
next_phase_recommended_lane=CONTROLLED_CONFIG_DELIVERY
must_prepare_review=CONFIG_DELIVERY_GATE_REVIEW
must_keep_public_exposure_separate=true
payload_output_allowed=false
```

Если цель - укрепить эксплуатацию:

```text
next_phase_recommended_lane=HARDENING_PRODUCTIZATION
candidate_reviews=SSH_AUTH_NOISE_MITIGATION_REVIEW,DB_AGGREGATE_COUNTS_REVIEW,TELEGRAM_OPERATION_RUNBOOK_POLISH
live_mutation_required=false_by_default
```

Если цель - надежность и восстановление:

```text
next_phase_recommended_lane=DR_RELIABILITY
must_prepare_review=RESTORE_IMPORT_DR_GATE_REVIEW
destructive_execution_go=false_until_explicit_gate
```

## Рекомендуемый default

```text
recommended_default=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
recommended_decision_gate=AMN2_PHASE_9_ENTRY_DECISION
```

## Copy/paste decision gate

```text
AMN2_PHASE_9_ENTRY_DECISION

Использовать Phase 8 final closeout evidence.
Не открывать live/VPS/SSH/config/Telegram/public gates.
Выбрать один lane для следующей фазы:
- PUBLIC_LAUNCH_READINESS;
- CONTROLLED_CONFIG_DELIVERY;
- HARDENING_PRODUCTIZATION;
- DR_RELIABILITY.

Подготовить review bundle для выбранного lane:
- цель;
- blockers;
- stop-lines;
- exact execution gate names;
- что можно делать docs-only;
- что требует отдельного live gate.

Ничего не выполнять live без отдельного exact named gate.
```

## Стоп-линии на входе в Phase 9

До выбора lane и отдельного gate нельзя:

- открывать public exposure;
- выполнять config generation/delivery;
- создавать peer/config;
- запускать Telegram polling/live send;
- менять Telegram profile/media;
- выполнять package upload/apply;
- менять firewall/sshd/auth/users/keys;
- выполнять restore/import/reboot/provider rebuild;
- начинать production rollout;
- выводить payload/secrets.
