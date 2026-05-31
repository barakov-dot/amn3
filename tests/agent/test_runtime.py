from app.agent.runtime import (
    FakeLocalRuntimeAdapter,
    ProtocolSnapshot,
    RuntimeSnapshot,
)


def test_fake_local_runtime_adapter_returns_default_snapshot():
    snapshot = FakeLocalRuntimeAdapter().snapshot()

    assert snapshot == RuntimeSnapshot(
        server_name="local-agent-dev",
        runtime_type="fake",
        status="running",
        protocols=(
            ProtocolSnapshot(
                name="amneziawg",
                status="unknown",
                runtime_type="fake",
                capabilities=("detect", "status"),
                container_name=None,
                interface=None,
                client_count=None,
            ),
        ),
    )


def test_fake_local_runtime_adapter_returns_custom_snapshot():
    custom = RuntimeSnapshot(
        server_name="custom-local",
        runtime_type="docker",
        status="running",
        protocols=(
            ProtocolSnapshot(
                name="xray",
                status="running",
                runtime_type="docker",
                capabilities=("detect", "status"),
                container_name="amnezia-xray",
                interface=None,
                client_count=3,
            ),
        ),
    )

    assert FakeLocalRuntimeAdapter(snapshot=custom).snapshot() == custom


def test_runtime_snapshot_repr_does_not_include_sensitive_terms():
    snapshot = RuntimeSnapshot(
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

    snapshot_repr = repr(snapshot).lower()

    for sensitive_term in (
        "privatekey",
        "private_key",
        "preshared",
        "token",
        "vpn://",
        "client_config",
        "password",
    ):
        assert sensitive_term not in snapshot_repr
