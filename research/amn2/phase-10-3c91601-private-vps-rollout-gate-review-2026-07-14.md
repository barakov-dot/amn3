# Phase 10 3c91601 private VPS rollout gate review

Date: 2026-07-14.

Decision: `APPROVE-CONDITIONAL-AWAITING-EXACT-LIVE-PHRASE`.

This review records the exact upload, source snapshot, clone-DB migration,
loopback smoke and rollback boundary. It did not contact the VPS, upload or
extract a package, stop or restart a service, migrate SQLite, call Telegram,
or mutate any user, device, ticket, config or peer.

## Bound inputs

```text
candidate_source=3c916015c10add37886370d04af70f0343f7f691
current_vps_overlay=1c7fb78
commits_ahead=9
package=dist/amn2-vps-update-and-smoke-kit-3c91601.zip
package_sha256=12E90EB54FCC374C84B6AA987C65E5644C4BD1B974089E81E16D00780389FB6E
source_sha256=5AD92A3A9D944825FEFDFEB4D56BDDBBB05390036E19E5AD197288C73812B0CB
apply_sha256=578A145E2AFE5BCC69B3730CE8C12BCE1BE368EC3B6DDD4847E94DD428D90DDA
smoke_sha256=4E49B183825603168108B227978F488A68EF31BC8BD11E2A839135CDE70E4106
package_review_commit=2ab94f5
package_remote=https://github.com/barakov-dot/amn3.git
package_branch=codex-spark-phase9-docs-sync
```

The package has five reviewed entries and no deleted tracked source path.
Its extracted source passed the focused `237` test run, the full `870 passed,
1 skipped` run, compile checks, package checks and secret-boundary review.

## Gate-record verification

```text
phase9_progress_harness=passed|all_five_stop_lines_false|docs_only_scope
scoped_harness_markdown_tests=20_passed
canonical_root_tests=43_passed
diff_check=passed
live_effect=none
```

The canonical orchestration suite is `python -m pytest -q tests`. A bare
workspace-wide pytest invocation is intentionally not used because this lab
retains several extracted package sources and Git worktrees with duplicate
test module names; collecting all of them together is not a valid suite.

## Exact schema delta

The production schema at `1c7fb78` already has `plans.max_devices` and
`devices.assignment_mode`. The `3c91601` migration adds only:

```text
tables=device_passports|device_enrollment_tickets|device_lifecycle_events
indexes=idx_device_passports_owner|idx_device_enrollment_tickets_user|idx_device_enrollment_tickets_expiry|idx_device_lifecycle_ticket|idx_device_lifecycle_passport
expected_new_table_rows=0|0|0
existing_table_row_changes=0
peer_or_config_changes=0
```

Schema initialization is idempotent. The clone rehearsal must prove the exact
delta before the same initialization is allowed against production SQLite.
Starting the new web source is not accepted as an implicit, unverified
migration step.

## Runtime invariants

`amnezia-awg2` serves already issued configurations and must stay running.
The rollout must not stop, restart, recreate or reconfigure that container.
Its pre-rollout state, restart count, peer count and safe public-key-set digest
must match after rollout or after rollback. Natural handshake times and traffic
counters are observational and are not compared for equality.

Only `amneziya-web.service` may be stopped briefly to freeze SQLite writers,
take the verified backup, perform the exact production migration and activate
the source overlay. `amneziya-bot.service` must remain inactive and disabled.

## Exact allowed live scope

Only after the exact phrase below:

1. Re-fetch the approved package from commit `2ab94f5`, then verify the local
   package SHA256 and all four bound artifact hashes.
2. Run a read-only VPS preflight. Require overlay `1c7fb78`, healthy SQLite,
   both product write gates false, web active/enabled, bot inactive/disabled,
   no API listener on `3040`, loopback-only web on `3030`, sufficient disk and
   `amnezia-awg2` running with no restart in the preflight window.
3. Upload only the package ZIP and its checksum file to `/root`, mode `0600`.
   Verify the outer checksum remotely before extraction.
4. Create unique mode `0700` candidate and rollback directories. Refuse path
   reuse, symlinks, unexpected owners or resolved paths outside the approved
   `/root` roots.
5. Stop only `amneziya-web.service`. Confirm the AWG container remains running
   and the bot remains inactive/disabled.
6. With web writers frozen, create and verify inside the rollback directory:
   a mode `0600` tar of exactly `.env.example`, `.gitattributes`, `.gitignore`,
   `README.md`, `app`, `deploy`, `docs`, `pyproject.toml`, `scripts` and
   `tests`; the prior overlay marker and metadata; a SQLite backup made through
   the SQLite backup API; and a secret-free manifest of paths, modes, sizes and
   SHA256 values.
7. Extract the package into the new candidate directory and verify the source,
   apply-tool and smoke-tool checksums plus commit binding.
8. Apply tracked source `3c91601` offline with `VPS_APPLY_ENABLED=false`,
   `OPERATOR_DEVICE_CREATE_ENABLED=false`, `PIP_NO_INDEX=1` and
   `PIP_DISABLE_PIP_VERSION_CHECK=1`. Preserve `.env`, `servers.yml`, `data`,
   `venv`, rollback material and private smoke evidence.
9. Create a private SQLite clone from the verified backup. Run
   `initialize_schema` on the clone using the active `3c91601` source.
10. Require clone integrity `ok`, zero foreign-key issues, the exact three new
    tables and five indexes, zero rows in each new table, and unchanged counts
    and safe logical digests for every pre-existing table.
11. Run `amn2_api_loopback_smoke.sh` as the service user against only the
    migrated clone. Bind both `DATABASE_PATH` and `AMN2_DB` to the clone; set
    server name `local`, host `127.0.0.1`, port `3040`, preflight off, server DB
    sync required, existing API disallowed and both write gates false.
12. Require clone API readiness, loopback-only listener, auth results
    `401/403/401`, safe audit evidence, token revocation and no raw token in
    retained output. Confirm production SQLite is still byte/logically
    unchanged before crossing the production-migration checkpoint.
13. Run only `initialize_schema` against production SQLite. Require the exact
    schema delta from this review, zero rows in all three new tables, unchanged
    existing-table counts and safe logical digests, integrity `ok` and zero
    foreign-key issues. No enrollment, passport or lifecycle row is seeded.
14. Start only `amneziya-web.service`. Require active/enabled state, login HTTP
    `200`, protected-route redirect, loopback-only `127.0.0.1:3030`, no public
    `3030/3040` listener, both write gates false and no bot process.
15. Reconfirm AWG running state, restart count, peer count and safe peer-set
    digest. Preserve rollback/evidence material and remove only the verified
    disposable clone and raw transient token files.

The production API smoke is explicitly excluded. All token issue/revoke,
server-config sync and read-audit writes occur only in the disposable clone.

## Stop and rollback criteria

Stop before source apply on any overlay or checksum mismatch, unsafe write
gate, active bot, unexpected listener, AWG instability, insufficient disk,
rollback verification failure, candidate collision, DB integrity/FK failure
or package binding mismatch.

Rollback after source apply on import failure, clone migration or clone smoke
failure, any production DB change before its checkpoint, unexpected schema or
row delta, web startup/auth/listener failure, changed write gate, bot
activation or AWG state/peer-set change.

Rollback sequence:

1. Terminate the disposable loopback API process and stop only the web service.
2. Resolve `/opt/amn2`, remove only the exact ten reviewed tracked roots/files
   listed above, then restore the tracked-source snapshot and prior overlay
   marker. This removes candidate-only files while preserving `.env`,
   `servers.yml`, `data`, `venv`, `vps-smoke`, Git metadata and evidence.
3. If the production migration checkpoint was crossed, restore the verified
   SQLite backup atomically and recheck integrity, foreign keys and the private
   pre-rollout logical digest.
4. Run the offline editable-install/import checks from restored `1c7fb78`.
5. Start the web service and repeat its login/auth/listener checks.
6. Require AWG still running with its original restart count and safe peer-set
   digest; keep the bot inactive and disabled.
7. Retain the mode `0700` rollback bundle and publish only a sanitized result.

Rollback never stops or recreates the AWG container. If AWG itself becomes
unhealthy, stop the rollout and switch to the existing production-runtime
recovery procedure instead of attempting a source-overlay rollback against it.

## Excluded

Production API token smoke, plan quota writes, ticket issue/claim/revoke,
passport creation, lifecycle writes, cascade device revoke, peer mutation,
config generation or delivery, Telegram API/polling, public exposure,
firewall/TLS/reverse-proxy changes, reboot and provider actions remain closed.

## Exact approval phrase

```text
APPROVE PHASE10_3C91601_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_SNAPSHOT_CLONE_DB_MIGRATION_AND_WEB_ACTIVATION_WITH_ROLLBACK
```

Without that exact phrase this decision remains review-only. No live upload,
apply, migration or service action is authorized by this document.
