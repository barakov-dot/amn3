# AMN2 canonical logo overlay 6abc620

Date: 2026-07-15.

Purpose: private source-overlay candidate for `amn2/codex-vps-test-prep`
commit `6abc620 Replace canonical bot branding`.

Package preparation does not authorize upload, extraction, source apply,
service changes, Telegram API calls, Telegram profile-photo mutation, bot
start/enable, database writes, peer/config actions or public exposure.

```text
source_commit=6abc620bc583ddd55490a25633516f2db8e50309
previous_vps_overlay=801f8c3
source_zip=amn2-codex-vps-test-prep-6abc620-source.zip
source_zip_sha256=4BED630024AD58B2E6B7111E172A18CF934262E4BB32DAD7A2787CFFFA4607A4
canonical_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
delta_paths=app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png|app/web/static/brand-full.jpg|app/web/static/brand-full.png|app/web/templates/dashboard.html|app/web/templates/login.html|tests/web/test_app.py
schema_delta=none
production_database_migration=not_required
regular_bot_runtime=inactive_disabled_before_and_after
telegram_profile_photo=unchanged
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

## Included change

The operator-provided PNG is the single canonical logo for the existing bot
start header and private web login/dashboard. Both PNG copies are byte-identical
and bound to the SHA-256 above. The obsolete web JPG is removed. The Telegram
profile icon is a separate live identity mutation and is not part of this
package or gate.

## Package boundary

The source archive is an exact `git archive` of commit `6abc620`; untracked,
private and working-tree files are excluded. The helper verifies the exact
source SHA-256 and preserves `.env`, `servers.yml`, `data`, `venv` and private
evidence directories. It must be invoked only by the approved live rollout
orchestrator, which snapshots tracked source and explicitly removes the stale
`app/web/static/brand-full.jpg` after the full archive overlay.

## Future live rollout contract

The separate exact live gate must:

1. Verify outer and inner checksums, the archive comment/full commit binding,
   the six-path `801f8c3..6abc620` allowlist and canonical PNG SHA-256.
2. Require current production overlay `801f8c3`, both write gates false,
   regular bot inactive/disabled, web active/healthy/loopback-only, database
   integrity and AWG running with the same restart count and peer-set digest.
3. Stop only `amneziya-web.service`; create a mode-0700 rollback directory,
   tracked-source snapshot, overlay-marker copy and SQLite backup; recheck AWG
   and database before applying anything.
4. Apply source `6abc620` offline, remove only the obsolete tracked JPG and
   verify the exact six-path source delta. Do not initialize schema or start
   the bot.
5. Start only `amneziya-web.service`; verify login/dashboard PNG responses,
   exact PNG SHA-256, imports, overlay marker, database logical/count/file
   invariants, private listeners, bot inactive/disabled and AWG continuity.
6. Roll back tracked source, marker and database backup on any binding,
   source-delta, web, database, bot-state or AWG invariant failure.

AWG must never be stopped, restarted, recreated or reconfigured. A successful
logo rollout does not authorize bot activation or Telegram profile mutation.

## Future approved command inputs

```text
AMN2_DIR=/opt/amn2
AMN2_SOURCE_ZIP=/root/amn2-canonical-logo-overlay-6abc620/amn2-codex-vps-test-prep-6abc620-source.zip
AMN2_EXPECTED_SOURCE_SHA=4BED630024AD58B2E6B7111E172A18CF934262E4BB32DAD7A2787CFFFA4607A4
AMN2_EXPECTED_SOURCE_COMMIT=6abc620
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

Any upload, extraction, source apply, web stop/start or live verification
requires a fresh exact Phase 11 logo-overlay approval phrase outside this
package.
