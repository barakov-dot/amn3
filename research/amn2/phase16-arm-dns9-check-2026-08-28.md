# Phase 16: ARM DNS9 check

At the operator's request, a protected profile variant changed only DNS from 1.1.1.1 to 9.9.9.9. The original stayed unchanged. No new keys or peers were created. The operator confirmed import.

The local read-only measurement at 2026-08-28T19:50:46Z observed the pilot address and MTU 1280. The interface was connected, but the expected DNS was not present and the selected route to 1.1.1.1 was not on the pilot interface. TCP to 1.1.1.1:443 succeeded. Explicit DNS9 and system DNS queries failed; curl exited 6 with HTTP status 000. The pilot address was still present at the end. A later readback found the pilot disconnected.

The measurement began when the interface address appeared, without confirming that AmneziaVPN had finished applying its settings. This limits interpretation: neither permanent DNS misconfiguration nor successful TCP through the tunnel is established. The next measurement must distinguish startup from a settled Connected state. Acceptance and Task 4.5 remain pending.

The profile hashes were checked again after the measurement. Original SHA256: 0f97d55814824e7d34121143f8c8ed516984b0822e8a12a658d6059c69acfa65. DNS9 variant SHA256: 787000df3317c672588c0521635f7eaa061f7a2108142173c3a870c755cab730. The variant ACL remains protected. Config contents were not printed or added to Git.

Read-only client settings inspection found both split-tunneling toggles disabled. Saved profiles are encrypted; no profile decryption or client setting changes were performed. No readable client log was found in the inspected Amnezia directories.

An upstream report describes a similar Windows 11 / AmneziaVPN 5.0.1.5 handshake-without-traffic symptom: https://github.com/amnezia-vpn/amnezia-client/issues/3043 (checked 2026-08-28). This is an unconfirmed hypothesis for this pilot, not a demonstrated cause or fix.

No SSH, server write, AWG2 change, stage, install, package rebuild, or global issuance occurred during this check. Public push remains prohibited; only this non-secret record is eligible for a local commit.
