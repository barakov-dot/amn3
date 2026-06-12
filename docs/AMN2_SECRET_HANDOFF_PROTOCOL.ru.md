# AMN2 Secret Handoff Protocol

Дата: 2026-06-12.

Статус: `P5-C004`, Phase 5 operator-only pilot.

Назначение: единый операторский протокол передачи и создания секретов для AMN2 без публикации raw secret material в AMN3, GitHub, чатах, evidence-файлах или логах.

Этот документ не разрешает live VPS commands, SSH commands, package apply, service restart/deploy, public exposure, config delivery, write API, Local Agent mutations, backup/import/reboot, production peer/user mutation, destructive VPS actions, Telegram token use, live bot send or Telegram profile mutation. Любое live-use секретов требует отдельного named gate.

## Базовое Решение

```text
secret_transfer_policy: regenerate_on_target_where_possible + operator_local_channel_only_for_external_secrets
default_publication_policy: no raw secrets in AMN3/GitHub/chat/evidence/log excerpts
default_runtime_boundary: VPS_APPLY_ENABLED=false
default_panel_boundary: WEB_HOST=127.0.0.1, SSH tunnel only
```

Если секрет можно безопасно сгенерировать на target/local machine, его нужно генерировать там и не переносить через чат. Если секрет приходит из внешнего сервиса, например Telegram BotFather, он передается только через локальный приватный канал оператора.

## Секретные Классы

| Class | Examples | Default handoff |
| --- | --- | --- |
| `external-token` | Telegram bot token, future payment/provider tokens | Operator local/private channel only |
| `generated-local-secret` | web session secret, admin password, API token raw value | Generate on target/local machine, store hash or file only |
| `target-server-config` | raw `servers.yml`, target IP/host, SSH user, key path, runtime paths | Operator local/private channel only; evidence uses redacted labels |
| `client-config-secret` | `.conf`, QR payload/PNG, `vpn://`, private key, PSK | Never publish; delivery requires separate config-delivery gate |
| `runtime-secret-state` | AmneziaWG private keys, PSKs, peer configs, backup contents | Never publish; backup/import needs separate gate |
| `auth-material` | raw API token, Authorization header, token hash, session cookie, web password hash | Never publish; safe metadata only |

## Разрешенные Каналы

Allowed by default:

- operator local shell;
- target VPS local filesystem during an approved named gate;
- local password manager or OS secret store managed by the operator;
- private provider/Telegram UI controlled by the operator;
- redacted yes/no/count summaries in AMN3 evidence.

Not allowed by default:

- pasting raw tokens, `.env`, `servers.yml`, `.conf`, QR, `vpn://`, private keys, PSK, passwords, cookies or Authorization headers into chat;
- committing secret-bearing files;
- storing secret-bearing screenshots in AMN3;
- sending secrets through GitHub comments, issues, commits or PR descriptions;
- asking Codex to print full secret-bearing logs as evidence.

## Safe Summary Format

Evidence may record only:

```text
telegram_token_present: yes/no/not_checked
admin_telegram_ids_count: <integer>
web_secret_present: yes/no/not_checked
server_config_present: yes/no/not_checked
server_config_selected_name: local | redacted-label
env_vps_apply_enabled_false: yes/no/not_checked
web_host_loopback: yes/no/not_checked
file_modes_restricted: yes/no/not_checked
secret_publication: none
```

Evidence must not record raw values, token prefixes/suffixes, target IP/host, exact SSH command with identity paths, Telegram IDs, full `.env`, full `servers.yml`, full logs, raw errors containing secrets, config payloads or screenshots with visible secret-bearing material.

## Operator Handoff Ceremony

Use this sequence only inside a named gate that explicitly needs secrets.

1. Declare the gate name and exact secret classes needed.
2. Confirm this protocol is in force.
3. Operator creates or retrieves secrets outside chat.
4. Operator writes secrets directly to the target/local file or secret store.
5. Operator restricts file permissions locally.
6. Operator reports only the safe summary fields.
7. If any required evidence would reveal a secret, stop and return `no-go` or `defer`.

Safe evidence example:

```text
gate_name: P5-EXAMPLE-SECRET-HANDOFF
secret_classes_used: external-token, generated-local-secret, target-server-config
telegram_token_present: yes
admin_telegram_ids_count: 2
web_secret_present: yes
server_config_present: yes
server_config_selected_name: local
env_vps_apply_enabled_false: yes
web_host_loopback: yes
file_modes_restricted: yes
secret_publication: none
go_no_go_decision: go
```

## File Boundaries

`.env` and `servers.yml` are private runtime files. They are not package inputs, not AMN3 evidence, and not chat payloads.

Required safe defaults for Phase 5 service-mode:

```text
VPS_APPLY_ENABLED=false
WEB_ADMIN_ENABLED=true
WEB_HOST=127.0.0.1
WEB_PORT=3030
```

Required safe summary after the operator writes private files:

```text
env_present: yes
servers_yml_present: yes
file_modes_restricted: yes
vps_apply_enabled_false: yes
web_host_loopback: yes
secret_publication: none
```

On Linux service-mode targets, the intended private-file mode is group-readable only for the service boundary, for example `0640` with the service group. The exact command is gate/runbook-specific and must not print file contents.

## Stop Lines

Stop immediately if:

- the operator is about to paste a raw secret into chat;
- a command output includes a token, key, `.conf`, QR payload, `vpn://`, target IP/host or full `servers.yml`;
- the target identity is ambiguous;
- the gate name does not explicitly authorize secret use;
- a live action would be required but only docs/local work is approved;
- `VPS_APPLY_ENABLED` is missing or not confirmed false for read-only/default Phase 5 work;
- a safe summary cannot be produced without revealing secret-bearing material.

## Related Gates

- Telegram bot token use or profile icon mutation: separate Telegram identity gate.
- Fresh VPS rebuild or wipe: `VPS-REBUILD-001` plus destructive final phrase.
- Config delivery, `.conf`, QR, `vpn://`, short links or self-service delivery: separate config-delivery/public/self-service gate.
- `/api/clients` write CRUD or production peer/user mutation: separate write/live gate.
- Backup/import/reboot: separate backup/import/reboot gate.
- Local Agent write/config routes: separate Local Agent mutation gate.

## Phase 5 Default

Until a named gate says otherwise:

```text
live_vps_commands: no
ssh_commands: no
telegram_token_use: no
live_bot_send: no
package_apply: no
service_restart_deploy: no
public_exposure: no
config_delivery: no
write_api: no
local_agent_mutation: no
backup_import_reboot: no
production_peer_user_mutation: no
secret_publication: none
```
