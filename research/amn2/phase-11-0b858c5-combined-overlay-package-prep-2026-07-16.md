# Phase 11 `0b858c5` combined overlay package preparation

Date: 2026-07-16.

Status: `prepared-verified|not-uploaded|not-applied|no-live-mutation`.

## Result

Prepared the exact combined private source-overlay candidate for AMN2 source
`codex-vps-test-prep` commit
`0b858c5cdbc5b565cc265966a2edfe2d339d65e0`. The source commit contains the
canonical square bot/web logo, the role-specific wide Telegram language header
and the local persistent-bot admission/unit hardening.

```text
production_overlay=801f8c3|unchanged
package=dist/amn2-combined-overlay-0b858c5.zip
package_sha256=7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54
package_bytes=9220155
outer_entries=4
source_zip=dist/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip
source_zip_sha256=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
source_zip_bytes=9277869
source_archive_comment=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
source_archive_entries=383
source_delta_paths=31
source_deleted_paths=app/web/static/brand-full.jpg
source_uncompressed_bytes=11309118
source_max_entry_bytes=2950469
forbidden_entries=0
unsafe_names=0
symlink_entries=0
canonical_square_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
language_header_sha256=BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F
```

The outer ZIP contains exactly:

1. `AMN2_COMBINED_OVERLAY_0b858c5.ru.md`;
2. `amn2_apply_source_zip.sh`;
3. `amn2-codex-vps-test-prep-0b858c5-source.zip`;
4. `amn2-codex-vps-test-prep-0b858c5-source.zip.sha256.txt`.

The inner ZIP is an exact `git archive`; it excludes working-tree and untracked
state. Both checksum receipts match computed bytes. The embedded inner ZIP is
byte-identical to the separately verified source archive.

## Verification

```text
package_helper_and_markdown_tests=5_passed
package_helper_bash_syntax=passed
helper_equivalence=only_source_path_sha_commit_defaults_differ
outer_integrity=passed
outer_allowlist=4_of_4_exact
inner_integrity=passed
inner_commit_binding=passed
inner_asset_and_package_data_bindings=passed
inner_forbidden_unsafe_symlink_counts=0_0_0
isolated_zip_traversal_probe=outside_writes_0|symlinks_0
source_full_tests=918_passed|1_skipped|1_known_warning
```

The marker scan found no private key, AWS key, GitHub token, Bearer credential
or live Telegram token. Seventeen inner-source matches were already-public
Windows path examples or visibly fake `Example` token samples. A newly authored
absolute local path in the package plan was removed before the sealed scan
snapshot.

## Security review

```text
security_scan_id=32d68a4_20260716T123509Z
security_snapshot=codex-security-snapshot/v1:sha256:1b94685eea2da582efd72341869fccae1738d1a6ace588c612803f39fbafcc4e
security_report_sha256=C722BF626EA437F9E0094B4977773DF354EBDB79C50CD8723A6F28845B28CF43
deep_review_receipts=7_of_7
reviewed_surfaces=5
coverage=complete
reportable_findings=0
deferred=0
```

The deterministic source-like inventory excluded `dist/` and `docs/` by
default, so all seven staged package/plan files were explicitly added back and
closed with full-file or full-container receipts. The unrelated untracked
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` was excluded and untouched.

## Safety boundary

No production SSH, package upload, extraction, source apply, service stop or
start, Telegram API/profile mutation, database write, provider mutation,
config/peer mutation, public exposure or AWG action occurred. Production stays
on `801f8c3`; the regular bot remains inactive/disabled.

The package contract requires a mode-0700 tracked-source snapshot, overlay
marker copy and SQLite backup before apply. A future approved rollout may stop
and start only the private web service, must remove only the stale tracked JPG,
must keep the installed bot unit/env unchanged, and must roll back source,
marker and database on any invariant failure. AWG must remain running and
untouched throughout.

## Next exact gate

Prepared but not consumed:

```text
APPROVE PHASE11_0B858C5_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED
```

This phrase does not authorize persistent bot activation, Telegram profile
mutation, schema initialization, provider action, public exposure, peer/config
mutation or any AWG service action.
