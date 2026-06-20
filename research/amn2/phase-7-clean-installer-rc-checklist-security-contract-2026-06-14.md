# Phase 7 P7-I002 + P7-M002 + P7-I003 clean installer RC checklist/security contract

Дата: 2026-06-14.

Статус: `local-only-rc-checklist-complete`.

This closes:

- `P7-I002` Clean installer RC acceptance checklist;
- `P7-M002` Package asset/runbook path verification integration;
- `P7-I003` Installer secret/input contract hardening.

## Scope

The work was done in AMN2 local code/tests/docs and AMN3 evidence/status only.
No live VPS gate was opened.

## AMN2 Changes

AMN2 branch:

```text
codex-vps-test-prep
```

AMN2 base head at start:

```text
b121865 Add multi instance conflict model
```

Changed local AMN2 files:

```text
app/services/fresh_install_wizard.py
tests/services/test_fresh_install_wizard.py
docs/FRESH_INSTALL_WIZARD.ru.md
docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md
```

Implemented local-only RC surfaces:

- `clean_installer_rc_acceptance` schema
  `clean-installer-rc-acceptance.v1`;
- Phase 7 gate IDs in fresh installer questions and stop-lines:
  `P7-C002`, `P7-C003`, `P7-C005`, `P7-C004`;
- current-head package preflight aligned to `b121865` with known-good VPS head
  `0de7a77`;
- package asset path preflight artifacts for the `b121865` AMN3 package;
- package-local helper default binding checks for commit and source SHA256;
- `secret_input_contract` with `raw_secret_input_allowed=false`;
- secret-bearing installer answer rejection before plan rendering, with
  field-only error text and no value echo.

## Package/Runbook Path Contract

The fresh installer manifest now records the Phase 7 RC package paths:

```text
package_zip: dist/amn2-vps-update-and-smoke-kit-b121865.zip
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-b121865.zip.sha256.txt
source_zip: dist/amn2-codex-vps-test-prep-b121865-source.zip
source_sha256_file: dist/amn2-codex-vps-test-prep-b121865-source.zip.sha256.txt
operator_runbook: dist/amn2-vps-update-and-smoke-kit-b121865/AMN2_VPS_UPDATE_AND_SMOKE_b121865.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-b121865/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-b121865/amn2_api_loopback_smoke.sh
```

Helper binding evidence:

```text
source_zip_commit: b121865
source_sha256: D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647
expected_commit: b121865
```

## TDD Evidence

RED focused test:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests/services/test_fresh_install_wizard.py -v
result: 6 failed, 10 passed
expected failures: old ff77d4c/c46f664 package heads, missing RC acceptance,
missing asset helper binding check, missing secret-bearing answer rejection
```

GREEN focused test:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests/services/test_fresh_install_wizard.py -v
result: 16 passed
```

Expanded local verification:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests/services/test_fresh_install_wizard.py tests/cli/test_fresh_install_wizard_cli.py tests/test_file_hygiene.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -v
result: 52 passed
```

Full AMN2 suite first run found one safe-payload regression:

```text
result: 1 failed, 726 passed, 1 StarletteDeprecationWarning
failed: tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit
root cause: safe metadata category names contained forbidden marker words `private` and `authorization`
fix: category names changed to avoid forbidden substrings without weakening the integration-status test
```

Regression verification:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit tests/services/test_fresh_install_wizard.py -v
result: 17 passed, 1 StarletteDeprecationWarning
```

Final AMN2 full suite:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 727 passed, 1 StarletteDeprecationWarning
```

## Safety

No live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

## Outcome

Closed from active Phase 7 plan:

- `P7-I002`;
- `P7-M002`;
- `P7-I003`.

Recommended next local-only bundle:

```text
P7-M003 + P7-N002
```

Alternative single:

```text
P7-M003
```

Alternative triple:

```text
P7-M003 + P7-N002 + P7-S002
```
