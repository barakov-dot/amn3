# AMN3 Local Agent Write Settings Contract

Этот документ фиксирует будущий settings contract для включения первого `agent:clients:write` slice после `GO-1`.
Он не меняет `.env.example`, не расширяет текущий read-only token и не включает write routes. До реального VPS smoke
активным остается только read-only Local Agent.

Связанные документы:

- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`
- `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`
- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md`
- `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`

## 1. Current invariant

Текущий invariant до VPS:

```text
LOCAL_AGENT_WRITE_ENABLED=false remains default
LOCAL_AGENT_TOKEN_SCOPES remains read-only
agent:clients:write must not be added to LOCAL_AGENT_TOKEN_SCOPES
VPS smoke required
no write routes
```

`LOCAL_AGENT_TOKEN_SCOPES` остается только для первого read-only slice:

```text
agent:health,agent:read,agent:protocols:read
```

Если туда попадает `agent:clients:write`, это ошибка конфигурации и `tests/config/test_settings.py` должен продолжать
падать с `LOCAL_AGENT_TOKEN_SCOPES`.

## 2. Future write mode gate

Включение write mode разрешено только после `GO-1` из `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`:

```text
LOCAL_AGENT_WRITE_ENABLED=true only after GO-1
```

Даже после `GO-1` включение должно быть явным:

- отдельный commit или rollout step;
- отдельный write token hash;
- отдельный controller token path;
- отдельные tests, которые доказывают, что read-only token не получил write scope;
- rollback проверен до первой mutation.

## 3. Dedicated write token set

Будущий write mode должен использовать dedicated write token set, а не расширять read-only token:

```text
LOCAL_AGENT_WRITE_TOKEN_ID=local-write-controller
LOCAL_AGENT_WRITE_TOKEN_HASH=sha256:<generated-write-token-hash>
LOCAL_AGENT_WRITE_TOKEN_OWNER=local-write-controller
LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write
LOCAL_AGENT_WRITE_TOKEN_EXPIRES_AT=<optional-utc-expiry>
LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH=/opt/amn2/secrets/local-agent-write.token
```

Правила:

- `LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write` без read-only scopes;
- read-only token не получает `agent:clients:write`;
- write token не используется для `/agent/health`, `/agent/runtime` и `/agent/protocols`;
- оба token hash хранятся как `sha256:<64 hex chars>`;
- raw token хранится только в отдельном root-readable secret file на VPS;
- controller читает raw write token из `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`;
- raw token не попадает в `.env`, docs, logs, screenshots, issue comments или bot messages.

## 4. Settings validation

Будущий код должен менять следующие файлы:

- `app/config/settings.py` - добавить explicit write settings и validators;
- `app/agent/config.py` - собрать read-only token и write token отдельно;
- `app/agent/auth.py` - оставить scope check через `missing_scope`;
- `tests/config/test_settings.py` - доказать запреты и разрешения;
- `tests/agent/test_config.py` - доказать, что token set разделен;
- `tests/test_file_hygiene.py` - оставить safe defaults в `.env.example` и `deploy/examples/.env.production.example`.

Минимальные проверки:

- `LOCAL_AGENT_WRITE_ENABLED=false` допускает отсутствие write token settings;
- `LOCAL_AGENT_WRITE_ENABLED=true` требует `LOCAL_AGENT_WRITE_TOKEN_HASH`;
- `LOCAL_AGENT_WRITE_ENABLED=true` требует `LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write`;
- write token scopes не должны содержать `agent:health`, `agent:read`, `agent:protocols:read`;
- read-only token scopes не должны содержать `agent:clients:write`;
- invalid write token hash rejected;
- `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH` обязателен для controller write flow;
- `.env.example` и `deploy/examples/.env.production.example` остаются с `LOCAL_AGENT_WRITE_ENABLED=false`.

## 5. Auth behavior

Expected behavior после реализации:

| Token | Allowed routes | Forbidden routes | Expected error |
| --- | --- | --- | --- |
| read-only token | `/agent/health`, `/agent/runtime`, `/agent/protocols` | `/agent/clients*` | `missing_scope` or route disabled |
| write token | `/agent/clients/dry-run`, `/agent/clients`, `/agent/clients/{id}` | read-only routes | `missing_scope` |
| expired write token | none | all write routes | `expired_token` |
| revoked write token | none | all write routes | `revoked_token` |

До `LOCAL_AGENT_WRITE_ENABLED=true` write routes должны оставаться недоступны даже с валидным write token.

## 6. Secret boundaries

Settings contract не должен раскрывать:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- raw confirmation nonce;
- full `.env`;
- SSH credentials.

Write settings отвечают только за authorization boundary. Delivery secrets и client config выдаются отдельным flow, не
через mutation endpoint.

## 7. TDD checklist for implementation

Когда после `GO-1` начнем кодовый slice, идти в таком порядке:

1. В `tests/config/test_settings.py` добавить RED-тест, что `LOCAL_AGENT_WRITE_ENABLED=true` требует
   `LOCAL_AGENT_WRITE_TOKEN_HASH`.
2. В `app/config/settings.py` добавить поля write token и validator.
3. Добавить тест, что `LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:clients:write` все еще rejected.
4. Добавить тест, что `LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write` accepted только при write enabled.
5. В `tests/agent/test_config.py` добавить тест, что `build_agent_tokens()` возвращает read-only token и write token
   отдельно.
6. В `app/agent/config.py` добавить сборку второго `AgentToken`, не смешивая scopes.
7. В `tests/test_file_hygiene.py` оставить проверку, что examples не содержат `LOCAL_AGENT_WRITE_ENABLED=true` и
   `agent:clients:write`.
8. Прогнать `tests/config/test_settings.py tests/agent/test_config.py tests/agent/test_policy.py tests/test_file_hygiene.py`.

## 8. Current status

Контракт зафиксирован локально. Реальные settings fields для write token пока не добавляются, потому что `GO-1` еще не
получен и текущий release gate должен продолжать доказывать, что write scope выключен.
