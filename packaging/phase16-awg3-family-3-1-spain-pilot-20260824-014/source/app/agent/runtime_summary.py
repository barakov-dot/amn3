from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.agent.runtime import ProtocolStatus, RuntimeSnapshot, RuntimeStatus


ControllerDisplayStatus = Literal["safe", "unsafe"]


@dataclass(frozen=True)
class ProtocolRuntimeSummary:
    name: str
    status: ProtocolStatus
    runtime_type: str
    capabilities: tuple[str, ...]
    client_count: int | None


@dataclass(frozen=True)
class LocalAgentRuntimeSummary:
    agent_status: str
    agent_version: str | None
    runtime_contract_version: int | None
    write_enabled: bool | None
    controller_display_status: ControllerDisplayStatus
    runtime_type: str
    runtime_status: RuntimeStatus
    protocols: tuple[ProtocolRuntimeSummary, ...]


def build_runtime_summary(
    *,
    agent_status: str,
    agent_version: str | None,
    runtime_contract_version: int | None,
    write_enabled: bool | None,
    runtime: RuntimeSnapshot | None,
) -> LocalAgentRuntimeSummary:
    return LocalAgentRuntimeSummary(
        agent_status=agent_status,
        agent_version=agent_version,
        runtime_contract_version=runtime_contract_version,
        write_enabled=write_enabled,
        controller_display_status="safe" if write_enabled is False else "unsafe",
        runtime_type=runtime.runtime_type if runtime is not None else "unknown",
        runtime_status=runtime.status if runtime is not None else "unknown",
        protocols=_protocol_summaries(runtime),
    )


def _protocol_summaries(
    runtime: RuntimeSnapshot | None,
) -> tuple[ProtocolRuntimeSummary, ...]:
    if runtime is None:
        return ()

    return tuple(
        ProtocolRuntimeSummary(
            name=protocol.name,
            status=protocol.status,
            runtime_type=protocol.runtime_type,
            capabilities=tuple(protocol.capabilities),
            client_count=protocol.client_count,
        )
        for protocol in runtime.protocols
    )
