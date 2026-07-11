# Phase 10 Telegram single-admin transient smoke runner hardening

Date: 2026-07-11.

Product commit:

```text
repository=amn2
branch=codex-vps-test-prep
commit=4e44c5d
push=done
live_vps_overlay=34b3b43
live_actions=false
```

## Product Slice

AMN2 now provides a dedicated CLI path:

```text
python -m app.cli bot controlled-start-smoke
```

The command is deliberately separate from `app.main` and its full production
dispatcher. It requires a configured administrator, expected bot username,
private SQLite clone and internal timeout. It never registers callback-query
routes.

Changed product files:

```text
app/bot/controlled_smoke.py
app/cli.py
app/main.py
tests/bot/test_controlled_smoke.py
```

`app.main` now shares `create_workflow_from_settings()` with the controlled
runner. Normal bot startup retains its previous production behavior; no
persistent runtime setting was changed.

## Safety Contract

The controlled runner:

1. Requires the selected ID to exist in `ADMIN_TELEGRAM_IDS`.
2. Refuses execution while either VPS write gate is enabled.
3. Refuses the production database, missing files and SQLite clone symlinks.
4. On POSIX, requires a process-owned mode `0700` clone directory and mode
   `0600` clone file.
5. Verifies production and clone SQLite integrity plus required tables.
6. Verifies the expected bot username, no webhook and zero backlog before
   waiting.
7. Uses `allowed_updates=["message"]`, `limit=1` and an internal deadline no
   greater than 120 seconds.
8. Accepts only exact `/start` from the selected administrator.
9. Calls `handle_start` directly against the clone workflow; the full
   dispatcher and callbacks are not created.
10. Does not acknowledge an unexpected first update.
11. Acknowledges the accepted update only after its response succeeds, then
    rechecks webhook and backlog.
12. Requires the production database logical digest to remain unchanged and
    reports only redacted state booleans.
13. Closes the Telegram session and sanitizes client, API and unexpected
    failures.

The outer transient systemd watchdog is intentionally not embedded in the
product command. A later live gate must still use `RuntimeMaxSec=180`,
`Restart=no`, `TimeoutStopSec=15` and `KillMode=control-group`; the regular bot
unit must remain disabled.

## Test Evidence

Project runtime verification used CPython `3.12.13` from the AMN2 `.venv`:

```text
controlled_smoke_focused=14_passed
controlled_smoke_plus_bootstrap_network=24_passed
bot_and_settings_scoped_regression=178_passed
full_regression=810_passed|1_skipped|1_warning
cli_help=passed
diff_check=passed
secret_pattern_scan=no_matches
phase9_progress_harness=14_passed|product_and_docs_scope_passed
```

The one warning is the pre-existing Starlette `TestClient` deprecation warning
for the installed `httpx` compatibility layer. No new warning was introduced.

An additional full run on the machine-default CPython `3.14` passed before the
final post-backlog test was added; the authoritative result above is the final
full run on the supported CPython `3.12.13` runtime.

## Diff Review

No blocking finding remains. The reviewed implementation cannot use the
production SQLite path through its supported CLI entry, cannot process
callbacks, cannot accept a different sender or command, and cannot report
success with a new post-run Telegram backlog.

## Runtime State And Next Gate

The VPS remains unchanged on source overlay `34b3b43`. The regular Telegram
unit remains inactive and disabled. No Telegram API method or polling was
called during this product slice.

The next action is package preparation for `4e44c5d`, followed by a separate
checksum-bound private upload/smoke gate. Controlled live polling still needs
another explicit approval after the hardened source is active on the VPS.

```text
START_PHASE10_4E44C5D_VPS_PACKAGE_PREP_SLICE
```

Android TV device `8` remains independently ready for the operator's physical
`IMPORT_CONNECT` test and Codex handshake/traffic verification.
