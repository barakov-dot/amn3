from __future__ import annotations

from collections.abc import Sequence
from fastapi import Depends, FastAPI, Header, HTTPException, status

from app.agent.audit import AgentAuditEvent, AgentAuditSink
from app.agent.auth import AgentAuthError, AgentToken, authenticate_agent_token
from app.agent.policy import AgentRoutePolicy, get_policy
from app.agent.runtime import LocalRuntimeAdapter


def create_agent_app(
    *,
    adapter: LocalRuntimeAdapter,
    tokens: Sequence[AgentToken],
    audit_sink: AgentAuditSink | None = None,
    build_version: str = "dev",
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    def require_policy(policy: AgentRoutePolicy):
        def dependency(
            authorization: str | None = Header(default=None),
        ) -> AgentToken:
            raw_token = _extract_bearer_token(authorization)
            try:
                return authenticate_agent_token(
                    raw_token,
                    tokens=tokens,
                    required_scope=policy.scope,
                )
            except AgentAuthError as exc:
                status_code = (
                    status.HTTP_403_FORBIDDEN
                    if "scope" in str(exc).lower()
                    else status.HTTP_401_UNAUTHORIZED
                )
                raise HTTPException(status_code=status_code, detail=str(exc)) from exc

        return dependency

    def audit_allowed(policy: AgentRoutePolicy, token: AgentToken) -> None:
        if audit_sink is None:
            return
        audit_sink.record(
            AgentAuditEvent(
                method=policy.method,
                path=policy.path,
                scope=policy.scope,
                risk_class=policy.risk_class,
                token_id=token.token_id,
                owner=token.owner,
                result="allowed",
            )
        )

    health_policy = get_policy("GET", "/agent/health")
    version_policy = get_policy("GET", "/agent/version")
    runtime_policy = get_policy("GET", "/agent/runtime")
    protocols_policy = get_policy("GET", "/agent/protocols")

    @app.get("/agent/health")
    def health(
        token: AgentToken = Depends(require_policy(health_policy)),
    ) -> dict[str, str]:
        audit_allowed(health_policy, token)
        return {"status": "ok", "service": "local-amnezia-agent"}

    @app.get("/agent/version")
    def version(
        token: AgentToken = Depends(require_policy(version_policy)),
    ) -> dict[str, str | bool]:
        audit_allowed(version_policy, token)
        return {
            "api": "local-amnezia-agent",
            "version": build_version,
            "write_enabled": False,
        }

    @app.get("/agent/runtime")
    def runtime(
        token: AgentToken = Depends(require_policy(runtime_policy)),
    ) -> dict[str, str]:
        audit_allowed(runtime_policy, token)
        snapshot = adapter.snapshot()
        return {
            "server_name": snapshot.server_name,
            "runtime_type": snapshot.runtime_type,
            "status": snapshot.status,
        }

    @app.get("/agent/protocols")
    def protocols(
        token: AgentToken = Depends(require_policy(protocols_policy)),
    ) -> dict[str, list[dict[str, object]]]:
        audit_allowed(protocols_policy, token)
        snapshot = adapter.snapshot()
        return {
            "protocols": [
                {
                    "name": protocol.name,
                    "status": protocol.status,
                    "runtime_type": protocol.runtime_type,
                    "capabilities": list(protocol.capabilities),
                    "container_name": protocol.container_name,
                    "interface": protocol.interface,
                    "client_count": protocol.client_count,
                }
                for protocol in snapshot.protocols
            ]
        }

    return app


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing agent token",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing agent token",
        )

    return token.strip()
