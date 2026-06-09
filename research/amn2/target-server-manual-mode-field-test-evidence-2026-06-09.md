# Target Server Manual Mode Field Test Evidence - 2026-06-09

Status: `phase3_manual_mode_field_test_partial_pass`.

Scope: read-only numbered live snapshot during real manual-runtime field testing with four operator-approved test peers left enabled. No peer was added, revoked or regenerated. No client config, QR, key, PSK, endpoint, public IP, raw server config or full runtime dump was copied into this evidence.

## Safe Summary

```text
numbered_live_snapshot: done
live_peer_count: 4
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
batch_public_key_dirs_count: 3
mapping_basis: first peer fixed; batch peers mapped by named remaining client_public.key directories after cleanup
Neobyatnaya-AMNZ-1: connected-with-traffic
Neobyatnaya-AMNZ-2: connected-with-traffic
Neobyatnaya-AMNZ-3: connected-with-traffic
Neobyatnaya-AMNZ-4: not-yet
connected_with_traffic_count: 3
```

## Interpretation

Manual runtime field testing is now proven for three of four approved test peers:

- at least three numbered profiles have observed handshake plus nonzero RX/TX traffic;
- the live peer count remains exactly `4`;
- direct public web/admin `3030` remains absent;
- public API `3040` remains absent;
- `VPS_APPLY_ENABLED=false` remains the baseline outside narrow approved gates;
- service-mode remains not enabled.

`Neobyatnaya-AMNZ-4` remains a follow-up item rather than a blocker for the manual-runtime field-test result. It should be resampled when that tester attempts connection.

## Remaining Manual-Mode Follow-Up

- Resample `Neobyatnaya-AMNZ-4` when the tester is online.
- Prepare a revoke-by-number runbook before expanding the test group or moving to broader exposure.
- Keep monitoring by friendly number without printing keys, peer public keys, client configs or endpoint data.

## Secret Handling

No `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, public IP, backup contents or full logs were copied into this evidence.
