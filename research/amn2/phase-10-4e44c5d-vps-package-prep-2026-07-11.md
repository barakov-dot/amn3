# Phase 10 4e44c5d VPS package preparation

Date: 2026-07-11.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
branch=codex-vps-test-prep
release_head=4e44c5d36f64d01f2d1afae5c6fd72e37c3dc22d
subject=Add controlled Telegram start smoke
working_tree=clean
origin_sync=done
current_vps_overlay=34b3b43
```

The source ZIP was created directly with `git archive` from the clean pushed
release commit. No working-tree or untracked file was added to the source.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-4e44c5d.zip
package_sha256=28447A7385A24BC01221DED073FAE1B4C6E583BBD6824F64E4D2DF4D0B294F13
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-4e44c5d.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-4e44c5d/amn2-codex-vps-test-prep-4e44c5d-source.zip
source_sha256=4E34EB736775749467BDD5E0DA20758F46B8F10224871091C96778E960A040FA
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-4e44c5d/amn2-codex-vps-test-prep-4e44c5d-source.zip.sha256.txt
```

The outer package contains exactly five entries: source ZIP, source checksum,
apply tool, loopback API smoke tool and operator runbook.

## Content Review

```text
package_entries=5
source_entries=357
source_files=314
source_dirs=43
required_missing=0
forbidden_entries=0
package_content_mismatches=0
source_sha=matched
package_sha=matched
checksum_manifest_contents=matched
apply_commit_and_sha_binding=passed
smoke_commit_binding=passed
runbook_full_commit_binding=passed
apply_old_default_binding_count=0
smoke_old_default_binding_count=0
runbook_previous_overlay_binding=34b3b43_exact_once
apply_nonbinding_canonical_diff_count=0
smoke_nonbinding_canonical_diff_count=0
shell_lf_no_bom=true
bash_syntax=passed
operator_markdown_hygiene=passed
```

The source archive includes the new controlled runner, CLI entry, shared
workflow helper and its regression tests. It excludes `.git`, live `.env`,
`servers.yml`, runtime data, virtual environments, bytecode and cache entries.

The only old commit occurrence is the intentional
`previous_vps_overlay=34b3b43` runbook field. Neither executable shell tool
contains an old default binding.

## Extracted-Source Verification

The package was expanded into a separate directory without Git metadata. Tests
used the AMN2 CPython `3.12.13` environment and a read-only Git metadata
binding to commit `4e44c5d` only for tests that call `git rev-parse`.

```text
focused_from_extracted_source=24_passed
full_from_extracted_source=810_passed_1_skipped_1_warning
source_overlay_tooling=2_passed
phase9_progress_harness=14_passed|package_product_and_docs_scope_passed
```

The warning is the pre-existing Starlette `TestClient` deprecation warning for
the installed `httpx` compatibility layer. No package-specific warning or test
failure remains.

## Boundary

No VPS/SSH command, package upload/apply, source overlay, service restart,
Telegram API request, bot startup/send/polling, credential mutation,
peer/config action, Android TV action, public exposure or secret publication
was performed. Both write gates remain false by package contract. The regular
bot unit is expected to remain inactive and disabled. Android TV device `8`
remains pending physical acceptance.

## Next Gate

```text
START_PHASE10_4E44C5D_PRIVATE_VPS_SOURCE_OVERLAY_UPLOAD_GATE_REVIEW
```

Review the checksum-bound upload, pre-apply snapshot, SQLite backup, source
apply, read-only smoke and rollback scope separately. Controlled Telegram
polling still requires another explicit approval after the hardened source is
active on the VPS.
