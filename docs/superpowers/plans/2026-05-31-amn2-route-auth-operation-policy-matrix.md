# AMN2 Route/Auth/Operation Policy Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ввести первый безопасный production slice после verified live VPS baseline: machine-checkable `Route/Auth/Operation Policy Matrix` для текущих `amn2` web, bot, Local Agent, CLI и remote-operation surfaces без новых API endpoints, без новых write flows и без live VPS calls.

**Architecture:** Добавляем отдельный inventory-only policy module в `app/security/surface_policy.py`. Он не подключается к runtime route guards в первом slice и не включает новую функциональность. Tests проверяют полноту критичных surfaces, связь с уже существующим `app.agent.policy`, обязательные gates для secret/public-token/remote/destructive surfaces и live-retest markers для VPS write behavior. Документация фиксирует правило: следующий endpoint или operation сначала получает policy entry, потом реализацию.

**Tech Stack:** Python 3.12+, dataclasses, pytest, существующие модули `app/security`, `app/agent`, `app/server`, `app/web`, `app/bot`. Рабочий production repo для выполнения плана: `C:\Users\SooL\Documents\Amneziya`.

---

## Scope

Входит в первый slice:

- policy registry для текущих критичных web/admin routes;
- policy registry для public email token routes;
- policy registry для Telegram bot logical actions;
- policy registry для уже существующих Local Agent route policies;
- policy registry для CLI/live-VPS operation classes как inventory, не как новый runner;
- tests, которые делают registry обязательным transfer gate;
- production doc с правилами использования policy matrix.

Не входит в первый slice:

- новые HTTP/API routes;
- включение `GET /agent/clients`, config download, backup, restore или reboot;
- scoped API tokens;
- изменения в web/bot behavior;
- миграция peer apply/revoke на общий runner;
- live VPS calls или новый live retest.

---

## File Structure

- Create: `app/security/surface_policy.py` - inventory-only dataclasses and registry.
- Create: `tests/security/test_surface_policy.py` - aggregate policy coverage tests.
- Create: `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md` - human-readable policy contract for future work.
- Update after implementation in AMN3: `research/amn2/transfer-backlog.md` and `docs/PROJECT_STATUS_CURRENT.ru.md` with branch/commit/test evidence.

---

## Task 1: Failing Aggregate Policy Tests

**Files:**
- Create: `tests/security/test_surface_policy.py`

- [ ] **Step 1: Create focused failing tests**

Create `tests/security/test_surface_policy.py` with:

```python
import pytest

from app.agent.policy import AGENT_ROUTE_POLICIES, first_slice_policies
from app.security.surface_policy import (
    SURFACE_POLICIES,
    get_surface_policy,
    policies_by_surface,
)


REQUIRED_POLICY_IDS = {
    "local_agent.health",
    "local_agent.version",
    "local_agent.runtime",
    "local_agent.protocols",
    "local_agent.configs.read.blocked",
    "web.auth.login_submit",
    "web.auth.logout",
    "web.config_templates.save",
    "web.config_templates.reset",
    "web.users.create",
    "web.users.update",
    "web.users.block",
    "web.users.delete",
    "web.users.disable_vpn",
    "web.users.enable_vpn",
    "web.devices.secrets",
    "web.devices.delete",
    "web.users.destroy",
    "public_token.email_verify_submit",
    "web.email.config_send",
    "web.email.recovery_start",
    "public_token.email_recover_submit",
    "web.servers.create",
    "web.servers.update",
    "web.servers.disable",
    "web.servers.sync_run",
    "web.servers.unknown_peers.ignore",
    "web.servers.unknown_peers.remove",
    "web.servers.missing_devices.add",
    "web.servers.health_run",
    "bot.admin.approve_order",
    "bot.admin.config_resend",
    "bot.user.config_resend",
    "bot.user.device_revoke",
    "bot.user.devices_reset",
    "remote.server.health_check",
    "cli.server.apply_peer_live",
    "cli.server.revoke_peer_live",
}

SECRET_RISKS = {"secret-read", "public-token-secret-read"}
PUBLIC_TOKEN_RISKS = {
    "public-token-entry",
    "public-token-state-write",
    "public-token-secret-read",
}
REMOTE_RISKS = {"remote-read", "remote-exec"}
VPS_WRITE_POLICY_IDS = {
    "web.users.disable_vpn",
    "web.users.enable_vpn",
    "web.devices.delete",
    "web.users.destroy",
    "web.servers.sync_run",
    "web.servers.unknown_peers.remove",
    "web.servers.missing_devices.add",
    "bot.admin.approve_order",
    "bot.user.device_revoke",
    "bot.user.devices_reset",
    "cli.server.apply_peer_live",
    "cli.server.revoke_peer_live",
}


def _gate_text(policy):
    return " ".join(policy.gates).lower()


def test_required_policy_ids_exist():
    actual = {policy.policy_id for policy in SURFACE_POLICIES}

    assert REQUIRED_POLICY_IDS <= actual


def test_policy_ids_are_unique():
    policy_ids = [policy.policy_id for policy in SURFACE_POLICIES]

    assert len(policy_ids) == len(set(policy_ids))


@pytest.mark.parametrize(
    "surface",
    ("web", "public-token", "bot", "local-agent", "cli", "remote-operation"),
)
def test_each_surface_has_policy_entries(surface):
    assert policies_by_surface(surface)


def test_no_policy_enables_new_behavior_in_first_slice():
    assert all(policy.enables_new_behavior is False for policy in SURFACE_POLICIES)


def test_local_agent_first_slice_matches_existing_agent_policy():
    expected = {
        (policy.method, policy.path, policy.scope)
        for policy in first_slice_policies()
    }
    actual = {
        (policy.method, policy.path, policy.auth_method.split()[-1])
        for policy in policies_by_surface("local-agent")
        if policy.implementation_mode == "inventory-only"
    }

    assert actual == expected


def test_future_local_agent_routes_are_recorded_as_blocked_future():
    future_agent_routes = {
        (policy.method, policy.path)
        for policy in AGENT_ROUTE_POLICIES
        if not policy.first_slice
    }
    blocked_surface_routes = {
        (policy.method, policy.path)
        for policy in policies_by_surface("local-agent")
        if policy.implementation_mode == "blocked-future"
    }

    assert future_agent_routes <= blocked_surface_routes


def test_secret_and_public_token_policies_have_required_gates():
    for policy in SURFACE_POLICIES:
        gates = _gate_text(policy)
        if policy.risk_class in SECRET_RISKS:
            assert policy.audit_required is True, policy.policy_id
            assert "redaction" in gates or "no raw secret" in gates, policy.policy_id
        if policy.risk_class in PUBLIC_TOKEN_RISKS:
            assert "no raw token" in gates, policy.policy_id
        if policy.risk_class == "public-token-secret-read":
            assert "purpose" in gates, policy.policy_id
            assert "ttl" in gates, policy.policy_id
            assert "one-time" in gates, policy.policy_id
            assert policy.audit_required is True, policy.policy_id


def test_web_admin_post_policies_require_csrf():
    for policy in policies_by_surface("web"):
        if policy.method == "POST":
            assert "csrf" in _gate_text(policy), policy.policy_id


def test_remote_operation_policies_are_bound_to_operation_contracts():
    for policy in SURFACE_POLICIES:
        if policy.risk_class in REMOTE_RISKS:
            assert policy.operation_contract, policy.policy_id
        if policy.risk_class == "remote-read":
            assert "read-only command policy" in _gate_text(policy), policy.policy_id
        if policy.risk_class == "remote-exec":
            assert policy.live_retest_required is True, policy.policy_id


def test_live_retest_is_marked_for_vps_write_surfaces():
    for policy_id in VPS_WRITE_POLICY_IDS:
        policy = get_surface_policy(policy_id)

        assert policy.live_retest_required is True
```

- [ ] **Step 2: Run focused tests and confirm initial failure**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'; & 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/security/test_surface_policy.py -v
```

Expected result before implementation:

```text
ModuleNotFoundError: No module named 'app.security.surface_policy'
```

---

## Task 2: Inventory-Only Policy Registry

**Files:**
- Create: `app/security/surface_policy.py`
- Modify: `tests/security/test_surface_policy.py` only if the real route inventory reveals a typo in a policy id

- [ ] **Step 1: Implement the registry module**

Create `app/security/surface_policy.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SurfaceName = Literal["web", "public-token", "bot", "local-agent", "cli", "remote-operation"]
RiskClass = Literal[
    "auth-entry",
    "auth-exit",
    "read-only",
    "secret-adjacent-read",
    "secret-read",
    "public-token-entry",
    "public-token-state-write",
    "public-token-secret-read",
    "state-write",
    "remote-read",
    "remote-exec",
    "destructive",
]
SecretClass = Literal[
    "none",
    "secret-adjacent",
    "client-config-secret",
    "token-raw-issue",
    "public-token",
    "operation-output",
]
ImplementationMode = Literal["inventory-only", "blocked-future"]


class SurfacePolicyError(ValueError):
    pass


@dataclass(frozen=True)
class SurfacePolicy:
    policy_id: str
    surface: SurfaceName
    method: str
    path: str
    actor: str
    auth_method: str
    risk_class: RiskClass
    secret_class: SecretClass
    side_effects: tuple[str, ...]
    gates: tuple[str, ...]
    audit_required: bool
    operation_contract: str
    live_retest_required: bool
    implementation_mode: ImplementationMode
    enables_new_behavior: bool
    test_refs: tuple[str, ...]
    notes: str


def _p(
    policy_id: str,
    surface: SurfaceName,
    method: str,
    path: str,
    actor: str,
    auth_method: str,
    risk_class: RiskClass,
    secret_class: SecretClass,
    side_effects: tuple[str, ...],
    gates: tuple[str, ...],
    audit_required: bool,
    operation_contract: str,
    live_retest_required: bool,
    implementation_mode: ImplementationMode,
    test_refs: tuple[str, ...],
    notes: str,
) -> SurfacePolicy:
    return SurfacePolicy(
        policy_id=policy_id,
        surface=surface,
        method=method,
        path=path,
        actor=actor,
        auth_method=auth_method,
        risk_class=risk_class,
        secret_class=secret_class,
        side_effects=side_effects,
        gates=gates,
        audit_required=audit_required,
        operation_contract=operation_contract,
        live_retest_required=live_retest_required,
        implementation_mode=implementation_mode,
        enables_new_behavior=False,
        test_refs=test_refs,
        notes=notes,
    )


SURFACE_POLICIES: tuple[SurfacePolicy, ...] = (
    _p(
        "local_agent.health",
        "local-agent",
        "GET",
        "/agent/health",
        "local-agent-controller",
        "hash-only bearer token + agent:health",
        "read-only",
        "none",
        (),
        ("AgentRoutePolicy first_slice", "audit event"),
        True,
        "Existing app.agent.policy first-slice route.",
        False,
        "inventory-only",
        ("tests/agent/test_policy.py",),
        "Health route stays local-agent first slice only.",
    ),
    _p(
        "local_agent.version",
        "local-agent",
        "GET",
        "/agent/version",
        "local-agent-controller",
        "hash-only bearer token + agent:health",
        "read-only",
        "none",
        (),
        ("AgentRoutePolicy first_slice", "audit event"),
        True,
        "Existing app.agent.policy first-slice route.",
        False,
        "inventory-only",
        ("tests/agent/test_policy.py",),
        "Version route exposes no secrets.",
    ),
    _p(
        "local_agent.runtime",
        "local-agent",
        "GET",
        "/agent/runtime",
        "local-agent-controller",
        "hash-only bearer token + agent:read",
        "read-only",
        "secret-adjacent",
        (),
        ("AgentRoutePolicy first_slice", "audit event", "no raw secret"),
        True,
        "Existing app.agent.policy first-slice route.",
        False,
        "inventory-only",
        ("tests/agent/test_policy.py",),
        "Runtime detection is read-only but remains command-adjacent.",
    ),
    _p(
        "local_agent.protocols",
        "local-agent",
        "GET",
        "/agent/protocols",
        "local-agent-controller",
        "hash-only bearer token + agent:protocols:read",
        "read-only",
        "secret-adjacent",
        (),
        ("AgentRoutePolicy first_slice", "audit event", "no raw secret"),
        True,
        "Existing app.agent.policy first-slice route.",
        False,
        "inventory-only",
        ("tests/agent/test_policy.py",),
        "Protocol listing is metadata only.",
    ),
    _p(
        "local_agent.clients.list.blocked",
        "local-agent",
        "GET",
        "/agent/clients",
        "local-agent-controller",
        "hash-only bearer token + agent:clients:read",
        "read-only",
        "secret-adjacent",
        (),
        ("blocked until privacy policy", "audit event", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        False,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "Client metadata stays blocked in first production slice.",
    ),
    _p(
        "local_agent.clients.create.blocked",
        "local-agent",
        "POST",
        "/agent/clients",
        "local-agent-controller",
        "hash-only bearer token + agent:clients:write",
        "state-write",
        "secret-adjacent",
        ("local client state",),
        ("blocked until operation contract", "audit event", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        True,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "No local-agent write route is exposed by this slice.",
    ),
    _p(
        "local_agent.clients.update.blocked",
        "local-agent",
        "PATCH",
        "/agent/clients/{id}",
        "local-agent-controller",
        "hash-only bearer token + agent:clients:write",
        "state-write",
        "secret-adjacent",
        ("local client state",),
        ("blocked until operation contract", "audit event", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        True,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "No local-agent write route is exposed by this slice.",
    ),
    _p(
        "local_agent.clients.delete.blocked",
        "local-agent",
        "DELETE",
        "/agent/clients/{id}",
        "local-agent-controller",
        "hash-only bearer token + agent:clients:write",
        "destructive",
        "secret-adjacent",
        ("local client state",),
        ("blocked until operation contract", "explicit confirmation", "audit event"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        True,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "No local-agent delete route is exposed by this slice.",
    ),
    _p(
        "local_agent.configs.read.blocked",
        "local-agent",
        "GET",
        "/agent/configs/{id}",
        "local-agent-controller",
        "hash-only bearer token + agent:configs:read",
        "secret-read",
        "client-config-secret",
        (),
        ("blocked until ownership policy", "audit event", "redaction", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        False,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        ".conf, QR and vpn:// stay blocked secret outputs.",
    ),
    _p(
        "local_agent.backup.redacted.blocked",
        "local-agent",
        "GET",
        "/agent/backup/redacted",
        "local-agent-controller",
        "hash-only bearer token + agent:backup:read",
        "secret-read",
        "secret-adjacent",
        (),
        ("blocked until backup policy", "audit event", "redaction", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        False,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "Even redacted backup needs a separate backup design.",
    ),
    _p(
        "local_agent.backup.full.blocked",
        "local-agent",
        "POST",
        "/agent/backup/full",
        "local-agent-controller",
        "hash-only bearer token + agent:backup:full",
        "secret-read",
        "client-config-secret",
        (),
        ("blocked until backup policy", "audit event", "redaction", "no raw secret"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        False,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "Full backup is secret-bearing and not first slice.",
    ),
    _p(
        "local_agent.restore.blocked",
        "local-agent",
        "POST",
        "/agent/restore",
        "local-agent-controller",
        "hash-only bearer token + agent:backup:restore",
        "destructive",
        "client-config-secret",
        ("local Amnezia state",),
        ("blocked until restore policy", "explicit confirmation", "audit event"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        True,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "Restore is destructive and not first slice.",
    ),
    _p(
        "local_agent.reboot.blocked",
        "local-agent",
        "POST",
        "/agent/reboot",
        "local-agent-controller",
        "hash-only bearer token + agent:operations:destructive",
        "destructive",
        "none",
        ("local host runtime",),
        ("blocked until dangerous-operation policy", "explicit confirmation", "audit event"),
        True,
        "Future route exists only as app.agent.policy blocked record.",
        True,
        "blocked-future",
        ("tests/agent/test_policy.py",),
        "Reboot remains out of scope.",
    ),
    _p(
        "web.auth.login_submit",
        "web",
        "POST",
        "/login",
        "public",
        "password form + session cookie",
        "auth-entry",
        "secret-adjacent",
        ("session",),
        ("csrf", "generic errors", "rate limit candidate", "no raw secret"),
        False,
        "",
        False,
        "inventory-only",
        ("tests/web/test_app.py",),
        "Login audit/rate-limit are follow-up policy work.",
    ),
    _p(
        "web.auth.logout",
        "web",
        "POST",
        "/logout",
        "web-admin",
        "session",
        "auth-exit",
        "none",
        ("session",),
        ("csrf", "session required"),
        False,
        "",
        False,
        "inventory-only",
        ("tests/web/test_app.py",),
        "Logout is current web session behavior.",
    ),
    _p(
        "web.config_templates.save",
        "web",
        "POST",
        "/config-templates/{config_version}/save",
        "web-admin",
        "session",
        "state-write",
        "secret-adjacent",
        ("config template state",),
        ("csrf", "session required", "synthetic preview", "no raw secret"),
        True,
        "",
        True,
        "inventory-only",
        ("tests/web/test_config_templates.py",),
        "Template changes can affect future generated configs.",
    ),
    _p(
        "web.config_templates.reset",
        "web",
        "POST",
        "/config-templates/{config_version}/reset",
        "web-admin",
        "session",
        "state-write",
        "secret-adjacent",
        ("config template state",),
        ("csrf", "session required", "synthetic preview", "no raw secret"),
        True,
        "",
        True,
        "inventory-only",
        ("tests/web/test_config_templates.py",),
        "Template reset can affect future generated configs.",
    ),
    _p(
        "web.users.create",
        "web",
        "POST",
        "/users/new",
        "web-admin",
        "session",
        "state-write",
        "none",
        ("users", "admin_actions"),
        ("csrf", "session required", "validation"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_users.py",),
        "Current admin user creation route.",
    ),
    _p(
        "web.users.update",
        "web",
        "POST",
        "/users/{user_id}/edit",
        "web-admin",
        "session",
        "state-write",
        "none",
        ("users", "admin_actions"),
        ("csrf", "session required", "validation"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_users.py",),
        "Current admin user update route.",
    ),
    _p(
        "web.users.block",
        "web",
        "POST",
        "/users/{user_id}/block",
        "web-admin",
        "session",
        "state-write",
        "none",
        ("users", "admin_actions"),
        ("csrf", "session required"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_users.py",),
        "Current user block route.",
    ),
    _p(
        "web.users.delete",
        "web",
        "POST",
        "/users/{user_id}/delete",
        "web-admin",
        "session",
        "destructive",
        "secret-adjacent",
        ("users", "devices", "admin_actions"),
        ("csrf", "session required", "explicit confirmation candidate"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_users.py",),
        "Existing route is inventoried; future UX can add stronger confirmation.",
    ),
    _p(
        "web.users.disable_vpn",
        "web",
        "POST",
        "/users/{user_id}/disable-vpn",
        "web-admin",
        "session",
        "remote-exec",
        "operation-output",
        ("devices", "remote peers", "admin_actions"),
        ("csrf", "session required", "operation contract", "redaction"),
        True,
        "Verified live VPS disable flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_users.py", "tests/server/test_peer_apply.py"),
        "Any behavior change requires live retest.",
    ),
    _p(
        "web.users.enable_vpn",
        "web",
        "POST",
        "/users/{user_id}/enable-vpn",
        "web-admin",
        "session",
        "remote-exec",
        "client-config-secret",
        ("devices", "remote peers", "admin_actions"),
        ("csrf", "session required", "operation contract", "redaction", "no raw secret"),
        True,
        "Verified live VPS enable/apply flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_users.py", "tests/server/test_peer_apply.py"),
        "Any behavior change requires live retest.",
    ),
    _p(
        "web.devices.secrets",
        "web",
        "POST",
        "/users/{user_id}/devices/{device_id}/secrets",
        "web-admin",
        "session",
        "secret-read",
        "client-config-secret",
        (),
        ("csrf", "session required", "user/device match", "audit event", "redaction", "no raw secret"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_users.py", "tests/services/test_config_delivery.py"),
        "Config artifacts are client-config-secret.",
    ),
    _p(
        "web.devices.delete",
        "web",
        "POST",
        "/users/{user_id}/devices/{device_id}/delete",
        "web-admin",
        "session",
        "remote-exec",
        "operation-output",
        ("devices", "remote peers", "admin_actions"),
        ("csrf", "session required", "operation contract", "redaction"),
        True,
        "Verified live VPS selective delete flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_users.py", "tests/server/test_peer_apply.py"),
        "Any behavior change requires live retest.",
    ),
    _p(
        "web.users.destroy",
        "web",
        "POST",
        "/users/{user_id}/destroy",
        "web-admin",
        "session",
        "destructive",
        "operation-output",
        ("users", "devices", "remote peers", "admin_actions"),
        ("csrf", "session required", "explicit confirmation candidate", "operation contract", "redaction"),
        True,
        "Current destructive web route; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_users.py",),
        "Future API must split preview/apply/recovery.",
    ),
    _p(
        "web.email.config_send",
        "web",
        "POST",
        "/users/{user_id}/devices/{device_id}/email-config",
        "web-admin",
        "session",
        "secret-read",
        "client-config-secret",
        (),
        ("csrf", "session required", "user/device match", "audit event", "redaction", "no raw secret"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_email_delivery.py",),
        "Email config delivery sends real .conf/QR/vpn:// artifacts.",
    ),
    _p(
        "web.email.recovery_start",
        "web",
        "POST",
        "/users/{user_id}/devices/{device_id}/email-recovery/start",
        "web-admin",
        "session",
        "state-write",
        "token-raw-issue",
        ("email recovery tokens", "admin_actions"),
        ("csrf", "session required", "token hash storage", "audit event", "no raw token"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_email_delivery.py",),
        "Raw recovery token must not be persisted or audited.",
    ),
    _p(
        "public_token.email_verify_submit",
        "public-token",
        "POST",
        "/email/verify",
        "public-token-holder",
        "raw token + stored hash lookup",
        "public-token-state-write",
        "public-token",
        ("email verification state",),
        ("purpose", "ttl", "one-time", "generic errors", "no raw token"),
        False,
        "",
        False,
        "inventory-only",
        ("tests/web/test_email_delivery.py",),
        "Public token is purpose-bound, not admin auth.",
    ),
    _p(
        "public_token.email_recover_submit",
        "public-token",
        "POST",
        "/email/recover",
        "public-token-holder",
        "raw token + stored hash lookup",
        "public-token-secret-read",
        "client-config-secret",
        (),
        ("purpose", "ttl", "one-time", "user/device binding", "rate limit candidate", "audit event", "redaction", "no raw token"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_email_delivery.py",),
        "Public token can release config secret only through strict one-time recovery.",
    ),
    _p(
        "web.servers.create",
        "web",
        "POST",
        "/servers/new",
        "web-admin",
        "session",
        "state-write",
        "secret-adjacent",
        ("servers", "admin_actions"),
        ("csrf", "session required", "validation", "no raw secret"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_servers.py",),
        "Server connection fields remain secret-adjacent.",
    ),
    _p(
        "web.servers.update",
        "web",
        "POST",
        "/servers/{server_id}/edit",
        "web-admin",
        "session",
        "state-write",
        "secret-adjacent",
        ("servers", "admin_actions"),
        ("csrf", "session required", "validation", "no raw secret"),
        True,
        "",
        True,
        "inventory-only",
        ("tests/web/test_servers.py",),
        "Server runtime/config changes can affect live behavior.",
    ),
    _p(
        "web.servers.disable",
        "web",
        "POST",
        "/servers/{server_id}/disable",
        "web-admin",
        "session",
        "state-write",
        "none",
        ("servers", "admin_actions"),
        ("csrf", "session required"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_servers.py",),
        "Disables local server record.",
    ),
    _p(
        "web.servers.sync_run",
        "web",
        "POST",
        "/servers/{server_id}/sync/run",
        "web-admin",
        "session",
        "remote-read",
        "operation-output",
        ("peer sync snapshots", "admin_actions"),
        ("csrf", "session required", "read-only command policy", "redaction"),
        True,
        "Existing peer sync reads live VPS state and updates local sync view.",
        True,
        "inventory-only",
        ("tests/web/test_servers.py", "tests/server/test_peer_sync.py"),
        "Sync classification changes require live retest.",
    ),
    _p(
        "web.servers.unknown_peers.ignore",
        "web",
        "POST",
        "/servers/{server_id}/unknown-peers/ignore",
        "web-admin",
        "session",
        "state-write",
        "none",
        ("peer sync ignore state", "admin_actions"),
        ("csrf", "session required"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/web/test_servers.py",),
        "Local ignore marker only.",
    ),
    _p(
        "web.servers.unknown_peers.remove",
        "web",
        "POST",
        "/servers/{server_id}/unknown-peers/remove",
        "web-admin",
        "session",
        "remote-exec",
        "operation-output",
        ("remote peers", "admin_actions"),
        ("csrf", "session required", "operation contract", "redaction"),
        True,
        "Existing live VPS remove flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_servers.py", "tests/server/test_peer_apply.py"),
        "Removing external peers requires careful confirmation in future API.",
    ),
    _p(
        "web.servers.missing_devices.add",
        "web",
        "POST",
        "/servers/{server_id}/missing-devices/{device_id}/add",
        "web-admin",
        "session",
        "remote-exec",
        "client-config-secret",
        ("remote peers", "admin_actions"),
        ("csrf", "session required", "operation contract", "redaction", "no raw secret"),
        True,
        "Existing live VPS add missing local device flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/web/test_servers.py", "tests/server/test_peer_apply.py"),
        "Adding a peer writes live VPS state.",
    ),
    _p(
        "web.servers.health_run",
        "web",
        "POST",
        "/servers/{server_id}/health/run",
        "web-admin",
        "session",
        "remote-read",
        "operation-output",
        ("server_health_checks", "admin_actions"),
        ("csrf", "session required", "read-only command policy", "redaction"),
        True,
        "RemoteOperationRunner read-only health check.",
        False,
        "inventory-only",
        ("tests/server/test_operation_runner.py", "tests/web/test_servers.py"),
        "Canonical read-only remote operation model.",
    ),
    _p(
        "bot.admin.approve_order",
        "bot",
        "ACTION",
        "ADMIN_APPROVE_PREFIX callback",
        "telegram-admin",
        "Telegram identity + workflow.is_admin",
        "remote-exec",
        "client-config-secret",
        ("orders", "devices", "remote peers", "admin_actions"),
        ("workflow.is_admin", "operation contract", "audit event", "redaction", "no raw secret"),
        True,
        "Verified live VPS approve/apply flow; not generalized API.",
        True,
        "inventory-only",
        ("tests/bot/test_bot_workflows.py",),
        "Verified baseline behavior contract.",
    ),
    _p(
        "bot.admin.config_resend",
        "bot",
        "ACTION",
        "ADMIN_RESEND_PREFIX callback",
        "telegram-admin",
        "Telegram identity + workflow.is_admin",
        "secret-read",
        "client-config-secret",
        (),
        ("workflow.is_admin", "audit event", "redaction", "no raw secret"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/bot/test_bot_workflows.py", "tests/bot/test_delivery.py"),
        "Admin resend emits config artifacts.",
    ),
    _p(
        "bot.user.config_resend",
        "bot",
        "ACTION",
        "USER_RESEND_PREFIX callback",
        "telegram-user",
        "Telegram identity + get_user_device ownership",
        "secret-read",
        "client-config-secret",
        (),
        ("ownership", "audit event", "redaction", "no raw secret"),
        True,
        "",
        False,
        "inventory-only",
        ("tests/bot/test_bot_workflows.py", "tests/bot/test_delivery.py"),
        "User resend must remain own-device only.",
    ),
    _p(
        "bot.user.device_revoke",
        "bot",
        "ACTION",
        "USER_REVOKE_CONFIRM_PREFIX callback",
        "telegram-user",
        "Telegram identity + get_user_device ownership",
        "remote-exec",
        "operation-output",
        ("devices", "remote peers"),
        ("ownership", "operation contract", "audit event", "redaction"),
        True,
        "Existing revoke flow removes remote peer before local revoke when configured.",
        True,
        "inventory-only",
        ("tests/bot/test_bot_workflows.py",),
        "Partial failure policy blocks broader API expansion.",
    ),
    _p(
        "bot.user.devices_reset",
        "bot",
        "ACTION",
        "USER_RESET_DEVICES_CONFIRM_CALLBACK",
        "telegram-user",
        "Telegram identity + user ownership",
        "remote-exec",
        "operation-output",
        ("devices", "remote peers"),
        ("ownership", "operation contract", "audit event", "redaction"),
        True,
        "Existing reset iterates owned devices; not generalized API.",
        True,
        "inventory-only",
        ("tests/bot/test_bot_workflows.py",),
        "Needs explicit partial-failure recovery before broader write API.",
    ),
    _p(
        "remote.server.health_check",
        "remote-operation",
        "OPERATION",
        "server.health.check",
        "web-admin or cli-operator or system",
        "session, cli or system",
        "remote-read",
        "operation-output",
        ("server_health_checks",),
        ("read-only command policy", "redaction", "no raw secret"),
        True,
        "RemoteOperationRunner read-only health check.",
        False,
        "inventory-only",
        ("tests/server/test_operation_runner.py", "tests/server/test_checks.py"),
        "First runner slice remains read-only.",
    ),
    _p(
        "cli.server.apply_peer_live",
        "cli",
        "COMMAND",
        "server apply-peer --apply",
        "cli-operator",
        "local shell",
        "remote-exec",
        "client-config-secret",
        ("remote peers",),
        ("explicit apply", "operation contract", "redaction", "no raw secret"),
        True,
        "Existing CLI live apply path; not future generic API.",
        True,
        "inventory-only",
        ("tests/server/test_peer_apply.py",),
        "Any behavior change requires live retest.",
    ),
    _p(
        "cli.server.revoke_peer_live",
        "cli",
        "COMMAND",
        "server revoke-peer --apply",
        "cli-operator",
        "local shell",
        "remote-exec",
        "operation-output",
        ("remote peers",),
        ("explicit apply", "operation contract", "redaction"),
        True,
        "Existing CLI live revoke path; not future generic API.",
        True,
        "inventory-only",
        ("tests/server/test_peer_apply.py",),
        "Any behavior change requires live retest.",
    ),
)


def get_surface_policy(policy_id: str) -> SurfacePolicy:
    for policy in SURFACE_POLICIES:
        if policy.policy_id == policy_id:
            return policy
    raise SurfacePolicyError(f"No surface policy for {policy_id}")


def policies_by_surface(surface: SurfaceName) -> tuple[SurfacePolicy, ...]:
    return tuple(policy for policy in SURFACE_POLICIES if policy.surface == surface)
```

- [ ] **Step 2: Run the focused policy tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'; & 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/security/test_surface_policy.py -v
```

Expected result:

```text
10 passed
```

If a referenced test file name differs in the local tree, update only `test_refs` strings in `app/security/surface_policy.py`. Do not change production behavior to satisfy this slice.

---

## Task 3: Production Policy Documentation

**Files:**
- Create: `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md`

- [ ] **Step 1: Add the policy contract document**

Create `docs/ROUTE_AUTH_OPERATION_POLICY.ru.md` with:

```markdown
# Route/Auth/Operation Policy

Дата: 2026-05-31.

Этот документ фиксирует первый безопасный API-readiness slice после verified live VPS baseline.

## Статус

`app/security/surface_policy.py` является inventory-only policy registry. Он не включает новые endpoints и не меняет runtime behavior.

## Правило для следующих изменений

Новый route, bot action, CLI command или remote operation не добавляется в production без policy entry, где указаны:

- actor;
- auth method;
- risk class;
- secret class;
- side effects;
- gates;
- audit decision;
- operation contract;
- live retest trigger;
- test references.

## Запреты первого slice

- Не включать `GET /agent/clients`.
- Не добавлять config/self-service API.
- Не добавлять backup, restore, reboot или generic write API.
- Не трогать live VPS.
- Не копировать upstream code.

## Live Retest Rule

Новый live retest нужен, если меняется хотя бы одна из областей:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.

Policy-only changes and tests do not require live VPS retest.
```

- [ ] **Step 2: Verify docs do not claim new behavior**

Run:

```powershell
Select-String -Path docs\ROUTE_AUTH_OPERATION_POLICY.ru.md -Pattern 'new endpoint|новый endpoint|live VPS touched'
```

Expected result:

```text
<no matches>
```

---

## Task 4: Regression Verification

**Files:**
- No file edits unless tests reveal a policy typo.

- [ ] **Step 1: Run focused policy and adjacent tests**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'; & 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/security/test_surface_policy.py tests/agent/test_policy.py tests/server/test_operation_runner.py tests/server/test_checks.py -v
```

Expected result:

```text
passed
```

- [ ] **Step 2: Run web/bot smoke tests that are named by policy refs**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'; & 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_email_delivery.py tests/bot/test_bot_workflows.py -v
```

Expected result:

```text
passed
```

- [ ] **Step 3: Check formatting and whitespace**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' diff --check
```

Expected result:

```text
<no output>
```

---

## Task 5: Production Commit

**Files:**
- Stage the exact files created in this plan.

- [ ] **Step 1: Review the diff**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' diff -- app/security/surface_policy.py tests/security/test_surface_policy.py docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
```

Expected changed files:

```text
app/security/surface_policy.py
tests/security/test_surface_policy.py
docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
```

- [ ] **Step 2: Commit production slice**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add app/security/surface_policy.py tests/security/test_surface_policy.py docs/ROUTE_AUTH_OPERATION_POLICY.ru.md
& 'C:\Program Files\Git\cmd\git.exe' diff --cached --check
& 'C:\Program Files\Git\cmd\git.exe' commit -m "Add route auth operation policy matrix"
```

Expected result:

```text
Commit is created on codex-vps-test-prep with message "Add route auth operation policy matrix".
```

Do not push until the user confirms the production branch should be published, unless the current session already has explicit push approval for `amn2`.

---

## Task 6: AMN3 Return Note

**Files in `C:\Users\SooL\Documents\VPS-OPS-LAB`:**
- Modify: `research/amn2/transfer-backlog.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`

- [ ] **Step 1: Record production evidence in AMN3**

After the `amn2` commit exists, update AMN3 with:

```markdown
## Route/Auth/Operation Policy Matrix

Status: `implemented-in-amn2` or `plan-ready`, depending on execution state.

Production branch: `codex-vps-test-prep`
Production commit: value from `git log -1 --oneline --decorate` after the production commit
Plan: `docs/superpowers/plans/2026-05-31-amn2-route-auth-operation-policy-matrix.md`
Verification:

- `pytest tests/security/test_surface_policy.py tests/agent/test_policy.py tests/server/test_operation_runner.py tests/server/test_checks.py -v`
- `pytest tests/web/test_app.py tests/web/test_users.py tests/web/test_servers.py tests/web/test_email_delivery.py tests/bot/test_bot_workflows.py -v`

Live VPS: not touched.
New endpoints: none.
New write behavior: none.
```

Use the actual commit SHA and actual test output before marking `implemented-in-amn2`.

- [ ] **Step 2: Commit AMN3 evidence**

Run from `C:\Users\SooL\Documents\VPS-OPS-LAB`:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add research/amn2/transfer-backlog.md docs/PROJECT_STATUS_CURRENT.ru.md
& 'C:\Program Files\Git\cmd\git.exe' diff --cached --check
& 'C:\Program Files\Git\cmd\git.exe' commit -m "Record route policy matrix transfer evidence"
& 'C:\Program Files\Git\cmd\git.exe' push origin master
```

Expected result:

```text
To https://github.com/barakov-dot/amn3.git
   <old>..<new>  master -> master
```

---

## Next Slice Recommendation

После этого slice следующий порядок остается таким:

1. Redaction coverage для config/QR/vpn/public-token/agent/remote outputs, если она еще не закрыта в текущем `amn2`.
2. Config delivery integrity regression suite: `.conf`, QR decode, `vpn://`, non-ASCII names, export/result contract.
3. Local Agent hardening: audit sink, token rotation/revoke, runtime metadata.
4. Read-only clients/metrics API только после privacy classification.
5. Remote write operation contract только после partial-failure/idempotency/recovery design.

PRVTPRO остается paused targeted input. KYORESUAS остается architecture reference. Ни один из них не становится источником copied production code.
