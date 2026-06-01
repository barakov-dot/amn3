# Local Agent Controller Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the controller-side client for guarded Local Agent write flow after VPS `GO-1`.

**Architecture:** Extend the existing read-only `LocalAgentClient` without weakening the read-only path. The controller uses `LOCAL_AGENT_CONTROLLER_TOKEN_PATH` for read-only status probes and a separate `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH` for the dedicated write token set. Web admin and CLI call typed client methods for `dry-run -> confirmation -> apply/revoke -> audit -> rollback`; neither layer logs Authorization headers, raw token values, PSK, private key, QR, `vpn://`, or full client config.

**Tech Stack:** Python 3.12, urllib transport already used by `app/agent/client.py`, existing `app.agent.write_contracts`, existing `app.web.server_health`, pytest.

---

## Scope And Gates

Execute this plan only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Before that:

- `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH` may be documented but not required in public examples;
- web admin continues to use only read-only Local Agent probe;
- `LocalAgentClient` does not expose write methods in production code;
- no controller path sends write requests to `/agent/clients*`.

After `GO-1`:

```text
LOCAL_AGENT_CONTROLLER_BASE_URL=http://127.0.0.1:3031
LOCAL_AGENT_CONTROLLER_TOKEN_PATH=/opt/amn2/secrets/local-agent.token
LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH=/opt/amn2/secrets/local-agent-write.token
```

Token boundary:

- read-only token: status/probe only;
- write token: `POST /agent/clients/dry-run`, `POST /agent/clients`, `DELETE /agent/clients/{id}`;
- dedicated write token set;
- do not log Authorization;
- do not log bearer token values;
- do not copy raw token values into exceptions, audit, templates, screenshots, issue comments, bot messages, or CLI output.

## File Structure

- Modify `app/agent/client.py`: add JSON body support to `AgentTransport`, `AgentHttpResponse`, `UrlLibAgentTransport`, and `LocalAgentClient`.
- Modify `tests/agent/test_client.py`: test read methods still use the read-only bearer token, write methods use write token, JSON body is correct, and errors redact secrets.
- Create `app/web/local_agent_actions.py`: controller-side helpers that read `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`, build a write client, and expose safe preflight/apply/revoke wrappers.
- Modify `app/web/server_health.py`: keep `probe_local_agent_controller` read-only and reference the separate write helper only through explicit write action code.
- Modify `tests/web/test_server_health.py`: prove read-only probe still uses `LOCAL_AGENT_CONTROLLER_TOKEN_PATH` and write helper uses `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`.
- Modify `app/cli.py`: add optional post-`GO-1` CLI commands that call the same client methods without printing raw token or delivery secrets.
- Keep `app/agent/api.py`: endpoint route behavior belongs to `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`.

## Client Contract

Methods added to `LocalAgentClient`:

```text
peer_apply_dry_run(request, *, actor_surface, actor_id, server_alias)
apply_peer(request, *, preflight, confirmation)
revoke_peer(request, *, preflight, confirmation)
```

The request models come from `app/agent/write_contracts.py`:

- `AgentPeerApplyRequest`;
- `AgentPeerRevokeRequest`;
- `AgentPeerMutationResult`.

Preflight and confirmation models come from `app/agent/write_confirmation.py`:

- `WritePreflightReference`;
- `WriteConfirmationChallenge`.

Expected server endpoints:

```text
POST /agent/clients/dry-run
POST /agent/clients
DELETE /agent/clients/{id}
```

Public error codes that the client must preserve:

- `missing_scope`;
- `preflight_required`;
- `runtime_degraded`;
- `mutation_failed`.

Sensitive values that must never appear in client repr, exceptions, logs, web pages, CLI output, or bot text:

- raw token;
- bearer token;
- Authorization header value;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config.

## Task 1: Transport JSON Bodies

**Files:**
- Modify: `tests/agent/test_client.py`
- Modify: `app/agent/client.py`

- [ ] **Step 1: Write the failing transport/body test**

Replace `FakeAgentTransport.request()` in `tests/agent/test_client.py` with a signature that captures body:

```python
class FakeAgentTransport:
    def __init__(self, responses: dict[str, AgentHttpResponse]):
        self._responses = responses
        self.calls: list[tuple[str, str, dict[str, str], float, bytes | None]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
        body: bytes | None = None,
    ) -> AgentHttpResponse:
        self.calls.append((method, url, headers, timeout, body))
        return self._responses[url]
```

Update the existing read-only assertions:

```python
    assert [call[0] for call in transport.calls] == ["GET", "GET", "GET"]
    assert [call[1] for call in transport.calls] == [
        "http://127.0.0.1:3031/agent/health",
        "http://127.0.0.1:3031/agent/runtime",
        "http://127.0.0.1:3031/agent/protocols",
    ]
    assert all(
        call[2] == {"Authorization": f"Bearer {RAW_TOKEN}", "Accept": "application/json"}
        for call in transport.calls
    )
    assert all(call[3] == 2.5 for call in transport.calls)
    assert all(call[4] is None for call in transport.calls)
```

Add this new test:

```python
def test_local_agent_client_transport_accepts_json_body_without_logging_token():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/clients/dry-run": AgentHttpResponse(
                status_code=200,
                payload={
                    "operation_id": "local_agent.clients.apply.dry_run",
                    "status": "planned",
                    "dry_run": True,
                    "risk_class": "state-write",
                    "consistency_status": "dry-run",
                    "message": "No changes will be made.",
                    "planned_commands": ["awg set awg0 peer peer-public allowed-ips 10.8.0.2/32"],
                    "preflight": {
                        "preflight_id": "preflight-1",
                        "operation_id": "local_agent.clients.apply",
                        "actor_surface": "web_admin",
                        "actor_id": "admin-1",
                        "server_alias": "demo-vps",
                        "client_id": "client-1",
                        "peer_public_key_fingerprint": "sha256:peerfingerprint",
                        "request_hash": "sha256:request",
                        "issued_at_epoch": 100,
                        "expires_at_epoch": 400,
                        "result_state": "passed",
                        "message": "No changes will be made.",
                    },
                },
            )
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    payload = client._post_json(
        "/agent/clients/dry-run",
        {
            "client_id": "client-1",
            "peer_public_key": "peer-public",
            "preshared_key": "secret-psk",
            "vpn_ip": "10.8.0.2",
            "protocol": "amneziawg",
        },
    )

    assert payload["operation_id"] == "local_agent.clients.apply.dry_run"
    method, url, headers, _timeout, body = transport.calls[0]
    assert method == "POST"
    assert url == "http://127.0.0.1:3031/agent/clients/dry-run"
    assert headers["Authorization"] == f"Bearer {RAW_TOKEN}"
    assert headers["Content-Type"] == "application/json"
    assert body is not None
    assert b"secret-psk" in body
    assert RAW_TOKEN.encode("utf-8") not in body
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py::test_local_agent_client_transport_accepts_json_body_without_logging_token -v
```

Expected: fail because `_post_json` and the transport `body` argument are not implemented.

- [ ] **Step 3: Add optional body to the transport protocol**

In `app/agent/client.py`, update `AgentTransport`:

```python
class AgentTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
        body: bytes | None = None,
    ) -> AgentHttpResponse:
        pass
```

Update `UrlLibAgentTransport.request()`:

```python
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
        body: bytes | None = None,
    ) -> AgentHttpResponse:
        request = Request(url=url, data=body, headers=headers, method=method)
```

- [ ] **Step 4: Add JSON helpers**

Add imports:

```python
from app.security.redaction import redact
```

Add these methods to `LocalAgentClient`:

```python
    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json_request("POST", path, payload)

    def _delete_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json_request("DELETE", path, payload)

    def _json_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        response = self._transport.request(
            method,
            f"{self._base_url}{path}",
            headers={
                "Authorization": f"Bearer {self._bearer_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
            body=body,
        )
        if response.status_code < 200 or response.status_code >= 300:
            detail = response.payload.get("detail", "request failed")
            raise AgentClientError(
                redact(
                    f"Local Agent {method} {path} failed with HTTP "
                    f"{response.status_code}: {detail}"
                ).replace(self._bearer_token, "[REDACTED]")
            )
        return response.payload
```

Keep `_get()` unchanged except passing `body=None` is optional because the protocol default covers it.

- [ ] **Step 5: Run client tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py -v
```

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add app/agent/client.py tests/agent/test_client.py
git commit -m "Add Local Agent client JSON transport"
```

## Task 2: Write Client Methods

**Files:**
- Modify: `tests/agent/test_client.py`
- Modify: `app/agent/client.py`

- [ ] **Step 1: Write the failing write method tests**

Add imports:

```python
from app.agent.write_confirmation import WriteConfirmationChallenge, WritePreflightReference
from app.agent.write_contracts import AgentPeerApplyRequest, AgentPeerRevokeRequest
```

Add this test:

```python
def test_local_agent_client_sends_peer_apply_dry_run_without_secret_leakage():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/clients/dry-run": AgentHttpResponse(
                status_code=200,
                payload=_dry_run_response(),
            )
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    result = client.peer_apply_dry_run(
        AgentPeerApplyRequest(
            client_id="client-1",
            peer_public_key="peer-public",
            preshared_key="secret-psk",
            vpn_ip="10.8.0.2",
            protocol="amneziawg",
        ),
        actor_surface="web_admin",
        actor_id="admin-1",
        server_alias="demo-vps",
    )

    assert result.operation_id == "local_agent.clients.apply.dry_run"
    assert result.preflight.preflight_id == "preflight-1"
    method, url, headers, _timeout, body = transport.calls[0]
    assert method == "POST"
    assert url.endswith("/agent/clients/dry-run")
    assert headers["Authorization"] == f"Bearer {RAW_TOKEN}"
    assert body is not None
    assert b"secret-psk" in body
    assert "secret-psk" not in repr(result)
    assert RAW_TOKEN not in repr(result)
```

Add apply/revoke tests:

```python
def test_local_agent_client_sends_peer_apply_request_with_bearer_token():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/clients": AgentHttpResponse(
                status_code=200,
                payload=_mutation_response("local_agent.clients.apply", "applied"),
            )
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    result = client.apply_peer(
        AgentPeerApplyRequest(
            client_id="client-1",
            peer_public_key="peer-public",
            preshared_key="secret-psk",
            vpn_ip="10.8.0.2",
        ),
        preflight=_preflight(),
        confirmation=_confirmation(),
    )

    assert result.operation_id == "local_agent.clients.apply"
    assert result.status == "applied"
    assert transport.calls[0][0] == "POST"
    assert transport.calls[0][2]["Authorization"] == f"Bearer {RAW_TOKEN}"
    assert RAW_TOKEN not in repr(result)


def test_local_agent_client_revokes_peer_with_delete_json():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/clients/client-1": AgentHttpResponse(
                status_code=200,
                payload=_mutation_response("local_agent.clients.revoke", "revoked"),
            )
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    result = client.revoke_peer(
        AgentPeerRevokeRequest(client_id="client-1", peer_public_key="peer-public"),
        preflight=_preflight(operation_id="local_agent.clients.revoke"),
        confirmation=_confirmation(operation_id="local_agent.clients.revoke"),
    )

    assert result.operation_id == "local_agent.clients.revoke"
    assert result.status == "revoked"
    assert transport.calls[0][0] == "DELETE"
    assert transport.calls[0][1].endswith("/agent/clients/client-1")
```

Add response helpers:

```python
def _dry_run_response() -> dict[str, object]:
    response = _mutation_response("local_agent.clients.apply.dry_run", "planned")
    response["dry_run"] = True
    response["consistency_status"] = "dry-run"
    response["preflight"] = _preflight_payload()
    return response


def _mutation_response(operation_id: str, status: str) -> dict[str, object]:
    return {
        "operation_id": operation_id,
        "status": status,
        "dry_run": False,
        "risk_class": "state-write",
        "consistency_status": "mutated",
        "message": "Peer mutation completed.",
        "planned_commands": ["awg set awg0 peer peer-public allowed-ips 10.8.0.2/32"],
        "rollback_reference": "rollback:apply:client-1",
        "peer_public_key_fingerprint": "sha256:peerfingerprint",
    }


def _preflight_payload(operation_id: str = "local_agent.clients.apply") -> dict[str, object]:
    return {
        "preflight_id": "preflight-1",
        "operation_id": operation_id,
        "actor_surface": "web_admin",
        "actor_id": "admin-1",
        "server_alias": "demo-vps",
        "client_id": "client-1",
        "peer_public_key_fingerprint": "sha256:peerfingerprint",
        "request_hash": "sha256:request",
        "issued_at_epoch": 100,
        "expires_at_epoch": 400,
        "result_state": "passed",
        "message": "No changes will be made.",
    }


def _preflight(operation_id: str = "local_agent.clients.apply") -> WritePreflightReference:
    return WritePreflightReference(
        preflight_id="preflight-1",
        operation_id=operation_id,
        actor_surface="web_admin",
        actor_id="admin-1",
        server_alias="demo-vps",
        client_id="client-1",
        peer_public_key="peer-public",
        request_hash="sha256:request",
        issued_at_epoch=100,
        expires_at_epoch=400,
        result_state="passed",
        message="No changes will be made.",
    )


def _confirmation(operation_id: str = "local_agent.clients.apply") -> WriteConfirmationChallenge:
    preflight = _preflight(operation_id)
    return WriteConfirmationChallenge(
        confirmation_id="confirmation-1",
        preflight=preflight,
        actor_surface="web_admin",
        actor_id="admin-1",
        confirmation_nonce="nonce-secret",
        issued_at_epoch=101,
        expires_at_epoch=300,
        message="Confirm mutation.",
    )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py::test_local_agent_client_sends_peer_apply_dry_run_without_secret_leakage tests/agent/test_client.py::test_local_agent_client_sends_peer_apply_request_with_bearer_token tests/agent/test_client.py::test_local_agent_client_revokes_peer_with_delete_json -v
```

Expected: fail because the methods and response dataclasses do not exist.

- [ ] **Step 3: Add write response dataclasses**

Add to `app/agent/client.py`:

```python
@dataclass(frozen=True, repr=False)
class AgentWritePreflight:
    preflight_id: str
    operation_id: str
    actor_surface: str
    actor_id: str
    server_alias: str
    client_id: str
    peer_public_key_fingerprint: str
    request_hash: str
    issued_at_epoch: int
    expires_at_epoch: int
    result_state: str
    message: str

    def __repr__(self) -> str:
        return (
            "AgentWritePreflight("
            f"preflight_id={self.preflight_id!r}, "
            f"operation_id={self.operation_id!r}, "
            f"client_id={self.client_id!r}, "
            f"peer_public_key_fingerprint={self.peer_public_key_fingerprint!r})"
        )


@dataclass(frozen=True, repr=False)
class AgentWriteResult:
    operation_id: str
    status: str
    dry_run: bool
    risk_class: str
    consistency_status: str
    message: str
    planned_commands: tuple[str, ...]
    preflight: AgentWritePreflight | None = None
    rollback_reference: str | None = None
    peer_public_key_fingerprint: str | None = None

    def __repr__(self) -> str:
        return (
            "AgentWriteResult("
            f"operation_id={self.operation_id!r}, "
            f"status={self.status!r}, "
            f"dry_run={self.dry_run!r}, "
            f"consistency_status={self.consistency_status!r})"
        )
```

- [ ] **Step 4: Add write methods**

Import request models:

```python
from app.agent.write_confirmation import WriteConfirmationChallenge, WritePreflightReference
from app.agent.write_contracts import AgentPeerApplyRequest, AgentPeerRevokeRequest
```

Add methods to `LocalAgentClient`:

```python
    def peer_apply_dry_run(
        self,
        request: AgentPeerApplyRequest,
        *,
        actor_surface: str,
        actor_id: str,
        server_alias: str,
    ) -> AgentWriteResult:
        payload = {
            **request.to_agent_payload(),
            "actor_surface": actor_surface,
            "actor_id": actor_id,
            "server_alias": server_alias,
        }
        return _parse_write_result(self._post_json("/agent/clients/dry-run", payload))

    def apply_peer(
        self,
        request: AgentPeerApplyRequest,
        *,
        preflight: WritePreflightReference,
        confirmation: WriteConfirmationChallenge,
    ) -> AgentWriteResult:
        payload = {
            **request.to_agent_payload(),
            "preflight": preflight.redacted_payload(),
            "confirmation": _confirmation_payload(confirmation),
        }
        return _parse_write_result(self._post_json("/agent/clients", payload))

    def revoke_peer(
        self,
        request: AgentPeerRevokeRequest,
        *,
        preflight: WritePreflightReference,
        confirmation: WriteConfirmationChallenge,
    ) -> AgentWriteResult:
        payload = {
            **request.to_agent_payload(),
            "preflight": preflight.redacted_payload(),
            "confirmation": _confirmation_payload(confirmation),
        }
        return _parse_write_result(
            self._delete_json(f"/agent/clients/{request.client_id}", payload)
        )
```

- [ ] **Step 5: Add parsers**

Add below `_parse_protocol`:

```python
def _parse_write_result(payload: dict[str, Any]) -> AgentWriteResult:
    commands = payload.get("planned_commands")
    if not isinstance(commands, list) or not all(isinstance(value, str) for value in commands):
        raise AgentClientError("Local Agent write response has invalid planned_commands")
    preflight_payload = payload.get("preflight")
    return AgentWriteResult(
        operation_id=_require_str(payload, "operation_id"),
        status=_require_str(payload, "status"),
        dry_run=_require_bool(payload, "dry_run"),
        risk_class=_require_str(payload, "risk_class"),
        consistency_status=_require_str(payload, "consistency_status"),
        message=_require_str(payload, "message"),
        planned_commands=tuple(commands),
        preflight=(
            _parse_write_preflight(preflight_payload)
            if isinstance(preflight_payload, dict)
            else None
        ),
        rollback_reference=_optional_str(payload, "rollback_reference"),
        peer_public_key_fingerprint=_optional_str(
            payload,
            "peer_public_key_fingerprint",
        ),
    )


def _parse_write_preflight(payload: dict[str, Any]) -> AgentWritePreflight:
    return AgentWritePreflight(
        preflight_id=_require_str(payload, "preflight_id"),
        operation_id=_require_str(payload, "operation_id"),
        actor_surface=_require_str(payload, "actor_surface"),
        actor_id=_require_str(payload, "actor_id"),
        server_alias=_require_str(payload, "server_alias"),
        client_id=_require_str(payload, "client_id"),
        peer_public_key_fingerprint=_require_str(
            payload,
            "peer_public_key_fingerprint",
        ),
        request_hash=_require_str(payload, "request_hash"),
        issued_at_epoch=_require_int(payload, "issued_at_epoch"),
        expires_at_epoch=_require_int(payload, "expires_at_epoch"),
        result_state=_require_str(payload, "result_state"),
        message=_require_str(payload, "message"),
    )


def _confirmation_payload(confirmation: WriteConfirmationChallenge) -> dict[str, Any]:
    return {
        "confirmation_id": confirmation.confirmation_id,
        "confirmation_nonce": confirmation.confirmation_nonce,
        "issued_at_epoch": confirmation.issued_at_epoch,
        "expires_at_epoch": confirmation.expires_at_epoch,
        "message": confirmation.message,
    }


def _require_bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise AgentClientError(f"Local Agent response is missing boolean field: {key}")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise AgentClientError(f"Local Agent response is missing integer field: {key}")
    return value
```

- [ ] **Step 6: Add error redaction test**

Add:

```python
def test_local_agent_client_redacts_token_from_write_errors():
    transport = FakeAgentTransport(
        {
            "http://127.0.0.1:3031/agent/clients": AgentHttpResponse(
                status_code=409,
                payload={
                    "detail": {
                        "code": "preflight_required",
                        "message": f"missing confirmation for {RAW_TOKEN}",
                    }
                },
            )
        }
    )
    client = LocalAgentClient(
        base_url="http://127.0.0.1:3031",
        bearer_token=RAW_TOKEN,
        transport=transport,
    )

    with pytest.raises(AgentClientError) as exc_info:
        client.apply_peer(
            AgentPeerApplyRequest(
                client_id="client-1",
                peer_public_key="peer-public",
                preshared_key="secret-psk",
                vpn_ip="10.8.0.2",
            ),
            preflight=_preflight(),
            confirmation=_confirmation(),
        )

    assert "preflight_required" in str(exc_info.value)
    assert RAW_TOKEN not in str(exc_info.value)
    assert "secret-psk" not in str(exc_info.value)
```

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py -v
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add app/agent/client.py tests/agent/test_client.py
git commit -m "Add Local Agent write client methods"
```

## Task 3: Controller Write Token Boundary

**Files:**
- Create: `app/web/local_agent_actions.py`
- Modify: `tests/web/test_server_health.py`
- Verify: `app/web/server_health.py`

- [ ] **Step 1: Write failing token boundary tests**

Add to `tests/web/test_server_health.py`:

```python
from app.web.local_agent_actions import build_local_agent_write_client


def test_build_local_agent_write_client_reads_dedicated_write_token_path(tmp_path):
    read_token_path = tmp_path / "local-agent.token"
    write_token_path = tmp_path / "local-agent-write.token"
    read_token_path.write_text("read-token", encoding="utf-8")
    write_token_path.write_text("write-token", encoding="utf-8")
    created = []

    class FakeWriteClient:
        def __init__(self, *, base_url, bearer_token):
            created.append((base_url, bearer_token))

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_token_path=str(read_token_path),
        local_agent_controller_write_token_path=str(write_token_path),
    )

    client = build_local_agent_write_client(settings, client_factory=FakeWriteClient)

    assert isinstance(client, FakeWriteClient)
    assert created == [("http://127.0.0.1:3031", "write-token")]


def test_build_local_agent_write_client_redacts_missing_write_token_path(tmp_path):
    missing_path = tmp_path / "missing-write-token"
    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_write_token_path=str(missing_path),
    )

    with pytest.raises(RuntimeError) as exc_info:
        build_local_agent_write_client(settings)

    message = str(exc_info.value)
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in message
    assert "write-token" not in message
    assert "raw token" not in message
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py::test_build_local_agent_write_client_reads_dedicated_write_token_path tests/web/test_server_health.py::test_build_local_agent_write_client_redacts_missing_write_token_path -v
```

Expected: fail because `app.web.local_agent_actions` does not exist and settings do not yet expose `local_agent_controller_write_token_path` until the settings plan is executed.

- [ ] **Step 3: Create write action helper**

Create `app/web/local_agent_actions.py`:

```python
from __future__ import annotations

from pathlib import Path

from app.agent.client import LocalAgentClient
from app.config.settings import Settings
from app.security.redaction import redact


class LocalAgentActionError(RuntimeError):
    pass


def build_local_agent_write_client(
    settings: Settings,
    *,
    client_factory=LocalAgentClient,
):
    token_path_value = getattr(settings, "local_agent_controller_write_token_path", "")
    token_path = Path(str(token_path_value))
    try:
        raw_token = token_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise LocalAgentActionError(
            redact(f"Could not read LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH: {exc}")
        ) from exc
    if not raw_token:
        raise LocalAgentActionError("LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH is empty")
    return client_factory(
        base_url=settings.local_agent_controller_base_url,
        bearer_token=raw_token,
    )
```

This helper reads only `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH`. It must not read `LOCAL_AGENT_CONTROLLER_TOKEN_PATH`.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py -v
```

Expected: pass after the write settings plan has added `local_agent_controller_write_token_path`.

- [ ] **Step 5: Commit**

```powershell
git add app/web/local_agent_actions.py tests/web/test_server_health.py
git commit -m "Add Local Agent write client factory"
```

## Task 4: Web And CLI Wrappers

**Files:**
- Modify: `app/web/local_agent_actions.py`
- Modify: `tests/web/test_server_health.py`
- Modify: `app/cli.py`
- Test: `tests/agent/test_cli.py`

- [ ] **Step 1: Write failing web wrapper test**

Add to `tests/web/test_server_health.py`:

```python
from app.web.local_agent_actions import run_local_agent_peer_apply_preflight


def test_run_local_agent_peer_apply_preflight_returns_redacted_plan(tmp_path):
    write_token_path = tmp_path / "local-agent-write.token"
    write_token_path.write_text("write-token", encoding="utf-8")
    calls = []

    class FakeWriteClient:
        def __init__(self, *, base_url, bearer_token):
            self.base_url = base_url
            self.bearer_token = bearer_token

        def peer_apply_dry_run(self, request, *, actor_surface, actor_id, server_alias):
            calls.append((request, actor_surface, actor_id, server_alias, self.bearer_token))
            return FakeWriteResult()

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_write_token_path=str(write_token_path),
    )

    result = run_local_agent_peer_apply_preflight(
        settings,
        client_id="client-1",
        peer_public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
        actor_surface="web_admin",
        actor_id="admin-1",
        server_alias="demo-vps",
        client_factory=FakeWriteClient,
    )

    assert result.operation_id == "local_agent.clients.apply.dry_run"
    assert calls[0][4] == "write-token"
    assert "secret-psk" not in repr(result)
    assert "write-token" not in repr(result)
```

Add fake result:

```python
class FakeWriteResult:
    operation_id = "local_agent.clients.apply.dry_run"
    status = "planned"
    dry_run = True
    planned_commands = ("awg set awg0 peer peer-public allowed-ips 10.8.0.2/32",)

    def __repr__(self):
        return "FakeWriteResult(operation_id='local_agent.clients.apply.dry_run')"
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py::test_run_local_agent_peer_apply_preflight_returns_redacted_plan -v
```

Expected: fail because `run_local_agent_peer_apply_preflight` does not exist.

- [ ] **Step 3: Add web wrapper**

In `app/web/local_agent_actions.py`, add:

```python
from app.agent.write_contracts import AgentPeerApplyRequest


def run_local_agent_peer_apply_preflight(
    settings: Settings,
    *,
    client_id: str,
    peer_public_key: str,
    preshared_key: str,
    vpn_ip: str,
    actor_surface: str,
    actor_id: str,
    server_alias: str,
    client_factory=LocalAgentClient,
):
    client = build_local_agent_write_client(settings, client_factory=client_factory)
    request = AgentPeerApplyRequest(
        client_id=client_id,
        peer_public_key=peer_public_key,
        preshared_key=preshared_key,
        vpn_ip=vpn_ip,
        protocol="amneziawg",
    )
    return client.peer_apply_dry_run(
        request,
        actor_surface=actor_surface,
        actor_id=actor_id,
        server_alias=server_alias,
    )
```

- [ ] **Step 4: Add CLI dry-run command test**

In `tests/agent/test_cli.py`, add a test after existing agent probe tests:

```python
def test_agent_write_dry_run_cli_uses_write_token_path_without_printing_token(tmp_path, capsys, monkeypatch):
    token_path = tmp_path / "local-agent-write.token"
    token_path.write_text("write-token", encoding="utf-8")
    calls = []

    class FakeClient:
        def __init__(self, *, base_url, bearer_token):
            calls.append(("init", base_url, bearer_token))

        def peer_apply_dry_run(self, request, *, actor_surface, actor_id, server_alias):
            calls.append(("dry-run", request.client_id, actor_surface, actor_id, server_alias))
            return FakeWriteResult()

    monkeypatch.setattr("app.cli.LocalAgentClient", FakeClient)

    exit_code = main(
        [
            "agent",
            "write-dry-run",
            "--base-url",
            "http://127.0.0.1:3031",
            "--write-token-path",
            str(token_path),
            "--client-id",
            "client-1",
            "--peer-public-key",
            "peer-public",
            "--preshared-key",
            "secret-psk",
            "--vpn-ip",
            "10.8.0.2",
            "--actor-id",
            "admin-1",
            "--server-alias",
            "demo-vps",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "local_agent.clients.apply.dry_run" in output
    assert "write-token" not in output
    assert "secret-psk" not in output
    assert calls[0] == ("init", "http://127.0.0.1:3031", "write-token")
```

- [ ] **Step 5: Add CLI parser and handler**

In `app/cli.py`, add `agent write-dry-run` under the existing `agent` parser. Required arguments:

```text
--base-url
--write-token-path
--client-id
--peer-public-key
--preshared-key
--vpn-ip
--actor-id
--server-alias
```

Handler behavior:

- read token from `--write-token-path`;
- instantiate `LocalAgentClient(base_url=args.base_url, bearer_token=raw_token)`;
- call `peer_apply_dry_run`;
- print only operation id, status, and redacted planned commands;
- never print raw token or PSK.

- [ ] **Step 6: Run wrapper tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/web/test_server_health.py tests/agent/test_cli.py -v
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add app/web/local_agent_actions.py tests/web/test_server_health.py app/cli.py tests/agent/test_cli.py
git commit -m "Add Local Agent write controller wrappers"
```

## Task 5: Final Verification

**Files:**
- Verify: `tests/agent/test_client.py`
- Verify: `tests/web/test_server_health.py`
- Verify: `tests/agent/test_cli.py`
- Verify: `tests/agent/test_write_contracts.py`
- Verify: `tests/agent/test_write_confirmation.py`
- Verify: `tests/security/test_redaction.py`
- Verify: `tests/test_file_hygiene.py`

- [ ] **Step 1: Run controller client suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_client.py tests/web/test_server_health.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py -v
```

Expected: pass. This is the core command string: `pytest tests/agent/test_client.py tests/web/test_server_health.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py`.

- [ ] **Step 2: Run CLI and redaction checks**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_cli.py tests/security/test_redaction.py tests/test_file_hygiene.py -v
```

Expected: pass.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit docs if this plan is executed with docs updates**

```powershell
git add docs/AMN3_NEXT_CHAT_HANDOFF.ru.md docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md docs/AMN3_WRITE_API_UX_FLOW.ru.md docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md
git commit -m "Document Local Agent controller write client"
```

Skip this docs commit if the same implementation branch already committed the documentation links.
