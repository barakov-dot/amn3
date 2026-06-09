# Target Server Service-Mode B2.1 Reverse Proxy Readiness Evidence - 2026-06-09

Status: `phase3_service_mode_B2_1_reverse_proxy_readiness_blocked_before_public_cutover`.

Scope: read-only domain, package and baseline readiness check before any HTTPS reverse proxy installation or public cutover. This gate did not install Caddy/nginx/certbot, did not create or modify certificates, did not change firewall/provider rules, did not change DNS, did not create reverse proxy routes, did not open public API `3040`, and did not expose direct public web/admin `3030`.

## Safe Summary

```text
phase3_B2_1_reverse_proxy_readiness: done
public_host_present: yes
public_host_format_valid: yes
dns_a_count: 0
dns_aaaa_count: 0
dns_matches_vps_route_v4: unknown
amneziya-web_enabled: enabled
amneziya-web_active: active
amneziya-bot_enabled: enabled
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_80: absent
tcp_443: absent
tcp_3030: present-loopback
tcp_3040: absent
caddy_installed: no
nginx_installed: no
certbot_installed: no
caddy_apt_candidate_present: yes
nginx_apt_candidate_present: yes
certbot_apt_candidate_present: yes
VPS_APPLY_ENABLED_file_false: no
B2_1_writes_performed: no
reverse_proxy_changed: no
```

## Interpretation

B2.1 is intentionally blocked before any public HTTPS cutover:

- the chosen public host has valid syntax, but no A/AAAA DNS records were visible from the VPS;
- DNS cannot yet be proven to point at the target VPS route source;
- package repositories can provide Caddy, nginx and certbot;
- B1 loopback service-mode remains healthy: web/admin is enabled, active and returns `/login` HTTP `200`;
- TCP `3030` is present only on loopback, which is expected after B1;
- TCP `3040`, `80` and `443` remain absent;
- the `.env` file did not prove an explicit `VPS_APPLY_ENABLED=false` line in this read-only check, so the file baseline must be fixed before public cutover even though earlier process-level checks were false.

## Required Follow-Up Before B2.2

- Create or fix the DNS record for the chosen public host through the provider/DNS panel without publishing the host or IP in chat.
- Reconfirm `dns_a_count >= 1` and `dns_matches_vps_route_v4=yes` from the VPS.
- Set an explicit `VPS_APPLY_ENABLED=false` line in `/opt/amn2/.env` through a separate small baseline-fix gate.
- Re-run B2.1 after DNS propagation and baseline fix.

Recommended path after B2.1 is green: Caddy reverse proxy to `127.0.0.1:3030`, because it keeps the B2 surface small and does not require opening public API `3040`.

## Boundaries

B2.1 does not unlock:

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

No public host, public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
