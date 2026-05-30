# Secret Inventory + Backup Policy для `amn2`: design spec

## Назначение

`Secret Inventory + Backup Policy` - кандидатный design artifact для `amn2`, который описывает, какие данные считаются секретами, где они могут храниться, как они попадают в backup/export, как restore должен с ними обращаться и какие проверки нужны до production-переноса.

Spec возник из анализа `PRVTPRO/Amnezia-Web-Panel`, но не переносит upstream storage layout, backup endpoints или код. Upstream имеет license verdict `GPL-3.0`, поэтому для `amn2` допустима только самостоятельная реализация идеи после отдельного review в репозитории `amn2`.

Цель design spec: не допустить ситуации, где backup состояния панели становится полным набором ключей от VPS, VPN-конфигов, API tokens и внешних интеграций.

## Контекст и проблема

VPN/control-panel хранит или обрабатывает много чувствительных данных:

- SSH credentials;
- VPN private keys и client configs;
- API token hashes;
- public share tokens;
- Telegram bot tokens;
- external API keys;
- SSL private keys;
- user password hashes;
- backup archives;
- raw command outputs;
- audit metadata.

Если эти данные лежат в одном state-файле и скачиваются как обычный backup, появляется несколько проблем:

- компрометация backup дает доступ к серверам и пользовательским конфигам;
- restore может неожиданно оживить старые tokens или share links;
- redaction выполняется ad hoc и пропускает новые secret fields;
- audit не показывает, кто скачал full backup;
- разработчик не понимает, что новое поле должно попасть в secret inventory.

`Secret Inventory + Backup Policy` должен стать обязательной частью design review перед добавлением новых secret-bearing функций.

## Scope

Входит в scope:

- secret inventory;
- классификация секретов;
- storage policy;
- backup modes;
- restore policy;
- redaction policy;
- audit events;
- связь с `Scoped API Tokens`, `Route Policy Matrix` и `RemoteOperationRunner`;
- test strategy.

Не входит в scope этого spec:

- выбор конкретной базы данных или vault;
- реализация encryption at rest;
- UI backup wizard;
- enterprise key management;
- legal/compliance режимы хранения персональных данных;
- disaster recovery runbook для инфраструктуры целиком.

## Основные принципы

1. Любое новое secret-bearing поле сначала добавляется в secret inventory.
2. Redacted backup является default.
3. Full backup является explicit dangerous mode.
4. Restore не должен автоматически оживлять tokens, share links и external credentials без явного решения.
5. Secret values не пишутся в audit, logs, generic errors и OpenAPI examples.
6. Backup download и restore всегда audit-required.
7. Secret classification должна быть machine-checkable, а не только текстовым комментарием.
8. Если система не знает класс поля, оно не попадает в backup по умолчанию.

## Secret classes

Минимальная классификация:

| Class | Значение | Примеры | Default backup behavior |
| --- | --- | --- | --- |
| `public-metadata` | не секрет, можно экспортировать | server name, protocol label | include |
| `internal-id` | внутренние id, не секрет сами по себе | server_id, user_id | include |
| `credential-secret` | дает доступ к системе или сервису | SSH password, API key, bot token | redact |
| `private-key` | приватный ключ или material для генерации доступа | SSH private key, VPN private key, SSL key | redact |
| `token-hash` | hash токена, usable for validation | API token hash, share token hash | redact by default |
| `password-hash` | user password hash | password hash, password salt | redact by default |
| `client-config-secret` | конфиг или ссылка, дающая VPN-доступ | WireGuard config, Xray link | redact |
| `recovery-sensitive` | данные, нужные для recovery, но опасные при утечке | encrypted backup key metadata | redact unless encrypted full |
| `audit-metadata` | metadata без secret value | token prefix, actor id, event type | include if safe |

Если поле содержит смешанные данные, выбирается самый строгий класс.

## Secret inventory record

Каждое secret-bearing поле описывается в inventory:

```text
SecretInventoryItem
  field_path: stable logical path, например "servers[].ssh.private_key"
  owner_domain: servers | users | tokens | sharing | integrations | vpn-configs | backups | audit
  class: credential-secret | private-key | token-hash | password-hash | client-config-secret | recovery-sensitive
  source: generated | user-provided | imported | external
  storage_policy: plaintext-disallowed | encrypted-at-rest | hash-only | external-secret-ref
  backup_policy: redact | encrypted-full-only | metadata-only | include
  restore_policy: never-restore | restore-disabled | restore-with-rotation | restore-as-is
  redaction_label: stable label for replacement text
  rotation_required_after_exposure: true | false
  audit_on_read: true | false
```

`field_path` должен быть логическим, а не привязанным к случайной структуре JSON. При миграции storage inventory должен обновляться.

## Storage policy

Запрещенная baseline-модель для production:

- хранить SSH password/private key в общем state без encryption;
- хранить plaintext share tokens;
- хранить raw API tokens;
- хранить Telegram/API integration tokens в backup-friendly settings field;
- хранить generated client configs как обычные read-model records без классификации;
- хранить SSL private key рядом с публичными settings без secret metadata.

Допустимые policies:

- `hash-only`: API tokens, share tokens, passwords;
- `encrypted-at-rest`: SSH credentials, external API keys, bot tokens, private keys;
- `external-secret-ref`: ссылка на vault/OS secret store, если появится;
- `plaintext-disallowed`: raw API token после one-time display;
- `metadata-only`: token prefix, last_used_at, created_at.

Первый production шаг может быть проще vault-а, но обязан иметь inventory, redaction и backup rules.

## Backup modes

### Redacted backup

Default mode.

Содержит:

- non-secret configuration;
- public metadata;
- internal ids, если они нужны для restore;
- users без password hashes или с disabled auth state;
- token metadata без token hashes;
- share metadata без usable token;
- audit metadata без secret values;
- schema version и migration metadata.

Не содержит:

- SSH password/private key;
- raw API tokens;
- API token hashes;
- share token values/hashes;
- user password hashes;
- VPN private keys;
- generated client configs;
- Telegram/API tokens;
- SSL private keys;
- raw command stdout/stderr.

Restore redacted backup должен явно показывать, какие secrets будут missing и какие функции останутся disabled до повторной настройки.

### Encrypted full backup

Dangerous explicit mode.

Требования:

- отдельный route policy и scope, например `backup:read-full`;
- explicit confirmation;
- audit event before and after export;
- encryption key не хранится внутри backup;
- backup содержит schema version и secret inventory version;
- оператор видит предупреждение, что архив содержит доступ к VPS, users и integrations;
- download filename не должен содержать secret material;
- backup не пишется во временный файл без контроля permissions.

Если encryption не реализована, full backup не должен существовать как production feature.

### Metadata-only export

Полезен для diagnostics и support:

- не содержит user secrets;
- не содержит token hashes;
- не содержит client configs;
- может содержать counts, enabled flags, versions, route policy ids, manager statuses;
- должен быть безопаснее redacted backup, но все равно проходит review.

## Restore policy

Restore - high-risk operation.

Правила:

- restore всегда `destructive` или high-risk `state-write`;
- restore требует schema validation;
- restore требует preview: что будет создано, изменено, отключено;
- restore redacted backup не включает старые tokens/share links;
- restore full backup требует отдельной confirmation;
- restore не должен overwite production secrets без preview;
- restore должен создавать audit event;
- restore должен иметь recovery note;
- несовместимая schema rejected до изменения state.

Secret restore policies:

| Restore policy | Поведение |
| --- | --- |
| `never-restore` | поле не восстанавливается никогда |
| `restore-disabled` | metadata восстанавливается, secret требует повторной настройки |
| `restore-with-rotation` | secret восстанавливается только с обязательной rotation |
| `restore-as-is` | допустимо только для encrypted full backup и явного confirmation |

API tokens и public share tokens по умолчанию должны быть `restore-disabled` или `never-restore`.

## Redaction policy

Redaction должна быть централизованной.

Redaction sources:

- secret inventory items;
- active token prefixes and hashes;
- known key markers;
- generated client config patterns;
- external API token patterns;
- runtime secret refs из `RemoteOperationRunner`;
- environment secret names.

Replacement examples:

```text
<redacted:ssh-private-key>
<redacted:api-token-hash>
<redacted:client-config>
<redacted:telegram-token>
```

Redaction применяется к:

- backup/export;
- logs;
- audit payload;
- API errors;
- command stdout/stderr;
- diagnostics bundles;
- support exports.

Redaction failure считается security bug.

## Audit requirements

Audit обязателен для:

- redacted backup download;
- encrypted full backup download attempt;
- encrypted full backup success/failure;
- restore preview;
- restore apply;
- restore failure;
- secret read outside normal operation;
- secret rotation;
- backup policy change;
- inventory classification change;
- failed attempt to include unknown secret field in backup.

Audit event:

```text
SecretPolicyAuditEvent
  event_type
  actor
  route_policy_id
  backup_mode
  secret_classes_touched
  decision: allowed | denied
  denial_reason
  request_id
  created_at
```

Не включать secret values, raw backup content или full field payload.

## Связь с другими specs

### Scoped API Tokens

- API token raw value не хранится после create.
- Token hashes не попадают в redacted backup.
- Restore redacted backup не оживляет токены.
- `backup:read`, `backup:restore` и будущий `backup:read-full` являются high-risk scopes.

### Route Policy Matrix

- Backup download и restore должны иметь route policies.
- Full backup требует отдельного scope и confirmation.
- Restore считается destructive или high-risk state-write.
- Secret-read routes должны иметь response secret policy.

### RemoteOperationRunner

- Secret refs не попадают в operation inputs.
- Command outputs проходят redaction перед audit/API response.
- Recovery notes не содержат secret values.
- Full backup не должен включать raw runner logs без redaction.

## Test strategy

Минимальные тесты:

- каждое secret-bearing поле имеет inventory record;
- unknown field class не попадает в backup по умолчанию;
- redacted backup не содержит SSH password/private key;
- redacted backup не содержит API token hash;
- redacted backup не содержит share token;
- redacted backup не содержит user password hash;
- redacted backup не содержит VPN client config;
- encrypted full backup недоступен без explicit product support;
- backup download создает audit event;
- restore preview не меняет state;
- restore rejected при несовместимой schema;
- redacted restore disables tokens/share links;
- restore apply создает audit event;
- API error не содержит secret value;
- command stdout/stderr проходят redaction;
- secret field addition without inventory fails test.

Aggregate checks:

- inventory covers all fields marked as secret in schemas;
- every `backup_policy=include` item has class `public-metadata`, `internal-id` или approved `audit-metadata`;
- every `restore-as-is` item requires encrypted full backup;
- every `audit_on_read=true` item has a route or service audit assertion;
- no test fixture stores realistic private keys or live tokens.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Открыть текущий `amn2` и составить inventory существующих secret-bearing fields.
2. Разделить поля по secret classes.
3. Ввести redacted backup как единственный допустимый export.
4. Добавить backup tests на отсутствие секретов.
5. Добавить restore preview без применения изменений.
6. Добавить restore redacted backup с disabled secrets.
7. Подключить audit для backup/restore.
8. Отдельно решить, нужен ли encrypted full backup.
9. Только после этого добавлять full backup route и scopes.

## Решение для lab

Статус: `design-candidate`.

Этот spec является четвертым foundational artifact после `RemoteOperationRunner`, `Route Policy Matrix` и `Scoped API Tokens`. До просмотра текущего `amn2` он остается research/design документом, а не задачей на немедленную реализацию.

## Источники

- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- Scoped API Tokens spec: [docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md](2026-05-30-scoped-api-tokens-design.md)
- Route Policy Matrix spec: [docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md](2026-05-30-route-policy-matrix-design.md)
- RemoteOperationRunner spec: [docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md](2026-05-30-remote-operation-runner-design.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
