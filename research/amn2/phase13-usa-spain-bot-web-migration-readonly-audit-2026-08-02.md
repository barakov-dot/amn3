# AMN2 Phase 13: read-only аудит переноса bot/web с USA на Spain

Дата проверки: 2026-08-02.

## Разрешённый scope

- только secret-safe read-only SSH аудит USA bot/web dependencies и текущего
  Spain target state;
- design checksum-bound backup, stage, verify, cutover и rollback;
- без deploy, restore, database write, service action, Telegram API call,
  package build, USA shutdown/reuse и любых Spain/USA/AWG mutation;
- без вывода target, user, private key path, host-key fingerprint, Telegram ID,
  token, password/hash value, raw DB row, peer identifier или stdout/stderr.

Root HEAD до проверки:
`0435090fb6d34d3e6aab368b776992619ab49ce1`.

Read-only runner SHA-256:
`29589714EFD95BAE7C14428E4C90E0EA2B01D3826B4A373618CFE605AB043ECA`.

Одноразовый HMAC proof runner SHA-256:
`12118DE13CE78D066D0AA79C12C73D0A769F1C7750B4CD3C13DE0C8480FE0B22`.

## Transport и safety receipt

```text
spain_transport=success
usa_transport=success
remote_file_written=false
service_action_attempted=false
database_write_attempted=false
telegram_api_called=false
raw_secret_emitted=false
raw_identifier_emitted=false
awg_action_attempted=false
live_mutation_authorized=false
live_mutation_attempted=false
```

Выполнено по одному основному SSH process на каждый server и отдельный
одноразовый secret-reference equality proof на каждый server. Proof использовал
случайный ephemeral HMAC key; наружу выведены только boolean equality results.
Raw secret values и стабильные secret fingerprints не сохранялись.

## Spain target

```text
web=active|enabled|restart_0|login_healthy
web_listener=127.0.0.1:3031_only
bot=inactive|static|restart_0
bot_enable_marker=absent
database=present|integrity_ok|foreign_key_issues_0
database_tables=18
database_total_rows=46
data_root_regular_files=4
users=1
devices=7
device_passports=7
device_lifecycle_events=7
admin_config_issuance_requests=2
admin_config_issuance_receipts=7
admin_actions=14
plans=0
orders=0
api_tokens=0
servers=1
```

Требуемые Spain database, runtime env, server config и source присутствуют.
Spain bot token, `APP_SECRET_KEY`, web password hash и web session secret имеют
непустые secret references. Значения не читались и не сохранялись.

## USA source

```text
web=active|enabled|restart_0|login_healthy
web_listener=127.0.0.1:3030_only
bot=active|enabled|restart_0
database=present|integrity_ok|foreign_key_issues_0
database_tables=15
database_total_rows=88
data_root_regular_files=2
users=6
devices=8
plans=8
orders=8
api_tokens=12
admin_actions=45
servers=1
configured_admin_count=2
```

Требуемые USA database, runtime env, server config, source и venv interpreter
присутствуют. Venv interpreter является ожидаемой symlink-границей, а не
отсутствующим artifact.

## Secret-reference equality

```text
telegram_bot_token_equal=false
app_secret_key_equal=false
web_admin_password_hash_equal=false
web_admin_session_secret_equal=false
raw_values_emitted=false
stable_fingerprints_persisted=false
```

Следствия:

1. Existing USA Telegram identity нельзя получить простым запуском текущего
   Spain bot: во время будущего disabled staging необходимо checksum-bound
   заменить только Spain bot token и перенести allowlisted admin identifiers.
2. Spain `APP_SECRET_KEY` остаётся authoritative. Blind USA DB restore либо
   перенос USA encrypted device secrets сделал бы live state нечитаемым или
   уничтожил бы Spain d1–d7.
3. Spain web password/session secret сохраняются. USA sessions не переносятся;
   это принудительное завершение старых web sessions.
4. USA API-token records не переносятся как usable credentials. Нужные
   интеграции получают отдельное reissue/revoke decision после cutover.

## Source compatibility

Read-only Git ancestry check доказал:

```text
usa_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
spain_authoritative_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
merge_base=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
```

То есть Spain source является потомком и функциональным superset USA overlay.
Копировать USA source поверх Spain или выполнять source downgrade не требуется
и запрещено. Перенос относится к application state, bot identity/configuration
и service lifecycle.

## Decision

`migration_design_required=true` и `blind_restore_allowed=false`.

Безопасный путь — versioned logical merge:

- Spain DB и её семь d1–d7 остаются основой;
- USA users/plans/orders и legacy device metadata проходят preview и
  idempotent mapping;
- legacy devices могут появиться только как `external_only` и недоступные для
  config resend/peer apply;
- USA servers, live peers, encrypted device keys/configs, API token hashes,
  sessions и canonical admin audit rows не импортируются в live Spain state;
- полный USA snapshot сохраняется как encrypted rollback/archive artifact;
- Spain bot staged disabled, затем отдельный two-host single-instance cutover;
- USA нельзя переустанавливать до Spain web/data acceptance и bot cutover
  acceptance.

Этот receipt не разрешает package build, data transfer, database apply,
service action, Telegram cutover, USA shutdown или reuse.
