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
- Уже сделано: metadata-поля delivery package, UTF-8 artifact tests, redaction coverage и config delivery integrity evidence зафиксированы локальным gate.
- Следующий шаг: не открывать public/self-service delivery до scoped token/self-service design; web-panel wording slice `22dfc37` уже уточнил, что `.conf`, QR и `vpn://` являются secret-bearing artifacts.

### Remote operations safety

- Цель: `amn2`.
- Статус: `in-progress`.
- Суть: любые SSH/sudo/Docker/firewall операции выполнять через единый runner с dry-run, timeout, redaction, audit и recovery note.
- Причина: удаленные операции могут сломать VPS, firewall, контейнеры или доступ пользователей.
- Текущий результат: read-only health slice `RemoteOperationRunner` уже присутствует в текущем `amn2` baseline и проверен focused/full тестами.
- Текущий результат 2026-05-31: redaction coverage first slice выполнен в ветке `codex/redaction-coverage-first-slice`; focused suite `61 passed`, full suite `513 passed`.
- Текущий результат 2026-05-31: state-changing metadata local slice выполнен в ветке `codex/remote-operation-contract-metadata`; focused suite `23 passed`, full suite `517 passed`.
- Текущий результат 2026-05-31: partial-failure local slice выполнен в ветке `codex/remote-operation-partial-failure`; focused suite `38 passed`, full suite `519 passed`.
- Текущий результат 2026-06-01: dry-run/audit metadata local slice перенесен на fresh VPS-gate candidate `codex/remote-operation-vps-gate-prep`; focused suite `79 passed`, docs suite `7 passed`, full suite `551 passed`.
- Текущий план 2026-05-31: следующий remote safety блок разделен на local-only gate и controlled real VPS verification gate.
- Локальная очередь 2026-05-31: [Local-only task priority](../research/amn2/local-only-task-priority.md) фиксирует P0/P1/P2/P3 задачи, которые можно сделать без VPS и без чтения `.env`.
- Следующий шаг: выполнить controlled real VPS verification gate по `research/amn2/vps-gate-remote-operation-dry-run-audit.md`. Начинать с read-only check и dry-run apply/revoke preview; single test peer apply/revoke выполнять только после отдельного подтверждения.

### Route/Auth policy matrix

- Цель: `amn2`.
- Статус: `implemented-pushed-local-gate-complete`.
- Суть: для каждого endpoint фиксировать role, auth method, risk class, side effect, audit requirement и tests.
- Причина: это снижает риск случайного privilege escalation при расширении API, web-admin, bot и интеграций.
- Текущий результат: создана конкретная [Route/Auth Policy Matrix](../research/amn2/route-policy-matrix.md) для web, bot, public-token и CLI/operator surfaces.
- Следующий шаг: использовать matrix как обязательный gate для scoped API tokens, self-service links, Local Agent expansion и remote-state-write surfaces.

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
- Текущий результат 2026-05-31: `Redaction coverage plan` исполнен как первый implementation gate для `.conf`, QR, `vpn://`, tokens, Local Agent headers и command output.
- Следующий шаг: использовать verified redaction gate как обязательную предпосылку для partial-failure/rollback и будущих secret-bearing surfaces.

## P1. Важные рекомендации

### Scoped API tokens

- Цель: `amn2`.
- Статус: `implemented-first-storage-slice`.
- Суть: granular scopes, expiry, revoke, hash-only storage, audit.
- Причина: внешним интеграциям нельзя выдавать admin-equivalent bearer tokens.
- Текущий результат: commit `1fdcde5` добавил `api_tokens` table и `app.services.api_tokens` contract: hash-only storage, one-time raw token issue metadata, expiry, revoke, last-used и safe audit metadata. Первый slice разрешает только `server:read` и `metrics:read`.
- Следующий шаг: не добавлять `/api/*`, `config:read` или write scopes до VPS evidence, route policy entry и privacy/secret-read classification.

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
- Текущий результат: first-slice foundation, production wiring и Local Agent hardening выполнены; commit `c5d7eb6` закрепляет audit/version contract для read-only routes.
- Следующий шаг: token rotation/revoke design и scoped token policy; не добавлять `/agent/clients`, `/agent/configs` или write lifecycle без отдельного gate.

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
- Статус: `in-progress`.
- Суть: confirmation text, preview, risk class labels и recovery hints для опасных действий.
- Польза: оператор видит последствия до выполнения, особенно для remote-exec/destructive операций.
- Текущий результат: commit `22dfc37` уточнил web-panel confirmations для server disable, add missing local device, Disable/Enable VPN и device delete без изменения write behavior.
- Следующий шаг: preview/risk labels добавлять только через отдельные local-gate tests; live VPS нужен, если меняется apply/revoke/sync/config behavior.

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

1. Провести controlled real VPS verification gate для `codex/remote-operation-vps-gate-prep` на тестовом peer/device: read-only check, dry-run apply/revoke preview, затем single apply/revoke только после отдельного подтверждения.
2. Зафиксировать VPS evidence через `research/amn2/vps-gate-evidence-checklist.md`.
3. Решить merge/PR для ветки `codex/remote-operation-vps-gate-prep` по `research/amn2/post-vps-gate-merge-decision.md`.
4. После VPS evidence выбрать первый integration slice из KYORESUAS/PRVTPRO inputs без копирования кода: вероятнее read-only metrics/API route shell или Local Agent runtime metadata.
5. Использовать `research/amn2/docker-manager-design-note.md` как safety input для будущего Docker manager implementation plan.
6. Только после закрытия этих gates возвращаться к self-service links, domain exclusions и 2FA.
