# AMN2 Phase 9 DB aggregate counts review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Run type: docs-only review.

## Input evidence

- `docs/AMN2_PRIVATE_RC_DB_RUNTIME_OBSERVATION_RETRY_RESULT.ru.md`
- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`
- `docs/AMN2_PRIVATE_RC_TELEGRAM_OPERATION_GATE_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`
- `research/amn2/phase-8-private-rc-db-runtime-observation-retry-result-2026-06-25.md`
- `research/amn2/phase-8-private-rc-final-closeout-2026-06-27.md`

## Result

`AMN2_DB_AGGREGATE_COUNTS_REVIEW` completed as docs-only.

```text
selected_phase9_lane=HARDENING_PRODUCTIZATION
db_runtime_path_classification=resolved-for-path-existence
db_aggregate_counts_required_for_current_lane=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
db_live_observation_approved=false
future_exact_gate_required_for_live_counts=true
```

## Rationale

Phase 8 already proved the configured DB path exists at
`/opt/amn2/data/amneziya.sqlite3`. Aggregate counts were not collected because
helper attempts hit SQL/shell quoting issues, not because the DB was missing.
For the current Phase 9 hardening/productization lane, counts are optional
confidence and do not block progress.

If counts become necessary later, use a future exact gate with a key-based
short SSH Python/sqlite helper and safe aggregate-only output.

## Output artifact

- `docs/AMN2_DB_AGGREGATE_COUNTS_REVIEW.ru.md`

## Post-condition

No live/VPS/SSH/DB/config/Telegram/public gate was opened. No DB rows were
printed, and no DB copy/download occurred.
