# Phase 16 — iPhone AWG3.1 alternate-network quality retest

- Recorded: `2026-08-30`
- Status: `connectivity-pass-quality-fail-second-network-strict-ab-incomplete`
- Client: iPhone, AmneziaWG, operator-owned pilot use
- Profile SHA-256:
  `66afe3784b4b16148c4fbd252a8cffe3a4f7da889ce412f827afcd817cef8146`
- Access network: operator-designated network different from the first iPhone
  quality run; provider and client identifiers not retained
- Server SSH/read/write/signal/restart: `false`
- Install/profile/server/AWG2 change: `false`
- General AWG3.1 issuance enabled: `false`

## Scope and custody

Windows, Android, INCY and other VPN paths were off. The single checksum-bound
peer was used only on the iPhone. The operator supplied screenshots for two VPN
measurements, before and after reconnect, and one no-VPN baseline on the same
second access network. The screenshots remain outside Git; this receipt keeps
only normalized metrics and result classifications.

No private key, PSK, HeaderProtectionKey, raw profile, peer public key, client
address, access-network provider identity, packet capture or DNS content was
collected or committed.

## Normalized observations

| Mode | Download | Upload | Latency | Jitter | Packet-loss result |
| --- | ---: | ---: | ---: | ---: | --- |
| No VPN baseline | 9.68 Mbps | 5.37 Mbps | 86.7 ms | 58.3 ms | unmeasured; ICE connection timeout |
| AWG3.1 before reconnect | 8.87 Mbps | 1.70 Mbps | 132 ms | 370 ms | 77.4% |
| AWG3.1 after reconnect | 7.65 Mbps | 0.593 Mbps | 159 ms | 403 ms | 46.8% |

Relative to the same-network no-VPN baseline:

- download was lower by approximately 8% before reconnect and 21% after;
- upload was lower by approximately 68% before reconnect and 89% after;
- latency was approximately 1.52x and 1.83x the baseline;
- jitter was approximately 6.35x and 6.91x the baseline.

Packet-loss percentages are not compared with the baseline because Cloudflare
did not produce a baseline percentage. The ICE timeout is not equivalent to
zero loss and is not converted into a percentage.

## Functional result

The operator confirmed that ordinary HTTPS pages, YouTube and Telegram worked
through AWG3.1. After disconnect and reconnect, application reachability
returned in approximately 2–3 seconds and no more than 5 seconds.

Therefore:

- connectivity: PASS;
- application reachability: PASS;
- reconnect: PASS;
- performance/stability quality: FAIL for acceptance.

Reconnect did not correct the measured upload, latency or jitter impairment.

## Interpretation boundary

The second access network itself was capacity-limited: its no-VPN download was
9.68 Mbps. This run therefore does not reproduce the first network's large
331-to-11.9–33.7 Mbps download collapse as a clean download comparison.

It does independently reproduce material AWG3.1-associated degradation in
upload, latency and jitter on the operator-designated second network. The first
access network alone is insufficient to explain all observed Phase 16 quality
symptoms. This does not prove an AWG3.1 source defect or identify a server,
client, provider or UDP-route root cause.

The strict Spain AWG2 versus AWG3.1 comparison is still missing. No current
Spain AWG2 profile was available on this iPhone, and the old USA profile
remains excluded. No parameter change follows from this evidence.

## Gate effect

- Task 4C iPhone connectivity/reconnect remains passed; performance remains
  failed for acceptance.
- Task 4.5 remains `quality-fail-root-cause-open-strict-ab-incomplete`.
- Task 3B, Task 5 and Task 6 remain blocked.
- Windows Task 4A remains a separate official-upstream client blocker.
- AWG2 remains `UNTOUCHED`.
- Application stage, install and general AWG3.1 issuance remain disabled.

No further live run, server action, config change, integration or rollout is
authorized by this receipt.
