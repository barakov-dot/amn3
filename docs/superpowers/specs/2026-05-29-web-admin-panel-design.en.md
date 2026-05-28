# Web Admin Panel Design

## Goal

Add a local Amneziya web admin panel on port `3030` so an administrator can visually manage users, servers, and diagnostics without relying on the Telegram interface. The panel should fit the first live VPS rollout: simple operations, minimal frontend deployment complexity, safe authentication, and useful logging.

## Context

Administration currently happens through the Telegram bot and CLI. The database already contains the main entities: `users`, `servers`, `devices`, `orders`, `admin_actions`, `device_traffic_snapshots`, and `message_templates`. Settings are loaded from `.env` through `app.config.Settings`. The VPS flow already has `server check`, `apply-peer`, `revoke-peer`, `collect-traffic`, and `bot check-network`.

## Recommended Approach

Use `FastAPI + Jinja2 + Uvicorn` inside the existing Python project.

Reasons:

- one runtime and one dependency stack with the current application;
- no Node.js build step on the VPS;
- server-rendered UI is enough for CRUD, logs, and diagnostic screens;
- easy reuse of the existing `Repository`, `Settings`, redaction, and services.

A React/Vue SPA is not needed yet: it would complicate deployment and authentication, while the first stage needs a reliable admin surface.

## New `.env` Settings

```env
WEB_ADMIN_ENABLED=true
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PORT=3030
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=replace-with-password-hash
WEB_ADMIN_SESSION_SECRET=replace-with-generated-random-secret-32-plus-chars
APP_LOG_ENABLED=true
APP_LOG_LEVEL=INFO
APP_LOG_MAX_LINES=500
APP_LOG_PATH=logs/app.log
```

`WEB_ADMIN_PASSWORD_HASH` stores a password hash, not the raw password. If the hash is empty or a placeholder, the web panel must refuse to start with an actionable error. `WEB_ADMIN_SESSION_SECRET` is used for signed session cookies and must be stored separately with `.env`.

`APP_LOG_ENABLED=false` disables application log file writing. `APP_LOG_LEVEL` supports `DEBUG`, `INFO`, `WARNING`, and `ERROR`. `APP_LOG_MAX_LINES` controls UI viewing depth, not infinite retention. File rotation can be simple: a Python logging rotating handler with a size limit.

## Architecture

```mermaid
flowchart TD
    CLI["python -m app.cli web serve"] --> WebApp["FastAPI app"]
    WebApp --> Auth["Session auth middleware"]
    WebApp --> Templates["Jinja2 templates"]
    WebApp --> Repo["Repository"]
    Repo --> DB["SQLite database"]
    WebApp --> Logs["Log reader / redaction"]
    WebApp --> ServerConfig["servers.yml loader"]
```

The panel runs as a separate process from the Telegram bot:

```bash
python -m app.cli web serve --host 0.0.0.0 --port 3030
```

CLI flags may override `.env`, but defaults come from `Settings`.

## Authentication

The panel uses a `/login` form:

- username is compared with `WEB_ADMIN_USERNAME`;
- password is checked against `WEB_ADMIN_PASSWORD_HASH`;
- on success, a signed session cookie is set;
- `/logout` clears the session;
- every page except `/login` and the health endpoint requires authentication.

For the first stage, one web-admin account from `.env` is enough. Telegram-admin roles do not grant automatic web access.

## UI and Pages

The panel should be an operational workspace, not a landing page:

- `/` Dashboard: database status, user count, active devices, pending orders, servers, recent errors.
- `/users`: user table with search by Telegram ID, username, and name; create, edit, block, soft-delete actions.
- `/users/new`: create user by Telegram ID, username, first/last name, admin flag.
- `/users/{id}`: user profile, status, admin flag, devices, orders, recent admin actions.
- `/servers`: all-server table from DB and related config; manual status, live state, ping/latency, SSH reachability, endpoint, VPN port, device count, last check time.
- `/servers/new`: create server DB record; secrets are not entered or shown.
- `/servers/{id}`: edit host, SSH port, endpoint host, VPN port, network CIDR, server address, server public key, runtime, firewall, status, max devices.
- `/servers/{id}/health`: live diagnostics page for one server: ping/latency, TCP/SSH reachability, read-only `server check`, `awg-quick` state, UDP port visibility, latest error.
- `/orders`: pending/fulfilled/rejected orders for Telegram flow debugging.
- `/logs`: show last `APP_LOG_MAX_LINES`, filter by level, and plain-text search.
- `/settings`: read-only runtime settings with secret redaction.

Deletion must be safe in the first stage:

- user: `status='deleted'` or `status='blocked'`, without physically deleting rows;
- server: `status='disabled'`, without physical deletion if linked devices exist;
- physical deletion can be added later after a separate backup/restore scenario.

## User Management

Minimum actions:

- show all existing users from the current `users` table, including users previously created through the Telegram bot;
- create user;
- edit `telegram_id`, `username`, `first_name`, `last_name`, `status`, `is_admin`;
- block user;
- mark user as deleted;
- view active/total devices;
- view recent admin actions.

Changes should be recorded in `admin_actions` with actions such as `web_user_create`, `web_user_update`, `web_user_block`, and `web_user_delete`.

The web panel does not create a separate users table. The source of truth is the existing `users` table; linked `devices`, `orders`, and `admin_actions` must appear for already-created users without migration or manual import.

## Server Management

Minimum actions:

- create server DB record;
- edit main server fields;
- disable server;
- view device count and basic configuration;
- see live state for every server;
- manually run a health check for one server;
- refresh health checks for all servers.

The panel must not store SSH private keys, passwords, or PSKs. In the first stage it manages the server DB record; `servers.yml` remains the runtime config for SSH/VPS operations. If DB fields and `servers.yml` disagree, the UI should show a warning on the server page.

Live server state must be stored separately from the manual `servers.status`. Add a `server_health_checks` table or equivalent repository layer with:

- `server_id`;
- `status`: `online`, `degraded`, `offline`, `unknown`;
- `latency_ms`;
- `ssh_ok`;
- `awg_ok`;
- `udp_port_ok`;
- `checked_at`;
- `error`.

In the UI, `ping` means a fast reachability check. For the MVP, TCP connect to the SSH port with a timeout is acceptable, and the full read-only `server check` can run from a button/refresh action. ICMP ping is not required because it is often disabled by VPS/firewall policy.

## Logging

Add centralized logging configuration:

- console logs remain available for systemd;
- when `APP_LOG_ENABLED=true`, write to `APP_LOG_PATH`;
- level comes from `APP_LOG_LEVEL`;
- secrets pass through `redact()` before file logging;
- web `/logs` shows only the last `APP_LOG_MAX_LINES`.

Useful debug events for Telegram/admin operations:

- application startup;
- successful and failed web login without logging the password;
- user create/update;
- server create/update;
- server health check success/failure;
- handler errors;
- Telegram network check;
- VPS apply/revoke/traffic commands and their result without secrets.

## Errors and Security

- All forms use POST with a CSRF token or a session-bound nonce.
- UI errors show a short message; details go to logs.
- Secrets are not shown in UI and are not written to logs.
- Password hash and session secret are validated at startup.
- The web panel is intended to run behind a firewall/VPN/reverse proxy. Publicly exposing port `3030` without network restrictions is not recommended.

## Testing

Cover with tests:

- Settings reads web/logging parameters;
- login success/failure;
- protected route redirects without session;
- users list/create/update/block/delete;
- servers list/create/update/disable;
- server health check stores online/degraded/offline state and exposes it in UI;
- logs viewer applies `APP_LOG_MAX_LINES` and redaction;
- CLI accepts `web serve`;
- startup refuses empty password hash.

## MVP Acceptance Criteria

- `python -m app.cli web serve --host 0.0.0.0 --port 3030` starts the web panel.
- `/login` accepts a valid username/password and protects the remaining pages.
- Users previously created through the Telegram bot appear in `/users` and detail pages with their devices and orders.
- Users can be added, edited, blocked, and marked as deleted.
- Servers can be added, edited, and disabled.
- Every server is shown with live state: online/degraded/offline/unknown, latency, last check time, and latest error.
- `/logs` shows recent log lines with redaction.
- `APP_LOG_ENABLED`, `APP_LOG_LEVEL`, `APP_LOG_MAX_LINES`, and `APP_LOG_PATH` control logging.
- All new behavior tests pass with the existing test suite.

## Out of Scope for MVP

- separate roles and multiple web-admin accounts;
- React/Vue SPA;
- public user registration;
- physical deletion of linked production records;
- editing SSH private keys and secrets through UI;
- automatic VPS provisioning from the web panel.
