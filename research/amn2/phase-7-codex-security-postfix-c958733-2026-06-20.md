# Phase 7 Codex Security post-fix validation for AMN2 c958733

Date: 2026-06-20.

Status: `completed-post-fix-security-validation-no-open-findings`.

Scope: AMN2 repository/worktree `codex-vps-test-prep`, post-fix commit
`c9587332d425583ed627899d7fa950756b64c4dc`
(`Harden security-sensitive operations`).

## Summary

Codex Security review found and remediated security-sensitive operation issues
after the `5501295` RC gates:

- CLI live peer apply/revoke now requires `VPS_APPLY_ENABLED=true`.
- Telegram admin delivery-failure fallback no longer sends secret-bearing config
  payloads/import links to admin chat.
- SMTP `STARTTLS` now uses an explicit verifying SSL context.
- Backup artifacts are chmodded to `0600` after write.
- Runtime debug snapshot port greps validate numeric ports and no longer use
  `bash -lc` string execution for environment-derived ports.

The fixes were committed and pushed to AMN2:

```text
c958733 Harden security-sensitive operations
origin/codex-vps-test-prep updated from 5501295 to c958733
```

## Verification

Local AMN2 verification used Python `3.12.13` from an existing AMN2 venv:

```text
Focused pytest set: 95 passed
Full pytest suite: 729 passed, 1 unrelated FastAPI/TestClient deprecation warning
git diff --check: passed before commit
```

Codex Security post-fix scan:

```text
scan_id=b9106c1d-1f68-493a-91a6-2698303da56e
target_revision=c9587332d425583ed627899d7fa950756b64c4dc
status=complete
reportable_findings=0
report=C:\Users\SooL\AppData\Local\Temp\codex-security-scans-he3cec\amn2-p7-c005-write-install\c9587332d425583ed627899d7fa950756b64c4dc_20260620T112513Z__b47am6m\report.md
```

The earlier `5501295` scan could not be finalized after remediation because
the repository HEAD changed during the scan, so the final completed scan is the
post-fix `c958733` validation scan.

## Boundary

This was local source/security/test work plus GitHub push. It did not perform
live VPS SSH, package upload/apply, service restart, public exposure, config
delivery, write execution, restore/import/reboot, provider mutation, Local Agent
mutation, Telegram send/profile/media mutation or secret-bearing evidence.

## Remaining Follow-Up

The disposable VPS runtime remains on the previously smoked `5501295` package
until a separate exact named gate builds/applies a `c958733` package and reruns
loopback/API/Telegram/backup smoke evidence.
