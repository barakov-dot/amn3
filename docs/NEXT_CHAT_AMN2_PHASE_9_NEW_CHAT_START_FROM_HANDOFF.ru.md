# Следующий чат: AMN2 Phase 9 старт из Phase 8 handoff

Дата: 2026-06-27.

## Команда для нового чата

```text
AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF

Модель: GPT-5.5 для первого решения/выбора Phase 9 направления.
После стартового решения Codex-Spark можно использовать для docs-only sync.

Использовать:
- docs/AMN2_PHASE_8_FINAL_HANDOFF_TO_PHASE_9_NEW_CHAT_SYNC.ru.md
- docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md
- docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_5.ru.md

Не открывать live/VPS/SSH/config/Telegram/public gates без отдельного exact
named gate.
Не менять VPS/config/auth/firewall/users/keys/ports.
Не выводить secrets, keys, tokens, configs или raw logs.

Цель:
- принять Phase 8 как закрытую;
- принять уже подготовленные Phase 9 docs/commits как existing material;
- выбрать первый конкретный Phase 9 шаг или подтвердить hold;
- не повторять generic refresh без нового статуса;
- при необходимости отдельно решить судьбу локального draft:
  docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
```

## Стартовый контекст

```text
previous_chat_closure=Phase 8 final closeout/handoff
phase8_final_status=launch-ready-with-explicit-limitations
phase9_material_status=prepared-existing-material
branch=codex-spark-phase9-docs-sync
latest_known_pushed_commit=157685f
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Phase 8 закрыта для private/operator RC. Android private/operator proof,
Telegram no-long-SSH proof, DB path existence classification и key-based SSH
prep уже зафиксированы. Public launch, config delivery, peer creation и
production rollout не разрешены.

## Что уже подготовлено для Phase 9

- Entry brief и lane candidates.
- Hardening/productization lane materials.
- Helper no-long-SSH standards.
- SSH auth-noise review как future exact gate boundary.
- DB aggregate counts как optional-confidence future gate.
- iOS DefaultVPN acceptance как failed-no-tested-import-path, без release claim.

## Локальный draft

В предыдущем workspace мог остаться untracked draft:

```text
docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
```

В новом чате сначала проверить `git status --short --branch`. Если draft
существует, не коммитить автоматически: принять его только после Phase 9
контекстной проверки или пересоздать.

## Ограничения

Остается запрещено без exact gate:

- public launch/public exposure;
- config generation/delivery;
- peer creation;
- production rollout;
- SSH/auth/firewall/users/keys/ports changes;
- Telegram polling/live send;
- package upload/apply;
- service restart/start/stop;
- restore/import/reboot/provider action;
- `.conf`, QR, `vpn://`, private key, PSK, token/password или raw log output.

## Recommended first decision

```text
recommended_first_decision=confirm_or_reselect_phase9_lane
recommended_model=GPT-5.5
execution_go=false_until_exact_gate
```
