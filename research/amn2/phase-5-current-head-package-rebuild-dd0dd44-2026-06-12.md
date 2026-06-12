# Phase 5 P5-C006 current-head package rebuild dd0dd44

Date: 2026-06-12.

Scope: local AMN3 package rebuild for current AMN2 head after `P5-N003`.

Result: `package-ready-not-vps-smoked`.

This slice does not authorize live VPS apply by itself. Any upload, source overlay, service restart or read-only loopback smoke on the disposable test VPS remains a separate named gate.

## Source

```text
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 branch: codex-vps-test-prep
AMN2 commit: dd0dd442f0f25c1113accdc625dd16a96059eba4
AMN2 commit short: dd0dd44
AMN2 subject: Refresh client platform guidance
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip
package_sha256: BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-dd0dd44.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-dd0dd44-source.zip
source_zip_sha256: E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-dd0dd44-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-dd0dd44/
operator_doc: dist/amn2-vps-update-and-smoke-kit-dd0dd44/AMN2_VPS_UPDATE_AND_SMOKE_dd0dd44.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-dd0dd44/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-dd0dd44/amn2_api_loopback_smoke.sh
```

Package entries:

```text
AMN2_VPS_UPDATE_AND_SMOKE_dd0dd44.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-dd0dd44-source.zip
amn2-codex-vps-test-prep-dd0dd44-source.zip.sha256.txt
```

## Local Verification

AMN2 toolchain:

```text
command: python -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

AMN2 full suite:

```text
command: PYTHONPATH=.codex_deps python -m pytest -q
result: 664 passed, 1 warning in 63.16s
warning: known StarletteDeprecationWarning
```

AMN2 source hygiene:

```text
git diff --check: passed
```

Package hygiene:

```text
package_sha256: matched .sha256.txt
source_sha256: matched .sha256.txt
package_entries: 5
source_files: 271
source_dirs: 0
required_source_entries: present
forbidden_source_entries: absent
shell_scripts_lf_no_bom: true
commit_bindings: present
test_extract: passed
test_extract_dir: C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p5-c006-dd0dd44-extract-20260612192633
```

Required source entries verified present:

```text
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
app/services/build_status.py
app/bot/delivery.py
app/bot/texts.py
app/web/templates/about.html
app/vpn/client_compatibility.py
tests/web/test_about.py
tests/web/test_users.py
tests/bot/test_delivery.py
tests/vpn/test_client_compatibility.py
```

Forbidden source entries verified absent:

```text
exact: .env, server.yml, servers.yml
prefixes: .git/, data/, venv/, .venv/, logs/, tmp/, __pycache__/, .pytest_cache/, .codex_deps/
suffixes: .sqlite3, .db, .key, .pem
```

## Package Quality Adjustment

The first local hygiene pass caught weak operator-kit binding, not a source-zip problem:

```text
apply script missing full commit binding
operator doc missing explicit Russian no-live-apply phrase
```

The generated kit was tightened locally before final packaging:

- `amn2_apply_source_zip.sh` now defaults `AMN2_EXPECTED_SOURCE_COMMIT` to the full `dd0dd442f0f25c1113accdc625dd16a96059eba4`;
- the operator runbook now states in Russian that the archive/runbook do not authorize live VPS apply;
- the smoke script intentionally keeps short `AMN2_EXPECTED_COMMIT=dd0dd44`, because it compares against `git rev-parse --short HEAD`;
- the package zip was rebuilt and the final package sha256 is `BB510BEABEB5ACCB7394C09F43EA7288BB08FC1352CCD35DA5AFF781E1B48E6D`.

## Boundary

Performed:

- local AMN2 toolchain check;
- local AMN2 full pytest suite;
- local package/source zip build;
- local package hygiene and test extraction;
- AMN3 docs/evidence/status updates.

Not performed:

- live VPS command;
- SSH command;
- package apply/rebuild on VPS;
- source overlay on `/opt/amn2`;
- service restart/deploy;
- public exposure;
- config delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive VPS/provider action;
- Telegram token use;
- live bot send;
- Telegram profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

`VPS_APPLY_ENABLED=false` remains the expected target boundary.

## Local Improvement Alternatives Before VPS Update

Safe local-only options remain available if the operator wants more product polish before `P5-C007`:

```text
P5-L001: optional read-only server status/latency display from safe cached/local/fake/operator-summary data only.
P5-L002: optional bot media local registry/upload implementation for start/header assets only; Telegram profile icon apply remains a named Telegram identity gate.
P5-L003: optional web/admin header asset local implementation for the web panel only, keeping it separate from bot headers.
```

These are alternatives to a VPS update, not prerequisites for it.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-C006 Current-head package rebuild for AMN2 dd0dd44
```

Remaining active default Phase 5 plan:

```text
critical: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Carried/gated directions remain:

```text
VPS-REBUILD-001: critical destructive gate, defer.
write API/config delivery/public exposure: critical gated.
P4-PRVTPRO-REFRESH-003 status/latency: carried from Phase 4, normal, design boundary closed; optional local-only implementation only.
```

## Next Recommendation

Recommended next choice:

```text
P5-C007 Named live update/smoke gate for AMN2 dd0dd44 on the disposable test VPS
```

If the operator wants to keep improving locally before touching the VPS, choose `P5-L001`, `P5-L002` or `P5-L003` instead.
