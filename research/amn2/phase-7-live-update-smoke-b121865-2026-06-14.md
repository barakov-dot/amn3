# Phase 7 P7-C001 live package/apply/smoke b121865

Дата: 2026-06-14.

Статус: `live-update-smoke-pass`.

Gate phrase:

```text
Открываю P7-C001 live package/apply/smoke gate для b121865 на текущем disposable VPS 89.185.80.166.
```

Target: disposable VPS `89.185.80.166`.

## Package

```text
package: dist/amn2-vps-update-and-smoke-kit-b121865.zip
package_sha256: 364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849
source_zip_sha256: D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647
target_commit: b121865f488821f6fc471c9529fb26e5d7992515
previous_known_good_vps_head: 0de7a77 Polish fresh installer preflight planning
```

Local package checksum matched the recorded checksum before upload.

## Upload And Extract

Uploaded to the VPS:

- `/root/amn2-vps-update-and-smoke-kit-b121865.zip`;
- `/root/amn2-vps-update-and-smoke-kit-b121865.zip.sha256.txt`.

Remote checksum:

```text
sha256sum -c: passed
```

Extracted to:

```text
/root/amn2-vps-update-and-smoke-kit-b121865
```

Expected kit files were present.

## Source Overlay

Source update evidence:

```text
source_update_status=passed
source_commit=b121865f488821f6fc471c9529fb26e5d7992515
safe_log_dir=/opt/amn2/vps-smoke/source-update-20260614T123810Z
```

Current source overlay marker:

```text
/opt/amn2/.amn2_source_overlay_commit
b121865f488821f6fc471c9529fb26e5d7992515
```

The apply script preserves `.env`, `data/`, `venv/` and `servers.yml`.

## Runtime

The already-running manual loopback AMN2 web/bot runtime was restarted so it
loaded the overlaid source.

Current verified web check:

```text
web_login_http=200
listener=127.0.0.1:3030
```

Current listener check after smoke:

```text
LISTEN 0 2048 127.0.0.1:3030 0.0.0.0:* users:(("python",pid=162552,fd=6))
```

The smoke-created `127.0.0.1:3040` listener was temporary and was not present in
the final webcheck listener snapshot.

## Loopback API Smoke

Environment:

```text
AMN2_DIR=/opt/amn2
AMN2_API_HOST=127.0.0.1
AMN2_API_PORT=3040
AMN2_SERVER_NAME=local
VPS_APPLY_ENABLED=false
```

Smoke result:

```text
VPS verdict: pass
run_id: 20260614T123823Z
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
safe_evidence_dir: /opt/amn2/vps-smoke/api-loopback-20260614T123823Z
safe_bundle: /opt/amn2/vps-smoke/api-loopback-safe-evidence-20260614T123823Z.tar.gz
```

Listener evidence inside smoke:

```text
listener_rows=1
api_pid=162594
expected_host=127.0.0.1
host=127.0.0.1 pid_match=yes row=LISTEN ... 127.0.0.1:3040 ... users:(("python",pid=162594,fd=6))
loopback_only=yes
```

Audit evidence:

```text
api_read_rows=5
forbidden_markers=none
audit_safe=yes
```

## External Exposure

External probes from the local workstation:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

No public listener was opened by this gate.

## Notes

The local PowerShell helper hit two local-only scripting issues before live
execution:

- PowerShell `<` redirection is not supported;
- `Get-FileHash` was unavailable in that shell and was replaced with
  `certutil -hashfile`.

Those failures happened before upload/apply. The successful run used
`certutil`, uploaded the package, applied the source overlay and completed the
loopback smoke.

The remote helper printed a trailing `bash: line 83: $'\r': command not found`
after the completed marker due to CRLF in the piped helper script. It happened
after the remote apply/smoke completed and did not change the smoke verdict.

## Not Performed

- public exposure;
- config delivery, `.conf`, QR or `vpn://` delivery;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive cleanup/reinstall;
- provider-side destructive action;
- Telegram token use, live bot send or identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Outcome

`P7-C001` is closed as `live-update-smoke-pass`.

Latest VPS-smoked/package head is now:

```text
b121865 Add multi instance conflict model
```
