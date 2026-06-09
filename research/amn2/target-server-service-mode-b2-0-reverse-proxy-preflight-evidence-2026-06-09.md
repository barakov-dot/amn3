# Target Server Service-Mode B2.0 Reverse Proxy Preflight Evidence - 2026-06-09

Status: `phase3_service_mode_B2_0_reverse_proxy_preflight_passed_ready_for_choice`.

Scope: read-only reverse proxy / HTTPS preflight after B1 loopback-only systemd passed. This gate did not install proxy software, did not change firewall, did not create certificates, did not change DNS, did not create or change reverse proxy routes, and did not open public API or direct public web/admin access.

## Safe Summary

```text
phase3_B2_0_reverse_proxy_preflight: done
source_overlay_commit: f7f6131
VPS_APPLY_ENABLED_process: false
amneziya-web_enabled: enabled
amneziya-web_active: active
amneziya-bot_enabled: enabled
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_80: absent
tcp_443: absent
tcp_3030: present-loopback
tcp_3040: absent
nginx_installed: no
nginx_enabled: not-installed
nginx_active: not-installed
caddy_installed: no
caddy_enabled: not-installed
caddy_active: not-installed
certbot_installed: no
docker_installed: yes
docker_proxy_candidates_count: 0
ufw_summary: inactive
B2_0_writes_performed: no
reverse_proxy_changed: no
```

## Interpretation

The target is ready for an explicit B2 proxy choice:

- B1 loopback web/admin is healthy at `127.0.0.1:3030`.
- Public API `3040` remains absent.
- Direct public web/admin `3030` remains loopback-only.
- No existing nginx/Caddy/certbot/Nginx Proxy Manager stack is installed/running.
- No OS-level UFW rule is currently active, but provider-level firewall or security group state is not proven by this preflight.

## Recommended Next Step

Run B2.1 domain/package readiness before any write:

- choose a public host/domain privately;
- verify DNS resolution without publishing IP values;
- verify whether package repositories can install Caddy or nginx/certbot;
- choose the reverse proxy path.

Recommended path if package availability and DNS are good: Caddy reverse proxy to `127.0.0.1:3030`, because it keeps the B2 surface small and handles HTTPS certificates directly.

## Boundaries

B2.0 does not unlock:

- reverse proxy installation;
- opening ports `80`/`443`;
- HTTPS public cutover;
- public API `3040`;
- direct public web/admin `3030`;
- config delivery;
- production peer/user mutation beyond the remaining approved test peers;
- Local Agent write/config mutations;
- backup/import/reboot routes.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
