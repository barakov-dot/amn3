# AMN2 Phase 7 P7-C002 Public Exposure Gate Pre-Cutover

Дата: 2026-06-14.

Gate: `P7-C002 Public exposure gate`.

Target: disposable VPS `89.185.80.166`.

Commit: `b121865f488821f6fc471c9529fb26e5d7992515`.

Статус: `blocked-by-preconditions`.

Transcript:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\p7-c002-public-exposure-gate-20260614T181835Z.log
```

## Итог

`P7-C002` был открыт оператором как public exposure gate для `b121865`, но
выполнен только как read-only pre-cutover. Public exposure не применялась.

Remote verdict:

```text
public_exposure_apply_allowed=false
public_exposure_precondition_status=blocked
blocker=WEB_ADMIN_USERNAME_missing
blocker=public_domain_or_base_url_missing
next_action=stop_before_reverse_proxy_firewall_tls_apply
```

## Evidence Summary

Source overlay commit:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Runtime:

```text
web: 127.0.0.1:3030
api: not publicly listening
```

Listeners:

```text
127.0.0.1:3030 LISTEN
0.0.0.0:22 LISTEN
[::]:22 LISTEN
```

Reverse proxy/service inventory:

```text
nginx_active=inactive
caddy_active=inactive
apache2_active=inactive
traefik_active=inactive
nginx_binary=missing
caddy_binary=missing
apache2_binary=missing
traefik_binary=missing
certbot_binary=missing
```

Firewall:

```text
ufw status: inactive
iptables input policy: ACCEPT
```

Loopback web:

```text
web_root_loopback_http=303
web_login_loopback_http=200
```

Safe env flags:

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

External probes:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Notes

The remote script printed `bash: line 153: $'\r': command not found` after the
pre-cutover completion line. The collected evidence and local external probes
were already complete; this appears to be a CRLF line-ending artifact in the
temporary remote script, not a public exposure action.

## Что Не Выполнялось

Не выполнялись:

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
