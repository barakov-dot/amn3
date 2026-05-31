from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class AgentHttpResponse:
    status_code: int
    payload: dict[str, Any]


class AgentTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> AgentHttpResponse:
        pass


@dataclass(frozen=True)
class AgentHealth:
    status: str
    service: str


@dataclass(frozen=True)
class AgentRuntime:
    server_name: str
    runtime_type: str
    status: str


@dataclass(frozen=True)
class AgentProtocol:
    name: str
    status: str
    runtime_type: str
    capabilities: tuple[str, ...]
    container_name: str | None
    interface: str | None
    client_count: int | None


class AgentClientError(RuntimeError):
    pass


class UrlLibAgentTransport:
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> AgentHttpResponse:
        request = Request(url=url, headers=headers, method=method)
        try:
            with urlopen(request, timeout=timeout) as response:
                return AgentHttpResponse(
                    status_code=response.status,
                    payload=_decode_json(response.read()),
                )
        except HTTPError as exc:
            return AgentHttpResponse(
                status_code=exc.code,
                payload=_decode_json(exc.read()),
            )
        except URLError as exc:
            raise AgentClientError(f"Local Agent request failed: {exc.reason}") from exc


class LocalAgentClient:
    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str,
        transport: AgentTransport | None = None,
        timeout: float = 5.0,
    ) -> None:
        normalized_base_url = base_url.strip().rstrip("/")
        normalized_token = bearer_token.strip()
        if not normalized_base_url:
            raise ValueError("base_url cannot be blank")
        if not normalized_token:
            raise ValueError("bearer_token cannot be blank")

        self._base_url = normalized_base_url
        self._bearer_token = normalized_token
        self._transport = transport or UrlLibAgentTransport()
        self._timeout = timeout

    def __repr__(self) -> str:
        return f"LocalAgentClient(base_url={self._base_url!r}, bearer_token=[REDACTED])"

    def health(self) -> AgentHealth:
        payload = self._get("/agent/health")
        return AgentHealth(
            status=_require_str(payload, "status"),
            service=_require_str(payload, "service"),
        )

    def runtime(self) -> AgentRuntime:
        payload = self._get("/agent/runtime")
        return AgentRuntime(
            server_name=_require_str(payload, "server_name"),
            runtime_type=_require_str(payload, "runtime_type"),
            status=_require_str(payload, "status"),
        )

    def protocols(self) -> tuple[AgentProtocol, ...]:
        payload = self._get("/agent/protocols")
        protocols = payload.get("protocols")
        if not isinstance(protocols, list):
            raise AgentClientError("Local Agent response is missing protocols list")

        return tuple(_parse_protocol(protocol) for protocol in protocols)

    def _get(self, path: str) -> dict[str, Any]:
        response = self._transport.request(
            "GET",
            f"{self._base_url}{path}",
            headers={
                "Authorization": f"Bearer {self._bearer_token}",
                "Accept": "application/json",
            },
            timeout=self._timeout,
        )
        if response.status_code < 200 or response.status_code >= 300:
            detail = response.payload.get("detail", "request failed")
            raise AgentClientError(
                f"Local Agent GET {path} failed with HTTP {response.status_code}: {detail}"
            )
        return response.payload


def _parse_protocol(payload: object) -> AgentProtocol:
    if not isinstance(payload, dict):
        raise AgentClientError("Local Agent protocol entry is not an object")

    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(value, str) for value in capabilities
    ):
        raise AgentClientError("Local Agent protocol entry has invalid capabilities")

    client_count = payload.get("client_count")
    if client_count is not None and not isinstance(client_count, int):
        raise AgentClientError("Local Agent protocol entry has invalid client_count")

    return AgentProtocol(
        name=_require_str(payload, "name"),
        status=_require_str(payload, "status"),
        runtime_type=_require_str(payload, "runtime_type"),
        capabilities=tuple(capabilities),
        container_name=_optional_str(payload, "container_name"),
        interface=_optional_str(payload, "interface"),
        client_count=client_count,
    )


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AgentClientError(f"Local Agent response is missing string field: {key}")
    return value


def _optional_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise AgentClientError(f"Local Agent response field must be string or null: {key}")
    return value


def _decode_json(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AgentClientError("Local Agent returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise AgentClientError("Local Agent JSON response must be an object")
    return payload
