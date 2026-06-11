# Phase 5 P5-X001 Russian-first microtexts

Date: 2026-06-11.

Status: `completed-amn2-local-only`.

## Summary

`P5-X001` was completed as an AMN2 local-only Russian-first microcopy polish slice.

AMN2 branch and commit:

```text
branch: codex/bot-labels-russian-copy
commit: de25576 Polish Russian-first microcopy
source-of-truth branch: codex-vps-test-prep
push: 17454e9..de25576 codex-vps-test-prep -> codex-vps-test-prep
```

Changed AMN2 files:

- `app/bot/ux.py`
- `app/web/templates/integration_status.html`
- `app/web/templates/server_detail.html`
- `app/web/templates/user_detail.html`
- `tests/bot/test_bot_handlers.py`
- `tests/bot/test_telegram_ux.py`
- `tests/web/test_web_integration_status.py`
- `tests/web/test_servers.py`
- `tests/web/test_users.py`

## Behavior

The slice makes the most visible operator/user microtexts Russian-first while preserving stable technical identifiers and user-provided tariff names:

- bot admin template view now says `Шаблон сообщения с конфигом`, uses `Сбросить шаблон`, and explains the reset action in Russian;
- user-facing bot tariff/device summaries format duration as `день/дня/дней` instead of hardcoded English `days`;
- `/integration-status` operator-only boundary notes are Russian-first;
- `/servers/{id}` health and peer-sync action notes are Russian-first and keep the local-only/read-only boundary explicit;
- `/users/{id}` external-only device notes are Russian-first while preserving the technical `external-only` marker.

No route, form action, permission, database, config-generation, QR/import-link payload, Telegram transport, delivery behavior or VPS behavior changed.

## Safety Boundary

No live VPS command, SSH command, service restart, deploy, package apply/rebuild, public exposure, real config delivery, Telegram send, Telegram token use, production peer/user mutation, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot, destructive provider action or upstream/GPL code copy was performed.

The slice changed local AMN2 bot/web copy and tests only.

## Verification

RED before implementation:

```text
tests/bot/test_telegram_ux.py tests/bot/test_bot_handlers.py::test_handle_admin_template_shows_editable_template_and_reset_button tests/web/test_web_integration_status.py tests/web/test_servers.py::test_server_detail_shows_config_health_and_actions tests/web/test_users.py::test_user_detail_marks_external_only_device_without_config_actions -q
result: 7 failed, 23 passed, 1 warning
expected failures:
- old `Config ready template` / `Reset template` admin-template copy
- old `30 days` rendered tariff/device durations
- old English operator-only/web action notes
- old English external-only device notes
```

GREEN after implementation:

```text
same focused command
result: 30 passed, 1 warning

tests/bot tests/web/test_web_integration_status.py tests/web/test_servers.py tests/web/test_users.py -q
result: 152 passed, 1 warning

python -m pytest -q
result: 664 passed, 1 warning

git diff --check
result: passed
```

AMN2 final state:

```text
branch: codex-vps-test-prep
head: de25576 Polish Russian-first microcopy
working tree: clean
remote: amn2/codex-vps-test-prep at de25576
```

## Decision

`P5-X001` is closed as an AMN2 local-only Russian-first microcopy polish slice.

Next safe local-only recommendation: `P5-S002` Удалять устаревшие рекомендации после каждого закрытого slice.
