from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema


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


@dataclass(frozen=True)
class RepositoryAgentAuditSink:
    database_path: str | Path
    admin_telegram_id: int = 0

    def record(self, event: AgentAuditEvent) -> None:
        conn = connect(self.database_path)
        try:
            initialize_schema(conn)
            repo = Repository(conn)
            repo.record_admin_action(
                admin_telegram_id=self.admin_telegram_id,
                action="local_agent_read",
                metadata={
                    "source": "local_agent",
                    "method": event.method,
                    "path": event.path,
                    "scope": event.scope,
                    "risk_class": event.risk_class,
                    "token_id": event.token_id,
                    "token_owner": event.owner,
                    "result": event.result,
                },
            )
        finally:
            conn.close()
