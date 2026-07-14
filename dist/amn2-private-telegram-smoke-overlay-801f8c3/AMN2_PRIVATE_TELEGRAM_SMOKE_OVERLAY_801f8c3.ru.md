# AMN2 private Telegram smoke overlay 801f8c3

Date: 2026-07-14.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `801f8c3 Harden Telegram smoke pre-ack backlog`.

Package preparation does not authorize upload, source apply, service changes,
Telegram API calls, polling, database writes, peer/config actions or public
exposure.

```text
source_commit=801f8c3406121549eb6a19150be009cfc0ea88d0
previous_vps_overlay=3c91601
source_zip=amn2-codex-vps-test-prep-801f8c3-source.zip
source_zip_sha256=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
delta_paths=app/bot/controlled_smoke.py|tests/bot/test_controlled_smoke.py
schema_delta=none
production_database_migration=not_required
web_code_delta=none
brief_web_stop=required_only_for_full_source_overlay_safety
regular_bot_runtime=inactive_disabled_before_and_after
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

## Included safety change

The controlled Telegram smoke runner now checks the pending-update count after
the selected administrator response succeeds but before it acknowledges any
update. Exactly one pending update must exist: the accepted `/start`. Any
additional update stops the run without an offset acknowledgement, preserving
the backlog. After acknowledgement the pending count must be zero.

The existing contract remains unchanged: one selected ID already present in
`ADMIN_TELEGRAM_IDS`, exact `/start`, message-only retrieval, private SQLite
clone writes, no callback dispatcher, no production DB path, internal deadline
at most 120 seconds and redacted result output.

## Overlay boundary

The source archive is an exact `git archive` of commit `801f8c3`; untracked,
private and working-tree files are excluded. The apply tool verifies the exact
source SHA-256 and preserves `.env`, `servers.yml`, `data`, `venv` and private
evidence directories.

The future live overlay gate must:

1. Re-fetch this package from its committed docs/evidence binding and verify
   the outer package plus every inner artifact SHA-256.
2. Require current production overlay `3c91601`, both write gates false,
   regular bot inactive/disabled, web healthy/loopback-only and AWG running
   with unchanged restart count and peer-set digest.
3. Stop only `amneziya-web.service`, then create a verified tracked-source
   snapshot, SQLite backup and unique rollback directory before applying any
   file. Confirm AWG remains running and the regular bot remains inactive and
   disabled.
4. Apply source `801f8c3` offline. No schema initialization, API smoke or
   production DB write is authorized by this delta.
5. Start only `amneziya-web.service`, then verify imports, overlay marker,
   exact two-path delta, production DB logical digest/count invariants, web
   health, private listeners, bot disabled state and AWG continuity.
6. Roll back the tracked source snapshot and overlay marker on any binding,
   import, runtime, database or AWG invariant failure.

AWG must never be stopped, restarted, recreated or reconfigured. The source
overlay approval does not authorize the later transient Telegram polling run.

## Future approved command inputs

```text
AMN2_DIR=/opt/amn2
AMN2_SOURCE_ZIP=/root/amn2-private-telegram-smoke-overlay-801f8c3/amn2-codex-vps-test-prep-801f8c3-source.zip
AMN2_EXPECTED_SOURCE_SHA=B332CB1DCFB85768ACE0DF78E038B955F7C853989CF1C67CDE0233FA51EBD6C3
AMN2_EXPECTED_SOURCE_COMMIT=801f8c3
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

Any upload, extraction, source apply or live verification requires the exact
Phase 11 overlay approval phrase recorded outside this package. A successful
overlay verification is required before a separate transient Telegram smoke
approval can be prepared.
