# Phase 5 P5-O002 web-admin gated-action and Russian-first UX cleanup

Date: 2026-06-12.

Scope: AMN2 local-only implementation/test slice.

AMN2 branch: `codex-vps-test-prep`.

AMN2 commit: `2215761 Polish operator web admin UX`.

Source finding: `P5-O001` operator-only UI smoke for AMN2 `9bff807` returned `needs-fix` because authenticated web/admin pages still exposed create/write/config/token controls during operator-only smoke, visible copy was mixed Russian/English, the header/resource name should be `AmneziyaDA`, and dashboard summary cards needed centered two-line counts.

## Changes

- Web/admin brand and title suffix now use `AmneziyaDA` instead of `Amneziya Admin`.
- Primary navigation and the sampled list/status pages are Russian-first while preserving stable technical route IDs and labels such as `API`, scopes and config version names.
- Dashboard summary cards render the numeric value on the first line and the Russian entity label on the second line, centered horizontally and vertically.
- Users and servers index pages no longer expose active `New user` / `New server` links in operator-only mode; they show disabled named-gate affordances instead.
- API token issue/revoke and config-template save/reset controls are visibly disabled and explain that a named gate is required.
- The About/build-status, disabled-devices, logs, settings, orders, API-readiness and integration-status surfaces were aligned toward Russian-first operator copy where they are part of the current smoke surface.

## Verification

Focused P5-O002:

```text
PYTHONPATH=.codex_deps;.
C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/web/test_operator_ui_p5_o002.py -q
4 passed, 1 warning
```

Expanded web regression:

```text
PYTHONPATH=.codex_deps;.
C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_api_tokens.py tests/web/test_config_templates.py tests/web/test_api_readiness.py tests/web/test_about.py tests/web/test_logs_settings_orders.py tests/web/test_web_integration_status.py tests/web/test_operator_ui_p5_o002.py -q
90 passed, 1 warning
```

Git hygiene:

```text
AMN2 git diff --check: passed
AMN2 staged git diff --cached --check: passed
```

Local browser smoke:

```text
target: http://127.0.0.1:13031/
mode: temporary local AMN2 web admin with test SQLite DB and test credentials only
result: login succeeded; title `Панель управления | AmneziyaDA`; dashboard metrics were `1|пользователь`, `1|сервер`, `1|заявка`, `1|устройство`; sampled pages `/users`, `/servers`, `/api-tokens`, `/config-templates`, `/about` showed Russian-first headings and no active `/users/new` or `/servers/new` links; token/template submit buttons were disabled.
cleanup: temporary local server stopped.
```

## Negative controls

No live VPS command, SSH command, package apply/rebuild on VPS, source-overlay update, service restart/deploy, public exposure change, config delivery, write API, Local Agent mutation, backup/import/reboot, production peer/user mutation, destructive VPS action, Telegram token use, live bot send, Telegram profile mutation, secret-bearing evidence publication or upstream/GPL code copy was performed.

## Status

`P5-O002` is closed as local-only AMN2 UX/test work.

Because AMN2 advanced from the latest VPS-smoked/package head `9bff807` to `2215761`, the next recommended step is a new current-head package rebuild:

```text
P5-C009 Current-head package rebuild for AMN2 2215761
```

This is an AMN3 local package/test gate only. It does not authorize live VPS apply, SSH, service restart/deploy or public exposure by itself.
