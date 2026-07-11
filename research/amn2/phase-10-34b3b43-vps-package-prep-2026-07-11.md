# Phase 10 34b3b43 VPS package preparation

Date: 2026-07-11.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
branch=codex-vps-test-prep
release_head=34b3b43a87fb673cb966a578d3d5e48533b541fa
subject=Add Telegram integration status
working_tree=clean
origin_sync=done
current_vps_overlay=6f475e6
```

The source ZIP was created directly with `git archive` from the clean pushed
release commit.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-34b3b43.zip
package_sha256=385EAC3DC53B9E9C1EA35F168B01D545177FEC459D948239F93B4D40A64D499C
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-34b3b43.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-34b3b43/amn2-codex-vps-test-prep-34b3b43-source.zip
source_sha256=97D7676B9C349877A8A51C971599C0C886616E9BBB6472749C0C695209BE5179
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-34b3b43/amn2-codex-vps-test-prep-34b3b43-source.zip.sha256.txt
```

## Verification

```text
package_entries=5
source_entries=355
source_files=312
source_dirs=43
required_missing=0
forbidden_entries=0
package_sha=matched
source_sha=matched
package_content_mismatches=0
commit_bindings=passed
shell_lf_no_bom=true
toolchain=AMN2_toolchain_ok_CPython_3.12.13
focused_from_extracted_source=184_passed
full_without_git_binding=793_passed_3_git_metadata_only_failed_1_skipped_1_warning
git_metadata_dependent_recheck=3_passed_1_warning
full_from_extracted_source_with_read_only_34b3b43_binding=796_passed_1_skipped_1_warning
source_overlay_tooling=2_passed
operator_markdown_hygiene=passed
```

The initial standalone full run exposed three tests that directly execute
`git rev-parse`; a clean `git archive` intentionally has no `.git`. Repeating
those tests and the full suite with read-only `GIT_DIR`/`GIT_WORK_TREE`
binding to the source commit passed. No Git metadata was added to the package.

## Boundary

No VPS/SSH command, package upload/apply, source overlay, service restart,
Telegram bot startup/send, credential mutation, peer/config action, Android TV
action, public exposure or secret publication was performed. Both write gates
remain false by package contract. Android TV device `8` remains pending physical
acceptance.

## Next Gate

```text
START_PHASE10_34B3B43_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_GATE_REVIEW
```

Review the private upload/source-overlay scope separately. Only after package
checksum verification and read-only smoke may a distinct Telegram bot runtime
activation gate be considered.
