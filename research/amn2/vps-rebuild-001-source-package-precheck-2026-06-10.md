# VPS-REBUILD-001: source/package precheck 2026-06-10

Дата: 2026-06-10.

Назначение: выполнить local-only precheck для source/package выбора перед возможным `VPS-REBUILD-001` fresh VPS rebuild. Этот документ не разрешает VPS commands, SSH commands, wipe, reinstall, package apply, service changes, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
precheck_id: VPS-REBUILD-001-SOURCE-PACKAGE-PRECHECK-2026-06-10
gate_name: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
precheck_scope: local-only source/package selection
result: source-precheck-pass-package-pending
AMN2_branch: codex-vps-test-prep
AMN2_remote_tracking: amn2/codex-vps-test-prep
AMN2_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
AMN2_source_commit_short: 1508e3c
current_VPS_smoked_baseline: f7f6131
package_for_1508e3c: not_built
package_hygiene_for_1508e3c: not_run
live_commands_run: no
ssh_commands_run: no
destructive_action_authorized: no
reinstall_authorized: no
secret_publication: none
go_no_go_decision: defer
```

## Local Source State

AMN2 working tree was clean and current on:

```text
branch: codex-vps-test-prep
tracking: amn2/codex-vps-test-prep
head: 1508e3c4a100b76815b29f91757290f1266f813d
```

Recent source line:

```text
1508e3c Merge branch 'codex/phase-4-prvtpro-build-status' into codex-vps-test-prep
8bb6a40 Merge branch 'codex/phase-4-prvtpro-expiration-contracts' into codex-vps-test-prep
dc79666 Add web admin build status page
b2eceeb Show device expiration in web admin
f7f6131 Update integration status for c92 manual prelaunch
```

Delta from the current VPS-smoked baseline `f7f6131` to source candidate `1508e3c`:

```text
app/db/repositories.py
app/services/build_status.py
app/web/app.py
app/web/templates/about.html
app/web/templates/base.html
app/web/templates/user_detail.html
tests/web/test_about.py
tests/web/test_users.py
```

Interpretation: `1508e3c` adds two already-completed local-only PRVTPRO-derived slices on top of the current VPS-smoked `f7f6131` baseline:

- `P4-PRVTPRO-REFRESH-002` expiration-field contract/tests;
- `P4-PRVTPRO-REFRESH-001` read-only About/Version/Build status.

## Local Verification

Command:

```text
$env:PYTHONPATH='.codex_deps;.'; .\.codex_deps\bin\pytest.exe tests/web/test_about.py tests/web/test_users.py tests/api/test_smoke.py tests/test_file_hygiene.py -q
```

Result:

```text
30 passed, 1 warning
warning: expected StarletteDeprecationWarning from TestClient/httpx compatibility
```

AMN2 post-test state:

```text
working_tree: clean
git_diff_check: passed
```

## Package Availability Check

AMN3 `dist/` has historical source/update packages through `f7f6131`, including:

```text
dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
dist/amn2-codex-vps-test-prep-f7f6131-source.zip
```

No local package/source zip for `1508e3c` was found during this precheck. Therefore `1508e3c` is a source candidate only, not yet a package-ready candidate.

Required next local-only package step:

```text
build package/source zip for 1508e3c
record package sha256
record source zip sha256
run package hygiene checks
run test extraction
verify forbidden entries are absent
keep package status package-ready-not-vps-smoked until a later approved VPS gate
```

## Neighboring Branch Intake

Already merged into current `1508e3c` source candidate:

```text
codex/phase-4-prvtpro-expiration-contracts -> b2eceeb
codex/phase-4-prvtpro-build-status -> dc79666
```

Useful neighboring branches not merged into `1508e3c`, but worth mining as separate post-rebuild/local-only candidates:

```text
codex/phase-4-web-panel-user-config-visibility -> a73e845
codex/phase-4-service-mode-status-wording -> 83f6d28
codex/phase-4-read-only-api-status-schema -> b71b8f4
codex/phase-4-endpoint-taxonomy-route-policy-docs -> acf39f8
codex/phase-4-aggregate-metrics-privacy-boundary -> 8b6aef8
codex/phase-4-api-token-lifecycle-boundary -> 22061ea
codex/phase-4-bot-admin-read-only-labels -> c9829b7
```

Security/design branches that should influence package/rebuild policy, but should not be silently merged into the rebuild package without a separate local merge plan:

```text
codex/redaction-coverage-first-slice -> f4bfb51
codex/secret-inventory-registry -> 9ce42f4
codex/backup-import-policy-contract -> afb2702
codex/public-config-delivery-policy-contract -> 2ef3af7
codex/manager-config-export-contract -> 4d4e7a4
codex/local-agent-production-wiring -> d5f30c6
codex/vps-gate-remote-ops-integration -> 1c9c674
```

Recommendation: do not broaden the first fresh-rebuild source beyond `1508e3c` automatically. Use `1508e3c` as the conservative source candidate after package build/hygiene, then bring neighboring Phase 4 improvements as explicit local-only or gated slices.

## Gate Result

```text
source_precheck_status: passed
package_precheck_status: blocked_until_1508e3c_package_build
install_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
install_package: pending-build-and-hygiene
provider_snapshot_confirmation: pending
final_destructive_phrase: not_sent
go_no_go_decision: defer
```
