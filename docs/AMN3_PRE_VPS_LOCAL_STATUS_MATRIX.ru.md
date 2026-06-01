# AMN3 Pre-VPS Local Status Matrix

Дата сверки: 2026-06-01. Ветка: `codex/local-agent-production-wiring`. Последний
проверенный commit: `137b1f1 Add first VPS mutation test packet`.

Цель документа - убрать повторные рекомендации перед реальным VPS и ясно
разделить три состояния: что уже реализовано локально, что только
задокументировано как post-VPS план, и что нельзя включать до результата
реального smoke.

Главное правило: Не дублировать соседний VPS smoke. Если соседний чат уже
готовит или выполняет проверку на живом VPS, текущий локальный чат должен
только синхронизировать документы, тесты и gate-условия.

## 1. Реализовано локально

Эти части уже есть в коде или локальных проверках и не требуют живого VPS для
поддержания:

- read-only Local Agent endpoints: `/agent/health`, `/agent/version`,
  `/agent/runtime`, `/agent/protocols`;
- read-only `LocalAgentClient` для health/runtime/protocols;
- CLI probe для проверки Local Agent без write operations;
- runtime registry, VPS checker, debug snapshot и redaction;
- systemd template для `amneziya-agent`;
- safe env defaults: `LOCAL_AGENT_WRITE_ENABLED=false`;
- future write contracts без активных mutation routes;
- policy matrix docs/tests для будущего `agent:clients:write`;
- checks, которые подтверждают отсутствие `/agent/clients*` до VPS gate;
- handoff, release gate, VPS smoke packet и post-VPS implementation map.

## 2. Только задокументировано

Эти документы готовы как code-ready планы, но не означают, что write API уже
включен:

- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`;
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`;
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`;
- `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`;
- `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md`;
- `docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md`;
- `docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md`.

Связанные gate-документы:

- `docs/AMN3_VPS_TEST_PACKET.ru.md`;
- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`;
- `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`;
- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`.

## 3. Не реализовано в коде до VPS

Текущий локальный статус по write surface:

- `app/web/local_agent_actions.py: absent until GO-1`;
- `app/agent/peer_commands.py: absent until GO-1`;
- `write_slice_policies(): absent until GO-1`;
- `LocalAgentClient write methods: absent until GO-1`;
- `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`: absent until GO-1;
- `LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write`: absent until GO-1;
- `/agent/clients/dry-run`, `/agent/clients`, `/agent/clients/{id}`: absent
  from active routes until GO-1.

Это намеренно. До реального VPS smoke read-only token remains read-only, а
`agent:clients:write` должен использовать отдельный token/scope set только
после принятого `go`.

## 4. Можно делать локально без VPS

Актуальная локальная работа до живого сервера:

- держать эту матрицу, `docs/AMN3_NEXT_CHAT_HANDOFF.ru.md` и
  `docs/AMN3_LOCAL_RELEASE_GATE.ru.md` синхронизированными;
- запускать локальные tests, которые доказывают, что write routes закрыты;
- уточнять UX/API тексты без открытия mutation surface;
- проверять, что `.env.example` и `deploy/examples/.env.production.example`
  содержат `LOCAL_AGENT_WRITE_ENABLED=false`;
- проверять, что `LOCAL_AGENT_WRITE_ENABLED=true` не стал default;
- проверять redaction: no raw token, private key, PSK, QR, `vpn://` или
  full client config в UI, docs, logs и responses;
- переносить выводы соседнего VPS smoke в
  `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`, когда они появятся.

## 5. Нельзя делать без VPS

До заполненного smoke result и явного `Decision: go` нельзя:

- включать `LOCAL_AGENT_WRITE_ENABLED=true`;
- добавлять `agent:clients:write` в read-only token;
- регистрировать `/agent/clients*` routes;
- создавать active write endpoints;
- создавать web admin mutation actions;
- создавать controller write client methods;
- выполнять first VPS mutation test;
- менять runtime state через Local Agent.

## 6. Если соседний чат уже сделал VPS smoke

Если рядом уже есть реальный результат:

1. Не повторять smoke в этом чате.
2. Перенести только проверяемое резюме в
   `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`.
3. Если `Decision: no-go`, вернуться к smoke/runbook fixes без write code.
4. Если `Decision: go`, идти по
   `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`, начиная с Phase 0 evidence
   intake.
5. Первый write slice выполнять только через планы из раздела 2 и только с
   отдельным `agent:clients:write` token/scope set.
