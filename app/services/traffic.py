from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from app.db.repositories import Repository


@dataclass(frozen=True)
class PeerTraffic:
    peer_public_key: str
    rx_bytes: int
    tx_bytes: int
    collected_at: str
    source: str


@dataclass(frozen=True)
class TrafficCollectionReport:
    stored_count: int
    unknown_peers: tuple[str, ...]


@dataclass(frozen=True)
class DeviceTrafficView:
    device_id: int
    device_name: str
    config_version: str
    status: str
    expires_at: str | None
    rx: str
    tx: str
    total: str
    collected_at: str | None
    is_available: bool
    is_stale: bool
    first_connected_at: str | None = None
    last_connected_at: str | None = None
    is_connected: bool = False


class TrafficCollector(Protocol):
    def collect(self, server_id: int) -> list[PeerTraffic]:
        pass


class TrafficService:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    def collect_and_store(
        self,
        server_id: int,
        collector: TrafficCollector,
    ) -> TrafficCollectionReport:
        stored_count = 0
        unknown_peers: list[str] = []
        for peer in collector.collect(server_id):
            device = self._repo.get_device_by_server_peer_public_key(
                server_id,
                peer.peer_public_key,
            )
            if device is None:
                unknown_peers.append(peer.peer_public_key)
                continue
            self._repo.record_device_traffic_snapshot(
                device_id=int(device["id"]),
                server_id=server_id,
                peer_public_key=peer.peer_public_key,
                rx_bytes=peer.rx_bytes,
                tx_bytes=peer.tx_bytes,
                source=peer.source,
                collected_at=peer.collected_at,
            )
            if peer.rx_bytes > 0 or peer.tx_bytes > 0:
                self._repo.mark_device_connected(
                    int(device["id"]),
                    connected_at=peer.collected_at,
                )
            stored_count += 1
        return TrafficCollectionReport(
            stored_count=stored_count,
            unknown_peers=tuple(unknown_peers),
        )


def format_bytes(value: int) -> str:
    if value < 0:
        raise ValueError("Byte value must be non-negative")
    if value == 0:
        return "0 B"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    amount = float(value)
    unit_index = 0
    while amount >= 1024 and unit_index < len(units) - 1:
        amount /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(amount)} B"
    return f"{amount:.1f} {units[unit_index]}"


def build_device_traffic_view(
    device,
    latest_snapshot,
    *,
    now: str | None = None,
    stale_after_minutes: int = 60,
) -> DeviceTrafficView:
    if latest_snapshot is None:
        return DeviceTrafficView(
            device_id=int(device["id"]),
            device_name=str(device["name"]),
            config_version=str(device["config_version"]),
            status=str(device["status"]),
            expires_at=device["expires_at"],
            rx="unavailable",
            tx="unavailable",
            total="unavailable",
            collected_at=None,
            is_available=False,
            is_stale=True,
            first_connected_at=_row_get(device, "first_connected_at"),
            last_connected_at=_row_get(device, "last_connected_at"),
            is_connected=_row_get(device, "first_connected_at") is not None,
        )

    rx_bytes = int(latest_snapshot["rx_bytes"])
    tx_bytes = int(latest_snapshot["tx_bytes"])
    collected_at = str(latest_snapshot["collected_at"])
    return DeviceTrafficView(
        device_id=int(device["id"]),
        device_name=str(device["name"]),
        config_version=str(device["config_version"]),
        status=str(device["status"]),
        expires_at=device["expires_at"],
        rx=format_bytes(rx_bytes),
        tx=format_bytes(tx_bytes),
        total=format_bytes(rx_bytes + tx_bytes),
        collected_at=collected_at,
        is_available=True,
        is_stale=_is_stale(
            collected_at=collected_at,
            now=now,
            stale_after_minutes=stale_after_minutes,
        ),
        first_connected_at=_row_get(device, "first_connected_at"),
        last_connected_at=_row_get(device, "last_connected_at"),
        is_connected=_row_get(device, "first_connected_at") is not None,
    )


def _is_stale(*, collected_at: str, now: str | None, stale_after_minutes: int) -> bool:
    if now is None:
        return False
    collected_dt = _parse_utc_datetime(collected_at)
    now_dt = _parse_utc_datetime(now)
    return (now_dt - collected_dt).total_seconds() > stale_after_minutes * 60


def _parse_utc_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _row_get(row, key: str):
    if isinstance(row, dict):
        return row.get(key)
    try:
        return row[key]
    except (KeyError, IndexError):
        return None
