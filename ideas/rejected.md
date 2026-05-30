# Отклоненные идеи

Здесь фиксируются идеи, которые не стоит переносить или развивать, вместе с причиной.

## Из PRVTPRO/Amnezia-Web-Panel

### Прямое копирование кода панели

- Решение: отклонено.
- Причина: GPL-3.0 и правило проекта запрещают перенос кода без отдельной проверки лицензии.
- Допустимая альтернатива: изучать сценарии и проектировать самостоятельную реализацию.

### Использование default `admin` / `admin` как нормального first-run сценария

- Решение: отклонено для production.
- Причина: высокий security-риск.
- Допустимая альтернатива: forced password setup, one-time bootstrap token или локальный first-run secret.

### Ephemeral `SECRET_KEY` без явной production-настройки

- Решение: отклонено для production.
- Причина: сброс session/security state после рестарта и неявная конфигурация.
- Допустимая альтернатива: обязательный persistent secret в production-режиме.

### Admin-equivalent API tokens без scopes и expiry

- Решение: отклонено для production как базовая модель.
- Причина: один leaked token получает слишком широкий доступ.
- Допустимая альтернатива: scoped tokens, expiry, revoke, audit и отдельные scopes для destructive operations.

### Plaintext share tokens в общем state

- Решение: отклонено для production.
- Причина: утечка state-файла превращается в доступ к пользовательским config links.
- Допустимая альтернатива: hashed share tokens, expiry, one-time mode, revoke и audit.

### Хранение SSH passwords/private keys без отдельной secret policy

- Решение: отклонено для production.
- Причина: компрометация state-файла дает доступ к удаленным серверам.
- Допустимая альтернатива: secret storage, encryption at rest, SSH keys, ограниченный sudoers-профиль и redacted backup.

### Sudo password inside command string

- Решение: отклонено для production.
- Причина: пароль может попасть в process command line или логи команд.
- Допустимая альтернатива: SSH keys, ограниченный sudoers, askpass/pty-less безопасная модель или агентный runner без прокидывания пароля в shell string.

### Raw backup `data.json` как обычный download

- Решение: отклонено для production по умолчанию.
- Причина: backup содержит секреты и может быть случайно передан дальше.
- Допустимая альтернатива: redacted backup по умолчанию, encrypted full backup как явный dangerous режим, audit download/restore.

### Raw config editing без validation и audit

- Решение: отклонено для production.
- Причина: прямое сохранение server-side config может сломать протокол, потерять клиентов или скрыто изменить security posture.
- Допустимая альтернатива: schema validation, backup-before-write, diff preview, audit event и rollback note.

### Destructive API endpoints без dry-run и confirmation

- Решение: отклонено для production.
- Причина: операции reboot, clear, uninstall и restore могут ломать удаленный сервер или состояние панели.
- Допустимая альтернатива: explicit confirmation, dry-run где возможно, audit, role/scope gate и recovery plan.

### Разнородные route guards без policy matrix

- Решение: отклонено как production-подход.
- Причина: при росте API легко получить несогласованное поведение между session, bearer token, user self-service и public sharing.
- Допустимая альтернатива: route policy matrix плюс тесты доступа для каждой роли и auth method.

### Auto-accept unknown SSH host keys

- Решение: отклонено для production.
- Причина: автоматическое доверие неизвестному host key ослабляет защиту от MITM при управлении VPS.
- Допустимая альтернатива: явный enrollment/pinning host key и отдельный recovery-flow при переустановке сервера.

### Remote command logging без redaction contract

- Решение: отклонено для production.
- Причина: команды, stdout и stderr могут содержать sudo password, VPN config, proxy credentials, tokens или private material.
- Допустимая альтернатива: structured audit без секретов, redaction pipeline и запрет secret material в command line.

### Shell command construction из runtime values

- Решение: отклонено как базовый production-подход.
- Причина: домены, ports, JSON payloads, filenames и user inputs легко становятся injection surface или ломают config.
- Допустимая альтернатива: typed command builder, строгая validation, escaping policy и unit tests на hostile inputs.

### `curl | sh` в manager-flow

- Решение: отклонено для production.
- Причина: установка зависимостей через remote shell без pinning, verification и preview усложняет audit и supply-chain контроль.
- Допустимая альтернатива: заранее проверенный installer, pinned packages, explicit plan preview и operator confirmation.

### Docker `latest` и target-host build как production default

- Решение: отклонено для production.
- Причина: результат установки становится неповторяемым, а build/download на VPS смешивает deployment и supply-chain risk.
- Допустимая альтернатива: pinned images, digest verification, signed artifacts и controlled release pipeline.

### Privileged container/firewall changes без operation plan

- Решение: отклонено для production.
- Причина: privileged containers, iptables, sysctl и Docker network changes могут сломать доступность сервера или соседние сервисы.
- Допустимая альтернатива: dry-run plan, conflict detection, explicit confirmation, audit и recovery note.

### Static Docker network/IP assumptions без проверки конфликтов

- Решение: отклонено как production-подход.
- Причина: фиксированные подсети и IP могут конфликтовать с существующей инфраструктурой пользователя.
- Допустимая альтернатива: network discovery, configurable ranges, conflict detection и migration plan.

### Config patching регулярными выражениями для sensitive configs

- Решение: отклонено для production.
- Причина: regex-патч может незаметно сломать JSON/YAML/service config или удалить критичные параметры.
- Допустимая альтернатива: structured parser, schema validation, diff preview и backup-before-write.

### Прямой перенос feature set без контекста `amn2`

- Решение: отклонено как способ планирования.
- Причина: этот lab-репозиторий не содержит код `amn2`; без ревью текущей архитектуры нельзя честно назначить функции в production backlog.
- Допустимая альтернатива: сначала feature gap, затем отдельный design spec в контексте `amn2` для каждой выбранной идеи.

## Из wg-easy/wg-easy

### Прямое копирование кода wg-easy

- Решение: отклонено.
- Причина: AGPL-3.0-only и правило проекта запрещают перенос кода без отдельной проверки лицензии.
- Допустимая альтернатива: изучать UX и production-сигналы, затем проектировать самостоятельную реализацию.

### Weak one-time link token generation/storage

- Решение: отклонено для production.
- Причина: one-time/share token должен быть crypto-secure, храниться как hash и проверяться по expiry/revoke/rate limit.
- Допустимая альтернатива: модель из `Public/Self-service Config Delivery`: hashed token, mandatory expiry, one-time mode, audit и abuse controls.

### Public config route без server-side expiry validation

- Решение: отклонено для production.
- Причина: UI countdown недостаточен; expiry должен проверяться на сервере до генерации и выдачи config.
- Допустимая альтернатива: server-side expiry check, revoke state, one-time consume transaction, rate limit и audit.

### Config delivery без audit

- Решение: отклонено для production.
- Причина: VPN config является secret-read artifact; без audit невозможно понять, кто и когда получил доступ.
- Допустимая альтернатива: audit event без raw config, route policy id, actor, connection id, delivery surface и decision.

### Basic Auth как full API fallback

- Решение: отклонено для production.
- Причина: password-only API fallback может обходить 2FA и не имеет scopes, expiry, revoke и token audit.
- Допустимая альтернатива: browser session для UI, scoped API tokens для integrations, owner inheritance и route policy checks.

### 2FA без покрытия всех auth methods

- Решение: отклонено как завершенная security-модель.
- Причина: 2FA на login form не защищает систему, если другой auth method принимает только password или broad bearer secret.
- Допустимая альтернатива: единая auth method matrix, TOTP enforcement policy, recovery flow, rate limit, lockout и audit.

### Coarse permission action без policy id

- Решение: отклонено как production-подход.
- Причина: action вроде `custom` требует ручной дисциплины в handler-ах и плохо проверяется tests/audit-ом.
- Допустимая альтернатива: stable route policy id, explicit risk class, ownership rule, allowed auth methods и tests per endpoint.

### Metrics labels без privacy review

- Решение: отклонено как production-default.
- Причина: client names, IP addresses и interface labels могут раскрывать sensitive metadata.
- Допустимая альтернатива: отдельная metrics policy: minimal labels, bearer scope, opt-in и privacy review.

### Internet-facing metrics без обязательной auth/network policy

- Решение: отклонено для production.
- Причина: read-only metrics могут раскрывать usage, client metadata, topology и activity state.
- Допустимая альтернатива: disabled by default, local-only/allowlist или scoped `metrics:read` token, rate limit и audit для включения.

### JSON metrics с per-client metadata как public/read-only endpoint

- Решение: отклонено для production.
- Причина: endpoint/publicKey/handshake/traffic являются sensitive metadata, даже если private keys не возвращаются.
- Допустимая альтернатива: отдельная detailed-metrics policy, scoped token, minimal fields by default и opt-in privacy review.

### Metrics password/hash как обычное config field

- Решение: отклонено как backup/export default.
- Причина: metrics secret или его hash участвуют в auth и должны считаться secret-derived material.
- Допустимая альтернатива: scoped token hash в secret inventory, redacted backup по умолчанию, rotation и revoke.

### API-доступ, требующий отключить 2FA

- Решение: отклонено для production.
- Причина: интеграции не должны заставлять оператора ослаблять account security.
- Допустимая альтернатива: scoped API tokens, route policy, expiry, revoke, owner inheritance и audit.

### Migration/import без preflight и rollback story

- Решение: отклонено для production.
- Причина: import VPN state может записывать private keys, pre-shared keys, addresses и live config; ошибка может сломать доступ или потерять клиентов.
- Допустимая альтернатива: schema validation, dry-run/preflight, redacted preview, backup-before-write, rollback note, audit и tests.

### Unattended setup secrets как долгоживущие env values

- Решение: отклонено как production-default.
- Причина: initial passwords/bootstrap secrets могут остаться в compose files, shell history, process env или support bundles.
- Допустимая альтернатива: one-time bootstrap token/local first-run secret, complexity check, automatic invalidation и cleanup guidance.

### CLI config/QR output без secret-read policy

- Решение: отклонено для production.
- Причина: CLI output может раскрывать VPN config так же, как web download или QR endpoint.
- Допустимая альтернатива: единая policy matrix для API/UI/CLI, audit, redaction и explicit operator confirmation для secret outputs.
