# Phase 16 — Windows AWG3.1 active route and interface-counter diagnostic

- Recorded: `2026-08-29`
- Status: `route-install-hypothesis-rejected-data-plane-session-failure`
- Client: Windows 11 Pro `10.0.26200` x64, AmneziaVPN `5.0.1.5`
- Profile SHA-256:
  `66afe3784b4b16148c4fbd252a8cffe3a4f7da889ce412f827afcd817cef8146`
- Live run: one sequential watcher, hard wall-clock maximum `60` seconds
- Packet capture, file write, SSH, server/config/AWG2 change: `false`

## Preflight and scope

Before arming the watcher, a hash-only readback matched the approved profile
SHA-256 and the active Amnezia/Wintun tunnel count was zero. The operator kept
iPhone, Android and INCY off, enabled only the checksum-bound Spain AWG3.1
profile after `WATCHER_ARMED`, and retained the normal kill-switch setting.

The watcher emitted only normalized state. It did not print interface
addresses, route destinations, peer endpoint, DNS content, keys or complete
configuration. It performed exactly one HTTPS request and wrote no file.

## Active tunnel result

The watcher detected the tunnel and completed in `45.586` seconds:

- adapter detected: `true`;
- adapter status: `Up`;
- IPv4 MTU: `1280`;
- IPv6 MTU: `1280`;
- IPv4 address count: `1`;
- IPv6 address count: `1`;
- IPv4 route count: `6`;
- IPv6 route count: `2`;
- IPv4 full-tunnel class: `default_route`;
- IPv6 default-route count: `1`;
- IPv4 host-route count: `3`;
- IPv4 interface metric: `5`;
- observed IPv4 route-metric range: `0..256`.

During the single bounded HTTPS interval, the adapter counters changed by:

- received: `+9323` bytes;
- sent: `+11367` bytes.

The HTTPS request did not complete within its bounded timeout:

- success: `false`;
- HTTP status: absent;
- normalized exception class: `TaskCanceledException`.

## Interpretation boundary

The hypothesis that Windows failed because the client did not install an
active full-tunnel route is rejected for this run. The adapter was Up, both
address families were configured, and both IPv4 and IPv6 default routes were
present. The earlier `/999999` route-monitor error therefore did not prevent
creation of the full-tunnel default routes observed here; this does not prove
that every exclusion-route operation was semantically correct.

The bidirectional counter deltas establish interface activity during the HTTPS
window. They are not packet capture, do not attribute every byte to the HTTPS
flow, and do not prove successful TLS payload exchange. `TaskCanceledException`
is a timeout classification, not a root cause.

The supported failure boundary is now after adapter/address/MTU/route setup and
within or adjacent to the Windows tunnel data-plane/session path. The exact
upstream source defect remains unproven. No DNS, MTU, port, firewall, server or
profile correction follows from this evidence.

## Post-run baseline

After operator disconnect, local readback showed:

- active tunnel adapters: `0`;
- dynamic tunnel services: `0`;
- base AmneziaVPN service: present and `Running`;
- ordinary IPv4 default-route count: `1`.

No post-run external HTTPS request was performed.

## Gate effect

- Task 4A Windows remains failed/blocked, with route absence excluded.
- Task 4.5 remains quality-failed and strict A/B incomplete.
- Task 3B, Task 5 and Task 6 remain blocked.
- General AWG3 issuance remains disabled.
- AWG2 remains untouched.

This local record does not authorize another live run, download, install,
profile/server mutation, application stage or issuance.
