# AMN2 Phase 7 Public Cutover Guard

Дата: 2026-06-18.

Gate: `P7-C002` public cutover gate.

Статус: `blocked-by-domain-tls-plan-not-exposed`.

Target: disposable VPS `89.185.80.166`.

AMN2 source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Transcript:

```text
tmp/p7-c002-public-cutover-guard-20260618T124833Z.log
```

## Operator Gate

Оператор открыл exact named gate:

```text
Открываю P7-C002 public cutover gate для b121865 на текущем disposable VPS 89.185.80.166.
```

Перед apply был выполнен read-only guard-preflight. Он не устанавливал пакеты,
не перезапускал сервисы, не менял `.env`, reverse proxy, TLS, firewall или
public listener.

## Runtime And Listener Snapshot

Remote source overlay:

```text
b121865f488821f6fc471c9529fb26e5d7992515
```

Manual runtime stayed loopback-only:

```text
166198 /opt/amn2/venv/bin/python -m app.cli web serve --host 127.0.0.1 --port 3030
166199 /opt/amn2/venv/bin/python -m app.main
LISTEN 0 2048 127.0.0.1:3030 0.0.0.0:* users:(("python",pid=166198,fd=6))
```

No direct public AMN2 listener was opened.

## Reverse Proxy / Firewall Inventory

Reverse proxy and TLS tooling:

```text
nginx_binary=missing
caddy_binary=missing
apache2_binary=missing
traefik_binary=missing
certbot_binary=missing
openssl_binary=present
ufw_binary=present
iptables_binary=present
```

Firewall snapshot:

```text
Status: inactive
-P INPUT ACCEPT
```

## Cutover Prerequisites

Safe env summary:

```text
APP_SECRET_KEY=present
WEB_ADMIN_USERNAME=present
WEB_ADMIN_PASSWORD_HASH=present
WEB_ADMIN_SESSION_SECRET=present
PUBLIC_BASE_URL=present
PUBLIC_DOMAIN=present
WEB_PUBLIC_BASE_URL=present
PUBLIC_BASE_URL_scheme=https
PUBLIC_BASE_URL_host_type=ip
PUBLIC_DOMAIN_type=ip
VPS_APPLY_ENABLED=false
LOCAL_AGENT_ENABLED=false
```

Guard verdict:

```text
preflight_blocker_count=1
blocker=trusted_tls_requires_dns_domain_not_ip
public_cutover_guard_status=blocked
public_cutover_apply_allowed=false
secret_values_printed=false
```

Interpretation:

- admin credential contract is present;
- loopback runtime/login is already verified by `P7-C002b`;
- current `PUBLIC_BASE_URL` / `PUBLIC_DOMAIN` points to an IP address;
- trusted TLS cutover requires an operator-provided DNS domain, not raw IP;
- reverse proxy/TLS tooling is not installed;
- cutover was stopped before any apply.

## Probe Results

Loopback checks:

```text
web_login_loopback_http=200
web_root_loopback_http=303
```

Remote local public-port probes:

```text
http://127.0.0.1:80/ 000
https://127.0.0.1:443/ 000
http://127.0.0.1:3030/login 200
http://127.0.0.1:3040/api/servers 000
```

External probes:

```text
http://89.185.80.166:3030/login 000
http://89.185.80.166:3040/api/servers 000
http://89.185.80.166:80/ 000
https://89.185.80.166:443/ 000
```

## Mutation Status

```text
service_restart_performed=false
env_mutation_performed=false
package_install_performed=false
reverse_proxy_apply_performed=false
firewall_apply_performed=false
tls_apply_performed=false
public_listener_change_performed=false
public_api_3040_exposed=false
```

## Verdict

`P7-C002` public cutover was safely stopped as
`blocked-by-domain-tls-plan-not-exposed`.

No public exposure was applied. `3030` and `3040` remain closed externally.

Next allowed action is a separate exact named prerequisite gate that supplies a
DNS domain / public base URL and chooses a reverse proxy + TLS mode, or
watch-only intake. Do not retry public cutover against raw IP as a trusted TLS
path.
