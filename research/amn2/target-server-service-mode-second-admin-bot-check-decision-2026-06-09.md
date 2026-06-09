# Target Server Service-Mode Second Admin Bot Check Decision - 2026-06-09

Status: `phase3_second_admin_bot_readonly_check_skipped_by_operator`.

Scope: operator decision after the second Telegram admin ID was added successfully. The planned read-only Telegram bot confirmation was intentionally skipped to save time. This evidence does not claim the second admin's Telegram UI was independently verified.

## Safe Summary

```text
second_admin_id_added: yes
configured_admin_count: 2
bot_readonly_check_requested: yes
bot_readonly_check_performed: no
bot_readonly_check_status: skipped_by_operator
raw_telegram_ids_recorded: no
write_buttons_pressed: no-evidence
slash_admin_write_commands_sent: no-evidence
```

## Interpretation

The configuration gate for adding a second Telegram admin ID passed earlier, but the follow-up Telegram UI read-only check was skipped by operator choice.

This means:

- configured admin count remains recorded as `2`;
- raw Telegram IDs remain unpublished;
- there is no direct evidence in this Phase 3 record that the second admin opened `/start`, saw admin mode, or opened read-only admin sections;
- this is not treated as a blocker for service-mode loopback/tunnel operation, but should be repeated later if bot admin delegation needs proof.

## Boundaries

This decision does not unlock:

- Telegram bot approve/revoke/create/write operations;
- authenticated destructive web-panel actions;
- config delivery;
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

No Telegram admin ID, public IP, public host, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents, session cookies or full logs were copied into this evidence.
