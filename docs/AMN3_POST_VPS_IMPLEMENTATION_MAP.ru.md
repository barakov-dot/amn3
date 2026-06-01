# AMN3 Post-VPS Implementation Map

Этот документ - короткая карта перехода от read-only VPS smoke к первому реальному `agent:clients:write` slice.
Он не заменяет детальный план `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`, а фиксирует
порядок входа в него после фактического результата из `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.

Связанные документы:

- `docs/AMN3_VPS_TEST_PACKET.ru.md`
- `docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md`
- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`
- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`
- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`
- `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md`
- `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`
- `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`
- `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`

## 1. Entry rule

До реального VPS smoke этот документ не разрешает write routes. Он начинает применяться только после заполненного
`Go / no-go for agent:clients:write design` в `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.

```text
Before VPS smoke: LOCAL_AGENT_WRITE_ENABLED=false
After accepted go: LOCAL_AGENT_WRITE_ENABLED=false -> true only for controlled VPS mutation test
Read-only token remains read-only
agent:clients:write uses a dedicated token/scope set
```

## 2. GO / NO-GO rules

`GO-1` - можно начинать реализацию первого write slice, если все пункты подтверждены:

- commit на VPS совпадает с веткой `codex/local-agent-production-wiring`;
- Local Agent слушает только `127.0.0.1:3031`;
- `/agent/health`, `/agent/runtime` и `/agent/protocols` отвечают без secret leakage;
- web admin видит Local Agent без raw token;
- rollback `sudo systemctl disable --now amneziya-agent` проверен;
- `LOCAL_AGENT_WRITE_ENABLED=false` до начала write test;
- write routes все еще выключены до явной активации;
- причина `degraded`, если она есть, понятна и не затрагивает peer mutation safety;
- в logs/UI/docs нет raw token, private key, PSK, QR, `vpn://` или полного client config.

`NO-GO` обязателен, если есть хотя бы одно условие:

- Local Agent недоступен или работает только частично без понятной причины;
- порт `3031` доступен публично;
- raw token появился в UI, docs, issue, `.env` dump или logs;
- `/agent/protocols` раскрывает private key, PSK, QR, `vpn://` или full client config;
- rollback не проверен;
- write routes были включены до решения `go`;
- Docker/host runtime неясен настолько, что peer apply/revoke нельзя безопасно откатить.

## 3. Implementation phases

### Phase 0 - VPS evidence intake

Цель: превратить smoke result в управляемое решение.

Действия:

- проверить `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`;
- убедиться, что `Decision: go`;
- зафиксировать commit, runtime, bind, rollback, secret-leak check и web admin status;
- если решение `no-go`, не начинать code slice и вернуться к smoke/runbook фиксам;
- если решение `go`, открыть детальный план `docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md`.

Файлы/тесты:

- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`
- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`
- `tests/deploy/test_runtime_registry.py`

### Phase 1 - write policy activation

Цель: явно выбрать только peer/device mutation policies и не открывать весь future API.

Действия:

- добавить helper для selected write slice в `app/agent/policy.py`;
- не менять read-only behavior `get_policy()` без явного write mode;
- связать active write policy с `LOCAL_AGENT_WRITE_ENABLED`;
- реализовать settings/token boundary по `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md`;
- для settings/token boundary использовать TDD-план `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`;
- использовать `app/agent/write_policy_matrix.py` как источник planned operations;
- scope `agent:clients:write` держать отдельным от read-only token.

Файлы/тесты:

- `app/agent/policy.py`
- `app/agent/write_policy_matrix.py`
- `tests/agent/test_policy.py`
- `tests/agent/test_write_policy_matrix.py`

### Phase 2 - Local Agent endpoints

Цель: добавить guarded endpoints без delivery secrets.

Действия:

- создать runtime adapter `app/agent/peer_commands.py` для local peer apply/revoke;
- для runtime adapter использовать TDD-план `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`;
- реализовать authoritative audit storage из `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md`;
- для audit storage использовать TDD-план `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`;
- добавить dry-run endpoint в `app/agent/api.py`;
- добавить apply/revoke endpoints только за `LOCAL_AGENT_WRITE_ENABLED=true`;
- для guarded endpoints использовать TDD-план `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`;
- принимать request/response contracts из `app/agent/write_contracts.py`;
- использовать `app/agent/write_confirmation.py` для fresh dry-run reference и confirmation nonce;
- писать audit через `app/agent/write_audit.py`;
- response не должен возвращать raw token, private key, PSK, QR, `vpn://` или full client config.

Файлы/тесты:

- `app/agent/api.py`
- `app/agent/peer_commands.py`
- `app/agent/write_contracts.py`
- `app/agent/write_confirmation.py`
- `app/agent/write_audit.py`
- `tests/agent/test_api.py`
- `tests/agent/test_peer_commands.py`
- `tests/agent/test_write_contracts.py`
- `tests/agent/test_write_confirmation.py`
- `tests/agent/test_write_audit.py`

### Phase 3 - controller client

Цель: дать web admin/CLI безопасный клиент к Local Agent write flow.

Действия:

- создать или расширить `app/agent/client.py`;
- добавить методы для `POST /agent/clients/dry-run`, `POST /agent/clients`, `DELETE /agent/clients/{id}`;
- хранить raw agent token только в controller settings/runtime secret path;
- передавать `user_id`, `device_id`, `device_label`, `client_id`, `server_alias`, `protocol=amneziawg` и
  `peer_public_key_fingerprint` по модели `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`;
- ошибки `preflight_required`, `runtime_degraded` и `mutation_failed` показывать без секретов.

Файлы/тесты:

- `app/agent/client.py`
- `app/web/server_health.py`
- `app/web/local_agent_actions.py`
- `tests/agent/test_client.py`
- `tests/web/test_server_health.py`

### Phase 4 - web admin preflight

Цель: включить операторский UX без прямого "one click mutation".

Действия:

- добавить web admin preview для dry-run;
- показывать user/device/server identity, risk class, planned commands и rollback hint;
- требовать confirmation nonce перед apply/revoke;
- блокировать повторное подтверждение после expiry;
- не показывать raw token, private key, PSK, QR, `vpn://` или полный config.

Файлы/тесты:

- `app/web/templates/server_detail.html`
- `app/web/templates/server_health.html`
- `app/web/server_health.py`
- `app/web/local_agent_actions.py`
- `tests/web/test_server_health.py`

### Phase 5 - first VPS mutation test

Цель: проверить минимальный apply/revoke на реальном VPS и сразу подтвердить rollback/secret boundaries.

Порядок:

1. Создать test-only user/device/peer binding.
2. Выполнить dry-run.
3. Подтвердить mutation.
4. Выполнить apply.
5. Проверить runtime state.
6. Выполнить revoke или rollback.
7. Проверить logs на raw token, private key, PSK, QR, `vpn://` и full client config.
8. Зафиксировать result summary без секретов.

Файлы/тесты:

- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`
- `deploy/runtime/collect_debug_snapshot.sh`
- `tests/security/test_redaction.py`

## 4. Required local verification before push

Перед пушем каждого post-VPS slice:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py tests/agent/test_api.py tests/agent/test_client.py tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py tests/security/test_redaction.py -v
```

Документальный gate:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py -v
git diff --check
git status --short --branch
```

## 5. Product line

В продукте сохраняем один понятный flow:

```text
dry-run -> confirmation -> apply/revoke -> audit -> rollback
```

Первый slice управляет только пользователями/устройствами/peer bindings. Backup/import/reboot, массовые операции,
delivery QR/config и публичный root API остаются вне этого этапа.
