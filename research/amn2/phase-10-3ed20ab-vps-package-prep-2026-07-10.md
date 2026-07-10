# Phase 10 3ed20ab VPS package preparation

Date: 2026-07-10.

Status: `completed-local-package-ready-not-vps-smoked`.

## Source

```text
branch=codex-vps-test-prep
product_commit=466e0bc
policy_test_followup_commit=3ed20ab
release_head=3ed20abfaa24d7ad2d3b72ff0c0a92dd10b823ab
working_tree=clean
origin_sync=done
current_vps_overlay=e7f6246
```

The source ZIP was created directly with `git archive` from the clean full
release commit. The follow-up includes the required route-policy and VPS-write
retest assertions that were detected as an unstaged test diff during package
preflight.

## Artifacts

```text
package=dist/amn2-vps-update-and-smoke-kit-3ed20ab.zip
package_sha256=8B16853A7BCD9DC012A851C1174A9CB743A2A531369B96F7238BC6719B0D80D8
package_sha256_file=dist/amn2-vps-update-and-smoke-kit-3ed20ab.zip.sha256.txt
source_zip=dist/amn2-vps-update-and-smoke-kit-3ed20ab/amn2-codex-vps-test-prep-3ed20ab-source.zip
source_sha256=F2F6AC74FD9311E72B9098DD2472841DFB8CAE804D5901A3DDD0F38CB3DE1066
source_sha256_file=dist/amn2-vps-update-and-smoke-kit-3ed20ab/amn2-codex-vps-test-prep-3ed20ab-source.zip.sha256.txt
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
toolchain=AMN2 toolchain ok CPython 3.12.x
focused_from_extracted_source=41 passed, 1 warning
full_from_extracted_source=772 passed, 1 skipped, 1 warning
```

The skip is the POSIX `0600` assertion on Windows. The warning is the known
FastAPI/Starlette test-client deprecation warning.

## Boundary

No VPS command, SSH command, package upload/apply, source overlay, service
restart, peer/user mutation, config generation/delivery, public exposure,
Telegram action or secret publication was performed.

The package requires `VPS_APPLY_ENABLED=false` and
`OPERATOR_DEVICE_CREATE_ENABLED=false` during source-overlay smoke. Android TV
import/connect remains `pending_physical_device`; device `8` was not modified.

## Next Gate

```text
vps_source_overlay_web_activation=completed-pass
evidence=research/amn2/phase-10-3ed20ab-vps-source-overlay-web-activation-2026-07-10.md
next=START_PHASE10_INTEGRATION_API_KEY_REGISTRY_SLICE
```

Source overlay, loopback smoke and separately observed private web activation
passed with both product-write flags remaining false. Continue with the
integration/API-key registry product slice and then the Telegram operator
workflow.
