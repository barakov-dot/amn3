# kyoresuas/amnezia-api GitHub refresh 2026-06-10

Дата проверки: 2026-06-10.

Источник: https://github.com/kyoresuas/amnezia-api

## Snapshot

```text
repo: kyoresuas/amnezia-api
branch: main
latest_tree_sha: ffdc78cf4e6f653322c6df251df10a7d7274a887
latest_commit: ffdc78c refactor: устойчивость записи конфигов, валидация и чистка кода
latest_commit_date_utc: 2026-06-02T21:02:25Z
commits_seen_on_github: 198
license: MIT
primary_stack: Node.js, TypeScript, Fastify, Swagger/OpenAPI
```

Последние upstream commits 2026-06-02 сфокусированы не на новой большой функции, а на production-quality доработках: устойчивость записи конфигов, race/concurrency protection, setup/deploy resilience, rate-limit handling, QR route and README/CI updates.

## What Is Newly Useful For AMN2

### 1. Operation serialization and safer config writes

Upstream now has explicit primitives around in-process serialization and safer shell writes:

```text
signal: src/utils/mutex.ts, src/utils/shellWrite.ts
```

For AMN2 this is useful as a design signal for future write gates, not as copied code. The AMN2 version should be stricter:

- one operation lock per server/protocol/write surface;
- backup-before-write for persistent configs;
- write temp file, verify, atomic replace, reload/sync, post-check;
- rollback note and audit metadata;
- no raw config or keys in logs.

This reinforces current P4-NG / write API threat-model work.

### 2. Client lifecycle vocabulary

Upstream keeps the product vocabulary clear:

```text
status: active | disabled
expiresAt: unix timestamp or null
cleanupExpiredClients: cron/task disables expired access
```

For AMN2 this is worth adopting as wording and API contract language, but actual enable/disable/expiry mutation remains blocked until a named write/config gate.

Safe local use now:

- web/admin labels and docs;
- read-only API schema/status descriptions;
- candidate wording for future `/api/clients` write CRUD.

### 3. QR/vpn import compatibility

Upstream has a dedicated QR route and helper for Amnezia `vpn://` configs with QR series/chunking.

For AMN2 this reinforces the existing rule: QR is not a cosmetic artifact. It is a `secret-read` import artifact and must have byte-level tests before any route exposure.

Add to future config-delivery gate:

- decode QR and compare exact payload;
- test non-ASCII client names/metadata;
- test `.conf`, QR and `vpn://` as separate artifacts;
- prove no config, QR payload, import URI, private key or PSK enters logs/audit/errors.

### 4. Fastify hardening signals

Upstream now imports/registers Fastify hardening components such as rate limit and Helmet alongside Swagger and metrics.

For AMN2 this is a useful signal, but only after route exposure decisions. Current AMN2 private API should not become public because upstream exposes Swagger/docs/metrics patterns.

Safe use now:

- keep rate-limit as a required gate item for any future public/self-service/config/token route;
- keep docs/OpenAPI private/local unless a separate public-docs decision exists;
- keep metrics aggregate-only and privacy-classified.

### 5. Setup/deploy resilience

Recent setup/deploy commits improve update/install robustness: build cleanup, update mode behavior, nginx duplication avoidance and IP detection handling.

For AMN2 this is useful as an operator-doc signal:

- preflight before update;
- backup before service/runtime change;
- explicit bind/public exposure checks;
- idempotent service/proxy setup;
- rollback and health checks.

It does not change the current decision: do not install `kyoresuas/amnezia-api` on AMN2 target VPS as-is.

## Still Not Transferable As-Is

- one shared `x-api-key` model for all business operations;
- direct `/clients` write CRUD as default;
- direct config return/QR generation as public/API feature;
- backup/import/reboot routes;
- Docker socket exposure in container mode;
- public HTTP/nginx setup as default;
- public Swagger/docs/metrics without a separate exposure decision;
- upstream code copy into AMN2.

## Candidate Mapping

```text
P4-C006 / future WAPI:
  client write CRUD is still blocked, but upstream reinforces operation lock, atomic write, status/expiresAt and partial-failure requirements.

P4-C007 / config delivery:
  QR/vpn import compatibility becomes a mandatory test-plan item, not a UI polish item.

P4-C008 / backup-import-reboot:
  upstream still confirms the need for dangerous-operation policy; no route exposure.

P4-I003 / read-only API status:
  Swagger/domain grouping remains useful only for private/local docs and schema maturity.

P4-N003 / metrics privacy:
  metrics/load/server stats stay aggregate-only and privacy-classified.

P4-NG write API readiness:
  add operation serialization, atomic write, backup-before-write, post-check and rollback to the threat model.
```

## Recommendation

Do not add upstream code or install upstream service. Add this refresh as Phase 4 candidate evidence and use it to strengthen the next local-only `WAPI-V001` write API threat model.

Next safe AMN2-facing work:

```text
task: WAPI-V001 threat model
scope: docs/local-only
inputs:
  - operation lock per server/protocol
  - atomic write + backup-before-write
  - status/expiresAt lifecycle contract
  - QR/vpn import as secret-read
  - rate-limit/public-route hardening requirements
blocked:
  - live peer writes
  - config delivery route exposure
  - public API 3040
  - backup/import/reboot
```
