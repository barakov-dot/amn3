# Кандидаты для будущего гибридного проекта

Здесь фиксируются идеи, которые не обязательно должны попадать в `amn2`, но могут быть полезны для будущего VPN-продукта.

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
- Риски: каждый канал становится secret delivery path; нужны expiry, audit, revoke, rate limit и clear warnings.
- Статус: полезно для гибридного продукта, не для быстрого переноса в `amn2`.

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
- Риски: registry нужно поддерживать синхронно с реальными manager-ами.
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
