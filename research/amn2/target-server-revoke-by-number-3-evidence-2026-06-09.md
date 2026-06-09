# Target Server Revoke-By-Number 3 Evidence - 2026-06-09

Status: `phase3_manual_mode_revoke_by_number_3_passed`.

Scope: controlled live revoke of exactly one operator-approved test peer, `Neobyatnaya-AMNZ-3`, using the prepared revoke-by-number runbook. This gate did not create any new peer, did not change service-mode, did not create a reverse proxy route, did not open public API or direct public web/admin access, and did not publish any secret-bearing material.

## Dry-Run Summary

```text
revoke_by_number_dry_run: done
target_name: Neobyatnaya-AMNZ-3
target_key_file_present: yes
target_in_persistent_config: yes
target_in_live_interface: yes
target_status_before: connected-with-traffic
live_peer_count_before: 4
tcp_3030_before: absent
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
dry_run_operation_id_present: yes
dry_run_risk_class_remote_state_write: yes
dry_run_no_changes_marker: yes
dry_run_remote_side_effects_marker: yes
dry_run_status: ok
```

## Live Revoke Summary

```text
revoke_by_number_live: done
target_name: Neobyatnaya-AMNZ-3
dry_run_operation_id_present: yes
dry_run_risk_class_remote_state_write: yes
dry_run_no_changes_marker: yes
dry_run_remote_side_effects_marker: yes
target_status_before: connected-with-traffic
live_peer_count_before: 4
tcp_3030_before: absent
tcp_3040_before: absent
target_in_persistent_after: no
target_in_live_after: no
live_peer_count_after: 3
tcp_3030_after: absent
tcp_3040_after: absent
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: not-yet
Neobyatnaya-AMNZ-3: not-found-on-server
Neobyatnaya-AMNZ-4: not-yet
live_revoke_status: ok
VPS_APPLY_ENABLED_reset: false
```

## Interpretation

The targeted peer `Neobyatnaya-AMNZ-3` was removed from both persistent config and live interface. The live peer count changed from `4` to `3`, matching the expected one-peer revoke. Direct public web/admin `3030` and public API `3040` remained absent.

The Docker runtime revoke path restarts the VPN container, so the immediate post-revoke sample showed the remaining peers as `not-yet`. This is expected until those clients reconnect and perform a fresh handshake after the container restart.

## Current Peer State

Current target state after this gate:

```text
approved_test_peers_remaining: 3
revoked_test_peer: Neobyatnaya-AMNZ-3
current_live_peer_count: 3
service_mode: not-enabled
reverse_proxy_public_https_cutover: not-enabled
public_api_3040: absent
direct_public_web_3030: absent
VPS_APPLY_ENABLED_final: false
```

## Post-Revoke Numbered Snapshot

A follow-up read-only numbered snapshot after the revoke gate confirmed that the revoked peer remained absent and the safety baseline remained closed.

```text
post_revoke_numbered_snapshot: done
live_peer_count: 3
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: not-yet
Neobyatnaya-AMNZ-3: not-found-on-server
Neobyatnaya-AMNZ-4: not-yet
```

Interpretation: `Neobyatnaya-AMNZ-3` remains revoked. The remaining peers had not produced a fresh post-restart handshake by this sample. This remains a reconnect follow-up, not evidence of wrong revocation.

## Post-Revoke Reconnect Snapshot

After manual reconnect/user browsing, a later read-only snapshot confirmed traffic for two remaining peers while the revoked peer stayed absent.

```text
post_revoke_reconnect_snapshot: done
live_peer_count: 3
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
Neobyatnaya-AMNZ-1: traffic-seen; handshake_age_sec=177
Neobyatnaya-AMNZ-2: traffic-seen; handshake_age_sec=36
Neobyatnaya-AMNZ-3: not-found-on-server
Neobyatnaya-AMNZ-4: not-yet
```

Interpretation: the revoke of `Neobyatnaya-AMNZ-3` did not prevent remaining peers `1` and `2` from reconnecting and passing traffic. Automatic reconnect after the Docker restart was not proven by this sample; manual reconnect/user activity was sufficient to restore traffic for the observed peers.

## Follow-Up

- Resample `Neobyatnaya-AMNZ-4` after that client attempts connection.
- Treat automatic reconnect behavior as unproven unless a separate controlled disruption test is approved.
- Do not regenerate or re-deliver configs by default.
- Do not revoke additional peers without a new explicit per-number gate.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
