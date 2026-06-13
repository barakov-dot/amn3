# After Phase 6: Fresh Installer Plan Renderer

Дата: 2026-06-13.

Статус: `FI-I001 + FI-I002 + FI-I003` completed as AMN2 local-only
code/tests/docs.

## Summary

AMN2 branch `codex-vps-test-prep` advanced to:

```text
de635a0 Add fresh installer plan renderer
```

This slice hardens the clean installer planning path without opening live,
destructive, public, config-delivery or write gates.

Implemented in AMN2:

- `build_fresh_install_manifest()` with versioned question and answer schemas;
- `fresh-install-plan.v1` in `build_fresh_install_plan()`;
- rendered operator plan phases: local preflight, secret handoff checklist,
  question-answer render and named-gate stop;
- explicit `requires_named_gates` mapping for `P6-C001`, `P6-C002`,
  `P6-C003` and `P6-C007`;
- `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`;
- `scripts/test.ps1` as the canonical Windows/Codex Desktop test wrapper.

## Runtime Fix

The recurring local test issue was documented and fixed operationally:

- system `python` may point to unsupported CPython 3.14;
- AMN2 supports CPython `>=3.12,<3.13`;
- current Codex Desktop checkout uses `.codex_deps` plus bundled CPython
  `3.12.13`;
- `scripts/test.ps1` chooses `.venv` first, then bundled Codex CPython 3.12,
  sets `PYTHONPATH=.codex_deps;.` and runs `app.toolchain check` before pytest.

The Windows `CreateProcessAsUserW failed: 5` issue is treated as a Codex
Desktop sandbox runner issue, not an AMN2 project failure. Read-only local
commands may be retried through explicit safe prefix rules.

## Verification

RED:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py -v
result: ImportError for missing build_fresh_install_manifest

powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py::test_fresh_install_secret_handoff_policy_doc_exists -v
result: failed because docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md was missing
```

GREEN focused:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py tests\cli\test_fresh_install_wizard_cli.py -v
result: 8 passed
```

GREEN full:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 714 passed, 1 StarletteDeprecationWarning
```

Git checks:

```text
git diff --cached --check
result: passed after removing trailing EOF whitespace
```

## Safety Boundary

Not performed:

- live VPS command;
- SSH command;
- package rebuild/apply/upload on VPS;
- service restart/deploy;
- public exposure;
- real config delivery, `.conf`, QR or `vpn://`;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive cleanup/reinstall;
- Telegram token use, live bot send or Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the default. AMN2 `de635a0` is local-only and
not package-rebuilt or VPS-smoked. Latest VPS-smoked/package head remains
`c46f664 Add public taxonomy cleanup checklist`.

## Plan Update

Completed and removed from the active recommendation:

- `FI-I001` Installer question model hardening;
- `FI-I002` Install plan renderer;
- `FI-I003` Secret handoff checklist binding.

Next recommended triple:

```text
FI-M001 + FI-M002 + FI-M003 as local-only preflight/runtime/package planning,
without live/destructive/public/config/write work.
```
