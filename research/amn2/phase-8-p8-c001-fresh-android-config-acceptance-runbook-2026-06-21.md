# Phase 8 P8-C001 fresh Android config acceptance runbook

Date: 2026-06-21.

Status: `prepared-exact-gate-runbook-no-payload-output`.

Scope: exact runbook for one fresh per-device Android AmneziaWG acceptance
attempt on disposable VPS `89.185.80.166`. This document does not itself run
live VPS/SSH commands, create or deliver a config, mutate peers, send Telegram
messages, expose public listeners, restore/import/reboot, or print any
secret-bearing payload.

## Gate Phrase

The selected gate is:

```text
P8-C001 fresh per-device Android config acceptance gate
```

Allowed scope:

- one fresh Android peer/config only;
- AMN2/dataplane path, not historical `C:\temp` configs;
- private operator handoff only;
- Android AmneziaWG `.conf` import/connect/traffic acceptance;
- safe evidence only, with fingerprints/counts/statuses instead of payload.

Not allowed in this gate:

- public web/API exposure;
- Cloudflare, ngrok, reverse proxy, TLS, firewall or listener changes;
- Telegram live config send, polling, profile/media mutation or identity
  changes;
- QR or full `vpn://` as release-primary;
- `.conf`, QR, `vpn://`, private key, PSK, token or secret screenshot output;
- backup restore/import/reboot;
- destructive clean install or provider mutation;
- more than one fresh Android peer/config.

## Preconditions

Verify before any live write:

```text
AMN2 worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current
AMN2 branch: codex/phase7-current-fixes
AMN2 head: 4d22ff2 Gate Phase 8 on Android acceptance
latest VPS-applied/package-smoked head before this gate: 6d5cf3e
target VPS: 89.185.80.166
target client: Android AmneziaWG
delivery artifact: .conf only
handoff channel: private operator handoff only
```

Required local/source checks:

```text
git status --short --branch
git log -1 --oneline --decorate
python -m py_compile app\services\access.py app\server\peer_apply.py app\vpn\config_versions.py app\vpn\config_templates.py app\cli.py
```

Required live safety checks before peer write:

```text
source_overlay_observed=<safe short commit/hash only>
web_admin_public_exposure=closed
api_public_exposure=closed
VPS_APPLY_ENABLED=false-before-write-window
existing_live_peer_count=<count only>
server_public_key_fp=<fingerprint only>
listen_port=<port only>
```

Do not paste `.env`, `servers.yml`, full logs, full `wg dump`, config text,
private keys, PSK or raw token material into evidence.

## Execution Shape

The expected AMN2 path is the existing access/config/peer path:

- `AccessService.approve_order(...)` generates a fresh keypair and PSK;
- AMN2 allocates a fresh per-device VPN IP;
- AMN2 renders `amneziawg_v2` `.conf`;
- `ServerConfigPeerApplier` applies the peer to the configured runtime;
- Docker runtime writes the persistent config and restarts the AmneziaWG
  container when the target server is Docker-backed;
- handoff sends only the actual `.conf` artifact privately to the operator.

Evidence must record only safe metadata:

```text
fresh_device_label=p8-c001-android
fresh_device_id=<id or redacted local reference>
fresh_peer_public_key_fp=<fingerprint only>
fresh_vpn_ip=<ip-only if acceptable for evidence; otherwise last-octet-redacted>
config_version=amneziawg_v2
handoff=private-operator-only
payload_output=no
```

If the live path cannot create a fresh peer through `AccessService`, stop and
classify the blocker. Do not manually craft a release config as a workaround
unless a new exact gate names the alternate path.

## Android Acceptance

Operator-side Android checks:

```text
client=Android AmneziaWG
artifact=.conf
import_result=passed|failed
connect_result=passed|failed
first_connect_time=instant|slow|failed
traffic_result=passed|failed
```

Server-side safe observation after the operator attempts connect:

```text
interface=awg0
listen_port=30001
server_public_key_fp=<fingerprint>
fresh_peer_public_key_fp=<fingerprint>
latest_handshake_age_s=<number-or-never>
transfer_rx_delta=<number>
transfer_tx_delta=<number>
endpoint_observed=yes|no
```

The acceptance is passed only if all are true:

- Android imports the fresh `.conf`;
- Android tunnel connects;
- Android traffic works through the tunnel;
- the fresh peer, not an old matched peer, shows a fresh handshake or clear
  transfer-counter growth consistent with the attempt;
- no payload/secret is printed to chat/evidence.

## Failure Classification

If the gate fails, record exactly one primary failure class:

```text
peer_creation_failed
remote_apply_failed
private_handoff_failed
android_import_failed
android_connect_failed
android_traffic_failed
server_handshake_missing
peer_mismatch_old_config_used
secret_boundary_violation
```

Stop-line:

```text
Do not promote Android release-primary and do not proceed to P8-C002/P8-C003
until the exact blocker is closed by a new named gate or a corrected repeat of
P8-C001.
```

## Result Contract

Pass result:

```text
p8_c001_status=passed-fresh-per-device-android-config-accepted
phase8_launch_gate_status=android-fresh-config-acceptance-closed
recommended_next_gate=P8-C002 package/current-head smoke gate
```

Fail result:

```text
p8_c001_status=failed
phase8_launch_gate_status=blocked-until-fresh-per-device-android-config-acceptance
primary_failure_class=<one class from Failure Classification>
recommended_next_gate=<exact blocker-specific gate>
```
