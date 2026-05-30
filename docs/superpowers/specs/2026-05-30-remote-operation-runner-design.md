# RemoteOperationRunner для `amn2`: design spec

## Назначение

`RemoteOperationRunner` - кандидатная production-абстракция для безопасного выполнения операций на удаленном VPS из `amn2`.

Spec возник из анализа `PRVTPRO/Amnezia-Web-Panel`, но не переносит его код, shell-flow, manager-реализации или конфиги. Upstream имеет license verdict `GPL-3.0`, поэтому для `amn2` допустима только самостоятельная реализация идеи после отдельного review в репозитории `amn2`.

Цель design spec: описать требования к слою, который будет выполнять SSH/sudo/Docker/firewall/config операции так, чтобы каждая операция была планируемой, проверяемой, логируемой без секретов и тестируемой через fake runner.

## Контекст и проблема

VPN-панель, которая управляет VPS, почти неизбежно выполняет рискованные remote operations:

- проверка состояния сервера;
- установка или обновление протоколов;
- изменение файлов конфигурации;
- управление контейнерами и сервисами;
- изменение firewall, sysctl, Docker networks;
- выдача или чтение секретных конфигов;
- удаление протоколов или очистка сервера.

Если такие действия реализовать как произвольные shell strings внутри API handlers или protocol manager-ов, появляются устойчивые production-риски:

- секреты попадают в command line, stdout/stderr, exceptions или audit;
- unknown SSH host key принимается без проверки;
- destructive operation запускается без preview;
- частичный failure оставляет сервер в непонятном состоянии;
- тесты проверяют только happy path;
- UI/API не могут честно показать, что именно будет изменено.

`RemoteOperationRunner` должен сделать remote execution отдельным доменным слоем, а не набором helper-функций.

## Scope

Входит в scope:

- модель remote operation;
- risk classes;
- plan/dry-run/apply flow;
- SSH host key enrollment;
- sudo policy без пароля в shell command string;
- redaction для logs, stdout/stderr, errors и audit payload;
- audit event model;
- fake runner для тестов;
- contract для будущих protocol/service manager-ов.

Не входит в scope этого spec:

- конкретная реализация в текущем коде `amn2`;
- выбор Python/Go/Rust/Node API;
- UI для запуска операций;
- конкретные команды установки WireGuard, AmneziaWG, Xray, DNS или proxy;
- миграция существующих серверов;
- хранение долгосрочных секретов вне общих требований.

## Основные принципы

1. Операция сначала планируется, потом применяется.
2. Любая state-changing операция создает audit event.
3. Секреты не попадают в command line, логи, exceptions, API responses и audit payload.
4. Unknown SSH host key не принимается автоматически в production-mode.
5. Destructive операции требуют явного confirmation token или другого подтверждения верхнего слоя.
6. Runner не знает бизнес-логику протокола, а исполняет уже описанный operation contract.
7. Protocol manager обязан уметь строить plan без выполнения изменений.
8. Fake runner является обязательной частью design, а не тестовой роскошью.

## Risk classes

Каждая операция получает один основной класс риска:

| Класс | Значение | Примеры | Минимальные требования |
| --- | --- | --- | --- |
| `read-only` | читает состояние без секретов | ping, `docker ps`, service status | timeout, audit optional |
| `secret-read` | читает секретный материал | client config, private key metadata, proxy credentials | scope/role check, redaction, audit |
| `state-write` | меняет локальный или удаленный state без remote exec | запись metadata, enable flag | audit, validation |
| `remote-exec` | выполняет команду на VPS | restart service, create directory, upload config | plan, audit, timeout, redaction |
| `destructive` | может удалить, сломать или заблокировать доступ | clear server, uninstall protocol, firewall rewrite, reboot | plan preview, confirmation, audit before/after, recovery note |

Если операция подходит под несколько классов, выбирается самый строгий.

## Operation contract

Каждая remote operation описывается структурой с обязательными полями. Имена полей можно адаптировать под язык `amn2`, но смысл должен сохраниться.

```text
RemoteOperation
  id: stable operation name, например "wireguard.install"
  risk_class: read-only | secret-read | state-write | remote-exec | destructive
  server_id: internal server reference
  actor_id: user, token или system actor
  inputs: validated non-secret inputs
  secret_refs: ссылки на секреты, не сами значения
  expected_changes: список файлов, сервисов, ports, containers, firewall rules
  commands: typed command steps или internal runner actions
  timeout_policy: per step and whole operation
  allowed_exit_codes: explicit list per command
  redaction_policy: какие поля и patterns скрывать
  audit_summary: краткое описание без секретов
  rollback_note: что делать при partial failure
  confirmation_required: true для destructive операций
```

`inputs` не должны содержать password, private key, token, raw config или client secret. Для них используются `secret_refs`, которые разрешаются только внутри безопасного execution boundary.

## Plan/dry-run/apply flow

Flow для state-changing operations:

1. Protocol manager строит `RemoteOperation`.
2. Runner валидирует operation contract.
3. Runner строит `OperationPlan` без выполнения изменений.
4. Верхний слой показывает plan preview или сохраняет его для API/UI.
5. Если операция destructive, верхний слой требует confirmation.
6. Runner выполняет `apply`.
7. Runner пишет audit events: `planned`, `started`, `step_succeeded`, `step_failed`, `completed` или `failed`.
8. При failure runner возвращает structured result и recovery note.

Read-only операции могут выполнять `apply` без отдельного confirmation, но все равно проходят validation, timeout и redaction.

## SSH host key policy

Production-mode не должен автоматически доверять неизвестному SSH host key.

Модель:

- при первом добавлении VPS runner получает host key fingerprint;
- оператор подтверждает fingerprint через enrollment-flow;
- подтвержденный fingerprint сохраняется как часть server identity;
- при mismatch операция блокируется;
- re-enrollment требует отдельного audit event и elevated permission;
- lab/dev-mode может иметь explicit insecure setting, но он должен быть видимым и недоступным по умолчанию в production.

Сообщение об ошибке при mismatch не должно предлагать автоматическое продолжение без проверки.

## Sudo и секреты

Запрещено:

- подставлять sudo password в shell command string;
- логировать команду вместе с секретом;
- возвращать raw stderr/stdout без redaction;
- хранить private key или password в operation payload;
- отдавать secret values через generic debug endpoint.

Предпочтительная модель:

- SSH keys вместо password-based SSH;
- отдельный системный пользователь;
- ограниченные sudoers rules для допустимых команд;
- secret storage возвращает секрет только внутри execution boundary;
- audit пишет `secret_ref`, но не secret value;
- runner передает секреты через безопасный механизм выбранной платформы, а не через shell interpolation.

Если на первом этапе `amn2` не может отказаться от password-based SSH, design должен явно пометить режим как degraded и требовать более строгую redaction, тесты и предупреждение в operator UX.

## Redaction policy

Redaction применяется до записи или возврата:

- command preview;
- actual command;
- stdout;
- stderr;
- exceptions;
- structured result;
- audit payload;
- API error response.

Минимальные redaction sources:

- `secret_refs`;
- known tokens and token prefixes;
- SSH private key markers;
- VPN private keys;
- proxy passwords;
- Telegram/API tokens;
- generated client configs;
- user-provided password-like fields.

Redaction failure считается security bug. Тесты должны проверять, что секрет не появляется ни в одном observable output.

## Audit model

Audit event должен отвечать на вопросы:

- кто инициировал операцию;
- на каком сервере;
- какой operation id;
- какой risk class;
- какой plan был подтвержден;
- когда началось и закончилось выполнение;
- какие шаги прошли;
- где произошел failure;
- какой recovery note показан оператору.

Audit event не должен содержать:

- raw command с секретом;
- private keys;
- client configs;
- passwords;
- bearer/share tokens;
- full stdout/stderr без redaction.

Для destructive operations audit event создается до фактического выполнения, чтобы попытка операции тоже оставалась видимой.

## Manager contract

Будущий protocol/service manager не должен напрямую выполнять SSH-команды. Он должен работать через contract:

```text
ProtocolManager
  detect(server) -> DetectionResult
  status(server) -> StatusResult
  plan(operation_input) -> RemoteOperation
  apply(operation, runner) -> OperationResult
  rollback_note(operation, failure) -> RecoveryNote
```

`detect` и `status` по умолчанию должны быть read-only. Любой auto-fix во время detect запрещен без отдельной operation.

## Result model

Runner возвращает structured result:

```text
OperationResult
  operation_id
  risk_class
  status: planned | completed | failed | cancelled | blocked
  started_at
  finished_at
  steps
  redacted_stdout_summary
  redacted_stderr_summary
  audit_event_ids
  recovery_note
```

Для API/UI важно возвращать краткое redacted summary, а не поток raw logs.

## Тестовая стратегия

Минимальные тесты перед production-внедрением:

- fake runner строит plan и не выполняет реальные команды;
- destructive operation без confirmation получает `blocked`;
- host key mismatch блокирует operation;
- sudo password не появляется в command preview, result, exception и audit;
- stdout/stderr проходят redaction;
- unknown risk class отклоняется;
- operation с secret value в `inputs` отклоняется;
- allowed exit codes применяются per step;
- timeout возвращает structured failure и recovery note;
- partial failure создает audit event и recovery note;
- `detect` manager не выполняет state-changing actions;
- API layer не отдает raw command output для secret-read operations.

Acceptance gate: ни одна state-changing operation не добавляется в `amn2`, пока для нее нет plan preview, audit event и fake-runner теста.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Открыть текущий репозиторий `amn2` и найти существующие remote/server operations.
2. Составить inventory: какие операции read-only, secret-read, remote-exec и destructive.
3. Ввести минимальные типы `RemoteOperation`, `OperationPlan`, `OperationResult`.
4. Добавить fake runner и тесты redaction/confirmation.
5. Перевести одну безопасную read-only операцию на runner.
6. Перевести одну state-changing, но не destructive операцию.
7. Только после этого проектировать destructive operations.

## Решение для lab

Статус: `design-candidate`.

Этот spec можно использовать как первый вход в implementation plan после review текущего `amn2`. До этого он остается исследовательским design artifact в `vpn-ops-lab`.

## Источники

- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- Manager architecture deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md](../../../research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md)
- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
