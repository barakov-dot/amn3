# Кандидаты для `amn2`

Идеи из этой очереди не являются задачами на реализацию. Каждая идея должна пройти gate:

- совместимость лицензии;
- практическая польза;
- operational- и security-риски;
- архитектурная совместимость с `amn2`;
- тестовый план.

Общий checklist для переноса: [Design Specs Index + `amn2` Transfer Checklist](../docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md).

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
- Статус: design candidate описан в [Public/Self-service Config Delivery для `amn2`](../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md).

### Параллельная проверка статусов

- Идея: проверять ping/status протоколов параллельно, чтобы UI не зависал на медленных серверах.
- Польза: быстрее и отзывчивее для панели управления.
- Риски: rate limits, SSH connection fan-out, timeouts, cancellation.
- Статус: research.

### Token-protected sharing

- Идея: публичные ссылки для получения конфигурации без доступа к панели.
- Польза: удобная выдача конфигов пользователям.
- Риски: срок жизни ссылок, одноразовость, аудит, утечки, revoke.
- Статус: design candidate описан в [Public/Self-service Config Delivery для `amn2`](../docs/superpowers/specs/2026-05-30-public-self-service-config-delivery-design.md).

### OpenAPI-группировка по доменам

- Идея: группировать API-документацию по понятным доменам.
- Польза: проще проверять admin/user/protocol/settings surface.
- Риски: минимальные, но нужна синхронизация docs с реальными route guards.
- Статус: research.

### Scoped API tokens

- Идея: развить концепцию API tokens в сторону granular scopes, expiry, revoke, audit и отдельного scope для destructive operations.
- Польза: безопаснее для CI, мониторинга и ограниченных внешних интеграций, чем admin-equivalent bearer tokens.
- Риски: сложность UX, миграции токенов, тесты на privilege escalation, хранение token hashes.
- Статус: design candidate описан в [Scoped API Tokens для `amn2`](../docs/superpowers/specs/2026-05-30-scoped-api-tokens-design.md).

### Hardened first-run bootstrap

- Идея: заменить default credentials на forced password setup, one-time bootstrap token или локальный first-run secret.
- Польза: снимает классический риск `admin/admin` после первого запуска.
- Риски: recovery flow, headless install, UX первого запуска, тесты bootstrap/recovery.
- Статус: research после deep-dive.

### Secret inventory и redacted backup

- Идея: перед любым backup/restore явно классифицировать секреты и по умолчанию отдавать redacted backup.
- Польза: снижает риск случайной утечки SSH keys, panel tokens, Telegram tokens и внешних API keys.
- Риски: пользователю нужен понятный full-backup режим, encryption key management, restore compatibility.
- Статус: design candidate описан в [Secret Inventory + Backup Policy для `amn2`](../docs/superpowers/specs/2026-05-30-secret-inventory-backup-policy-design.md).

### Safe SSH/sudo policy

- Идея: описать безопасный SSH execution layer: host key pinning, no password in command string, secret redaction in logs, dry-run, audit, rollback.
- Польза: критично для любых операций, которые меняют удаленный VPN-сервер.
- Риски: сложность реализации, разные sudoers-конфигурации, совместимость с существующими серверами.
- Статус: research после deep-dive.

### Route policy matrix

- Идея: перед реализацией API фиксировать таблицу endpoint, role, auth method, side effect, audit requirement и tests.
- Польза: снижает риск разнородных guards и случайного privilege escalation.
- Риски: требует дисциплины при добавлении endpoints и синхронизации OpenAPI/docs.
- Статус: design candidate описан в [Route Policy Matrix для `amn2`](../docs/superpowers/specs/2026-05-30-route-policy-matrix-design.md).

### API operation risk classes

- Идея: классифицировать API-действия как read-only, secret-read, state-write, remote-exec и destructive.
- Польза: помогает заранее определить confirmation, audit, dry-run и test requirements.
- Риски: ошибочная классификация может дать слишком мягкие guardrails.
- Статус: research после API surface deep-dive.

### Destructive operation test plan

- Идея: для reboot, clear, uninstall, raw config save и restore иметь отдельные тесты отказов, audit events и recovery notes.
- Польза: production-перенос становится проверяемым, а не только “осторожным”.
- Риски: нужны test doubles для remote server и аккуратная модель dry-run.
- Статус: research после API surface deep-dive.

### Command execution contract

- Идея: remote operation должна описываться contract-ом: тип риска, inputs, expected side effects, timeout, allowed exit codes, redaction, audit summary и recovery note.
- Польза: SSH/sudo/Docker/firewall операции становятся тестируемыми и обозримыми до выполнения.
- Риски: больше design работы перед первой реализацией; понадобится fake runner и дисциплина в manager-ах.
- Статус: design candidate описан в [RemoteOperationRunner для `amn2`](../docs/superpowers/specs/2026-05-30-remote-operation-runner-design.md).

### Dry-run-first remote operations

- Идея: install, uninstall, clear, raw config save и firewall/Docker changes сначала строят plan preview, а уже затем применяются.
- Польза: снижает риск случайно сломать VPS или удалить рабочие контейнеры.
- Риски: не все remote checks можно идеально эмулировать; dry-run не должен создавать ложное чувство безопасности.
- Статус: research после manager architecture deep-dive.

### Remote operation audit events

- Идея: каждая state-changing remote operation пишет audit event до и после выполнения, без секретов в payload.
- Польза: проще разбирать инциденты, partial failures и действия операторов.
- Риски: нужно хранить audit отдельно от sensitive outputs и продумать retention.
- Статус: research после manager architecture deep-dive.

### Manager interface checklist

- Идея: для каждого protocol/service manager заранее фиксировать обязательные методы: `detect`, `status`, `plan`, `apply`, `rollback_note`, `audit_summary`, `test_double`.
- Польза: уменьшает хаос при добавлении новых протоколов и облегчает тестирование.
- Риски: слишком жесткий interface может мешать нестандартным протоколам; нужен capability-based подход.
- Статус: research после manager architecture deep-dive.

### Host key enrollment

- Идея: добавление VPS должно включать явный SSH host key enrollment/pinning вместо автоматического доверия неизвестному ключу.
- Польза: снижает риск MITM при управлении production-сервером.
- Риски: UX сложнее для новичков; нужен recovery-flow при переустановке VPS.
- Статус: research после manager architecture deep-dive.

### Ближайшая очередь design review

- `RemoteOperationRunner`: command contract, host key enrollment, redaction, audit, dry-run и fake runner.
- `Route Policy Matrix`: endpoint, role, auth method, side effect, risk class, audit и tests.
- `Scoped API Tokens`: one-time display, hash storage, scopes, expiry, revoke и owner inheritance.
- `Secret Inventory + Backup Policy`: redacted backup по умолчанию и encrypted full backup как явный режим.
- `Public/Self-service Config Delivery`: ownership tests, hashed share tokens, expiry, revoke и audit.
- Статус: собрано из feature gap; перед реализацией нужен контекст текущего `amn2`.

## Из wg-easy/wg-easy

Источник: [research/upstreams/wg-easy-wg-easy.md](../research/upstreams/wg-easy-wg-easy.md)

Статус лицензии: AGPL-3.0-only, только самостоятельная реализация идей.

### Public-safe client read models

- Идея: разделять internal client model и public-safe representation, где private key/pre-shared key исключены по умолчанию.
- Польза: снижает риск случайной утечки client secrets через list/detail endpoints.
- Риски: нужен secret inventory и тесты, что sensitive fields не попадают в API/backup/logs.
- Статус: reinforced by [wg-easy config delivery deep-dive](../research/upstreams/wg-easy-wg-easy-config-delivery.md).

### Client expiration

- Идея: добавить expiration как часть lifecycle connection/client.
- Польза: удобно для временного доступа, trial, support и cleanup.
- Риски: что значит expiration для уже выданного config, нужен revoke/disable behavior и tests.
- Статус: reinforced by [wg-easy config delivery deep-dive](../research/upstreams/wg-easy-wg-easy-config-delivery.md).

### Metrics surface для peers

- Идея: read-only metrics endpoint для configured/enabled/connected peers, traffic и latest handshake.
- Польза: полезно для monitoring без захода в admin UI.
- Риски: labels могут раскрывать client names/IP, нужен route policy, bearer scope и privacy review.
- Статус: research after second upstream.

### Permission wrapper with required resource check

- Идея: route wrapper должен заставлять handler выполнить resource-level check, если policy зависит от конкретного resource.
- Польза: снижает риск забыть ownership check после role check.
- Риски: требует аккуратного API middleware/dependency design и тестов на denied ownership.
- Статус: research after second upstream.
