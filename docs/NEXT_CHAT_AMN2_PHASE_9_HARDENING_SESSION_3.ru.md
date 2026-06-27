# Следующий чат: AMN2 Phase 9 — hardening session 3 (bridge handoff)

Дата: 2026-06-27.

## Текущий контур

- `Phase`: 9
- `lane`: `HARDENING_PRODUCTIZATION`
- `режим`: Codex-Spark (docs-only, no live steps)
- `default_hold`: `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`
- `status`: `docs-only-progress-continued`
- `branch`: `codex-spark-phase9-docs-sync`
- `remote_sync`: `commit выполнен, push не выполнен из‑за TLS/SSL handshake (schannel), требуется ручной повтор`

## Что уже зафиксировано

- `AMN2_PHASE_9_ENTRY_DECISION` — lane `HARDENING_PRODUCTIZATION` зафиксирован.
- `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` — выполнен.
- `AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW` — продолжение в hardening, public launch no-go.
- `AMN2_PHASE_9_DOCS_SYNC_SECRET_SCAN_AND_COMMIT_PREP` — локально чисто, без секретных артефактов.
- `AMN2_PHASE_9_HARDENING_DOCS_PACKAGE`, `AMN2_PHASE_9_TASK_MATRIX_REFRESH`, `AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION` — выполнены.
- `AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH` и связанная закрывающая документация phase 8/9 уже учтены в `docs/PROJECT_STATUS_CURRENT.ru.md`.

## Приоритеты (по модели по умолчанию)

- Критично
  1. Держать `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА` до next exact gate.
  2. Не выполнять ни одного live-экшна (VPS/SSH/Telegram/public/config) без свежего exact named gate.

- Очень важно
  1. Перед каждым следующим commit/push выполнить:
     - `git status --short --branch`
     - `git diff --check`
     - `SECRET_POLLUTION_SCAN` для phase-целевой зоны.
  2. Подготовить and согласовать следующий `requires_model_switch=true` шаг (если появится).

- Важно
  1. `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` — обновить ограничения, если изменятся условия lane.
  2. `AMN2_PHASE_9_PRIVATE_FINAL_*` (при необходимости) — финально зафиксировать завершение сессии в соответствии с новым доказательным срезом.

- Просто
  1. Сформировать чистый `NEXT_CHAT_AND_PUSH` только после твого подтверждения model-flow.
  2. После нового exact gate — вернуться в live lane и оформить `FINAL_STATUS` bridge на основе того же hold.

## Модельное исполнение

- `Codex-Spark` делает:
  - docs-only обновления статуса и task matrix
  - scan/commit-prep без live команд
  - шаблоны next-chat и clean-room handoff
- `requires_model_switch=true` для:
  - новых entry decisions
  - смены lane
  - выбора/аргументации будущего live lane
- `requires_exact_named_gate=true`:
  - любые live VPS/SSH/Telegram/public/config operations

## Открытые блокеры после закрытия документации

- `public_launch_status=not-approved`
- `config_delivery_status=not-approved`
- `peer_creation_status=not-approved`
- `production_rollout_status=not-approved`
- `telegram_profile_media_mutation_status=not-approved`
- `ios_defaultvpn_status=failed-not-accepted`
- `ssh_auth_hardening_execution_approved=false` (ждет будущего exact gate)
- `db_aggregate_counts_status=optional-confidence-not-hardening-blocker` (ждет future exact gate)

## Рекомендованный следующий шаг

1. `NEXT_CHAT_AND_PUSH` (если требуется) после подтверждения текущего шага и проверки, что рабочий tree clean.
2. Ждать operator confirmation для exact hardening gate.
3. После подтверждения — начать тот single/paired exact gate, который ты выберешь первым:
   - `AMN2_SSH_AUTH_HARDENING_GATE_REVIEW` (если идем в SSH hardening lane)
   - или `AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE_REVIEW`
   - или `AMN2_IOS_ACCEPTANCE_GATE_REVIEW` (по необходимости).

## Stop-lines на этом промежутке

- Не делать public launch, peer creation, config delivery, production rollout.
- Не трогать `sshd/auth/firewall/keys/port`.
- Не выводить конфиг/QR/vpn/private key/PSK/token/password payloads.
- Не запускать service restart/start/stop без explicit exact gate и явного сценария.
