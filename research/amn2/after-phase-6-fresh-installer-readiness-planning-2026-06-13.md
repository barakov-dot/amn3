# After Phase 6: Fresh Installer Readiness Planning

Дата: 2026-06-13.

Статус: `FI-M001 + FI-M002 + FI-M003` completed as AMN2 local-only
code/tests/docs.

## Summary

AMN2 branch `codex-vps-test-prep` advanced to:

```text
7416fb0 Add fresh installer readiness planning
```

This slice extends the fresh installer planning contract with local-only
readiness metadata:

- `fresh-install-readiness.v1`;
- target OS/runtime preflight matrix;
- runtime mode decision for `docker` / `host_systemd`;
- package hygiene checklist for future package gates;
- rendered plan phases for preflight, runtime and package hygiene.

## Implemented

AMN2 changes:

- `app/services/fresh_install_wizard.py`
  - adds `installer_readiness`;
  - adds read-only target checks: OS release, CPython 3.12.x, Docker runtime,
    ports, disk, time sync and package/archive tools;
  - records runtime decision from operator answer;
  - keeps service restart disabled;
  - records package hygiene checks without enabling package rebuild.
- `tests/services/test_fresh_install_wizard.py`
  - adds RED/GREEN coverage for readiness manifest and rendered phases.
- `docs/FRESH_INSTALL_WIZARD.ru.md`
  - documents readiness schema, local-only preflight matrix, runtime decision
    and package hygiene boundary.

## Verification

RED:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py -v
result: 2 failed, 6 passed
failures: missing installer_readiness and target-preflight-matrix rendered phase
```

GREEN focused:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\cli\test_fresh_install_wizard_cli.py -v
result: 10 passed
```

GREEN full:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 716 passed, 1 StarletteDeprecationWarning
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
- target diagnostic execution;
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

`VPS_APPLY_ENABLED=false` remains default. AMN2 `7416fb0` is local-only and not
package-rebuilt or VPS-smoked. Latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`.

## Plan Update

Completed and removed from the active recommendation:

- `FI-M001` Target OS/runtime preflight matrix;
- `FI-M002` Runtime mode decision;
- `FI-M003` Package hygiene integration.

Next recommended triple:

```text
FI-N001 + FI-N002 + FI-S001 as local-only docs/test evidence readiness,
without live/destructive/public/config/write work.
```
