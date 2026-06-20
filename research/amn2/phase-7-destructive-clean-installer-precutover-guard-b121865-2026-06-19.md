# AMN2 Phase 7 P7-C004a Destructive Clean Installer Pre-Cutover Guard

Дата: 2026-06-19.

Статус: `ready-for-final-destructive-stop-line-no-apply`.

Gate: `P7-C004a destructive clean installer pre-cutover guard`.

Target VPS: `89.185.80.166`.

Transcript:

```text
tmp/p7-c004a-destructive-pre-cutover-guard-20260619T172404Z.log
```

## Scope

Оператор открыл gate:

```text
Открываю P7-C004a destructive clean installer pre-cutover guard для b121865 на текущем disposable VPS 89.185.80.166. Без wipe/reinstall/apply.
```

Этот guard является read-only pre-cutover проверкой. Он не разрешает и не
выполняет destructive action.

## Local Package/Source Readiness

```text
package_path=dist/amn2-vps-update-and-smoke-kit-b121865.zip
package_present=True
package_sha256=364025bd1ae5a23979889a6ded3d78078e1c939f883af277106f9851ce660849
package_sha256_expected=364025BD1AE5A23979889A6DED3D78078E1C939F883AF277106F9851CE660849
package_sha256_match=True
source_zip_path=dist/amn2-codex-vps-test-prep-b121865-source.zip
source_zip_present=True
source_zip_sha256=d0fb561d5a12c3b2c095521c3b44923b001f49c8e94ca5c13db1e811abb17647
source_zip_sha256_expected=D0FB561D5A12C3B2C095521C3B44923B001F49C8E94CA5C13DB1E811ABB17647
source_zip_sha256_match=True
```

## Destructive Boundary

```text
operator_disposable_target_declaration=provided-in-chat
wipe_performed=false
reinstall_performed=false
package_apply_performed=false
service_restart_performed=false
provider_action_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
remote_backup_download_performed=false
reboot_performed=false
```

## Remote Identity And Runtime

```text
os_id=ubuntu
os_version_id=24.04
hostname_static=166780.ip-ptr.tech
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
source_overlay_expected=b121865f488821f6fc471c9529fb26e5d7992515
source_overlay_match=yes
```

Runtime/listener summary:

```text
web_runtime=127.0.0.1:3030
public_api_3040_exposed=false
public_80_exposed=false
public_443_exposed=false
```

Safe env flags:

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

## Backup Prerequisite

Backup-only prerequisite from `P7-C006` was present and matched:

```text
expected_backup_path=/opt/amn2/backups/p7-c006-retry-20260619T171342Z/amneziya-backup-20260619T171402Z.tar.enc
backup_artifact_present=true
backup_artifact_bytes=245860
backup_artifact_mode=600
backup_artifact_owner=root:root
backup_artifact_sha256=9947bf97b242e46d86cf7cbf41ed7ffb8cec8a9bae728a71f3095c86d50b73c9
backup_artifact_sha256_match=yes
backup_artifact_contents_printed=false
```

## State Safe Inventory

```text
db_present=True
db_bytes=172032
users_count=1
devices_count=2
servers_count=1
api_tokens_count=24
admin_actions_count=58
```

Disk space summary:

```text
root_size=9.8G
root_used=5.2G
root_avail=4.2G
root_use_percent=56
```

External probes stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Verdict

```text
pre_cutover_blocker_count=0
p7_c004a_pre_cutover_status=ready_for_final_destructive_stop_line
final_destructive_phrase_received=false
destructive_apply_allowed_by_this_gate=false
secret_values_printed=false
```

## Decision

`P7-C004a` is closed as
`ready-for-final-destructive-stop-line-no-apply`.

The next destructive step is still not authorized by this evidence. It requires
a separate exact named destructive gate and final destructive phrase. Suggested
next phrase, if the operator chooses to proceed:

```text
Открываю P7-C004b destructive clean installer execution gate для b121865 на disposable VPS 89.185.80.166. Разрешаю wipe/reinstall/apply clean installer на этом disposable VPS.
```

Until that exact gate is opened, wipe/reinstall/apply remains blocked.
