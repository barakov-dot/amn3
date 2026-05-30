# Route Policy Matrix для `amn2`: design spec

## Назначение

`Route Policy Matrix` - кандидатный design artifact для `amn2`, который фиксирует правила доступа к API до реализации или изменения endpoint-ов.

Spec возник из анализа `PRVTPRO/Amnezia-Web-Panel`, но не переносит upstream route layout, handlers или код. Upstream имеет license verdict `GPL-3.0`, поэтому для `amn2` допустима только самостоятельная реализация идеи после отдельного review в репозитории `amn2`.

Цель design spec: сделать authorization, auth methods, risk classes, scopes, audit и test requirements явной таблицей, чтобы API не рос как набор локальных проверок внутри handler-ов.

## Контекст и проблема

VPN/control-panel API обычно имеет несколько разных поверхностей:

- HTML/UI routes;
- admin API;
- support/operator API;
- user self-service API;
- public share links;
- integration API через bearer tokens;
- internal callbacks или background jobs.

Без общей policy matrix быстро появляются слабые места:

- один endpoint принимает session cookie, другой bearer token, третий public token, но это не видно из документации;
- роль `support` случайно получает destructive action;
- обычный user может прочитать чужой config из-за неполной ownership-проверки;
- public link становится secret-read surface без expiry и audit;
- API docs описывают группы endpoint-ов, но не доказывают, что guards совпадают с design;
- tests проверяют success, но не forbidden access.

`Route Policy Matrix` должна быть обязательным источником правды для route guards и access tests.

## Scope

Входит в scope:

- структура policy matrix;
- auth method taxonomy;
- role and actor model;
- risk classes для API operations;
- связь со scopes для API tokens;
- ownership rules;
- audit requirements;
- confirmation/dry-run requirements;
- test matrix для access control;
- процесс изменения policy.

Не входит в scope этого spec:

- конкретный web framework;
- конкретные route paths текущего `amn2`;
- реализация middleware/dependencies;
- UI для управления ролями;
- полная модель scoped API tokens, она должна получить отдельный spec.

## Основные принципы

1. Каждый non-public endpoint должен иметь запись в policy matrix.
2. Public endpoint тоже должен иметь запись, если он выдает config, token, secret или sensitive metadata.
3. Route handler не должен сам изобретать authorization rule.
4. Policy matrix должна указывать не только "кто может", но и "почему можно безопасно".
5. Risk class endpoint-а должен совпадать с требованиями `RemoteOperationRunner`, если endpoint запускает remote operation.
6. API docs, tests и guards должны выводиться из одной policy или проверяться против нее.
7. Любое изменение policy требует обновления tests.

## Auth method taxonomy

Минимальный набор auth methods:

| Auth method | Назначение | Где допустимо | Особый риск |
| --- | --- | --- | --- |
| `session` | browser/admin UI | UI и operator API | CSRF/session lifetime |
| `bearer-token` | integrations, CI, automation | integration API и ограниченные admin actions | scopes, expiry, revoke |
| `user-session` | self-service | user-owned resources | ownership boundary |
| `public-share-token` | выдача config по ссылке | строго ограниченный delivery surface | expiry, brute force, leakage |
| `internal-job` | background worker callbacks | internal execution only | spoofing и replay |
| `bootstrap-token` | first-run setup | только bootstrap flow | одноразовость и срок жизни |

Endpoint может поддерживать несколько auth methods, но каждая комбинация должна быть явно перечислена. Если bearer-token разрешен там же, где session admin, это должно быть осознанным решением, а не побочным эффектом guard-а.

## Role and actor model

Policy должна различать:

- `admin` - полный operator, но destructive actions все равно требуют confirmation и audit;
- `support` - ограниченный operator без доступа к secrets и destructive operations по умолчанию;
- `user` - владелец своих connections/configs;
- `integration` - bearer token actor со scopes;
- `public` - anonymous actor с public token или одноразовой ссылкой;
- `system` - internal worker, scheduler, migration или maintenance actor.

Actor должен сохраняться в audit payload как stable identifier:

```text
Actor
  type: user | token | public-link | system
  id: stable internal id
  role: admin | support | user | integration | public | system
  auth_method: session | bearer-token | user-session | public-share-token | internal-job | bootstrap-token
```

## Endpoint policy record

Каждый endpoint описывается записью:

```text
RoutePolicy
  id: stable policy id, например "servers.install_protocol"
  method: GET | POST | PATCH | DELETE
  path_pattern: framework-neutral path pattern
  surface: ui | admin-api | support-api | self-service | public-share | integration | internal
  allowed_auth_methods: explicit list
  allowed_roles: explicit list
  required_scopes: list for bearer-token actors
  ownership_rule: none | server-owner | connection-owner | user-self | token-owner | custom
  risk_class: read-only | secret-read | state-write | remote-exec | destructive
  remote_operation_id: optional link to RemoteOperationRunner contract
  confirmation_required: boolean
  dry_run_required: boolean
  audit_required: boolean
  rate_limit_policy: none | login | token | public-link | remote-operation
  response_secret_policy: no-secrets | redacted | secret-download | one-time-secret
  tests_required: explicit test ids
```

`path_pattern` не должен быть единственным идентификатором policy, потому что route path может измениться. Stable `id` нужен для tests, audit и changelog.

## Risk classes

Route-level risk class должен совпадать с доменной операцией:

| Класс | Endpoint examples | Требования |
| --- | --- | --- |
| `read-only` | list servers, status, health | auth, ownership где нужно, rate limit где нужно |
| `secret-read` | download config, show one-time token | stronger role/scope, audit, response secret policy |
| `state-write` | rename server, toggle user flag | validation, audit, ownership |
| `remote-exec` | restart service, install protocol | RemoteOperationRunner, plan, audit, timeout |
| `destructive` | clear server, delete protocol, restore backup | confirmation, dry-run или preview, audit before/after, recovery note |

Если endpoint вызывает `RemoteOperationRunner`, его `risk_class` не может быть мягче, чем risk class remote operation.

## Scopes для bearer tokens

До отдельного token spec можно использовать базовые scope families:

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

Правило: bearer token без explicit scope не должен проходить. Admin-equivalent bearer token без scopes считается rejected production model.

Destructive endpoint требует отдельный scope вроде `operations:destructive` даже если token уже имеет `operations:run`.

## Ownership rules

Self-service и public delivery routes требуют отдельной ownership policy:

- `user-self` - actor может читать или менять только свой user record;
- `connection-owner` - actor может читать config только для assigned connection;
- `server-owner` - если в `amn2` появится ownership серверов;
- `token-owner` - token actor не может управлять токенами другого owner-а;
- `public-link-bound` - public token дает доступ только к связанной заранее выборке configs.

Custom ownership rule допустим, но должен иметь отдельный test id и короткое описание.

## Audit requirements

Audit обязателен для:

- `secret-read`;
- `state-write`;
- `remote-exec`;
- `destructive`;
- login failures после rate threshold;
- token create/revoke;
- backup download/restore;
- share link create/revoke/use for config download;
- role or scope changes.

Audit payload должен включать:

```text
AuditAccessEvent
  route_policy_id
  actor
  auth_method
  server_id or resource_id
  risk_class
  decision: allowed | denied
  denial_reason
  remote_operation_id
  request_id
  created_at
```

Audit payload не должен содержать raw config, token, password, private key или full request body.

## Confirmation и dry-run

Правила:

- `destructive` always requires confirmation.
- `remote-exec` requires plan preview, если операция меняет remote state.
- `secret-read` не требует dry-run, но требует explicit response secret policy.
- `backup:restore` считается destructive.
- raw config save считается destructive или high-risk state-write, пока нет schema validation и rollback.

Confirmation должен быть привязан к конкретному plan hash или operation id, чтобы нельзя было подтвердить одно действие, а выполнить другое.

## Policy lifecycle

Изменение API должно идти так:

1. Добавить или изменить `RoutePolicy`.
2. Добавить forbidden-access tests для всех недопустимых ролей и auth methods.
3. Добавить allowed-access test для разрешенного actor-а.
4. Добавить ownership tests, если endpoint работает с user-owned ресурсом.
5. Добавить audit assertion для risk class, где audit обязателен.
6. Сверить OpenAPI/docs с policy.
7. Только после этого менять route handler.

Если endpoint существует без policy record, build/test gate должен падать.

## Пример policy table

Пример не является утвержденным API `amn2`; он показывает формат будущей матрицы.

| Policy id | Surface | Auth | Roles/scopes | Risk | Ownership | Audit | Extra gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `servers.list` | admin-api | session, bearer-token | admin/support, `servers:read` | read-only | none | optional | rate limit |
| `connections.my_config` | self-service | user-session | user | secret-read | connection-owner | required | response redaction |
| `share.config_download` | public-share | public-share-token | public | secret-read | public-link-bound | required | expiry/rate limit |
| `protocol.install` | admin-api | session, bearer-token | admin, `operations:run` | remote-exec | none | required | operation plan |
| `server.clear` | admin-api | session, bearer-token | admin, `operations:destructive` | destructive | none | required | plan hash confirmation |
| `settings.backup_restore` | admin-api | session | admin | destructive | none | required | schema validation |

## Test strategy

Минимальный test set для каждого endpoint:

- anonymous denied, кроме явно public routes;
- wrong role denied;
- wrong auth method denied;
- bearer token without scope denied;
- disabled token denied;
- user cannot access another user's resource;
- public share token cannot access unbound resource;
- destructive endpoint without confirmation denied;
- confirmed destructive endpoint links to plan hash;
- required audit event is emitted for allow and deny where policy says so;
- secret-read response follows `response_secret_policy`;
- OpenAPI/docs group matches route surface.

Минимальный aggregate test set:

- every registered route has policy;
- every policy id maps to an existing route;
- no policy has empty `allowed_auth_methods`;
- no bearer-token policy has empty `required_scopes`;
- no destructive policy has `confirmation_required=false`;
- no secret-read policy has `audit_required=false`;
- no public-share policy lacks rate limit and expiry requirement.

## Связь с RemoteOperationRunner

`Route Policy Matrix` отвечает за вопрос "имеет ли actor право начать операцию".

`RemoteOperationRunner` отвечает за вопрос "как безопасно спланировать и выполнить операцию".

Связка:

- route policy определяет `risk_class`, `required_scopes`, `confirmation_required`, `dry_run_required`;
- route handler создает request к domain service только после policy allow;
- domain service строит `RemoteOperation`;
- runner валидирует operation contract;
- audit связывает `route_policy_id` и `remote_operation_id`.

Если route policy и remote operation расходятся по risk class, выполнение блокируется.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Открыть текущий `amn2` и собрать список route handlers.
2. Разделить routes по surfaces: admin, support, self-service, public, integration, internal.
3. Для каждого route назначить stable `policy_id`.
4. Заполнить risk class и audit requirement.
5. Добавить policy coverage test: каждый route имеет policy.
6. Добавить forbidden-access tests для самых рискованных routes.
7. Подключить bearer token scopes только после отдельного scoped token spec.
8. Связать remote-exec/destructive routes с `RemoteOperationRunner`.

## Решение для lab

Статус: `design-candidate`.

Этот spec можно использовать как второй foundational artifact после `RemoteOperationRunner`. До просмотра текущего `amn2` он остается research/design документом, а не задачей на немедленную реализацию.

## Источники

- API surface deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-api-surface.md](../../../research/upstreams/prvtpro-amnezia-web-panel-api-surface.md)
- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- RemoteOperationRunner spec: [docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md](2026-05-30-remote-operation-runner-design.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
