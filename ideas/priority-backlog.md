# Приоритетный backlog для `amn2` и будущего hybrid

Этот файл фиксирует рабочую карту решений после анализа PRVTPRO/Amnezia-Web-Panel, wg-easy/wg-easy, kyoresuas/amnezia-api и текущего состояния `amn2`.

Backlog не является списком задач к немедленной реализации. Любая идея переходит в `amn2` только после transfer gate:

- лицензия и отсутствие копирования внешнего кода;
- практическая польза;
- operational- и security-риски;
- архитектурная совместимость с `amn2`;
- тестовый план;
- recovery/rollback-модель для опасных изменений.

## Статусы

- `ready-for-plan` - можно писать implementation plan.
- `design-needed` - сначала нужен отдельный design spec.
- `in-progress` - уже есть локальная ветка, plan или первый срез.
- `paused` - осознанно отложено.
- `hybrid-only` - не переносить в ближайший `amn2`, держать для будущего продукта.

## P0. Критически важные рекомендации

### Secret-safe config delivery

- Цель: `amn2`.
- Статус: `in-progress`.
- Суть: `.conf`, QR и `vpn://` всегда считать `secret-read` артефактами, а не обычными metadata.
- Причина: config delivery содержит private key/pre-shared key или import payload, поэтому случайное логирование, share без expiry или неверная кодировка сразу становятся production-рискoм.
- Уже сделано: подготовлен первый срез с metadata-полями delivery package и UTF-8 artifact tests.
- Следующий шаг: после GitHub-доступа создать PR из ветки `codex/config-delivery-artifact-integrity-isolated`; затем расширить тесты до import-совместимости и audit/redaction.

### Remote operations safety

- Цель: `amn2`.
- Статус: `in-progress`.
- Суть: любые SSH/sudo/Docker/firewall операции выполнять через единый runner с dry-run, timeout, redaction, audit и recovery note.
- Причина: удаленные операции могут сломать VPS, firewall, контейнеры или доступ пользователей.
- Текущий результат: read-only health slice `RemoteOperationRunner` уже присутствует в текущем `amn2` baseline и проверен focused/full тестами.
- Следующий шаг: исполнить подготовленный redaction coverage first slice; затем отдельно описать partial-failure/rollback contract.

### Route/Auth policy matrix

- Цель: `amn2`.
- Статус: `ready-for-plan`.
- Суть: для каждого endpoint фиксировать role, auth method, risk class, side effect, audit requirement и tests.
- Причина: это снижает риск случайного privilege escalation при расширении API, web-admin, bot и интеграций.
- Текущий результат: создана конкретная [Route/Auth Policy Matrix](../research/amn2/route-policy-matrix.md) для web, bot, public-token и CLI/operator surfaces.
- Следующий шаг: написать implementation plan для route policy coverage tests или использовать matrix как вход для `RemoteOperationRunner`.

### SSH host key enrollment

- Цель: `amn2`.
- Статус: `design-needed`.
- Суть: добавление VPS должно включать явное SSH host key enrollment/pinning.
- Причина: автоматическое доверие неизвестному host key оставляет риск MITM при production-управлении сервером.
- Следующий шаг: описать UX первого подключения, re-enrollment и recovery после переустановки VPS.

### Backup/import как dangerous API

- Цель: `amn2`, позже hybrid.
- Статус: `design-needed`.
- Суть: backup/import только через redacted/full режимы, dry-run preview, validation, encryption option и recovery note.
- Причина: full backup почти всегда содержит private keys, tokens, configs и состояние клиентов.
- Следующий шаг: использовать обновленный P0 secret inventory как вход для backup/import policy; redacted backup оставить default, full backup считать dangerous explicit mode.

### Secret inventory

- Цель: `amn2`.
- Статус: `ready-for-plan`.
- Суть: единая таблица секретов: где хранятся, где могут утечь, как redacted, rotated, revoked и restored.
- Причина: без inventory нельзя безопасно проектировать backup, config delivery, scoped tokens, agent и audit.
- Текущий результат: `research/amn2/secret-surface-inventory.md` расширен до P0-gate для config delivery, backup/import, scoped tokens, Local Agent, SSH/VPS operations, metrics и audit.
- Следующий шаг: использовать `Redaction coverage plan` как первый implementation gate для `.conf`, QR, `vpn://`, tokens, Local Agent headers и command output.

## P1. Важные рекомендации

### Scoped API tokens

- Цель: `amn2`.
- Статус: `design-needed`.
- Суть: granular scopes, expiry, revoke, hash-only storage, audit.
- Причина: внешним интеграциям нельзя выдавать admin-equivalent bearer tokens.
- Следующий шаг: начать с `metrics:read`, `config:read`, `server:read`, затем destructive scopes отдельно.

### Public/self-service config delivery

- Цель: `amn2`.
- Статус: `design-needed`.
- Суть: share links и self-service выдача конфигов с ownership checks, expiry, revoke, audit и rate limit.
- Причина: полезно для пользователей, но это новый secret delivery surface.
- Следующий шаг: строить только после P0 `Secret-safe config delivery`.

### Manager config export contract

- Цель: `amn2`, позже hybrid.
- Статус: `design-needed`.
- Суть: единый result contract для `.conf`, QR, `vpn://` и будущих protocol-specific артефактов.
- Причина: UI/API/bot/self-service не должны зависеть от несовместимых `get_client_config` signatures.
- Следующий шаг: описать минимальный `ConfigExportResult` и capability-based behavior.

### Local Amnezia API agent

- Цель: `amn2`.
- Статус: `in-progress`.
- Суть: локальный agent рядом с Amnezia управляет users/peers через ограниченный HTTP contract вместо постоянного внешнего SSH control plane.
- Причина: перспективно для управления Amnezia через API, но agent получает высокий доступ к runtime/config state.
- Следующий шаг: продолжить production hardening: local-only bind, token hash, rotation, audit и version checks.

### Configurable VPN subnet/IPAM

- Цель: `amn2`.
- Статус: `design-needed`.
- Суть: subnet/IPAM сделать явной настройкой server/profile, а не hardcoded behavior.
- Причина: нужно для нескольких серверов, миграций, routed/site-to-site сценариев и conflict detection.
- Следующий шаг: CIDR validation, reserved addresses, conflict report, migration plan.

### Metrics surface и privacy policy

- Цель: `amn2`, позже hybrid.
- Статус: `design-needed`.
- Суть: read-only metrics endpoint для peers/traffic/handshake только с privacy class и scoped metrics token.
- Причина: monitoring полезен, но может раскрывать client names, IP, endpoint и activity metadata.
- Следующий шаг: определить aggregate-only default и opt-in detailed labels.

## P2. Малая важность или отложить

### Web-admin 2FA

- Цель: `amn2`.
- Статус: `paused`.
- Суть: account-level TOTP/2FA для админов.
- Причина паузы: полезно, но требует recovery flow, lockout policy, rate limit, audit и secret inventory для TOTP key.
- Условие возврата: отдельное решение о необходимости 2FA после закрытия P0 auth/secret вопросов.

### Domain Zone Exclusion Policy

- Цель: `amn2`, позже hybrid.
- Статус: `design-needed`.
- Суть: policy-driven исключения доменных зон, например `.ru` и `.рф`, с client-side split-routing как основным механизмом.
- Важное ограничение: настоящий bypass возможен только на клиенте до входа пакета в VPN. Server-side DNS/egress policy может быть только fallback, blocklist или diagnostic guardrail.
- Следующий шаг: отдельный design spec с default-off, preview, audit и OS/client compatibility matrix.

### Multi-protocol dashboard

- Цель: hybrid.
- Статус: `hybrid-only`.
- Суть: единая панель для VPN-протоколов, DNS, ad blocking, proxy и внешних интеграций.
- Причина отложения: слишком широкий scope для ближайшего `amn2`; сначала нужны protocol capabilities и remote operation safety.

### Attach existing server reconciliation

- Цель: hybrid, частично `amn2` позже.
- Статус: `hybrid-only`.
- Суть: подключение уже настроенного сервера через read-only detect, redacted preview и reconciliation plan.
- Причина отложения: высокий риск ошибочного распознавания состояния и destructive auto-fix.

### Background remote jobs

- Цель: hybrid, позже `amn2`.
- Статус: `design-needed`.
- Суть: длинные install/clear/reconcile операции как jobs с progress, timeout, cancellation и final audit summary.
- Причина отложения: сначала нужен единый remote operation contract.

## P3. Косметика, UX и документация

### OpenAPI grouping

- Цель: `amn2`.
- Статус: `ready-for-plan`.
- Суть: группировать API docs по доменам: auth, users, servers, devices, config delivery, admin, metrics.
- Польза: легче проверять route guards и external integration surface.

### Operator docs as transfer gate

- Цель: `amn2` и lab.
- Статус: `ready-for-plan`.
- Суть: feature не считается готовой к переносу без install/update/rollback/recovery/security docs.
- Польза: production-перенос становится проверяемым, а не просто "код написан".

### Русский-first documentation

- Цель: lab и `amn2`.
- Статус: `ready-for-plan`.
- Суть: `.md`, README, specs и research notes сначала пишем на русском; английский используем вторым слоем для code terms, filenames, links, licenses и external project names.
- Польза: единый стиль работы и меньше потери смысла при обсуждении.

### Dangerous action UX

- Цель: `amn2`.
- Статус: `design-needed`.
- Суть: confirmation text, preview, risk class labels и recovery hints для опасных действий.
- Польза: оператор видит последствия до выполнения, особенно для remote-exec/destructive операций.

### VPS Ops Lab DESIGN.md

- Цель: lab и будущий hybrid.
- Статус: `design-needed`.
- Суть: создать самостоятельный `DESIGN.md` для operator-first VPN панели, используя [VoltAgent/awesome-design-md](../research/upstreams/awesome-design-md.md) как reference-only источник паттернов.
- Польза: будущие UI-задачи получат единый visual/UX contract: плотность, навигация, таблицы, риск-состояния, secret-read/destructive actions, documentation surfaces.
- Ограничение: не копировать брендовые DESIGN.md и не делать UI похожим на конкретный известный продукт.

### Naming cleanup

- Цель: lab.
- Статус: `ready-for-plan`.
- Суть: убрать двусмысленность между AMN3, `vpn-ops-lab`, `amn2`, Amneziya и future hybrid.
- Польза: меньше путаницы при переносе идей и подготовке handoff-файлов.

## Ближайшая рекомендуемая очередь

1. Закрыть PR/branch по `Secret-safe config delivery`, когда GitHub-доступ к приватному `amn2` будет настроен.
2. Исполнить redaction coverage first slice для `.conf`, QR, `vpn://`, tokens, Local Agent headers и command output.
3. После redaction coverage описать partial-failure/rollback contract для state-changing remote operations.
4. Позже превратить `Route/Auth Policy Matrix` в machine-checkable route policy coverage tests.
5. Только после этого возвращаться к self-service links, domain exclusions и 2FA.
