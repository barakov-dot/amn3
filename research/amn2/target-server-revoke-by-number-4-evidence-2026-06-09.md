# Target Server Revoke-By-Number 4 Evidence - 2026-06-09

Status: `phase3_revoke_by_number_4_passed_unused_peer_removed`.

Scope: operator-approved revoke-by-number gate for `Neobyatnaya-AMNZ-4`, which had remained unused with `target_status_before=not-yet`. The gate removed exactly this one test peer from persistent and live state. This did not create new peers, did not request config delivery, did not open public API `3040`, did not expose direct public web/admin `3030`, did not install or change reverse proxy, and did not publish secret-bearing artifacts.

## Dry-Run Safe Summary

```text
revoke_number_4_dry_run: done
target_name: Neobyatnaya-AMNZ-4
target_key_file_present: yes
target_in_persistent_config: yes
target_in_live_interface: yes
target_status_before: not-yet
live_peer_count_before: 3
amneziya-web_active: active
amneziya-bot_active: active
tcp_80_before: absent
tcp_443_before: absent
tcp_3030_before: present-loopback
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
dry_run_operation_id_present: yes
dry_run_risk_class_remote_state_write: yes
dry_run_no_changes_marker: yes
dry_run_remote_side_effects_marker: yes
dry_run_status: ok
```

## Live Revoke Safe Summary

```text
revoke_number_4_live: done
target_name: Neobyatnaya-AMNZ-4
target_status_before: not-yet
live_peer_count_before: 3
tcp_80_before: absent
tcp_443_before: absent
tcp_3030_before: present-loopback
tcp_3040_before: absent
target_in_persistent_after: no
target_in_live_after: no
live_peer_count_after: 2
amneziya-web_active: active
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_80_after: absent
tcp_443_after: absent
tcp_3030_after: present-loopback
tcp_3040_after: absent
live_revoke_status: ok
VPS_APPLY_ENABLED_process_reset: false
VPS_APPLY_ENABLED_file_false: yes
```

## Interpretation

The unused `Neobyatnaya-AMNZ-4` test peer was removed successfully:

- dry-run identified the target as present in persistent config and live interface;
- live revoke removed the target from both persistent and live state;
- live peer count changed from `3` to `2`;
- web and bot service-mode units remained active;
- web/admin loopback `/login` remained healthy;
- TCP `3030` remained loopback-only;
- TCP `80`, `443` and `3040` remained absent;
- `VPS_APPLY_ENABLED` was reset to false and `.env` still explicitly contains `VPS_APPLY_ENABLED=false`.

An earlier attempted live command failed with a local Python syntax error before printing the live-start marker and before executing the revoke operation. The successful live gate above is the actual state-changing operation recorded for #4.

## Post-Revoke Numbered Snapshot

```text
post_revoke_4_numbered_snapshot: done
live_peer_count: 2
amneziya-web_active: active
amneziya-bot_active: active
web_login_loopback_http: 200
tcp_80: absent
tcp_443: absent
tcp_3030: present-loopback
tcp_3040: absent
VPS_APPLY_ENABLED_file_false: yes
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: not-yet
Neobyatnaya-AMNZ-3: not-found-on-server
Neobyatnaya-AMNZ-4: not-found-on-server
```

The latest numbered snapshot confirms #3 and #4 remain absent after the #4 revoke. #1 and #2 showed `not-yet` in this immediate post-revoke sample, which is expected until clients reconnect after the Docker/AWG restart; both had prior `traffic-seen` evidence earlier in Phase 3.

## Current Safe Operating Mode

```text
mode: service-mode loopback web/bot
operator access: SSH local port forward to 127.0.0.1:3030
public web/admin 3030: closed by loopback binding
public API 3040: closed
reverse proxy / HTTPS: deferred until a domain exists
peer scope: two remaining approved test peers
revoked test peers: Neobyatnaya-AMNZ-3, Neobyatnaya-AMNZ-4
```

## Remaining Follow-Up

- Optionally resample `Neobyatnaya-AMNZ-1` and `Neobyatnaya-AMNZ-2` after clients reconnect if fresh live traffic evidence is needed.
- Commit the Phase 3 evidence/runbooks in AMN3 once the operator is ready.

## Boundaries

This evidence does not unlock:

- creating replacement peers;
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
