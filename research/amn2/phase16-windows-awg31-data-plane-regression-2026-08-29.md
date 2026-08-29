# Phase 16 — Windows AWG3.1 data-plane regression evidence

- Recorded: `2026-08-29`
- Status: `failed-upstream-data-plane-regression-class-match`
- Primary client: AmneziaVPN `5.0.1.5`
- Client OS: Windows 11 Pro `10.0.26200` x64
- Profile binding: SHA-256
  `66afe3784b4b16148c4fbd252a8cffe3a4f7da889ce412f827afcd817cef8146`
- Record scope: sanitized local evidence and official upstream comparison only
- Live action in this record step: `false`
- Server/profile/AWG2 changed: `false`
- Protected artifacts added to Git: `false`

## Decision

The Windows AmneziaVPN `5.0.1.5` path is blocked by an AWG3.1 data-plane
regression class. The client creates and configures the tunnel, completes an
AWG handshake and exchanges keepalives, but the operator cannot pass
application traffic. Disabling the kill switch did not restore VPN traffic.
The exact defective source line inside the Windows transport implementation is
not proven, but the failure boundary is below the application and above the
already validated Spain server path.

This result closely matches the still-open official upstream report
`amnezia-client#3043`:

https://github.com/amnezia-vpn/amnezia-client/issues/3043

That issue is corroborating upstream evidence, not a maintainer-confirmed fix.
At the time of this record it has no assignee, milestone, linked pull request or
published remediation.

## Sanitized evidence custody

The two operator-exported client logs were checksum-copied to the approved
private-artifacts location outside Git. Their contents were analyzed only from
checksum-identical local originals through a strict line filter. No key, peer,
endpoint, DNS value or complete configuration was printed or committed.

- service log: `23358` bytes, SHA-256
  `495d257637a77477c4862258434dabea90d8b295c47e8851a031ec6d1ecc7982`;
- application log: `1970` bytes, SHA-256
  `84d8feaa929adb3c74f66e41ba03509cb00bd5b43ec1007aa0fed0a6c102b19b`;
- tunnel ring-log: `1064968` bytes, SHA-256
  `b9a7f11cc8f5add83695bfc03d6be4f5f9433f9f14d6a4c18c196146f1aabddd`.

The ring-log is not stored in Git. It was read with the format documented by
the official `WindowsTunnelLogger` implementation:

https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/platforms/windows/daemon/windowstunnellogger.cpp

## Primary AmneziaVPN run

The client and service logs establish the complete successful setup path:

- the application requested activation and later displayed `Connected`;
- the dynamic Windows tunnel service started;
- tunnel.dll created a Wintun adapter using driver `0.14`;
- the interface configuration and AWG3.1 UAPI parameters were applied;
- the interface became `Up`;
- IPv4 and IPv6 address setup ran;
- MTU `1280` was applied;
- the peer handshake completed.

The earlier polling watcher did not observe this short-lived dynamic state and
is superseded by the client/service/tunnel logs. Its negative adapter result is
not evidence that the adapter was never created.

The same service log also recorded Windows route-monitor errors:

- error `87`: invalid parameter;
- error `5010`: object already exists;
- an invalid empty-address route rendered as `/999999`.

Official source shows that the Windows peer update path attempts both IPv4 and
IPv6 exclusion routes even when only the IPv4 server endpoint is present. That
explains the `/999999` error class, but does not by itself prove the loss of all
transport traffic:

https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/platforms/windows/daemon/wireguardutilswindows.cpp

## Kill-switch A/B

One separately approved sequential run temporarily disabled only the client
kill switch. Android, iPhone and INCY were off; the server and profile were not
changed.

The operator again observed no Internet through the VPN. Sanitized ring-log
classification for the approximately `57` second tunnel lifetime showed:

- handshake initiation sent: `2`;
- handshake response received: `1`;
- keepalive sent: `1`;
- keepalive received: `1`;
- data-packet event-log entries: `0`;
- tunnel transport errors or panics: `0`;
- shutdown was operator-triggered at the end of the run.

The ring-log is an event stream, not a packet capture or authoritative packet
counter. Zero data-packet log entries therefore must not be read as a measured
zero-packet counter. The supported claim is narrower: handshake and keepalive
events were present, tunnel errors were absent, and the operator's application
traffic still did not work.

Therefore kill switch was not the root cause. With kill switch disabled, the
ordinary Internet path can recover outside the tunnel, which is direct fallback
and not an acceptable VPN workaround.

After disconnect, the safe local baseline was confirmed:

- dynamic VPN adapter count: `0`;
- dynamic tunnel service count: `0`;
- base AmneziaVPN service: `Running`;
- ordinary IPv4 default-route count: `1`;
- ordinary HTTPS check: HTTP `200`.

## Upstream match

Official issue `#3043` describes the same distinguishing sequence on Windows
11 with AmneziaVPN `5.0.1.5` and AWG3.1:

- handshake completes;
- the UI may report connected;
- no application transport traffic passes;
- changing MTU, DNS, split-tunneling state and server engine does not remove the
  symptom;
- the same server path works for other protocols or clients.

The official daemon source reports `connected` when it observes a peer
handshake. It does not require a successful application-data probe before
emitting that state:

https://github.com/amnezia-vpn/amnezia-client/blob/dev/client/daemon/daemon.cpp

Our independent evidence adds the same-client ring-log classification of
bidirectional handshake/keepalive without a tunnel error, concurrent with the
operator-observed application traffic failure. Together with the successful
sequential Android and iPhone connectivity tests, this rules out Spain UDP
reachability, peer identity, basic server forwarding/NAT and profile acceptance
as explanations for the Windows-only failure.

## Phase 16 gate effect

- Task 4A Windows: `failed-upstream-data-plane-regression-class-match`;
- Task 4B Android connectivity: `passed`;
- Task 4C iPhone connectivity: `passed`;
- Task 4.5 AWG2/AWG3.1 quality: `failed-and-incomplete`;
- Task 5 acceptance: `blocked`;
- Task 6 closeout: `blocked`.

No downgrade, native-client install, server mutation, DNS/MTU/port change,
profile reissue, application stage or general AWG3.1 issuance is authorized by
this record. The next Windows remediation gate is an official upstream fix or
a separately checksum-bound official build with explicit approval. AWG2 remains
`UNTOUCHED`.
