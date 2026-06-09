# Target Server Phone Live Test Peer Evidence 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать safe evidence Phase 3A.1 phone/desktop live test peer gate на новом target VPS после bootstrap, AWG2 runtime smoke, disposable live peer gate и manual web/bot readiness. Gate оставляет ровно один operator-approved test peer включенным для живого клиентского тестирования.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
previous runtime evidence: research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
previous live peer evidence: research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
previous manual web/bot evidence: research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
phone_live_test_peer_gate: explicitly approved by operator
runtime_mode: manual
service_mode: not-enabled
public_api_3040: closed
direct_public_web_3030: closed
```

## Safety Boundary

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

The phone/desktop client profile was created as a secret-bearing manual test artifact and was not published to chat or GitHub. The profile name/file label used by the operator was `Neobyatnaya-AMNZ`.

This gate does not authorize public/self-service config delivery. It also does not authorize production user/peer writes beyond the single operator-approved test peer.

## Gate Result

```text
phone_live_test_peer_gate: passed
source_overlay_commit: f7f6131
peer_scope: single operator phone/desktop test peer
initial_apply_attempt: failed before remote mutation due to invalid local test VPN IP input
partial_apply_after_initial_failure: no
peer_in_persistent_config_after_initial_failure: no
peer_in_live_interface_after_initial_failure: no
live_peer_count_after_initial_failure: 0
free_vpn_ip_selection: regenerated locally without publishing value
apply_dry_run_repeat: passed
revoke_dry_run_repeat: passed
apply_live: passed
client_config_awg_params: regenerated from live server AWG2 config
client_config_i_fields: removed because live server config does not contain I1-I5
handshake_seen: yes
rx_nonzero: yes
tx_nonzero: yes
phone_connectivity: passed
test_peer_left_enabled: yes
live_peer_count_final: 1
tcp_3030_final: absent
tcp_3040_final: absent
VPS_APPLY_ENABLED_final: false
safe_evidence_dir: /root/amn2-phone-test-peer-20260609T063916Z
```

## Final Runtime Snapshot

```text
container: amnezia-awg2
container_status: running
peer_count: 1
test_peer_status: enabled
tcp_3030: absent
tcp_3040: absent
service_mode: not-enabled
reverse_proxy_public_https: not-enabled
public_api_3040: closed
direct_public_web_3030: closed
```

## Still Closed

- persistent service-mode `systemd` deployment;
- reverse proxy/public HTTPS cutover;
- broad `VPS_APPLY_ENABLED=true`;
- production peer/user mutation beyond the approved single test peer;
- public API `3040`;
- direct public web/admin `3030`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Recommended next decision: either keep manual runtime with the single test peer enabled for operator testing, or open a separate service-mode gate for web/bot `systemd` plus HTTPS reverse proxy. Service-mode remains a separate explicit gate because it changes process lifecycle and public access boundaries.
