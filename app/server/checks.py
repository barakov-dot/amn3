import re

from app.server.operations import CommandStep, RemoteOperation
from app.server.report import CheckResult, ServerCheckReport
from app.server.ssh import CommandResult, SshClient
from app.server_config.models import ServerConfig


class CommandPolicyError(ValueError):
    pass


_EXACT_READ_ONLY_COMMANDS = {
    "cat /etc/os-release",
    "command -v systemctl",
    "command -v awg",
    "command -v awg-quick",
    "command -v ufw",
    "command -v docker",
    "docker ps --format {{.Names}}",
    "ss -lun",
}
_SYSTEMD_ACTIVE_RE = re.compile(r"^systemctl is-active awg-quick@[A-Za-z0-9_.:-]+$")
_DOCKER_EXEC_AWG_COMMAND_RE = re.compile(r"^docker exec [A-Za-z0-9_.:-]+ command -v awg$")
_DOCKER_EXEC_AWG_SHOW_RE = re.compile(r"^docker exec [A-Za-z0-9_.:-]+ awg show [A-Za-z0-9_.:-]+(?: dump)?$")
_SHELL_CONTROL_TOKENS = ("|", "&", ";", ">", "<", "`", "$(", "\n", "\r")
_MUTATING_WORDS = {
    "apt",
    "apt-get",
    "chmod",
    "chown",
    "cp",
    "curl",
    "dd",
    "docker",
    "install",
    "iptables",
    "mkdir",
    "mv",
    "reboot",
    "rm",
    "rsync",
    "scp",
    "sed",
    "service",
    "start",
    "stop",
    "systemctl start",
    "systemctl stop",
    "systemctl enable",
    "tee",
    "ufw",
    "wget",
}

READ_ONLY_CHECK_COMMANDS = (
    "cat /etc/os-release",
    "command -v systemctl",
    "command -v awg",
    "command -v awg-quick",
    "command -v ufw",
    "systemctl is-active awg-quick@{interface}",
    "ss -lun",
)
DOCKER_READ_ONLY_CHECK_COMMANDS = (
    "cat /etc/os-release",
    "command -v docker",
    "docker ps --format {{{{.Names}}}}",
    "docker exec {container} command -v awg",
    "docker exec {container} awg show {interface}",
    "ss -lun",
)


def planned_check_commands(server: ServerConfig) -> list[str]:
    if server.runtime.type == "docker":
        container = server.runtime.container_name or ""
        return [
            command.format(container=container, interface=server.vpn.interface)
            for command in DOCKER_READ_ONLY_CHECK_COMMANDS
        ]
    return [
        command.format(interface=server.vpn.interface)
        for command in READ_ONLY_CHECK_COMMANDS
    ]


def build_server_check_operation(
    server: ServerConfig,
    *,
    actor_id: str,
    actor_auth_method,
) -> RemoteOperation:
    commands = planned_check_commands(server)
    steps = tuple(
        CommandStep(
            id=f"server-check-{index + 1}",
            command=command,
            command_policy_class="read-only",
            expected_remote_effect="none",
            allowed_exit_codes=(0,),
            timeout_seconds=20,
            output_policy="internal-only",
        )
        for index, command in enumerate(commands)
    )
    return RemoteOperation(
        id="server.health.check",
        risk_class="read-only-remote",
        server_id=server.name,
        actor_id=actor_id,
        actor_auth_method=actor_auth_method,
        inputs={
            "server_name": server.name,
            "runtime": server.runtime.type,
        },
        secret_refs=(),
        local_side_effects=("server_health_checks", "admin_actions"),
        remote_side_effects=(),
        command_policy="read-only",
        steps=steps,
        consistency_policy="read-only",
        audit_summary=f"Run read-only health check for server {server.name}",
        rollback_note=(
            "No rollback is needed for read-only health checks. "
            "Re-run server check after fixing server access."
        ),
        confirmation_required=False,
    )


def ensure_read_only_command(command: str) -> None:
    normalized = " ".join(command.strip().split())
    if not normalized:
        raise CommandPolicyError("Empty command is not allowed")
    if any(token in command for token in _SHELL_CONTROL_TOKENS):
        raise CommandPolicyError(f"Shell control token is not allowed: {normalized}")
    if (
        normalized in _EXACT_READ_ONLY_COMMANDS
        or _SYSTEMD_ACTIVE_RE.match(normalized)
        or _DOCKER_EXEC_AWG_COMMAND_RE.match(normalized)
        or _DOCKER_EXEC_AWG_SHOW_RE.match(normalized)
    ):
        return
    lowered = normalized.lower()
    for word in _MUTATING_WORDS:
        if lowered == word or lowered.startswith(f"{word} "):
            raise CommandPolicyError(f"Mutating command is not allowed: {normalized}")
    raise CommandPolicyError(f"Command is not in the read-only allowlist: {normalized}")


def run_server_checks(server: ServerConfig, ssh: SshClient) -> ServerCheckReport:
    from app.server.operation_runner import RemoteOperationRunner

    operation = build_server_check_operation(
        server,
        actor_id="system",
        actor_auth_method="system",
    )
    operation_result = RemoteOperationRunner(ssh).apply(operation)
    if operation_result.status == "blocked":
        return ServerCheckReport(
            server_name=server.name,
            results=[
                CheckResult(
                    "remote-operation-policy",
                    "error",
                    operation_result.recovery_note,
                )
            ],
        )
    commands = [step.command for step in operation_result.steps]
    command_results = {
        step.command: CommandResult(step.exit_code, step.stdout, step.stderr)
        for step in operation_result.steps
    }
    if server.runtime.type == "docker":
        results = [
            _check_debian(command_results[commands[0]]),
            _check_command("docker", command_results[commands[1]], missing_status="error"),
            _check_container(server, command_results[commands[2]]),
            _check_command("awg", command_results[commands[3]], missing_status="warning"),
            _check_docker_interface(server, command_results[commands[4]]),
            _check_udp_port(server, command_results[commands[5]]),
        ]
        return ServerCheckReport(server_name=server.name, results=results)

    results = [
        _check_debian(command_results[commands[0]]),
        _check_command("systemd", command_results[commands[1]], missing_status="error"),
        _check_command("awg", command_results[commands[2]], missing_status="warning"),
        _check_command("awg-quick", command_results[commands[3]], missing_status="warning"),
        _check_command("ufw", command_results[commands[4]], missing_status="warning"),
        _check_interface(server, command_results[commands[5]]),
        _check_udp_port(server, command_results[commands[6]]),
    ]
    return ServerCheckReport(server_name=server.name, results=results)


def _run(ssh: SshClient, command: str) -> CommandResult:
    ensure_read_only_command(command)
    return ssh.run(command)


def _check_debian(result: CommandResult) -> CheckResult:
    if result.exit_code != 0:
        return CheckResult("debian", "error", "Could not read /etc/os-release", result.stderr)
    if "ID=debian" not in result.stdout:
        return CheckResult("debian", "error", "Server OS is not Debian", result.stdout)
    return CheckResult("debian", "ok", "Debian detected", result.stdout)


def _check_command(name: str, result: CommandResult, *, missing_status: str) -> CheckResult:
    if result.exit_code == 0:
        return CheckResult(name, "ok", f"{name} is installed", result.stdout.strip())
    return CheckResult(name, missing_status, f"{name} is not installed", result.stderr or result.stdout)


def _check_interface(server: ServerConfig, result: CommandResult) -> CheckResult:
    service = server.runtime.service_name or "<missing-service>"
    active_text = result.stdout.strip() or result.stderr.strip()
    if result.exit_code == 0 and active_text == "active":
        return CheckResult("interface", "ok", f"{service} is active", active_text)
    return CheckResult("interface", "warning", f"{service} is not active", active_text)


def _check_container(server: ServerConfig, result: CommandResult) -> CheckResult:
    container = server.runtime.container_name or "<missing-container>"
    if result.exit_code != 0:
        return CheckResult("container", "error", "Could not list Docker containers", result.stderr)
    containers = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if container in containers:
        return CheckResult("container", "ok", f"Docker container {container} is running", result.stdout)
    return CheckResult("container", "error", f"Docker container {container} is not running", result.stdout)


def _check_docker_interface(server: ServerConfig, result: CommandResult) -> CheckResult:
    container = server.runtime.container_name or "<missing-container>"
    output = result.stdout.strip() or result.stderr.strip()
    if result.exit_code == 0:
        return CheckResult(
            "interface",
            "ok",
            f"awg show {server.vpn.interface} succeeded in container {container}",
            output,
        )
    return CheckResult(
        "interface",
        "warning",
        f"awg show {server.vpn.interface} failed in container {container}",
        output,
    )


def _check_udp_port(server: ServerConfig, result: CommandResult) -> CheckResult:
    if result.exit_code != 0:
        return CheckResult("udp-port", "warning", "Could not inspect UDP sockets", result.stderr)
    port = str(server.vpn.port)
    if port in result.stdout:
        return CheckResult("udp-port", "ok", f"UDP port {port} is visible", result.stdout)
    return CheckResult("udp-port", "warning", f"UDP port {port} is not visible", result.stdout)
