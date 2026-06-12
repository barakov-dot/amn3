# Phase 5 P5-C009 current-head package rebuild 2215761

Date: 2026-06-13.

Scope: local AMN3 package rebuild for current AMN2 head after `P5-O002`.

Result: `package-ready-not-vps-smoked`.

This slice does not authorize live VPS apply by itself. Any upload, source overlay, service restart or read-only loopback smoke on the disposable test VPS remains a separate named gate.

## Source

```text
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 branch: codex-vps-test-prep
AMN2 commit: 221576169a84bbf662114c564e83c41fba0091b5
AMN2 commit short: 2215761
AMN2 subject: Polish operator web admin UX
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-2215761.zip
package_sha256: 6C360E8005E117EC59DD2829E9C4E9D2F36B5070275CD989D9D51A0675CF8B44
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-2215761.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-2215761-source.zip
source_zip_sha256: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-2215761-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-2215761/
operator_doc: dist/amn2-vps-update-and-smoke-kit-2215761/AMN2_VPS_UPDATE_AND_SMOKE_2215761.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-2215761/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-2215761/amn2_api_loopback_smoke.sh
```

Package entries:

```text
AMN2_VPS_UPDATE_AND_SMOKE_2215761.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-2215761-source.zip
amn2-codex-vps-test-prep-2215761-source.zip.sha256.txt
```

## Local Verification

Initial wrong-runtime check:

```text
command: python -m app.toolchain check
result: failed as expected on system Python 3.14.3
message: AMN2 supports CPython 3.12.x for this gate; got 3.14.3.
```

AMN2 toolchain with CPython 3.12.13:

```text
command: PYTHONPATH=.codex_deps;. C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

AMN2 full suite:

```text
command: PYTHONPATH=.codex_deps;. C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
result: 675 passed, 1 warning in 64.74s
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
source_files: 275
source_dirs: 42
required_source_entries: present
forbidden_source_entries: absent
shell_scripts_lf_no_bom: true
commit_bindings: present
test_extract: passed
test_extract_dir: C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p5-c009-2215761-extract-final-20260613
```

Required source entries verified present:

```text
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
app/services/build_status.py
app/services/bot_media.py
app/bot/delivery.py
app/bot/texts.py
app/web/app.py
app/web/templates/dashboard.html
app/web/templates/users.html
app/web/templates/api_tokens.html
app/web/templates/config_templates.html
app/web/static/admin.css
tests/web/test_operator_ui_p5_o002.py
tests/web/test_app.py
tests/web/test_config_templates.py
```

Forbidden source entries verified absent:

```text
exact: .env, server.yml, servers.yml
prefixes: .git/, data/, venv/, .venv/, logs/, tmp/, __pycache__/, .pytest_cache/, .codex_deps/
suffixes: .sqlite3, .db, .key, .pem
```

Commit binding checks:

```text
apply script contains full source commit: 221576169a84bbf662114c564e83c41fba0091b5
apply script contains source sha256: 825D1EF34F8DF11C0DB12B7A3DCDAE8FE79F04A8C56113CBA9CAEA3ECDBCC38B
smoke script contains short expected commit: 2215761
operator doc contains explicit Russian no-live-apply phrase: yes
```

## Boundary

Performed:

- local AMN2 wrong-runtime and CPython 3.12.13 toolchain checks;
- local AMN2 full pytest suite;
- local AMN2 source hygiene check;
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

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-C009 Current-head package rebuild for AMN2 2215761
```

Remaining default Phase 5 plan:

```text
critical_default: none
very_important: none
important: none
normal: none
simple: none
cosmetic: none
```

Deferred/gated work remains not executed:

```text
P5-C010: named live update/smoke gate for AMN2 2215761 on the disposable test VPS.
VPS-REBUILD-001: critical destructive gate, not executed, defer.
write API: critical gated, not executed.
config delivery: critical gated, not executed.
public exposure: critical gated, not executed.
P4-PRVTPRO-REFRESH-003 live probes/actions: normal gated, not executed; safe design boundary and local cached display are closed.
```

## Next Recommendation

Recommended next choice:

```text
P5-C010 Named live update/smoke gate for AMN2 2215761 on the disposable test VPS
```

`P5-C010` remains a separate named gate. This package does not open live VPS commands, SSH, upload, source overlay, restart/deploy or smoke by itself.
