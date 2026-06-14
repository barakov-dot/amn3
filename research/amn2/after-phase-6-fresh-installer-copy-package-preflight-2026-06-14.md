# AMN2 After Phase 6 Fresh Installer Copy And Package Preflight Planning

Дата: 2026-06-14.

Статус: `FI-X001 + current-head package preflight planning` completed as AMN2
local-only code/tests/docs.

## AMN2 Commit

```text
0de7a77 Polish fresh installer preflight planning
```

Branch:

```text
barakov-dot/amn2 codex-vps-test-prep
```

Latest VPS-smoked/package head remains:

```text
c46f664 Add public taxonomy cleanup checklist
```

`0de7a77` is local-only and not package-rebuilt/VPS-smoked.

## Scope

This slice closes the remaining clean-installer copy item and adds local-only
current-head package preflight planning.

AMN2 changes:

- fresh installer prompts are Russian-first while stable technical IDs stay the
  same;
- `fresh-install-package-preflight.v1` is added to the manifest and rendered
  plan;
- the package preflight planning records target head `ff77d4c` and latest
  VPS-smoked head `c46f664`;
- package build, live apply and live smoke remain disabled by default;
- docs `docs/FRESH_INSTALL_WIZARD.ru.md` and
  `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md` record the boundary.

## Verification

RED:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py -v
result: 3 failed, 9 passed
```

Failures were expected: English prompts and missing
`current_head_package_preflight` fields.

GREEN focused:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests\services\test_fresh_install_wizard.py -v
result: 12 passed
```

Full AMN2 suite:

```text
powershell -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 721 passed, 1 StarletteDeprecationWarning
```

Hygiene:

```text
git diff --check
git diff --cached --check
result: passed
```

## Safety

No live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive
action, Telegram action, secret publication or upstream/GPL code copy was
performed.

## Next Recommendation

Recommended pair:

```text
Local package build/preflight for 0de7a77 + next-chat handoff refresh
```

Scope: local package/hygiene only, without live apply/smoke.

Gated alternative:

```text
Live apply/smoke for 0de7a77
```

Only after a separate exact named gate phrase.
