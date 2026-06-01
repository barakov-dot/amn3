# AMN3 Local Release Gate

Этот gate нужен для локальной сборки до реального VPS smoke. Он фиксирует, что AMN3 можно пушить и передавать в
соседний чат только если write API остается закрытым, read-only token не получил write scope, а все future write
контракты по-прежнему завязаны на VPS gate.

## 1. Обязательные условия

Локальный release считается допустимым только если:

- `LOCAL_AGENT_WRITE_ENABLED=false` в `.env.example` и `deploy/examples/.env.production.example`;
- `LOCAL_AGENT_WRITE_ENABLED=true` нигде не используется как default;
- read-only token содержит только `agent:health,agent:read,agent:protocols:read`;
- `agent:clients:write` не добавлен в read-only token;
- `/agent/clients*` routes не зарегистрированы в active policy;
- `get_policy()` продолжает отклонять `/agent/clients/dry-run`, `/agent/clients` и `/agent/clients/{id}`;
- write API docs продолжают говорить `VPS smoke required`;
- результат реального smoke должен идти через `docs/AMN3_VPS_TEST_PACKET.ru.md`;
- финальный `Go / no-go` фиксируется в `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.

## 2. Локальные команды проверки

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py tests/agent/test_write_policy_matrix.py tests/test_file_hygiene.py -v
```

Документальные проверки:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py -v
```

Перед коммитом:

```powershell
git diff --check
git status --short --branch
```

## 3. Что запрещено до VPS smoke

До реального VPS smoke нельзя:

- включать `LOCAL_AGENT_WRITE_ENABLED=true` как default;
- добавлять `agent:clients:write` в read-only token;
- регистрировать `/agent/clients*` write routes;
- добавлять mutation endpoints;
- делать Local Agent публичным;
- возвращать private key, PSK, QR, `vpn://`, raw token или full client config из write responses;
- начинать implementation slice без заполненного `Go / no-go`.

## 4. Что разрешено локально

Можно делать до VPS:

- contract types для будущего write API;
- tests, которые доказывают, что write routes закрыты;
- UX/API docs;
- audit/preflight/confirmation docs;
- release checklist;
- handoff для соседнего чата.

## 5. Gate result

Если все локальные проверки зеленые, можно передавать сборку в VPS smoke через
`docs/AMN3_VPS_TEST_PACKET.ru.md`.

Если любая проверка показывает active write surface до VPS smoke, результат gate - `no-go`, и такую сборку нельзя
использовать для перехода к `agent:clients:write`.
