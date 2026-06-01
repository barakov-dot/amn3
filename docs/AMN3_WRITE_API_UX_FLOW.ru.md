# AMN3 Write API UX Flow

Этот документ фиксирует будущий пользовательский и API-поток первого write-среза Local Agent. Цель: заранее
согласовать, как web admin, Telegram bot и CLI будут вести оператора через безопасную цепочку
`dry-run -> confirmation -> apply/revoke -> audit -> rollback`.

Документ не включает write routes, не включает `LOCAL_AGENT_WRITE_ENABLED`, не добавляет mutation endpoints и не меняет
production defaults. Это локальный продуктовый контракт перед VPS gate.

Связанный audit contract: `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`.
Связанный preflight/confirmation contract: `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`.
Локальный release gate до VPS: `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`.
Связанная identity model: `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`.
Связанный runtime adapter plan: `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`.
Связанный controller client plan: `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md`.
Связанный web admin preflight UX plan: `docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md`.
Связанный first VPS mutation packet: `docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md`.

## 1. Gate

Write API остается закрытым, пока не выполнены все условия:

- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md` заполнен с решением `go`;
- Local Agent read-only smoke на VPS зеленый или `degraded` объяснен;
- Local Agent слушает только `127.0.0.1:3031`;
- web admin видит Local Agent без raw token;
- rollback проверен;
- logs и UI не раскрывают raw token, private key, PSK, QR, `vpn://` или полный client config;
- отдельный scope `agent:clients:write` готов, но не добавлен в read-only token.

До этого:

```text
LOCAL_AGENT_WRITE_ENABLED=false
VPS smoke required
write routes remain disabled
/agent/clients* remains rejected by policy
```

## 2. Planned operations

Операции синхронизированы с `app/agent/write_policy_matrix.py`:

| Operation | Surface action | Route shape | Scope | Confirmation | Notes |
| --- | --- | --- | --- | --- | --- |
| `local_agent.clients.apply.dry_run` | preview create/update peer | `POST /agent/clients/dry-run` | `agent:clients:write` | no | Без изменения runtime state. |
| `local_agent.clients.apply` | create/update peer | `POST /agent/clients` | `agent:clients:write` | yes | Только после успешного preflight. |
| `local_agent.clients.revoke` | revoke peer | `DELETE /agent/clients/{id}` | `agent:clients:write` | yes | Сначала показать revoke preview на стороне controller. |

Первый slice не должен превращаться в root API для всего сервера. Backup/import/reboot, массовые операции и выдача
готовых конфигов остаются вне этого потока.

## 3. Shared flow

### Step 1. Select operation

Оператор выбирает действие:

- добавить устройство пользователю;
- обновить peer/device binding;
- отозвать устройство;
- повторить неуспешную mutation после диагностики.

Controller нормализует ввод в `AgentPeerApplyRequest` или `AgentPeerRevokeRequest`. Некорректные поля дают
`validation_failed` до обращения к Local Agent.

Стабильные поля `user_id`, `device_id`, `device_label`, `client_id`, `server_alias` и `peer_public_key_fingerprint`
описаны в `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`. UI может показывать labels, но mutation подтверждается по
стабильным идентификаторам.

### Step 2. Dry-run / preflight

Для apply поток всегда начинается с `local_agent.clients.apply.dry_run`.

Dry-run возвращает только безопасные поля:

- `operation_id`;
- `status`;
- `dry_run`;
- `risk_class`;
- `consistency_status`;
- `message`;
- `planned_commands`.

Ответ не должен содержать private key, PSK, QR, `vpn://`, raw token или полный client config.

Для revoke первый UI-экран также показывает preview: какой `client_id` и `peer_public_key` будут отозваны, какой runtime
будет затронут, и какой rollback возможен. Если после VPS smoke понадобится отдельный revoke dry-run endpoint, он должен
получить собственную строку policy matrix перед реализацией.

### Step 3. Confirmation

Mutation запрещена без подтверждения. Подтверждение должно показывать:

- целевой сервер;
- пользователя или client/device label;
- operation id;
- risk class `state-write`;
- результат последнего dry-run/preflight;
- отсутствие public bind для Local Agent;
- краткий rollback hint.

Confirmation token или UI nonce живет коротко и не содержит секретов. Повторный apply без свежего preflight должен
получить `preflight_required`.
Формальные поля dry-run reference, confirmation nonce и expiry описаны в
`docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`.

### Step 4. Apply / revoke

После подтверждения controller вызывает будущую write operation:

- `local_agent.clients.apply` для создания или обновления peer;
- `local_agent.clients.revoke` для отзыва peer.

Mutation должна быть узкой и атомарной настолько, насколько позволяет runtime. Если runtime возвращает неполный или
сомнительный статус, пользователь получает `runtime_degraded`, а UI предлагает диагностику вместо повторного клика.

### Step 5. Audit

Каждая операция audit-required. Audit record должен содержать:

- поля и states из `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`;
- timestamp;
- actor surface: `web_admin`, `telegram_bot` или `cli`;
- actor id без лишних персональных данных;
- operation id;
- server alias;
- client id;
- peer public key fingerprint;
- dry-run result id или hash;
- mutation result;
- rollback reference.

Audit не хранит raw token, private key, PSK, QR, `vpn://` и полный client config.

### Step 6. Rollback

Rollback path показывается до mutation и фиксируется после mutation. Для первого slice достаточно:

- проверить, что revoke может убрать созданный peer;
- записать redacted planned rollback action;
- дать оператору понятную команду или кнопку rollback после `mutation_failed`;
- не обещать автоматический rollback там, где runtime state неизвестен.

## 4. Web admin

Web admin должен быть основным операторским интерфейсом.

Поток:

1. Оператор открывает карточку сервера.
2. Блок Local Agent показывает read-only status, runtime и protocols.
3. Оператор выбирает пользователя и устройство.
4. Кнопка mutation запускает dry-run, а не apply.
5. UI показывает preview: operation, target, risk, planned commands, degraded reasons.
6. Confirm доступен только после успешного dry-run.
7. Apply/revoke показывает audit id и следующий безопасный шаг.
8. Ошибка показывает public message и ссылку на diagnostics, без секретов.

Текст кнопок должен быть коротким и операционным: `Dry-run`, `Confirm apply`, `Confirm revoke`, `View audit`,
`Rollback hint`. Никаких raw token или client configs в HTML.

## 5. Telegram bot

Telegram bot должен быть осторожнее web admin, потому что чат легко переслать или случайно показать.

Поток:

1. Пользователь выбирает сервер и устройство через inline buttons.
2. Bot запускает dry-run и показывает короткий summary.
3. Для mutation требуется явная inline-confirmation.
4. Confirmation истекает по времени.
5. После apply/revoke bot показывает результат и audit id.
6. При ошибке bot показывает только safe public message.

Bot не отправляет private key, PSK, QR, `vpn://`, raw token или полный config в рамках write flow. Delivery config
остается отдельным контролируемым процессом.

## 6. CLI

CLI нужен для оператора и диагностики, а не для массовой автоматизации первого slice.

Планируемая форма команд:

```bash
python -m app.cli agent clients dry-run --client-id alice-phone --peer-public-key <pub> --vpn-ip 10.8.0.10
python -m app.cli agent clients apply --client-id alice-phone --peer-public-key <pub> --vpn-ip 10.8.0.10 --confirm
python -m app.cli agent clients revoke --client-id alice-phone --peer-public-key <pub> --confirm
```

CLI должен по умолчанию печатать redacted output. JSON output допустим только если он проходит те же правила redaction.

## 7. Error handling

Обязательные error contracts:

| Code | UX handling |
| --- | --- |
| `validation_failed` | Подсветить поле и не обращаться к Local Agent. |
| `missing_or_invalid_token` | Показать оператору, что controller token недоступен или неверен. |
| `missing_scope` | Показать, что token не содержит `agent:clients:write`; не предлагать auto-fix. |
| `preflight_required` | Потребовать свежий dry-run. |
| `runtime_degraded` | Остановить mutation и предложить diagnostics. |
| `mutation_failed` | Показать redacted failure, audit id и rollback hint. |

Повтор mutation после `runtime_degraded` или `mutation_failed` должен требовать новый dry-run.

## 8. Implementation guardrails

Перед реальной реализацией endpoints нужно отдельным commit включить только то, что прошло VPS gate:

- feature flag `LOCAL_AGENT_WRITE_ENABLED`;
- отдельный token с `agent:clients:write`;
- route registration для `/agent/clients*`;
- audit storage;
- tests на запрет secret leakage;
- tests на то, что read-only token не может выполнять write operations.

Не делать в первом write slice:

- public Local Agent;
- broad admin API;
- backup/import/reboot;
- массовое изменение peers;
- выдачу конфигов через mutation response;
- silent mutation без dry-run и confirmation.
