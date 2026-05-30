# Scoped API Tokens для `amn2`: design spec

## Назначение

`Scoped API Tokens` - кандидатный design artifact для `amn2`, который описывает безопасную модель API-токенов для интеграций, CI, мониторинга и ограниченных операторских сценариев.

Spec возник из анализа `PRVTPRO/Amnezia-Web-Panel`, но не переносит upstream token implementation, route guards или storage layout. Upstream имеет license verdict `GPL-3.0`, поэтому для `amn2` допустима только самостоятельная реализация идеи после отдельного review в репозитории `amn2`.

Цель design spec: заменить модель "bearer token как второй admin password" на scoped, auditable, expiring и revocable token model, связанную с `Route Policy Matrix` и `RemoteOperationRunner`.

## Контекст и проблема

API-токены полезны для:

- мониторинга;
- CI/CD и health checks;
- внешних admin tools;
- support tooling;
- automation для read-only или ограниченных write operations;
- будущих integrations.

Но broad bearer token без scopes и срока жизни создает слишком широкий blast radius:

- leaked token может выполнять admin-equivalent actions;
- token невозможно ограничить read-only задачей;
- destructive operations могут запускаться из automation без отдельного gate;
- revoke и rotation становятся ручной дисциплиной, а не свойством системы;
- audit показывает "token used", но не объясняет, какие права были выданы и почему request разрешен.

`Scoped API Tokens` должны быть отдельной auth method для integration surface, а не полным заменителем browser session.

## Scope

Входит в scope:

- token lifecycle;
- token format;
- hash storage;
- prefix/fingerprint для UI и audit;
- scopes;
- expiry;
- revoke и rotation;
- owner inheritance;
- route policy integration;
- destructive operation restrictions;
- audit events;
- rate limiting;
- test strategy.

Не входит в scope этого spec:

- конкретный криптографический API языка `amn2`;
- UI-детали token creation form;
- OAuth/OIDC;
- machine-to-machine federation;
- billing/API marketplace;
- long-lived public share links, для них нужен отдельный spec.

## Основные принципы

1. Raw token показывается только один раз при создании.
2. В хранилище лежит только сильный hash токена, не plaintext.
3. Token всегда имеет owner-а.
4. Token всегда имеет explicit scopes.
5. Token всегда имеет expiry.
6. Disabled или demoted owner отзывает token effective access.
7. Destructive operations требуют отдельного scope и отдельного route/operation gate.
8. Token use создает audit event для sensitive operations.
9. Token не должен давать больше прав, чем owner может иметь через policy.
10. Token model не должна зависеть от конкретного route handler-а.

## Token actor model

Token request превращается в actor:

```text
TokenActor
  type: token
  token_id: stable internal id
  owner_user_id: user who created or owns token
  owner_role_snapshot: role at validation time
  auth_method: bearer-token
  scopes: effective scopes after owner inheritance
  token_prefix: non-secret prefix for audit/UI
```

Важно: `owner_role_snapshot` не означает, что роль фиксируется навсегда. При каждом request effective access пересчитывается по текущему owner state.

## Token storage record

Минимальная запись:

```text
ApiTokenRecord
  id: stable internal id
  name: operator-visible label
  owner_user_id
  token_hash
  token_prefix
  scopes
  created_at
  expires_at
  last_used_at
  last_used_ip_hash
  revoked_at
  revoked_by
  revoke_reason
  created_from_request_id
```

Не хранить:

- raw token;
- full Authorization header;
- plaintext secret material;
- request body, в котором мог быть секрет.

Если в `amn2` появится отдельное secret storage, token hashes лучше хранить отдельно от обычного application state или как минимум исключать из raw backup по умолчанию.

## Token format

Рекомендуемая форма:

```text
amn2_<public_prefix>_<random_secret>
```

Требования:

- `public_prefix` короткий и не является секретом;
- `random_secret` генерируется криптографически безопасным RNG;
- общий entropy должен быть достаточным для offline guessing resistance;
- token должен иметь version marker, чтобы можно было менять формат;
- token parsing не должен раскрывать, существует ли prefix.

В UI показывать:

- name;
- prefix;
- owner;
- scopes;
- created_at;
- expires_at;
- last_used_at;
- revoked status.

Raw token показывать только в момент создания.

## Hashing

Минимальная модель:

- hash raw token перед сохранением;
- сравнение constant-time;
- optional server-side pepper из production secret;
- token lookup по prefix, затем constant-time compare hash кандидатов;
- не логировать lookup failures с raw token.

Если token hash хранится в обычной базе, pepper должен быть вне базы. При потере pepper все токены становятся недействительными, это acceptable security trade-off при documented recovery.

## Scopes

Scope names должны совпадать с `Route Policy Matrix`.

Базовый набор:

```text
servers:read
servers:write
connections:read
connections:write
configs:read
operations:run
operations:destructive
settings:read
settings:write
tokens:manage
backup:read
backup:restore
```

Правила:

- token без scopes не создается;
- wildcard scopes не вводить на первом этапе;
- `operations:destructive` не включается автоматически вместе с `operations:run`;
- `configs:read` считается secret-read scope;
- `backup:read` и `backup:restore` считаются high-risk scopes;
- `tokens:manage` не должен позволять token-у повышать собственные scopes.

## Expiry и rotation

Каждый token имеет `expires_at`.

Рекомендуемые defaults:

- read-only monitoring token: до 90 дней;
- integration write token: до 30 дней;
- destructive-capable token: до 7 дней или запрещен без отдельного product decision;
- bootstrap/setup token: minutes, одноразовый.

Rotation flow:

1. Создать новый token с нужными scopes.
2. Показать raw token один раз.
3. Audit: `api_token.created`.
4. Старый token revoke после проверки интеграции.
5. Audit: `api_token.revoked`.

Auto-renew без operator action не входит в первый design.

## Owner inheritance

Effective access токена зависит от текущего owner-а:

- disabled owner -> token denied;
- deleted owner -> token denied или token revoked migration;
- owner role downgraded -> token denied для scopes, которые новая роль не может иметь;
- owner loses admin/support eligibility -> token denied для operator scopes;
- owner password reset не обязан отзывать token автоматически, но может быть policy option;
- owner MFA reset или suspected compromise должен иметь bulk revoke option.

Это защищает от ситуации, где пользователь потерял права, но старый token продолжает работать.

## Route Policy Matrix integration

При request с `Authorization: Bearer`:

1. Extract token without logging raw value.
2. Resolve token record by prefix.
3. Constant-time hash compare.
4. Check revoked/expired.
5. Load owner state.
6. Compute effective scopes.
7. Build `TokenActor`.
8. Ask `Route Policy Matrix`: allowed auth method, role, required scopes, risk class, ownership.
9. Emit audit for denied sensitive request, if policy requires.

Route handler не должен проверять scopes вручную. Он получает уже authorizable actor или отказ.

## Destructive operations

Bearer token может запускать destructive operation только если одновременно выполнено:

- route policy разрешает `bearer-token`;
- token имеет `operations:destructive` или более конкретный destructive scope;
- owner role допускает destructive action;
- operation имеет plan preview;
- confirmation привязан к plan hash или operation id;
- audit event создан до выполнения.

На первом этапе допустимое product decision: полностью запретить destructive operations для bearer tokens. Тогда `operations:destructive` остается reserved scope и не выдается.

## Audit events

Audit обязателен для:

- token created;
- token revoked;
- token expired rejection for sensitive route;
- token used for `secret-read`;
- token used for `state-write`;
- token used for `remote-exec`;
- token denied due missing scope;
- token denied due owner disabled/demoted;
- token failed validation after rate threshold.

Audit payload:

```text
ApiTokenAuditEvent
  event_type
  token_id
  token_prefix
  owner_user_id
  actor_id
  route_policy_id
  required_scopes
  granted_scopes
  risk_class
  decision
  denial_reason
  request_id
  ip_hash
  created_at
```

Audit payload не содержит raw token, Authorization header или response body.

## Rate limiting

Нужны отдельные лимиты:

- failed token validation by prefix/IP;
- missing/invalid bearer header;
- token use for secret-read endpoints;
- token use for remote-exec/destructive endpoints;
- token creation/revoke actions.

Rate limit responses не должны раскрывать, существует ли token prefix.

## Backup и export

По умолчанию backup должен быть redacted:

- не содержит raw tokens;
- может содержать token metadata без hash;
- может содержать revoked/created audit metadata;
- token hashes включаются только в encrypted full backup, если это вообще нужно product decision-ом.

Restore не должен неожиданно оживлять старые tokens. Без отдельного решения restore либо инвалидирует все tokens, либо требует explicit "restore token hashes" dangerous mode.

## UI/API behavior

Token creation response:

```text
CreateTokenResult
  token_id
  raw_token: shown once
  prefix
  scopes
  expires_at
```

Token list response:

```text
TokenListItem
  token_id
  name
  prefix
  scopes
  owner
  created_at
  expires_at
  last_used_at
  revoked_at
```

Token list не возвращает hash и raw token.

Token revoke должен быть idempotent: повторный revoke возвращает нормальный результат без восстановления token.

## Test strategy

Минимальные тесты:

- raw token показывается только в create response;
- token hash сохраняется, raw token в storage отсутствует;
- wrong token не проходит;
- revoked token не проходит;
- expired token не проходит;
- disabled owner invalidates token;
- demoted owner loses effective access;
- token without required scope denied;
- token with required scope allowed for matching policy;
- token with `operations:run` denied for destructive endpoint;
- destructive endpoint denied without confirmation even with destructive scope;
- `configs:read` request создает audit event;
- missing scope denial создает audit event для sensitive route;
- Authorization header не попадает в logs/audit/errors;
- last_used_at обновляется с throttling, чтобы не писать storage на каждый request;
- token list не возвращает raw token или hash;
- backup redacted не содержит token_hash;
- restore redacted не оживляет tokens.

Aggregate tests:

- каждый scope из token model используется или зарезервирован в route policy;
- каждый bearer-token route имеет required scopes;
- no wildcard scopes in first implementation;
- no token has expiry absent;
- no destructive route allows bearer-token без explicit product decision.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Открыть текущий `amn2` и найти существующие tokens, API keys или integration auth.
2. Составить route inventory через `Route Policy Matrix`.
3. Утвердить минимальный набор scopes, который реально нужен первым integrations.
4. Ввести token record и hash storage.
5. Добавить create/list/revoke без подключения к risky routes.
6. Подключить read-only route с `servers:read` или аналогом.
7. Добавить secret-read route только после audit/redaction tests.
8. State-write и remote-exec scopes подключать после `RemoteOperationRunner`.
9. Destructive scopes оставить reserved до отдельного product/security decision.

## Решение для lab

Статус: `design-candidate`.

Этот spec является третьим foundational artifact после `RemoteOperationRunner` и `Route Policy Matrix`. До просмотра текущего `amn2` он остается research/design документом, а не задачей на немедленную реализацию.

## Источники

- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- API surface deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-api-surface.md](../../../research/upstreams/prvtpro-amnezia-web-panel-api-surface.md)
- Route Policy Matrix spec: [docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md](2026-05-30-route-policy-matrix-design.md)
- RemoteOperationRunner spec: [docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md](2026-05-30-remote-operation-runner-design.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
