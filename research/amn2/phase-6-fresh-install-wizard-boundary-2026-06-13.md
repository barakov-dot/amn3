# AMN2 Phase 6 Fresh Install Wizard Boundary

Дата: 2026-06-13.

Статус: `local-only-code-tests-docs-complete`.

## Scope

Закрыта задача:

```text
P6-I007 Interactive fresh-install wizard/bootstrap automation
```

Это local-only question-and-answer clean installer boundary. Он не выполняет
установку, не чистит VPS, не подключается по SSH и не открывает live gates.

## AMN2 Change

AMN2 branch:

```text
codex-vps-test-prep
```

AMN2 commit:

```text
60d2570 Add fresh install wizard boundary
```

Pushed to:

```text
amn2/codex-vps-test-prep
```

Latest VPS-smoked/package head remains:

```text
b3102db Add client compatibility delivery boundary
```

`60d2570` is local-only and not package-rebuilt/VPS-smoked.

## What Changed

Added `app.services.fresh_install_wizard`:

- default safe answers;
- interactive answer collection;
- JSON plan builder;
- status `fresh_install_wizard_ready` when all gated answers are `no`;
- status `blocked_named_gate_required` when public/config/write/destructive
  answers are `yes`;
- explicit stop-lines for `P6-C001`, `P6-C002`, `P6-C003` and `P6-C007`;
- safety manifest with live VPS commands, SSH, package apply, restart/deploy,
  public exposure, config delivery, write API, Local Agent mutation,
  backup/restore/import, production peer/user mutation, destructive cleanup and
  Telegram identity mutation all disabled;
- local dry-run steps only.

Added CLI commands:

```text
python -m app.cli install wizard --pretty
python -m app.cli install plan --answers fresh-install-answers.json --pretty
```

Added docs:

```text
docs/FRESH_INSTALL_WIZARD.ru.md
```

Updated `/api/integration/status` and web `/integration-status` to expose the
fresh-install wizard boundary and set the next local recommendation to:

```text
P6-N001 public docs/API taxonomy if approved
```

## Verification

RED:

```text
tests/services/test_fresh_install_wizard.py
tests/cli/test_fresh_install_wizard_cli.py

result: 2 import errors as expected
```

GREEN focused:

```text
PYTHONPATH=.codex_deps python -m pytest \
  tests/services/test_fresh_install_wizard.py \
  tests/cli/test_fresh_install_wizard_cli.py \
  tests/services/test_integration_status_service.py \
  tests/api/test_api_integration_status.py \
  tests/web/test_web_integration_status.py

result: 14 passed, 1 StarletteDeprecationWarning
```

Security/hygiene:

```text
PYTHONPATH=.codex_deps python -m pytest \
  tests/security/test_surface_policy.py \
  tests/test_file_hygiene.py

result: 26 passed
```

Toolchain:

```text
python -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

`git diff --check` and staged `git diff --cached --check` passed.

## Safety Boundary

No live VPS command, SSH command, package apply/rebuild on VPS, service
restart/deploy, public exposure, real config delivery, write API, Local Agent
mutation, backup/import/reboot, production peer/user mutation, destructive VPS
action, payment provider integration, Telegram token use, live bot send,
Telegram profile mutation, secret-bearing evidence publication or upstream/GPL
code copy was performed.

`VPS_APPLY_ENABLED=false` remains the default.

## Plan Result

`P6-I007` is removed from the active Phase 6 plan.

`P6-C007` remains critical gated/deferred. The wizard does not authorize cleanup
or reinstall.

Next practical recommendation:

```text
P6-N001 public docs/API taxonomy if approved
```

Alternative pair:

```text
P6-N001 + P6-C007 checklist-only
```

Only as local-only documentation of destructive-gate criteria; not as cleanup.
