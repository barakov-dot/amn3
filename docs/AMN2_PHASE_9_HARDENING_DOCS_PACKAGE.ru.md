# SPARK_SAFE_HARDENING_DOCS_PACKAGE

Дата: 2026-06-27.
Модель: `Codex-Spark`.
Статус: `completed-docs-only`.

Этот пакет закрывает безопасный hardening-пакет для Phase 9 (lane `HARDENING_PRODUCTIZATION`) без открытия live/VPS/SSH/Telegram/public gates.

## Что входит в пакет

Документы, подготовленные/обновленные в рамках пакета:

- `docs/AMN2_HELPER_STYLE_HARDENING.ru.md`
- `docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`
- `docs/AMN2_HELPER_TELEGRAM_OPERATION_NO_LONG_SSH_HARDENING.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_PUBLIC_LAUNCH_ENTRY_REVIEW.ru.md`
- `docs/AMN2_TELEGRAM_OPERATION_RUNBOOK_POLISH.ru.md`
- `docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`
- `docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`
- `docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md` (обновлён с явной моделью `Codex-Spark`/`GPT-5.5`)
- `docs/AMN2_PRIVATE_RC_RELEASE_LIMITATIONS_REFRESH.ru.md`
- `docs/AMN2_PRIVATE_RC_FINAL_STATUS_REFRESH.ru.md`
- `docs/NEXT_CHAT_AMN2_PHASE_9_HARDENING_SESSION_0.ru.md`
- `research/amn2/phase-9-hardenings-docs-package-2026-06-27.md`
- `research/amn2/phase-9-public-launch-entry-review-2026-06-27.md`

Базовые ограничения на входе в Phase 9 оставлены:

```text
public_launch_status=not-approved
config_delivery_status=not-approved
peer_creation_status=not-approved
public_self_service_config_delivery_status=not-approved
telegram_profile_media_mutation_status=not-approved
restore_import_status=not-proven
provider_rebuild_status=not-proven
production_rollout_status=not-approved
ios_defaultvpn_status=failed-not-accepted
ios_config_import_status=failed-no-tested-import-path
ssh_auth_hardening_execution_approved=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
```

## Принятые hardening правила

```text
helper_ssh_transport_hardening_status=completed-docs-only
single_session_preference=true
short_ssh_precheck_required=true
manual_window_without_open_ssh_preferred=true
remote_watchdog_ttl_max_seconds=180
remote_script_lf_normalization_required=true
scp_upload_required=false
remote_temp_helper_file_created=false
raw_process_list_output_allowed=false
raw_log_output_allowed=false
secret_payload_output_allowed=false
```

## Короткий пакетный итог

```text
phase9_hardening_lane=HARDENING_PRODUCTIZATION
public_launch_entry_review=blocked
phase9_entry_decision_doc=docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md
helper_stability_review_status=passed
telegram_no_long_ssh_pattern=standardized
transport_hardening_review_status=passed
runbook_polish_status=passed
ios_acceptance_decision_review_status=passed
ssh_auth_noise_mitigation_review_status=passed
db_aggregate_counts_review_status=passed
release_limitations_status=refreshed
final_status_refresh_status=updated
final_status_refresh_includes=no-long-ssh-retry-passed-private-operator-no-config-delivery
public_launch_entry_review_status=completed-docs-only-no-go
docs_only=true
```

## Следующий step после пакета

После этого пакета продолжаем по очереди:

1. `AMN2_PHASE_9_HARDENING_ENTRY_REVIEW` уже пройден.
2. `AMN2_PHASE_9_TASK_MATRIX_REFRESH` обновлен.
3. `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` уже закрыт.
4. `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` уже закрыт.
5. `AMN2_DB_AGGREGATE_COUNTS_REVIEW` уже закрыт.
6. Следующий живой (внешний) шаг возможен только после явного operator-confirmed lane gate.

До следующего exact gate:

- только docs/research/status updates,
- no live/VPS/SSH/Telegram/public actions,
- no secret/payload output.
