# API Token Rotation/Revoke Policy

Дата: 2026-06-01.

Назначение: зафиксировать следующий safety gate для scoped API tokens и Local Agent tokens после первого storage/auth slice в `amn2`.

Этот документ не является implementation plan. Он не добавляет `/api/*` routes, не меняет `amn2`, не включает `config:read`, не расширяет Local Agent до clients/configs и не требует live VPS. Его цель - определить, какие lifecycle-правила должны быть выполнены до подключения token auth к новым API/controller routes.

## Current production baseline

В `amn2` уже есть первый local-gate slice:

```text
commit: 1fdcde5 Add scoped API token storage contract
docs: docs/API_TOKEN_POLICY.ru.md
service: app/services/api_tokens.py
storage: app/db/schema.py, app/db/repositories.py
tests: tests/services/test_api_tokens.py, tests/db/test_repositories.py
```

Текущий contract:

- `api_tokens` table хранит `token_hash`, `scopes_json`, `expires_at`, `revoked_at`, `last_used_at`;
- raw API token возвращается только через `ApiTokenIssue.raw_token`;
- safe metadata не содержит raw token или hash;
- allowed first-slice scopes: `server:read`, `metrics:read`;
- `config:read`, write, remote-exec и destructive scopes отклоняются;
- `/api/*` routes пока не добавлены;
- live VPS behavior не менялся.

Local Agent baseline отдельно содержит hash-only bearer token validation для scopes:

```text
agent:health
agent:read
agent:protocols:read
```

Local Agent token не должен автоматически становиться external API token. Это разные trust channels.

## Decision

Status: `policy-prepared-local-docs`.

Следующий production implementation по API tokens должен быть lifecycle/policy slice, а не endpoint expansion.

Минимальный безопасный порядок:

1. Зафиксировать token route policy для будущих read-only endpoints.
2. Сделать explicit expiry policy обязательной для tokens, которые реально используются route handlers.
3. Добавить revoke/rotation semantics на уровне service/API, не только storage flag.
4. Добавить owner inheritance или explicit service-owner exception.
5. Только после этого подключать `server:read` / `metrics:read` к read-only routes.

## Token classes

| Token class | Purpose | First allowed scopes | Boundary |
| --- | --- | --- | --- |
| `api-integration-token` | External or automation access to future `/api/*` | `server:read`, `metrics:read` | No config, no write, no remote-exec |
| `local-agent-token` | Controller-to-local-agent read-only calls | `agent:health`, `agent:read`, `agent:protocols:read` | Local-only, no external API reuse |
| `public/share-token` | Future public/self-service config access | none in this slice | Separate secret-read gate |
| `bootstrap-token` | Future setup/enrollment | none in this slice | Short TTL, one-time, separate design |

Do not merge these token classes into one broad bearer credential.

## Scope policy

Allowed now:

```text
server:read
metrics:read
agent:health
agent:read
agent:protocols:read
```

Blocked until separate gates:

```text
config:read
configs:read
server:write
metrics:write
operations:run
operations:destructive
backup:read
backup:restore
tokens:manage
agent:clients:read
agent:configs:read
agent:*:write
```

Rules:

- no wildcard scopes in first implementation;
- every bearer-token route must have an explicit required scope;
- route handlers must not inspect scopes ad hoc; they should use the route/auth policy layer;
- `metrics:read` means aggregate/default-safe metrics only until detailed metrics policy is implemented;
- `server:read` means operational metadata only, not config paths, peer keys, endpoints or remote command output;
- `agent:*` scopes remain Local Agent only and are not valid external `/api/*` scopes.

## Expiry policy

Storage can represent `expires_at = null`, but route-connected tokens should not use no-expiry behavior.

Recommended route-connected defaults:

| Token purpose | Max TTL | Notes |
| --- | --- | --- |
| Monitoring / read-only metrics | 90 days | `metrics:read`, aggregate only |
| Server/runtime read-only integration | 90 days | `server:read`, no topology-sensitive fields by default |
| Local Agent read-only token | 30 days | Shorter because token reaches local runtime adapter |
| Write/remote/destructive capable token | blocked | Requires separate decision, preview/confirmation and live VPS gate |
| Bootstrap/enrollment token | minutes | One-time, not part of current slice |

Expired tokens must fail closed. Error text must be generic to callers, while internal audit can record `expired_token` without raw token.

## Revoke policy

Revoke is immediate from the perspective of future route auth:

- revoked token cannot authenticate even if TTL remains valid;
- repeated revoke should be idempotent at API/service boundary;
- low-level storage may return "already revoked", but user-facing behavior should not restore or rotate the token;
- revoke must not delete audit history;
- revoke metadata should include `revoked_at`, actor, reason and request id when those actor models exist;
- bulk revoke is required before any multi-operator or owner-demotion model goes live.

Revoke does not rotate peer keys, configs or Local Agent runtime state. If a token had access to secret-bearing future surfaces, incident response must include a separate secret/config rotation note.

## Rotation policy

Rotation is create-new-then-revoke-old:

1. Create a new token with explicit scopes and expiry.
2. Show raw token once.
3. Audit `api_token.created` without raw token or hash.
4. Operator updates the integration.
5. Revoke the old token.
6. Audit `api_token.revoked`.

Do not support in-place raw token replacement. A token id should represent one credential lifecycle.

Auto-renew is out of scope for the first API/controller integration. If introduced later, it must still create a new token record and leave auditable lineage.

## Owner inheritance

Current storage allows `owner_user_id` to be nullable. That is acceptable for first storage groundwork, but route-connected tokens need one of two explicit models:

| Model | When to use | Requirement |
| --- | --- | --- |
| User-owned token | Admin/operator creates integration token | effective access recalculated from current owner state |
| Service-owned token | Monitoring or local controller token without a DB user | explicit service owner label, narrow scopes, short TTL, separate revoke command |

For user-owned tokens:

- disabled owner -> token denied;
- deleted owner -> token denied or revoked by migration;
- demoted owner -> scopes above new privileges denied;
- suspected compromise -> bulk revoke option;
- owner password reset may optionally trigger revoke, but the policy decision must be explicit.

For service-owned tokens:

- `owner_label` is not enough for privilege escalation;
- scopes must remain read-only in first implementation;
- expiry is mandatory;
- creation must be operator-only and audited.

## Backup/restore policy

Redacted backup default:

- include token metadata only if needed for audit/history;
- exclude raw tokens;
- exclude token hashes by default;
- include revoked/created audit metadata only without usable credential material.

Restore default:

- restored redacted backup must not revive usable tokens;
- full encrypted restore of token hashes is a dangerous explicit mode, not default;
- if hashes are restored, operator must rotate/revoke tokens after restore unless product decision says otherwise.

## Audit and logging policy

Audit may include:

```text
token_id
token prefix/fingerprint if implemented
owner_user_id or service owner label
scopes
route_policy_id
required_scope
decision
denial_reason
request_id
ip_hash
```

Audit/logs must not include:

```text
raw token
Authorization header
token_hash
request body containing secrets
.conf
QR payload
vpn:// link
private key
PSK
Local Agent raw bearer token
remote command stdout/stderr with secret material
```

Failed token validation must not reveal whether a token id, prefix or owner exists.

## Rate-limit policy

Before exposing bearer-token routes, add policy for:

- invalid bearer token attempts by IP/request fingerprint;
- repeated missing-scope attempts;
- token creation/revoke attempts;
- secret-read and remote-operation attempts, when those scopes exist later.

Rate-limit responses must be generic and must not leak token existence.

## Required implementation tests

Before connecting API tokens to any route, implementation plan must include tests that:

- token without expiry is rejected for route-connected creation;
- wrong token fails with generic response;
- expired token fails closed;
- revoked token fails closed;
- repeated revoke is idempotent at service/API boundary;
- token with `metrics:read` cannot access `server:read`;
- token with `server:read` cannot access `metrics:read`;
- `config:read`, write, remote-exec and destructive scopes cannot be created in first route-connected slice;
- disabled/demoted owner loses effective access, or service-owned token is explicitly narrow and expiring;
- token list never returns raw token or token hash;
- audit for create/revoke/denial contains safe metadata only;
- logs/errors never include `Authorization` header or raw token;
- redacted backup does not contain token hashes;
- redacted restore does not revive usable tokens.

For Local Agent tokens, tests must additionally prove:

- `agent:*` scopes cannot authorize external `/api/*` routes;
- external API scopes cannot authorize Local Agent routes;
- Local Agent token is not logged in audit or errors;
- Local Agent clients/configs/write lifecycle remain unavailable.

## First safe implementation boundary after this policy

Recommended next code boundary, after VPS evidence or as a local-only policy implementation:

```text
route-connected scoped API token lifecycle gate
```

It may include:

- token creation/list/revoke service boundary;
- explicit expiry requirement for route-connected tokens;
- route policy binding tests for `server:read` and `metrics:read`;
- audit-safe metadata checks.

It must not include:

- `/api/configs/*`;
- config downloads;
- per-peer detailed metrics;
- Local Agent clients/configs;
- remote apply/revoke;
- backup/import;
- broad admin-equivalent bearer token.
