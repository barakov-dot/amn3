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
