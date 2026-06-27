# Следующий чат: AMN2 Phase 9 старт из Phase 8 handoff

Дата: 2026-06-27.

## Команда для нового чата

```text
AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF

Модель: ChatGPT 5.3-Spark для текущего docs-only синхрона после решения.
ChatGPT 5.5 используется только для отдельного exact gate (`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`) по запросу оператора.

Порядок выполнения для docs-only Spark-потока (по состоянию на этот handoff):
`NEXT_CHAT` -> `safe-scan` -> `git diff --check` -> `commit/push`,
только если в процессе синка появился новый артефакт для синхронизации в
`PROJECT_STATUS_CURRENT` / `AMN2_PHASE_9_TASK_MATRIX_REFRESH` /
`NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF`.

Использовать:
- docs/AMN2_PHASE_8_FINAL_HANDOFF_TO_PHASE_9_NEW_CHAT_SYNC.ru.md
- docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md
- docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md
- docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md
- docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
- docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md
- docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md

Не открывать live/VPS/SSH/config/Telegram/public gates без отдельного exact
named gate.
Не менять VPS/config/auth/firewall/users/keys/ports.
Не выводить secrets, keys, tokens, configs или raw logs.

Цель:
- принять Phase 8 как закрытую;
- принять уже подготовленные Phase 9 docs/commits как existing material;
- принять решение 5.5 по `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE` и
  закрепить его в `status/matrix/next-chat`.
- оценить близость Phase 9 к закрытому self/operator config release, не к
  public release;
- добавить обязательную naming-доработку:
  имя config/device должно быть `Neobyatnaya-AMNZ-N`;
- отдельно разобрать проблему названия профиля в приложении:
  после import профиль/сервер сейчас отображается как `SERVER1`; надо определить,
  берёт ли Android AmneziaWG имя из filename, имени device, metadata или
  из дефолтного поведения app;
- зафиксировать решение 5.5: pass=`Neobyatnaya-AMNZ-N`, `SERVER1` — это только
  client display-name compatibility gap с fallback `manual rename`, всё остальное
  generic/name/fail.
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
android_display_name_gate_decision=passed_with_documented_limitation
android_display_name_gate_execution_go=false
android_display_name_next_step=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА_OR_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_observed_display_name=Сервер_1
windows_amneziawg_display_name_strategy=filename_basename
android_ios_display_name_strategy=manual_rename_fallback_until_supported_or_proven
ssh_auth_hardening_gate_review=passed-docs-only
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
current_model=ChatGPT 5.3-Spark
spark_docs_only_sync_mode=NEXT_CHAT_safe_scan_diffcheck_commit_push
spark_docs_only_sync_scope=PROJECT_STATUS_CURRENT_and_TASK_MATRIX_REFRESH_and_NEXT_CHAT
phase9_platform_display_name_implementation_readiness_doc=docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md
phase9_platform_display_name_implementation_next=generator_code_docs_ready
android_display_name_gate_result=DOCUMENTED_LIMITATION
android_display_name_gate_observed=Сервер 1
android_display_name_gate_next=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА_OR_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
execution_go_after_gate_result=false
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
  Первый трек подтвержден как `PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING`.
  `execution_go=false` до operator-confirmed exact gate.
- SSH auth hardening review:
  `docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md`. Review passed docs-only;
  execution approved now: false.
- Android display-name gate package docs:
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE_REVIEW.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RUNBOOK.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT_TEMPLATE.ru.md`
  - `docs/AMN2_ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_RESULT.ru.md`
  Docs-only артефакты и safe result подготовлены. Решение 5.5:
  pass=`Neobyatnaya-AMNZ-N`,
  limitation=`SERVER1`/`Сервер 1` documented с fallback `manual rename`,
  fail=`generic/production naming или payload/secrets action`.
- Platform display-name policy:
  Windows AmneziaWG standalone: реализуем через filename/basename
  `Neobyatnaya-AMNZ-N.conf`.
  Android/iOS Amnezia app: automatic display-name из `.conf` не доказан,
  оставляем `manual rename` fallback.
  Safe observation: `Observed display name = Сервер 1`.
  Implementation readiness handoff prepared: `docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md`.

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
android_display_name_pass=Neobyatnaya-AMNZ-N
android_display_name_documented_limitation=SERVER1_or_Сервер_1_as_client_display_name_gap_with_manual_rename_fallback
android_display_name_fail=generic_name_or_filename|payload_secrets_output|peer_config_public_self_service_action
android_display_name_execution_go=false
windows_amneziawg_display_name_strategy=filename_basename
windows_amneziawg_required_filename=Neobyatnaya-AMNZ-N.conf
android_display_name_strategy=manual_rename_fallback
ios_display_name_strategy=not_proven_manual_rename_fallback
```

Важно разделить два слоя:

- имя config/device/file должно формироваться как `Neobyatnaya-AMNZ-N`;
- имя, которое видит пользователь в Android AmneziaWG после import, должно быть
  проверено отдельно. Если клиент игнорирует filename и показывает `SERVER1` или
  `Сервер 1`,
  Phase 9 зафиксировала это как client display-name gap и фиксирует fallback
  `manual rename`.
- где можно задать имя без изменения payload, закладываем реализацию: для
  Windows AmneziaWG standalone это filename/basename `Neobyatnaya-AMNZ-N.conf`.
- для Android/iOS Amnezia app автоматическое display-name из `.conf` не
  подтверждено; оставляем documented limitation.

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

## Текущее рекомендованное решение

```text
recommended_first_decision=post_decision_sync_completed
recommended_model_for_risk_decision=ChatGPT 5.5
recommended_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
next_safe_docs_step=done-by-spark-sync
android_display_name_gate_decision=passed
android_display_name_gate_pass=Neobyatnaya-AMNZ-N
android_display_name_gate_documented_limitation=SERVER1_or_Сервер_1_client_display_name_gap_with_manual_rename_fallback
android_display_name_gate_fail=generic_name_or_filename_or_payload_or_peer_public_action
android_display_name_gate_result=Сервер_1_documented_limitation
windows_amneziawg_next=implement_filename_basename_policy
android_ios_next=keep_manual_rename_fallback
execution_go=false_until_operator_exact_gate
next_execution_candidate_if_operator_requests=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
