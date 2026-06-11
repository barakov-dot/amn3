# Phase 5 Runtime/toolchain Standardization Evidence 2026-06-11

## Summary

`P5-I003` completed as an AMN2 local-only slice.

Purpose: stop relying on a neighboring worktree `.venv` and make the supported
local runtime explicit before any future package rebuild, VPS deploy or live
write/config gate.

## AMN2 Result

Repository: `barakov-dot/amn2`

Branch:

```text
codex/runtime-toolchain-standardization
```

Commit:

```text
578d91e Add runtime toolchain standardization
```

Integration branch:

```text
amn2/codex-vps-test-prep
```

The integration branch was fast-forwarded from `137d471` to `578d91e`.

## Changes

- `pyproject.toml` now pins the supported runtime to `>=3.12,<3.13`.
- `app.toolchain` exposes a machine-checkable runtime contract and CLI:
  `python -m app.toolchain check`.
- `docs/RUNTIME_TOOLCHAIN.ru.md` documents CPython 3.12.x bootstrap, local
  `.venv` creation and full-suite commands.
- The Windows workflow now explicitly says to create one `.venv` per worktree
  and not use `.venv` from a neighboring worktree.
- README and beginner guide point operators toward CPython 3.12.x and the
  toolchain check.
- `tests/test_runtime_toolchain.py` verifies the pyproject pin, helper behavior
  and reproducible local commands.

## Verification

RED step:

```text
tests/test_runtime_toolchain.py failed before implementation:
ModuleNotFoundError: No module named 'app.toolchain'
```

Focused tests after implementation:

```text
tests/test_runtime_toolchain.py -v
result: 4 passed
```

Runtime/hygiene regression:

```text
tests/test_runtime_toolchain.py tests/test_file_hygiene.py tests/deploy/test_runtime_registry.py -v
result: 19 passed
```

Toolchain check:

```text
python -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

Full local AMN2 suite:

```text
pytest tests -q
result: 658 passed, 1 warning
```

Known warning:

```text
StarletteDeprecationWarning from fastapi.testclient/httpx compatibility.
```

Git checks:

```text
git diff --check: passed
git diff --cached --check: passed
```

## Safety Boundary

No live VPS command, SSH command, service restart, deploy, package apply,
production peer/user mutation, public exposure, `/api/clients` CRUD, config
delivery, Local Agent mutation, backup/import/reboot, destructive provider
action or upstream code copy was performed.

This slice does not authorize Python 3.14 migration. Python 3.14 remains a
separate future upgrade gate requiring dependency rebuild and full-suite
verification.

## Follow-up Recommendation

The original next safe local-only recommendation, `P5-I002` external-only
backfill rehearsal on a local DB copy, was completed later in
`research/amn2/phase-5-external-only-backfill-rehearsal-2026-06-11.md`.
`P5-I004` operator-only smoke checklist was also completed later in
`research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.

Current next safe local-only recommendation: `P5-M003` AMN3 evidence
discipline.
