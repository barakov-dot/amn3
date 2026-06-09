# Target Server Service-Mode Admin Telegram ID Add Evidence - 2026-06-09

Status: `phase3_service_mode_second_admin_telegram_id_added`.

Scope: small operator-approved service-mode configuration change to add one additional Telegram admin ID to `ADMIN_TELEGRAM_IDS` in `/opt/amn2/.env`. This gate did not publish raw Telegram IDs, did not enable `VPS_APPLY_ENABLED`, did not perform peer/user production writes, did not request config delivery, did not open public API `3040`, did not expose direct public web/admin `3030`, and did not change reverse proxy state.

## Safe Summary

```text
admin_add_status: updated
admin_telegram_ids_count_after: 2
VPS_APPLY_ENABLED_file_false: yes
web_login_probe_1_http: 000curl-failed
web_login_probe_2_http: 000curl-failed
web_login_probe_3_http: 000curl-failed
web_login_probe_4_http: 000curl-failed
web_login_probe_5_http: 200
amneziya-bot_active: active
amneziya-web_active: active
tcp_3030_loopback: yes
tcp_3040_absent: yes
VPS_APPLY_ENABLED_file_false_final: yes
```

## Interpretation

The second Telegram admin ID was added successfully. The resulting configured admin count is `2`; raw Telegram IDs were intentionally not copied into this evidence.

After restarting `amneziya-bot` and `amneziya-web`, the web service had a short readiness window: the first four loopback `/login` probes failed to connect, and the fifth probe returned HTTP `200`. The final state is healthy:

- `amneziya-bot` is active;
- `amneziya-web` is active;
- TCP `3030` is loopback-only;
- TCP `3040` remains absent;
- explicit `.env` `VPS_APPLY_ENABLED=false` is present.

## Boundaries

This evidence does not unlock:

- HTTPS reverse proxy/public cutover;
- public API `3040`;
- direct public web/admin `3030`;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- production peer/user mutation beyond the remaining approved test peers.

## Secret Handling

No Telegram admin ID, public IP, public host, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
