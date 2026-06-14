# After Phase 6: Fresh Installer Evidence Readiness

Дата: 2026-06-13.

Статус: `FI-N001 + FI-N002 + FI-S001` completed as AMN2 local-only
code/tests/docs.

## Summary

AMN2 branch `codex-vps-test-prep` advanced to:

```text
525a9cd Add fresh installer evidence readiness
```

This slice completes the local-only docs/test evidence readiness layer for the
future clean installer:

- smoke/evidence template contract;
- existing-server reconciliation input contract;
- operator docs index.

## Implemented

AMN2 changes:

- `app/services/fresh_install_wizard.py`
  - adds `fresh-install-evidence.v1`;
  - adds `installer_evidence.smoke_evidence_template`;
  - adds report-only existing-server reconciliation input;
  - adds rendered phases for smoke evidence, reconciliation input and docs index.
- `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`
  - indexes wizard, secret handoff, destructive cleanup gate, reconciliation
    checklist and runtime/toolchain docs.
- `docs/FRESH_INSTALL_WIZARD.ru.md`
  - documents evidence template, reconciliation input and docs index.
- `tests/services/test_fresh_install_wizard.py`
  - verifies no-secret evidence template, report-only reconciliation input and
    docs index existence.

## Verification

RED:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py -v
result: 3 failed, 8 passed
failures: missing installer_evidence, rendered evidence phases and operator index doc
```

GREEN focused:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\cli\test_fresh_install_wizard_cli.py -v
result: 13 passed
```

GREEN full:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 719 passed, 1 StarletteDeprecationWarning
```

Git checks:

```text
git diff --check
git diff --cached --check
result: passed
```

## Safety Boundary

Not performed:

- live VPS command;
- SSH command;
- live smoke execution;
- package rebuild/apply/upload on VPS;
- service restart/deploy;
- public exposure;
- config delivery, `.conf`, QR or `vpn://`;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive cleanup/reinstall;
- Telegram token use, live bot send or identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains default. AMN2 `525a9cd` is local-only and not
package-rebuilt or VPS-smoked. Latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`.

## Plan Update

Completed and removed from the active recommendation:

- `FI-N001` Smoke/evidence template;
- `FI-N002` Existing-server reconciliation input;
- `FI-S001` Installer docs index.

Remaining local-only clean installer candidate:

```text
FI-X001 Russian-first prompt copy polish.
```

The operator also requested the next work item immediately after this slice:

```text
P6-C001 + P6-C002 docs-only checklist refresh,
without opening public/config gates.
```
