# `amn2`: API token lifecycle gate

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/api-token-lifecycle-gate
```

Production commit:

```text
c2ba646 Add API token lifecycle gate
```

Stacked variant, если первым объединяется route/auth binding slice:

```text
branch: codex/api-token-lifecycle-gate-stacked
base: codex/route-auth-binding-tests
commit: 256d0c0 Add API token lifecycle gate
```

## Что добавлено

В `amn2` добавлен local-only lifecycle gate для scoped API tokens:

- `create_route_api_token()` требует явный `expires_at` для route-connected token creation;
- `authenticate_api_token()` учитывает owner inheritance: token с `owner_user_id` проходит только если текущий owner status равен `active`;
- `revoke_api_token()` возвращает idempotent safe event без раскрытия raw token или hash;
- `rotate_api_token()` реализует create-new-then-revoke-old и возвращает новый raw token только через one-time issue object;
- таблица `api_tokens` получила `revoke_reason` и `rotated_from_token_id`;
- `get_valid_api_token()` возвращает `owner_status` для эффективной проверки владельца;
- docs/API_TOKEN_POLICY.ru.md и docs/DATA_MODEL.ru.md обновлены.

## Граница среза

Срез не добавляет `/api/*` routes, не включает `config:read`, не добавляет write/remote-exec/destructive scopes, не меняет Local Agent clients/configs/write lifecycle и не трогает live VPS.

Это подготовка перед read-only API route shell и будущими bearer-token integrations. Token lifecycle теперь есть на уровне service/repository contract, но route exposure остается отдельным gated slice.

## Проверка

Focused:

```text
tests/services/test_api_tokens.py
tests/db/test_repositories.py::test_api_token_lifecycle_stores_hash_scopes_and_revoke_state
tests/db/test_repositories.py::test_api_token_rotation_lineage_is_stored_without_raw_token
result: 12 passed
```

Broader auth/db/security:

```text
tests/services/test_api_tokens.py tests/db/test_repositories.py tests/security/test_surface_policy.py tests/agent/test_auth.py -v
result: 58 passed
```

Full local suite:

```text
tests -v
result: 548 passed, 1 StarletteDeprecationWarning
```

Также `git diff --check` прошел без замечаний.

Известное окружение Windows иногда печатает ignored pytest temp cleanup `PermissionError` после успешного exit code `0`; это не меняет результат тестов.

## Следующее решение

Следующий local-only кандидат из очереди: manager config export contract. Read-only metrics/API route shell лучше держать после VPS evidence или после отдельного решения, потому что он начнет использовать bearer-token surface.
