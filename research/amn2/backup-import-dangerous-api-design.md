# Backup/Import Dangerous API Design

Дата: 2026-06-01.

Назначение: зафиксировать safety boundary для будущих backup/import/restore surfaces в `amn2`, чтобы они не стали обычными download/upload endpoints с доступом к secret-bearing state.

Этот документ не является implementation plan. Он не меняет `amn2`, не добавляет web/API routes, не меняет текущий CLI backup/restore, не читает `.env` и не требует live VPS. Он описывает policy gates для будущего переноса backup/import идей из AMN3/PRVTPRO/hybrid в production.

## Current production baseline

В `amn2` уже есть локальный CLI recovery baseline:

```text
app/backup/service.py
app/backup/manifest.py
app/backup/storage.py
tests/backup/test_backup_service.py
docs/EMERGENCY_RESTORE_CHECKLIST.ru.md
```

Текущий behavior:

- `BackupService.create()` создает encrypted `.tar.enc` archive;
- archive содержит `database.sqlite3` и `manifest.json`;
- encryption uses `APP_SECRET_KEY` через `SecretBox`;
- manifest excludes `app_secret_key`, `telegram_bot_token`, `qr_files`, `plain_configs`;
- `verify()` decrypts archive, validates manifest and DB checksum;
- `restore()` refuses overwrite unless `force=True`;
- restore validates SQLite integrity, required tables/columns, order rows, active device rows and decryptability of encrypted peer secrets before writing target DB;
- tests confirm checksum/schema/decryptability failures block restore before target write.

Этот baseline полезен, но это не web/API backup policy. CLI operator recovery и downloadable API backup имеют разный blast radius.

## Problem

Backup/import touches nearly every high-risk area:

- peer private keys and preshared keys;
- API token hashes;
- public/share token hashes when those appear;
- user/device/server state;
- audit history;
- runtime topology;
- future SSH host key pins;
- future Local Agent/controller metadata.

If backup/import becomes a normal endpoint:

- leaked full backup can become a full control-plane compromise;
- restore can revive old tokens/share links;
- import can overwrite live production state without preview;
- generated configs, QR payloads or `vpn://` links can leak through archive or diagnostics;
- operator cannot distinguish "metadata export" from "credential-bearing disaster recovery artifact".

## Decision

Status: `implemented-pushed-local-gate-complete` for the first local-only policy/preview contract.

Implementation evidence:

```text
branch: amn2/codex/backup-import-policy-contract
head: afb2702 Tighten backup import preview type contract
foundation: d2c160b Add backup import policy contract
evidence: research/amn2/backup-import-policy-contract-implementation.md
focused: 61 passed
full: 584 passed, 1 warning
```

Future backup/import work must split into three explicit lanes:

1. `metadata-export` - support/debug metadata only, no usable secrets.
2. `redacted-backup` - default backup/export mode, safe for support handoff but not a full disaster recovery artifact.
3. `encrypted-full-backup` - explicit dangerous mode for operator recovery only, never default.

Restore/import must be separate from export:

- `restore-preview` validates archive and shows redacted impact without writing state;
- `restore-apply` is destructive/high-risk and requires explicit confirmation;
- `import-existing-state` is a separate migration wizard, not a shortcut around restore.

## Route/auth policy

Future routes must not reuse generic admin endpoints.

Suggested policies:

| Policy id | Surface | Actor | Risk | Required gates |
| --- | --- | --- | --- | --- |
| `backup.metadata_export` | metadata/support export | `web-admin` or `cli-operator` | `secret-adjacent-read` | redaction, no secret classes, audit recommended |
| `backup.redacted_create` | redacted backup download | `web-admin` or `cli-operator` | `secret-adjacent-read` | CSRF for web, audit, no token hashes/configs |
| `backup.full_create` | encrypted full backup | `cli-operator` first; web/API later only after decision | `secret-read` + `dangerous` | explicit confirmation, encryption, audit before/after |
| `restore.preview` | restore/import preview | `web-admin` or `cli-operator` | `destructive-preview` | decrypt/validate only, no target write |
| `restore.apply` | restore to target DB/state | `cli-operator` first | `destructive` | preview id, confirmation, backup-before-write, audit, recovery note |
| `import.existing_state_preview` | external state import preview | `cli-operator` first | `secret-read` + `destructive-preview` | structured parser, conflict report, no writes |
| `import.existing_state_apply` | external state import apply | blocked until separate design | `destructive` | versioned migration plan, rollback, audit |

Bearer tokens must not get backup/import scopes in the first integration. `backup:read`, `backup:read-full`, `backup:restore` and `import:apply` remain reserved high-risk scopes.

## Backup modes

### Metadata export

Allowed:

- app version;
- schema version;
- route policy ids;
- runtime type summary;
- counts by status;
- feature flags;
- redacted latest errors;
- backup/import capability state.

Forbidden:

- database rows with encrypted secrets;
- token hashes;
- password hashes;
- generated configs;
- QR payloads or QR PNG bytes;
- `vpn://` links;
- raw command stdout/stderr;
- `.env` values.

### Redacted backup

Default web/API export mode if such export is ever added.

Allowed:

- non-secret metadata needed for support or dry-run restore;
- users/devices/server rows after applying per-field backup policy;
- audit metadata without secret payload;
- token records with hashes removed and restored as disabled metadata;
- secret-bearing records represented as missing/disabled until reconfigured.

Forbidden:

- `APP_SECRET_KEY`;
- Telegram/SMTP/VPS credentials;
- API/Local Agent token hashes;
- email recovery/share token hashes;
- peer private keys;
- preshared keys;
- generated `.conf`;
- QR payload/PNG;
- `vpn://` import links;
- raw backup encryption material.

Restore from redacted backup must not revive usable VPN credentials, tokens or share links.

### Encrypted full backup

Dangerous explicit mode.

Allowed only when:

- encryption is mandatory;
- encryption key is not stored inside archive;
- operator receives visible warning that archive can grant VPN/control-plane access;
- route/policy scope is separate from normal admin read;
- audit logs attempt, success/failure and actor without archive content;
- restore path validates archive before write.

Current CLI encrypted backup is the closest existing baseline. It should remain CLI/operator recovery until web/API policy and tests exist.

## Restore/import flow

Future safe flow:

1. Upload/select backup or import artifact.
2. Decrypt/parse in isolated temporary area.
3. Validate manifest/schema/checksum.
4. Validate secret decryptability when full encrypted restore is requested.
5. Build redacted preview:
   - rows to create/update/disable;
   - secrets missing or requiring rotation;
   - tokens/share links that will remain disabled;
   - runtime/server conflicts;
   - host key pins requiring revalidation.
6. Require explicit confirmation tied to preview id/hash.
7. Create backup-before-write of current target state.
8. Apply changes.
9. Write audit and recovery note.

No preview means no restore/import apply.

## Import existing state

Importing existing server/config state is not the same as restoring an `amn2` backup.

Allowed first import boundary:

```text
import-existing-state-preview-only
```

It may parse and report:

- protocol/runtime type;
- public server metadata;
- peer count;
- IP/CIDR conflicts;
- unsupported fields;
- missing required fields;
- secret classes detected.

It must not:

- write local DB;
- write server runtime;
- generate configs;
- activate peers;
- trust imported private keys without secret inventory entry;
- log raw configs or `vpn://` links.

Apply for imported state remains blocked until a versioned migration plan exists.

## Secret restore policy

| Secret class | Redacted backup | Encrypted full backup | Restore default |
| --- | --- | --- | --- |
| `credential-secret` | exclude/redact | include only explicit full | restore-disabled or reconfigure |
| `private-key` | exclude/redact | include only explicit full | restore-as-is only with confirmation |
| `preshared-key` | exclude/redact | include only explicit full | restore-as-is only with confirmation |
| `client-config-secret` | exclude | avoid storing generated artifacts | regenerate after restore |
| `token-raw` | never include | never include | never restore |
| `token-hash` | exclude/redact | include only explicit full if decided | restore-disabled or rotate |
| `password-hash` | exclude/redact | include only explicit full if decided | restore-disabled or force reset |
| `session-secret` | exclude | exclude | recreate |
| `topology-sensitive` | redact/pseudonymize | include if needed | revalidate |

## Audit and logging

Audit events:

```text
backup.metadata_exported
backup.redacted_created
backup.full_requested
backup.full_created
backup.denied
restore.preview_created
restore.apply_started
restore.apply_completed
restore.apply_failed
import.preview_created
import.apply_blocked
```

Audit payload may include:

```text
actor
route_policy_id
backup_mode
manifest_version
archive_id/fingerprint
secret_classes_touched
preview_id
decision
denial_reason
request_id
```

Audit/logs must not include:

```text
archive bytes
raw database rows
APP_SECRET_KEY
token hashes
private keys
PSK
.conf
QR payload/PNG
vpn:// link
raw import file body
```

## Safety gates before web/API exposure

Before adding any web/API backup/import route:

- Route/Auth Policy Matrix entry exists.
- Secret inventory covers every included field.
- Redacted backup is tested as default.
- Full backup is either absent or explicit dangerous mode.
- Restore preview exists and is side-effect free.
- Restore apply requires confirmation tied to preview id/hash.
- Backup-before-write exists for restore apply.
- Audit before/after exists.
- OpenAPI examples contain no realistic secret values.
- Rate limit / file size limits exist for upload/import.

## Required tests before implementation

Implementation plan must include tests that:

- metadata export contains no token hashes, encrypted peer secrets, configs, QR payloads or `vpn://` links;
- redacted backup excludes token hashes, peer private keys, PSK, password hashes and generated configs;
- encrypted full backup cannot be created without explicit dangerous mode;
- backup manifest lists includes/excludes and mode;
- restore preview validates checksum/schema/decryptability without writing target state;
- restore apply refuses to run without preview confirmation;
- restore apply creates backup-before-write before target mutation;
- redacted restore does not revive tokens/share links;
- full restore with wrong `APP_SECRET_KEY` fails before target write;
- import preview rejects unsupported schema/version without writes;
- import preview reports conflicts without logging raw config;
- audit payload contains safe metadata only;
- API errors never include archive contents, token hashes, private keys, PSK or `vpn://` links;
- file upload/import size and member list are constrained.

## First safe implementation boundary

Recommended first code boundary if this moves to `amn2`:

```text
backup/import policy registry and restore-preview contract
```

Status: implemented as local-only no-route slice in `amn2/codex/backup-import-policy-contract`, head `afb2702` with foundation commit `d2c160b`.

It may include:

- machine-readable backup mode registry;
- redacted field policy table;
- restore preview object;
- tests proving preview has no side effects;
- docs clarifying CLI encrypted backup vs future web/API backup modes.

It must not include:

- public backup download;
- broad API token access to backup;
- full backup web/API endpoint;
- restore apply from web/API;
- import apply;
- live VPS changes;
- copying PRVTPRO backup/restore code.
