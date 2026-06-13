# Phase 6 P6-C008 current-head package refresh/preflight c46f664

Date: 2026-06-13.

Status: `package-ready-not-vps-smoked`.

This is the local package/preflight part of `P6-C008` only. It also prepares a
current-head smoke plan and a named live gate checklist. The live VPS
apply/restart/smoke path is not opened and is tracked as future `P6-C009`.

## Source

```text
AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 commit: c46f664762d7774756b88db8d4e1ebc038b20bb5
AMN2 subject: Add public taxonomy cleanup checklist
previous latest VPS-smoked/package head: b3102db Add client compatibility delivery boundary
```

## Artifacts

```text
source zip:
dist/amn2-codex-vps-test-prep-c46f664-source.zip

source sha256:
5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248

package:
dist/amn2-vps-update-and-smoke-kit-c46f664.zip

package sha256:
5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE

package directory:
dist/amn2-vps-update-and-smoke-kit-c46f664/
```

The package contains:

```text
AMN2_VPS_UPDATE_AND_SMOKE_c46f664.ru.md
amn2_api_loopback_smoke.sh
amn2_apply_source_zip.sh
amn2-codex-vps-test-prep-c46f664-source.zip
amn2-codex-vps-test-prep-c46f664-source.zip.sha256.txt
```

## Verification

Local package verification passed:

```text
package_verification=passed
source_sha=5A92EA9BD5B60626F120B5367A02EDDCB742ECF5E6C4FCB8444151BFEB18B248
kit_sha=5C952103B3435E1D30AF7CF0A70C40BC027885F1E860C31089DD4ACA3E8347EE
kit_entries=5
source_entries=337
forbidden_source_entries=0
shell_scripts=LF/no-BOM
apply_script_commit_binding=c46f664762d7774756b88db8d4e1ebc038b20bb5
smoke_script_expected_commit=c46f664
```

Required package/source entries were present, including the API/web/bot files,
integration status, public productization boundary, public docs/API taxonomy,
destructive cleanup checklist and focused regression tests.

AMN2 focused current-head suite on bundled CPython 3.12.13:

```text
11 passed, 1 StarletteDeprecationWarning
```

AMN2 toolchain:

```text
AMN2 toolchain ok: CPython 3.12.x.
```

AMN3 apply-script regression:

```text
Ran 2 tests in 4.514s
OK
```

## Current-head smoke plan

Future live smoke must be opened separately as `P6-C009`. The prepared package
runbook records this exact example phrase:

```text
Открываю P6-C009 live apply/smoke gate для c46f664 на текущем disposable VPS 89.185.80.166.
```

The live plan, once separately opened, is:

1. Confirm target is still the disposable VPS `89.185.80.166`.
2. Confirm latest VPS-smoked/package head is still `b3102db`.
3. Upload only the `c46f664` kit and checksum to the target.
4. Verify checksum before extraction.
5. Extract to `/root/amn2-vps-update-and-smoke-kit-c46f664`.
6. Run `amn2_apply_source_zip.sh` only after target path and stop criteria are
   confirmed.
7. Keep API smoke loopback-only with `AMN2_API_HOST=127.0.0.1`,
   `AMN2_SERVER_NAME=local` and `VPS_APPLY_ENABLED=false`.
8. Run `amn2_api_loopback_smoke.sh`.
9. Collect only safe summary/evidence.
10. If smoke passes, record `c46f664` as latest VPS-smoked/package head; if
    blocked, keep `b3102db` as latest VPS-smoked/package head and record blocker
    evidence.

## Named live gate checklist

Before `P6-C009` can run, record:

- exact operator phrase naming `P6-C009`, commit `c46f664` and target
  `89.185.80.166`;
- package SHA256 and source SHA256 from this evidence;
- stop criteria for checksum mismatch, source overlay failure, import failure,
  listener drift, web/bot inactive state or smoke failure;
- confirmation that no public exposure/config delivery/write API/Local Agent
  mutation/backup-import/destructive cleanup/Telegram identity mutation is
  being opened;
- safe evidence destination and redaction rule: no raw tokens, no config
  material, no peer keys, no endpoint secrets.

## Boundary

Not executed:

- live VPS command;
- SSH command;
- package upload/apply on VPS;
- source overlay on VPS;
- service restart/deploy;
- live bot verification or send;
- public exposure;
- config delivery, `.conf`, QR or `vpn://` delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use or Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the required default for the future loopback
smoke.

## Decision

`c46f664` is now package-ready locally, but not VPS-smoked.

The latest VPS-smoked/package head remains:

```text
b3102db Add client compatibility delivery boundary
```

`P6-C008` is removed from the active Phase 6 plan.

`P6-C009` is added as critical gated/deferred work for optional live
apply/smoke of `c46f664` on the current disposable VPS. It must not run without
the exact separate named gate.

## Next recommendation

The default local-only Phase 6 queue is empty. Practical choices:

- single gated: `P6-C009` named live apply/smoke gate for `c46f664` if the
  operator wants the disposable VPS/bot updated;
- pair docs-only: `P6-C001 + P6-C002` decision checklist refresh, without
  opening public exposure or config delivery;
- triple docs-only: Phase 6 closeout packet + next-chat handoff + fresh
  installer backlog grooming, without live/destructive work.
