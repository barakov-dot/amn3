from app.server.report import CheckResult
from app.server.report import ServerCheckReport
from app.agent.client import AgentClientError, AgentHealth, AgentProtocol, AgentRuntime
from app.config.settings import Settings
from app.web.server_health import probe_local_agent_controller
from app.web.server_health import summarize_check_report


def test_summarize_check_report_marks_online_when_all_checks_pass():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("ssh", "ok", "connected"),
            CheckResult("awg", "ok", "awg is installed"),
            CheckResult("awg-quick", "ok", "awg-quick is installed"),
            CheckResult("interface", "ok", "awg-quick@awg0 is active"),
            CheckResult("udp-port", "ok", "UDP port 30001 is visible"),
        ],
    )

    summary = summarize_check_report(report, latency_ms=25)

    assert summary.status == "online"
    assert summary.latency_ms == 25
    assert summary.ssh_ok is True
    assert summary.awg_ok is True
    assert summary.udp_port_ok is True
    assert summary.error is None
    assert summary.operation_id == "server.health.check"
    assert summary.risk_class == "read-only-remote"
    assert summary.consistency_status == "read-only"


def test_summarize_check_report_marks_degraded_for_warnings():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("ssh", "ok", "connected"),
            CheckResult("awg", "ok", "awg is installed"),
            CheckResult("awg-quick", "warning", "awg-quick is not installed"),
            CheckResult("udp-port", "warning", "UDP port 30001 is not visible"),
        ],
    )

    summary = summarize_check_report(report, latency_ms=140)

    assert summary.status == "degraded"
    assert summary.ssh_ok is True
    assert summary.awg_ok is False
    assert summary.udp_port_ok is False
    assert summary.error is not None
    assert "awg-quick: awg-quick is not installed" in summary.error
    assert "udp-port: UDP port 30001 is not visible" in summary.error
    assert summary.operation_id == "server.health.check"
    assert summary.risk_class == "read-only-remote"
    assert summary.consistency_status == "read-only"


def test_summarize_check_report_keeps_ssh_ok_when_reachable_report_has_warnings():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("debian", "ok", "Debian detected"),
            CheckResult("systemd", "ok", "systemd is installed"),
            CheckResult("awg", "warning", "awg is not installed"),
            CheckResult("interface", "warning", "awg-quick@awg0 is not active"),
            CheckResult("udp-port", "warning", "UDP port 30001 is not visible"),
        ],
    )

    summary = summarize_check_report(report, latency_ms=50)

    assert summary.status == "degraded"
    assert summary.ssh_ok is True
    assert summary.awg_ok is False
    assert summary.udp_port_ok is False


def test_summarize_check_report_marks_offline_for_errors():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("ssh", "error", "SSH connection timed out"),
            CheckResult("awg", "warning", "awg is not installed"),
        ],
    )

    summary = summarize_check_report(report, latency_ms=None)

    assert summary.status == "offline"
    assert summary.latency_ms is None
    assert summary.ssh_ok is False
    assert summary.awg_ok is False
    assert summary.udp_port_ok is False
    assert summary.error is not None
    assert "ssh: SSH connection timed out" in summary.error
    assert summary.operation_id == "server.health.check"
    assert summary.risk_class == "read-only-remote"
    assert summary.consistency_status == "read-only"


def test_summarize_check_report_keeps_ssh_ok_for_non_ssh_error_results():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult("debian", "ok", "Debian detected"),
            CheckResult("systemd", "error", "systemd is not installed"),
            CheckResult("awg", "warning", "awg is not installed"),
        ],
    )

    summary = summarize_check_report(report, latency_ms=80)

    assert summary.status == "offline"
    assert summary.ssh_ok is True
    assert summary.awg_ok is False
    assert summary.error is not None
    assert "systemd: systemd is not installed" in summary.error


def test_summarize_check_report_marks_unknown_when_no_results_exist():
    report = ServerCheckReport(server_name="debian-vps-1", results=[])

    summary = summarize_check_report(report, latency_ms=None)

    assert summary.status == "unknown"
    assert summary.ssh_ok is False
    assert summary.awg_ok is False
    assert summary.udp_port_ok is False
    assert summary.error == "No check results returned"
    assert summary.operation_id == "server.health.check"
    assert summary.risk_class == "read-only-remote"
    assert summary.consistency_status == "read-only"


def test_probe_local_agent_controller_reads_token_file_and_summarizes_runtime(tmp_path):
    token_path = tmp_path / "local-agent.token"
    token_path.write_text("raw-agent-token\n", encoding="utf-8")
    calls = []

    class FakeAgentClient:
        def __init__(self, *, base_url: str, bearer_token: str):
            calls.append(("init", base_url, bearer_token))

        def health(self) -> AgentHealth:
            calls.append(("health",))
            return AgentHealth(status="ok", service="local-amnezia-agent")

        def runtime(self) -> AgentRuntime:
            calls.append(("runtime",))
            return AgentRuntime(
                server_name="demo-vps",
                runtime_type="docker",
                status="running",
            )

        def protocols(self) -> tuple[AgentProtocol, ...]:
            calls.append(("protocols",))
            return (
                AgentProtocol(
                    name="amneziawg",
                    status="running",
                    runtime_type="docker",
                    capabilities=("detect", "status"),
                    container_name="amnezia-awg",
                    interface="awg0",
                    client_count=2,
                ),
            )

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_token_path=str(token_path),
    )

    summary = probe_local_agent_controller(settings, client_factory=FakeAgentClient)

    assert calls == [
        ("init", "http://127.0.0.1:3031", "raw-agent-token"),
        ("health",),
        ("runtime",),
        ("protocols",),
    ]
    assert summary.status == "online"
    assert summary.status_class == "online"
    assert summary.service == "local-amnezia-agent"
    assert summary.runtime_status == "running"
    assert summary.runtime_type == "docker"
    assert summary.server_name == "demo-vps"
    assert summary.protocols[0].name == "amneziawg"
    assert summary.protocols[0].client_count == 2
    assert summary.error is None
    assert summary.operation_id == "local_agent.probe"
    assert summary.risk_class == "read-only-runtime"
    assert summary.consistency_status == "read-only"
    assert "raw-agent-token" not in repr(summary)


def test_probe_local_agent_controller_returns_disabled_without_token_file():
    summary = probe_local_agent_controller(_settings())

    assert summary.status == "disabled"
    assert summary.status_class == "disabled"
    assert summary.error == "LOCAL_AGENT_CONTROLLER_ENABLED=false"
    assert summary.protocols == ()


def test_probe_local_agent_controller_redacts_client_errors(tmp_path):
    token_path = tmp_path / "local-agent.token"
    token_path.write_text("raw-agent-token\n", encoding="utf-8")

    class FailingAgentClient:
        def __init__(self, *, base_url: str, bearer_token: str):
            pass

        def health(self) -> AgentHealth:
            raise AgentClientError("request failed for raw-agent-token")

    settings = _settings(
        local_agent_controller_enabled=True,
        local_agent_controller_base_url="http://127.0.0.1:3031",
        local_agent_controller_token_path=str(token_path),
    )

    summary = probe_local_agent_controller(settings, client_factory=FailingAgentClient)

    assert summary.status == "offline"
    assert summary.status_class == "offline"
    assert summary.error is not None
    assert "request failed" in summary.error
    assert "raw-agent-token" not in summary.error


def _settings(**overrides) -> Settings:
    values = {
        "_env_file": None,
        "telegram_bot_token": "TEST_TOKEN",
        "app_secret_key": "test-secret",
    }
    values.update(overrides)
    return Settings(**values)
