# Phase 8 P8-S001 goal/status framing

Date: 2026-06-21.

Status: `completed-phase8-goal-status-framing-no-live-action`.

Scope: local-only Phase 8 launch readiness framing. No live VPS/SSH command,
package upload/apply, service restart, public exposure, config delivery,
Telegram action, write/install execution, backup restore/import/reboot,
provider mutation, production peer/user mutation or secret-bearing output was
performed.

## Source Of Truth

AMN3/evidence workspace:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB
branch=master
head_before_p8_s002=0d93807 Record Phase 8 launch readiness gates
status_before_p8_s002=clean
```

AMN2 clean current-fixes worktree:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current
branch=codex/phase7-current-fixes
head=187949b Persist Android-compatible AWG defaults
status=clean-local
```

Latest VPS-applied/package-smoked head after P8-C002:

```text
187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
```

Current disposable VPS:

```text
89.185.80.166
```

## Current Launch Posture

Phase 7 entry into Phase 8 is valid:

```text
phase8_entry_status=phase8-prep-ready
phase8_launch_gate_status=blocked-until-fresh-from-zero-vps-rehearsal
```

The live dataplane question is closed by `P7-C011f2`: `awg0` listens on UDP
`30001`, live server public key fingerprint is `0bdc326c396a`, old matched
peer `a6a551084fad` had a fresh handshake and growing transfer counters, and
the operator observed Android connecting instantly.

The launch blocker is narrower: the working old local files from `C:\temp` are
diagnostic proof only. They are not release delivery artifacts and must not be
used as Phase 8 acceptance.

## Distance To Launch

Current distance-to-launch estimate after P8-C002:

```text
private_operator_rc_distance_to_launch=92_percent
```

Already strong:

- live VPN dataplane works;
- Android can connect to the live server with an old matched config;
- Telegram-first user channel policy is accepted;
- operator web/admin can remain private by VPS IP plus loopback/SSH tunnel;
- public exposure is closed by default;
- previous package/apply, loopback web/API, Telegram getMe/non-polling smoke
  and backup create+verify evidence exists.

Still blocking launch after P8-C003 readiness confirmation:

- fresh-from-zero VPS rehearsal for the final Phase 8 line is not complete;
- `P8-C003` proposal is prepared and readiness is `go-with-limitation`, but the
  destructive gate is not opened;
- the Android device for `P8-C003` is an Android projector with browser/app
  traffic, not an Android phone, and this limitation must be recorded if used;
- final launch readiness freeze has not yet been recorded.

## Phase 8 Gate Map

### P8-C001 fresh per-device Android config acceptance gate

ЦЕЛЬ:
create/add one fresh Android peer/config through AMN2/dataplane path, perform
private operator handoff only, then verify Android AmneziaWG import, connect
and traffic.

Что доказывает:
fresh per-device `.conf` delivery can become the primary mobile release path.

Что не доказывает:
iOS, QR, full `vpn://`, Telegram live config send, public exposure,
fresh-from-zero install, restore/import or production scale.

Влияние на близость запуска:
passed on 2026-06-21 with compatible AWG parameters for fresh peer
`594ba96e4f90`; moved the launch estimate to roughly `85_percent`.

Следующий gate если passed:
`P8-C002 package/current-head smoke and compatible AWG defaults persistence gate`.

Stop-line если failed:
do not reuse old diagnostic configs as release proof; classify the blocker as
peer creation, private handoff, import, connect, traffic, handshake/counters or
peer mismatch.

### P8-C002 package/current-head smoke gate

ЦЕЛЬ:
if needed, package/apply current AMN2 head to the disposable VPS and smoke
loopback web/API, Telegram getMe/non-polling surface, backup create+verify and
closed external probes.

Что доказывает:
current head does not regress the private/operator RC runtime surfaces.

Что не доказывает:
fresh-from-zero reproducibility.

Влияние на близость запуска:
passed on 2026-06-21 for AMN2 `187949b`; launch estimate moved to roughly
`92_percent`.

Следующий gate если passed:
`P8-C003 fresh-from-zero VPS rehearsal gate`.

Stop-line если failed:
do not continue to destructive rehearsal until package/apply or smoke blocker
is fixed under a new exact gate.

### P8-S002 fresh-from-zero preflight ledger

ЦЕЛЬ:
record the criticality/size task matrix, package inputs, readiness checklist,
pass criteria and stop-lines before opening the destructive rehearsal gate.

Что доказывает:
the project has a clear non-live contract for what `P8-C003` is allowed to do
and how it will pass or fail.

Что не доказывает:
fresh-from-zero installation, live runtime behavior, Android acceptance on a
fresh VPS or launch readiness.

Влияние на близость запуска:
passed on 2026-06-21 as docs-only preparation; launch estimate remains roughly
`92_percent` because the destructive rehearsal has not run.

Следующий gate если passed:
operator review or explicit opening of `P8-C003 fresh-from-zero VPS rehearsal
gate`.

Stop-line если failed:
do not open `P8-C003`; fix the missing preflight item or unclear stop-line
first.

### P8-C003 readiness confirmation

ЦЕЛЬ:
confirm private input strategy and Android test-device availability before the
destructive rehearsal approval.

Что доказывает:
the operator has a private Telegram token source, will use new private web/admin
credentials, will generate fresh env secrets plus private inputs, has a private
handoff path outside the workspace, and has an Android projector capable of
browser/app traffic.

Что не доказывает:
fresh-from-zero installation, live runtime behavior, Android phone acceptance
inside `P8-C003` or final launch readiness.

Влияние на близость запуска:
completed on 2026-06-21 as `go-with-limitation`; launch estimate remains
roughly `92_percent` until `P8-C003` actually runs.

Следующий gate если passed:
explicit `P8-C003 destructive gate approval`.

Stop-line если failed:
do not approve destructive execution; resolve private input or Android
availability blocker first.

### P8-C003 fresh-from-zero VPS rehearsal gate

ЦЕЛЬ:
perform destructive clean/fresh install on the disposable VPS, apply package,
initialize safe env/DB, run loopback smoke, complete one fresh Android
per-device config acceptance, backup create+verify and external closed probes.

Что доказывает:
reproducible fresh launch path for private/operator RC.

Что не доказывает:
public launch, public web/admin, iOS primary support or restore/import DR.

Влияние на близость запуска:
if passed, allows final launch-readiness freeze.

Следующий gate если passed:
`P8-SFINAL launch readiness freeze`.

Stop-line если failed:
stop at first failed prerequisite and do not compensate with ad hoc manual
runtime edits unless a new exact gate is opened.

### P8-SFINAL launch readiness freeze

ЦЕЛЬ:
decide one final status: `private/operator RC launch-ready`,
`launch-ready-with-explicit-limitations` or `blocked-with-exact-remaining-blockers`.

Что доказывает:
the evidence is internally consistent enough to make the launch decision.

Что не доказывает:
any missing live gate that did not pass.

Влияние на близость запуска:
turns Phase 8 evidence into the final private/operator RC verdict.

Следующий gate если passed:
private/operator RC launch handoff.

Stop-line если failed:
publish only the short exact blocker list and required gates.

## Default Stop Lines

Without a fresh exact named Phase 8 gate, do not perform:

- destructive VPS/provider action;
- public exposure, Cloudflare, ngrok, reverse proxy, TLS, firewall or listener
  changes;
- `.conf`, QR, `vpn://`, private key, PSK or token output;
- Telegram live send/profile/media mutation;
- write/install execution;
- backup restore/import/reboot;
- production peer/user mutation;
- upstream/GPL code copy.

## Result

`P8-S001` is closed as local-only framing. `P8-C001` fresh per-device Android
acceptance, `P8-C002` package/current-head smoke, `P8-S002` fresh-from-zero
preflight ledger and `P8-C003` readiness confirmation have also passed on
2026-06-21. `P8-C003` is proposed but not opened. Readiness is
`go-with-limitation` because the available Android test device is an Android
projector rather than a phone. The recommended next exact gate is still:

```text
P8-C003 fresh-from-zero VPS rehearsal gate
```

`P8-C003` is destructive and must not run without a fresh exact named gate.
