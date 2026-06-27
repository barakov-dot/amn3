# Следующий чат: AMN2 Phase 9 старт из Phase 8 handoff

Дата: 2026-06-27.

## Команда для нового чата

```text
AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF

Модель: ChatGPT 5.5 для первого решения/выбора Phase 9 направления.
После стартового решения ChatGPT 5.3-Spark можно использовать для docs-only
sync, status/matrix refresh, handoff и commit/push.

Использовать:
- docs/AMN2_PHASE_8_FINAL_HANDOFF_TO_PHASE_9_NEW_CHAT_SYNC.ru.md
- docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md
- docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md
- docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md
- docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md

Не открывать live/VPS/SSH/config/Telegram/public gates без отдельного exact
named gate.
Не менять VPS/config/auth/firewall/users/keys/ports.
Не выводить secrets, keys, tokens, configs или raw logs.

Цель:
- принять Phase 8 как закрытую;
- принять уже подготовленные Phase 9 docs/commits как existing material;
- выбрать первый конкретный Phase 9 шаг или подтвердить hold;
- оценить близость Phase 9 к закрытому self/operator config release, не к
  public release;
- добавить обязательную naming-доработку:
  config/device name follows `Neobyatnaya-AMNZ-N`;
- отдельно разобрать app display-name issue:
  imported profile/server currently appears as `SERVER1`, and Phase 9 must
  determine whether Android AmneziaWG takes display name from filename,
  device name, profile metadata, or app default;
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
latest_known_pre_sync_commit=5bcbbc4
private_self_config_readiness_with_naming_review=passed
ssh_auth_hardening_gate_review=passed-docs-only
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
- Private self-config readiness with naming review:
  `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md`.
  Первый трек подтвержден как `PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING`,
  но execution/config generation/import остаются закрыты до exact gate.
- SSH auth hardening review:
  `docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md`. Review passed docs-only;
  execution approved now: false.
- Android display-name gate package docs:
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md`
  Все три docs-only артефакта подготовлены.

## Обязательная naming-граница для config/self-use

Phase 9 должна считать `Neobyatnaya-AMNZ-N` не примером и не обходным путем, а
canonical naming policy для private/self/operator configs.

```text
canonical_config_device_name=Neobyatnaya-AMNZ-N
config_filename_policy=Neobyatnaya-AMNZ-N.conf
do_not_use_generic_names=true
forbidden_generic_names=SERVER1,server1,third-party-android-device-N,android-device-N
app_display_name_issue=SERVER1_observed_after_import
display_name_acceptance_required=true
server1_classification=client-display-name-product-compatibility-gap
android_display_name_future_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
```

Важно разделить два слоя:

- имя config/device/file должно формироваться как `Neobyatnaya-AMNZ-N`;
- имя, которое видит пользователь в Android AmneziaWG после import, должно быть
  проверено отдельно. Если клиент игнорирует filename и показывает `SERVER1`,
  Phase 9 должна зафиксировать это как client display-name gap и выбрать
  следующий вариант: filename/import-path fix, metadata-compatible fix или
  manual rename instruction as fallback.

Первый Phase 9 практический трек должен быть ближе к private self-config
readiness, а не к public launch:

```text
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
first_track_review_status=passed-docs-only
public_launch_go=false
public_self_service_go=false
config_for_everyone_go=false
self_operator_config_review_required=true
private_self_config_execution_go=false
```

## Разделение задач по моделям

`ChatGPT 5.5`:

- выбирает Phase 9 lane и первый exact gate;
- решает, разрешать ли private self-config generation/handoff review;
- формирует risk/rollback/pass-fail/stop-lines для live/config gates;
- принимает решение по `SERVER1` display-name problem как product/compatibility
  issue;
- решает, нужен ли execution gate или только docs/local implementation prep.

`ChatGPT 5.3-Spark`:

- делает docs-only sync, status refresh, task matrix, NEXT_CHAT;
- готовит runbook/checklist после решения `ChatGPT 5.5`;
- делает local-only code/doc prep только без live/VPS/SSH/Telegram/public gate;
- выполняет safe scan, diff check, commit/push для docs-only changes;
- не принимает рискованные решения и не открывает exact gates сам.

## Локальный draft

В предыдущем workspace оставался untracked draft:

```text
docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
```

В этом sync он принят как docs-only review material. Он не открывает SSH/auth
execution и не разрешает mutation. Любая реальная SSH hardening execution
требует отдельный exact gate `AMN2_SSH_AUTH_HARDENING_EXECUTION_GATE`.

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

## Current recommended decision

```text
recommended_first_decision=completed-docs-only
recommended_model_for_risk_decision=ChatGPT 5.5
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
next_safe_docs_step=done-by-spark-sync
android_display_name_gate_docs_prep=completed
execution_go=false_until_exact_gate
next_execution_candidate_if_operator_requests=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
