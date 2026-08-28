# Phase 16: first ARM connection failed

The operator reported that AmneziaVPN 5.0.1.5 did not connect and internet access disappeared during the attempt. Pilot acceptance remains blocked. No live settings were changed in this diagnostic turn.

## Verified observations

- UTC 18:06:43-18:06:45: the claim-bound pilot container was running with zero restarts, its interface was up, its configured port was 30002, and one peer was present. No handshake had ever completed; the peer had no learned endpoint and zero transferred bytes.
- UTC 18:12:57-18:13:01: the container UDP counters were all zero. Its internal forwarding and NAT had passed the earlier observation. No pilot port rules appeared in the host iptables exports.
- UTC 18:15:11-18:15:23: nftables showed DROP policies for IPv4 INPUT/FORWARD, an IPv4 wildcard UDP 30002 listener, and existing AWG2-specific routing/NAT rules. No rules referenced the new pilot port, bridge or container address.
- UTC 18:18:17-18:18:22: the broader allow-path report exceeded the local 16 KiB output acceptance bound. SSH exited 0 with empty stderr. Its content was not persisted or treated as accepted evidence.
- UTC 18:19:51-18:20:01: a narrower IPv4 allow-rule report succeeded. Explicit input UDP allowances excluded 30002; existing explicit forward allowances did not include the pilot bridge/address. The inherited rules_truncated flag describes the pre-filter rule count, not truncation of this filtered list.
- Client and service log files were not found in their inspected application log directories. Split tunneling toggles were false. The encrypted/opaque profile store could not be decoded by the bounded read-only comparison; imported-field equality is NOT established.

## Diagnosis boundary

There is a concrete server-readiness gap: the pilot runtime was created without integrating its network into the host firewall/NAT path. Container/parser health did not validate end-to-end connectivity. Fix this gap before another operator connection attempt; do not regenerate keys or guess MTU/DNS values. Additional client-side defects are not excluded until a handshake and real traffic pass.

Official 5.0.1.5 supports AWG3.1, and its tagged import parser includes the AWG3.1 field list. The older missing-field import report is not evidence of that bug in this version.

- https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.1.5
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/controllers/selfhosted/importController.cpp
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/utils/constants/configKeys.h

Evidence: ignored tmp/phase16-pilot-first-client-diagnostic-001.json, phase16-pilot-udp-path-readonly-001.json, phase16-pilot-nft-path-readonly-001.json, phase16-pilot-nft-allow-path-readonly-001.json and phase16-pilot-nft-ipv4-allows-readonly-001.json. All server observations used the pinned SSH trust bundle and normalized output; no raw traffic, keys or complete configurations were printed or persisted.

## Next boundary

Prepare a minimal pilot-only host firewall/NAT correction with rollback of only its added resources. Do not disable UFW, flush nftables, change existing AWG2 rules, reinstall the host, restart AWG2 or regenerate this peer. Re-test the workstation only after the network path is verified. Task 4.5 failed; Task 5 and closeout remain blocked.

Update at 18:49 UTC: the operator subsequently authorized the scoped correction. Temporary application and both network-path probes succeeded; the first real VPN handshake still remains pending. See [the separate firewall-fix receipt](phase16-pilot-firewall-fix-2026-08-28.md). This does not retroactively change the failed first test or claim client acceptance.
