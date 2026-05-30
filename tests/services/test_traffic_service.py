from dataclasses import dataclass

from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.server.ssh import CommandResult
from app.services.traffic import (
    AwgDumpTrafficCollector,
    PeerTraffic,
    TrafficCollectionError,
    TrafficService,
    parse_awg_show_dump,
)


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
    device = repo.get_device(device_id)
    assert device["first_connected_at"] == "2026-05-27T12:00:00Z"
    assert device["last_connected_at"] == "2026-05-27T12:00:00Z"


def test_collect_and_store_traffic_does_not_mark_zero_byte_peer_connected(tmp_path):
    repo, server_id, device_id = _repo_with_device(tmp_path)
    service = TrafficService(repo)
    collector = FakeCollector(
        [
            PeerTraffic(
                peer_public_key="known-peer",
                rx_bytes=0,
                tx_bytes=0,
                collected_at="2026-05-27T12:00:00Z",
                source="fake",
            )
        ]
    )

    service.collect_and_store(server_id, collector)

    device = repo.get_device(device_id)
    assert device["first_connected_at"] is None
    assert device["last_connected_at"] is None


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


def test_parse_awg_show_dump_reads_peer_transfer_counters():
    dump = "\n".join(
        [
            "awg0\tserver-public\tserver-private\t51820\toff",
            "known-peer\tpsk\t203.0.113.20:50000\t10.8.0.2/32\t1700000000\t1024\t2048\t25",
            "idle-peer\t(none)\t(none)\t10.8.0.3/32\t0\t0\t0\toff",
        ]
    )

    peers = parse_awg_show_dump(
        dump,
        collected_at="2026-05-27T12:00:00Z",
        source="awg:debian-vps-1",
    )

    assert peers == [
        PeerTraffic(
            peer_public_key="known-peer",
            rx_bytes=1024,
            tx_bytes=2048,
            collected_at="2026-05-27T12:00:00Z",
            source="awg:debian-vps-1",
        ),
        PeerTraffic(
            peer_public_key="idle-peer",
            rx_bytes=0,
            tx_bytes=0,
            collected_at="2026-05-27T12:00:00Z",
            source="awg:debian-vps-1",
        ),
    ]


def test_awg_dump_traffic_collector_runs_read_only_dump_command(tmp_path):
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=0,
            stdout="\n".join(
                [
                    "awg0\tserver-public\tserver-private\t51820\toff",
                    "known-peer\tpsk\t203.0.113.20:50000\t10.8.0.2/32\t1700000000\t1024\t2048\t25",
                ]
            ),
            stderr="",
        )
    )
    collector = AwgDumpTrafficCollector(
        interface="awg0",
        source="awg:debian-vps-1",
        ssh_client=ssh,
        now=lambda: "2026-05-27T12:00:00Z",
    )

    peers = collector.collect(server_id=1)

    assert ssh.calls == [("awg show awg0 dump", None)]
    assert peers[0].peer_public_key == "known-peer"
    assert peers[0].rx_bytes == 1024
    assert peers[0].tx_bytes == 2048


def test_awg_dump_traffic_collector_runs_docker_dump_command():
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=0,
            stdout="\n".join(
                [
                    "awg0\tserver-public\tserver-private\t51820\toff",
                    "known-peer\tpsk\t203.0.113.20:50000\t10.8.0.2/32\t1700000000\t1024\t2048\t25",
                ]
            ),
            stderr="",
        )
    )
    collector = AwgDumpTrafficCollector(
        interface="awg0",
        source="awg:debian-vps-1",
        ssh_client=ssh,
        container_name="amnezia-awg",
        now=lambda: "2026-05-27T12:00:00Z",
    )

    peers = collector.collect(server_id=1)

    assert ssh.calls == [("docker exec amnezia-awg awg show awg0 dump", None)]
    assert peers[0].peer_public_key == "known-peer"


def test_awg_dump_traffic_collector_raises_redacted_error_on_failure():
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=1,
            stdout="",
            stderr="failed with secret-psk",
        )
    )
    collector = AwgDumpTrafficCollector(
        interface="awg0",
        source="awg:debian-vps-1",
        ssh_client=ssh,
        now=lambda: "2026-05-27T12:00:00Z",
    )

    try:
        collector.collect(server_id=1)
    except TrafficCollectionError as exc:
        assert "Traffic collection failed" in str(exc)
        assert "secret-psk" not in str(exc)
    else:
        raise AssertionError("collector must fail on non-zero awg exit")


class RecordingSshClient:
    def __init__(self, *, result):
        self.calls = []
        self._result = result

    def run(self, command: str, stdin: str | None = None) -> CommandResult:
        self.calls.append((command, stdin))
        return self._result
