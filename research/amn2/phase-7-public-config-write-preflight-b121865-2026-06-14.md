# Phase 7 P7-C002 + P7-C003 + P7-C005 public/config/write preflight b121865

Дата: 2026-06-14.

Статус: `blocked-by-preconditions`.

Gate phrase:

```text
Открываю P7-C002 + P7-C003 + P7-C005 public/config/write gate для b121865 на текущем disposable VPS 89.185.80.166.
```

Target: disposable VPS `89.185.80.166`.

Transcript:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p7-c002-c003-c005-preflight-20260614T160424Z.log
```

## Decision

The combined public/config/write gate was not enabled. The safe read-only
preflight showed that the current VPS is healthy on loopback, but public
exposure, config delivery and write API/install mutation are not ready to turn
on in one step.

Outcome:

```text
P7-C002: blocked-by-preconditions
P7-C003: blocked-by-preconditions
P7-C005: blocked-by-current-surface
```

No public listener, config delivery channel or write route was opened.

## Source And Runtime

Remote source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Running AMN2 processes:

```text
/opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
/opt/amn2/venv/bin/python -m app.main
```

Loopback web check:

```text
web_login_loopback_http=200
```

## Listener And External Exposure

Remote listener snapshot showed AMN2 web only on loopback:

```text
127.0.0.1:3030 users:(("python",pid=162552,fd=6))
0.0.0.0:22 users:(("sshd",...))
```

Firewall snapshot:

```text
ufw: inactive
iptables INPUT: ACCEPT
```

External probes from the local workstation:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

Decision for `P7-C002`: do not expose direct public `3030` or `3040`. A future
public exposure gate needs an explicit web/admin credential check, domain/TLS or
reverse-proxy plan, firewall plan and post-change public/loopback verification.

## Safe Environment Summary

Secret values were not printed. Only presence/boolean state was collected.

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=missing
WEB_ADMIN_PASSWORD_HASH=present
VPS_APPLY_ENABLED=false
EMAIL_CONFIG_ATTACHMENTS_ENABLED=unset
SMTP_HOST=missing
SMTP_USERNAME=missing
SMTP_PASSWORD=missing
LOCAL_AGENT_ENABLED=false
```

Decision for `P7-C003`: do not enable config delivery. SMTP is not configured,
email config attachments are not enabled, and this gate did not authorize
printing `.conf`, QR payloads or `vpn://` import links into evidence or chat.

Decision for `P7-C005`: do not enable live peer/user mutation. `VPS_APPLY_ENABLED`
is still `false`, Local Agent is disabled, and write API routes are absent from
the current public API surface.

## Public API Route Inventory

Current `/api/*` routes:

```text
GET /api/integration/status
GET /api/local-agent/runtime/summary
GET /api/metrics/summary
GET /api/servers
GET /api/servers/{server_name}/summary
GET /api/users/summary
```

Write API route check:

```text
write_api_route_count=0
```

This means `P7-C005` cannot be honestly enabled as broad `/api/clients` write
CRUD in `b121865`; that surface is not implemented in the current public API
head.

## Web Route Inventory For Config/Write Surfaces

The web admin app has local operator write/config surfaces, including:

```text
POST /api-tokens/issue
POST /api-tokens/{token_id}/revoke
POST /config-templates/{config_version}/reset
POST /config-templates/{config_version}/save
POST /servers/new
POST /servers/{server_id}/amnezia-peers/unmark
POST /servers/{server_id}/disable
POST /servers/{server_id}/edit
POST /servers/{server_id}/health/run
POST /servers/{server_id}/missing-devices/{device_id}/add
POST /servers/{server_id}/sync/run
POST /servers/{server_id}/unknown-peers/ignore
POST /servers/{server_id}/unknown-peers/remove
POST /users/new
POST /users/{user_id}/block
POST /users/{user_id}/delete
POST /users/{user_id}/destroy
POST /users/{user_id}/devices/{device_id}/delete
POST /users/{user_id}/devices/{device_id}/email-config
POST /users/{user_id}/devices/{device_id}/email-recovery/start
POST /users/{user_id}/devices/{device_id}/secrets
POST /users/{user_id}/disable-vpn
POST /users/{user_id}/edit
POST /users/{user_id}/email/verify/start
POST /users/{user_id}/enable-vpn
```

These remain loopback/operator-only in this preflight. They were not exposed
publicly and were not invoked by Codex.

## Aggregate Database Counts

Only aggregate counts were collected:

```text
users_count=1
devices_count=2
servers_count=1
api_tokens_count=24
admin_actions_count=58
devices_status_active=2
```

No per-user, per-device, peer key, config body, QR, token or secret-bearing
database content was printed.

## Helper Notes

The first preflight helper had two read-only scripting mistakes:

- it imported `create_app` instead of `create_web_app`;
- PowerShell interpreted `$Target:3030` as a scoped variable, which produced
  malformed external probe URLs.

The corrected helper produced the evidence above. The remote helper still
printed a trailing `bash: line 159: $'\r': command not found` after
`[remote] preflight complete` due to CRLF in the piped helper script. It
happened after the safe preflight completed and did not change the verdict.

## Not Performed

- public `3030`, `3040`, `80` or `443` exposure;
- domain, TLS, reverse proxy or firewall change;
- public OpenAPI publication;
- config delivery, `.conf`, QR or `vpn://` output;
- tokenized public redeem or self-service download;
- Telegram live config send;
- write API route enablement;
- `/api/clients` CRUD;
- Local Agent mutation;
- `VPS_APPLY_ENABLED=true`;
- live peer/user mutation;
- backup/import/reboot;
- destructive cleanup/reinstall;
- secret-bearing evidence publication;
- upstream/GPL code copy.

## Next Recommendation

Do not continue the triple gate as a single live enablement step.

Recommended safe next candidates:

1. `P7-C002a` public exposure design/readiness: domain/TLS/reverse proxy,
   admin credential contract and firewall plan, still no live exposure unless a
   new exact gate is opened.
2. `P7-C003a` config delivery channel readiness: choose delivery channel,
   configure SMTP or operator-local delivery, and define no-secret evidence
   checks before sending real configs.
3. `P7-C005a` write API scope decision: either keep public API read-only for
   RC, or add a separate AMN2 implementation slice for write routes before any
   live write gate.
