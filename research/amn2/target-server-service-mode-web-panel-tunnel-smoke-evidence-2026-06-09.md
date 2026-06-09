# Target Server Service-Mode Web Panel Tunnel Smoke Evidence - 2026-06-09

Status: `phase3_service_mode_web_panel_tunnel_smoke_passed_read_only`.

Scope: read-only unauthenticated web-panel smoke through the operator SSH local port forward to the loopback-only web/admin service. This smoke did not submit login credentials, did not call POST routes, did not perform write operations, did not request config delivery, did not open API `3040`, and did not expose public web/admin `3030`.

## Safe Summary

```text
phase3_web_panel_tunnel_smoke: done
access_path: ssh-local-port-forward
local_tunnel_3030_listening: yes
local_login_http: 200
local_login_content_type: text/html; charset=utf-8
local_login_bytes: nonzero
local_root_http: 303
local_root_redirect: /login
login_has_form: yes
login_has_password_field: yes
login_forbidden_markers_count: 0
login_error_markers_count: 0
local_api_3040_http: 000
local_api_3040_connects: no
write_routes_called: no
login_credentials_submitted: no
config_delivery_requested: no
```

## Unauthenticated Protected Route Smoke

All sampled protected GET routes redirected to `/login` with HTTP `303`:

```text
/users: 303 -> /login
/servers: 303 -> /login
/orders: 303 -> /login
/logs: 303 -> /login
/settings: 303 -> /login
/config-templates: 303 -> /login
/api-readiness: 303 -> /login
/integration-status: 303 -> /login
/api-tokens: 303 -> /login
/devices/disabled: 303 -> /login
```

## Interpretation

The web/admin panel is reachable to the operator through the SSH tunnel, but unauthenticated protected pages do not render internal content. The login page renders normally and does not expose obvious error or secret-bearing markers in the response body.

The local `3040` check failed to connect as expected, confirming that this web-panel tunnel did not accidentally expose the API port to the operator workstation.

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
