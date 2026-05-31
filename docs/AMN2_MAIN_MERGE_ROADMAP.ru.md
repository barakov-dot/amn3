# `amn2`: основной порядок слияния API, web panel и operations

Дата: 2026-05-31.

Режим: coordination roadmap в `VPS-OPS-LAB`. Production-код `amn2` не менялся. Upstream code не копируется. Live VPS не трогаем.

## Решение по соседним чатам

### `VPS OPS LAB - PRVTPRO-Amnezia-Web-Panel`

Решение: поставить на паузу широкие research-задачи, но не закрывать источник.

Почему:

- GPL-3.0 блокирует прямое копирование кода, UI, manager-flow, Dockerfile, route layout и текстов.
- Deep-dive уже дал достаточно signal для ближайших production-gates: route taxonomy, self-service, public share, API tokens, manager contract, config delivery integrity, dangerous operations.
- Дальнейшее широкое исследование PRVTPRO сейчас будет конкурировать с переносом уже понятных безопасных foundation-срезов в `amn2`.

Что остается активным:

- точечные проверки PRVTPRO issues/UX только под конкретный `amn2` slice;
- config delivery integrity требования: `.conf`, QR, `vpn://`, Android/import compatibility;
- web-panel product patterns: endpoint grouping, self-service boundary, operator status UX, dangerous-action UX.

Что ставим на паузу:

- multi-protocol dashboard как цель для ближайшего `amn2`;
- attach existing server auto-reconcile;
- DNS/AdGuard/SOCKS/MTProxy manager flows;
- raw config editing;
- destructive server clear/install/uninstall flows.

### `VPN Ops Lab — KYORESUAS-API`

Решение: держать active as API/Local-Agent architecture reference, но не как источник кода.

Почему:

- MIT снижает license friction, но production-риск выше юридического: API управляет Docker/config/secrets/reboot.
- Самая полезная идея уже совпала с `amn2`: local-only server-side agent и route policy перед client lifecycle API.
- Нельзя переносить one shared API key, публичные `/docs`/`metrics`, backup/import/reboot и Docker socket exposure как default.

Что остается активным:

- Local Agent / controller split;
- server metadata: protocols, status, capacity/load;
- client lifecycle language: active/disabled/expiresAt;
- warning list для backup/import/reboot/destructive endpoints.

Что ставим на паузу:

- установка `kyoresuas/amnezia-api` на production VPS;
- копирование Node/Fastify implementation;
- полноценный `/clients` CRUD до policy, secret и remote-write gates.

## Критически важные задачи

### 1. Зафиксировать lab baseline

Статус: current.

Состав:

- `research/amn2/api-readiness-audit-after-live-baseline.md`
- `research/amn2/route-policy-matrix.md`
- `research/amn2/secret-surface-inventory.md`
- `research/amn2/remote-operations-inventory.md`
- `research/amn2/transfer-backlog.md`
- этот roadmap

Цель: чтобы следующий production plan не спорил с соседними чатами и verified live baseline.

### 2. Route/Auth/Operation Policy Matrix как первый production slice

Статус: first implementation candidate.

Правило: не добавлять новые API routes. Сначала сделать machine-checkable policy coverage для текущих surfaces.

Входит:

- web-admin routes: auth, users, servers, health, config/email delivery;
- public-token routes: email verify/recover;
- Telegram bot surfaces: admin/user config, approve, revoke/reset;
- Local Agent first-slice routes;
- CLI/remote operation classes.

Не входит:

- new `/api/*`;
- Local Agent clients/configs;
- public/self-service download;
- backup/import/reboot;
- remote-state-write runner expansion.

### 3. Secret/redaction coverage

Статус: next P0 after policy matrix.

Цель: перед любыми API/web panel выдачами доказать, что `.conf`, QR, `vpn://`, raw tokens, token hashes, Local Agent token, command stdout/stderr и diagnostics не попадают в logs/audit/errors.

### 4. Config delivery integrity

Статус: important P0 web-panel slice, но после policy/redaction base.

Цель: взять лучшее из PRVTPRO web-panel темы не как UI-копию, а как test/product contract:

- `.conf` byte-level UTF-8;
- QR decode equals expected payload;
- `vpn://` decode round-trip;
- non-ASCII names;
- no secret in audit/logs;
- единый export/result contract для будущих delivery surfaces.

## Важные задачи

### 5. Web panel safe improvements

Статус: начинать после P0 policy/redaction/config integrity.

Порядок web-panel доработок:

1. Улучшить policy/test coverage существующей web panel, не меняя UX.
2. Улучшить operator status UX вокруг server health и working configs.
3. Уточнить config delivery UI language: `.conf`, QR, `vpn://` как secret-bearing artifacts.
4. Добавить safer dangerous-action wording/confirmation только для уже существующих state-changing actions.
5. OpenAPI/domain grouping позже, когда будет стабильная API surface.

Не начинать с:

- новой большой панели;
- self-service portal;
- public share links;
- multi-protocol dashboard.

### 6. Local Agent hardening

Статус: foundation уже merged в `amn2`; расширять осторожно.

Следующие безопасные шаги:

- unified production audit sink для allowed read routes;
- token rotation/revoke design;
- version/runtime compatibility response;
- public-safe runtime metadata.

Отложить:

- `GET /agent/clients`;
- `GET /agent/configs/{id}`;
- write lifecycle;
- backup/import/reboot.

### 7. Scoped API tokens

Статус: design-needed после policy matrix.

Начинать со scopes:

- `server:read`;
- `metrics:read`;
- `config:read` только после config delivery policy;
- destructive scopes отдельно и позже.

### 8. Remote operation partial-failure contract

Статус: design-needed перед любым remote-state-write API.

Нужны:

- operation id;
- before/after audit;
- idempotency key или replay policy;
- recovery note;
- resume flow;
- no secret-bearing CLI args;
- shared read-only telemetry command policy.

## Простые задачи

- Обновлять AMN3 status/backlog после каждого production slice.
- Держать manual source links на PRVTPRO/KYORESUAS как research sources.
- Перед каждым `amn2` plan явно писать: нужен ли live retest.
- Синхронизировать docs с committed branch/commit/test evidence.
- Сократить повторяющиеся handoff-фразы после стабилизации roadmap.

## Косметические задачи

- Naming cleanup: AMN3, VPS Ops Lab, `amn2`, Amneziya, future hybrid.
- Русский-first docs, English only for code/API terms.
- OpenAPI grouping как operator/developer UX.
- Dangerous action UX labels.
- UI wording для secret-bearing artifacts.

## Что переносим из PRVTPRO и KYORESUAS в `amn2`

Переносим как самостоятельные требования:

- route taxonomy and policy matrix;
- separate admin/user/public-token surfaces;
- hash-only tokens with one-time raw display;
- scoped tokens, expiry, revoke, owner inheritance;
- config delivery integrity for `.conf`, QR, `vpn://`;
- manager/export contract idea;
- dangerous operation risk classes;
- local-only API agent;
- client lifecycle vocabulary: active, disabled, expiresAt;
- server status/capacity metadata.

Не переносим:

- PRVTPRO GPL code/UI/templates/managers/scripts;
- KYORESUAS Node/Fastify implementation;
- one broad shared API key;
- public docs/metrics as default;
- direct backup/import/reboot endpoints;
- raw config editing;
- remote install/clear/uninstall flows before runner/job model.

## Recommended merge order

1. Commit AMN3 audit/roadmap state.
2. Write `amn2` implementation plan for route/auth/operation policy coverage tests.
3. Implement policy coverage in `amn2` with tests only, no new behavior.
4. Add redaction coverage plan and implementation.
5. Add config delivery integrity tests/contract.
6. Improve existing web panel UX around status/config delivery/dangerous wording.
7. Design scoped API tokens.
8. Harden Local Agent read-only/audit/versioning.
9. Only then consider read-only clients/metrics endpoints.
10. Only after remote-write contract consider client lifecycle write API.

## Recommendation

Start merge work from policy and tests, not UI or API endpoints. It is the least glamorous step, but it is the step that lets us safely take useful ideas from both neighboring chats without dragging in their risks.
