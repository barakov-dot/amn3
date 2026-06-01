# AMN3 Write API Audit Model

Этот документ фиксирует audit contract для будущего `agent:clients:write` slice. Модель нужна до включения mutation
endpoints, чтобы web admin, Telegram bot и CLI одинаково записывали, кто сделал dry-run, кто подтвердил mutation, что
изменилось, где rollback reference и какие секреты нельзя сохранять.

Кодовая основа:

- `app/agent/write_audit.py`
- `tests/agent/test_write_audit.py`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md`
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`

## 1. Gate

Audit model можно держать локально до VPS smoke. Она не включает write routes, не включает `LOCAL_AGENT_WRITE_ENABLED` и
не создает storage layer. Реальная запись audit events подключается только после зеленого read-only VPS smoke и после
отдельного решения по месту хранения.

## 2. Actor surfaces

Разрешенные значения `actor_surface`:

| Surface | Meaning |
| --- | --- |
| `web_admin` | Оператор работает через web admin. |
| `telegram_bot` | Оператор подтверждает действие через Telegram bot. |
| `cli` | Оператор запускает локальную CLI-команду. |

Другие surfaces, включая public API, не входят в первый write slice.

## 3. Result states

Разрешенные значения `result_state`:

| State | Meaning |
| --- | --- |
| `dry_run_planned` | Preflight выполнен, runtime state не изменен. |
| `mutation_applied` | Peer apply/create/update завершен. |
| `mutation_revoked` | Peer revoke завершен. |
| `mutation_failed` | Mutation не прошла или runtime state сомнителен. |
| `rollback_planned` | Rollback action рассчитан и показан оператору. |
| `rollback_applied` | Rollback выполнен и зафиксирован. |

После `mutation_failed` следующий retry должен начинаться с нового dry-run.

## 4. Required audit fields

Минимальная запись:

- `audit_id`;
- `operation_id`;
- `actor_surface`;
- `actor_id`;
- `server_alias`;
- `user_id`;
- `device_id`;
- `device_label`;
- `client_id`;
- `peer_public_key_fingerprint`;
- `dry_run_reference`;
- `result_state`;
- `risk_class`;
- `rollback_reference`;
- `message`;
- `details`.

Полный `peer_public_key` не должен храниться в audit record. Для связи используется `peer_public_key_fingerprint`.

## 5. Redaction rules

Audit не сохраняет:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- содержимое `.env`;
- полный WireGuard/AmneziaWG config block.

Если эти значения появились в `message`, `details` или planned command, они должны быть заменены на `[REDACTED]` до
сериализации записи. `repr()` audit event также должен быть безопасным.

## 6. Surface mapping

Web admin:

- пишет `dry_run_planned` после preview;
- пишет `mutation_applied`, `mutation_revoked` или `mutation_failed` после confirm;
- показывает audit id оператору.

Telegram bot:

- пишет actor id в форме Telegram user id или internal admin id;
- не пишет raw chat payload целиком;
- не пишет secrets из callback data.

CLI:

- пишет actor id из локального operator label или системного пользователя;
- по умолчанию выводит только redacted audit record;
- JSON output проходит те же redaction rules.

## 7. Storage note

Первый локальный контракт не выбирает окончательное хранилище. Подходящие варианты после VPS smoke:

- SQLite table рядом с web admin state;
- append-only JSONL с ротацией и правами `0600`;
- отдельная таблица в существующем application DB, если она уже есть в production deployment.

Выбор storage должен быть отдельным маленьким slice с миграцией, backup policy и тестами на redaction.
