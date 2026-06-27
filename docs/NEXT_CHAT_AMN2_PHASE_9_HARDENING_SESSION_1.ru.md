# Следующий чат: AMN2 Phase 9 — hardening session 1 (docs-only closeout)

Дата: 2026-06-27.

## Короткий старт

Сохраняем `Codex-Spark`-safe режим:

- Phase 9 lane: `HARDENING_PRODUCTIZATION`
- На текущий момент: docs-only + локальные проверки
- Операторское правило: `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`
- Live/VPS/SSH/Telegram/public actions доступны только после fresh exact gate

## Gate-резюме (это сессия)

```text
scope=AMN2_PHASE_9_HARDENING_DOCS_SYNC
status=docs-only-pass
gate_model=Codex-Spark
completed_items=AMN2_PHASE_9_HARDENING_DOCS_PACKAGE, AMN2_PHASE_9_ENTRY_DECISION, AMN2_PHASE_9_HARDENING_ENTRY_REVIEW, AMN2_IOS_ACCEPTANCE_DECISION_REVIEW, AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW, AMN2_DB_AGGREGATE_COUNTS_REVIEW, AMN2_PHASE_9_TASK_MATRIX_REFRESH
critical_statuses=public_launch_status=not-approved; config_delivery_status=not-approved; peer_creation_status=not-approved; production_rollout_status=not-approved; ios_defaultvpn_status=failed-not-accepted; ssh_auth_hardening_execution_approved=false; db_aggregate_counts_status=optional-confidence-not-hardening-blocker
model_contract=tasks marked "requires_model_switch=true" still need explicit GPT-5.5 confirmation
```

## Что подтверждено

- `docs/AMN2_PHASE_9_HARDENING_DOCS_PACKAGE.ru.md` обновлен и завершен.
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md` обновлен под реальный статус и привязку задач к моделям.
- `docs/PROJECT_STATUS_CURRENT.ru.md` обновлен на текущий срез hardening.
- `docs/NEXT_CHAT_AMN2_PHASE_9_IOS_DECISION.ru.md` и `docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md` остаются актуальными.
- Проход `SECRET_POLLUTION_SCAN` и `git diff --check` ранее выполнены в рамках `AMN2_PHASE_9_DOCS_SYNC_SECRET_SCAN_AND_COMMIT_PREP`.

## Что важно перед push/PR

### Локальные проверки (Spark-safe)

```bash
git status --short --branch
git diff --check
rg -n -e "BEGIN PRIVATE KEY|private key|PSK|token=|password=|vpn://|private key" docs/AMN2_* docs/NEXT_CHAT_AMN2_PHASE_9_*
```

### Предложение по коммиту

```bash
git add docs/AMN2_PHASE_9_DOCS_SYNC_SECRET_SCAN_AND_COMMIT_PREP.ru.md docs/AMN2_PHASE_9_HARDENING_DOCS_PACKAGE.ru.md docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md docs/PROJECT_STATUS_CURRENT.ru.md docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md docs/NEXT_CHAT_AMN2_PHASE_9_IOS_DECISION.ru.md docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_1.ru.md
git commit -m "Finalize AMN2 phase-9 hardening docs sync and status handoff"
git push
```

### Шаблон PR body (после push)

```text
### Что закрыто
- Закрыт hardening docs-sync phase 9: helper hardening + runbook polish + task matrix refresh
- Подтверждена модель-матрица исполнения (Codex-Spark vs GPT-5.5)
- Обновлен статус проекта и новый NEXT_CHAT handoff session 1
- Выполнен локальный контроль секретной утечки и diff/markup sanity

### Ключевые ограничения
- public launch / config delivery / peer creation / production rollout: not-approved
- iOS DefaultVPN не принят (no tested import path)
- Telegram/Live/SSH/VPS/Config/Public actions: только по exact gate
```

## Рекомендуемый next-step (безопасный)

- Остаемся на `ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА`.
- После подтверждения оператора/next exact gate: переход в live hardening gate (по выбранному lane) и затем отдельный `FINAL_STATUS_REFRESH` + обновление handoff.
