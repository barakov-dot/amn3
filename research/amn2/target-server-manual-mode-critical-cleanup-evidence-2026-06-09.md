# Target Server Manual Mode Critical Cleanup Evidence - 2026-06-09

Status: `phase3_manual_mode_critical_cleanup_passed`.

Scope: critical manual-runtime hardening after four operator-approved test peers were created and downloaded through private channels. This cleanup did not revoke peers, did not change the live AWG2 interface, did not enable service-mode, did not install `systemd` units, did not create a reverse proxy route, and did not open public API or direct public web/admin access.

## Read-Only Baseline Before Cleanup

```text
critical_manual_A_readonly: done
source_overlay_commit: f7f6131
live_peer_count: 4
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: not-yet
Neobyatnaya-AMNZ-3: not-yet
Neobyatnaya-AMNZ-4: not-yet
first_gate_dir_present: yes
first_gate_dir_delivery_artifact_count: 18
first_gate_dir_key_file_count: 3
batch_gate_dir_present: yes
batch_gate_dir_delivery_artifact_count: 9
batch_gate_dir_key_file_count: 9
root_delivery_archives_count: 1
```

The pre-cleanup delivery artifact count was an inventory signal only. Some patterns overlapped, so the cleanup step removed unique files rather than the summed inventory count.

## Cleanup Action

Only secret-bearing delivery artifacts were removed from the phone/test peer gate directories and root delivery archive location:

- client `.conf` files;
- QR/PNG files;
- delivery `.tar.gz` archives.

Monitoring key files were intentionally left in place so the operator can continue checking the four peers by friendly number without printing public keys or client secrets.

```text
cleanup_targets_count: 19
cleanup_apply: done
remaining_delivery_artifacts: 0
remaining_key_files: 12
```

## Post-Cleanup Control

```text
critical_manual_A_post_cleanup_control: done
live_peer_count: 4
tcp_3030: absent
tcp_3040: absent
VPS_APPLY_ENABLED_process: false
remaining_delivery_artifacts: 0
remaining_key_files: 12
```

## Result

Critical manual-mode items completed:

- four approved test peers remain live for field testing;
- no temporary client config, QR/PNG or delivery archive remains in the checked gate locations;
- key files needed for safe numbered monitoring remain available;
- public/direct `3030` and public API `3040` remain closed;
- `VPS_APPLY_ENABLED=false` is preserved;
- service-mode remains not enabled.

Remaining manual-mode follow-up:

- wait for tester activity and resample `Neobyatnaya-AMNZ-1..4` by number;
- if any tester is done or compromised, run a separate revoke gate by number;
- if service-mode is desired, open a separate explicit service-mode gate.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, backup contents or full logs were copied into this evidence.
