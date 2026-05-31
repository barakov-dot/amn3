# Local Amnezia Agent

## Статус

Первый slice agent является read-only foundation. Он нужен, чтобы controller мог безопасно спросить сервер о состоянии runtime и поддерживаемых protocols без выдачи клиентских конфигов, QR, `vpn://`, private keys, PSK, backup payloads или выполнения write operations.

## Что включено

- `GET /agent/health`
- `GET /agent/version`
- `GET /agent/runtime`
- `GET /agent/protocols`
- hash-only bearer token auth
- explicit scopes
- route policy matrix
- fake runtime adapter for tests
- audit events for allowed read routes
- disabled public docs/openapi in the agent app

## Что не включено

- создание клиентов
- отключение или удаление клиентов
- выдача конфигов
- QR и `vpn://`
- backup/import
- reboot/reset
- Docker mutation
- public HTTP exposure

## Scopes

| Scope | Доступ |
| --- | --- |
| `agent:health` | `/agent/health`, `/agent/version` |
| `agent:read` | `/agent/runtime` |
| `agent:protocols:read` | `/agent/protocols` |

## Production правило

Agent считается привилегированным local runtime adapter. Его нельзя публиковать как общий root API к серверу. Любое расширение за пределы read-only routes требует route policy, secret inventory, audit plan и отдельного implementation plan.

## Production wiring

Agent disabled by default:

```text
LOCAL_AGENT_ENABLED=false
```

Минимальный production режим:

```text
LOCAL_AGENT_ENABLED=true
LOCAL_AGENT_HOST=127.0.0.1
LOCAL_AGENT_PORT=3031
LOCAL_AGENT_TOKEN_ID=local-controller
LOCAL_AGENT_TOKEN_OWNER=local-controller
LOCAL_AGENT_TOKEN_SCOPES=agent:health,agent:read,agent:protocols:read
LOCAL_AGENT_TOKEN_EXPIRES_AT=
LOCAL_AGENT_TOKEN_HASH=sha256:<generated-hash>
```

Raw token не хранится в `.env`. Сгенерировать hash:

```powershell
python -m app.cli agent hash-token
```

Запуск:

```powershell
python -m app.cli agent serve
```

## Smoke checklist

1. Скопировать `.env.example` в `.env`.
2. Сгенерировать hash через `python -m app.cli agent hash-token`.
3. Записать в `.env` только `LOCAL_AGENT_TOKEN_HASH`; raw token не сохранять.
4. Оставить `LOCAL_AGENT_HOST=127.0.0.1` и `LOCAL_AGENT_PORT=3031`.
5. Запустить `python -m app.cli agent serve`.
6. Проверить read-only routes с Bearer token:

```powershell
$token = "raw-token-used-for-hash"
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Headers $headers http://127.0.0.1:3031/agent/health
Invoke-RestMethod -Headers $headers http://127.0.0.1:3031/agent/runtime
Invoke-RestMethod -Headers $headers http://127.0.0.1:3031/agent/protocols
```

Ожидаемые статусы runtime: `running`, `stopped`, `degraded` или `unknown`.
Если Docker недоступен или `awg dump` не читается, agent должен вернуть `degraded`,
а не маскировать проблему под `stopped`.

Для первого production режима держать `LOCAL_AGENT_HOST=127.0.0.1` и открывать доступ только через SSH tunnel, reverse proxy с auth или будущий controller-side transport. Публично наружу agent не выставлять.
