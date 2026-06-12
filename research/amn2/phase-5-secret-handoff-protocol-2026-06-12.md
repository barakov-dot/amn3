# Phase 5 P5-C004 Secret Handoff Protocol

Date: 2026-06-12

Status: completed-docs-only

Protocol doc: `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md`

## Scope

This slice creates the Phase 5 operator-only protocol for Telegram token, web secret, server config and bootstrap secret handling.

No AMN2 runtime code changed. No live VPS command, SSH command, package apply/rebuild on VPS, deploy/restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive provider action, Telegram token use, live bot send, Telegram profile mutation or secret-bearing evidence publication was performed.

## Inputs

The protocol consolidates existing AMN3 boundaries:

- Phase 4 NG secrets policy: evidence may contain only safe summaries and must not publish `.env`, raw `servers.yml`, tokens, headers, hashes, keys, PSK, `.conf`, QR, `vpn://`, cookies, full logs or secret-bearing command output.
- `VPS-REBUILD-001` selected `regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets`.
- Fresh deploy runbook already requires `.env` and `servers.yml` to be created through the operator local/private channel and not pasted into chat or GitHub.
- Phase 5 default keeps `VPS_APPLY_ENABLED=false`, loopback web/admin and no public/config/write/destructive surfaces by default.

## Result

Created `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md` with:

- secret classes: `external-token`, `generated-local-secret`, `target-server-config`, `client-config-secret`, `runtime-secret-state`, `auth-material`;
- allowed and forbidden channels;
- safe evidence summary fields;
- operator handoff ceremony;
- `.env` / `servers.yml` private-file boundary;
- stop lines;
- related named gates for Telegram identity, config delivery, write API, backup/import/reboot, Local Agent mutation and destructive rebuild.

Core policy:

```text
secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
default_publication_policy: no raw secrets in AMN3/GitHub/chat/evidence/log excerpts
default_runtime_boundary: VPS_APPLY_ENABLED=false
default_panel_boundary: WEB_HOST=127.0.0.1, SSH tunnel only
```

## Verification

```text
secret_doc_created: yes
secret_classes_defined: yes
safe_summary_fields_defined: yes
stop_lines_defined: yes
related_named_gates_defined: yes
raw_secret_values_recorded: no
```

Performed local checks:

```text
rg -n "BOT_TOKEN=|TELEGRAM_BOT_TOKEN=|WEB_SECRET=|SESSION_SECRET=|BEGIN (RSA|OPENSSH)|PrivateKey =|PresharedKey =|vpn://[A-Za-z0-9_-]{16,}" docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md
result: no matches

git diff --check
result: passed
```

## Next Recommendation

`P5-N001` cleanup operator docs after pilot. Since active critical Phase 5 protocol tasks are now closed, continue with normal documentation cleanup unless the operator explicitly opens a named live/write/config/destructive gate.
