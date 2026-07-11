# Phase 10 1c7fb78 VPS package preparation

Date: 2026-07-11.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
branch=codex-vps-test-prep
release_head=1c7fb789b1e4de09811f03e008cfad1fe6a7392c
subject=Add config assignment policies
working_tree=clean
origin_sync=done
current_vps_overlay=34b3b43
```

The source ZIP was created directly with `git archive` from the clean pushed
commit. No working-tree, private or untracked file entered the source archive.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-1c7fb78.zip
package_sha256=AEEB5A5C81354D7631F14DF57D7422CF02C08157CB4075B4B37B5BFD2BE6015B
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-1c7fb78.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-1c7fb78/amn2-codex-vps-test-prep-1c7fb78-source.zip
source_sha256=B99CBD51759076F60BE4BE11DC3F548051D1D6B2CED89641203206F5726A7BBA
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-1c7fb78/amn2-codex-vps-test-prep-1c7fb78-source.zip.sha256.txt
reconciliation_runner=private-artifacts/phase10/vps-preflight/1c7fb78/reconcile_device_owner_shared.py
reconciliation_runner_sha256=D4566B42D6FCB7B6891F65826E0E302DF59CBEC49536D3AFC4A3A3ED789C7E72
```

The outer package contains the same five reviewed entry classes as the prior
kit: source ZIP, source checksum, apply tool, loopback API smoke tool and
operator runbook. The checksum-bound private reconciliation runner is kept
separate because it is a one-time live-gated production DB operation, not a
normal source-overlay tool.

## Content Review

```text
package_entries=5
source_entries=359
source_files=316
source_dirs=43
required_missing=0
forbidden_entries=0
package_content_mismatches=0
source_sha=matched
package_sha=matched
old_4e44c5d_executable_binding_count=0
apply_commit_and_sha_binding=passed
smoke_commit_binding=passed
shell_lf_no_bom=true
bash_syntax=passed
operator_markdown_hygiene=passed
```

The source delta from the current VPS overlay has no deleted paths. It contains
the controlled Telegram smoke runner accumulated after `34b3b43`, restored
Android-compatible AWG defaults, cross-client compatibility evidence in code,
and the new config-assignment schema/service/UI/test slice.

## Extracted-Source Verification

The package was expanded into a private directory without Git metadata. A
read-only Git binding to the AMN2 repository supplied `git rev-parse` metadata
for tests that require the release head.

```text
toolchain=CPython_3.12_ok
focused_from_extracted_source=131_passed_1_skipped_1_warning
full_from_extracted_source=823_passed_1_skipped_1_warning
package_tooling=4_tests_ok
reconciliation_runner_legacy_schema_test=passed_dry_run_apply_idempotent_retry
phase9_progress_harness=14_passed|product_and_docs_scope_passed
```

The first focused attempt had `130 passed, 1 skipped` plus one infrastructure
failure because the read-only Git directory path was wrong. After correcting
only that metadata binding, the same extracted source returned the green result
above. No code or package content changed between those runs.

## Boundary

Package preparation and verification did not upload or apply the package, stop
or restart a service, migrate production SQLite, change a user/device/peer,
call Telegram, expose a listener or publish a secret. Both product write gates
remain false. The private artifacts and config remain excluded from Git.

## Next Gate

```text
START_PHASE10_1C7FB78_PRIVATE_VPS_SCHEMA_OWNER_SHARED_ROLLOUT_GATE
```

The live gate must separately authorize source snapshot, SQLite backup, clone
DB migration/reconciliation/API smoke, production migration and device 8
assignment update, web-only restart, verification and automatic rollback.

## Rollout Result

The separate exact gate was later approved and completed on successful run
`20260711T154907Z`. VPS overlay is now `1c7fb78`, device 8 is
`owner_shared`, and the private web service passed final smoke. Evidence:
`research/amn2/phase-10-1c7fb78-private-vps-schema-owner-shared-rollout-2026-07-11.md`.
