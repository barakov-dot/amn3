from app.server.report import CheckResult
from app.server.report import ServerCheckReport
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
