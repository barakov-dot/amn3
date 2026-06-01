# AMN3 Write Audit Storage Decision

Этот ADR фиксирует, где хранить future write audit events для первого `agent:clients:write` slice. Решение нужно до
реальных mutation endpoints, чтобы apply/revoke не появились без надежного следа, rollback reference и redaction
boundary.

Связанные документы:

- `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`
- `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`
- `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`
- `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`

## Decision

Decision: application SQLite DB.

Первое production-хранилище для write audit events - та же application SQLite DB, которая задается через
`DATABASE_PATH`. Новый storage slice должен добавить таблицу `local_agent_write_audit_events` в `app/db/schema.py` и
методы записи/чтения в `app/db/repositories.py`.

Коротко:

- `local_agent_write_audit_events` - authoritative audit trail для `agent:clients:write`;
- `admin_actions is not the write audit store`;
- `append-only JSONL mirror is fallback/export`, но не основной источник истины;
- Local Agent logs и `app.agent.audit.InMemoryAgentAuditSink` остаются diagnostic/runtime-only;
- audit write должен быть redacted до сериализации.

## Почему не `admin_actions`

`admin_actions` уже используется для операторских действий web/bot уровня: изменение пользователя, grant/revoke admin,
серверные действия из панели. Этого недостаточно для Local Agent mutation audit:

- нужны `operation_id`, `dry_run_reference`, `rollback_reference` и `result_state`;
- нужна связка с `peer_public_key_fingerprint`, а не с полным `peer_public_key`;
- нужен отдельный query path для первого write slice и будущих rollback views;
- нельзя смешивать UI command log и runtime mutation trail.

`admin_actions` может ссылаться на write audit id в будущем, но не заменяет `local_agent_write_audit_events`.

## Почему не JSONL как primary

Append-only JSONL прост, но для первого production slice хуже как основной storage:

- сложнее атомарно связать audit event с user/device/server state;
- хуже query UX для web admin;
- сложнее backup/restore consistency;
- сложнее dedup по `operation_id UNIQUE`;
- выше риск получить две конкурирующие истины: DB state и file log.

JSONL можно включить позже как mirror/export для расследований:

- файл вне репозитория, например `logs/local-agent-write-audit.jsonl`;
- только redacted payload;
- запись после успешной DB-записи;
- сбой mirror не должен отменять mutation, если authoritative DB event уже записан.

## Почему не отдельная SQLite DB

Отдельная SQLite DB добавляет миграции, backup, restore и permissions без реальной пользы для первого slice. Сейчас
controller уже использует application DB для `users`, `servers`, `devices`, `orders`, `admin_actions`,
`device_traffic_snapshots` и recovery tokens. Write audit должен жить рядом с этими сущностями, чтобы web admin мог
показывать историю user/device/server без cross-DB join.

## Table contract

Будущая таблица:

```text
local_agent_write_audit_events
```

Минимальные поля:

- `id INTEGER PRIMARY KEY AUTOINCREMENT`;
- `audit_id TEXT NOT NULL UNIQUE`;
- `operation_id TEXT NOT NULL UNIQUE`;
- `actor_surface TEXT NOT NULL`;
- `actor_id TEXT NOT NULL`;
- `result_state TEXT NOT NULL`;
- `risk_class TEXT NOT NULL DEFAULT 'state-write'`;
- `server_alias TEXT NOT NULL`;
- `server_id INTEGER`;
- `user_id INTEGER`;
- `device_id INTEGER`;
- `device_label TEXT`;
- `client_id TEXT NOT NULL`;
- `protocol TEXT NOT NULL DEFAULT 'amneziawg'`;
- `peer_public_key_fingerprint TEXT NOT NULL`;
- `dry_run_reference TEXT NOT NULL`;
- `rollback_reference TEXT NOT NULL`;
- `message TEXT NOT NULL`;
- `details_json TEXT NOT NULL DEFAULT '{}'`;
- `created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP`.

Required indexes:

- `operation_id UNIQUE`;
- `audit_id UNIQUE`;
- `(server_alias, created_at DESC)`;
- `(client_id, created_at DESC)`;
- `(user_id, created_at DESC)`;
- `(device_id, created_at DESC)`.

`details_json` хранит только redacted data. Для первого slice не хранить raw request, raw response, command stdout целиком
или full config.

## Secret boundaries

В `local_agent_write_audit_events` нельзя хранить:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- raw confirmation nonce;
- full `.env`;
- SSH credentials;
- no full peer_public_key.

Для peer identity хранится только `peer_public_key_fingerprint`. Если runtime adapter временно получает полный
`peer_public_key`, он должен быть заменен fingerprint до записи в DB.

## Write semantics

Первый implementation slice должен придерживаться таких правил:

- `record audit before mutation` для `dry_run_planned` и confirmation-ready preview;
- `if audit write fails, block mutation`;
- для apply/revoke сначала сохранить pre-mutation audit event или mutation intent;
- после runtime ответа записать `mutation_applied`, `mutation_revoked` или `mutation_failed`;
- если mutation завершилась неопределенно, записать `mutation_failed` с redacted diagnostic reference;
- rollback action получает отдельный event `rollback_planned` или `rollback_applied`;
- повторный request с тем же `operation_id` не должен создавать второй authoritative event.

Если DB недоступна до mutation, Local Agent write endpoint должен вернуть безопасную ошибку и не менять runtime. Если DB
стала недоступна после mutation, controller обязан остановить дальнейшие операции, собрать redacted incident summary и
потребовать ручную сверку runtime state.

## Backup and retention

Поскольку audit хранится в application SQLite DB, он попадает в существующий encrypted backup flow. Это ожидаемо:
write audit - часть production state, а не обычный log tail.

Минимальные правила:

- encrypted backup включает `local_agent_write_audit_events`;
- restore должен сохранять audit trail вместе с users/devices/servers;
- retention по умолчанию не удаляет write audit events в первом slice;
- future pruning/export policy добавляется отдельным решением после production наблюдений;
- redacted JSONL export можно генерировать из DB, но не использовать как restore source.

## Implementation targets

Кодовые файлы для будущего slice:

- `app/db/schema.py` - создать `local_agent_write_audit_events` и indexes;
- `app/db/repositories.py` - добавить write audit repository methods;
- `tests/db/test_repositories.py` - проверить insert, unique `operation_id`, redaction boundaries и query order;
- `app/agent/write_audit.py` - оставить source contract для redacted event shape;
- `tests/agent/test_write_audit.py` - продолжать проверять event contract и repr redaction;
- `app/agent/write_confirmation.py` - связывать `dry_run_reference` и confirmation with audit;
- `app/agent/api.py` - блокировать mutation при недоступном audit storage.

## First test checklist

Перед реальным mutation endpoint:

- schema создает таблицу и индексы идемпотентно;
- repository rejects duplicate `operation_id`;
- repository stores `peer_public_key_fingerprint`, not full public key;
- repository rejects blank `audit_id`, `operation_id`, `client_id`, `server_alias`;
- `details_json` проходит redaction;
- backup validation не ломается от новой таблицы;
- web admin может запросить последние events по user/device/server без секретов.

## Current status

Это решение не создает storage layer прямо сейчас. До VPS smoke оно только фиксирует выбранный путь и связывает будущий
implementation slice с существующей SQLite архитектурой. Реальная таблица появляется после `GO-1` из
`docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.
