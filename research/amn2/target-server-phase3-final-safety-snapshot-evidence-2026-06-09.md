# Target Server Phase 3 Final Safety Snapshot Evidence - 2026-06-09

Status: `phase3_final_safety_snapshot_passed_with_source_overlay_git_metadata_unknown`.

Scope: final read-only safety snapshot after service-mode loopback systemd, no-domain SSH tunnel access, web-panel read-only smokes, and second Telegram admin ID addition. This snapshot did not apply/revoke peers, did not call write routes, did not request config delivery, did not open public API `3040`, did not expose direct public web/admin `3030`, did not install reverse proxy software, and did not publish secret-bearing artifacts.

## Safe Summary

```text
phase3_final_safety_snapshot: done
source_overlay_commit: unknown
runtime_type: docker
container_running: true
live_peer_count: 3
amneziya-web_enabled: enabled
amneziya-web_active: active
amneziya-bot_enabled: enabled
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_80: absent
tcp_443: absent
tcp_3030: present-loopback
tcp_3040: absent
VPS_APPLY_ENABLED_file_false: yes
numbered_mapping_count: 4
Neobyatnaya-AMNZ-1: traffic-seen
Neobyatnaya-AMNZ-2: traffic-seen
Neobyatnaya-AMNZ-3: not-found-on-server
Neobyatnaya-AMNZ-4: not-yet
production_write_surfaces: not-opened
config_delivery: not-opened
reverse_proxy_public_https: not-enabled
```

## Interpretation

The final Phase 3 safety surface is healthy:

- Docker runtime is running with `live_peer_count=3`;
- `Neobyatnaya-AMNZ-3` remains absent after the revoke-by-number gate;
- `Neobyatnaya-AMNZ-1` and `Neobyatnaya-AMNZ-2` have traffic history;
- `Neobyatnaya-AMNZ-4` remains `not-yet`;
- web and bot service-mode units are enabled and active;
- web/admin returns loopback `/login` HTTP `200`;
- TCP `3030` is loopback-only;
- TCP `80`, `443` and `3040` are absent;
- explicit `.env` `VPS_APPLY_ENABLED=false` is present;
- production write surfaces and config delivery remain closed;
- reverse proxy/public HTTPS remains disabled.

`source_overlay_commit` returned `unknown` in this snapshot, likely because `/opt/amn2` did not expose git metadata to this check. Earlier gates in this Phase 3 thread already tracked the current source-overlay package as `f7f6131`; this snapshot does not re-prove that commit and records the limitation explicitly.

## Current Safe Operating Mode

```text
mode: service-mode loopback web/bot
operator access: SSH local port forward to 127.0.0.1:3030
public web/admin 3030: closed by loopback binding
public API 3040: closed
reverse proxy / HTTPS: deferred until a domain exists
peer scope: remaining approved test peers only
```

## Remaining Follow-Up

- Run a bot admin read-only check for the second Telegram admin without approve/revoke/create actions.
- Decide whether to keep waiting for `Neobyatnaya-AMNZ-4` or revoke it as unused.
- Commit the Phase 3 evidence/runbooks in AMN3 once the operator is ready.

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
