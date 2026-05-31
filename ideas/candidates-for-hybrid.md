# Кандидаты для будущего гибридного проекта

Здесь фиксируются идеи, которые не обязательно должны попадать в `amn2`, но могут быть полезны для будущего VPN-продукта.

## Из VoltAgent/awesome-design-md

Источник: [research/upstreams/awesome-design-md.md](../research/upstreams/awesome-design-md.md)

### VPS Ops Lab DESIGN.md

- Идея: создать собственный `DESIGN.md` для будущего lab/hybrid UI, используя `awesome-design-md` только как reference library для структуры и сравнения дизайн-подходов.
- Польза: у проекта появится единый visual/UX contract для operator-first интерфейса: плотные таблицы, ясные статусы, predictable navigation, risk labels, audit-friendly actions и документация как часть продукта.
- Риски: нельзя копировать узнаваемую визуальную идентичность известных брендов; marketing-site паттерны не должны вытеснить operational/admin ergonomics.
- Статус: design-needed; лучше вынести в отдельный проектный чат, а главный чат оставить для координации.

## Из PRVTPRO/Amnezia-Web-Panel

Источник: [research/upstreams/prvtpro-amnezia-web-panel.md](../research/upstreams/prvtpro-amnezia-web-panel.md)

### Attach existing server flow

- Идея: добавить уже настроенный сервер и автоматически определить протоколы, пользователей и конфигурацию.
- Польза: мягкая миграция существующих пользователей в новую панель.
- Риски: небезопасное хранение SSH-доступа, некорректное распознавание состояния, destructive operations.
- Статус: high-signal для гибридного продукта.

### Multi-protocol dashboard

- Идея: единая панель для VPN-протоколов, DNS, ad blocking, proxy и внешних интеграций.
- Польза: единый operator UX.
- Риски: слишком широкий scope, сложность ролей и lifecycle management.
- Статус: high-signal для будущего продукта, не для ближайшего `amn2`.

### Manager architecture per protocol

- Идея: общий SSH/control layer плюс отдельные manager-модули на каждый протокол.
- Польза: понятные границы между протоколами.
- Риски: дублирование logic, разные error models, общий contract manager-ов.
- Статус: research.

### Telegram bot integration

- Идея: уведомления и ограниченное управление через Telegram.
- Польза: быстрый канал для operator/user events.
- Риски: secret storage, rate limits, command authorization.
- Статус: research.

### i18n и RTL

- Идея: ранняя поддержка нескольких языков и RTL.
- Польза: продуктовая готовность для разных рынков.
- Риски: поддержка переводов, layout regressions, терминология.
- Статус: research.

### Sensitive config delivery

- Идея: выдавать VPN-конфиги через несколько каналов: web self-service, public share link, Telegram, API.
- Польза: гибкий user delivery UX для разных сценариев.
- Риски: каждый канал становится secret delivery path; нужны expiry, audit, revoke, rate limit, clear warnings и import-level тесты для `.conf`, QR и `vpn://`.
- Статус: полезно для гибридного продукта, не для быстрого переноса в `amn2`; усилено после [PRVTPRO config delivery integrity](../research/upstreams/prvtpro-amnezia-web-panel-config-delivery-integrity.md).

### Operator backup/restore

- Идея: иметь UI/API для backup/restore состояния панели.
- Польза: проще переносить и восстанавливать небольшие инсталляции.
- Риски: backup почти всегда содержит секреты; нужен redacted/full режим, encryption, restore validation и audit.
- Статус: research.

### Operator API taxonomy

- Идея: сделать API docs продуктовой частью operator UX: отдельные группы для auth, servers, protocols, connections, users, self-service, sharing, settings и integrations.
- Польза: проще расширять multi-protocol продукт и подключать внешние инструменты.
- Риски: docs могут расходиться с реальными guards, если нет policy matrix и тестов.
- Статус: полезно для будущего гибридного проекта.

### Integration-friendly API surface

- Идея: проектировать внешний API не как “те же admin routes”, а как отдельный integration surface со scopes, audit и стабильными contracts.
- Польза: безопаснее для мониторинга, CI, billing, support tooling и миграций.
- Риски: больше design работы и больше compatibility obligations.
- Статус: research.

### Protocol capability registry

- Идея: описывать каждый протокол через capabilities: install, detect, status, add user, remove user, config export, secret outputs, ports, networks, destructive operations.
- Польза: гибридный продукт сможет показывать UI и API по возможностям протокола, а не по hardcoded branches.
- Риски: registry нужно поддерживать синхронно с реальными manager-ами; config export должен иметь единый result contract, чтобы UI/public share/self-service не зависели от несовместимых signatures.
- Статус: research после manager architecture deep-dive.

### Plugin-like protocol managers

- Идея: вынести protocol/service manager-ы в plugin-like modules с общим contract и отдельными tests.
- Польза: проще добавлять VPN, DNS, proxy и integration modules без переписывания core.
- Риски: plugin boundary усложняет версии, migrations и security review.
- Статус: полезно для будущего гибридного продукта.

### Existing server reconciliation

- Идея: attach-flow должен уметь читать existing layout, containers, users и configs, а затем предлагать безопасный reconciliation plan.
- Польза: мягкая миграция существующих серверов без немедленного изменения host.
- Риски: распознавание может ошибиться; любые auto-fix действия должны быть отдельно подтверждены.
- Статус: high-signal для гибридного продукта.

### Service mode model

- Идея: для DNS/ad-blocking/proxy сервисов заранее поддержать режимы `replacement`, `side-by-side`, `disabled`, `external`.
- Польза: operator может выбирать модель внедрения без ручного изменения Docker networks и ports.
- Риски: конфликт IP/ports, migration path, rollback и support matrix.
- Статус: research после manager architecture deep-dive.

### Domain-aware split routing

- Идея: поддержать policy-driven split routing по доменным зонам и доменам, где часть направлений идет через VPN, а часть остается на прямом маршруте клиента.
- Польза: гибридный продукт сможет управлять DNS, proxy и VPN-routing как единой policy, а не как набором несвязанных настроек.
- Риски: domain routing требует client-side поддержки, OS-specific rules, DNS consistency и понятной диагностики. Server-only реализация не дает настоящего bypass, если трафик уже вошел в туннель.
- Статус: hybrid roadmap candidate; для `amn2` нужен отдельный узкий design spec `Domain Zone Exclusion Policy`, чтобы не смешивать client split-routing с server DNS/egress fallback.

### Chained service routing

- Идея: поддержать последовательную маршрутизацию между VPN/proxy/DNS-сервисами, например service A отправляет исходящий трафик через service B.
- Польза: дает гибкую multi-service topology для продвинутых операторов.
- Риски: легко получить routing loops, непрозрачный troubleshooting, портовые конфликты, сложный threat model и слабую observability.
- Статус: hybrid-only candidate после [GitHub watch PRVTPRO](../research/upstreams/prvtpro-amnezia-web-panel-github-watch.md); не переносить в `amn2` без отдельного topology design.

### Background remote jobs

- Идея: долгие install/clear/reconcile операции выполнять как jobs с progress, structured logs, timeout, cancellation и final audit summary.
- Польза: UI не зависает, а оператор видит понятное состояние remote operation.
- Риски: job queue, retry semantics, idempotency и восстановление после рестарта панели.
- Статус: research после manager architecture deep-dive.

### Hybrid feature set из Amnezia Web Panel

- Идея: держать multi-protocol orchestration, attach existing server, DNS/ad-blocking/proxy adjunct services, Telegram delivery и external sync в отдельной гибридной дорожной карте.
- Польза: `amn2` не раздувается раньше времени, а будущий продукт получает цельную operator platform vision.
- Риски: широкий scope, сложная support matrix, много secret delivery surfaces и remote operation risks.
- Статус: feature gap относит это к `hybrid-only` или `needs-amn2-context`, не к прямому переносу в `amn2`.

## Из wg-easy/wg-easy

Источник: [research/upstreams/wg-easy-wg-easy.md](../research/upstreams/wg-easy-wg-easy.md)

Итоговый feature gap: [research/upstreams/wg-easy-wg-easy-feature-gap.md](../research/upstreams/wg-easy-wg-easy-feature-gap.md)

### WireGuard-first UX reference

- Идея: использовать focused WireGuard panel как эталон минимального operator UX: clients, QR/config, status, charts, expiration.
- Польза: помогает не перегружать будущий гибридный продукт до того, как базовый protocol UX станет хорошим.
- Риски: single-protocol UX нельзя напрямую растянуть на multi-protocol platform.
- Статус: high-signal reference.

### Per-client firewall filtering

- Идея: advanced access-control для clients через per-client allowed destinations.
- Польза: полезно для корпоративных или ограниченных VPN-сценариев.
- Риски: firewall rules являются high-risk host changes; нужен plan/dry-run/audit/recovery.
- Статус: hybrid-only до отдельного risk design.

### Account security baseline

- Идея: для будущего гибридного продукта заранее заложить account page с password update, 2FA, disabled user state и понятной role matrix.
- Польза: multi-protocol продукт будет безопаснее расширять, если auth methods и roles заданы до появления integrations, bot и public links.
- Риски: recovery flow, support role, scoped tokens, audit и secret inventory нужно проектировать вместе, а не отдельными patches.
- Статус: research после [wg-easy permissions/auth/2FA deep-dive](../research/upstreams/wg-easy-wg-easy-auth-permissions-2fa.md).

### Observability baseline

- Идея: заложить единый metrics registry для протоколов: aggregate counts, per-peer status, traffic, last-seen/handshake и privacy class для каждого field.
- Польза: будущий гибридный продукт получит нормальный monitoring surface без хаотичных endpoint-ов на каждый протокол.
- Риски: labels и JSON fields могут раскрывать sensitive metadata; нужны scoped tokens, opt-in detailed mode и retention guidance.
- Статус: research после [wg-easy metrics surface deep-dive](../research/upstreams/wg-easy-wg-easy-metrics-surface.md).

### Operational docs system

- Идея: строить docs как часть продукта: install, setup, unattended setup, migration, API, CLI, metrics, update, rollback и recovery.
- Польза: гибридный VPN-продукт будет проще внедрять, обновлять и поддерживать на разных deployment-сценариях.
- Риски: docs должны быть versioned и проверяемыми; migration/import docs работают с secret-bearing state.
- Статус: research после [wg-easy operational docs/migration deep-dive](../research/upstreams/wg-easy-wg-easy-operational-docs-migration.md).

### Migration/import wizard

- Идея: добавить безопасный wizard для import existing config/server state: upload, validate, redacted preview, conflict report, apply, rollback note.
- Польза: дает мягкий onboarding существующих пользователей и серверов.
- Риски: private keys, pre-shared keys, IP conflicts, partial import, version mismatch и support burden.
- Статус: hybrid-only candidate после [wg-easy operational docs/migration deep-dive](../research/upstreams/wg-easy-wg-easy-operational-docs-migration.md).

## Из kyoresuas/amnezia-api

Источник: [research/upstreams/kyoresuas-amnezia-api.md](../research/upstreams/kyoresuas-amnezia-api.md)

### Per-server API agent

- Идея: будущий hybrid может использовать lightweight agent на каждом VPN-сервере, а центральная панель будет говорить с ним через stable API.
- Польза: опасные Docker/config операции остаются локально на ноде, а панель получает единый control surface.
- Риски: agent enrollment, token rotation, mTLS или другой channel security, version skew и compromise blast radius.
- Статус: high-signal architecture reference.

### Multi-server balancing metadata

- Идея: server endpoint возвращает `region`, `weight`, `maxPeers`, `totalPeers`, protocols и load для выбора подходящей ноды.
- Польза: база для billing/provisioning/orchestrator, который создает пользователей на разных VPN-серверах.
- Риски: metrics могут раскрывать capacity/activity metadata; нужна privacy policy и scoped read token.
- Статус: hybrid roadmap candidate.

### Unified protocol adapter contract

- Идея: для каждого protocol runtime держать общий adapter contract: list, create, update, delete, export/import, status, metrics.
- Польза: гибридный продукт может добавлять новые runtimes без переписывания панели.
- Риски: слишком общий contract может скрыть protocol-specific side effects; нужны capabilities и risk classes.
- Статус: research candidate.
