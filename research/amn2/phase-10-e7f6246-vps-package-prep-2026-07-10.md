# Phase 10 e7f6246 VPS package preparation

Date: 2026-07-10.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
repo=amn2
branch=codex-vps-test-prep
commit=e7f62461af69ceaef175093242349f4aa3496239
subject=Harden operator single device creation
working_tree=clean
origin_sync=done
current_live_vps_overlay=4326cae
```

The source ZIP was created directly with `git archive` from the exact full
commit. No uncommitted worktree content was included.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-e7f6246.zip
package_sha256=17988115CEBD7CA5D924300506259CE4DB7161DBB1980D248892E4A7CF7DA72E
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-e7f6246.zip.sha256.txt
package_dir=dist/amn2-vps-update-and-smoke-kit-e7f6246/
source_zip=dist/amn2-vps-update-and-smoke-kit-e7f6246/amn2-codex-vps-test-prep-e7f6246-source.zip
source_sha256=FE980BDBC209ED339B33231BCABD42000E2DA6910791DAA8ABA85620A099B0EE
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-e7f6246/amn2-codex-vps-test-prep-e7f6246-source.zip.sha256.txt
```

Package entries:

```text
AMN2_VPS_UPDATE_AND_SMOKE_e7f6246.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-e7f6246-source.zip
amn2-codex-vps-test-prep-e7f6246-source.zip.sha256.txt
```

## Verification

```text
toolchain=AMN2 toolchain ok CPython 3.12.x
focused_from_extracted_source=31 passed, 1 skipped
full_suite_from_extracted_source=766 passed, 1 skipped, 1 StarletteDeprecationWarning
package_entries=5
source_entries=348
source_files=305
source_dirs=43
required_source_entries_missing=0
forbidden_source_entries=0
package_sha256=matched
source_sha256=matched_before_and_after_extract
test_extract=passed
apply_commit_binding=passed
apply_sha_binding=passed
smoke_commit_binding=passed
shell_scripts_lf_no_bom=true
```

The skipped test is the POSIX `0600` assertion on the Windows development host.
Its complementary non-POSIX rejection test passed. The warning is the known
FastAPI/Starlette test-client deprecation warning.

## Upstream Continuity

This release lane remains connected to the upstream research streams, but uses
them as requirement and threat-model inputs rather than copied implementation:

- PRVTPRO informs operator web-panel domains, one-time token UX, self-service
  boundaries, sharing and Telegram delivery risks;
- KYORESUAS informs API taxonomy, lifecycle states, serialized/atomic writes,
  rate limiting, headers and config/QR compatibility checks;
- official Amnezia clients inform import naming, format compatibility and
  physical-device acceptance tests;
- AMN2 keeps its own database, service layer, scoped token policy, audit model,
  private operator panel and Telegram delivery contracts.

GPL/upstream source, UI, templates, workflows and broad shared-key security
models were not copied into this package.

## Boundary

No VPS command, SSH command, upload, source overlay, package apply, service
restart, public exposure, peer/user mutation, config generation/delivery,
Telegram action or secret publication was performed.

Android TV import/connect remains `pending_physical_device`. Existing device `8`
was not modified. At package-prep closure the live VPS source overlay still
remained `4326cae`; the follow-up below later promoted `e7f6246`.

## Next Step

```text
read_only_vps_upload_smoke=completed-pass
evidence=research/amn2/phase-10-e7f6246-read-only-vps-source-overlay-smoke-2026-07-10.md
next=START_PHASE10_OPERATOR_DEVICE_CREATE_WEB_UI_SLICE
```

The package has now passed its exact VPS source-overlay and loopback smoke gate.
Product write actions remain separate gates.
