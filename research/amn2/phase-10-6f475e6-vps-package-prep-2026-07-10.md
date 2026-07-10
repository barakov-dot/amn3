# Phase 10 6f475e6 VPS package preparation

Date: 2026-07-10.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
branch=codex-vps-test-prep
release_head=6f475e6ef3c3610be9de971ef7f18c5e9d6d19ee
subject=Add integration credential registry
working_tree=clean
origin_sync=done
current_vps_overlay=3ed20ab
```

The source ZIP was created directly with `git archive` from the clean pushed
release commit.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-6f475e6.zip
package_sha256=0B67CD3AB4ABFC2F74772B7D3F247D9730136DA5AB571E890F3A77D2873939BC
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-6f475e6.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-6f475e6/amn2-codex-vps-test-prep-6f475e6-source.zip
source_sha256=BEDFDBE04CA40DA21A51B1ACAB4C0C21BD7F5EC408A77D1223664EAAAF673FFF
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-6f475e6/amn2-codex-vps-test-prep-6f475e6-source.zip.sha256.txt
```

## Verification

```text
package_entries=5
source_entries=349
source_files=306
source_dirs=43
required_missing=0
forbidden_entries=0
package_sha256=matched
source_sha256=matched_before_and_after_extract
apply_commit_binding=passed
apply_sha_binding=passed
smoke_commit_binding=passed
dual_default_false_gate_binding=passed
shell_lf_no_bom=true
toolchain=AMN2_toolchain_ok_CPython_3.12.13
focused_from_extracted_source=73_passed_1_warning
full_from_extracted_source=774_passed_1_skipped_1_warning
source_overlay_tooling=2_passed
```

The skip is the existing POSIX `0600` assertion on Windows. The warning is the
known FastAPI/Starlette TestClient deprecation warning.

## Boundary

No VPS/SSH command, package upload/apply, source overlay, service restart,
credential issue/rotate/revoke, peer/user mutation, config generation/delivery,
public exposure, Telegram action or secret publication was performed during
package preparation.

The approved live scope keeps `VPS_APPLY_ENABLED=false` and
`OPERATOR_DEVICE_CREATE_ENABLED=false`, promotes tracked source only, runs
read-only loopback smoke and activates the private loopback web service. Android
TV import/connect remains `pending_physical_device`; device `8` is not modified.

## Next Gate

```text
vps_source_overlay_web_activation=completed-pass
evidence=research/amn2/phase-10-6f475e6-vps-source-overlay-web-activation-2026-07-10.md
next=START_PHASE10_TELEGRAM_OPERATOR_READ_ONLY_STATUS_SLICE
```
