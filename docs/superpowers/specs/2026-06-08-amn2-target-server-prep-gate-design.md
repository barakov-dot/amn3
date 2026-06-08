# AMN2 Target Server Prep Gate Design

Дата: 2026-06-08.

## Контекст

Текущий VPS-smoked source overlay AMN2: `f7f6131 Update integration status for c92 manual prelaunch`. Validation VPS уже прошел read-only loopback API smoke и manual runtime checks при `VPS_APPLY_ENABLED=false`, ручном запуске web/bot, без direct public `3030` и без public API `3040`.

Следующий физический VPS рассматриваем как отдельный target-server gate, а не как продолжение source-overlay работ на validation VPS.

## Решение

Создать docs-only/read-only target-server prep slice в AMN3. Slice готовит оператора к аренде и первичной safe-проверке нового VPS, сбору безопасной evidence и отдельному выбору следующего gate.

Этот design не меняет production-код AMN2, contents AMN3 package, live VPS state, service mode, reverse proxy, API surfaces или peer write behavior.

## Компоненты

- `docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md`: high-level gate, требования, download/checksum entry point и safe summary.
- `docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md`: phased manual bootstrap/read-only runbook для нового target VPS.
- `research/amn2/target-server-prep-gate-2026-06-08.md`: evidence note, зачем существует этот slice и что остается закрытым.
- `research/amn2/target-server-prep-evidence-template-2026-06-08.md`: safe evidence template для operator-returned summaries.
- Existing status/backlog docs: ссылки, чтобы новый gate был виден из project handoff документов.

## Safety Boundary

Target-server prep slice оставляет закрытыми:

- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040`;
- direct public web/admin `3030`;
- service-mode `systemd` or HTTPS reverse proxy deployment without a separate gate;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent write/config mutations;
- backup/import/reboot routes;
- secret-bearing evidence in chat or GitHub.

## Success Criteria

- New target-server prep docs committed in AMN3.
- Текущий `f7f6131` package и smoke evidence остаются source of truth.
- Download instructions используют raw URLs без Authorization headers.
- Safe evidence templates запрашивают только non-secret summaries.
- Future service-mode и live-write actions остаются отдельными explicit decisions.
