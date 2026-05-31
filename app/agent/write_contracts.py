from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress
from typing import Literal

from app.security.redaction import redact


class AgentWriteContractError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class AgentPeerApplyRequest:
    client_id: str
    peer_public_key: str
    preshared_key: str = field(repr=False)
    vpn_ip: str
    protocol: str = "amneziawg"

    def __post_init__(self) -> None:
        object.__setattr__(self, "client_id", _require_text(self.client_id, "client_id"))
        object.__setattr__(
            self,
            "peer_public_key",
            _require_text(self.peer_public_key, "peer_public_key"),
        )
        object.__setattr__(
            self,
            "preshared_key",
            _require_text(self.preshared_key, "preshared_key"),
        )
        object.__setattr__(self, "vpn_ip", _normalize_host_ip(self.vpn_ip))
        object.__setattr__(self, "protocol", _require_text(self.protocol, "protocol"))

    @property
    def allowed_ips(self) -> str:
        address = ipaddress.ip_address(self.vpn_ip)
        return f"{address}/{address.max_prefixlen}"

    def to_agent_payload(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "protocol": self.protocol,
            "peer_public_key": self.peer_public_key,
            "preshared_key": self.preshared_key,
            "allowed_ips": self.allowed_ips,
        }

    def redacted_payload(self) -> dict[str, str]:
        payload = self.to_agent_payload()
        payload["preshared_key"] = "[REDACTED]"
        return payload

    def __repr__(self) -> str:
        return (
            "AgentPeerApplyRequest("
            f"client_id={self.client_id!r}, "
            f"protocol={self.protocol!r}, "
            f"peer_public_key={self.peer_public_key!r}, "
            "preshared_key='[REDACTED]', "
            f"allowed_ips={self.allowed_ips!r})"
        )


@dataclass(frozen=True)
class AgentPeerRevokeRequest:
    client_id: str
    peer_public_key: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "client_id", _require_text(self.client_id, "client_id"))
        object.__setattr__(
            self,
            "peer_public_key",
            _require_text(self.peer_public_key, "peer_public_key"),
        )

    def to_agent_payload(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "peer_public_key": self.peer_public_key,
        }

    def redacted_payload(self) -> dict[str, str]:
        return self.to_agent_payload()


MutationStatus = Literal["planned", "applied", "revoked", "failed"]
ConsistencyStatus = Literal["dry-run", "mutated", "failed"]


@dataclass(frozen=True, repr=False)
class AgentPeerMutationResult:
    operation_id: str
    status: MutationStatus
    dry_run: bool
    message: str
    planned_commands: tuple[str, ...]
    secret_values: tuple[str, ...] = field(default_factory=tuple, repr=False)
    risk_class: str = "state-write"

    @property
    def consistency_status(self) -> ConsistencyStatus:
        if self.status == "failed":
            return "failed"
        if self.dry_run:
            return "dry-run"
        return "mutated"

    def redacted_payload(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "status": self.status,
            "dry_run": self.dry_run,
            "risk_class": self.risk_class,
            "consistency_status": self.consistency_status,
            "message": _redact_values(self.message, self.secret_values),
            "planned_commands": [
                _redact_values(command, self.secret_values)
                for command in self.planned_commands
            ],
        }

    def __repr__(self) -> str:
        return f"AgentPeerMutationResult({self.redacted_payload()!r})"


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise AgentWriteContractError(f"{field_name} cannot be blank")
    return normalized


def _normalize_host_ip(value: str) -> str:
    raw_value = _require_text(value, "vpn_ip")
    try:
        if "/" in raw_value:
            return str(ipaddress.ip_interface(raw_value).ip)
        return str(ipaddress.ip_address(raw_value))
    except ValueError as exc:
        raise AgentWriteContractError(f"vpn_ip is invalid: {raw_value}") from exc


def _redact_values(value: str, secrets: tuple[str, ...]) -> str:
    safe_value = value
    for secret in secrets:
        if secret:
            safe_value = safe_value.replace(secret, "[REDACTED]")
    return redact(safe_value)
