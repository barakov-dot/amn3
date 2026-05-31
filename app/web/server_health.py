from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Literal

from app.agent.client import AgentClientError, AgentProtocol, LocalAgentClient
from app.config.settings import Settings
from app.security.redaction import redact
from app.server.checks import run_server_checks
from app.server.report import CheckResult
from app.server.report import ServerCheckReport
from app.server.ssh import SystemSshClient
from app.server_config.loader import ConfigError
from app.server_config.loader import load_server_config
from app.server_config.loader import select_server


HealthStatus = Literal["online", "degraded", "offline", "unknown"]

_AWG_CHECK_NAMES = {"awg", "awg-quick", "interface"}


@dataclass(frozen=True)
class HealthSummary:
    status: HealthStatus
    latency_ms: int | None
    ssh_ok: bool
    awg_ok: bool
    udp_port_ok: bool
    error: str | None
    operation_id: str = "server.health.check"
    risk_class: str = "read-only-remote"
    consistency_status: str = "read-only"


@dataclass(frozen=True)
class LocalAgentSummary:
    status: HealthStatus
    status_class: str
    base_url: str
    service: str | None
    server_name: str | None
    runtime_type: str | None
    runtime_status: str | None
    protocols: tuple[AgentProtocol, ...]
    error: str | None
    operation_id: str = "local_agent.probe"
    risk_class: str = "read-only-runtime"
    consistency_status: str = "read-only"


def summarize_check_report(
    report: ServerCheckReport,
    latency_ms: int | None,
) -> HealthSummary:
    if not report.results:
        return HealthSummary(
            status="unknown",
            latency_ms=latency_ms,
            ssh_ok=False,
            awg_ok=False,
            udp_port_ok=False,
            error="No check results returned",
        )

    if any(result.status == "error" for result in report.results):
        status: HealthStatus = "offline"
    elif any(result.status == "warning" for result in report.results):
        status = "degraded"
    else:
        status = "online"

    return HealthSummary(
        status=status,
        latency_ms=latency_ms,
        ssh_ok=_ssh_ok(report.results),
        awg_ok=_all_named_checks_ok(report.results, _AWG_CHECK_NAMES),
        udp_port_ok=_all_named_checks_ok(report.results, {"udp-port"}),
        error=_issue_summary(report.results),
    )


def run_server_health_check(settings: Settings, server_name: str) -> HealthSummary:
    config_path = Path(settings.server_config_path)
    try:
        config = load_server_config(config_path)
        server = select_server(config, server_name)
    except ConfigError as exc:
        return HealthSummary(
            status="unknown",
            latency_ms=None,
            ssh_ok=False,
            awg_ok=False,
            udp_port_ok=False,
            error=redact(
                f"Add server '{server_name}' to {config_path} before running "
                f"a live health check: {exc}"
            ),
        )

    started_at = perf_counter()
    try:
        report = run_server_checks(
            server,
            SystemSshClient(server, password=settings.vps_ssh_password),
        )
    except Exception as exc:  # pragma: no cover - defensive boundary for UI safety.
        return HealthSummary(
            status="unknown",
            latency_ms=None,
            ssh_ok=False,
            awg_ok=False,
            udp_port_ok=False,
            error=redact(
                "Live health check failed before a report could be stored: "
                f"{type(exc).__name__}: {exc}"
            ),
        )

    latency_ms = max(0, int((perf_counter() - started_at) * 1000))
    return summarize_check_report(report, latency_ms=latency_ms)


def probe_local_agent_controller(
    settings: Settings,
    *,
    client_factory=LocalAgentClient,
) -> LocalAgentSummary:
    base_url = settings.local_agent_controller_base_url
    if not settings.local_agent_controller_enabled:
        return LocalAgentSummary(
            status="disabled",
            status_class="disabled",
            base_url=base_url,
            service=None,
            server_name=None,
            runtime_type=None,
            runtime_status=None,
            protocols=(),
            error="LOCAL_AGENT_CONTROLLER_ENABLED=false",
        )

    token_path = Path(settings.local_agent_controller_token_path)
    try:
        raw_token = token_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return _local_agent_error(
            base_url,
            f"Could not read LOCAL_AGENT_CONTROLLER_TOKEN_PATH: {exc}",
            token="",
            status="unknown",
        )
    if not raw_token:
        return _local_agent_error(
            base_url,
            "LOCAL_AGENT_CONTROLLER_TOKEN_PATH is empty",
            token="",
            status="unknown",
        )

    try:
        client = client_factory(base_url=base_url, bearer_token=raw_token)
        health = client.health()
        runtime = client.runtime()
        protocols = client.protocols()
    except AgentClientError as exc:
        return _local_agent_error(base_url, str(exc), token=raw_token, status="offline")

    status = _local_agent_status(runtime.status)
    return LocalAgentSummary(
        status=status,
        status_class=status,
        base_url=base_url,
        service=health.service,
        server_name=runtime.server_name,
        runtime_type=runtime.runtime_type,
        runtime_status=runtime.status,
        protocols=protocols,
        error=None,
    )


def _ssh_ok(results: list[CheckResult]) -> bool:
    ssh_results = [result for result in results if result.name == "ssh"]
    if ssh_results:
        return all(result.status == "ok" for result in ssh_results)
    return bool(results)


def _all_named_checks_ok(results: list[CheckResult], names: set[str]) -> bool:
    matching = [result for result in results if result.name in names]
    return bool(matching) and all(result.status == "ok" for result in matching)


def _issue_summary(results: list[CheckResult]) -> str | None:
    issues = []
    for result in results:
        if result.status == "ok":
            continue
        issue = f"{result.name}: {result.message}"
        if result.details:
            issue = f"{issue} ({result.details.strip()})"
        issues.append(issue)
    if not issues:
        return None
    return redact("; ".join(issues))


def _local_agent_status(runtime_status: str) -> HealthStatus:
    if runtime_status == "running":
        return "online"
    if runtime_status == "degraded":
        return "degraded"
    if runtime_status == "stopped":
        return "offline"
    return "unknown"


def _local_agent_error(
    base_url: str,
    message: str,
    *,
    token: str,
    status: HealthStatus,
) -> LocalAgentSummary:
    safe_message = message.replace(token, "[REDACTED]") if token else message
    return LocalAgentSummary(
        status=status,
        status_class=status,
        base_url=base_url,
        service=None,
        server_name=None,
        runtime_type=None,
        runtime_status=None,
        protocols=(),
        error=redact(safe_message),
    )
