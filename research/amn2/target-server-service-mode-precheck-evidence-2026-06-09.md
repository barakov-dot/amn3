# Target Server Service-Mode Read-Only Precheck Evidence - 2026-06-09

Status: `phase3_service_mode_precheck_passed_read_only`.

Scope: read-only service-mode/prod-readiness precheck after the phone live test peer gate and the additional test-peers batch gate. No `systemd` unit was installed, enabled or started. No HTTPS reverse proxy route was created or changed. No public API, config delivery, Local Agent mutation, backup/import/reboot or additional peer mutation was unlocked.

## Safe Summary

```text
phase3_service_mode_precheck: passed-read-only
source_overlay_commit: f7f6131
runtime_type: docker
container_running: true
live_peer_count: 4
tcp_3030_before: absent
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
web_unit_template_present: yes
web_unit_template_loopback_3030: yes
bot_unit_template_present: yes
bot_unit_template_python_entry: yes
telegram_bot_token_present: yes
web_admin_password_hash_present: yes
web_admin_session_secret_present: yes
amneziya-web_unit_file_present: no
amneziya-web_enabled: not-found
amneziya-web_active: inactive
amneziya-bot_unit_file_present: no
amneziya-bot_enabled: not-found
amneziya-bot_active: inactive
service_mode: not-enabled
reverse_proxy_public_https_cutover: not-enabled
```

## Named Test Peer Activity Sample

The precheck also sampled the four operator-approved test peers by friendly number without printing peer public keys, VPN IPs, client configs or QR data.

```text
Neobyatnaya-AMNZ-1: not-yet
Neobyatnaya-AMNZ-2: not-yet
Neobyatnaya-AMNZ-3: not-yet
Neobyatnaya-AMNZ-4: not-yet
```

Interpretation: the read-only sample did not observe an active/current handshake with nonzero traffic for the four named test peers at that moment. The earlier first-phone peer connectivity proof remains recorded separately as `handshake_seen=yes`, `rx_nonzero=yes`, `tx_nonzero=yes` in `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`.

## Decision Point

The service-mode precheck is clean enough to make the explicit Phase 3 decision:

- remain in manual runtime mode with the four approved test peers enabled for live testing; or
- open a separate service-mode gate for `amneziya-web` and `amneziya-bot` `systemd` units plus a controlled HTTPS reverse proxy path.

If the service-mode gate is approved later, the next gate must still keep these boundaries:

- web/admin binds to loopback behind the reverse proxy;
- direct public `3030` remains closed;
- public API `3040` remains closed;
- `VPS_APPLY_ENABLED=false` outside narrow approved live peer gates;
- no public/self-service config delivery;
- no production peer/user mutation beyond explicitly approved test peers;
- no Local Agent write/config mutations;
- no backup/import/reboot routes.

## Secret Handling

No `.env`, `servers.yml`, raw tokens, authorization headers, password/session hashes, keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, backup contents or full logs were copied into this evidence.
