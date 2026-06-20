# AMN2 Phase 7 P7-C005 Write / Install Mutation Contour

Date: 2026-06-20.

Status: `completed-scoped-write-contour-smoked`.

Gate: `P7-C005 write API / install mutation gate`, explicitly opened by the
operator for AMN2 on disposable VPS `89.185.80.166`.

## Boundary

Allowed in this gate:

- implement and package a scoped `install:write` contour;
- apply the AMN2 source overlay package to the disposable VPS;
- restart only the loopback web runtime so the new API route is loaded;
- run loopback-only API smoke;
- invoke the scoped write route as an audit-only mutation request.

Not opened:

- public exposure, reverse proxy, TLS, firewall or public listener changes;
- config delivery, `.conf`, QR, `vpn://` or client secret output;
- restore/import/reboot or remote backup download;
- Local Agent mutation;
- Telegram token use, live send, profile or media mutation;
- provider action or actual installer execution;
- secret-bearing evidence publication.

## AMN2 Source

```text
repo: barakov-dot/amn2
branch: codex-vps-test-prep
commit: 55012958ff6b8338254f3f68dfe6779f4bc56f5d
subject: Add P7 install write contour
previous live clean-install source overlay: b121865 Add multi instance conflict model
```

The branch was pushed from `b121865` to `5501295`.

## Implementation Scope

AMN2 added the first P7 write contour:

- new scope: `install:write`;
- new route: `POST /api/install/mutation-requests`;
- accepted action: `clean_install_prepare`;
- accepted target: `local`;
- behavior while `VPS_APPLY_ENABLED=false`:
  `recorded_blocked_by_vps_apply_disabled`;
- side effect: safe `api_write` row in `admin_actions`;
- no installer executor invocation, package apply, service restart, public
  exposure, config delivery or Telegram action from the route itself.

The route does not return or store `operator_note` in audit metadata.

## Local Verification

AMN2 test command:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest -q
```

Result:

```text
726 passed, 1 StarletteDeprecationWarning
```

AMN3/package checks:

```text
python -m unittest discover -s tests -p "test_amn2_apply_source_zip.py" -v
2 tests OK

python -m unittest discover -s tests -p "test_markdown_hygiene.py" -v
2 tests OK

package zip entries: 5
source zip entries: 343
forbidden zip hits: 0
```

## Package Artifacts

```text
package: dist/amn2-vps-update-and-smoke-kit-5501295.zip
package_sha256: C03D26673AD79D9487A3ED34E9657E0DCA10EBC9BB601E429385091F1DFEF407
source_zip: dist/amn2-codex-vps-test-prep-5501295-source.zip
source_zip_sha256: DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3
```

The source zip inventory did not contain `.env`, `servers.yml`, `data/`,
`venv/`, `.venv/`, `tmp/`, SQLite DB files or `.git/`.

## Live Apply / Smoke

Transcript:

```text
tmp/p7-c005-write-install-apply-smoke-20260619T193623Z.log
```

Outcome before route-specific resume:

```text
package_sha256_match=True
package_sha256sum_check=passed
source_zip_sha256_expected=DA7DA58E0FD8D778BD4A22471BBCD9038CC455ACD3C0538A38874215C81646D3
source_update_status=passed
source_overlay_commit=5501295
package_apply_performed=true
write_api_route_count=1
install_mutation_route_present=yes
loopback_web_restart_performed=true
web_login_loopback_http=200
web_runtime_status=passed
VPS verdict: pass
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
auth_status: passed
listener_status: passed
audit_status: passed
```

External probes after the apply/smoke step stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

The first route-specific verifier failed because the helper queried
`admin_actions.metadata`, while the AMN2 schema stores audit metadata in
`admin_actions.metadata_json`.

Classification: verifier bug, not an AMN2 route/runtime failure.

## Route Smoke Resume

Transcript:

```text
tmp/p7-c005-resume-route-smoke-20260620T042247Z.log
```

The resume did not upload, apply, restart, expose public listeners, deliver
configs, restore/import/reboot, use Telegram or invoke any installer executor.

Resume evidence:

```text
source_overlay_commit=5501295
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
write_api_route_count=1
install_mutation_route_present=yes
web_login_loopback_http=200
server_read_token_post_http=403
install_write_token_post_http=202
write_route_status=recorded_blocked_by_vps_apply_disabled
write_route_request_recorded=True
execution_vps_apply_enabled=False
execution_executor_invoked=False
execution_package_apply_performed=False
execution_service_restart_performed=False
execution_public_exposure_performed=False
execution_config_delivery_performed=False
execution_telegram_action_performed=False
audit_action=api_write
audit_metadata_keys=aggregate_only,method,owner_label,path,requested_action,scope,status,target,token_id,token_name,vps_apply_enabled
audit_forbidden_marker_count=0
audit_safe=yes
temporary_token_values_printed=false
p7_c005_scoped_write_route_smoke_status=passed
remote_p7_c005_resume_exit_code=0
```

External probes after the resume stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Final Verdict

`P7-C005` is closed as `completed-scoped-write-contour-smoked`.

Current disposable VPS state:

```text
source_overlay_commit=5501295
web_admin_listener=127.0.0.1:3030
public_api_listener=absent by default
public_80_443=absent
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
scoped_write_route=POST /api/install/mutation-requests
route_scope=install:write
route_behavior=audit-only blocked by VPS_APPLY_ENABLED=false
```

Remaining actual Phase 7 gates:

- residual `P7-C006` restore/import/download/reboot/disaster-recovery scopes;
- `P7-C007` Telegram identity/profile/media mutation;
- inactive `P7-C006a` provider backup restore-point confirmation, postponed
  by the operator until the end.
