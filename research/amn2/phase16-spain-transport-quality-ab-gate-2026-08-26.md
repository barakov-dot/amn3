# Phase 16 Spain transport-quality A/B gate

- Recorded: `2026-08-26`
- Status: `mandatory-pending-after-first-awg31-pilot-config`
- Priority: after Task 4 and before Task 5 acceptance or Task 6 closeout
- Scope: one operator client, Spain AWG2 and the first Spain AWG3.1 pilot
- Package 013 changed by this note: `false`
- Live action authorized by this note: `false`

## Operator observation

The operator reported that the current Spain AWG2 configuration is unstable
and slow on this computer, while the server does not show the same speed
problem on other protocols. This is an observed client-path symptom, not yet a
confirmed server, protocol, configuration, MTU, DNS, firewall, Docker, or
network root cause.

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
2. Task 1 — AWG3.1 code and immutable package 013: complete.
3. Task 2 — checksum-bound Spain read-only preflight: complete/PASS.
4. Task 3 — controlled server-only stage: current exact gate.
5. Task 4 — exactly one operator AWG3.1 pilot config: pending.
6. Task 4.5 — mandatory AWG2 versus AWG3.1 transport-quality A/B gate: pending.
7. Task 5 — real-client acceptance after Task 4.5: pending.
8. Task 6 — concise closeout after Task 4.5 and Task 5: pending.

This note does not authorize Spain egress, remote write, stage, install,
service mutation, peer/config issuance, AWG2 operation, or global AWG3
issuance.
