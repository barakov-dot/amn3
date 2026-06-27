# AMN2 Phase 9 hardening entry review

Дата: 2026-06-27.
Модель: `GPT-5.5`.
Статус: `completed-docs-only-review`.

Этот review использует Phase 8 final closeout evidence и результат
`AMN2_PHASE_9_ENTRY_DECISION`. Live/VPS/SSH/config/Telegram/public gates этим
документом не открывались.

## Решение

```text
gate_name=AMN2_PHASE_9_HARDENING_ENTRY_REVIEW
selected_phase9_lane=HARDENING_PRODUCTIZATION
review_status=passed
live_execution_go=false
next_live_or_mutating_step_requires_exact_named_gate=true
```

Итог: hardening lane можно продолжать как review/docs/local-only работу. Любой
live шаг остается заблокирован до отдельного exact named gate.

## Стартовая позиция

```text
previous_phase=Phase 8 private/operator RC
previous_phase_status=launch-ready-with-explicit-limitations
target_vps=89.185.80.166
expected_amn2_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
android_private_operator_rc_proof=complete-with-explicit-limitations
telegram_private_operator_rc_proof=passed-private-operator-no-config-delivery
ssh_key_based_access_status=passed
db_runtime_path_classification=resolved-for-path-existence
public_launch_status=not-approved
config_delivery_status=not-approved
peer_creation_status=not-approved
production_rollout_status=not-approved
```

## Что разрешено сейчас

Разрешено без live gate:
- обновлять docs/research/status/next-chat;
- готовить hardening runbooks;
- готовить exact gate review bundles;
- уточнять stop-lines и pass/fail criteria;
- делать secret/payload policy review;
- делать local-only helper hardening.

Разрешено только после отдельного exact named gate:
- live SSH/VPS observation;
- SSH auth-noise mitigation execution;
- DB aggregate observation on VPS;
- Telegram controlled polling;
- cleanup/guard steps на VPS;
- любые изменения runtime/config/keys/services.

## Что остается запрещено

```text
public_launch_status=not-approved
public_exposure_status=closed-by-default
config_delivery_status=not-approved
peer_creation_status=not-approved
public_self_service_config_delivery_status=not-approved
telegram_profile_media_mutation_status=not-approved
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_rollout_status=not-approved
secret_payload_output_allowed=false
```

## Hardening backlog

| Критичность | Задача | Модель | Можно делать сейчас | Exact gate нужен | Рекомендация |
| --- | --- | --- | --- | --- | --- |
| Критично | `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` | `GPT-5.5` | done | false | Считать lane выбранным |
| Критично | `AMN2_PHASE_9_HARDENING_GATE_SELECTION` | `GPT-5.5` | true | false | Выбрать первый конкретный hardening gate |
| Очень важно | `HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING` | `Codex-Spark` | true | false | Закрепить no-long-SSH pattern как стандарт |
| Очень важно | `HELPER_SSH_TRANSPORT_HARDENING` | `Codex-Spark` | true | false | Убрать CRLF/quoting/stdin pitfalls из helper-шаблонов |
| Очень важно | `SSH_AUTH_NOISE_MITIGATION_REVIEW` | `GPT-5.5` | true | false | Только review; execution отдельно |
| Очень важно | `DB_AGGREGATE_COUNTS_REVIEW` | `GPT-5.5` | true | false | Решить, нужен ли live aggregate gate |
| Важно | `TELEGRAM_OPERATION_RUNBOOK_POLISH` | `Codex-Spark` | true | false | Обновить runbook под короткие SSH-сессии |
| Важно | `RELEASE_LIMITATIONS_REFRESH_AFTER_HARDENING_ENTRY` | `Codex-Spark` | true | false | Синхронизировать ограничения после выбора lane |
| Просто | `NEXT_CHAT_SYNC_AND_PUSH` | `Codex-Spark` | true | false | Делать после ближайшего закрытого docs-step |

## Recommended first hardening step

```text
recommended_next=HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING
recommended_model=Codex-Spark
reason=already_observed_working_pattern_and_no_live_gate_required
```

Почему это первый шаг: Telegram no-long-SSH retry уже прошел, а предыдущие
ошибки повторялись из-за длинных SSH-сессий, stdin-script transport, shell
quoting и CRLF exit-code issues. Закрепление helper pattern снизит риск
повторять эти сбои в новых gates.

## Stop-lines

Без отдельного exact named gate нельзя:
- открывать public exposure;
- выполнять config generation/delivery;
- создавать peer/config;
- запускать Telegram polling/live send;
- выполнять package upload/apply;
- менять firewall/sshd/auth/users/keys;
- выполнять service start/restart/stop;
- выполнять restore/import/reboot/provider rebuild;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- выводить raw DB rows, raw `wg dump`, raw process list, raw server logs.

