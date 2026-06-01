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
- если token привязан к `owner_user_id`, текущий owner status должен оставаться `active`.

Safe audit metadata содержит только `token_id`, `name`, `owner_label` и scopes.

## Lifecycle gate

Второй local-only slice добавляет lifecycle boundary до подключения токенов к маршрутам:

- `create_route_api_token()` требует явный `expires_at` для route-connected токенов;
- `revoke_api_token()` возвращает idempotent safe event: повторный revoke не раскрывает, существовал ли usable token;
- `rotate_api_token()` использует create-new-then-revoke-old: новый token получает отдельный id и raw token показывается только один раз;
- `rotated_from_token_id` хранит lineage без raw token и без token hash в safe metadata;
- `revoke_reason` хранит причину отзыва без удаления audit history;
- user-owned token наследует статус владельца: `blocked`/`deleted` owner не проходит auth.

Safe lifecycle metadata не содержит raw token, Authorization header, token hash, `.conf`, QR payload, `vpn://`, private key, PSK или remote command output.

## VPS Gate

VPS gate не нужен для этого slice: нет routes, нет live write flow, нет peer apply/revoke/config/sync/runtime changes.

VPS gate понадобится только когда API начнет вызывать real remote operations или читать/выдавать live secret-bearing config artifacts.
