# Phase 6 P6-C010 live update/smoke 0de7a77

Date: 2026-06-14.

Task: `P6-C010` named live apply/smoke gate for AMN2 `0de7a77`.

Operator phrase:

```text
Открываю P6-C010 live apply/smoke gate для 0de7a77 на текущем disposable VPS 89.185.80.166.
```

Target: operator-provided disposable VPS `89.185.80.166`.

## Package

```text
package: dist/amn2-vps-update-and-smoke-kit-0de7a77.zip
package_sha256: 7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B
source_zip: dist/amn2-codex-vps-test-prep-0de7a77-source.zip
source_sha256: B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295
source_commit: 0de7a77f3eb09d23dc2785d402bc51c2b5eb7835
```

Local package checksum matched the prepared `.sha256` file before upload.

Remote package checksum passed:

```text
amn2-vps-update-and-smoke-kit-0de7a77.zip: OK
```

Remote extract target:

```text
/root/amn2-vps-update-and-smoke-kit-0de7a77
```

Expected extracted files were present:

```text
AMN2_VPS_UPDATE_AND_SMOKE_0de7a77.ru.md
amn2-codex-vps-test-prep-0de7a77-source.zip
amn2-codex-vps-test-prep-0de7a77-source.zip.sha256.txt
amn2_api_loopback_smoke.sh
amn2_apply_source_zip.sh
```

## Source Overlay

Command scope: source overlay only, preserving target `.env`, `data/`, `venv/`
and `servers.yml`.

Result:

```text
source_update_status=passed
run_id=20260614T062734Z
target=/opt/amn2
source_sha=B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295
expected_commit=0de7a77f3eb09d23dc2785d402bc51c2b5eb7835
source_commit=0de7a77f3eb09d23dc2785d402bc51c2b5eb7835
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260614T062734Z
python=Python 3.12.3
.env: preserved
data/: preserved
venv/: preserved
servers.yml: preserved
permission_strategy=target-root-metadata-preserved
copied_root_entries=10
```

## Runtime

The pre-existing manual runtime was restarted so the web/bot processes would
load the newly overlaid source. The restart was limited to the existing manual
AMN2 web and bot processes.

Post-restart state:

```text
web: /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
bot: /opt/amn2/venv/bin/python -m app.main
web_login_http=200
```

The web listener remained loopback-only:

```text
127.0.0.1:3030
```

## Smoke

The first smoke attempt intentionally stopped before test execution because
`3030` was already occupied by the Web Admin listener. A second attempt with
`AMN2_ALLOW_EXISTING_API=1` against `3030` correctly showed that Web Admin does
not expose the operator API routes:

```text
missing_bearer_http=404
wrong_scope_http=404
revoked_token_http=404
```

The successful smoke used the intended temporary API loopback port `3040`.

Environment:

```text
AMN2_DIR=/opt/amn2
AMN2_API_HOST=127.0.0.1
AMN2_API_PORT=3040
AMN2_SERVER_NAME=local
VPS_APPLY_ENABLED=false
```

Result:

```text
VPS verdict: pass
run_id: 20260614T063327Z
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
audit_status: passed
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260614T063327Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260614T063327Z.tar.gz
```

The smoke-created API listener on `3040` was temporary and was not present in
the final listener snapshot.

## Final Exposure Check

Final remote listener snapshot:

```text
127.0.0.1:3030
```

No final listeners were observed on `3040`, `80` or `443`.

External probes from the local workstation:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Safety

Performed under the named `P6-C010` gate:

- package upload/checksum/extract to the disposable VPS;
- scoped source overlay update of `/opt/amn2`;
- minimal restart of the already-running manual AMN2 web/bot runtime;
- read-only loopback API smoke with `VPS_APPLY_ENABLED=false`;
- listener and external exposure verification.

Not performed:

- public exposure change;
- config delivery;
- write API production opening;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive cleanup/reinstall;
- provider-side destructive action;
- Telegram identity/profile mutation;
- live bot send by Codex;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Status

`P6-C010` is closed as `live-update-smoke-pass`.

Latest AMN2 VPS-smoked/package head is now:

```text
0de7a77 Polish fresh installer preflight planning
```
