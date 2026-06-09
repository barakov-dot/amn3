# Service-mode web panel read-only UX review evidence template 2026-06-09

Дата: 2026-06-09.

Назначение: зафиксировать, что для следующего operator UX/product review есть отдельный safe evidence template, совместимый с текущей Phase 3 service-mode границей.

## Artifacts

```text
checklist: docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md
evidence_template: docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md
planning_note: research/amn2/service-mode-web-panel-read-only-ux-review-2026-06-09.md
```

## Scope

Только приватная web/admin панель через SSH tunnel:

```text
access_path: external browser over SSH local port forward
remote_web_bind: 127.0.0.1:3030
public API 3040: absent/closed
public web/admin 3030: closed
VPS_APPLY_ENABLED: false
allowed: GET navigation, visual UX/product observations, labels/copy/status/empty states
blocked: POST/write/config/token/sync/backup/reboot/public exposure
```

## Expected Operator Return

Оператор возвращает только заполненную текстовую сводку из `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_EVIDENCE_TEMPLATE.ru.md`.

Скриншоты не нужны. Если screenshot понадобится позже, сначала нужен отдельный redaction decision.

## Decision Boundary

Этот template не является разрешением на:

- destructive/admin write actions;
- config delivery;
- API token issue/revoke;
- sync/health operation buttons;
- backup/import/reboot;
- Local Agent mutations;
- public API `3040`;
- direct public web/admin `3030`;
- HTTPS reverse proxy/public cutover;
- production peer/user mutation.
