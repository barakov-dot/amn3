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
