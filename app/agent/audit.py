from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass
class InMemoryAgentAuditSink:
    events: list[AgentAuditEvent] = field(default_factory=list)

    def record(self, event: AgentAuditEvent) -> None:
        self.events.append(event)
