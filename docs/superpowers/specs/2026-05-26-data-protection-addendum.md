# Data Protection Addendum

## Goal

Define how the first Amneziya MVP protects sensitive data before the Python scaffold is created. Security must be part of the initial architecture, not a later cleanup task.

## Sensitive Data Inventory

### Telegram Identity Data

Fields:

- `telegram_id`
- `username`
- `first_name`
- `last_name`
- admin Telegram IDs

Risks:

- User deanonymization if the database leaks.
- Admin targeting if administrator IDs leak.
- Excessive logging of message payloads.

Controls:

- Store only fields needed for bot operation.
- Do not log full Telegram message objects.
- Keep admin IDs in `.env` or secret storage, not committed config.
- Treat `telegram_id` as personal data in exports and backups.

### VPN Secret Material

Fields and artifacts:

- peer private key
- preshared key
- full `.conf`
- QR image generated from `.conf`
- import link or import key, if later supported

Risks:

- Anyone with these values can use the VPN identity.
- QR images are equivalent to full configs.
- Resend and debug flows can accidentally expose complete configs.

Controls:

- Encrypt `peer_private_key` and `preshared_key` at rest with an application encryption key from the environment.
- Never persist generated QR files longer than needed for delivery.
- Never write full `.conf` content to normal application logs.
- Use redaction helpers for any object that may contain config text.
- Store generated config files only in temporary locations and delete them after Telegram delivery.
- Keep `last_config_sent_at`, but not a plaintext copy of the sent config.

### Server Access Data

Fields and artifacts:

- SSH host
- SSH port
- SSH username
- SSH private key path
- endpoint host
- server public key
- `servers.yml`

Risks:

- SSH metadata helps attackers find the management surface.
- Private key paths can reveal local filesystem layout.
- A committed real `servers.yml` could expose infrastructure.

Controls:

- Commit only `servers.example.yml` with placeholders.
- Add real `servers.yml` to `.gitignore`.
- Do not log SSH passwords, private key contents, or full connection strings.
- Prefer a restricted provisioning SSH user.
- Validate that generated server summaries hide secret fields.
- Keep endpoint host visible only where needed for client config generation and admin views.

### Database and Backups

Artifacts:

- SQLite database
- database dumps
- server config backups
- application logs

Risks:

- SQLite contains user identity, device metadata, peer public keys, encrypted secrets, and order history.
- Server config backups may contain peer public keys and server-side topology.
- Logs can silently become the biggest leak surface.

Controls:

- Store the SQLite file outside the repository by default.
- Add local database files, dumps, generated configs, QR files, and backups to `.gitignore`.
- Encrypt backup archives before storing them outside the host.
- Use log redaction for keys, tokens, configs, Telegram IDs where practical, and payment identifiers.
- Separate operational logs from audit events.
- Audit events should store action metadata, not secret payloads.

### Payment and Order Data

Fields:

- payment provider
- external payment ID
- amount
- currency
- status
- paid timestamp

Risks:

- External payment IDs can link a Telegram user to a payment provider account.
- Webhook payloads may contain personal or financial metadata.

Controls:

- Store only provider fields required for reconciliation.
- Do not log full webhook bodies.
- Redact external payment IDs in logs.
- Keep payment provider credentials in environment or secret storage.
- Isolate payment handling behind a provider interface.

## Default Redaction Rules

Any logging or admin display layer must redact values matching these categories:

- Telegram bot token
- encryption key
- private key
- preshared key
- full `.conf`
- QR payload
- SSH password
- SSH private key contents
- payment provider token
- external payment IDs

Public keys and endpoint hosts may be displayed in admin-only contexts, but should not appear in user-facing errors unless required.

## Encryption-at-Rest Decision

The MVP stores peer secret fields encrypted, not plaintext and not as a plaintext full config.

Required environment variable:

```env
APP_SECRET_KEY=CHANGE_ME_GENERATED_SECRET
```

Implementation requirements:

- The app must refuse to start in normal mode if `APP_SECRET_KEY` is missing.
- Tests may use a deterministic test key.
- Secret encryption and decryption should live in a small dedicated module.
- The encrypted database value should include enough metadata to support future key rotation.

## File Hygiene

The scaffold should include `.gitignore` entries for:

```text
.env
*.db
*.sqlite
*.sqlite3
*.conf
*.qr.png
servers.yml
backups/
tmp/
```

Committed examples should use placeholders only:

- `.env.example`
- `servers.example.yml`

## Operational Rules

- Generate config and QR artifacts just in time.
- Delete temporary config and QR artifacts after delivery.
- Do not print generated configs to console.
- Do not include secrets in exception messages.
- Do not store raw Telegram updates in the database.
- Keep admin allowlist enforcement close to the bot entry point.
- Rate-limit user access requests and config resend actions.

## Security Tests for the First Scaffold

Add tests that verify:

- redaction removes private keys, PSK values, bot tokens, and full config markers from log-safe strings;
- config generation does not log the generated config;
- secret fields round-trip through encryption and decryption;
- the app refuses normal startup without `APP_SECRET_KEY`;
- `.gitignore` covers `.env`, local databases, generated configs, QR files, `servers.yml`, and backups.

## Backup and Recovery

Detailed backup and restore requirements are defined in [2026-05-26-backup-and-recovery-addendum.md](2026-05-26-backup-and-recovery-addendum.md).

Data protection rules for backups:

- backup archives must be encrypted before leaving the host;
- backup archives must not include plaintext `APP_SECRET_KEY`;
- restore requires the operator to provide the original `APP_SECRET_KEY`;
- backup manifests may include counts and checksums, not user identifiers or secret payloads;
- backup and restore logs must use the same redaction rules as application logs.

## Remaining Decisions

- Choose the exact encryption library during implementation. The preferred Python path is `cryptography` with Fernet or another authenticated encryption primitive.
- Define long-term off-host storage and retention when real VPS integration begins.
- Define key rotation before production use with real users.
