from app.server.report import CheckResult, ServerCheckReport


def test_report_marks_overall_failed_when_any_error_exists():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult(name="ssh", status="ok", message="connected"),
            CheckResult(name="debian", status="error", message="not Debian"),
        ],
    )

    assert report.ok is False


def test_report_safe_text_redacts_secrets():
    report = ServerCheckReport(
        server_name="debian-vps-1",
        results=[
            CheckResult(
                name="ssh",
                status="error",
                message="failed",
                details="APP_SECRET_KEY = secret-value",
            )
        ],
    )

    text = report.to_text()

    assert "secret-value" not in text
    assert "[REDACTED]" in text
