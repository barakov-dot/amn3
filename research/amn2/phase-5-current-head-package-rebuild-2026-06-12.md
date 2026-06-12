# Phase 5 P5-C001: current-head package rebuild 2026-06-12

Дата: 2026-06-12.

Назначение: пересобрать local-only AMN2 source/update package от текущего выбранного head `de25576` для Phase 5 operator-only pilot. Этот документ фиксирует только локальную сборку, checksum и hygiene/test-extract. Он не разрешает VPS commands, SSH commands, package apply, service restart/deploy, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation или destructive VPS actions.

## Decision

```text
task_id: P5-C001
scope: local package rebuild/hygiene
result: package-ready-not-vps-smoked
AMN2_branch: codex-vps-test-prep
AMN2_remote_tracking: amn2/codex-vps-test-prep
AMN2_source_commit: de2557639cd3853e6973002be3cab24033d2f722
AMN2_source_commit_short: de25576
previous_package_candidate: 1508e3c
live_commands_run: no
ssh_commands_run: no
package_apply_authorized: no
service_restart_authorized: no
public_exposure_authorized: no
config_delivery_authorized: no
destructive_action_authorized: no
VPS_APPLY_ENABLED: false
go_no_go_decision: defer-live
```

## Built Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-de25576.zip
package_sha256: B35D176F871ADB3B4CFDD3EC8D55B9BC5DF972E537038345B2E66899CFD21F87
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-de25576.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-de25576-source.zip
source_zip_sha256: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-de25576-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-de25576/
operator_doc: dist/amn2-vps-update-and-smoke-kit-de25576/AMN2_VPS_UPDATE_AND_SMOKE_de25576.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-de25576/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-de25576/amn2_api_loopback_smoke.sh
```

Package contents:

```text
package_entries: 5
required_package_entries:
- AMN2_VPS_UPDATE_AND_SMOKE_de25576.ru.md
- amn2_apply_source_zip.sh
- amn2_api_loopback_smoke.sh
- amn2-codex-vps-test-prep-de25576-source.zip
- amn2-codex-vps-test-prep-de25576-source.zip.sha256.txt
```

## Local Verification

AMN2 toolchain guard:

```text
command: python -m app.toolchain check
result: AMN2 toolchain ok: CPython 3.12.x.
```

AMN2 full suite:

```text
command: pytest -q
result: 664 passed, 1 warning in 64.45s
warning: expected StarletteDeprecationWarning from TestClient/httpx compatibility
```

Package hygiene:

```text
package_sha_check: passed
source_sha_check: passed
package_entries: 5
source_entries: 313
source_files: 271
source_dirs: 42
required_package_entries: passed
source_required_entries: passed
forbidden_source_entries: 0
test_extract: passed
text_bom_check: passed
shell_script_crlf_check: passed
commit_binding: passed
```

Forbidden source patterns checked:

```text
exact: .env, server.yml, servers.yml
prefixes: .git/, data/, venv/, .venv/, logs/, tmp/, __pycache__/, .pytest_cache/, .codex_deps/
suffixes: .sqlite3, .db, .key, .pem
```

Required source entries checked:

```text
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
app/services/build_status.py
app/bot/delivery.py
app/bot/texts.py
app/web/templates/about.html
tests/web/test_about.py
tests/web/test_users.py
tests/bot/test_delivery.py
```

## Boundary

This package is only `package-ready-not-vps-smoked`.

It does not authorize:

- running the package on the VPS;
- SSH commands against the target VPS;
- package apply, deploy or service restart;
- wipe/reinstall/rebuild;
- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web-admin `3030` exposure;
- Caddy/nginx/HTTPS/domain public cutover;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery, `.conf`, QR or `vpn://`;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- production peer/user mutation;
- secret-bearing evidence publication.

## Next Recommendation

Recommended next task: `P5-C003` Named gate live rollout for the disposable test VPS, using the `de25576` package above, with `P5-C004` secret handoff only if the live gate needs fresh operator-provided secrets/config. Until that gate is explicitly opened, keep the package local and do not run VPS/SSH/apply/restart commands.
