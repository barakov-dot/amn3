# Target Server Service-Mode SSH Tunnel Access Evidence - 2026-06-09

Status: `phase3_service_mode_ssh_tunnel_access_passed`.

Scope: post-decision control after no-domain service-mode access path was selected. The operator opened the loopback web/admin panel through SSH local port forwarding in an external browser. This gate did not install or change reverse proxy software, did not create certificates, did not open public API `3040`, did not expose direct public web/admin `3030`, did not perform production peer/user writes, and did not publish secret-bearing artifacts.

## Safe Summary

```text
phase3_tunnel_access_control: done
amneziya-web_active: active
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_3030_loopback: yes
tcp_3040_absent: yes
VPS_APPLY_ENABLED_file_false: yes
operator_browser_opened: yes
access_path: ssh-local-port-forward
reverse_proxy_changed: no
public_https_cutover: no
```

## Interpretation

The no-domain access path is validated:

- `amneziya-web` and `amneziya-bot` are active under systemd;
- web/admin responds on the VPS loopback `/login` endpoint;
- remote TCP `3030` is loopback-only;
- remote TCP `3040` remains absent;
- `/opt/amn2/.env` explicitly contains `VPS_APPLY_ENABLED=false`;
- the operator was able to open the panel through an SSH local tunnel in a normal external browser.

This makes service-mode usable for operator web/admin access without public HTTPS, while keeping the public web/API surfaces closed.

## Current Safe Operating Mode

```text
mode: service-mode loopback web/bot
operator access: SSH local port forward to 127.0.0.1:3030
public web/admin 3030: closed by loopback binding
public API 3040: closed
reverse proxy / HTTPS: deferred until a domain exists
peer scope: remaining approved test peers only
```

## Boundaries

This evidence does not unlock:

- HTTPS reverse proxy/public cutover;
- public API `3040`;
- direct public web/admin `3030`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- production peer/user mutation beyond the remaining approved test peers.

## Secret Handling

No public IP, public host, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
