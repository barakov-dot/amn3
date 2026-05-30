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

## Уточнение после `amn2` inventory

2026-05-30 был сделан первый read-only inventory текущих remote operations в `amn2`: [research/amn2/remote-operations-inventory.md](../../../research/amn2/remote-operations-inventory.md).

Найденный baseline важен для этого spec:

- `amn2` уже держит live apply выключенным по умолчанию через `VPS_APPLY_ENABLED=false`.
- CLI `server apply-peer` и `server revoke-peer` требуют явный `--dry-run` или `--apply`.
- Read-only server checks уже имеют command allowlist через `ensure_read_only_command()`.
- Web health check защищен web-admin session + CSRF и пишет локальный audit action.
- Peer apply передает preshared key через stdin, а не через remote command string.
- Docker live apply/revoke/traffic collection намеренно заблокированы, пока не описан persistent config path.

Значит первый production design должен не изобретать remote execution с нуля, а аккуратно обобщить эти уже хорошие guardrails в единый contract layer.

## Scope

Входит в scope:

- модель remote operation;
- risk classes;
- plan/dry-run/apply flow;
- command policy for read-only, telemetry and state-changing steps;
- SSH host key enrollment;
- sudo policy без пароля в shell command string;
- redaction для logs, stdout/stderr, errors и audit payload;
- audit event model;
- partial-failure and local/remote consistency model;
- secret-safe CLI requirements;
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
| `read-only-remote` | выполняет read-only команду на VPS | `systemctl is-active`, `ss -lun`, `docker ps` | command allowlist, timeout, redaction |
| `read-only-remote-telemetry` | читает operational/activity metrics и пишет локальные snapshots | `awg show awg0 dump` | command allowlist, privacy review, local write audit policy |
| `secret-read` | читает секретный материал | client config, private key metadata, proxy credentials | scope/role check, redaction, audit |
| `state-write` | меняет локальный или удаленный state без remote exec | запись metadata, enable flag | audit, validation |
| `remote-state-write` | меняет состояние VPS через remote command | `awg set peer`, service reload, config write | plan, audit before/after, timeout, redaction, rollback note |
| `remote-exec` | выполняет команду на VPS без гарантии read-only | restart service, create directory, upload config | plan, audit, timeout, redaction |
| `destructive-remote` | может удалить, сломать или заблокировать доступ | clear server, uninstall protocol, firewall rewrite, reboot | plan preview, confirmation, audit before/after, recovery note |

Если операция подходит под несколько классов, выбирается самый строгий.

## Operation contract

Каждая remote operation описывается структурой с обязательными полями. Имена полей можно адаптировать под язык `amn2`, но смысл должен сохраниться.

```text
RemoteOperation
  id: stable operation name, например "wireguard.install"
  risk_class: read-only | read-only-remote | read-only-remote-telemetry | secret-read | state-write | remote-state-write | remote-exec | destructive-remote
  run_id: unique operation attempt id
  idempotency_key: optional key for retry/resume
  server_id: internal server reference
  actor_id: user, token или system actor
  actor_auth_method: session | telegram-admin | scoped-token | cli | system
  inputs: validated non-secret inputs
  secret_refs: ссылки на секреты, не сами значения
  local_side_effects: DB rows, audit rows, snapshots or files changed locally
  remote_side_effects: files, services, ports, containers, peers, firewall rules
  preconditions: host key, runtime, package, service and config checks
  command_policy: read-only allowlist, telemetry allowlist or state-write command set
  commands: typed command steps or internal runner actions
  timeout_policy: per step and whole operation
  allowed_exit_codes: explicit list per command
  consistency_policy: what happens if remote succeeds and local step fails
  redaction_policy: какие поля и patterns скрывать
  audit_summary: краткое описание без секретов
  rollback_note: что делать при partial failure
  confirmation_required: true для destructive-remote операций
```

`inputs` не должны содержать password, private key, token, raw config или client secret. Для них используются `secret_refs`, которые разрешаются только внутри безопасного execution boundary.

Для текущего `amn2` это означает: PSK для peer apply остается secret material. Его нельзя принимать как обычный CLI argument в будущем runner API; безопасные варианты - stdin, one-shot prompt, file descriptor или secret reference, который разрешается внутри execution boundary.

## Command step contract

Каждый remote step должен быть typed, а не просто raw string. На первом этапе достаточно такой модели:

```text
CommandStep
  id: stable step name
  command_template: command with typed variables
  args: validated non-secret args
  stdin_secret_ref: optional secret reference for stdin
  expected_remote_effect: none | peer-added | peer-removed | service-reloaded | file-written | firewall-changed
  allowed_exit_codes: explicit list
  timeout_seconds
  output_policy: discard | summarize | redact-and-store
  command_policy_class: read-only | telemetry | state-write
```

Правило: state-changing step не может быть исполнен через read-only runner path, а telemetry step не может обходить command allowlist. Это закрывает gap из текущего `AwgDumpTrafficCollector`, где команда read-only по смыслу, но не проходит через общий `ensure_read_only_command()`.

## Plan/dry-run/apply flow

Flow для state-changing operations:

1. Protocol manager строит `RemoteOperation`.
2. Runner валидирует operation contract.
3. Runner строит `OperationPlan` без выполнения изменений.
4. Верхний слой показывает plan preview или сохраняет его для API/UI.
5. Если операция `destructive-remote`, верхний слой требует confirmation.
6. Runner создает audit event до первого remote side effect.
7. Runner выполняет `apply`.
8. Runner пишет audit events: `planned`, `started`, `step_succeeded`, `step_failed`, `completed` или `failed`.
9. При failure runner возвращает structured result, consistency status и recovery note.

Read-only операции могут выполнять `apply` без отдельного confirmation, но все равно проходят validation, timeout и redaction.

Для `amn2` в ближайшем implementation plan это должно сохранить текущий UX: dry-run остается быстрым и понятным, а live operations остаются opt-in.

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

Текущий `SystemSshClient` уже блокирует non-interactive password backend с exit code `125`. Runner должен сохранить это поведение как safe default: password auth не становится live backend без отдельного design review.

## Secret-safe CLI

CLI не должен принимать long-lived or high-value secrets как обычные flags, потому что shell history и process arguments являются отдельной exposure surface.

Правила:

- запретить новые flags вида `--password`, `--private-key`, `--preshared-key`, если значение передается inline;
- разрешить `--secret-stdin`, one-shot prompt или secret reference;
- dry-run не должен требовать raw secret value;
- live apply должен принимать secret value только внутри execution boundary;
- тесты должны проверять command preview, result, exception и audit без raw secret.

Для существующего `server apply-peer --preshared-key` это не значит срочно ломать CLI. Это значит, что перенос в `RemoteOperationRunner` должен заменить этот канал до расширения live operations.

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

Для `destructive-remote` operations audit event создается до фактического выполнения, чтобы попытка операции тоже оставалась видимой.

## Consistency and partial failure

Runner должен явно описывать локально-удаленную консистентность. Для `amn2` это не абстракция: в текущем approve flow local DB transaction откатывается, если peer apply падает, но если remote apply уже прошел, а последующий local audit/DB step упадет, нужен recovery path.

Минимальная модель:

```text
ConsistencyPolicy
  local_first | remote_first | two_phase_best_effort | read_only
  remote_success_local_failure_note
  local_success_remote_failure_note
  retry_safety: safe | unsafe | requires_inspection
  resume_key: optional stable operation key
```

Требования:

- state-changing remote operation получает `run_id`;
- audit пишет before/after event без секретов;
- result явно говорит `consistent`, `remote_changed_local_failed`, `local_changed_remote_failed` или `unknown`;
- rollback note должен быть конкретным: какая команда dry-run/read-only check помогает оператору проверить состояние;
- reset нескольких устройств не должен скрывать partial success: если один peer удален remote-side, а следующий remove упал, result должен перечислить redacted step states.

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
  run_id
  risk_class
  status: planned | completed | failed | cancelled | blocked
  consistency_status
  started_at
  finished_at
  steps
  redacted_stdout_summary
  redacted_stderr_summary
  audit_event_ids
  recovery_note
```

Для API/UI важно возвращать краткое redacted summary, а не поток raw logs.

## Mapping текущего `amn2`

| Current surface | Current class | Runner migration target | First useful test |
| --- | --- | --- | --- |
| `server check` | `read-only-remote` | wrap existing allowlist as `CommandPolicy` | unknown command blocked before SSH |
| Web health run | `read-only-remote + local-state-write` | operation result stored as health snapshot + audit | CSRF/session + audit without raw stderr |
| `collect-traffic` | `read-only-remote-telemetry + local-state-write` | telemetry command policy + privacy class | telemetry command cannot use shell control tokens |
| Bot approve with live apply | `remote-state-write + local-state-write + secret-read` | peer apply operation with PSK secret ref | remote success/local failure has recovery note |
| CLI apply-peer | `remote-state-write + secret input` | secret-safe CLI wrapper around peer apply operation | PSK absent from argv-style preview/result |
| Bot revoke/reset | `remote-state-write + local-state-write` | peer revoke operation with partial-failure state | reset reports per-peer partial result |
| Docker live operations | blocked | separate Docker manager design | blocked until persistent config path is set |

## Тестовая стратегия

Минимальные тесты перед production-внедрением:

- fake runner строит plan и не выполняет реальные команды;
- `destructive-remote` operation без confirmation получает `blocked`;
- host key mismatch блокирует operation;
- sudo password не появляется в command preview, result, exception и audit;
- stdout/stderr проходят redaction;
- unknown risk class отклоняется;
- operation с secret value в `inputs` отклоняется;
- allowed exit codes применяются per step;
- timeout возвращает structured failure и recovery note;
- partial failure создает audit event и recovery note;
- remote success followed by local failure returns explicit consistency status;
- reset-like multi-step operation reports per-step partial success without leaking secrets;
- telemetry command uses shared allowlist and rejects shell control tokens;
- CLI secret input is not represented as plain flag in plan/result;
- Docker apply/revoke remains blocked until manager defines persistent config path and backup behavior;
- `detect` manager не выполняет state-changing actions;
- API layer не отдает raw command output для secret-read operations.

Acceptance gate: ни одна state-changing operation не добавляется в `amn2`, пока для нее нет plan preview, audit event и fake-runner теста.

## Путь внедрения в `amn2`

Рекомендуемый порядок:

1. Использовать уже созданный [remote operations inventory](../../../research/amn2/remote-operations-inventory.md) как baseline.
2. Ввести минимальные типы `RemoteOperation`, `CommandStep`, `OperationPlan`, `OperationResult`.
3. Добавить fake runner и тесты redaction/confirmation/consistency.
4. Перевести одну безопасную read-only операцию на runner: лучший кандидат - server health check.
5. Перевести telemetry read-only operation: `collect-traffic`, чтобы закрыть shared command policy gap.
6. Перевести одну state-changing, но узкую операцию: peer apply или peer revoke для `host_systemd`.
7. Заменить secret-bearing CLI input для peer apply на stdin/prompt/secret ref.
8. Только после этого проектировать destructive operations или Docker live apply/revoke.

## Решение для lab

Статус: `design-candidate`.

Этот spec можно использовать как первый вход в implementation plan после review текущего `amn2`. До этого он остается исследовательским design artifact в `vpn-ops-lab`.

## Источники

- Feature gap: [research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md](../../../research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md)
- Manager architecture deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md](../../../research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md)
- Auth/secrets deep-dive: [research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md](../../../research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md)
- `amn2` remote operations inventory: [research/amn2/remote-operations-inventory.md](../../../research/amn2/remote-operations-inventory.md)
- `amn2` config delivery inventory: [research/amn2/config-delivery-inventory.md](../../../research/amn2/config-delivery-inventory.md)
- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
