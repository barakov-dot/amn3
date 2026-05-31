# Design Specs Index + `amn2` Transfer Checklist

## Назначение

Этот документ связывает foundational design specs, подготовленные в `vpn-ops-lab`, с будущим решением о переносе идей в основной Amneziya/`amn2`.

Главная цель: не переносить функции из lab в production импульсивно. Сначала идея проходит license verdict, security/operational review, архитектурную проверку, тестовый план и только потом становится кандидатом на работу в `amn2`.

Документ не является implementation plan. Это навигационная карта и transfer gate.

## Текущий статус

Источник первой серии: `PRVTPRO/Amnezia-Web-Panel`.

License verdict upstream: `GPL-3.0`, режим `research-only`.

Правило переноса:

- код, route layout, manager scripts, config templates, UI и Dockerfile upstream не копируются;
- переносимыми считаются только самостоятельно сформулированные идеи, требования, test plans и safety gates;
- любой перенос в `amn2` требует отдельного review текущего кода `amn2`.

## Foundational specs

| Spec | Статус | Что закрывает | Первый возможный перенос в `amn2` |
| --- | --- | --- | --- |
| [RemoteOperationRunner](2026-05-30-remote-operation-runner-design.md) | `design-candidate-updated-after-amn2-inventory` | SSH/sudo/remote execution, dry-run, command policy, audit, redaction, consistency и recovery note | implementation plan для первого безопасного runner slice после review |
| [Route Policy Matrix](2026-05-30-route-policy-matrix-design.md) | `design-candidate` | route guards, auth methods, roles, scopes, risk classes, access tests | таблица текущих API endpoints |
| [Scoped API Tokens](2026-05-30-scoped-api-tokens-design.md) | `design-candidate` | one-time token display, hash storage, scopes, expiry, revoke, owner inheritance | read-only integration token после route matrix |
| [Secret Inventory + Backup Policy](2026-05-30-secret-inventory-backup-policy-design.md) | `design-candidate` | secret classes, inventory, redacted/full backup, restore, redaction, audit | secret inventory текущего state/storage |
| [Public/Self-service Config Delivery](2026-05-30-public-self-service-config-delivery-design.md) | `design-candidate-updated-after-prvtpro-config-integrity` | user-owned configs, public links, share token hash, expiry, revoke, audit, `.conf`/QR/`vpn://` integrity, manager export contract | artifact integrity tests для текущей выдачи configs |

## Зависимости между specs

Рекомендуемый порядок применения в `amn2`:

1. `Secret Inventory + Backup Policy`
2. `Route Policy Matrix`
3. `RemoteOperationRunner`
4. `Scoped API Tokens`
5. `Public/Self-service Config Delivery`

Почему так:

- secret inventory нужен, чтобы понимать, какие поля нельзя логировать, экспортировать и отдавать через API;
- route policy нужна, чтобы не спорить в каждом handler-е, кто имеет право на действие;
- remote runner нужен до опасных SSH/sudo операций;
- token scopes должны опираться на route policy;
- config delivery зависит от ownership, secret inventory, audit, route policy и artifact integrity tests.

Если в текущем `amn2` уже есть remote operations, можно параллельно начать с inventory remote actions для `RemoteOperationRunner`, но без немедленной переписи кода.

## Transfer statuses

При разборе каждой идеи использовать один из статусов:

| Статус | Значение |
| --- | --- |
| `lab-only` | идея остается исследованием, перенос не планируется |
| `ready-for-amn2-review` | идея достаточно ясна, чтобы открыть текущий `amn2` и проверить совместимость |
| `needs-amn2-context` | без кода `amn2` нельзя решить применимость |
| `ready-for-implementation-plan` | после review `amn2` можно писать implementation plan |
| `hybrid-only` | идея подходит будущему гибридному продукту, но не ближайшему `amn2` |
| `blocked-by-license` | нельзя переносить как код или derivative implementation |
| `blocked-by-risk` | риск выше пользы без отдельного redesign |
| `rejected-for-production` | подход нельзя использовать в production |

## `amn2` Transfer Checklist

### 1. Источник и лицензия

- Указан upstream source.
- Указана лицензия upstream.
- Зафиксировано, что именно изучалось: идея, UX, architecture, API surface, protocol flow, security pattern.
- Подтверждено, что код, configs, scripts, UI и тексты upstream не копируются.
- Для GPL-3.0 источника указан режим `research-only`.

Verdict:

```text
license_verdict: research-only | idea-only | compatible | blocked
copying_allowed: no | yes-after-legal-review
```

### 2. Граница идеи

- Описано, какую самостоятельную идею переносим.
- Описано, что не переносим.
- Есть ссылка на design spec в lab.
- Есть ссылка на конкретную проблему в `amn2`, если она уже известна.
- Нет зависимости от upstream implementation details.

Verdict:

```text
transfer_unit: principle | requirement | test-plan | design-spec | implementation
upstream_code_dependency: none | present-and-blocking
```

### 3. Польза для `amn2`

- Понятно, какую production-проблему решает идея.
- Понятно, кто выигрывает: admin, support, user, integration, maintainer.
- Есть критерий успеха.
- Есть причина, почему это нужно сейчас, а не в будущий гибрид.

Verdict:

```text
value: high | medium | low
target: amn2 | hybrid | both | lab-only
```

### 4. Risk class

Выбрать самый строгий класс:

- `read-only`
- `secret-read`
- `state-write`
- `read-only-remote`
- `read-only-remote-telemetry`
- `remote-state-write`
- `remote-exec`
- `destructive-remote`

Обязательные проверки:

- secret leakage risk;
- privilege escalation risk;
- remote server damage risk;
- backup/export risk;
- rollback/recovery risk;
- support burden.

Verdict:

```text
risk_class: read-only | read-only-remote | read-only-remote-telemetry | secret-read | state-write | remote-state-write | remote-exec | destructive-remote
risk_verdict: acceptable-with-tests | needs-redesign | blocked
```

### 5. Архитектурная совместимость

До implementation plan открыть текущий `amn2` и ответить:

- где сейчас лежит похожая ответственность;
- есть ли существующий auth/session/token layer;
- есть ли storage и secret handling;
- есть ли route organization;
- есть ли remote operation layer;
- есть ли audit/logging;
- есть ли tests, которые можно расширить;
- не раздувает ли идея scope `amn2`.

Verdict:

```text
architecture_fit: fits-existing-pattern | needs-small-adapter | needs-redesign | hybrid-only
```

### 6. Security requirements

Для любой идеи явно ответить:

- какие secrets появляются или читаются;
- какие roles/auth methods допускаются;
- нужны ли scopes;
- нужен ли audit;
- нужен ли rate limit;
- нужен ли dry-run или confirmation;
- что будет в backup/export;
- что будет в logs/errors.

Verdict:

```text
security_gate: pass | pass-with-conditions | fail
required_specs:
  - Secret Inventory + Backup Policy
  - Route Policy Matrix
  - RemoteOperationRunner
  - Scoped API Tokens
  - Public/Self-service Config Delivery
```

### 7. Test plan

Минимально указать:

- allowed access tests;
- forbidden access tests;
- ownership tests;
- secret redaction tests;
- audit assertions;
- failure tests;
- migration/restore tests, если есть state;
- fake runner tests, если есть remote operation.

Verdict:

```text
test_plan: sufficient | incomplete | missing
```

### 8. Rollback и recovery

Для `state-write`, `remote-state-write`, `remote-exec` и `destructive-remote`:

- есть recovery note;
- есть backup-before-write или preview;
- есть partial failure behavior;
- есть audit trail;
- понятно, что делать оператору после ошибки.

Verdict:

```text
recovery_gate: not-needed | documented | missing
```

### 9. Решение

Финальное решение фиксируется коротко:

```text
decision: transfer-to-amn2-design | transfer-to-amn2-plan | keep-in-lab | move-to-hybrid | reject
reason:
next_artifact:
owner:
```

## Быстрая матрица для текущих пяти specs

| Spec | License gate | Risk gate | `amn2` readiness | Следующий artifact |
| --- | --- | --- | --- | --- |
| RemoteOperationRunner | pass as idea-only | high, manageable with fake runner, command policy, audit and consistency tests | `ready-for-implementation-plan-review` | [first runner slice plan](../plans/2026-05-30-remote-operation-runner-first-slice.md) |
| Route Policy Matrix | pass as idea-only | medium, mostly design/test discipline | `ready-for-amn2-review` | route inventory |
| Scoped API Tokens | pass as idea-only | high, requires scopes/expiry/audit | `needs-amn2-context` | token/auth inventory |
| Secret Inventory + Backup Policy | pass as idea-only | high, foundational | `ready-for-amn2-review` | secret inventory |
| Public/Self-service Config Delivery | pass as idea-only | high, depends on ownership model | `needs-amn2-context` | config delivery inventory |

## Что делать перед открытием `amn2`

Подготовить короткий audit plan:

1. Найти все API routes.
2. Найти все secret-bearing fields.
3. Найти все places where configs are generated, stored or returned.
4. Найти все remote operations.
5. Найти auth/token/session code.
6. Найти backup/export/import logic.
7. Сопоставить найденное с пятью specs.

Цель первой проверки `amn2` - не править код сразу, а получить reality map.

Статус на 2026-05-30: первые route/auth, secret, config delivery и remote operations inventories уже собраны в `research/amn2/`. Следующий шаг для RemoteOperationRunner - не новый inventory, а review updated design и затем implementation plan для узкого безопасного slice.

## Что пока не переносить

Оставить в lab или future hybrid:

- multi-protocol dashboard;
- attach existing server auto-detection;
- DNS/AdGuard/SOCKS5 service orchestration;
- Telegram delivery;
- raw config editing;
- plugin-like protocol managers.

Причина: эти идеи шире foundational safety layer и требуют больше контекста продукта.

## Источники

- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- API surface deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-api-surface.md](../../../research/upstreams/prvtpro-amnezia-web-panel-api-surface.md)
- Manager architecture deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md](../../../research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
