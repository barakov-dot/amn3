# Scoped API Token Policy

Дата: 2026-06-01.

Этот документ фиксирует первый local-only slice для будущих external API tokens. Slice не добавляет `/api/*` endpoints, не меняет web/bot/agent runtime behavior и не трогает live VPS.

## First-slice contract

Разрешенные scopes первого slice:

- `server:read`;
- `metrics:read`.

Запрещено в первом slice:

- `config:read` - это future `secret-read` surface для `.conf`, QR и `vpn://`;
- любые `*:write`;
- destructive/remote-exec scopes;
- shared broad API key без scopes;
- хранение raw token в базе, audit metadata или logs.

## Storage

Таблица `api_tokens` хранит:

- `id` - стабильный token id для audit/revoke;
- `name` - operator label;
- `owner_user_id` и `owner_label`;
- `token_hash` - только `sha256:<digest>`, без raw token;
- `scopes_json` - отсортированный список scopes;
- `expires_at`;
- `revoked_at`;
- `last_used_at`;
- `created_at`.

Raw token возвращается только в момент выдачи через `ApiTokenIssue.raw_token`. Safe metadata содержит `raw_token_display=one-time` и не содержит raw token или token hash.

## Auth

`app.services.api_tokens.authenticate_api_token()` принимает raw bearer token, считает hash, проверяет:

- token exists;
- token not revoked;
- token not expired;
- required scope is present.

Safe audit metadata содержит только `token_id`, `name`, `owner_label` и scopes.

## VPS Gate

VPS gate не нужен для этого slice: нет routes, нет live write flow, нет peer apply/revoke/config/sync/runtime changes.

VPS gate понадобится только когда API начнет вызывать real remote operations или читать/выдавать live secret-bearing config artifacts.
