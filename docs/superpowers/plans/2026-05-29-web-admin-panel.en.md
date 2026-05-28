# Web Admin Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI/Jinja2 web admin panel on port `3030` with login/password auth, users CRUD, servers CRUD, live server health, logs viewer, and `.env`-controlled logging.

**Architecture:** Add a separate `app.web` package that reuses existing `Settings`, SQLite `Repository`, redaction, and server check code. The web panel runs as a separate process through `python -m app.cli web serve`, uses signed cookie sessions, server-rendered templates, and records admin actions through the existing database. Live server state is stored in `server_health_checks` and refreshed by explicit UI/CLI actions.

**Tech Stack:** Python 3.12+, FastAPI, Starlette sessions, Jinja2, Uvicorn, SQLite, pytest, standard-library logging.

---

## File Structure

- Modify `pyproject.toml`: add `fastapi`, `uvicorn`, `jinja2`, `python-multipart`.
- Modify `.env.example`: add web admin and logging settings.
- Modify `app/config/settings.py`: add web/log fields and validators.
- Modify `app/db/schema.py`: add `server_health_checks`.
- Modify `app/db/repositories.py`: add web admin CRUD/query methods and health persistence.
- Create `app/logging_config.py`: configure console/file logging with redaction and log depth support.
- Create `app/web/__init__.py`: export app factory.
- Create `app/web/auth.py`: password hashing/checking, session auth, CSRF helpers.
- Create `app/web/server_health.py`: TCP reachability and read-only server check summary.
- Create `app/web/logs.py`: tail and redact log files.
- Create `app/web/forms.py`: small validation helpers for users and servers.
- Create `app/web/app.py`: FastAPI app factory and routes.
- Create `app/web/templates/*.html`: base, login, dashboard, users, user form/detail, servers, server form/detail/health, orders, logs, settings.
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
8. CLI serve, docs, and full verification.

## Acceptance Requirements

- `python -m app.cli web serve --host 0.0.0.0 --port 3030` starts the panel.
- `/login` protects every admin page.
- Users can be created, edited, blocked, and marked as deleted.
- Servers can be created, edited, disabled, and shown with live health state.
- Every server row includes online/degraded/offline/unknown, latency, last checked time, and latest error when available.
- `/logs` shows redacted recent log lines with depth controlled by `APP_LOG_MAX_LINES`.
- All settings come from `.env` through `Settings`.
- Full test suite passes.

## Final Verification

```bash
python -m pytest tests -q
git diff --check
python -m app.cli web serve --host 127.0.0.1 --port 3030
```

Then open `http://127.0.0.1:3030/login` and verify Dashboard, Users, Servers, Logs, and Settings pages.
