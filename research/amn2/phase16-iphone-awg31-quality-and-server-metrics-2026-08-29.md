# Phase 16 — iPhone AWG3.1 quality and synchronized server metrics

- Recorded: `2026-08-29`
- Status: `connectivity-pass-quality-fail-root-cause-open`
- Target: Spain AWG3.1 minimal pilot, UDP 30002
- Client: iPhone, AmneziaWG, operator-owned pilot use
- Profile SHA-256: `66afe3784b4b16148c4fbd252a8cffe3a4f7da889ce412f827afcd817cef8146`
- Server write, signal, restart, install or config change: `false`
- AWG2 changed: `false`
- General AWG3.1 issuance enabled: `false`

## Scope and safety

The same single-peer checksum-bound profile was used sequentially after the
Android and Windows attempts were disconnected. No private key, PSK,
HeaderProtectionKey, raw config, peer public key, client endpoint, packet
capture or DNS query content was collected or added to Git. Server-side output
was reduced remotely to aggregate counters before transport.

The operator reported successful iPhone connection and ordinary Internet use.
Reconnect plus DNS/HTTPS page load completed in approximately 2–3 seconds.
This is a connectivity PASS, not performance or stability acceptance.

## Client quality observations

All listed measurements used the same iPhone and Wi-Fi access network.

No-VPN Cloudflare baseline:

- download: 331 Mbps;
- upload: 150 Mbps;
- latency: 41.1 ms;
- jitter: 18.2 ms;
- packet loss: 0%;
- network quality: Great for video streaming, online gaming and video chat.

Spain AWG3.1 observations:

| Run | Download | Upload | Latency | Jitter | Packet-loss result | Quality/result |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 19.8 Mbps | 1.96 Mbps | 112 ms | 287 ms | 20.5% | all three Cloudflare quality classes Bad |
| 2 | 11.9 Mbps | 2.34 Mbps | 95 ms | 2.66 ms idle; loaded jitter reached seconds | ICE connection timeout | incomplete/unstable |
| 3, synchronized | 33.7 Mbps | 1.89 Mbps | 95 ms | 159 ms | ICE connection timeout | Poor / Poor / Bad |

The healthy no-VPN baseline and three materially degraded AWG3.1 samples make
the result repeatable enough to block performance acceptance. They do not by
themselves distinguish AWG3.1 implementation behaviour from the client-to-VPS
UDP route or provider handling.

## Synchronized server observation

The third client run was observed through a bounded 150-second read-only SSH
window. One pilot peer remained present. The handshake refreshed when the
client traffic began, and the counters changed as follows:

- peer received: +3,041,673 bytes;
- peer sent: +9,620,817 bytes;
- `awg3` interface RX: +492,487 bytes;
- `awg3` interface TX: +8,772,138 bytes;
- `awg3` RX/TX errors and dropped: 0 throughout.

The post-run snapshot showed:

- pilot container: running;
- CPU: 0.01% at the post-run sample;
- memory: 43.54 MiB of 961.5 MiB;
- host load average: 0.00 / 0.04 / 0.04;
- host default interface `ens3`: RX/TX errors and dropped 0 at the snapshot.

The post-run CPU sample is not a peak-CPU trace. It is evidence against an
obvious persistent resource-pressure condition, not proof that no transient
pressure occurred.

## Bounded VPS egress observation

A separate approved read-only check downloaded exactly 10,000,000 bytes from
Cloudflare to `/dev/null`:

- HTTP: 200;
- measured rate: 28,611,402 B/s, approximately 228.9 Mbps;
- connect: 0.058707 s;
- first byte: 0.155450 s;
- total: 0.349511 s.

Parallel ICMP samples to `1.1.1.1` and `8.8.8.8` both returned nonzero. The two
interleaved summaries observed 12.5% and 37.5% loss respectively, but the
parallel output does not safely bind either percentage to one target. ICMP may
be deprioritized or rate-limited, so these samples are a path-instability
signal, not proof of equivalent HTTPS or AWG UDP loss.

An earlier 25 MB attempt lost its local stdout and is excluded from evidence.
No second 25 MB download was performed.

## A/B and decision boundary

The operator reiterated that the earlier Spain AWG2 client path had also been
slow and unstable. That is relevant qualitative history, but no fresh
same-iPhone quantitative AWG2 run was available. A surviving AWG2 profile was
confirmed by the operator to belong to an old USA server and was excluded.
Therefore the strict same-device Spain AWG2-versus-AWG3.1 comparison remains
incomplete and must not be marked PASS.

The available evidence places the unresolved boundary on the iPhone-to-Spain
VPS UDP/AWG path. The local Wi-Fi baseline, direct VPS HTTPS capacity and
server/container/interface health do not explain the observed degradation.
Separating the access-network/provider route from AWG3.1 client transport
requires a second access network or another equivalently controlled client
path; mobile Internet was unavailable during this run.

## Decision

- iPhone connectivity and reconnect: PASS;
- AWG3.1 performance/stability: FAIL for current acceptance;
- Task 4.5 strict AWG2/AWG3.1 A/B: incomplete;
- Task 5 acceptance: blocked on the quality root cause;
- Task 6 closeout: blocked;
- Windows Task 4A: remains a separate client transport failure;
- AWG2, application stage, install and general AWG3.1 issuance: unchanged.

No server mutation, application integration, install, config issuance, push or
global rollout is authorized by this evidence note.
