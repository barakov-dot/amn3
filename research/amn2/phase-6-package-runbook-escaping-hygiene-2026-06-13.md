# Phase 6 P6-X003 package runbook escaping hygiene

Date: 2026-06-13.

Status: `closed`.

Scope: AMN3 docs/tooling hygiene only.

## Decision

```text
task_id: P6-X003
priority: cosmetic
scope: local-only AMN3 docs/tooling hygiene
result: closed
already_smoked_package_rebuilt: no
already_smoked_package_modified: no
live_vps_command: no
ssh_command: no
package_apply_on_vps: no
```

## Why

The already-smoked `c46f664` operator package doc contains a few accidental
ASCII control characters where literal inline-code backticks were intended.
The observed pattern matches PowerShell backtick escapes:

- `` `b `` became `U+0008` before `3102db`;
- `` `a `` became `U+0007` before `mn2_apply_source_zip.sh` and
  `mn2_api_loopback_smoke.sh`;
- `` `v `` became `U+000B` before `pn://`.

The source overlay apply script, API smoke script, checksums and live smoke
result were not affected. Because `dist/amn2-vps-update-and-smoke-kit-c46f664.zip`
is already the evidence package for `P6-C009`, this task intentionally did not
rebuild, repack or alter that artifact.

## What Changed

Added local Markdown/operator-doc hygiene tooling:

```text
scripts/check_markdown_hygiene.py
tests/test_markdown_hygiene.py
```

The checker fails on unexpected ASCII control characters while allowing normal
Markdown whitespace controls: LF, CR and TAB. It also emits targeted hints for
PowerShell backtick escape accidents.

## Verification

RED:

```text
python -m unittest tests.test_markdown_hygiene
result: failed
reason: scripts/check_markdown_hygiene.py was missing
```

GREEN:

```text
python -m unittest tests.test_markdown_hygiene
result: OK
tests: 2
```

Known sealed artifact diagnostic:

```text
python scripts\check_markdown_hygiene.py dist\amn2-vps-update-and-smoke-kit-c46f664\AMN2_VPS_UPDATE_AND_SMOKE_c46f664.ru.md
result: failed as expected
findings: 5
```

This confirms the tool catches the historical defect without changing the
already-smoked package artifact.

## Boundary

This task did not perform:

- live VPS command;
- SSH command;
- package rebuild or repack of the already-smoked `c46f664` package;
- package upload/apply on VPS;
- service restart/deploy;
- public exposure;
- config delivery, `.conf`, QR or `vpn://`;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or Telegram identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Recommendation

Run the hygiene checker against future generated operator Markdown before
packaging new AMN2 VPS update/smoke kits. Historical sealed evidence packages
may be diagnosed but should not be rewritten after live smoke evidence exists.
