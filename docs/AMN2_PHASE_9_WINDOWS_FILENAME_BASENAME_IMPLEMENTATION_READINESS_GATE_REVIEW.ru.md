# AMN2 Windows Filename/Basename Implementation Readiness Review

Модель: ChatGPT 5.3-Spark (docs-only).
Режим: docs-only read-only readiness + generator-code inventory.

## Задача

Подтвердить, что Phase 9 может перейти в слой `generator-code` по реализации
Windows filename/basename policy для naming-compatible клиентских настроек без
открытия live/VPS/SSH/config/Telegram/public gates.

## Фактические вводные (факты из последних решённых шагов)

- `canonical_naming=Neobyatnaya-AMNZ-N`
- `windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N`
- Android после import показывает `Сервер 1` как documented limitation.
- `execution_go=false`
- `config_generation=false`
- `config_delivery=false`
- `peer_creation=false`
- `live_vps_ssh_telegram_public=false`

## Содержание review

```text
review_name=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE
review_status=approved
scope=docs-only
next_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE
decision_status=APPROVED_FOR_DOCS_AND_READ_ONLY_READINESS
ready_for_generator_code_readiness=true
allowed_scope=doc_sync + read-only workspace inventory
forbidden_scope=live/VPS/SSH/config/Telegram/public gates; peer/config creation; config generation/delivery; secret payload output
pass_state=canonical filename/basename rule can be implemented where platform allows it
fail_state=не открывать execution-only gate без дополнительного точного запроса 5.5-моделью
```

## Что считаем pass для этого readiness

- Подтверждена стратегия `Windows filename/basename` как допустимое место реализации
  canonical naming.
- Имеется read-only точка, где формируется `config_filename` (см. inventory).
- Есть минимум один репозиторий/branch с кодом для последующей правки filename.
- Артефакты и next step фиксируются только в docs.

## Что считаем fail для этого readiness

- Отсутствие подтверждённого code-location до проведения actual implementation.
- Попытка выполнить live/VPS/SSH/config/Telegram/public изменения.
- Обработка как production naming при обнаружении `Сервер 1` без `manual rename` policy.
- Любой вывод secrets/keys/tokens/`.conf`/QR/`vpn://`/raw logs.

## Ограничения (не меняются)

- Не открывать live/VPS/SSH/config/Telegram/public gates без точного exact gate от модели 5.5.
- Не создавать peer/config.
- Не выполнять config generation/delivery, payload/secrets output.
- `execution_go=false` после фиксации readiness до нового exact gate.

## Что передаётся дальше

- `docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RUNBOOK.ru.md`
- `docs/AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_RESULT_TEMPLATE.ru.md`
- Инвентарная запись в `PROJECT_STATUS_CURRENT.ru.md`, `AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`,
  `NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md`.
