# Runbook: AMN2 private self-config execution package prep (docs-only)

Дата: 2026-06-28.
Статус: `prepared-docs-only`.

## Назначение

Подготовить docs-only пакет для следующего шага:
`AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE`.

Решение 5.5 уже принято:
`APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY` (`execution_go=false`, `config_generation=false`,
`config_delivery=false`, `peer_creation=false`, `live_vps_ssh_telegram_public=false`).

## Что включает пакет

- `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_READINESS_GATE_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RUNBOOK.ru.md` (этот файл)
- `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_RESULT_TEMPLATE.ru.md`

## Разрешённые действия (подготовка пакета)

1. Обновить только документацию: review / runbook / result template / статусы.
2. Заполнить `PROJECT_STATUS_CURRENT.ru.md`.
3. Обновить `AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`.
4. Обновить `NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md`.
5. Сделать `safe scan` и `git diff --check`.
6. При разрешении пользователем сделать `commit/push`.

## Запрещено на этом этапе

- Любой `live/VPS/SSH/Telegram/public` action.
- Любая попытка `peer creation`.
- `config_generation` / `config_delivery`.
- Любой вывод `payload`/`secrets`/raw values
  (`.conf`, `QR`, `vpn://`, `private key`, `PSK`, `token`, `password`, `raw logs`).

## Проверки для review-пакета

Перед финализацией package-prep зафиксировать в review:

```text
canonical_naming=Neobyatnaya-AMNZ-N
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE
decision_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY
```

## Шаблон operator prompt для следующего exact gate

Если оператор запрашивает следующий exact gate для execution package:

```text
Модель: ChatGPT 5.5
Контекст: execution package Phase 9 готов.
Требуется проверить готовность execution package scope и следующий exact gate.
Контрольный статус: decision_status=APPROVED_FOR_EXECUTION_PACKAGE_PREP_ONLY, next_gate=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_EXECUTION_PACKAGE_PREP_GATE.
Критичные границы: execution_go=false, no_live_vps_ssh_telegram_public, no_peer_creation, no_config_generation, no_config_delivery, no_payload_or_secret_output.
Ожидаю подтверждение на execution_readiness_package scope и risk model.
По результату верни: pass/fail/stop-lines + allowed next sub-gate.
```

## Safe summary после prep

```text
phase9_private_self_config_execution_package_prep=ready
docs_bundle_prepared=true
review_result_ready=true
operator_prompt_ready=true
forbidden_actions_performed=false
sync_targets=PROJECT_STATUS_CURRENT|TASK_MATRIX_REFRESH|NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF
```
