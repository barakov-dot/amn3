# Кандидаты для `amn2`

Идеи из этой очереди не являются задачами на реализацию. Каждая идея должна пройти gate:

- совместимость лицензии;
- практическая польза;
- operational- и security-риски;
- архитектурная совместимость с `amn2`;
- тестовый план.

## Из PRVTPRO/Amnezia-Web-Panel

Источник: [research/upstreams/prvtpro-amnezia-web-panel.md](../research/upstreams/prvtpro-amnezia-web-panel.md)

Статус лицензии: GPL-3.0, только самостоятельная реализация идей.

### API tokens для интеграций

- Идея: токены для внешних интеграций, где raw token показывается один раз, а в хранилище лежит только hash.
- Польза: безопаснее для CI, мониторинга и внешних админ-инструментов.
- Риски: token scope, rotation, audit, revoke, role inheritance.
- Статус: research.

### Self-service endpoints

- Идея: отделить пользовательские `/my/*` endpoints от admin API.
- Польза: меньше риска случайно открыть admin-действия обычному пользователю.
- Риски: authorization boundary, тесты на privilege escalation.
- Статус: research.

### Параллельная проверка статусов

- Идея: проверять ping/status протоколов параллельно, чтобы UI не зависал на медленных серверах.
- Польза: быстрее и отзывчивее для панели управления.
- Риски: rate limits, SSH connection fan-out, timeouts, cancellation.
- Статус: research.

### Token-protected sharing

- Идея: публичные ссылки для получения конфигурации без доступа к панели.
- Польза: удобная выдача конфигов пользователям.
- Риски: срок жизни ссылок, одноразовость, аудит, утечки, revoke.
- Статус: research.

### OpenAPI-группировка по доменам

- Идея: группировать API-документацию по понятным доменам.
- Польза: проще проверять admin/user/protocol/settings surface.
- Риски: минимальные, но нужна синхронизация docs с реальными route guards.
- Статус: research.

### Scoped API tokens

- Идея: развить концепцию API tokens в сторону granular scopes, expiry, revoke, audit и отдельного scope для destructive operations.
- Польза: безопаснее для CI, мониторинга и ограниченных внешних интеграций, чем admin-equivalent bearer tokens.
- Риски: сложность UX, миграции токенов, тесты на privilege escalation, хранение token hashes.
- Статус: research после deep-dive.

### Hardened first-run bootstrap

- Идея: заменить default credentials на forced password setup, one-time bootstrap token или локальный first-run secret.
- Польза: снимает классический риск `admin/admin` после первого запуска.
- Риски: recovery flow, headless install, UX первого запуска, тесты bootstrap/recovery.
- Статус: research после deep-dive.

### Secret inventory и redacted backup

- Идея: перед любым backup/restore явно классифицировать секреты и по умолчанию отдавать redacted backup.
- Польза: снижает риск случайной утечки SSH keys, panel tokens, Telegram tokens и внешних API keys.
- Риски: пользователю нужен понятный full-backup режим, encryption key management, restore compatibility.
- Статус: research после deep-dive.

### Safe SSH/sudo policy

- Идея: описать безопасный SSH execution layer: host key pinning, no password in command string, secret redaction in logs, dry-run, audit, rollback.
- Польза: критично для любых операций, которые меняют удаленный VPN-сервер.
- Риски: сложность реализации, разные sudoers-конфигурации, совместимость с существующими серверами.
- Статус: research после deep-dive.
