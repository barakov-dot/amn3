# Web Admin Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI/Jinja2 web admin panel on port `3030` with login/password auth, users CRUD, servers CRUD, live server health, client config templates, `vpn://` delivery links, optional verified-email delivery/recovery, logs viewer, and `.env`-controlled logging.

**Architecture:** Add a separate `app.web` package that reuses existing `Settings`, SQLite `Repository`, redaction, and server check code. The web panel runs as a separate process through `python -m app.cli web serve`, uses signed cookie sessions, server-rendered templates, and records admin actions through the existing database. Live server state is stored in `server_health_checks` and refreshed by explicit UI/CLI actions.

**Tech Stack:** Python 3.12+, FastAPI, Starlette sessions, Jinja2, Uvicorn, SQLite, pytest, standard-library logging.

---

## File Structure

- Modify `pyproject.toml`: add `fastapi`, `uvicorn`, `jinja2`, `python-multipart`.
- Modify `.env.example`: add web admin and logging settings.
- Modify `app/config/settings.py`: add web/log fields and validators.
- Modify `app/db/schema.py`: add `server_health_checks`.
- Modify `app/db/repositories.py`: add web admin CRUD/query methods and health persistence.
- Modify `app/bot/delivery.py`: include `{vpn_link}` and delivery package import link.
- Modify `app/bot/delivery.py`: include email-safe delivery payload fields where needed.
- Modify `app/services/access.py`: render client configs through editable templates.
- Create `app/services/email_recovery.py`: verified-email recovery tokens and resend orchestration.
- Create `app/notifications/email.py`: SMTP email sender with redaction-safe logging.
- Modify `app/vpn/config_versions.py`: route config rendering through versioned templates.
- Create `app/vpn/config_templates.py`: load, validate, render, and preview client config templates.
- Create `app/vpn/templates/amneziawg_v1_5.conf.tpl`: default editable client config template.
- Create `app/vpn/templates/amneziawg_v2.conf.tpl`: default editable client config template.
- Create `app/logging_config.py`: configure console/file logging with redaction and log depth support.
- Create `app/web/__init__.py`: export app factory.
- Create `app/web/auth.py`: password hashing/checking, session auth, CSRF helpers.
- Create `app/web/server_health.py`: TCP reachability and read-only server check summary.
- Create `app/web/logs.py`: tail and redact log files.
- Create `app/web/forms.py`: small validation helpers for users and servers.
- Create `app/web/app.py`: FastAPI app factory and routes.
- Create `app/web/templates/*.html`: base, login, dashboard, users, user form/detail, servers, server form/detail/health, orders, config templates, email, logs, settings.
- Create `app/web/static/admin.css`: compact operational UI.
- Modify `app/cli.py`: add `web serve`.
- Create tests under `tests/web/`.
- Update `docs/PRODUCTION_VPS_CHECKLIST.ru.md` and `.en.md`: web panel launch and firewall note.

---

## Implementation Tasks

This English plan mirrors the Russian plan at `docs/superpowers/plans/2026-05-29-web-admin-panel.ru.md`. Execute the Russian plan task-by-task if the implementation discussion stays in Russian. The required task order is:

1. Dependencies, settings, and logging config.
2. Database and repository support.
3. Authentication, sessions, and CSRF.
4. FastAPI app skeleton, login, and dashboard.
5. Users CRUD.
6. Servers CRUD and live health.
7. Orders, logs, and settings pages.
8. Client config templates, `vpn://` links, and delivery display.
9. Verified email delivery and recovery.
10. CLI serve, docs, and full verification.

## Acceptance Requirements

- `python -m app.cli web serve --host 0.0.0.0 --port 3030` starts the panel.
- `/login` protects every admin page.
- Users can be created, edited, blocked, and marked as deleted.
- Existing users previously created through the Telegram bot are listed from the current `users` table without migration or import.
- Servers can be created, edited, disabled, and shown with live health state.
- Every server row includes online/degraded/offline/unknown, latency, last checked time, and latest error when available.
- `/config-templates` shows the delivery message template, versioned `.conf` templates, source, placeholders, safe preview, and a generated `vpn://` import link.
- User delivery options are explicit: Telegram text, `.conf` attachment, QR, user/admin resend, raw config fallback, `vpn://` link, and verified email.
- `CLIENT_CONFIG_TEMPLATE_DIR` controls local editable template overrides so VPS edits are not overwritten by package defaults.
- Email delivery is disabled by default, requires SMTP settings, uses verified addresses only, and recovery uses one-time TTL tokens.
- `/logs` shows redacted recent log lines with depth controlled by `APP_LOG_MAX_LINES`.
- All settings come from `.env` through `Settings`.
- Full test suite passes.

## Final Verification

```bash
python -m pytest tests -q
git diff --check
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Then open `http://127.0.0.1:3030/login` and verify Dashboard, Users, Servers, Config Templates, Email, Logs, and Settings pages.
