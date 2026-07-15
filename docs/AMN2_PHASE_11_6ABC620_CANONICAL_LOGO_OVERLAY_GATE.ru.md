# AMN2 Phase 11: canonical logo overlay 6abc620 gate

Актуально: 2026-07-15.

## State and decision

```text
source_branch=codex-vps-test-prep
source_commit=6abc620bc583ddd55490a25633516f2db8e50309
production_overlay=801f8c3
package=dist/amn2-canonical-logo-overlay-6abc620.zip
package_sha256=2683420DD7A705C96490DC1878D14D208986209BF8EB1B6E1B066D31B17932F5
canonical_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
package_status=prepared_local_not_uploaded_not_applied
regular_bot=inactive_disabled
telegram_profile_photo=unchanged
```

Package source and full runbook:
`dist/amn2-canonical-logo-overlay-6abc620/`.

## Exact production delta

`801f8c3..6abc620` содержит только:

1. `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`;
2. удаление `app/web/static/brand-full.jpg`;
3. добавление `app/web/static/brand-full.png`;
4. `app/web/templates/dashboard.html`;
5. `app/web/templates/login.html`;
6. `tests/web/test_app.py`.

Schema, database, settings, service units, bot polling, Telegram profile,
AWG/config/peer code и public exposure не меняются.

## Rollout and rollback contract

- Require overlay `801f8c3`, healthy loopback-only web, bot inactive/disabled,
  write gates false/false, database integrity and unchanged running AWG
  snapshot.
- Verify outer/inner checksums, archive full-commit comment, exact six-path
  delta and canonical PNG SHA before service mutation.
- Stop/start only `amneziya-web.service`; never stop/restart/recreate AWG and
  never start/enable the bot.
- Create mode-0700 tracked-source snapshot, DB backup and overlay-marker copy
  before apply; verify DB/AWG remain unchanged while web is stopped.
- Apply offline source `6abc620`, remove only obsolete tracked JPG, verify
  byte-identical bot/web PNG and exact source delta.
- Verify served PNG, login/dashboard, private listeners, DB invariants, bot
  disabled state and AWG continuity.
- On any invariant failure restore tracked source/marker/DB and web health,
  then re-verify bot and AWG state.

## Prepared exact live approval phrase

Не выполнять до завершения package tests/diff/security review и отдельного
сообщения оператора:

```text
APPROVE PHASE11_6ABC620_CANONICAL_LOGO_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
```

Approval не разрешает Telegram profile-photo mutation, bot start/enable,
polling/send, database migration/write, public exposure, peer/config mutation
или provider action.
