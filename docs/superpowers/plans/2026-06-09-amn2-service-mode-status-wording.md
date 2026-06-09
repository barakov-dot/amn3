# AMN2 Service-mode Status Wording Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the private web/admin integration status page clearly show the accepted Phase 3 service-mode baseline: loopback-only web/admin, SSH tunnel access, no public API/web exposure, no domain/HTTPS cutover, and `VPS_APPLY_ENABLED=false`.

**Architecture:** Keep this as a local/read-only status slice. Add a static safe `service_mode_boundary` section to the existing integration status report and render it on `/integration-status`; do not read live VPS state, mutate settings, add routes, or change POST behavior.

**Tech Stack:** AMN2 Python service dicts, FastAPI TestClient, Jinja2 templates, pytest.

---

### Task 1: Add Service-mode Boundary Contract

**Files:**

- Modify: `app/services/integration_status.py`
- Test: `tests/services/test_integration_status_service.py`

- [ ] **Step 1: Write the failing service test**

Add assertions to `test_build_integration_status_reports_controlled_prod_without_write_enablement`:

```python
    boundary = report["service_mode_boundary"]
    assert boundary["web_bot_services"] == "active"
    assert boundary["web_admin_listener"] == "127.0.0.1:3030_loopback_only"
    assert boundary["operator_access"] == "ssh_tunnel_only"
    assert boundary["public_web_admin"] == "closed"
    assert boundary["public_api_3040"] == "absent_closed"
    assert boundary["tcp_80_443"] == "absent"
    assert boundary["domain_https_cutover"] == "deferred_no_domain"
    assert boundary["vps_apply_enabled"] is False
    assert "direct public web/admin 3030" in report["blocked_lanes"]
    assert "Caddy/HTTPS/domain cutover" in report["blocked_lanes"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests\web\test_web_integration_status.py tests\services\test_integration_status_service.py -q --basetemp tmp\pytest-p4-i002-red
```

Expected: fail because `service_mode_boundary` is missing.

- [ ] **Step 3: Add minimal service data**

Add a `service_mode_boundary` dict to `build_integration_status()` and update blocked lanes with direct public web/admin and Caddy/HTTPS/domain cutover.

- [ ] **Step 4: Run service tests**

Run:

```powershell
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests\services\test_integration_status_service.py -q --basetemp tmp\pytest-p4-i002-service
```

Expected: pass.

### Task 2: Render Boundary On Integration Status Page

**Files:**

- Modify: `app/web/templates/integration_status.html`
- Test: `tests/web/test_web_integration_status.py`

- [ ] **Step 1: Write the failing web test**

Add assertions to `test_integration_status_page_renders_gate_without_secret_markers`:

```python
    assert "Service-mode boundary" in response.text
    assert "127.0.0.1:3030-loopback-only" in response.text
    assert "ssh-tunnel-only" in response.text
    assert "absent-closed" in response.text
    assert "deferred-no-domain" in response.text
    assert "direct public web/admin 3030" in response.text
    assert "Caddy/HTTPS/domain cutover" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests\web\test_web_integration_status.py::test_integration_status_page_renders_gate_without_secret_markers -q --basetemp tmp\pytest-p4-i002-web-red
```

Expected: fail because the page does not render the new boundary yet.

- [ ] **Step 3: Add minimal template panel**

Render `report.service_mode_boundary` as a `Service-mode boundary` panel near the current decision panel.

- [ ] **Step 4: Run focused verification**

Run:

```powershell
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-api-web-panel-finish\.venv\Scripts\python.exe -m pytest tests\web\test_web_integration_status.py tests\services\test_integration_status_service.py tests\web\test_api_readiness.py -q --basetemp tmp\pytest-p4-i002-focused
git diff --check
```

Expected: pytest passes; `git diff --check` returns exit code 0.

### Task 3: Record AMN3 Evidence

**Files:**

- Create: `research/amn2/phase-4-service-mode-status-wording-implementation-2026-06-09.md`
- Modify: `research/amn2/transfer-backlog.md`
- Modify: `research/amn2/phase-4-candidate-registry-2026-06-09.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/superpowers/plans/2026-06-09-amn2-phase-4-start.md`

- [ ] **Step 1: Record implementation evidence**

Capture AMN2 branch, commit, changed files, tests, and the explicit statement that no live VPS commands or write/config/token/sync/apply/revoke/backup/import/reboot actions were performed.

- [ ] **Step 2: Remove `P4-I002` from the active plan**

Update the active remaining plan so the next recommendation moves to `P4-I001` only if a second UX pass is needed, otherwise to route/secret gate planning.

- [ ] **Step 3: Commit AMN2 and AMN3**

Commit AMN2 implementation separately from AMN3 evidence.
