# AMN2 Phase 9 hardenings docs package — 2026-06-27

## Статус

Кодекс-Spark, статус: `completed-docs-only`.

## Цель

Подготовить комплект документов и research-артефактов для перехода в Phase 9 lane
`HARDENING_PRODUCTIZATION` после закрытия Private RC, без открытия live/VPS/SSH/Telegram/public
шагов.

## Вход

- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md` (выбран lane `HARDENING_PRODUCTIZATION`)
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH.ru.md`
- `docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md`

## Выполнено

Документы/пакетные артефакты, подготовленные в рамках hardening-диапазона:

- `docs/AMN2_HELPER_STYLE_HARDENING.ru.md`
- `docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`
- `docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`
- `docs/AMN2_TELEGRAM_OPERATION_RUNBOOK_POLISH.ru.md`
- `docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`
- `docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`
- `docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md`
- `docs/AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_DOCS_PACKAGE.ru.md`
- `docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md`

## Ключевые hardening-решения

- Для Telegram-операции подтверждена стратегия короткого окна без долгого SSH-сессирования:
  `PRIVATE_RC_TELEGRAM_OPERATION_NO_LONG_SSH_RETRY_GATE`.
- Для SSH: single-session/no-SCP/скрипт с LF-нормализацией как базовый приём.
- Для iOS: DefaultVPN failed/not accepted; config import has no tested working
  path; no iOS release/support/config-delivery claims without future exact gate.
- Для SSH auth-noise: observed heavy, but hardening execution not approved
  without future exact gate and rollback/provider-console boundary.
- Для DB aggregate counts: optional confidence, not a hardening blocker; live
  counts require future exact gate.
- Все пакеты выполнены в `docs-only` режиме для этого этапа; никаких payload или
  секретов в выходе.
- Блокировки на public launch / config delivery / peer creation / production rollout
  сохранены как `not-approved / not-proven` согласно Phase 8 ограничениям.

## Ограничения продолжения

```text
public_launch_status=not-approved
config_delivery_status=not-approved
peer_creation_status=not-approved
public_self_service_config_delivery_status=not-approved
telegram_profile_media_mutation_status=not-approved
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_rollout_status=not-approved
ios_defaultvpn_status=failed-not-accepted
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
```

## Непосредственный следующий шаг после hardening docs пакета

- По умолчанию: `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
- Любой live/external step: только после отдельного operator-confirmed exact
  named gate.
- `NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md` как единый handoff для
  следующей части с сохранением lane и stop-lines.
