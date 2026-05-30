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
