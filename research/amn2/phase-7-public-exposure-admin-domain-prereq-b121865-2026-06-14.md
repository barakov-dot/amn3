# AMN2 Phase 7 P7-C002a Public Exposure Admin/Domain Prerequisite

Дата: 2026-06-14.

Gate: `P7-C002a Public exposure admin/domain prerequisite`.

Target: disposable VPS `89.185.80.166`.

Commit: `b121865f488821f6fc471c9529fb26e5d7992515`.

Статус: `prerequisite-updated`.

Transcript:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p7-c002a-admin-domain-prereq-20260614T183111Z.log
```

## Итог

Operator opened `P7-C002a` to update the public exposure admin/domain
prerequisites. The gate updated only `.env` admin/domain fields and did not
restart services or apply public exposure.

Operator-selected non-secret inputs:

```text
PUBLIC_BASE_URL=https://89.185.80.166
PUBLIC_DOMAIN=89.185.80.166
WEB_ADMIN_USERNAME=root
```

Remote source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Pre-mutation safe flags:

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=missing
WEB_ADMIN_PASSWORD_HASH=present
PUBLIC_BASE_URL=missing
PUBLIC_DOMAIN=missing
WEB_PUBLIC_BASE_URL=missing
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

Mutation result:

```text
env_update_status=passed
secret_values_printed=false
rollback_copy_created_on_vps=true
service_restart_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
```

Post-mutation safe flags:

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
PUBLIC_BASE_URL=present
PUBLIC_DOMAIN=present
WEB_PUBLIC_BASE_URL=present
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

Post-mutation precondition verdict:

```text
public_exposure_apply_allowed=false
public_exposure_precondition_status=ready_for_operator_cutover_plan
next_action=separate_named_runtime_reload_or_public_cutover_gate
```

Listeners remained loopback/public-closed:

```text
127.0.0.1:3030 LISTEN
0.0.0.0:22 LISTEN
[::]:22 LISTEN
```

Local external probes after the gate:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Notes

The remote script printed `bash: line 203: $'\r': command not found` after the
`[remote] P7-C002a complete` line. The mutation and post-mutation evidence were
already complete. Temporary remote payload scripts were removed locally after
the run.

Because no service restart was performed, any currently running process may not
have reloaded the new `.env` values yet. Runtime reload/restart remains a
separate named gate.

## Что Не Выполнялось

Не выполнялись:

- service restart/deploy;
- reverse proxy install/apply;
- TLS certificate issue;
- firewall change;
- public listener change;
- public `3030` or `3040` exposure;
- public web/admin exposure;
- public API exposure;
- config delivery;
- write API enablement;
- Local Agent mutation;
- backup/import/reboot/restore apply;
- production peer/user mutation;
- destructive action;
- Telegram token use;
- live bot send;
- Telegram profile/media mutation;
- secret publication;
- upstream/GPL code copy.
