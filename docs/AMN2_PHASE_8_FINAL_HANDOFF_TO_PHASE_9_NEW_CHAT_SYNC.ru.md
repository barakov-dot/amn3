# AMN2 Phase 8 final handoff to Phase 9 new chat sync

Дата: 2026-06-27.
Модель: `Codex-Spark`.
Статус: `completed-docs-only-handoff-sync`.

Этот sync финально закрывает текущий чат как Phase 8 closeout/handoff и
готовит переход в новый чат для дальнейшей Phase 9 работы.

Live/VPS/SSH/config/Telegram/public gates этим документом не открывались.
Phase 9 execution/review дальше в этом чате не выполнялся. VPS/config/auth/
firewall/users/keys/ports не менялись. Secrets, keys, tokens, configs и raw
logs не выводились.

## Итоговая граница

```text
current_chat_closure=Phase 8 final closeout/handoff
phase8_final_status=launch-ready-with-explicit-limitations
phase8_private_operator_rc_status=completed
phase9_material_status=prepared-existing-material
phase9_continuation_chat_required=true
phase9_execution_in_current_chat=false
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Phase 8 завершена. Закрытый private/operator RC готов с явными ограничениями.
Дальнейшая Phase 9 работа переносится в новый чат.

## Phase 8 что доказано

Использован final closeout:

```text
closeout_doc=docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
android_private_operator_rc_proof=complete-with-explicit-limitations
third_party_android_phone_status=passed-manual-and-server-side
telegram_private_operator_rc_proof=passed-private-operator-no-config-delivery
telegram_no_long_ssh_retry_status=passed
db_runtime_path_classification=resolved-for-path-existence
ssh_key_based_access_status=passed
public_closed_probes_status=passed-closed-by-default
```

## Ограничения остаются

```text
public_launch_status=not-approved
public_exposure_status=closed-by-default
config_delivery_status=not-approved
peer_creation_status=not-approved
public_self_service_config_delivery_status=not-approved
production_rollout_status=not-approved
telegram_profile_media_mutation_status=not-approved
restore_import_status=not-proven
provider_rebuild_status=not-proven
ios_defaultvpn_status=failed-not-accepted
```

Без нового exact named gate нельзя выполнять live/VPS/SSH/config/Telegram/
public action, package upload/apply, service start/restart/stop, auth/firewall/
users/keys/ports changes, restore/import/reboot или provider action.

## Уже подготовленные Phase 9 материалы

Уже созданные и запушенные Phase 9 docs/commits остаются как prepared material.
Они не откатываются и не считаются ошибкой. В этом чате Phase 9 дальше не
развивается.

Актуальный pushed sync на ветке:

```text
branch=codex-spark-phase9-docs-sync
latest_pushed_commit=157685f
phase9_prepared_material_kept=true
```

Ключевые prepared docs:

- `docs/AMN2_PHASE_9_ENTRY_BRIEF.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_5.ru.md`

## Локальный not-committed draft

На момент handoff в workspace есть локальный untracked Phase 9 draft:

```text
untracked_phase9_draft=docs/AMN2_SSH_AUTH_HARDENING_GATE_REVIEW.ru.md
untracked_phase9_draft_status=not-committed-prepared-draft
include_in_phase8_commit=false
```

Этот draft не включается в Phase 8 handoff commit, чтобы не смешивать финальное
закрытие Phase 8 с новым Phase 9 hardening review. В новом Phase 9 чате его
можно либо принять как draft, либо пересоздать/перепроверить в Phase 9
контексте.

## Новый next-chat

```text
next_chat_handoff=docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md
recommended_new_chat_command=AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF
recommended_model_for_new_chat_start=GPT-5.5
spark_allowed_after_new_chat_start=true_for_docs_only_sync
```

## Stop-lines

До нового чата и нового exact gate:

- не открывать public launch;
- не делать config generation/delivery;
- не создавать peer/config;
- не запускать production rollout;
- не менять SSH/auth/firewall/users/keys/ports;
- не запускать Telegram polling/live send;
- не выполнять package upload/apply;
- не выполнять service restart/start/stop;
- не выполнять restore/import/reboot/provider action;
- не выводить `.conf`, QR, `vpn://`, private key, PSK, token/password или raw
  logs.

## Следующее действие

```text
recommended_next=AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF
where=new_chat
current_chat_action=closed-after-this-docs-only-sync
```
