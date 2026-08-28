# Phase 16: pilot DNS and HTTPS path checks

Recorded 2026-08-29; measurements occurred on 2026-08-28 UTC.

The operator reported recreating the connection, connecting, and still having no usable internet, while confirming two DNS addresses in the configuration. This is not evidence that Windows applied those addresses. The local check at 20:48:08Z found no pilot interface, so no new live client traffic test was performed in this turn.

Prior client evidence remains partial: at 20:37Z one source-bound HTTPS request returned 200, while HTTPS by IP timed out and explicit DNS9 failed. Both Quad9 addresses were absent from the observed interface. Later operator recreation must be measured separately; those earlier interface observations must not be presented as its current settings.

## Read-only server checks

At 20:54:22-20:54:25Z, one SSH session verified the existing pilot script hash, image digest, and claim binding. The container was running with zero restarts, one peer, forwarding enabled, and the expected NAT rule present. Native nslookup from inside the container returned exit 0 for both Quad9 and Cloudflare. The HTTPS check was not run because curl was absent (exit 127); absence of the tool is not an internet failure.

At 20:56:53-20:57:00Z, one separate SSH session used existing host Python via nsenter into the bound pilot network namespace. TCP to 1.1.1.1:443 succeeded, TLS certificate validation succeeded, and HTTPS returned 301. Nothing was installed. This validates egress from the pilot network namespace using the host TLS stack, not the entire forwarded VPN path from Windows.

Both observations reported RX 3839 / TX 3593 interface packets, zero interface errors/drops, and AWG transfer counters RX 1930153 / TX 3656516 bytes. The latest handshake ages were 323 and 479 seconds respectively. These are historical observations, not ongoing health monitoring or acceptance.

## Limits and next step

Server-namespace DNS/HTTPS work. A fault in Windows, the encrypted transport path, or forwarding of client-originated traffic is not ruled out. Do not infer a fully healthy server-to-client path from these egress checks. The two-address configuration correction has not established usable internet.

The next operator-synchronized client check should record actual DNS classes, route selection, and source-bound DNS/HTTPS behavior after connection recreation. Keep the VPN disconnected between checks. No additional DNS/MTU/config changes are justified by this result alone. Task 4.5 and client acceptance remain open.

No AWG2 probes or changes, remote file writes, service changes, stage/install, package rebuilds, new peers, or key generation occurred. Raw command output was held only in memory; saved receipts contain normalized fields and hashes. Existing immutable package attempts were not replayed.

Local normalized receipts:

- tmp/phase16-pilot-netns-egress-001.json: SHA256 52aaeee0083b8f4d5b5771fee2bbbb91b248029fc6ff43028be8a5aee86d6e4e.
- tmp/phase16-pilot-netns-https-001.json: SHA256 c1d755a3d67beffb83efc87e0a5c22daa31a5a424da79017756acb6c856a82e1.
