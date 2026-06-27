# AMN2 Phase 9 public launch entry review

Дата: 2026-06-27.
Модель решения: `GPT-5.5` (подтверждена в чате).
Статус: `completed-docs-only-review`.

Этот review подтверждает, что переход в lane `PUBLIC_LAUNCH_READINESS` на текущем шаге
некорректен по факту сохранённых ограничений Phase 8/Private RC.

## Решение

```text
gate_name=AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW
selected_phase9_lane=HARDENING_PRODUCTIZATION
review_status=blocked_pending_lane_change_request
public_launch_go=false
next_live_or_mutating_step_requires_exact_named_gate=true
```

### Итог

На текущем наборе evidence:
- `public_launch_status=not-approved` (из `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`);
- `config_delivery_status=not-approved`;
- `peer_creation_status=not-approved`;
- `production_rollout_status=not-approved`;
- `public_self_service_config_delivery_status=not-approved`;
- `telegram_profile_media_mutation_status=not-approved`;
- `restore_import_status=not-proven`;
- `provider_rebuild_status=not-proven`;
- `admin_telegram_ids_count_actual=2` при двух-ручном управлении, без расширенной self-service модели.

Следовательно: **lane остается `HARDENING_PRODUCTIZATION`**, пока не будет отдельного operator-решения
о смене `next_phase` и полного запуска public-lane gates/approvals.

## Основа решения

Использованные документы:

- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md`
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`

Ключевые источники:

```text
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
private_operator_rc_outcome=closed-with-explicit-limitations
telegram_private_operator_rc_status=passed-no-config-delivery
android_private_operator_rc_status=passed-manual-and-server-side
```

## Что разрешено до explicit lane-change approval

- docs/research/status updates;
- helper hardening пакеты;
- task matrix/next-chat sync refresh;
- local secret/payload policy checks;
- подготовка gate-review пакетов для любых альтернативных lane.

## Что запрещено до смены lane

- любые public exposure/публичные шаги;
- config generation/delivery;
- peer creation;
- Telegram polling/live send;
- Telegram profile/media mutation;
- package upload/apply и service restarts;
- restore/import/reboot/provider rebuild/release rollout;
- вывод payload/secrets (ключи, токены, PSK, `.conf`, QR, `vpn://`).

## Что требуется для перехода в PUBLIC_LAUNCH_READINESS

Если будет принято решение сменить lane:

1. зафиксировать новый `entry_decision` и обновить `AMN2_PHASE_9_ENTRY_DECISION`;
2. обновить `AMN2_PHASE_9_TASK_MATRIX_REFRESH`;
3. запустить отдельный `AMN2_PHASE_9_PUBLIC_GATE_PREP_REFRESH` (GPT-5.5, docs-only);
4. выполнить exact named gate `PUBLIC_EXPOSURE_GATE`;
5. после него обновить `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` и final status docs.

## Stop-lines для future public lane

- public launch и config delivery остаются `not-approved` до полного отдельного gate path;
- нельзя смешивать public launch с hardening controls в одном live step;
- без explicit `exact gate` и operator подтверждения никаких mutations на VPS/SSH/Telegram/public.

