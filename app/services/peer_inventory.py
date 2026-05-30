from __future__ import annotations

from dataclasses import dataclass
import shlex
from typing import Protocol

from app.db.repositories import Repository
from app.server.ssh import SshClient


@dataclass(frozen=True)
class RemotePeer:
    peer_public_key: str
    allowed_ips: str
    latest_handshake: int
    rx_bytes: int
    tx_bytes: int


@dataclass(frozen=True)
class LocalPeer:
    device_id: int
    device_name: str
    peer_public_key: str
    vpn_ip: str


@dataclass(frozen=True)
class PeerInventoryReport:
    known_remote_peers: tuple[RemotePeer, ...]
    unknown_remote_peers: tuple[RemotePeer, ...]
    missing_local_peers: tuple[LocalPeer, ...]


class PeerInventoryCollector(Protocol):
    def collect(self, server_id: int) -> list[RemotePeer]:
        pass


class PeerInventoryError(RuntimeError):
    pass


class AwgDumpPeerInventoryCollector:
    def __init__(
        self,
        *,
        interface: str,
        ssh_client: SshClient,
        container_name: str | None = None,
    ) -> None:
        self._interface = interface
        self._ssh_client = ssh_client
        self._container_name = container_name

    def collect(self, server_id: int) -> list[RemotePeer]:
        command = _awg_dump_command(
            interface=self._interface,
            container_name=self._container_name,
        )
        result = self._ssh_client.run(command)
        if result.exit_code != 0:
            raise PeerInventoryError(
                "Peer inventory failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={_stream_status(result.stdout)} "
                f"stderr={_stream_status(result.stderr)}"
            )
        return parse_awg_peer_inventory_dump(result.stdout)


class PeerInventoryService:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    def compare(
        self,
        server_id: int,
        collector: PeerInventoryCollector,
    ) -> PeerInventoryReport:
        remote_peers = collector.collect(server_id)
        local_peers = {
            peer.peer_public_key: peer
            for peer in _local_peers(self._repo.list_active_devices_for_server(server_id))
        }
        remote_by_key = {peer.peer_public_key: peer for peer in remote_peers}
        known_remote = tuple(
            peer for peer in remote_peers if peer.peer_public_key in local_peers
        )
        unknown_remote = tuple(
            peer for peer in remote_peers if peer.peer_public_key not in local_peers
        )
        missing_local = tuple(
            peer
            for key, peer in local_peers.items()
            if key not in remote_by_key
        )
        return PeerInventoryReport(
            known_remote_peers=known_remote,
            unknown_remote_peers=unknown_remote,
            missing_local_peers=missing_local,
        )


def parse_awg_peer_inventory_dump(dump: str) -> list[RemotePeer]:
    peers: list[RemotePeer] = []
    for index, line in enumerate(dump.splitlines()):
        if not line.strip():
            continue
        parts = line.split("\t")
        if index == 0 and len(parts) >= 5 and not _looks_like_peer_row(parts):
            continue
        if len(parts) < 7:
            continue
        peers.append(
            RemotePeer(
                peer_public_key=parts[0],
                allowed_ips=parts[3],
                latest_handshake=_safe_int(parts[4]),
                rx_bytes=_safe_int(parts[5]),
                tx_bytes=_safe_int(parts[6]),
            )
        )
    return peers


def _local_peers(rows) -> list[LocalPeer]:
    return [
        LocalPeer(
            device_id=int(row["id"]),
            device_name=str(row["name"]),
            peer_public_key=str(row["peer_public_key"]),
            vpn_ip=str(row["vpn_ip"]),
        )
        for row in rows
    ]


def _awg_dump_command(*, interface: str, container_name: str | None) -> str:
    interface_arg = shlex.quote(interface)
    if container_name:
        return f"docker exec {shlex.quote(container_name)} awg show {interface_arg} dump"
    return f"awg show {interface_arg} dump"


def _looks_like_peer_row(parts: list[str]) -> bool:
    return len(parts) >= 8 and parts[4].isdigit() and parts[5].isdigit() and parts[6].isdigit()


def _safe_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def _stream_status(value: str) -> str:
    return "present" if value else "empty"
