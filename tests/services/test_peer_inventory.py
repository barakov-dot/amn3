from app.db.connection import connect
from app.db.repositories import Repository
from app.db.schema import initialize_schema
from app.services.peer_inventory import (
    AwgDumpPeerInventoryCollector,
    PeerInventoryService,
    parse_awg_peer_inventory_dump,
)
from app.server.ssh import CommandResult


def test_parse_awg_peer_inventory_dump_reads_allowed_ips_and_counters():
    dump = "\n".join(
        [
            "awg0\tserver-public\tserver-private\t51820\toff",
            "known-peer\tpsk\t203.0.113.20:50000\t10.8.0.2/32\t1700000000\t1024\t2048\t25",
            "idle-peer\t(none)\t(none)\t10.8.0.3/32\t0\t0\t0\toff",
        ]
    )

    peers = parse_awg_peer_inventory_dump(dump)

    assert peers[0].peer_public_key == "known-peer"
    assert peers[0].allowed_ips == "10.8.0.2/32"
    assert peers[0].rx_bytes == 1024
    assert peers[0].tx_bytes == 2048
    assert peers[1].latest_handshake == 0


def test_parse_awg_peer_inventory_dump_skips_amneziawg_interface_row():
    dump = "\n".join(
        [
            "server-private\tserver-public\t37661\t4\t10\t50\t19\t90\t45\t17\t1622123045-2053868572",
            "remote-peer\tpsk\t203.0.113.20:50000\t10.8.1.1/32\t1700000000\t1024\t2048\t25",
            "idle-peer\t(none)\t(none)\t10.8.1.2/32\t0\t0\t0\toff",
        ]
    )

    peers = parse_awg_peer_inventory_dump(dump)

    assert [peer.peer_public_key for peer in peers] == ["remote-peer", "idle-peer"]
    assert [peer.allowed_ips for peer in peers] == ["10.8.1.1/32", "10.8.1.2/32"]


def test_peer_inventory_service_compares_remote_and_local_peers(tmp_path):
    conn = connect(tmp_path / "inventory.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    server_id = repo.ensure_default_server(name="local", network_cidr="10.8.0.0/24")
    user_id = repo.upsert_user(
        telegram_id=1001,
        username="known",
        first_name="Known",
        last_name=None,
    )
    repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="known-device",
        duration_days=7,
        vpn_ip="10.8.0.2",
        peer_public_key="known-peer",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )
    repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="missing-device",
        duration_days=7,
        vpn_ip="10.8.0.4",
        peer_public_key="missing-peer",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )
    collector = FakeInventoryCollector(
        "awg0\tserver-public\tserver-private\t51820\toff\n"
        "known-peer\tpsk\t203.0.113.20:50000\t10.8.0.2/32\t1700000000\t1024\t2048\t25\n"
        "unknown-peer\tpsk\t(none)\t10.8.0.3/32\t0\t0\t0\toff\n"
    )

    report = PeerInventoryService(repo).compare(server_id, collector)

    assert [peer.peer_public_key for peer in report.known_remote_peers] == ["known-peer"]
    assert [peer.peer_public_key for peer in report.unknown_remote_peers] == ["unknown-peer"]
    assert [device.peer_public_key for device in report.missing_local_peers] == ["missing-peer"]


def test_awg_dump_peer_inventory_collector_runs_docker_dump_command():
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=0,
            stdout="awg0\tserver-public\tserver-private\t51820\toff\n",
            stderr="",
        )
    )
    collector = AwgDumpPeerInventoryCollector(
        interface="awg0",
        ssh_client=ssh,
        container_name="amnezia-awg",
    )

    collector.collect(server_id=1)

    assert ssh.calls == [("docker exec amnezia-awg awg show awg0 dump", None)]


class FakeInventoryCollector:
    def __init__(self, dump: str):
        self._dump = dump

    def collect(self, server_id: int):
        return parse_awg_peer_inventory_dump(self._dump)


class RecordingSshClient:
    def __init__(self, *, result):
        self.calls = []
        self._result = result

    def run(self, command: str, stdin: str | None = None) -> CommandResult:
        self.calls.append((command, stdin))
        return self._result
