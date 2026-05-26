# Backup and Recovery Addendum

## Goal

Make backup and restore a first-class part of the first Amneziya scaffold so the service can be moved to another host or recovered after failure with minimal data loss and minimal disruption for clients.

The first scaffold does not manage a live VPS yet, so the initial implementation focuses on application data, encrypted secrets, server metadata, and restore verification. Live VPN server config backup and peer re-application become mandatory when real `awg` integration is added.

## Recovery Targets

The MVP should support two recovery scenarios:

1. **Application host loss**: the Telegram bot host or local database is lost, but the VPN server is still running. Restore should bring the bot back with users, devices, expiry dates, encrypted peer secrets, server metadata, and order history intact.
2. **Migration to another bot host**: move the bot and database to a new machine while keeping the same VPN server and existing client configs working.

Future live-server recovery:

3. **VPN server loss**: restore service on a replacement VPS. Existing clients cannot stay connected automatically if the endpoint or server keys change; the realistic recovery path is to issue new configs or restore identical server-side configuration where possible.

## Backup Contents

Each backup archive should contain:

- SQLite database dump or consistent SQLite copy;
- schema or migration version;
- application version metadata;
- backup manifest with timestamp, hostname, app version, and database checksum;
- sanitized server metadata needed to regenerate configs;
- optional `servers.yml` if present, encrypted inside the backup archive;
- no plaintext generated `.conf` files;
- no QR images;
- no plaintext Telegram bot token;
- no plaintext `APP_SECRET_KEY`.

The backup must not contain the `APP_SECRET_KEY` in plaintext. Restoring encrypted peer secrets requires the operator to provide the same `APP_SECRET_KEY` separately through environment or secret storage.

## Backup Format

Use a portable archive format:

```text
amneziya-backup-YYYYMMDD-HHMMSS.tar
```

Then encrypt the archive:

```text
amneziya-backup-YYYYMMDD-HHMMSS.tar.age
```

For the first scaffold, the implementation can use an application-level encryption backend through Python. The exact tool can be selected during implementation, but the backup interface should not depend on one hard-coded storage provider.

Minimum manifest fields:

```json
{
  "format_version": 1,
  "created_at": "2026-05-26T00:00:00Z",
  "app": "amneziya",
  "database_kind": "sqlite",
  "database_checksum_sha256": "...",
  "includes": ["database", "manifest", "server_metadata"],
  "excludes": ["app_secret_key", "telegram_bot_token", "qr_files", "plain_configs"]
}
```

## Backup Storage

The scaffold should support local backup creation first:

```powershell
python -m app.cli backup create --output backups
python -m app.cli backup verify --file backups/amneziya-backup-...tar.age
python -m app.cli backup restore --file backups/amneziya-backup-...tar.age --target-data-dir data
```

Future storage backends can include SFTP, S3-compatible storage, or another VPS. They should be added behind a storage interface.

Local `backups/` must stay ignored by git.

## Restore Behavior

Restore must be explicit and guarded:

- refuse to overwrite an existing database unless `--force` is provided;
- verify the backup checksum before restoring;
- verify manifest `format_version`;
- require `APP_SECRET_KEY` to be present before restore validation;
- run a post-restore integrity check;
- print a summary without secrets.

Post-restore checks:

- database can be opened;
- required tables exist;
- encrypted peer fields can be decrypted with the provided `APP_SECRET_KEY`;
- active devices have VPN IPs and expiry dates;
- server records needed for config regeneration exist;
- no plaintext `.conf` or QR files were restored.

## Client Connectivity Strategy

For the first scaffold, backup protects the bot state and the ability to regenerate user configs. It does not touch live peers because live peer management is outside this increment.

When live VPS support is added:

- backup the server-side AmneziaWG config before every peer add, revoke, or expiry operation;
- store server config backups encrypted;
- include enough server metadata to reconstruct peer state;
- keep dynamic peer application and persistent config writes in sync;
- after restoring the bot, reconcile database devices against live `awg show` output before making changes;
- if the VPN server itself is lost and cannot be restored with the same endpoint and keys, mark affected devices as needing reissue and send users new configs.

This avoids promising impossible seamless failover while still minimizing disruption.

## Scheduling

The scaffold should include backup service code and CLI commands. Automatic scheduling can be added as a later operational step.

Recommended production policy:

- create a backup after every successful peer lifecycle change;
- create a scheduled backup at least daily;
- keep short-term local backups and encrypted off-host backups;
- test restore regularly on a non-production host.

## Security Requirements

- Backups must be encrypted before leaving the host.
- Backups must not include plaintext `APP_SECRET_KEY`.
- Backup logs must not include user names, Telegram IDs, private keys, PSK, full configs, or payment IDs.
- Backup filenames must not include server hostnames, Telegram IDs, or user identifiers.
- Restore summaries may include counts, not sensitive records.

## First Scaffold Requirements

Add these modules:

```text
app/backup/
  manifest.py
  service.py
  storage.py
app/cli.py
```

Add these tests:

- backup manifest contains required metadata and excludes secret categories;
- backup creation includes the database and manifest;
- backup verification fails on checksum mismatch;
- restore refuses overwrite without `--force`;
- restore requires `APP_SECRET_KEY`;
- restored encrypted peer fields can be decrypted;
- `.gitignore` excludes `backups/`.

## Non-Goals for First Scaffold

- No automated remote upload yet.
- No live `awg` server config backup yet.
- No transparent client failover.
- No backup of plaintext configs or QR files.
- No storage of `APP_SECRET_KEY` inside backup archives.
