# API/Web Panel Finish Implementation

Дата: 2026-06-04.

Production repo: `C:\Users\SooL\Documents\Amneziya`.

Branch:

```text
codex/api-web-panel-finish
```

Commit:

```text
294803e Add API readiness and token web pages
```

## Реализовано

- web-admin route `GET /api-readiness`;
- web-admin route `GET /api-tokens`;
- web-admin route `POST /api-tokens/issue`;
- web-admin route `POST /api-tokens/{token_id}/revoke`;
- safe Repository list для API token metadata без `token_hash`;
- route-policy bindings для новых web routes;
- tests for login requirement, aggregate-only readiness, one-time raw API token display, refresh without raw/hash leak, revoke and unsupported scope rejection.

## Границы

Не добавлялось:

- `/api/clients` write CRUD;
- API `config:read`;
- public/self-service config delivery;
- backup/import/reboot;
- Local Agent `/configs`;
- live peer apply/revoke;
- web actions that trigger live Docker writes.

Raw API token показывается только в immediate issue response. Token hash не выбирается для web list view и не выводится в template.

## Verification

Focused:

```text
python -m pytest tests/api tests/services/test_api_tokens.py tests/web/test_api_readiness.py tests/web/test_api_tokens.py tests/security/test_surface_policy_bindings.py -q --basetemp tmp/pytest-focused-api-web
39 passed, 1 StarletteDeprecationWarning
```

Full:

```text
python -m pytest -q --basetemp tmp/pytest-full-api-web-panel
594 passed, 1 StarletteDeprecationWarning
```

## VPS Test Recommendation

После merge/rebase этого branch в целевой production head пересобрать AMN3 install/update package от нового commit и выполнять только `docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md`:

- API loopback smoke;
- DB-only server config sync;
- web panel через SSH tunnel;
- `VPS_APPLY_ENABLED=false`;
- без live apply/revoke/config delivery.
