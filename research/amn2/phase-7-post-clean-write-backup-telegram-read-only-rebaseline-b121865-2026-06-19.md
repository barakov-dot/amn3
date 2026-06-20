# AMN2 Phase 7 P7-C005 + P7-C006 + P7-C007 Post-Clean Read-Only Rebaseline

Дата: 2026-06-19.

Статус: `completed-post-clean-read-only-rebaseline-no-mutation`.

Gate: `P7-C005 + P7-C006 + P7-C007 post-clean read-only rebaseline`.

Target VPS: `89.185.80.166`.

AMN2 source/package: `b121865 Add multi instance conflict model`.

Transcript:

```text
tmp/p7-c005-c006-c007-post-clean-readonly-rebaseline-20260619T180851Z.log
```

## Scope

Оператор открыл exact named gate:

```text
Открываю P7-C005 + P7-C006 + P7-C007 post-clean read-only rebaseline gate для b121865 на текущем disposable VPS 89.185.80.166. Без write mutation, без restore/import/reboot, без Telegram token use/profile/media mutation.
```

Разрешенный scope:

- read-only post-clean evidence collection after `P7-C004b`;
- source/filesystem/runtime/listener validation;
- safe `.env` flag presence summary without values;
- loopback web checks;
- DB aggregate counts only;
- public API route inventory;
- backup CLI help probe only;
- Telegram guard flags only;
- external closed probes.

Explicitly excluded:

- write API enablement;
- install mutation;
- backup create;
- restore apply;
- archive import apply;
- remote backup download;
- reboot;
- service restart;
- public exposure or public listener changes;
- config delivery;
- Local Agent mutation;
- Telegram token use, API call, live send, profile mutation or media mutation;
- secret-bearing evidence output.

## Post-Clean Baseline

The clean install produced by `P7-C004b` remained active:

```text
source_overlay_commit=b121865f488821f6fc471c9529fb26e5d7992515
source_overlay_expected=b121865f488821f6fc471c9529fb26e5d7992515
source_overlay_match=yes
opt_amn2_present=true
venv_python_present=true
dotenv_present=true
servers_yml_present=true
db_present=true
old_quarantine_count=1
```

Runtime/listener state:

```text
web_runtime=/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
web_listener=127.0.0.1:3030
public_api_listener_3040=absent
public_80_443_listeners=absent
```

Safe settings flags:

```text
TELEGRAM_BOT_TOKEN=present
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
WEB_ADMIN_HOST=127.0.0.1
WEB_ADMIN_PORT=3030
SERVER_NAME=local
PUBLIC_BASE_URL=missing
PUBLIC_DOMAIN=missing
WEB_PUBLIC_BASE_URL=missing
settings_load_status=passed
web_admin_cookie_secure=False
secret_values_printed=false
```

Loopback web checks:

```text
http://127.0.0.1:3030/login 200
http://127.0.0.1:3030/ 303
```

Clean DB aggregate inventory:

```text
db_present=True
db_bytes=147456
users_count=0
devices_count=0
servers_count=1
api_tokens_count=2
admin_actions_count=6
```

## P7-C005 Write API / Install Mutation

Public API route inventory after clean install:

```text
api_route_inventory_module=app.api.app
api_route_inventory_status=passed
GET /api/integration/status
GET /api/local-agent/runtime/summary
GET /api/metrics/summary
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/users/summary
GET /docs
GET /docs/oauth2-redirect
GET /openapi.json
GET /redoc
api_route_count=10
write_api_route_count=0
write_api_routes_present=no
```

Web/admin route inventory was inspected but not invoked:

```text
web_route_inventory_status=passed
web_route_count=55
web_non_get_route_count=29
api_write_route_invoked=false
web_write_route_invoked=false
```

Verdict:

```text
p7_c005_post_clean_status=passed_blocked_for_mutation
p7_c005_apply_allowed=false
```

## P7-C006 Backup/Restore/Import

Backup/restore/import guard after clean install:

```text
new_backups_dir_present=true
new_backups_file_count=0
quarantined_backup_file_count=2
backup_help_exit_code=0
backup_help_forbidden_marker_count=0
backup_create_performed=false
restore_apply_performed=false
archive_import_apply_performed=false
remote_backup_download_performed=false
reboot_performed=false
```

Only the CLI help summary was printed:

```text
usage: amneziya backup [-h] {create,verify,restore} ...
```

No backup archive was created in this rebaseline. The previous `P7-C006`
backup-only create/verify evidence remains the backup evidence source; restore,
import, remote backup download, reboot and disaster-recovery drill remain
separate exact gates.

Verdict:

```text
p7_c006_post_clean_status=passed_blocked_for_restore_import_reboot
p7_c006_apply_allowed=false
```

## P7-C007 Telegram Identity/Profile/Media

Telegram guard after clean install:

```text
telegram_token_presence_checked=true
telegram_token_value_printed=false
telegram_token_used=false
telegram_api_called=false
telegram_live_send_performed=false
telegram_profile_name_mutation_performed=false
telegram_profile_description_mutation_performed=false
telegram_profile_photo_mutation_performed=false
telegram_media_upload_performed=false
bot_runtime_started=false
```

Verdict:

```text
p7_c007_post_clean_status=passed_blocked_for_telegram_mutation
p7_c007_apply_allowed=false
```

## External Probes

External probes stayed closed:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Final Verdict

```text
post_clean_read_only_rebaseline_status=completed_no_mutation
remote_safe_evidence_dir=/opt/amn2/vps-smoke/p7-c005-c006-c007-post-clean-readonly-rebaseline-20260619T180851Z
remote_rebaseline_exit_code=0
secret_values_printed=false
```

The post-clean `b121865` disposable VPS baseline is now confirmed for the
remaining write/backup/Telegram gates without opening any mutation path.

Recommended next structure:

```text
P7-C005: exact named write/install mutation gate only if a scoped write slice is chosen
P7-C006: exact named restore/import/download/reboot/drill gate only
P7-C007: exact named Telegram identity/profile/media gate only
```

## Boundary

This gate did not perform write API enablement, install mutation, backup
archive create, restore apply, archive import, remote backup download, reboot,
service restart, public exposure, public listener change, config delivery,
Local Agent mutation, production peer/user mutation, Telegram token use,
Telegram API call, live bot send, Telegram identity/profile/media mutation,
media upload, secret publication or upstream/GPL code copy.
