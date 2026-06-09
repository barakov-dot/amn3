# Target Server Protocol Identity And Numbered Peer Evidence - 2026-06-09

Status: `phase3_manual_mode_protocol_identity_checked`.

Scope: investigate the operator report that downloaded client configs did not visibly identify themselves as "Amnezia 2.0" in the client UI. This was a read-only investigation. No peer was added, revoked or regenerated. No client config, QR, key, PSK, endpoint, public IP or full server config was copied into this evidence.

## Client Artifact Shape

The operator checked the downloaded configs locally and reported only field-presence metadata.

```text
Neobyatnaya-AMNZ:   core_awg_fields_count=11, i_fields_count=0, protocol_guess=amneziawg-fields-present
Neobyatnaya-AMNZ-2: core_awg_fields_count=11, i_fields_count=0, protocol_guess=amneziawg-fields-present
Neobyatnaya-AMNZ-3: core_awg_fields_count=11, i_fields_count=0, protocol_guess=amneziawg-fields-present
Neobyatnaya-AMNZ-4: core_awg_fields_count=11, i_fields_count=0, protocol_guess=amneziawg-fields-present
```

Interpretation: the downloaded configs include the expected core AmneziaWG fields (`Jc`, `Jmin`, `Jmax`, `S1`-`S4`, `H1`-`H4`). The `I1`-`I5` fields are absent by design for the current server runtime because the live server config also does not include those fields.

## Live Server Shape And Numbered Peer Status

```text
protocol_identity_live_check: done
live_peer_count: 4
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
server_core_awg_fields_count: 11
server_i_fields_count: 0
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: connected-with-traffic
Neobyatnaya-AMNZ-3: not-yet
Neobyatnaya-AMNZ-4: not-yet
```

## Conclusion

The evidence does not support the hypothesis that the downloaded files are plain WireGuard or wrong Amnezia 1/1.5-style exports. Both client artifact metadata and live server config metadata have the same protocol-shape summary: core AmneziaWG fields present and `I1`-`I5` absent.

The likely root cause is UI/label ambiguity: the client import view may not display a human-readable "Amnezia 2.0" protocol label even when the imported `.conf` contains the AmneziaWG fields required by the current server runtime.

No config regeneration or re-delivery gate is required on this evidence alone. A future regenerate/re-delivery gate should be opened only if a tester has reproducible connection failure with a config that lacks the expected core AmneziaWG fields or mismatches the live server runtime.

## Secret Handling

No `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, public IP, backup contents or full logs were copied into this evidence.
