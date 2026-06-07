# c92bd1a manual prelaunch evidence

Дата: 2026-06-07.

Назначение: зафиксировать safe evidence ручной prelaunch-проверки source overlay `c92bd1a Bind web admin systemd to loopback` на validation VPS. На этом сервере постоянные `systemd` services намеренно не запускались: рабочий production server будет другим.

## Decision

```text
decision: c92bd1a-manual-prelaunch-pass-systemd-deferred
validation_server: mirror
working_server: different future server
systemd_launch_status: deferred-working-server
VPS_APPLY_ENABLED: false
```

## Runtime And Backup

```text
source_overlay_commit: c92bd1a
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
backup_file: amneziya-backup-20260607T192509Z.tar.enc
backup_verify: passed
```

Backup manifest was verified without publishing backup contents, `.env`, secret material or database contents.

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
- enabling `systemd` services on this validation VPS;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, `vpn://` links, full logs, backup contents or database contents.

## Next

On the future working server, repeat the safe gate from the current source overlay/package, then enable `systemd` and HTTPS reverse proxy there. On the validation VPS, `c92bd1a` is accepted as manual prelaunch pass with service deployment deferred.
