# Target Server Service-Mode No-Domain SSH Tunnel Decision - 2026-06-09

Status: `phase3_service_mode_no_domain_ssh_tunnel_access_selected`.

Scope: operator decision after B2.1 showed no public DNS records for the selected host and the operator confirmed that the current access basis is IP-only, with no domain available. Public HTTPS reverse proxy cutover is deferred. The selected access path is SSH local port forwarding to the loopback-only web/admin service.

## Safe Summary

```text
domain_available: no
public_https_cutover: deferred
reverse_proxy_installation: not-authorized
reverse_proxy_changed: no
access_path_selected: ssh-local-port-forward
remote_web_bind: 127.0.0.1:3030
browser_path: external-browser-localhost
codex_preview_required: no
public_api_3040: closed
direct_public_web_3030: closed
production_peer_writes: not-authorized
config_delivery: not-authorized
```

## Interpretation

Without a domain, the safe service-mode access path is to keep `amneziya-web` bound to loopback and reach it through an SSH tunnel from the operator workstation.

This avoids:

- exposing direct public web/admin `3030`;
- exposing public API `3040`;
- installing reverse proxy software prematurely;
- accepting an IP-only HTTP or self-signed HTTPS admin surface.

## Operator Runbook

Runbook: `docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md`.

The tunnel command is intentionally operator-local and must use the private VPS address known to the operator. Public host/IP values are not copied into this evidence.

## Remaining Gate

If a domain is added later, return to B2.1 domain/package readiness:

- verify DNS resolution from the VPS without publishing IP values;
- prove DNS points at the target VPS route source;
- prove explicit `.env` `VPS_APPLY_ENABLED=false`;
- then run a separate Caddy/HTTPS write gate.

## Boundaries

This decision does not unlock:

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
