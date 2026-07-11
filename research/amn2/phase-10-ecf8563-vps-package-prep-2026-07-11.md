# Phase 10 ecf8563 VPS package preparation

Date: 2026-07-11.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source Binding

```text
branch=codex-vps-test-prep
release_head=ecf85632216724ff22da48314321d01339f416e9
subject=Add plan device quota admin UI
working_tree=clean
origin_sync=done
current_vps_overlay=1c7fb78
```

The source ZIP was produced directly with `git archive` from the clean pushed
commit. No working-tree, private or untracked file entered the archive.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-ecf8563.zip
package_size=8770962
package_sha256=0AE0B2EC04986B0475647C0971D49F712A173840404D0F359CB1C98A9BD59DDE
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-ecf8563.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-ecf8563/amn2-codex-vps-test-prep-ecf8563-source.zip
source_size=8821468
source_sha256=15AA131EAA1B3B878ADB6D0FB04ED8DF3114D08641966EFC018D6E528D6CE990
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-ecf8563/amn2-codex-vps-test-prep-ecf8563-source.zip.sha256.txt
```

The outer ZIP contains exactly five entries: source ZIP, source checksum,
source apply tool, loopback API smoke tool, and operator runbook.

## Content Review

```text
package_entries=5
source_entries=361
source_files=318
source_dirs=43
required_missing=0
forbidden_entries=0
package_content_mismatches=0
source_sha=matched
package_sha=matched
old_1c7fb78_executable_binding_count=0
apply_delta=bindings_plus_fail_closed_offline_install_fallback
smoke_delta=expected_commit_only
canonical_package_apply_sha256=931379B0DADA5E225C5F35A4F3A2BC34C7AEE55C967B941423710D889AA9B8DD
canonical_package_smoke_sha256=636A20D62AF65FE194C056D8740D7C7A26AF6452CA6F26E8BD4F0ED1B49F7EDB
shell_lf_no_bom=true
bash_syntax=passed
operator_markdown_hygiene=passed
```

The source delta from the current VPS overlay contains 11 expected files and no
deleted paths. It is limited to plan quota repository behavior, authenticated
web UI/routes, CSS/navigation, explicit surface policy bindings, tests, and
AMN2 operator/data-model documentation.

## Extracted-Source Verification

The source archive was expanded into an ignored private directory without Git
metadata. A read-only Git binding supplied exact release metadata to tests that
inspect the source head.

```text
toolchain=CPython_3.14.3_local
release_head_binding=ecf85632216724ff22da48314321d01339f416e9
focused_from_extracted_source=38_passed_1_warning
full_from_extracted_source=829_passed_1_skipped_1_warning
package_tooling=5_passed
orchestration_tests=20_passed
offline_fallback_regression=passed_exact_diagnostic_and_source_path_binding
phase9_progress_harness=15_passed|product_only_scope_passed
```

## Boundary

Package preparation did not upload or apply the package, stop or restart a
service, write a plan quota, change production SQLite, mutate a user/order/
device/peer/config, call Telegram, expose a listener, or publish a secret. The
VPS remains on `1c7fb78`; all five stop-lines remain false.

## Next Gate

```text
REVIEW_ECF8563_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_GATE
```

That review must define checksum-bound upload, source and SQLite snapshots,
offline apply, web-only restart, authenticated read-only `/plans` smoke,
loopback/API verification, bot-stays-disabled checks, and automatic rollback.
Submitting a quota form remains outside that gate unless separately and
explicitly approved.
