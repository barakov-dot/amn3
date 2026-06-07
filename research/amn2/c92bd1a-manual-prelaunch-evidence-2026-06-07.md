# c92bd1a manual prelaunch evidence

Дата: 2026-06-07.

Назначение: зафиксировать safe evidence ручной prelaunch/manual-runtime проверки source overlay `c92bd1a Bind web admin systemd to loopback` на validation VPS. На этом сервере `systemd` services намеренно не используются в текущем режиме: web/admin и bot запущены оператором вручную.

## Decision

```text
decision: c92bd1a-controlled-prod-manual-runtime-pass
validation_server: mirror
runtime_mode: manual
systemd_web: not-used
systemd_bot: not-used
web_process: present
bot_process: present
web_3030_loopback: 127.0.0.1:3030
web_3030_public: no
api_3040_public: no
VPS_APPLY_ENABLED: false
```

## Runtime And Backup

```text
source_overlay_commit: c92bd1a
runtime_mode: manual
data_dir: present
env_file: present
servers_yml: present
venv: present
shell_VPS_APPLY_ENABLED: false
env_VPS_APPLY_ENABLED: false
WEB_ADMIN_HOST: 127.0.0.1
WEB_ADMIN_PORT: 3030
WEB_ADMIN_SESSION_COOKIE_SECURE: true
backup_create: passed
backup_file: amneziya-backup-20260607T195851Z.tar.enc
backup_verify: passed
```

Backup manifest was verified without publishing backup contents, `.env`, secret material or database contents.

The first backup attempt failed because `APP_SECRET_KEY` was not exported into the operator shell; the valid retry loaded only that key from `.env` without printing the value and then verified the encrypted backup.

## API Loopback Smoke

```text
run_id: 20260607T194229Z
api_bind: http://127.0.0.1:3040
preflight_status: skipped
server_db_sync_status: passed
api_ready_status: passed
api_smoke_status: passed
checked_routes: 6
route_status_codes: 200
forbidden_markers: []
auth_status: passed
missing_bearer_http: 401
wrong_scope_http: 403
revoked_token_http: 401
listener_status: passed
listener: 127.0.0.1:3040 loopback-only
audit_status: passed
audit_safe: yes
server_db_sync: passed
server_name: local
runtime: docker
```

## Latest Safe Preflight And API Cycle

```text
bot_check_network: ok
server_preflight: ok
server_check_dry_run: ok
api_smoke_status: passed
checked_routes: 6
route_status_codes: 200
forbidden_markers_count: 0
token_raw_display: hidden
revoke_status: revoked
VPS_APPLY_ENABLED: false
```

## Manual Web/Admin Loopback Smoke

The old manual web listener was found and safely stopped before repeating the check.

```text
old_manual_web_pid: 2333887
old_manual_web_process: matches_manual_web
old_manual_web_cleanup: stopped
diagnostic_web_pid: 2990245
startup_tick: 5
startup_log: Application startup complete
listener: 127.0.0.1:3030
web_login_http: 200
web_listener_after_cleanup: stopped
```

Latest manual runtime evidence:

```text
runtime_mode: manual
systemd_web: not-used
systemd_bot: not-used
web_process: present
bot_process: present
web_login_http: 200
web_3030_loopback: 127.0.0.1:3030
web_3030_public: no
api_3040_public: no
VPS_APPLY_ENABLED: false
```

## Bot Network

```text
bot_check_network: ok
bot_identity: @Samurai_02_bot
proxy: enabled
```

## Boundary

This evidence does not authorize:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web/admin `3030` exposure;
- enabling `systemd` services without a separate service-mode gate;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links, full logs, backup contents or database contents.

## Next

Current accepted mode is operator-controlled manual runtime: web/admin and bot are present, web/admin is loopback-only on `127.0.0.1:3030`, public API `3040` is not exposed, and `VPS_APPLY_ENABLED=false`. If service mode is desired later, run a separate `systemd`/reverse-proxy gate. Continue only with read-only/status/docs slices until a new explicit gate is opened.
