# Local Amnezia Agent First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить в `amn2` первый безопасный read-only Local Amnezia Agent slice: route policy, scoped token auth, fake runtime adapter и API endpoints `/agent/health`, `/agent/version`, `/agent/runtime`, `/agent/protocols` без выдачи secrets и без write operations.

**Architecture:** Agent добавляется как отдельный package `app/agent`, а не как часть текущей web-админки. Первый slice изолирован от live VPS: он использует fake/local adapter, hash-only scoped tokens, protected FastAPI app factory, in-memory audit sink for tests и route policy matrix для будущего расширения.

**Tech Stack:** Python 3.12+, dataclasses, Protocol, hashlib/secrets, FastAPI, Pydantic-compatible dict responses, pytest, FastAPI TestClient.

---

## Рабочий Репозиторий

Исполнять план в production repo:

```text
C:\Users\SooL\Documents\Amneziya
```

Связанный design spec:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\docs\superpowers\specs\2026-05-31-local-amnezia-agent-design.md
```

## Scope

Входит в первый slice:

- отдельный package `app/agent`;
- policy matrix для route surface agent;
- hash-only bearer token auth with scopes;
- fake runtime adapter;
- local runtime/protocol snapshot models;
- FastAPI app factory для Local Agent;
- protected read-only endpoints;
- disabled public docs/openapi for agent app;
- audit events for read routes;
- tests for policy, auth, runtime and API behavior;
- краткая русская документация.

Не входит в первый slice:

- create/disable/delete clients;
- config, QR, `.conf`, `vpn://`, Xray link delivery;
- backup/import/reboot;
- Docker mutation;
- SSH tunnel/mTLS implementation;
- DB migration for agent tokens;
- integration into existing `app/web/app.py`;
- production systemd unit.

## Структура Файлов

- Create: `app/agent/__init__.py` - package marker and public exports kept minimal.
- Create: `app/agent/policy.py` - route policy matrix, risk classes, required scopes.
- Create: `app/agent/auth.py` - hash-only scoped bearer token validation.
- Create: `app/agent/runtime.py` - runtime snapshot models and fake adapter.
- Create: `app/agent/audit.py` - audit event model and in-memory sink for first slice tests.
- Create: `app/agent/api.py` - FastAPI app factory and read-only endpoints.
- Create: `tests/agent/__init__.py` - test package marker.
- Create: `tests/agent/test_policy.py` - policy coverage tests.
- Create: `tests/agent/test_auth.py` - token auth tests.
- Create: `tests/agent/test_runtime.py` - fake runtime and secret-free snapshot tests.
- Create: `tests/agent/test_api.py` - protected endpoint and audit tests.
- Create: `docs/LOCAL_AGENT.ru.md` - operator-facing Russian summary of first slice.

---

### Task 1: Route Policy Matrix

**Files:**
- Create: `app/agent/__init__.py`
- Create: `app/agent/policy.py`
- Create: `tests/agent/__init__.py`
- Create: `tests/agent/test_policy.py`

- [ ] **Step 1: Write failing policy tests**

Create `tests/agent/__init__.py`:

```python
```

Create `tests/agent/test_policy.py`:

```python
import pytest

from app.agent.policy import (
    AGENT_ROUTE_POLICIES,
    AgentPolicyError,
    first_slice_policies,
    get_policy,
)


def test_first_slice_routes_have_explicit_read_only_policies():
    expected = {
        ("GET", "/agent/health", "agent:health", "read-only"),
        ("GET", "/agent/version", "agent:health", "read-only"),
        ("GET", "/agent/runtime", "agent:read", "read-only-runtime"),
        ("GET", "/agent/protocols", "agent:protocols:read", "read-only-runtime"),
    }

    actual = {
        (policy.method, policy.path, policy.scope, policy.risk_class)
        for policy in first_slice_policies()
    }

    assert actual == expected
    assert all(policy.audit_required for policy in first_slice_policies())


def test_secret_and_write_routes_are_not_in_first_slice():
    risky_paths = {
        "/agent/clients",
        "/agent/clients/{id}",
        "/agent/configs/{id}",
        "/agent/backup/redacted",
        "/agent/backup/full",
        "/agent/restore",
        "/agent/reboot",
    }

    first_slice_paths = {policy.path for policy in first_slice_policies()}

    assert risky_paths.isdisjoint(first_slice_paths)


def test_get_policy_returns_exact_policy():
    policy = get_policy("GET", "/agent/protocols")

    assert policy.scope == "agent:protocols:read"
    assert policy.risk_class == "read-only-runtime"
    assert policy.first_slice is True


def test_get_policy_rejects_unknown_route():
    with pytest.raises(AgentPolicyError, match="No agent route policy"):
        get_policy("POST", "/agent/clients")


def test_every_policy_has_scope_risk_and_audit_decision():
    for policy in AGENT_ROUTE_POLICIES:
        assert policy.method
        assert policy.path.startswith("/agent/")
        assert policy.scope.startswith("agent:")
        assert policy.risk_class in {
            "read-only",
            "read-only-runtime",
            "secret-read",
            "state-write",
            "destructive-local",
        }
        assert isinstance(policy.audit_required, bool)
```

- [ ] **Step 2: Run policy tests and confirm expected failure**

Run:

```powershell
python -m pytest tests/agent/test_policy.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.agent'`.

- [ ] **Step 3: Add policy implementation**

Create `app/agent/__init__.py`:

```python
"""Local Amnezia Agent first-slice package."""
```

Create `app/agent/policy.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AgentRiskClass = Literal[
    "read-only",
    "read-only-runtime",
    "secret-read",
    "state-write",
    "destructive-local",
]


class AgentPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class AgentRoutePolicy:
    method: str
    path: str
    risk_class: AgentRiskClass
    scope: str
    audit_required: bool
    first_slice: bool


AGENT_ROUTE_POLICIES: tuple[AgentRoutePolicy, ...] = (
    AgentRoutePolicy(
        method="GET",
        path="/agent/health",
        risk_class="read-only",
        scope="agent:health",
        audit_required=True,
        first_slice=True,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/version",
        risk_class="read-only",
        scope="agent:health",
        audit_required=True,
        first_slice=True,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/runtime",
        risk_class="read-only-runtime",
        scope="agent:read",
        audit_required=True,
        first_slice=True,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/protocols",
        risk_class="read-only-runtime",
        scope="agent:protocols:read",
        audit_required=True,
        first_slice=True,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/clients",
        risk_class="read-only",
        scope="agent:clients:read",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="POST",
        path="/agent/clients",
        risk_class="state-write",
        scope="agent:clients:write",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="PATCH",
        path="/agent/clients/{id}",
        risk_class="state-write",
        scope="agent:clients:write",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="DELETE",
        path="/agent/clients/{id}",
        risk_class="state-write",
        scope="agent:clients:write",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/configs/{id}",
        risk_class="secret-read",
        scope="agent:configs:read",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="GET",
        path="/agent/backup/redacted",
        risk_class="secret-read",
        scope="agent:backup:read",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="POST",
        path="/agent/backup/full",
        risk_class="secret-read",
        scope="agent:backup:full",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="POST",
        path="/agent/restore",
        risk_class="destructive-local",
        scope="agent:backup:restore",
        audit_required=True,
        first_slice=False,
    ),
    AgentRoutePolicy(
        method="POST",
        path="/agent/reboot",
        risk_class="destructive-local",
        scope="agent:operations:destructive",
        audit_required=True,
        first_slice=False,
    ),
)


def get_policy(method: str, path: str) -> AgentRoutePolicy:
    normalized_method = method.upper()
    for policy in AGENT_ROUTE_POLICIES:
        if policy.method == normalized_method and policy.path == path:
            return policy
    raise AgentPolicyError(f"No agent route policy for {normalized_method} {path}")


def first_slice_policies() -> tuple[AgentRoutePolicy, ...]:
    return tuple(policy for policy in AGENT_ROUTE_POLICIES if policy.first_slice)
```

- [ ] **Step 4: Run policy tests and confirm pass**

Run:

```powershell
python -m pytest tests/agent/test_policy.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit policy slice**

Run:

```powershell
git add app/agent/__init__.py app/agent/policy.py tests/agent/__init__.py tests/agent/test_policy.py
git commit -m "Add local agent route policy"
```

---

### Task 2: Scoped Agent Token Auth

**Files:**
- Create: `app/agent/auth.py`
- Create: `tests/agent/test_auth.py`

- [ ] **Step 1: Write failing auth tests**

Create `tests/agent/test_auth.py`:

```python
from datetime import datetime, timedelta, timezone

import pytest

from app.agent.auth import (
    AgentAuthError,
    AgentToken,
    authenticate_agent_token,
    hash_agent_token,
)


def _future() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=10)


def test_hash_agent_token_is_stable_and_does_not_return_raw_token():
    raw = "raw-agent-token"

    hashed = hash_agent_token(raw)

    assert hashed.startswith("sha256:")
    assert hashed == hash_agent_token(raw)
    assert raw not in hashed


def test_authenticate_agent_token_accepts_required_scope():
    raw = "raw-agent-token"
    token = AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(raw),
        scopes=frozenset({"agent:health", "agent:read"}),
        expires_at=_future(),
        owner="local-controller",
    )

    authenticated = authenticate_agent_token(
        raw,
        tokens=(token,),
        required_scope="agent:read",
    )

    assert authenticated.token_id == "agent-token-1"
    assert authenticated.owner == "local-controller"


@pytest.mark.parametrize("raw", ["", "wrong-token"])
def test_authenticate_agent_token_rejects_missing_or_unknown_token(raw):
    token = AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token("right-token"),
        scopes=frozenset({"agent:health"}),
        expires_at=_future(),
    )

    with pytest.raises(AgentAuthError, match="Invalid agent token"):
        authenticate_agent_token(
            raw,
            tokens=(token,),
            required_scope="agent:health",
        )


def test_authenticate_agent_token_rejects_insufficient_scope():
    raw = "raw-agent-token"
    token = AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(raw),
        scopes=frozenset({"agent:health"}),
        expires_at=_future(),
    )

    with pytest.raises(AgentAuthError, match="Missing required scope"):
        authenticate_agent_token(
            raw,
            tokens=(token,),
            required_scope="agent:protocols:read",
        )


def test_authenticate_agent_token_rejects_expired_token():
    raw = "raw-agent-token"
    token = AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(raw),
        scopes=frozenset({"agent:health"}),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    with pytest.raises(AgentAuthError, match="expired"):
        authenticate_agent_token(
            raw,
            tokens=(token,),
            required_scope="agent:health",
        )


def test_authenticate_agent_token_rejects_revoked_token():
    raw = "raw-agent-token"
    token = AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(raw),
        scopes=frozenset({"agent:health"}),
        expires_at=_future(),
        revoked_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AgentAuthError, match="revoked"):
        authenticate_agent_token(
            raw,
            tokens=(token,),
            required_scope="agent:health",
        )
```

- [ ] **Step 2: Run auth tests and confirm expected failure**

Run:

```powershell
python -m pytest tests/agent/test_auth.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.agent.auth'`.

- [ ] **Step 3: Add auth implementation**

Create `app/agent/auth.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import secrets
from collections.abc import Sequence


class AgentAuthError(ValueError):
    pass


@dataclass(frozen=True)
class AgentToken:
    token_id: str
    token_hash: str
    scopes: frozenset[str]
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    owner: str = "local-controller"


def hash_agent_token(raw_token: str) -> str:
    digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def authenticate_agent_token(
    raw_token: str,
    *,
    tokens: Sequence[AgentToken],
    required_scope: str,
    now: datetime | None = None,
) -> AgentToken:
    if not raw_token:
        raise AgentAuthError("Invalid agent token")
    candidate_hash = hash_agent_token(raw_token)
    for token in tokens:
        if not secrets.compare_digest(candidate_hash, token.token_hash):
            continue
        _validate_token_state(token, required_scope=required_scope, now=now)
        return token
    raise AgentAuthError("Invalid agent token")


def _validate_token_state(
    token: AgentToken,
    *,
    required_scope: str,
    now: datetime | None,
) -> None:
    actual_now = now or datetime.now(timezone.utc)
    if token.revoked_at is not None:
        raise AgentAuthError("Agent token is revoked")
    if token.expires_at is not None and token.expires_at <= actual_now:
        raise AgentAuthError("Agent token is expired")
    if required_scope not in token.scopes:
        raise AgentAuthError(f"Missing required scope: {required_scope}")
```

- [ ] **Step 4: Run auth and policy tests**

Run:

```powershell
python -m pytest tests/agent/test_auth.py tests/agent/test_policy.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit auth slice**

Run:

```powershell
git add app/agent/auth.py tests/agent/test_auth.py
git commit -m "Add scoped local agent token auth"
```

---

### Task 3: Runtime Snapshot And Fake Adapter

**Files:**
- Create: `app/agent/runtime.py`
- Create: `tests/agent/test_runtime.py`

- [ ] **Step 1: Write failing runtime tests**

Create `tests/agent/test_runtime.py`:

```python
from app.agent.runtime import (
    FakeLocalRuntimeAdapter,
    ProtocolSnapshot,
    RuntimeSnapshot,
)


def test_fake_runtime_adapter_returns_default_read_only_snapshot():
    adapter = FakeLocalRuntimeAdapter()

    snapshot = adapter.snapshot()

    assert snapshot.server_name == "local-agent-dev"
    assert snapshot.runtime_type == "fake"
    assert snapshot.status == "running"
    assert snapshot.protocols == (
        ProtocolSnapshot(
            name="amneziawg",
            status="unknown",
            runtime_type="fake",
            capabilities=("detect", "status"),
            container_name=None,
            interface=None,
            client_count=None,
        ),
    )


def test_fake_runtime_adapter_can_return_custom_snapshot():
    custom = RuntimeSnapshot(
        server_name="demo-vps",
        runtime_type="docker",
        status="running",
        protocols=(
            ProtocolSnapshot(
                name="xray",
                status="running",
                runtime_type="docker",
                capabilities=("detect", "status"),
                container_name="amnezia-xray",
                interface=None,
                client_count=3,
            ),
        ),
    )

    snapshot = FakeLocalRuntimeAdapter(snapshot=custom).snapshot()

    assert snapshot == custom


def test_runtime_snapshot_does_not_contain_secret_bearing_fields():
    snapshot = FakeLocalRuntimeAdapter().snapshot()
    rendered = repr(snapshot).lower()

    for marker in (
        "privatekey",
        "private_key",
        "preshared",
        "token",
        "vpn://",
        "client_config",
        "password",
    ):
        assert marker not in rendered
```

- [ ] **Step 2: Run runtime tests and confirm expected failure**

Run:

```powershell
python -m pytest tests/agent/test_runtime.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.agent.runtime'`.

- [ ] **Step 3: Add runtime models and fake adapter**

Create `app/agent/runtime.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


RuntimeStatus = Literal["running", "degraded", "stopped", "unknown"]
ProtocolStatus = Literal["running", "degraded", "stopped", "unknown"]


@dataclass(frozen=True)
class ProtocolSnapshot:
    name: str
    status: ProtocolStatus
    runtime_type: str
    capabilities: tuple[str, ...]
    container_name: str | None = None
    interface: str | None = None
    client_count: int | None = None


@dataclass(frozen=True)
class RuntimeSnapshot:
    server_name: str
    runtime_type: str
    status: RuntimeStatus
    protocols: tuple[ProtocolSnapshot, ...]


class LocalRuntimeAdapter(Protocol):
    def snapshot(self) -> RuntimeSnapshot:
        pass


class FakeLocalRuntimeAdapter:
    def __init__(self, snapshot: RuntimeSnapshot | None = None) -> None:
        self._snapshot = snapshot or RuntimeSnapshot(
            server_name="local-agent-dev",
            runtime_type="fake",
            status="running",
            protocols=(
                ProtocolSnapshot(
                    name="amneziawg",
                    status="unknown",
                    runtime_type="fake",
                    capabilities=("detect", "status"),
                ),
            ),
        )

    def snapshot(self) -> RuntimeSnapshot:
        return self._snapshot
```

- [ ] **Step 4: Run runtime tests**

Run:

```powershell
python -m pytest tests/agent/test_runtime.py tests/agent/test_auth.py tests/agent/test_policy.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit runtime slice**

Run:

```powershell
git add app/agent/runtime.py tests/agent/test_runtime.py
git commit -m "Add fake local agent runtime adapter"
```

---

### Task 4: Protected Read-Only Agent API

**Files:**
- Create: `app/agent/audit.py`
- Create: `app/agent/api.py`
- Create: `tests/agent/test_api.py`

- [ ] **Step 1: Write failing API tests**

Create `tests/agent/test_api.py`:

```python
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.agent.api import create_agent_app
from app.agent.audit import InMemoryAgentAuditSink
from app.agent.auth import AgentToken, hash_agent_token
from app.agent.runtime import (
    FakeLocalRuntimeAdapter,
    ProtocolSnapshot,
    RuntimeSnapshot,
)


RAW_TOKEN = "raw-agent-token"


def _token(scopes: set[str]) -> AgentToken:
    return AgentToken(
        token_id="agent-token-1",
        token_hash=hash_agent_token(RAW_TOKEN),
        scopes=frozenset(scopes),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        owner="test-controller",
    )


def _client(scopes: set[str]):
    audit = InMemoryAgentAuditSink()
    adapter = FakeLocalRuntimeAdapter(
        RuntimeSnapshot(
            server_name="demo-vps",
            runtime_type="docker",
            status="running",
            protocols=(
                ProtocolSnapshot(
                    name="amneziawg",
                    status="running",
                    runtime_type="docker",
                    capabilities=("detect", "status"),
                    container_name="amnezia-awg",
                    interface="awg0",
                    client_count=2,
                ),
            ),
        )
    )
    app = create_agent_app(
        adapter=adapter,
        tokens=(_token(scopes),),
        audit_sink=audit,
        build_version="test-build",
    )
    return TestClient(app), audit


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {RAW_TOKEN}"}


def test_agent_docs_are_not_public():
    client, audit = _client({"agent:health"})

    response = client.get("/docs")

    assert response.status_code == 404
    assert audit.events == []


def test_health_requires_bearer_token():
    client, audit = _client({"agent:health"})

    response = client.get("/agent/health")

    assert response.status_code == 401
    assert "agent token" in response.json()["detail"].lower()
    assert audit.events == []


def test_health_rejects_invalid_token():
    client, audit = _client({"agent:health"})

    response = client.get(
        "/agent/health",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert audit.events == []


def test_runtime_rejects_insufficient_scope():
    client, audit = _client({"agent:health"})

    response = client.get("/agent/runtime", headers=_auth_headers())

    assert response.status_code == 403
    assert "scope" in response.json()["detail"].lower()
    assert audit.events == []


def test_health_and_version_return_secret_free_metadata():
    client, audit = _client({"agent:health"})

    health = client.get("/agent/health", headers=_auth_headers())
    version = client.get("/agent/version", headers=_auth_headers())

    assert health.status_code == 200
    assert health.json() == {
        "status": "ok",
        "service": "local-amnezia-agent",
    }
    assert version.status_code == 200
    assert version.json() == {
        "api": "local-amnezia-agent",
        "version": "test-build",
        "write_enabled": False,
    }
    assert [event.path for event in audit.events] == [
        "/agent/health",
        "/agent/version",
    ]
    assert all(event.result == "allowed" for event in audit.events)


def test_runtime_endpoint_returns_read_only_runtime_snapshot():
    client, audit = _client({"agent:read"})

    response = client.get("/agent/runtime", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "server_name": "demo-vps",
        "runtime_type": "docker",
        "status": "running",
    }
    assert audit.events[-1].path == "/agent/runtime"
    assert audit.events[-1].scope == "agent:read"


def test_protocols_endpoint_returns_read_only_protocol_snapshot():
    client, audit = _client({"agent:protocols:read"})

    response = client.get("/agent/protocols", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "protocols": [
            {
                "name": "amneziawg",
                "status": "running",
                "runtime_type": "docker",
                "capabilities": ["detect", "status"],
                "container_name": "amnezia-awg",
                "interface": "awg0",
                "client_count": 2,
            }
        ]
    }
    assert audit.events[-1].path == "/agent/protocols"
    assert audit.events[-1].scope == "agent:protocols:read"


def test_first_slice_does_not_expose_secret_or_write_routes():
    client, audit = _client(
        {
            "agent:health",
            "agent:read",
            "agent:protocols:read",
            "agent:configs:read",
            "agent:clients:write",
        }
    )

    config_response = client.get("/agent/configs/client-1", headers=_auth_headers())
    create_response = client.post("/agent/clients", headers=_auth_headers(), json={})
    reboot_response = client.post("/agent/reboot", headers=_auth_headers(), json={})

    assert config_response.status_code == 404
    assert create_response.status_code == 404
    assert reboot_response.status_code == 404
    assert audit.events == []


def test_agent_api_responses_do_not_contain_secret_markers():
    client, audit = _client(
        {
            "agent:health",
            "agent:read",
            "agent:protocols:read",
        }
    )

    responses = [
        client.get("/agent/health", headers=_auth_headers()).text,
        client.get("/agent/version", headers=_auth_headers()).text,
        client.get("/agent/runtime", headers=_auth_headers()).text,
        client.get("/agent/protocols", headers=_auth_headers()).text,
    ]
    rendered = "\n".join(responses).lower()

    for marker in (
        "privatekey",
        "private_key",
        "preshared",
        "vpn://",
        "token",
        RAW_TOKEN.lower(),
    ):
        assert marker not in rendered
    assert len(audit.events) == 4
```

- [ ] **Step 2: Run API tests and confirm expected failure**

Run:

```powershell
python -m pytest tests/agent/test_api.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.agent.api'`.

- [ ] **Step 3: Add audit model**

Create `app/agent/audit.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AgentAuditEvent:
    method: str
    path: str
    scope: str
    risk_class: str
    token_id: str
    owner: str
    result: str


class AgentAuditSink(Protocol):
    def record(self, event: AgentAuditEvent) -> None:
        pass


class InMemoryAgentAuditSink:
    def __init__(self) -> None:
        self.events: list[AgentAuditEvent] = []

    def record(self, event: AgentAuditEvent) -> None:
        self.events.append(event)
```

- [ ] **Step 4: Add protected API app factory**

Create `app/agent/api.py`:

```python
from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

from app.agent.audit import AgentAuditEvent, AgentAuditSink, InMemoryAgentAuditSink
from app.agent.auth import AgentAuthError, AgentToken, authenticate_agent_token
from app.agent.policy import AgentRoutePolicy, get_policy
from app.agent.runtime import LocalRuntimeAdapter, ProtocolSnapshot, RuntimeSnapshot


def create_agent_app(
    *,
    adapter: LocalRuntimeAdapter,
    tokens: Sequence[AgentToken],
    audit_sink: AgentAuditSink | None = None,
    build_version: str = "dev",
) -> FastAPI:
    app = FastAPI(
        title="Local Amnezia Agent",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    sink = audit_sink or InMemoryAgentAuditSink()

    def require_policy(policy: AgentRoutePolicy):
        def dependency(
            authorization: Annotated[str | None, Header(alias="Authorization")] = None,
        ) -> AgentToken:
            raw_token = _bearer_token(authorization)
            try:
                return authenticate_agent_token(
                    raw_token,
                    tokens=tokens,
                    required_scope=policy.scope,
                )
            except AgentAuthError as exc:
                status_code = 403 if "scope" in str(exc).lower() else 401
                raise HTTPException(status_code=status_code, detail=str(exc)) from exc

        return dependency

    health_policy = get_policy("GET", "/agent/health")
    version_policy = get_policy("GET", "/agent/version")
    runtime_policy = get_policy("GET", "/agent/runtime")
    protocols_policy = get_policy("GET", "/agent/protocols")

    @app.get("/agent/health")
    def health(token: AgentToken = Depends(require_policy(health_policy))):
        _record(sink, health_policy, token, result="allowed")
        return {
            "status": "ok",
            "service": "local-amnezia-agent",
        }

    @app.get("/agent/version")
    def version(token: AgentToken = Depends(require_policy(version_policy))):
        _record(sink, version_policy, token, result="allowed")
        return {
            "api": "local-amnezia-agent",
            "version": build_version,
            "write_enabled": False,
        }

    @app.get("/agent/runtime")
    def runtime(token: AgentToken = Depends(require_policy(runtime_policy))):
        snapshot = adapter.snapshot()
        _record(sink, runtime_policy, token, result="allowed")
        return _runtime_response(snapshot)

    @app.get("/agent/protocols")
    def protocols(token: AgentToken = Depends(require_policy(protocols_policy))):
        snapshot = adapter.snapshot()
        _record(sink, protocols_policy, token, result="allowed")
        return {
            "protocols": [
                _protocol_response(protocol)
                for protocol in snapshot.protocols
            ]
        }

    return app


def _bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing agent token")
    prefix = "bearer "
    if not authorization.lower().startswith(prefix):
        raise HTTPException(status_code=401, detail="Missing agent token")
    raw_token = authorization[len(prefix):].strip()
    if not raw_token:
        raise HTTPException(status_code=401, detail="Missing agent token")
    return raw_token


def _record(
    sink: AgentAuditSink,
    policy: AgentRoutePolicy,
    token: AgentToken,
    *,
    result: str,
) -> None:
    sink.record(
        AgentAuditEvent(
            method=policy.method,
            path=policy.path,
            scope=policy.scope,
            risk_class=policy.risk_class,
            token_id=token.token_id,
            owner=token.owner,
            result=result,
        )
    )


def _runtime_response(snapshot: RuntimeSnapshot) -> dict[str, str]:
    return {
        "server_name": snapshot.server_name,
        "runtime_type": snapshot.runtime_type,
        "status": snapshot.status,
    }


def _protocol_response(protocol: ProtocolSnapshot) -> dict[str, object]:
    return {
        "name": protocol.name,
        "status": protocol.status,
        "runtime_type": protocol.runtime_type,
        "capabilities": list(protocol.capabilities),
        "container_name": protocol.container_name,
        "interface": protocol.interface,
        "client_count": protocol.client_count,
    }
```

- [ ] **Step 5: Run API tests**

Run:

```powershell
python -m pytest tests/agent/test_api.py -v
```

Expected: PASS.

- [ ] **Step 6: Run complete agent test group**

Run:

```powershell
python -m pytest tests/agent -v
```

Expected: PASS.

- [ ] **Step 7: Commit API slice**

Run:

```powershell
git add app/agent/audit.py app/agent/api.py tests/agent/test_api.py
git commit -m "Add protected local agent read API"
```

---

### Task 5: Documentation And Regression Verification

**Files:**
- Create: `docs/LOCAL_AGENT.ru.md`

- [ ] **Step 1: Add Russian operator documentation**

Create `docs/LOCAL_AGENT.ru.md`:

```markdown
# Local Amnezia Agent

## Статус

Первый slice agent является read-only foundation. Он нужен, чтобы controller мог безопасно спросить сервер о состоянии runtime и поддерживаемых protocols без выдачи клиентских конфигов, QR, `vpn://`, private keys, PSK, backup payloads или выполнения write operations.

## Что включено

- `GET /agent/health`
- `GET /agent/version`
- `GET /agent/runtime`
- `GET /agent/protocols`
- hash-only bearer token auth
- explicit scopes
- route policy matrix
- fake runtime adapter for tests
- audit events for allowed read routes
- disabled public docs/openapi in the agent app

## Что не включено

- создание клиентов
- отключение или удаление клиентов
- выдача конфигов
- QR и `vpn://`
- backup/import
- reboot/reset
- Docker mutation
- public HTTP exposure

## Scopes

| Scope | Доступ |
| --- | --- |
| `agent:health` | `/agent/health`, `/agent/version` |
| `agent:read` | `/agent/runtime` |
| `agent:protocols:read` | `/agent/protocols` |

## Production правило

Agent считается привилегированным local runtime adapter. Его нельзя публиковать как общий root API к серверу. Любое расширение за пределы read-only routes требует route policy, secret inventory, audit plan и отдельного implementation plan.
```

- [ ] **Step 2: Run focused agent tests**

Run:

```powershell
python -m pytest tests/agent -v
```

Expected: PASS.

- [ ] **Step 3: Run related existing regression tests**

Run:

```powershell
python -m pytest tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_servers.py -v
```

Expected: PASS.

- [ ] **Step 4: Run formatting hygiene check**

Run:

```powershell
git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 5: Commit docs and verification marker**

Run:

```powershell
git add docs/LOCAL_AGENT.ru.md
git commit -m "Document local agent first slice"
```

---

## Final Verification

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
python -m pytest tests/agent tests/server/test_operation_runner.py tests/server/test_checks.py tests/web/test_servers.py -v
git diff --check
git status --short --branch
```

Expected:

- all selected tests PASS;
- `git diff --check` has no whitespace errors;
- branch contains only intentional Local Agent commits.

## Self-Review

Spec coverage:

- Read-only endpoints are covered by Task 4.
- Route policy is covered by Task 1.
- Scoped hash-only tokens are covered by Task 2.
- Fake runtime adapter is covered by Task 3.
- Audit for read routes is covered by Task 4.
- No config/write/backup/reboot behavior is enforced by Task 4 tests.
- Documentation is covered by Task 5.

Security posture:

- No endpoint returns config, QR, `vpn://`, private key, PSK or token body.
- Agent docs/openapi are disabled for the app factory.
- Missing, invalid, expired, revoked and insufficient tokens are rejected.
- Write and secret routes have policy records but are not exposed in the first slice.

Execution note:

- Use `superpowers:subagent-driven-development` for task-by-task execution when possible.
- Use `superpowers:executing-plans` for inline execution if one continuous session is preferred.
