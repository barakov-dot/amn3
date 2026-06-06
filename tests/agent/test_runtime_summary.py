from dataclasses import asdict

from app.agent.runtime import ProtocolSnapshot, RuntimeSnapshot
from app.agent.runtime_summary import build_runtime_summary


def test_runtime_summary_keeps_only_controller_safe_fields():
    snapshot = RuntimeSnapshot(
        server_name="customer-vps-name",
        runtime_type="docker",
        status="running",
        protocols=(
            ProtocolSnapshot(
                name="amneziawg",
                status="running",
                runtime_type="docker",
                capabilities=("detect", "status"),
                container_name="amnezia-awg2",
                interface="awg0",
                client_count=4,
            ),
        ),
    )

    summary = build_runtime_summary(
        agent_status="ok",
        agent_version="test-build",
        runtime_contract_version=1,
        write_enabled=False,
        runtime=snapshot,
    )

    assert asdict(summary) == {
        "agent_status": "ok",
        "agent_version": "test-build",
        "runtime_contract_version": 1,
        "write_enabled": False,
        "controller_display_status": "safe",
        "runtime_type": "docker",
        "runtime_status": "running",
        "protocols": (
            {
                "name": "amneziawg",
                "status": "running",
                "runtime_type": "docker",
                "capabilities": ("detect", "status"),
                "client_count": 4,
            },
        ),
    }

    joined = repr(asdict(summary)).lower()
    for forbidden in (
        "customer-vps-name",
        "server_name",
        "amnezia-awg2",
        "container_name",
        "awg0",
        "interface",
        "config_path",
        "stdout",
        "stderr",
        "privatekey",
        "private_key",
        "preshared",
        "psk",
        "vpn://",
        "endpoint",
        "latest_handshake",
        "traffic",
        "client_name",
        "configs",
    ):
        assert forbidden not in joined


def test_runtime_summary_marks_non_false_write_enabled_as_unsafe():
    summary = build_runtime_summary(
        agent_status="ok",
        agent_version="test-build",
        runtime_contract_version=1,
        write_enabled=True,
        runtime=RuntimeSnapshot(
            server_name="demo",
            runtime_type="docker",
            status="running",
            protocols=(),
        ),
    )

    assert summary.agent_status == "ok"
    assert summary.write_enabled is True
    assert summary.controller_display_status == "unsafe"
    assert summary.runtime_type == "docker"
    assert summary.runtime_status == "running"
    assert summary.protocols == ()


def test_runtime_summary_handles_missing_runtime_as_unknown():
    summary = build_runtime_summary(
        agent_status="unknown",
        agent_version=None,
        runtime_contract_version=None,
        write_enabled=None,
        runtime=None,
    )

    assert asdict(summary) == {
        "agent_status": "unknown",
        "agent_version": None,
        "runtime_contract_version": None,
        "write_enabled": None,
        "controller_display_status": "unsafe",
        "runtime_type": "unknown",
        "runtime_status": "unknown",
        "protocols": (),
    }
