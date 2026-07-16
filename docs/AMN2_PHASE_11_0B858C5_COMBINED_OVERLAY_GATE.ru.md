# AMN2 Phase 11: combined overlay `0b858c5` gate

Актуально: 2026-07-16.

## State and decision

```text
source_branch=codex-vps-test-prep
source_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
production_overlay=801f8c3
package=dist/amn2-combined-overlay-0b858c5.zip
package_sha256=7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54
package_bytes=9220155
source_zip_sha256=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
source_zip_bytes=9277869
outer_entries=4
source_archive_entries=383
source_delta_paths=31
canonical_square_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
language_header_sha256=BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F
package_status=prepared_local_not_uploaded_not_applied
regular_bot=inactive_disabled
telegram_profile_photo=unchanged
awg=untouched
```

Package source and complete inner contract:
`dist/amn2-combined-overlay-0b858c5/`.

Evidence:
`research/amn2/phase-11-0b858c5-combined-overlay-package-prep-2026-07-16.md`.

## Exact production delta

`801f8c3..0b858c5` contains 31 tracked paths and combines:

1. canonical square bot/web PNG and web JPG -> PNG transition;
2. role-specific wide `/start` language-selection PNG, fixed asset path,
   package-data declaration and text-only fallback;
3. local persistent Telegram admission/runtime and hardened unit example;
4. associated design/plan and regression tests.

The only deleted tracked path is
`app/web/static/brand-full.jpg`. Schema/database migration is absent.

The source includes Telegram hardening code and a unit example, but this
source rollout does not install or modify the production bot unit/env and does
not activate polling.

## Completed package verification

- outer and inner checksum/byte binding passed;
- outer allowlist `4/4`, source archive `383` entries and full commit comment
  passed;
- forbidden entries, unsafe names and symlink entries: `0/0/0`;
- both square PNG copies and the wide PNG match their exact SHA-256 values;
- obsolete JPG absent and package-data declaration present in exact source;
- helper differs from the tested root helper only in source path/hash/commit
  defaults; `bash -n` passed;
- scoped helper/markdown tests: `5 passed`;
- full AMN2 source: `918 passed, 1 skipped, 1 known warning`;
- sealed security diff scan: `7/7` receipts, `5` surfaces, complete coverage,
  findings `0`.

## Rollout and rollback contract

A future exact live transaction must:

1. Recompute outer/inner hashes; verify exact outer allowlist, full source ZIP
   comment, 31-path delta, both asset hashes and forbidden/unsafe/symlink zero
   counts before upload or extraction.
2. Require production overlay `801f8c3`, write gates false/false, regular bot
   inactive/disabled, private web active/healthy/loopback-only, database
   integrity and an unchanged running AWG snapshot.
3. Upload only after exact approval. Before apply create a mode-0700 rollback
   root, tracked-source snapshot, overlay-marker copy and SQLite backup; capture
   installed bot unit/env read-only without changing them.
4. Stop only `amneziya-web.service`, recheck database and AWG, apply exact
   source offline and remove only stale tracked
   `app/web/static/brand-full.jpg`. Do not initialize schema, install bot unit,
   enable/start the bot or call Telegram.
5. Start only `amneziya-web.service`; verify login/dashboard, served square
   PNG, exact wide source PNG, imports, marker, private listeners, database
   logical/count/file invariants, bot inactive/disabled and AWG continuity.
6. On any binding/source/web/database/bot/AWG failure restore tracked source,
   marker and database backup, restore private web health, and re-prove bot and
   AWG invariants.

AWG must never be stopped, restarted, recreated or reconfigured.

## Prepared exact live approval phrase

Не выполнять без отдельного сообщения оператора:

```text
APPROVE PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
```

Approval не разрешает persistent bot start/enable, Telegram send/profile
mutation, schema/database write, public exposure, provider action, peer/config
mutation, recovery artifact action или AWG service/config action.
