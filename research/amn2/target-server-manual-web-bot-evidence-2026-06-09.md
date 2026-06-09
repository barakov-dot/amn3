# Target Server Manual Web/Bot Gate Evidence 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать safe evidence для manual web/admin и Telegram bot readiness на новом целевом VPS после bootstrap, AWG2 runtime smoke и live single disposable peer gate. Gate не включает service-mode, public exposure, reverse proxy, production peer mutation или расширение API/write surfaces.

## Baseline

```text
current AMN2 source overlay/package: f7f6131 Update integration status for c92 manual prelaunch
previous runtime evidence: research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
previous live peer evidence: research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
runtime_mode: manual/diagnostic
systemd_web: not-used
systemd_bot: not-used
public_api_3040: closed
direct_public_web_3030: closed
production_peer_mutation: not-used
```

## Safety Boundary

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs are recorded here.

The Telegram bot token, web admin password hash and web admin session secret were set directly on the VPS through a secret-safe operator path. This evidence records only presence/validity markers, never values.

## Secret/Config Presence Checks

```text
source_overlay_commit: f7f6131
telegram_bot_token: present
web_admin_password_hash: present
web_admin_session_secret: present_valid
```

## Bot Network Check

```text
bot_check_network: passed
telegram_api: ok
bot_identity: @NeobyatnayaAMNZ_bot
proxy: disabled
```

## Manual Web Loopback Check

```text
manual_web_check: passed
run_id: 20260609T054709Z
source_overlay_commit: f7f6131
runtime_mode: manual
systemd_web: not-found
systemd_bot: not-found
old_manual_web_cleanup: not-needed
diagnostic_web_process: started_hidden_pid
startup_tick: 4
web_login_http: 200
web_listener: 127.0.0.1:3030
public_3030: no
api_3040_listener: absent
web_listener_after_cleanup: stopped
safe_evidence_dir: /opt/amn2/vps-smoke/manual-web-check-20260609T054709Z
```

## Final Runtime Snapshot

```text
source_overlay_commit: f7f6131
tcp_3030: absent
tcp_3040: absent
container: amnezia-awg2
container_status: running
peer_count: 0
telegram_bot_token: present
web_admin_password_hash: present
web_admin_session_secret: present
VPS_APPLY_ENABLED: false/not-set outside narrow gates
```

## Result

```text
target_server_manual_web_bot_gate: passed
web_admin_manual_loopback: passed
bot_network_readiness: passed
service_mode: not-enabled
direct_public_web_3030: closed
public_api_3040: closed
peer_count_final: 0
```

## Still Closed

- persistent service-mode `systemd` deployment;
- reverse proxy/public HTTPS cutover;
- production peer mutation;
- broad `VPS_APPLY_ENABLED=true`;
- public API `3040`;
- direct public web/admin `3030`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- publication of `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, `.conf`, QR, `vpn://`, backup contents or full logs.

## Next Gate

Recommended next gate: choose between staying in manual runtime mode for product/API work, or opening a separate service-mode gate for `systemd` plus HTTPS reverse proxy. Service-mode should remain explicit because it changes process lifecycle and public access boundaries.
