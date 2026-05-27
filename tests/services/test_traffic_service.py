from dataclasses import dataclass

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.traffic import PeerTraffic, TrafficService


@dataclass
class FakeCollector:
    peers: list[PeerTraffic]

    def collect(self, server_id: int) -> list[PeerTraffic]:
        return self.peers


def _repo_with_device(tmp_path):
    conn = connect(tmp_path / "traffic-service.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id = repo.upsert_user(
        telegram_id=3001,
        username="traffic_service_user",
        first_name="Traffic",
        last_name="Service",
    )
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="known-peer",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )
    return repo, server_id, device_id


def test_collect_and_store_traffic_records_known_peer(tmp_path):
    repo, server_id, device_id = _repo_with_device(tmp_path)
    service = TrafficService(repo)
    collector = FakeCollector(
        [
            PeerTraffic(
                peer_public_key="known-peer",
                rx_bytes=1024,
                tx_bytes=2048,
                collected_at="2026-05-27T12:00:00Z",
                source="fake",
            )
        ]
    )

    report = service.collect_and_store(server_id, collector)
    latest = repo.get_latest_device_traffic(device_id)

    assert report.stored_count == 1
    assert report.unknown_peers == ()
    assert latest is not None
    assert latest["rx_bytes"] == 1024
    assert latest["tx_bytes"] == 2048


def test_collect_and_store_traffic_reports_unknown_peer_without_snapshot(tmp_path):
    repo, server_id, device_id = _repo_with_device(tmp_path)
    service = TrafficService(repo)
    collector = FakeCollector(
        [
            PeerTraffic(
                peer_public_key="unknown-peer",
                rx_bytes=1024,
                tx_bytes=2048,
                collected_at="2026-05-27T12:00:00Z",
                source="fake",
            )
        ]
    )

    report = service.collect_and_store(server_id, collector)

    assert report.stored_count == 0
    assert report.unknown_peers == ("unknown-peer",)
    assert repo.get_latest_device_traffic(device_id) is None
