# Phase 5 P5-C008 current-head package rebuild 9bff807

Date: 2026-06-12.

Scope: local AMN3 package rebuild for current AMN2 head after `P5-L002` and `P5-L001`.

Result: `package-ready-not-vps-smoked`.

This slice does not authorize live VPS apply by itself. Any upload, source
overlay, service restart or read-only loopback smoke on the disposable test VPS
remains a separate named gate.

## Source

```text
AMN2 repo: C:\Users\SooL\Documents\Amneziya
AMN2 branch: codex-vps-test-prep
AMN2 commit: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
AMN2 commit short: 9bff807
AMN2 subject: Add local bot media and status summaries
AMN3 repo: C:\Users\SooL\Documents\VPS-OPS-LAB
```

## Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-9bff807.zip
package_sha256: 882619B665B93CF4D6EFAB7977F7AE968F032C08C74CCFDA19A6B06BD629FAF9
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-9bff807.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-9bff807-source.zip
source_zip_sha256: 5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-9bff807-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-9bff807/
operator_doc: dist/amn2-vps-update-and-smoke-kit-9bff807/AMN2_VPS_UPDATE_AND_SMOKE_9bff807.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-9bff807/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-9bff807/amn2_api_loopback_smoke.sh
```

Package entries:

```text
AMN2_VPS_UPDATE_AND_SMOKE_9bff807.ru.md
amn2_apply_source_zip.sh
amn2_api_loopback_smoke.sh
amn2-codex-vps-test-prep-9bff807-source.zip
amn2-codex-vps-test-prep-9bff807-source.zip.sha256.txt
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
command: PYTHONPATH=.codex_deps C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

AMN2 full suite:

```text
command: PYTHONPATH=.codex_deps C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
result: 671 passed, 1 warning in 65.16s
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
source_files: 274
source_dirs: 42
required_source_entries: present
forbidden_source_entries: absent
shell_scripts_lf_no_bom: true
commit_bindings: present
test_extract: passed
test_extract_dir: C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p5-c008-9bff807-extract-final-20260612
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
app/web/templates/server_detail.html
app/vpn/client_compatibility.py
tests/services/test_bot_media.py
tests/cli/test_bot_media_cli.py
tests/web/test_servers.py
tests/bot/test_delivery.py
tests/vpn/test_client_compatibility.py
```

Forbidden source entries verified absent:

```text
exact: .env, server.yml, servers.yml
prefixes: .git/, data/, venv/, .venv/, logs/, tmp/, __pycache__/, .pytest_cache/, .codex_deps/
suffixes: .sqlite3, .db, .key, .pem
```

Commit binding checks:

```text
apply script contains full source commit: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
apply script contains source sha256: 5109C0FD7FBF40BB2F48C7476015E8BD4CCCF3AF54CAD702160488B0CE898AFD
smoke script contains short expected commit: 9bff807
operator doc contains explicit Russian no-live-apply phrase: yes
```

## Boundary

Performed:

- local AMN2 toolchain check with CPython 3.12.13;
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
P5-C008 Current-head package rebuild for AMN2 9bff807
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
P4-PRVTPRO-REFRESH-003 status/latency: carried from Phase 4, normal, design boundary closed and local display implemented without live probes.
```

## Next Recommendation

Recommended next choice:

```text
P5-C007 Named live update/smoke gate for AMN2 9bff807 on the disposable test VPS
```

`P5-C007` remains a separate named gate. This package does not open live VPS
commands, SSH, upload, source overlay, restart/deploy or smoke by itself.
