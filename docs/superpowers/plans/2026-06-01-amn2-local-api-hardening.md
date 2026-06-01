# AMN2 Local API Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the local-only hardening tasks for the read-only API shell before live VPS smoke.

**Architecture:** Keep the API as a scoped FastAPI app backed by SQLite `Repository` methods. Add a local smoke validator, safe read audit events, and one more aggregate-only users summary route without exposing personal identifiers or config-bearing data.

**Tech Stack:** Python 3.12, FastAPI, SQLite repository, pytest, standard-library `urllib`.

---

### Task 1: API Smoke Guard

**Files:**
- Create: `app/services/api_smoke.py`
- Modify: `app/cli.py`
- Test: `tests/api/test_smoke.py`, `tests/api/test_cli_tokens.py`

- [x] Write failing tests for forbidden response markers and live smoke CLI output.
- [x] Implement marker detection and route status aggregation.
- [x] Add `python -m app.cli api smoke-check --base-url ... --token ... --server-name ...`.
- [x] Ensure output never includes raw token, Authorization header, or response bodies.

### Task 2: API Read Audit

**Files:**
- Modify: `app/api/app.py`
- Test: `tests/api/test_app.py`

- [x] Write failing tests proving successful API reads record `api_read`.
- [x] Include only safe metadata: method, route template, required scope, token id/name/owner label.
- [x] Do not record Authorization header, raw token, token hash, response body, `.conf`, QR, or `vpn://`.

### Task 3: Users Summary Route

**Files:**
- Modify: `app/db/repositories.py`, `app/api/app.py`, `app/security/surface_policy.py`
- Test: `tests/db/test_repositories.py`, `tests/api/test_app.py`, `tests/security/test_surface_policy.py`

- [x] Add aggregate repository query for users, devices per user, and orders by status.
- [x] Expose `GET /api/users/summary` under `metrics:read`.
- [x] Add policy `api.users.summary` with read-only, aggregate-only, no-secret gates.
- [x] Keep `server:read` unable to access this route.

### Task 4: Operator Docs And Output Polish

**Files:**
- Modify: `docs/NEXT_CHAT_HANDOFF.ru.md`, `docs/NEXT_STAGE_BEGINNER_GUIDE.ru.md`, `docs/VPS_RETEST_PROTOCOL.ru.md`, `docs/PRODUCTION_VPS_CHECKLIST.ru.md`, `docs/API_TOKEN_POLICY.ru.md`
- Test: focused docs/files checks and full pytest.

- [x] Update handoff branch/commit language for `codex/read-only-api-route-shell`.
- [x] Add `jq` helpers as optional convenience commands.
- [x] Add `--pretty` JSON output to API token/smoke CLI commands.
- [x] Keep all docs in Russian where user-facing.
