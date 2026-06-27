# AMN2 DB aggregate counts review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Статус: `completed-docs-only-review`.

Этот review использует существующие Phase 8/9 evidence. Live/VPS/SSH/DB/config/
Telegram/public gates этим документом не открывались.

## Decision

```text
gate_name=AMN2_DB_AGGREGATE_COUNTS_REVIEW
selected_phase9_lane=HARDENING_PRODUCTIZATION
review_status=passed
db_runtime_path_classification=resolved-for-path-existence
db_aggregate_counts_required_for_current_lane=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
db_live_observation_approved=false
future_exact_gate_required_for_live_counts=true
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Итог: DB aggregate counts не являются blocker для текущего Phase 9
`HARDENING_PRODUCTIZATION` lane. Сбор live counts можно делать позже только как
optional confidence или как precondition для другого lane (`CONTROLLED_CONFIG_DELIVERY`,
`PUBLIC_LAUNCH_READINESS`, `DR_RELIABILITY`) через отдельный exact gate.

## Evidence base

Использованные документы:

- `docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_RETRY_RESULT.ru.md`;
- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`;
- `docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW.ru.md`;
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`;
- `research/amn2/phase-8-private-rc-db-runtime-observation-retry-result-2026-06-25.md`;
- `research/amn2/phase-8-private-rc-final-closeout-2026-06-27.md`.

Ключевые факты:

```text
settings_database_path=data/amneziya.sqlite3
settings_database_resolved_path=/opt/amn2/data/amneziya.sqlite3
settings_database_exists=true
settings_database_bytes=147456
settings_database_mode=600
db_candidate_count=1
db_candidate_1_path=data/amneziya.sqlite3
previous_telegram_live_preview_db_present_false_reclassified=helper_observation_issue
aggregate_counts_status=not_observed_due_to_helper_quoting
db_rows_printed=false
db_download_copy_performed=false
```

## Interpretation

Phase 8 resolved the important runtime question:

```text
db_discrepancy_status=resolved_for_path_existence
db_runtime_path_status=settings_db_present
```

Aggregate counts were not collected because helper attempts hit SQL/shell
quoting problems over Windows SSH. That does not invalidate the DB path
classification and does not create a release blocker inside current private RC
limitations.

For Phase 9 hardening/productization, the useful action is not another ad-hoc
quoted SQL attempt. If counts are needed later, use a purpose-built exact gate
with a safe helper shape.

## Future exact gate, if needed

Future review name:

```text
AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE_REVIEW
```

Future execution gate should allow only:

- key-based short SSH;
- read-only SQLite aggregate counts;
- table existence/counts only;
- no row dumps;
- no DB download/copy;
- no raw SQL output containing values;
- no config generation/delivery;
- no peer creation;
- no service start/restart/stop;
- no public exposure;
- no secrets/payload output.

Recommended implementation shape for future helper:

```text
transport=key-based-short-ssh
python_sqlite_helper=true
shell_sql_pipeline=false
raw_rows_output=false
db_copy_download=false
safe_fields_only=table_exists,count
```

## Stop-lines

Без нового exact named gate нельзя:

- выполнять live VPS/SSH/DB command;
- читать или выводить DB rows;
- копировать или скачивать DB;
- выводить raw SQL query results beyond safe counts;
- выводить tokens/passwords/config payloads;
- создавать peer/config;
- доставлять config;
- запускать Telegram polling/live send;
- выполнять service start/restart/stop;
- открывать public exposure;
- выполнять package upload/apply;
- выполнять restore/import/reboot/provider rebuild.

## Phase 9 status

```text
phase9_db_aggregate_counts_review_status=passed
phase9_db_aggregate_counts_blocker=false
phase9_db_aggregate_counts_optional_confidence=true
phase9_db_live_counts_future_gate_required=true
recommended_next_docs_only=PROJECT_STATUS_CURRENT_REFRESH_AND_SECRET_SCAN
```
