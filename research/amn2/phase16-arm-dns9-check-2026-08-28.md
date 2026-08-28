# Phase 16: ARM DNS9 check

At the operator's request, a protected profile variant changed only DNS from 1.1.1.1 to 9.9.9.9. The original stayed unchanged. No new keys or peers were created. The operator confirmed import.

The local read-only measurement at 2026-08-28T19:50:46Z observed the pilot address and MTU 1280. The interface was connected, but the expected DNS was not present and the selected route to 1.1.1.1 was not on the pilot interface. TCP to 1.1.1.1:443 succeeded. Explicit DNS9 and system DNS queries failed; curl exited 6 with HTTP status 000. The pilot address was still present at the end. A later readback found the pilot disconnected.

The measurement began when the interface address appeared, without confirming that AmneziaVPN had finished applying its settings. This limits interpretation: neither permanent DNS misconfiguration nor successful TCP through the tunnel is established. The next measurement must distinguish startup from a settled Connected state. Acceptance and Task 4.5 remain pending.

The profile hashes were checked again after the measurement. Original SHA256: 0f97d55814824e7d34121143f8c8ed516984b0822e8a12a658d6059c69acfa65. DNS9 variant SHA256: 787000df3317c672588c0521635f7eaa061f7a2108142173c3a870c755cab730. The variant ACL remains protected. Config contents were not printed or added to Git.

Read-only client settings inspection found both split-tunneling toggles disabled. Saved profiles are encrypted; no profile decryption or client setting changes were performed. No readable client log was found in the inspected Amnezia directories.

An upstream report describes a similar Windows 11 / AmneziaVPN 5.0.1.5 handshake-without-traffic symptom: https://github.com/amnezia-vpn/amnezia-client/issues/3043 (checked 2026-08-28). This is an unconfirmed hypothesis for this pilot, not a demonstrated cause or fix.

No SSH, server write, AWG2 change, stage, install, package rebuild, or global issuance occurred during this check. Public push remains prohibited; only this non-secret record is eligible for a local commit.

## Follow-up: settled connection and DNS import compatibility

The operator confirmed that AmneziaVPN had displayed Connected in the preceding test. One new operator-triggered read-only measurement ran on 2026-08-28 from 20:07:11Z to 20:07:41Z. The diagnostic was syntax-checked and its normalized snapshot/error handling checked with synthetic cmdlets before execution.

At interface creation, internet and DNS route queries returned CimException and were recorded as unknown, not false. After ten seconds, and again after the probes, routes to 1.1.1.1 and 9.9.9.9 used the pilot interface; the route to the Spain endpoint did not. MTU remained 1280. The interface had two DNS entries, neither including 9.9.9.9; their actual addresses were not collected.

TCP to 1.1.1.1:443, bound to the pilot source address, succeeded. Source-bound HTTPS by IP returned curl exit 35, status 000; source-bound HTTPS by domain returned exit 28, status 000. An explicit DNS9 query failed. No raw stderr, packet contents, or keys were collected. A subsequent local readback confirmed the pilot disconnected. This establishes a settled-state failure, not a complete diagnosis of HTTPS or transport quality.

Official tag 5.0.1.5 source inspection found that extractWireGuardConfig imports DNS only when its regular expression matches two IPv4 addresses on the DNS line. The one-address line used in the prepared profile does not match. NativeServerConfig and SelfHostedUserServerConfig fall back to application DNS settings when imported DNS fields are empty; the application defaults are 1.1.1.1 and 1.0.0.1. The observed missing DNS9 is consistent with this path. A local reproduction of the published expression using .NET matched the two-address synthetic line and rejected the single-address line; this was not a full Qt client import test.

Sources checked 2026-08-28:

- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/controllers/selfhosted/importController.cpp#L568
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/controllers/connectionController.cpp
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/models/selfhosted/nativeServerConfig.cpp
- https://github.com/amnezia-vpn/amnezia-client/blob/5.0.1.5/client/core/repositories/secureAppSettingsRepository.cpp
- https://docs.quad9.net/services/

A separate protected profile, Spain-AWG31-ARM-DNS9-DUAL.conf, was prepared in the same private-artifacts directory. Only the DNS line changed to the official Quad9 pair 9.9.9.9, 149.112.112.112. At 20:15:36Z, verification confirmed an exact inverse byte comparison, both original profile hashes unchanged, matching protected ACLs, and both DNS captures from the published regex. New profile SHA256: 85a7d02205da399bfc27b3030d104c7e836791e5bbd877549714cc82f2d02d3c.

No keys, peers, MTU, server configuration, app-wide settings, AWG2, or immutable package were changed. There was no SSH or server write. The new file is outside Git. Operator import and a subsequent live check remain pending; do not claim internet recovery or acceptance. Do not enable multiple variants of this same peer together. The generator still also needs this compatibility case addressed before future profile issuance; it was not changed in this bounded configuration-only correction.
