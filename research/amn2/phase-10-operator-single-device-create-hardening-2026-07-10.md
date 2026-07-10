# Phase 10 operator single-device create hardening

Date: 2026-07-10.

Status: `completed-code-merged-and-pushed`.

## Source

```text
AMN2 base=codex-vps-test-prep@4326cae
feature_branch=codex/phase10-operator-single-device-create
feature_commit=e7f6246
stable_branch=codex-vps-test-prep
stable_head=e7f6246
merge=fast-forward
push=feature-and-stable-completed
```

## Product Result

The slice replaces the reusable parts of the one-off Android TV gate with a
supported operator-only contract:

- `AccessService.create_operator_device(...)` requires an explicit active owner,
  explicit duration/server/device/config version and a live peer applier;
- device limits, encrypted config material, remote IP inventory/allocation and
  admin audit remain on the common product path;
- configured admins and active DB-admins are accepted as operator actors;
- `device create-operator` has explicit `--dry-run` / `--apply` and
  `--execution-target local|remote-ssh` modes;
- `local` runs Docker mutation on the target VPS without self-SSH;
- `remote-ssh` preserves the existing remote operator path;
- live apply remains blocked unless `VPS_APPLY_ENABLED=true` and an exact
  one-device gate is open;
- private config output is POSIX-only, atomic, `0600` and refuses overwrite;
- non-POSIX apply is rejected before remote mutation instead of pretending that
  `chmod` secures a Windows DACL;
- config payload is never included in CLI stdout;
- remote-applied/local-failed results use the existing structured partial-failure
  contract and attempt a safe reconciliation admin action after rollback.

## Verification

```text
RED=2 expected collection errors for missing service/CLI contracts
focused_initial=24 passed, 1 skipped
focused_hardened=31 passed, 1 skipped
expanded_regression=90 passed, 1 skipped
full_suite=766 passed, 1 skipped, 1 StarletteDeprecationWarning
post_merge_focused=31 passed, 1 skipped
toolchain=AMN2 toolchain ok CPython 3.12.x
file_hygiene=3 passed
diff_check=passed
real_cli_dry_run=passed secret-safe no mutation
status_sync_markdown_hygiene=2 passed
status_sync_progress_harness=12 passed
status_sync_diff_check=passed
status_sync_secret_scan=passed
```

The skipped test is the POSIX `0600` assertion on the Windows development host.
The complementary non-POSIX rejection test passed; the production writer remains
covered for behavior and will require POSIX execution for apply.

## Boundary

This slice performed no VPS SSH, source upload, source-overlay update, peer
creation/revoke, config generation/delivery, Android import, service restart,
public exposure, Telegram send, backup/import/reboot or secret publication.

Existing Android TV device `8` is unchanged. Its ownership remains provisional,
and handshake/traffic acceptance remains pending until the physical device is
available.

At the initial hardening closure, the live VPS source overlay still remained
`4326cae`; `e7f6246` was merged and pushed but not yet packaged or VPS-smoked.
The package/smoke follow-up below later promoted `e7f6246`.

## Package Follow-Up

```text
package_prep=completed-local-package-ready-not-vps-smoked
package=dist/amn2-vps-update-and-smoke-kit-e7f6246.zip
package_evidence=research/amn2/phase-10-e7f6246-vps-package-prep-2026-07-10.md
read_only_vps_upload_smoke=completed-pass
vps_smoke_evidence=research/amn2/phase-10-e7f6246-read-only-vps-source-overlay-smoke-2026-07-10.md
next=START_PHASE10_OPERATOR_DEVICE_CREATE_WEB_UI_SLICE
```

The package is locally verified and its exact VPS source-overlay/loopback smoke
gate passed with `VPS_APPLY_ENABLED=false`. Product write actions remain
separate gates.
