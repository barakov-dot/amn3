# Phase 7 P7-C011f2 mobile dataplane closeout

Date: 2026-06-21.

Status: `completed-mobile-dataplane-observed-old-matched-config-diagnostic-only`.

Target: disposable VPS `89.185.80.166`.

Scope: read-only live AWG handshake observation plus operator real-device
Android observation. No `.conf`, private key, PSK, token, QR, `vpn://`, config
payload or secret-bearing screenshot was printed into evidence. No
container/config mutation, Telegram send, restore/import/reboot, provider
mutation, write execution or public web/API exposure was performed.

## Context

Earlier mobile acceptance attempts failed because generated/test payloads were
not a reliable release path:

- QR and full `vpn://` were not reliable as mobile release-primary artifacts.
- iOS DefaultVPN remained unreliable/experimental.
- One helper-generated Android test payload used a dummy TEST-NET endpoint and
is invalid for connectivity evidence.
- Private correspondence diagnostics later showed that the current live
  `amnezia-awg2` container has two live peers, and only the older local files
  from `C:\temp` matched them.

Matched diagnostic configs:

```text
Neobyatnaya-AMNZ.conf    -> live peer fp a6a551084fad
Neobyatnaya-AMNZ-2.conf  -> live peer fp 2ed2b69a2f79
```

These files are treated as diagnostic proof only, not as a release delivery
path.

## P7-C011f2 Evidence

Corrected parser gate:

```text
P7-C011f2 live AWG handshake observation gate
```

The first `P7-C011f` helper used `wg dump` parsing and produced invalid field
mapping (`live_listen_port=3`, `transfer_tx_bytes=off`), so that output is not
used as dataplane evidence. `P7-C011f2` used separate `wg show` fields.

Safe baseline/after-attempt values from the operator-provided transcript:

```text
live_interface=awg0
live_listen_port=30001
live_server_public_key_fp=0bdc326c396a
live_peer_count=2

before:
peer_fp=a6a551084fad latest_handshake_age_s=8
transfer_rx_bytes=17706856
transfer_tx_bytes=35751155
endpoint_observed=yes

peer_fp=2ed2b69a2f79 latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no

after_attempt:
peer_fp=a6a551084fad latest_handshake_age_s=32
transfer_rx_bytes=17792776
transfer_tx_bytes=35860605
endpoint_observed=yes

peer_fp=2ed2b69a2f79 latest_handshake_age_s=never
transfer_rx_bytes=0
transfer_tx_bytes=0
endpoint_observed=no

remote_before_exit_code=0
remote_after_exit_code=0
remote_cleanup_exit_code=0
```

Observed deltas for `a6a551084fad`:

```text
rx_delta=85920
tx_delta=109450
```

The baseline was not a clean "all clients idle" snapshot because peer
`a6a551084fad` already had a very fresh handshake before the after-attempt
step. This means the gate proves the dataplane/peer is active and carrying
traffic, but it should not be used to uniquely attribute every byte to one
manual Android attempt.

Operator observation after the corrected gate:

```text
Android connected instantly.
```

## Result

The live VPN dataplane is not globally broken:

- `amnezia-awg2`/`awg0` listens on UDP `30001`;
- server public key fingerprint matches the private matched configs;
- live peer `a6a551084fad` has fresh handshake and increasing transfer
  counters;
- the operator observed Android connecting instantly with the matched old
  config path.

## Release Interpretation

This closes the "does the current dataplane work at all?" question.

It does not close release config delivery:

- the working file is an older matched config, not a reproducible fresh AMN2
  per-device delivery artifact;
- using the same peer config on multiple devices remains unsafe because one
  WireGuard/AWG peer identity can move between endpoints;
- Phase 8 should not rely on shared historical configs.

Phase 8 entry status:

```text
phase8_entry_status=phase8-prep-ready
phase8_launch_gate_status=blocked-until-fresh-per-device-android-config-acceptance
```

Recommended first Phase 8 exact gate:

```text
P8-C001 fresh per-device Android config acceptance gate
```

Acceptable variants:

- create/add one new Android peer/config through a named AMN2/dataplane gate,
  then private operator handoff and Android acceptance; or
- perform a fresh-from-zero VPS install/package smoke, then generate and accept
  one fresh per-device Android config.

Fresh-from-zero/destructive VPS work remains a separate exact destructive gate
with final stop-line phrase, even though the current VPS is operator-declared
disposable.
