# Phase 16: temporary pilot firewall integration

## Authority and scope

The operator explicitly approved the preceding proposal to add temporary host firewall/NAT rules for the existing AWG3.1 pilot, replying: "разрешаю все для достижения результата". This was used only for the scoped pilot correction and bounded network checks, not as authority to change AWG2, disable UFW, publish Git history, reinstall software, replace profiles, or enable general issuance.

Existing pilot: `pilot-spain-awg31-arm-20260828-002`, container `amn2-spain-awg31-pilot`, bridge `amn2sp31p0`, container address `172.29.252.2`, public UDP port `30002`. Container/image/claim/network/mount/profile bindings were checked before mutation. The v4 pilot source and both existing profiles were not modified.

## Local verification

- TDD: seven initial RED tests before the module existed; four additional transaction RED tests before the transaction function existed; one additional RED race test before atomic rejection handling.
- 12/12 tests passed before live execution. Covered: pilot-only rules, input validation, exact-handle rollback, foreign-resource refusal, unrelated-drift preservation, failed native-check, failed network probe, and no cleanup after a known atomic rejection by a racing writer.
- Post-run local review added a RED/GREEN named-counter identity test. Final result: 13/13 PASS. Only packet/byte values are normalized; named-counter identity and other properties remain significant. This local refinement did not reapply or change the live rules.
- Live-executed helper SHA256: `9aa7715844e1843ad9dbae8a149f08c1612d46fdf8033b40e4a6b53e1d930e32`.
- Final local helper SHA256 after the counter-identity refinement: `efb60e924691d559d9fa141c9f2c0a243e14fd3d7721e7b9e3b69b55ef8977cb`.
- Existing packages and their materialization/verifier were not rerun. No workstation VPN was toggled by automation.

## Live sequence (UTC)

1. **18:44:52-18:45:01:** native `nft -c -f -` passed. The state fence stopped the transaction before any real firewall write. The exact source of that transient mismatch was not captured and is not claimed as diagnosed.
2. **18:46:33-18:46:41:** a separate bounded read-only comparison, with native-check between snapshots, found AWG2 equality, firewall equality, no owned resources, and zero differing normalized fields. No checks were weakened.
3. **18:47:39-18:47:46:** a new attempt passed the same preconditions and native-check, then committed one nft batch. Existing firewall and fresh AWG2 fingerprints remained equal. A TCP connection to `1.1.1.1:443` from the existing pilot network namespace succeeded; no HTTP payload was sent.
4. **18:48:48-18:48:59:** one constant non-secret UDP probe was sent from the workstation to the pilot. Read-only counters confirmed passage through DNAT and FORWARD to the container socket. No raw packet capture was performed.

All SSH sessions used the pinned trust bundle with strict host-key checking. Remote source ran in memory; no remote helper file or persistent firewall configuration was written. The first stopped attempt and subsequent receipts are separate, never overwritten. There is no automatic retry loop.

## Actual changes and rollback boundary

- Created only `ip amn2_p16_awg31`, with prerouting/postrouting NAT chains.
- DNAT only on the observed external interface, destination `138.124.181.246`, UDP `30002`, to `172.29.252.2:30002`.
- MASQUERADE only for `172.29.252.2` leaving that external interface.
- Three scoped rules inserted in existing `ip filter FORWARD`: inbound DNAT pilot UDP; pilot outbound; established/related replies to the pilot.
- No INPUT rules, policy changes, flushes, UFW disablement, AWG2 changes, container restarts, new peers, new keys, or profile edits.
- Added FORWARD handles at success: `168,167,166`. Tags are `amn2_p16_awg31:return`, `amn2_p16_awg31:out`, `amn2_p16_awg31:in` respectively. Before any future rollback, revalidate ownership, the complete resource set and current handles; never delete blindly using stale handles.
- Rollback removes only the three owned rules and owned NAT table. It refuses foreign additions in the owned namespace and never restores an old whole-host ruleset over concurrent changes.
- The rules are temporary: no persistence across reboot or firewall reload was installed. Native atomic transactions and handles follow the [official nft manual](https://netfilter.org/projects/nftables/manpage.html) and [atomic rule documentation](https://wiki.iptables.org/wiki-nftables/index.php/Atomic_rule_replacement).

## Verified result, not client acceptance

At the 18:48:59 UTC network-probe readback:

- Pilot firewall complete: true; existing firewall equal: true.
- Own rule packet counters: DNAT 1, inbound 1, MASQUERADE 1, outbound 4, return 2.
- Container UDP: InDatagrams 1, OutDatagrams 0, NoPorts 0, InErrors 0.
- Exactly one peer; no handshake yet; VPN RX/TX still zero.

This verifies the missing host network path, not a working AWG3.1 session. The operator was asked to reconnect the unchanged protected `Spain-AWG31-ARM.conf` for 30-60 seconds, without simultaneous AWG2, and disconnect if internet stayed unavailable for 15-20 seconds. Actual handshake, user traffic, stability, DNS and A/B acceptance remain pending.

### Second operator test

The operator subsequently reported that the client connected but internet was still unavailable. At **19:00:18-19:00:26 UTC**, a separate read-only observation confirmed an actual AWG3.1 handshake (age 213 seconds), one peer, RX 386172 bytes and TX 1165377 bytes. Container UDP counters were 906 received / 1046 sent, zero NoPorts and zero InErrors. Pilot rules were complete, and the pre-existing firewall baseline remained equal. This is real protocol progress, not client acceptance or proof of healthy internet access.

The operator was asked to disconnect. A local read-only adapter inventory then found no active or retained Amnezia/WireGuard/Wintun candidate. A short, read-only workstation route/DNS/HTTPS check was prepared for the next operator-controlled connection; no speculative MTU, DNS, IPv6, proxy or client changes were made. Second-test server receipt: `tmp/phase16-pilot-second-client-diagnostic-001.json`.

## Evidence

Ignored local receipts:

- `tmp/phase16-pilot-firewall-apply-001.json`: stop before mutation.
- `tmp/phase16-pilot-firewall-state-diagnostic-001.json`: bounded read-only comparison.
- `tmp/phase16-pilot-firewall-apply-002.json`: SHA256 `b5186cf545349b7511e864f0260c1746554b2f61efb0703c1dde5c6e2c300517`.
- `tmp/phase16-pilot-firewall-network-readback-001.json`: SHA256 `2d250516b9172e2df76c6ed4a37808c046bd43c7305c7f37802b24d649ba5981`.

Existing-firewall baseline at application/readback: `4f591e8249abff5bf8fe6eb5f1b77841eab8ef74813e8163d36f6c0f186b978c`. No raw secrets, traffic, stdout/stderr, full profiles or client registry content were persisted. Public Git push remains outside the approved publication boundary.
