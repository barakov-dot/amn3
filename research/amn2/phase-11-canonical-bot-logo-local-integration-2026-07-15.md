# Phase 11 canonical bot logo local integration

Date: 2026-07-15

Status: `completed-local-source|committed|pushed|not-deployed`

## Operator input and canonical identity

The operator supplied the new project/bot logo and explicitly instructed that
it replace the previous branding everywhere locally required. The original PNG
was copied without re-encoding.

```text
format=PNG
dimensions=1254x1254
bytes=2950469
sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
```

## Implemented source scope

- Replaced `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`, preserving the existing
  `/start` runtime binding.
- Added the same bytes as `app/web/static/brand-full.png` for web login and
  dashboard branding.
- Removed the superseded `app/web/static/brand-full.jpg`.
- Updated both web templates to the PNG path and the exact `1254x1254`
  intrinsic dimensions.
- Added a regression assertion that the bot and web copies are byte-identical
  and match the canonical SHA-256; web tests also require `image/png`.

## TDD and verification evidence

```text
red=3_failed|expected_missing_png_and_stale_template_paths
focused_green=58_passed|1_known_dependency_warning
full_suite=872_passed|1_skipped|1_known_dependency_warning
diff_check=passed
staged_diff_check=passed
stale_brand_full_jpg_references=0
```

The local bot-media validator accepted the same file for both intended roles:

```text
start_header=valid|local-only|telegram_api_called_false
profile_icon=valid|staged-for-operator|telegram_api_called_false
```

The sealed Codex Security working-tree diff scan recorded complete coverage,
three reviewed surfaces, nine sealed artifacts, zero deferred rows and zero
findings. Snapshot:
`codex-security-snapshot/v1:sha256:7c3403f67b7b8dfc75e0bb439b53de0a1f7157d94315f09d413931ec03a8ace3`.
An independent final reviewer found no code/security defects; its only staging
observation was closed by selective staging and a fresh `58 passed` run.

## Git evidence

```text
branch=codex-vps-test-prep
commit=6abc620 Replace canonical bot branding
origin_sync=true
```

## Live and recovery boundaries

This slice did not call Telegram, change the Telegram profile photo, start or
enable the bot, contact a VPS, apply a package, restart a service, expose a
listener, modify a database, create/revoke a peer, or stop/restart/recreate
production AWG.

Production remains on overlay `801f8c3`. Therefore the new logo is canonical
in current source but is not yet visible on production web or the disabled
production bot. A later production source/package apply needs its own exact
rollout gate. Telegram profile-photo mutation remains a different live
identity gate.

The already approved `RESTORE-001A` transaction remains pinned to source and
production overlay `801f8c3`; advancing the source branch to `6abc620` does not
expand or consume that approval and must not silently change its bundle input.
