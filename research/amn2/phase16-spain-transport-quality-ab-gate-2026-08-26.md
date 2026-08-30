# Phase 16 Spain transport-quality A/B gate

- Recorded: `2026-08-26`
- Status: `quality-fail-root-cause-open-strict-ab-incomplete`
- Priority: after Task 4 and before Task 5 acceptance or Task 6 closeout
- Scope: one operator client, Spain AWG2 and the first Spain AWG3.1 pilot
- Package 016 changed by this update: `false`
- Live action authorized by this note: `false`

## Operator observation

The operator reported that the current Spain AWG2 configuration is unstable
and slow on this computer, while the server does not show the same speed
problem on other protocols. This is an observed client-path symptom, not yet a
confirmed server, protocol, configuration, MTU, DNS, firewall, Docker, or
network root cause.

## Evidence update — 2026-08-30 alternate access network

The same checksum-bound iPhone AWG3.1 profile was retested sequentially on an
operator-designated second access network. HTTPS pages, YouTube and Telegram
worked, and reconnect restored application reachability in approximately 2–3
seconds and no more than 5 seconds. Connectivity/reconnect therefore remain a
PASS.

The same-network no-VPN baseline was 9.68/5.37 Mbps with 86.7 ms latency and
58.3 ms jitter. AWG3.1 measured 8.87/1.70 Mbps, 132 ms and 370 ms before
reconnect, then 7.65/0.593 Mbps, 159 ms and 403 ms after reconnect. The VPN
packet-loss results were 77.4% and 46.8%; the no-VPN percentage is unavailable
because the Cloudflare ICE test timed out, so loss is not compared across
modes.

The second network was already download-limited, but AWG3.1 still materially
worsened upload, latency and jitter. This means the first access network alone
does not explain all observed quality symptoms. It does not prove a protocol
source defect or complete the mandatory Spain AWG2 versus AWG3.1 comparison.
Task 4.5 remains failed/incomplete. Full evidence:
`research/amn2/phase16-iphone-awg31-alternate-network-quality-retest-2026-08-30.md`.

## Evidence update — 2026-08-29

The first Spain AWG3.1 pilot was tested sequentially on iPhone with the
checksum-bound profile. Connectivity and 2–3 second reconnect/DNS/HTTPS passed,
but three quality samples were materially degraded against a healthy no-VPN
baseline. The synchronized sample measured 33.7/1.89 Mbps, 95 ms latency,
159 ms jitter and an ICE packet-loss-test timeout, while the no-VPN baseline
measured 331/150 Mbps, 41.1 ms, 18.2 ms jitter and 0% loss.

During the synchronized sample the server observed a fresh handshake and
bidirectional traffic with zero `awg3` errors/dropped. Post-run container and
host snapshots showed no persistent load or interface-drop condition. Direct
VPS Cloudflare HTTPS download reached approximately 228.9 Mbps. This narrows
the unresolved boundary to the client-to-Spain UDP/AWG path, but does not yet
separate access-network/provider behaviour from AWG3.1 client transport.

The operator's prior Spain AWG2 instability remains qualitative evidence. No
fresh same-iPhone Spain AWG2 profile was available; an old USA AWG2 profile was
explicitly excluded. The strict quantitative AWG2/AWG3.1 comparison therefore
remains incomplete. Task 5 and Task 6 are blocked because AWG3.1 itself is
currently unstable. Full evidence:
`research/amn2/phase16-iphone-awg31-quality-and-server-metrics-2026-08-29.md`.

The Windows 11 / AmneziaVPN 5.0.1.5 run is a separate acceptance blocker.
Wintun creation, interface Up, MTU 1280, handshake and keepalive were observed,
but application traffic failed; disabling kill switch did not restore it. The
observed class matches open official upstream issue #3043, without proving the
final root cause. Acceptance requires a bounded retest after an official
upstream fix or supported client path; server, port, DNS, MTU, firewall and the
profile must not be changed speculatively. Evidence commit: `eefe693`; full
evidence:
`research/amn2/phase16-windows-awg31-data-plane-regression-2026-08-29.md`.

## Mandatory placement in Phase 16

1. Complete Task 3 controlled server-only stage under its separate exact
   approval.
2. Complete Task 4 under a separate exact pilot approval and create exactly one
   operator-owned AWG3.1 profile, peer, and `.conf`.
3. Run this Task 4.5 A/B gate on the same computer and access network before
   Task 5 acceptance and before Phase 16 closeout.
4. Preserve AWG2 throughout the comparison; do not stop, restart, rewrite, or
   reissue it as part of this gate.

## Bounded A/B observations

Compare AWG2 and AWG3.1 sequentially under materially equivalent client and
access-network conditions. Record only normalized, non-secret results for:

- connection stability and disconnects;
- packet loss;
- RTT and jitter;
- download and upload throughput;
- reconnect behavior;
- MTU and fragmentation symptoms;
- DNS resolution and reachability.

Collect matching read-only server-side classifications for:

- interface errors and drops;
- Docker and network-namespace path;
- UDP listener and traffic path;
- CPU and softirq pressure;
- firewall path and counters.

Do not capture raw traffic, private keys, PSKs, HeaderProtectionKey values,
complete configs, DNS query contents, or unrelated client/server data. Do not
change parameters speculatively. Any mutation or expanded diagnostic requires
its own exact approval and evidence binding.

## Decision contract

- If AWG3.1 is also unstable or materially degraded, block Task 5 acceptance
  and Task 6 closeout until a root cause is identified and a bounded TDD
  correction is verified.
- If AWG3.1 is stable while the existing AWG2 path remains degraded, continue
  AWG3.1 acceptance and open a separate high-priority AWG2 remediation item.
- If both paths are stable during the bounded observation, record that the
  original AWG2 symptom was not reproduced; do not infer that it is fixed.
- In every outcome, keep general AWG3 issuance disabled until Phase 16
  acceptance and closeout explicitly permit otherwise.

## Current Phase 16 order

1. Task 0 — local baseline: complete.
2. Task 1 — AWG3.1 code and package 016/local tooling: complete.
3. Task 2 — checksum-bound Spain read-only preflight: complete/PASS.
4. Task 3A — minimal isolated AWG3.1 runtime: complete.
5. Task 3B — application integration: pending and not authorized.
6. Task 4A — Windows client: upstream-class data-plane blocker; bounded official-path retest required.
7. Task 4B — Android/projector connectivity: complete; performance not accepted.
8. Task 4C — iPhone connectivity: complete; performance not accepted.
9. Task 4.5 — quality FAIL/root cause open; strict AWG2/AWG3.1 A/B incomplete.
10. Task 5 — acceptance: blocked by Task 4.5.
11. Task 6 — closeout: blocked.

This note does not authorize Spain egress, remote write, stage, install,
service mutation, peer/config issuance, AWG2 operation, or global AWG3
issuance.
