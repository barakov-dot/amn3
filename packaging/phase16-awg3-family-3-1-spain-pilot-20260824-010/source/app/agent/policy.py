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
        if policy.method == normalized_method and policy.path == path and policy.first_slice:
            return policy
    raise AgentPolicyError(f"No agent route policy for {normalized_method} {path}")


def first_slice_policies() -> tuple[AgentRoutePolicy, ...]:
    return tuple(policy for policy in AGENT_ROUTE_POLICIES if policy.first_slice)
