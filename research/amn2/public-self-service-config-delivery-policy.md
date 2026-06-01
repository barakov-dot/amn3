# Политика public/self-service выдачи конфигов

Дата: 2026-06-01.

Назначение: зафиксировать policy boundary для будущей self-service/public выдачи `.conf`, QR, `vpn://` и других client config artifacts в `amn2`.

Этот документ не является implementation plan. Он не меняет `amn2`, не добавляет public routes, не включает API `config:read`, не меняет текущие bot/email flows, не читает `.env`, не требует live VPS и не переносит код из PRVTPRO/Amnezia-Web-Panel. Он переводит уже существующий широкий design spec в конкретный gate для текущего verified `amn2` baseline.

## Current production baseline

Текущие опорные artifacts:

```text
research/amn2/config-delivery-inventory.md
research/amn2/route-policy-matrix.md
research/amn2/secret-surface-inventory.md
research/amn2/manager-config-export-contract.md
docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md
```

В `amn2` уже есть безопасные строительные блоки:

- `build_device_config_delivery()` восстанавливает config из encrypted device secrets;
- `ConfigDeliveryPackage` содержит `.conf` bytes, QR PNG, QR payload text, `vpn://` import link and artifact metadata;
- `vpn://`, QR payload/PNG and `.conf` are classified as `client-config-secret`;
- email verification/recovery raw tokens are issued one-time and stored as hashes;
- Route/Auth Policy Matrix already marks public-token secret-read as TTL + one-time + purpose + audit + rate-limit candidate.

Current baseline still does not mean public/self-service download routes are ready. It only gives us the pieces needed to define the policy.

## Decision status

Status: `implemented-pushed-local-gate-complete`.

Decision: public/self-service config delivery remains blocked for routes, but the first no-route policy/contract slice exists. It defines policy records, share-token storage semantics and tests without exposing downloadable configs through a new route.

Implementation evidence:

```text
branch: codex/public-config-delivery-policy-contract
base: codex/manager-config-export-contract
commit: 2ef3af7 Add config share policy contract
focused local gate: 94 passed
full local suite: 577 passed, 1 StarletteDeprecationWarning
```

## Risk model

Every config delivery output is `secret-read`:

- raw `.conf` gives VPN access;
- QR PNG is a secret-bearing rendering, not a harmless image;
- QR payload text is the secret source for the PNG;
- `vpn://` reversibly encodes the full config;
- delivery message becomes secret-bearing if it embeds `vpn://`;
- generated config artifacts must not appear in audit, logs, metrics, diagnostics or redacted backups.

Public/self-service delivery adds extra risk:

- actor may be unauthenticated public token holder;
- token misuse can bypass the admin panel;
- link lifetime and revoke behavior become product security controls;
- wrong ownership checks can expose another user's device config;
- raw token, config body or import URI may leak through logs/errors.

## Delivery lanes

| Lane | Actor | First status | Policy |
| --- | --- | --- | --- |
| `self-service-session` | authenticated user | future, blocked | owned active devices only, audit required for secret download |
| `admin-issued-share` | web-admin / telegram-admin | future, blocked | admin can create/revoke bounded share, not download silently |
| `public-share-token` | public token holder | future, blocked | hash-only token, TTL, one-time or max downloads, generic denial |
| `public-email-recovery` | raw recovery token + verified email | current narrow baseline | keep as purpose-bound token flow, no raw token/config in audit |
| `integration-api-config-read` | scoped bearer token | future, blocked | requires explicit `config:read`, resource policy and audit |
| `local-agent-configs` | Local Agent/controller | future, blocked | requires separate Local Agent secret-read gate |

Default recommendation: public routes still remain blocked; the next step for this lane is a separate route-exposure gate, not automatic endpoint implementation.

## Route policy table

Future policy ids should be explicit:

| Policy id | Surface | Actor | Risk | Required gates |
| --- | --- | --- | --- | --- |
| `self.devices.list` | owned devices metadata | user-session | `read-only` | user active, ownership filter |
| `self.device.config_download` | owned device config | user-session | `secret-read` | ownership, active user/device, audit, rate limit |
| `admin.share.create` | create bounded share | admin-session | `state-write` + `token-raw issue` | CSRF/confirmation, target ownership, TTL, hash-only raw token issue |
| `admin.share.revoke` | revoke share | admin-session | `state-write` | CSRF/confirmation, audit, immediate denial |
| `share.config_download` | token config download | public-token | `public-token-secret-read` | hash lookup, purpose, TTL, one-time/max downloads, resource binding, audit, rate limit |
| `integration.config_download` | API config download | scoped-token | `secret-read` | `config:read`, resource policy, audit, rate limit |
| `agent.config_export` | Local Agent config export | local-agent | `secret-read` | blocked until separate agent config policy |

No existing admin route should become public/self-service by adding an optional token parameter.

## Share token contract

Conceptual storage model:

```text
ConfigShareToken
  id
  token_hash
  token_prefix
  purpose
  created_by_actor
  owner_user_id
  bound_device_ids
  bound_server_ids
  allowed_artifact_kinds
  target_client
  created_at
  expires_at
  revoked_at
  revoked_by_actor
  one_time
  max_downloads
  download_count
  last_used_at
  last_used_ip_hash
```

Storage rules:

- raw token is shown/sent once and never stored;
- `token_hash` is required and must not be included in redacted backup by default;
- `token_prefix` is display-only and insufficient for access;
- `expires_at` is required;
- `purpose` must be config-specific, not a generic public token;
- bound resources must be explicit;
- disabled user, revoked device or revoked server state denies access even if token is otherwise valid.

## Token lifecycle

Create:

- admin/session actor chooses user/device/resources;
- default expiry is short;
- one-time mode is preferred for high-risk delivery;
- raw token appears only in immediate response or outbound message;
- audit stores token id/prefix only.

Use:

- raw token is hashed and compared constant-time;
- wrong/expired/revoked/used token returns generic denial;
- successful download increments `download_count`;
- one-time token is consumed before or atomically with delivery decision;
- repeated failures are rate-limited.

Revoke:

- admin revoke sets `revoked_at` and preserves audit;
- user/device/server revoke makes linked tokens unusable;
- config credential rotation should invalidate affected shares;
- restore from redacted backup must not revive active public shares.

## Ownership and resource binding

Self-service:

- user can list/download only devices assigned to that user;
- disabled user cannot download configs;
- inactive/revoked device cannot be downloaded;
- request body/path cannot override `user_id`;
- user cannot enumerate device ids through error differences.

Public share:

- token is bound to a specific user/device set;
- token cannot be used to query arbitrary device ids;
- token cannot disclose whether another device exists;
- if multiple artifacts are allowed, each artifact kind must be in policy;
- share does not grant admin metadata.

Integration API:

- `server:read` and `metrics:read` do not imply config access;
- `config:read` requires separate route policy and resource filtering;
- broad admin-equivalent bearer tokens remain blocked.

## Artifact policy

All secret artifacts must pass through the manager export contract before a new route can serve them:

- artifact kind is explicit;
- target client is explicit;
- QR payload kind is explicit;
- payload is separate from safe metadata;
- safe metadata may include kind, filename, byte length and encoding;
- audit may not include payload, QR text/PNG, `vpn://`, private key or PSK.

Allowed first artifacts for future design:

| Artifact | Requirement |
| --- | --- |
| `.conf` download | UTF-8 byte equality test, no-cache response, audit without body |
| QR PNG | QR decode/payload equality test before route exposure |
| `vpn://` | decode round-trip, entire URI redacted |
| delivery message | safe if no import URI; secret-bearing if it embeds URI |

## Response policy

| Response policy | Meaning | Allowed before route implementation |
| --- | --- | --- |
| `redacted-preview` | metadata only | yes |
| `delivery-started` | external channel triggered, no payload in response | possible after channel-specific gate |
| `secret-download` | payload returned to actor | blocked until route policy/tests |
| `one-time-secret` | payload returned once and token consumed | blocked until share-token implementation/tests |

Secret download responses require:

- `Cache-Control: no-store`;
- no payload in logs;
- safe error categories;
- audit before/after decision;
- rate limit;
- no OpenAPI/example payload containing real config.

## Audit policy

Safe audit fields:

- event type;
- actor type/id where known;
- policy id;
- token id/prefix only;
- user id;
- device id;
- artifact kinds;
- target client;
- status: allowed/denied;
- denial category;
- request id;
- IP hash/prefix only after privacy review.

Forbidden audit fields:

- raw token;
- token hash;
- raw `.conf`;
- QR payload;
- QR PNG/base64;
- `vpn://`;
- rendered secret-bearing message text;
- private key;
- preshared key.

Minimum event names:

```text
config.self.download_allowed
config.self.download_denied
config.share.created
config.share.revoked
config.share.download_allowed
config.share.download_denied
config.integration.download_allowed
config.integration.download_denied
```

## Rate limit policy

Required before public route exposure:

- public token attempts by IP/prefix;
- share password failures if password is added;
- successful downloads per token;
- denied ownership attempts per authenticated user;
- share creation per admin and target user;
- API config downloads per token.

Public denial must not reveal whether token, user, device or share exists.

## Backup and restore policy

Redacted backup:

- excludes generated config artifacts;
- excludes raw share tokens;
- excludes token hashes by default;
- may include disabled/share metadata only if it cannot be used for access;
- restore must not revive active shares.

Encrypted full backup:

- may include share token hashes only after explicit dangerous backup decision;
- restore should prefer `restore-disabled` for shares unless product explicitly chooses restore-as-is;
- restored active shares must be audited and preferably rotated/reissued.

## Required tests before implementation

Policy/contract tests:

- public share without expiry rejected;
- raw token is returned once and never stored;
- only hash/prefix stored;
- disabled user denied;
- revoked device denied;
- expired token denied;
- revoked token denied;
- used one-time token denied;
- wrong purpose denied;
- token bound to device A cannot access device B;
- API token without `config:read` denied;
- `server:read`/`metrics:read` cannot download configs;
- audit contains safe metadata only.

Artifact tests:

- `.conf` bytes equal UTF-8 config text;
- non-ASCII names round-trip;
- `vpn://` decodes to original config;
- QR payload decodes to expected payload where tooling allows;
- raw config, QR payload and `vpn://` are redacted in logs/errors/audit.

Backup tests:

- redacted backup excludes generated configs;
- redacted backup excludes raw tokens;
- redacted backup excludes or disables share token hashes;
- restore redacted backup cannot produce usable public share.

Abuse tests:

- public denial responses are generic;
- rate-limit hook exists for failed token attempts;
- repeated wrong device ids do not reveal ownership boundaries.

## First safe implementation boundary

The first safe code slice, already moved from AMN3 docs to `amn2`, is:

```text
public/self-service config delivery policy registry and share-token contract
```

It includes:

- route policy entries without routes;
- share-token storage contract or schema proposal;
- token lifecycle service tests with no config payload returned;
- audit-safe metadata tests;
- backup/restore policy tests for share records;
- adapter dependency on `manager-config-export-contract.md` as a prerequisite.

It must not include:

- public download endpoint;
- self-service config download endpoint;
- API `config:read`;
- Local Agent `/configs`;
- generated config persistence;
- live VPS calls;
- QR/import behavior changes for users;
- copying PRVTPRO implementation.

## Current recommendation

Keep public/self-service config delivery routes blocked until:

1. product explicitly chooses which lane opens first;
2. route policy exists for that concrete route;
3. rate-limit implementation is connected to the route;
4. no-secret response/audit/log tests exist for the route;
5. ownership/resource policy is verified against real caller context.

Backup/import policy registry and restore-preview contract is now complete in `amn2/codex/backup-import-policy-contract`, commit `d2c160b`. If VPS is still not ready, the next local-only lane should be smaller: machine-checkable secret inventory registry, not public links or backup/import routes.
