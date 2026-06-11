# VPS-REBUILD-001: package build and hygiene 2026-06-10

Дата: 2026-06-10.

Назначение: собрать local-only package для выбранного AMN2 source candidate `1508e3c4a100b76815b29f91757290f1266f813d` и проверить checksum/hygiene/test-extract перед возможным `VPS-REBUILD-001` fresh VPS rebuild. Этот документ не разрешает VPS commands, SSH commands, wipe, reinstall, package apply, service changes, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot или production peer/user mutation.

## Decision

```text
precheck_id: VPS-REBUILD-001-PACKAGE-BUILD-HYGIENE-2026-06-10
gate_name: VPS-REBUILD-001-FRESH-VPS-REBUILD-2026-06-10
precheck_scope: local-only package build/hygiene
result: package-ready-not-vps-smoked
AMN2_source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
AMN2_source_commit_short: 1508e3c
package_status: package-ready-not-vps-smoked
live_commands_run: no
ssh_commands_run: no
destructive_action_authorized: no
reinstall_authorized: no
package_apply_authorized: no
secret_publication: none
go_no_go_decision: defer
```

## Built Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
package_sha256_file: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip.sha256.txt

source_zip: dist/amn2-codex-vps-test-prep-1508e3c-source.zip
source_zip_sha256: 0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E
source_zip_sha256_file: dist/amn2-codex-vps-test-prep-1508e3c-source.zip.sha256.txt

package_dir: dist/amn2-vps-update-and-smoke-kit-1508e3c/
operator_doc: dist/amn2-vps-update-and-smoke-kit-1508e3c/AMN2_VPS_UPDATE_AND_SMOKE_1508e3c.ru.md
apply_script: dist/amn2-vps-update-and-smoke-kit-1508e3c/amn2_apply_source_zip.sh
smoke_script: dist/amn2-vps-update-and-smoke-kit-1508e3c/amn2_api_loopback_smoke.sh
```

## Package Contents

```text
package_entries: 5
required_package_entries:
- AMN2_VPS_UPDATE_AND_SMOKE_1508e3c.ru.md
- amn2_apply_source_zip.sh
- amn2_api_loopback_smoke.sh
- amn2-codex-vps-test-prep-1508e3c-source.zip
- amn2-codex-vps-test-prep-1508e3c-source.zip.sha256.txt
```

## Hygiene Result

```text
source_entries: 302
forbidden_source_entries: 0
test_extract: passed
source_required_entries: passed
package_required_entries: passed
package_sha_check: passed
source_sha_check: passed
text_bom_check: passed
shell_script_crlf_check: passed
```

Forbidden source patterns checked:

```text
exact: .env, server.yml, servers.yml
prefixes: .git/, data/, venv/, .venv/, logs/, tmp/, __pycache__/, .pytest_cache/
suffixes: .sqlite3, .db, .key, .pem
```

Required source entries checked:

```text
app/api/app.py
app/services/api_smoke.py
app/services/integration_status.py
app/services/build_status.py
app/web/templates/about.html
tests/web/test_about.py
tests/web/test_users.py
```

## Boundary

This package is only `package-ready-not-vps-smoked`.

It does not authorize:

- running the package on the VPS;
- wipe/reinstall/rebuild;
- package apply;
- service stop/start/restart/enable/disable;
- firewall/reverse proxy/listener changes;
- public API `3040`;
- direct public web/admin `3030`;
- Caddy/nginx/HTTPS public cutover;
- config delivery, `.conf`, QR or `vpn://`;
- write API or `/api/clients` CRUD;
- Local Agent mutations;
- backup/import/reboot;
- production peer/user mutation;
- secret-bearing evidence publication.

## Next Gate Requirements

```text
provider_snapshot_confirmation: pending
stop_criteria_review: pending
final_destructive_phrase: not_sent
go_no_go_decision: defer
```

Recommendation: do not run this package live yet. First record the retention path and stop criteria, then decide whether the operator still wants to send the exact final destructive phrase.
