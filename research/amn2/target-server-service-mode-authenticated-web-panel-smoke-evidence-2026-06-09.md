# Target Server Service-Mode Authenticated Web Panel Smoke Evidence - 2026-06-09

Status: `phase3_service_mode_authenticated_web_panel_smoke_passed_read_only`.

Scope: operator-performed authenticated read-only web-panel smoke through the SSH local port forward. The operator logged into the web/admin panel in an external browser and sampled overview GET pages only. This smoke did not call POST routes, did not save settings, did not issue/revoke API tokens, did not run sync/health operations, did not request config delivery, did not perform peer/user writes, did not open public API `3040`, and did not expose direct public web/admin `3030`.

## Safe Summary

```text
authenticated_web_panel_smoke: done
access_path: ssh-local-port-forward
browser_path: external-browser-localhost
login_session: present
write_routes_called: no
config_delivery_requested: no
public_api_3040_opened: no
direct_public_web_3030_opened: no
```

## Authenticated Read-Only Route Smoke

All sampled authenticated GET pages returned HTTP `200` without redirect:

```text
/: 200
/users: 200
/servers: 200
/orders: 200
/logs: 200
/settings: 200
/config-templates: 200
/api-readiness: 200
/integration-status: 200
/api-tokens: 200
/devices/disabled: 200
```

## Interpretation

The service-mode web/admin panel is usable by the operator through the SSH tunnel after login. The sampled overview pages render as authenticated pages rather than redirecting back to `/login`.

This is a read-only panel smoke only. It proves authenticated navigation and page availability, not write-operation safety or production peer/user mutation readiness.

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

- authenticated destructive web-panel actions;
- API token issue/revoke;
- settings save/reset;
- server sync/health run operations;
- config delivery;
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

No public IP, public host, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents, session cookies or full logs were copied into this evidence.
