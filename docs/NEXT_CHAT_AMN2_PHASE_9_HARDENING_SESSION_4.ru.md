# Следующий чат: AMN2 Phase 9 — hardening session 4 (bridge handoff)

Дата: 2026-06-27.

## Текущий контур

- `Phase`: 9
- `lane`: `HARDENING_PRODUCTIZATION`
- `режим`: Codex-Spark (`docs-only`, no live steps)
- `default_hold`: `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`
- `status`: `docs-only-ready-for-operator-confirmation`
- `branch`: `codex-spark-phase9-docs-sync`
- `remote_sync`: `в sync с origin после push `aeeb539`

## Что уже зафиксировано

- Session 3 docs-only handoff/refresh обновлён под факт успешного push в origin.
- `AMN2_PHASE_9_HARDENING_SESSION_4_STATUS_REFRESH` подготовлен.
- `AMN2_PHASE_9_POST_SSH_AUTH_REVIEW_SYNC` выполнен: status matrix и final status синхронизированы после `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`.
- Обновлён `docs/PROJECT_STATUS_CURRENT.ru.md` с новым active next-chat (`SESSION_4`).
- `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`, `AMN2_DB_AGGREGATE_COUNTS_REVIEW`,
  `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` уже закрыты как docs-only-reviews и остаются в статусе
  optional/not-approved для hardening execution.

## Приоритеты (по модели по умолчанию)

- Критично
  1. Держать `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
  2. Не открывать live/VPS/SSH/Telegram/public шаги без свежего exact named gate.

- Очень важно
  1. Следующий live шаг — только после операторского подтверждения и корректной модели:
     - `GPT-5.5` для `requires_model_switch=true` задач (lane switch / exact gate выбор);
     - `Codex-Spark` для следующего docs-only follow-up, если gate ещё не запрошен.
  2. Перед следующим commit/push:
     - `git status --short --branch`,
     - `git diff --check`,
     - `SECRET_POLLUTION_SCAN`.

- Важно
  1. Обновить после следующего exact gate:
     - `AMN2_PHASE_9_FINAL_STATUS_REFRESH` или private analog bridge.
  2. Держать iOS claims ограниченными: `DefaultVPN failed-no-tested-import-path`.

- Просто
  1. Если нужно ускорить без твоего участия на этом контуре — можем продолжать только docs-only bridge-пакет.
  2. Любой запуск live-экшна — по exact gate-цепочке и только после подтверждения модели.

## Модельное исполнение

- `Codex-Spark` делает:
  - docs-only updates статусов и task matrix;
  - корректировки следующего handoff-цепочки;
  - commit/push pre-check и housekeeping.
- `requires_model_switch=true`:
  - `AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH` при изменении ограничений;
  - `AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH` с live evidence;
  - first exact hardening gate decision/argue-set.
- `requires_exact_named_gate=true`:
  - любые VPS/SSH/Telegram/public/config операции.

## Рекомендуемый следующий шаг

1. `WAIT` — `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
2. После подтверждения оператора:
   - выбрать один exact hardening gate:
     - `AMN2_SSH_AUTH_HARDENING_GATE_REVIEW`,
     - или `AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE`,
     - или `AMN2_IOS_ACCEPTANCE_GATE_REVIEW` (если решим закрывать iOS-кейс отдельно).
   - После нового exact gate выполнить соответствующий `*_POST_*_SYNC` и только потом следующий next-chat.

## Stop-lines на этом промежутке

- Не делать public launch, config delivery, peer creation, production rollout.
- Не открывать `sshd/config/firewall/keys/port` changes.
- Не выводить конфиг/QR/vpn/private key/PSK/token/password payloads.
- Не запускать service restart/start/stop без explicit exact gate.
