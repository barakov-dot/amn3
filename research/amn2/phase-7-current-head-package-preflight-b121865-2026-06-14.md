# Phase 7 P7-I001 + P7-M001 current-head package/preflight b121865

Дата: 2026-06-14.

Статус: `package-ready-not-vps-smoked`.

This closes `P7-I001` and `P7-M001` as local-only/package-preflight work.

## Source

```text
AMN2 repo: barakov-dot/amn2
AMN2 branch: codex-vps-test-prep
AMN2 commit: b121865f488821f6fc471c9529fb26e5d7992515
AMN2 subject: Add multi instance conflict model
known-good VPS-smoked/package head: 0de7a77 Polish fresh installer preflight planning
current disposable VPS: 89.185.80.166
```

`b121865` is now package-ready locally, but it was not uploaded, applied,
restarted or smoked on the VPS. The known-good VPS baseline remains `0de7a77`.

## Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-b121865.zip
package_sha256: 364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-b121865.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-b121865-source.zip
source_zip_sha256: D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-b121865-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-b121865/
operator_doc: dist/amn2-vps-update-and-smoke-kit-b121865/AMN2_VPS_UPDATE_AND_SMOKE_b121865.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-b121865/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-b121865/amn2_api_loopback_smoke.sh
```

The package-local apply script defaults are bound to the `b121865` source zip,
source SHA256 and full source commit. The package-local smoke script default
`AMN2_EXPECTED_COMMIT` is bound to `b121865`.

## Package Hygiene

```text
kit_entries: 5
source_entries: 300
missing_required: 0
forbidden_source_entries: 0
shell_lf_no_bom: passed
operator_doc_markdown_hygiene: passed
package_sha_check: passed
source_sha_check: passed
test_extract: passed
test_extract_dir: tmp/package-preflight-b121865
```

Required kit entries were present:

```text
AMN2_VPS_UPDATE_AND_SMOKE_b121865.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-b121865-source.zip
amn2-codex-vps-test-prep-b121865-source.zip.sha256.txt
```

## Verification

AMN2 focused RC-relevant suite:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests/services/test_fresh_install_wizard.py tests/vpn/test_ipam.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py -v
result: 56 passed, 1 StarletteDeprecationWarning
```

AMN2 full suite:

```text
powershell.exe -ExecutionPolicy Bypass -File scripts\test.ps1 tests -v
result: 724 passed, 1 StarletteDeprecationWarning
```

AMN2 whitespace:

```text
git diff --check
result: passed

git diff --cached --check
result: passed
```

AMN3 package/apply-script and markdown hygiene tests:

```text
python -m unittest tests.test_amn2_apply_source_zip tests.test_markdown_hygiene
result: 4 tests OK
```

Operator doc hygiene:

```text
python scripts\check_markdown_hygiene.py dist\amn2-vps-update-and-smoke-kit-b121865\AMN2_VPS_UPDATE_AND_SMOKE_b121865.ru.md
result: passed
```

## Known-Good Alignment

The Phase 7 known-good VPS baseline remains:

```text
known_good_vps_head: 0de7a77 Polish fresh installer preflight planning
known_good_evidence: research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
known_good_package: dist/amn2-vps-update-and-smoke-kit-0de7a77.zip
```

The `b121865` package is a current-head RC candidate only. Updating the
disposable VPS from `0de7a77` to `b121865` remains `P7-C001` and requires a
separate exact named live gate phrase:

```text
Открываю P7-C001 live package/apply/smoke gate для b121865 на текущем disposable VPS 89.185.80.166.
```

## Safety

No live VPS command, SSH command, package upload/apply on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram action, secret publication or
upstream/GPL code copy was performed.

## Outcome

Closed from active Phase 7 plan:

- `P7-I001` Current-head release-candidate package/preflight for `b121865`;
- `P7-M001` Known-good snapshot/runbook alignment.

Recommended next local-only bundle:

```text
P7-I002 + P7-M002
```

Alternative triple:

```text
P7-I002 + P7-M002 + P7-I003
```
