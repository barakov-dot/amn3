# Target Server Test Peers Batch Evidence 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать safe evidence Phase 3A.2 batch gate для трех дополнительных test peers на новом target VPS. Эти peers предназначены только для operator-approved test zone пользователей и оставлены включенными для ручного клиентского тестирования.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
previous phone live test peer evidence: research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md
peer_count_before_batch: 1
batch_scope: three additional test-zone peers
runtime_mode: manual
service_mode: not-enabled
public_api_3040: closed
direct_public_web_3030: closed
```

## Safety Boundary

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

The three generated client profiles and QR files are secret-bearing manual test artifacts. They were downloaded by the operator through a private channel and were not published to chat or GitHub. File labels follow the operator-approved sequence:

```text
Neobyatnaya-AMNZ-2
Neobyatnaya-AMNZ-3
Neobyatnaya-AMNZ-4
```

This gate does not authorize public/self-service config delivery. It also does not authorize production peer/user writes beyond the four currently approved test peers.

## Gate Result

```text
test_peers_batch_gate: passed
source_overlay_commit: f7f6131
peer_scope: three additional operator-approved test-zone peers
configs_created_hidden: 3
qrs_created_hidden: 3
configs_downloaded_by_operator: yes
test_peers_left_enabled: yes
live_peer_count_final: 4
tcp_3030_final: absent
tcp_3040_final: absent
VPS_APPLY_ENABLED_final: false
safe_batch_dir: /root/amn2-test-peers-batch-20260609T103147Z
```

## Current Runtime Snapshot

```text
container: amnezia-awg2
container_status: running
peer_count: 4
test_peer_status: enabled
tcp_3030: absent
tcp_3040: absent
service_mode: not-enabled
reverse_proxy_public_https: not-enabled
public_api_3040: closed
direct_public_web_3030: closed
```

## Notes

The first phone/desktop test peer has confirmed handshake/RX/TX evidence in `research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md`. This batch evidence confirms creation/download and final enabled peer count for the three additional test peers; per-client handshake for those users remains a manual follow-up if needed.

## Still Closed

- persistent service-mode `systemd` deployment;
- reverse proxy/public HTTPS cutover;
- broad `VPS_APPLY_ENABLED=true`;
- production peer/user mutation beyond the four approved test peers;
- public API `3040`;
- direct public web/admin `3030`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Recommended next decision: keep manual runtime with four test peers enabled for operator/test-zone validation, or open a separate service-mode gate for web/bot `systemd` plus HTTPS reverse proxy. Service-mode remains a separate explicit gate because it changes process lifecycle and public access boundaries.
