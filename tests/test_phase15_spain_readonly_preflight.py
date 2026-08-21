import base64
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
COLLECTOR = ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "phase15_spain_readonly_preflight_ssh_runner.ps1"
PACKAGE_ID = "phase15-dual-protocol-bootstrap-20260811-001"
MANIFEST_SHA256 = "a" * 64
COLLECTOR_SHA256 = "b" * 64
FIXTURES = Path(__file__).parent / "fixtures" / "phase15_spain_preflight"
EXPECTED_OBSERVATIONS = {
    "application_state",
    "architecture",
    "awg2_health",
    "backup_capability",
    "bridge_amn2sp3br0",
    "config_path",
    "container_capability",
    "container_cidr_172_29_252_0_28",
    "container_name",
    "database_state",
    "disk_space",
    "firewall",
    "interface_awg3",
    "os_compatibility",
    "python_3_12",
    "recovery_markers_phase14_phase15",
    "routes",
    "service_capability",
    "service_name",
    "state_root",
    "telegram_prerequisites",
    "udp_30002",
    "vpn_cidr_10_212_13_0_24",
}


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        pytest.fail(f"missing {label}: {path}")
    return path


def fixture_snapshot(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def run_collector(name: str):
    require_file(COLLECTOR, "collector")
    fixture = FIXTURES / name
    before = fixture_snapshot(fixture)
    observed = collector_helper("observed")
    build_document = collector_helper("build_document")
    fixture_value = json.loads((fixture / "observations.json").read_text(encoding="utf-8"))
    host_identity = fixture_value["host_identity"]
    raw_values = {name: observed(item["state"], item["raw"]) for name, item in fixture_value["observations"].items()}
    document = build_document(
        package_id=PACKAGE_ID,
        manifest_sha256=MANIFEST_SHA256,
        collector_sha256=COLLECTOR_SHA256,
        claim_id="phase15-preflight-test-001",
        expected_host="spain.test.invalid",
        host_identity=host_identity,
        raw_values=raw_values,
        observed_at="2026-08-16T00:00:00Z",
    )
    stdout = (json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()
    result = SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")
    after = fixture_snapshot(fixture)
    return result, before, after


def collector_python_namespace() -> dict[str, object]:
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    match = re.search(r'(?ms)^exec /usr/bin/python3 -I -B - "\$1" "\$2" "\$3" "\$4" "\$5" <<\'PHASE15_PY\'\n(?P<body>.*)\nPHASE15_PY$', source)
    if match is None:
        match = re.search(r'(?ms)^exec "\$python_executable" - "\$1" "\$2" "\$3" "\$4" "\$5" <<\'PHASE15_PY\'\n(?P<body>.*)\nPHASE15_PY$', source)
    if match is None:
        match = re.search(r'(?ms)^exec "\$python_executable" -c \'\n(?P<body>.*)\n\'(?: .*)?$', source)
    if match is None:
        pytest.fail("collector embedded Python not found")
    body = match.group("body")
    prefix = body.split("\ntry:\n    claim_id", 1)[0]
    namespace: dict[str, object] = {"__name__": "phase15_collector_test"}
    exec(compile(prefix, str(COLLECTOR), "exec"), namespace)
    return namespace


def collector_helper(name: str):
    helper = collector_python_namespace().get(name)
    if not callable(helper):
        pytest.fail(f"missing collector helper: {name}")
    return helper


def test_actual_shell_entrypoint_preserves_embedded_python_literals_and_exact_argv(tmp_path: Path):
    harness = tmp_path / "collector_harness.py"
    wrapper = tmp_path / "python-double"
    collector_copy = tmp_path / "collector.sh"
    expected = [PACKAGE_ID, MANIFEST_SHA256, COLLECTOR_SHA256, "phase15-preflight-test-001", "spain.test.invalid"]
    harness.write_text(
        "import sys\n"
        "source = sys.stdin.read()\n"
        "assert sys.argv[1] == '-'\n"
        f"assert sys.argv[2:] == {expected!r}\n"
        "compile(source, '<phase15-collector>', 'exec')\n"
        "prefix = source.split('\\ntry:\\n    claim_id', 1)[0]\n"
        "namespace = {'__name__': 'phase15_entrypoint_test'}\n"
        "exec(compile(prefix, '<phase15-prefix>', 'exec'), namespace)\n"
        "assert namespace['_network_conflicts']('192.0.2.0/24') is False\n"
        "assert namespace['_nft_scalar_conflict']({'prefix': {'addr': '192.0.2.0', 'len': 24}}, 'saddr') is False\n"
        "assert namespace['parse_awg2_container_probe']((0, b'true|4242|0\\n', b'', 'success')) == (4242, 0)\n"
        "assert namespace['current_spain_identity']()['interface'] == 'awg0'\n"
        "print('ENTRYPOINT_OK')\n",
        encoding="utf-8",
        newline="\n",
    )
    python_path = str(Path(sys.executable)).replace("\\", "/")
    harness_path = str(harness).replace("\\", "/")
    wrapper.write_text(
        f"#!/usr/bin/env bash\nshift 2\nexec {shlex.quote(python_path)} {shlex.quote(harness_path)} \"$@\"\n",
        encoding="utf-8",
        newline="\n",
    )
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    wrapper_path = str(wrapper).replace("\\", "/")
    collector_copy.write_text(
        source.replace("exec /usr/bin/python3 -I -B -", f'exec /usr/bin/bash "{wrapper_path}" -I -B -'),
        encoding="utf-8",
        newline="\n",
    )
    result = subprocess.run(
        [str(BASH), str(collector_copy), *expected],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "ENTRYPOINT_OK\n"
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert "<<'PHASE15_PY'" in source
    assert '"$1" "$2" "$3" "$4" "$5"' in source
    assert ' -c \'\n' not in source
    assert "prefix['addr']" in source and "prefix['len']" in source and ".decode('ascii')" in source


def test_ready_fixture_emits_one_utf8_json_document_without_writes():
    result, before, after = run_collector("ready")

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stderr == b""
    assert result.stdout.endswith(b"\n") and result.stdout.count(b"\n") == 1
    document = json.loads(result.stdout.decode("utf-8"))
    assert document["schema"] == "amn2.phase15.spain-readonly-collector.v1"
    assert document["package_id"] == PACKAGE_ID
    assert document["manifest_sha256"] == MANIFEST_SHA256
    assert document["collector_sha256"] == COLLECTOR_SHA256
    assert document["host_identity"] == "spain.test.invalid"
    assert document["decision"] == "pass"
    assert document["blocking_reasons"] == []
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", document["observed_at"])
    assert {item["name"] for item in document["observations"]} == EXPECTED_OBSERVATIONS
    assert all(item["state"] in {"absent", "free", "pass", "present", "stop", "unknown"} for item in document["observations"])
    assert all(len(item["observation_sha256"]) == 64 for item in document["observations"])
    assert document["safety"] == {
        "live_mutation": False,
        "raw_output_persisted": False,
        "remote_file_written": False,
    }
    assert before == after


def test_conflict_fixture_reports_resource_and_recovery_stops_without_changes():
    result, before, after = run_collector("conflict")

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    document = json.loads(result.stdout.decode("utf-8"))
    states = {item["name"]: item["state"] for item in document["observations"]}
    assert document["decision"] == "stop"
    assert states["interface_awg3"] == "stop"
    assert states["bridge_amn2sp3br0"] == "stop"
    assert states["udp_30002"] == "stop"
    assert states["vpn_cidr_10_212_13_0_24"] == "stop"
    assert states["container_cidr_172_29_252_0_28"] == "stop"
    assert states["recovery_markers_phase14_phase15"] == "stop"
    assert set(document["blocking_reasons"]) >= {
        "resource_conflict",
        "recovery_incomplete",
    }
    assert before == after


def test_observation_hashes_bind_safe_states_without_returning_raw_fixture_values():
    result, _before, _after = run_collector("ready")

    document = json.loads(result.stdout.decode("utf-8"))
    fixture = json.loads((FIXTURES / "ready" / "observations.json").read_text(encoding="utf-8"))
    by_name = {item["name"]: item for item in document["observations"]}
    raw = fixture["observations"]["awg2_health"]["raw"].encode("utf-8")
    assert by_name["awg2_health"]["observation_sha256"] == hashlib.sha256(raw).hexdigest()
    assert fixture["observations"]["telegram_prerequisites"]["raw"].encode("utf-8") not in result.stdout


def test_collector_requires_exact_positional_remote_envelope(tmp_path: Path):
    require_file(COLLECTOR, "collector")
    source = COLLECTOR.read_text(encoding="utf-8")
    temporary = tmp_path / "collector.sh"
    wrapper = tmp_path / "python-wrapper"
    python_path = sys.executable.replace("\\", "/")
    wrapper.write_text(f'#!/usr/bin/env bash\nexec "{python_path}" "$@"\n', encoding="utf-8", newline="\n")
    wrapper_path = str(wrapper).replace("\\", "/")
    temporary.write_text(
        source.replace("    /usr/bin/python3 -I -B -c", f'    /usr/bin/bash "{wrapper_path}" -I -B -c'),
        encoding="utf-8",
        newline="\n",
    )

    try:
        result = subprocess.run(
            [str(BASH), str(temporary)],
            check=False,
            capture_output=True,
            timeout=10,
        )
    finally:
        temporary.unlink(missing_ok=True)

    assert result.returncode == 64
    assert result.stdout == b""
    assert result.stderr == b"collector_envelope_invalid\n"


def test_collector_has_no_production_fixture_environment_bypass():
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert "PHASE15_PREFLIGHT_FIXTURE_ROOT" not in source
    assert "PHASE15_PYTHON" not in source


@pytest.mark.parametrize(
    "values",
    [
        ("wrong-package", MANIFEST_SHA256, COLLECTOR_SHA256, "phase15-preflight-test-001", "spain.test.invalid"),
        (PACKAGE_ID, "A" * 64, COLLECTOR_SHA256, "phase15-preflight-test-001", "spain.test.invalid"),
        (PACKAGE_ID, MANIFEST_SHA256, "b" * 63, "phase15-preflight-test-001", "spain.test.invalid"),
        (PACKAGE_ID, MANIFEST_SHA256, COLLECTOR_SHA256, "Bad Claim", "spain.test.invalid"),
        (PACKAGE_ID, MANIFEST_SHA256, COLLECTOR_SHA256, "phase15-preflight-test-001", "user@host"),
    ],
)
def test_collector_five_field_envelope_is_exact(values: tuple[str, ...]):
    validate = collector_helper("validate_envelope")
    assert validate(PACKAGE_ID, MANIFEST_SHA256, COLLECTOR_SHA256, "phase15-preflight-test-001", "spain.test.invalid")
    assert not validate(*values)


def test_collector_command_streams_and_caps_stdout_and_stderr_at_limit_plus_one():
    namespace = collector_python_namespace()
    namespace["ALLOWED_COMMANDS"].add(sys.executable)
    command = namespace["command"]
    result = command(
        [sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*4096);sys.stderr.buffer.write(b'y'*4096)"],
        maximum_output_bytes=32,
        timeout_seconds=5,
    )

    return_code, stdout, stderr, disposition = result
    assert return_code != 0
    assert len(stdout) <= 33
    assert len(stderr) <= 33
    assert disposition == "output_oversized"


def test_collector_command_only_classifies_exact_missing_binary_as_unavailable(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    command = namespace["command"]
    subprocess_module = namespace["subprocess"]

    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError()))
    assert command(["/usr/bin/systemctl"]) == (127, b"", b"", "unavailable")

    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError()))
    assert command(["/usr/bin/systemctl"])[3] == "launch_failed"


def test_collector_command_fails_closed_on_reader_exception_or_incomplete_eof(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    command = namespace["command"]
    subprocess_module = namespace["subprocess"]

    class RaisingStream:
        def read(self, _count: int):
            raise OSError("synthetic reader failure")

        def close(self):
            pass

    class BlockingStream:
        def __init__(self, release: threading.Event):
            self.release = release

        def read(self, _count: int):
            self.release.wait(2)
            return b""

        def close(self):
            pass

    class FakeProcess:
        def __init__(self, stdout, stderr):
            self.stdout = stdout
            self.stderr = stderr

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: FakeProcess(RaisingStream(), io.BytesIO()))
    assert command(["/usr/bin/systemctl"])[3] == "incomplete_output"

    release = threading.Event()
    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: FakeProcess(BlockingStream(release), io.BytesIO()))
    try:
        assert command(["/usr/bin/systemctl"])[3] == "incomplete_output"
    finally:
        release.set()


def test_collector_kill_and_wait_paths_are_bounded_and_fail_incomplete(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    command = namespace["command"]
    subprocess_module = namespace["subprocess"]

    class RetainedProcess:
        def __init__(self):
            self.stdout = io.BytesIO()
            self.stderr = io.BytesIO()
            self.wait_timeouts: list[float | None] = []
            self.kills = 0

        def poll(self):
            return 0

        def wait(self, timeout=None):
            self.wait_timeouts.append(timeout)
            raise subprocess.TimeoutExpired("synthetic", timeout)

        def kill(self):
            self.kills += 1

    process = RetainedProcess()
    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: process)
    result = command(["/usr/bin/systemctl"], timeout_seconds=0)

    assert result[0] != 0
    assert result[3] == "incomplete_output"
    assert process.kills >= 1
    assert process.wait_timeouts and all(timeout is not None and timeout <= 1 for timeout in process.wait_timeouts)
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    command_source = source[source.index("def command") : source.index("def probe_ok")]
    assert "process.wait()" not in command_source


@pytest.mark.parametrize(
    ("return_code", "stderr", "expected"),
    [
        (1, b'Device "awg3" does not exist.\n', "free"),
        (1, b"permission denied\n", "stop"),
        (2, b'Device "awg3" does not exist.\n', "stop"),
        (0, b"", "stop"),
    ],
)
def test_interface_absence_is_exact_and_errors_fail_closed(return_code: int, stderr: bytes, expected: str):
    classify = collector_helper("classify_ip_link")
    probe = (return_code, b"", stderr, "success" if return_code == 0 else "command_failed")

    assert classify(probe, "awg3") == expected


def test_container_inventory_includes_stopped_objects_and_errors_fail_closed():
    classify = collector_helper("classify_container_inventory")

    stopped_conflict = classify([("docker", (0, b"amn2-spain-awg3\n", b"", "success"))])
    clean = classify([("podman", (0, b"other-container\n", b"", "success"))])
    errored = classify([("docker", (125, b"", b"daemon unavailable", "command_failed"))])
    stderr_on_success = classify([("docker", (0, b"other-container\n", b"warning\n", "success"))])
    malformed_name = classify([("docker", (0, b"valid-name\ninvalid name\n", b"", "success"))])
    duplicate_name = classify([("docker", (0, b"same-name\nsame-name\n", b"", "success"))])

    assert stopped_conflict == ("pass", "stop")
    assert clean == ("pass", "free")
    assert errored == ("stop", "stop")
    assert stderr_on_success == ("stop", "stop")
    assert malformed_name == ("stop", "stop")
    assert duplicate_name == ("stop", "stop")


def test_phase13_current_spain_identity_and_dedicated_docker_inventory_are_exact():
    classify = collector_helper("classify_dedicated_spain_docker")
    identity = collector_helper("current_spain_identity")()
    success = "success"
    inventory = (0, b"amn2-spain-awg\nother\n", b"", success)
    networks = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [(0, b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.28.0.0/16"}],"Driver":"default","Options":{}}\n', b"", success)]
    conflict_subnets = [(0, b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.29.252.8/29"}],"Driver":"default","Options":{}}\n', b"", success)]

    assert classify(inventory, networks, clean_subnets) == ("pass", "free", "free")
    assert classify((0, b"amn2-spain-awg3\n", b"", success), networks, clean_subnets) == ("pass", "stop", "free")
    assert classify(inventory, networks, conflict_subnets) == ("pass", "free", "stop")
    assert classify(inventory, (0, b"malformed-id\n", b"", success), clean_subnets) == ("stop", "stop", "stop")
    assert classify(inventory, networks, [(0, clean_subnets[0][1], b"warning\n", success)]) == ("stop", "stop", "stop")
    assert identity == {
        "application_root": "/opt/amn2-spain",
        "bot_unit": "amn2-spain-bot.service",
        "container": "amn2-spain-awg",
        "database_path": "/var/lib/amn2-spain/amn2.sqlite3",
        "docker_host": "unix:///run/amn2-spain-docker/docker.sock",
        "interface": "awg0",
    }

    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    for literal in (
        'CURRENT_APPLICATION_ROOT = "/opt/amn2-spain"',
        'CURRENT_DATABASE_PATH = "/var/lib/amn2-spain/amn2.sqlite3"',
        'CURRENT_AWG2_CONTAINER = "amn2-spain-awg"',
        'CURRENT_AWG2_INTERFACE = "awg0"',
        'CURRENT_BOT_UNIT = "amn2-spain-bot.service"',
        'SPAIN_DOCKER_HOST = "unix:///run/amn2-spain-docker/docker.sock"',
    ):
        assert literal in source


def test_candidate_inventory_combines_explicit_local_system_spain_and_podman_engines():
    classify = collector_helper("classify_spain_docker_sources")
    success = "success"
    unavailable = (127, b"", b"", "unavailable")
    failed = (126, b"", b"permission denied\n", "launch_failed")
    clean_inventory = (0, b"other\n", b"", success)
    candidate_inventory = (0, b"amn2-spain-awg3\n", b"", success)
    network_ids = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [(0, b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.28.0.0/16"}],"Driver":"default","Options":{}}\n', b"", success)]
    conflict_subnets = [(0, b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.29.252.8/29"}],"Driver":"default","Options":{}}\n', b"", success)]
    dedicated = (clean_inventory, network_ids, clean_subnets)

    system = (clean_inventory, network_ids, clean_subnets)

    assert classify(system, dedicated, (unavailable, None, [])) == ("pass", "free", "free")
    assert classify((candidate_inventory, network_ids, clean_subnets), dedicated, (unavailable, None, [])) == ("pass", "stop", "free")
    assert classify(system, dedicated, (candidate_inventory, network_ids, clean_subnets)) == ("pass", "stop", "free")
    assert classify((clean_inventory, network_ids, conflict_subnets), dedicated, (unavailable, None, [])) == ("pass", "free", "stop")
    assert classify(system, dedicated, (failed, None, [])) == ("stop", "stop", "stop")
    assert classify((unavailable, None, []), dedicated, (unavailable, None, [])) == ("stop", "stop", "stop")


def test_container_engine_commands_bind_local_endpoints_and_inventory_all_rows_and_networks():
    namespace = collector_python_namespace()
    production_source = namespace.get("production_container_source")
    assert callable(production_source), "missing explicit container-engine inventory"
    network_id = "a" * 64
    calls: list[list[str]] = []

    def local_double(parts, **_kwargs):
        calls.append(parts)
        if "ps" in parts:
            return 0, b"other-container\n", b"", "success"
        if parts[-3:] == ["ls", "-q", "--no-trunc"]:
            return 0, (network_id + "\n").encode(), b"", "success"
        if "/usr/bin/podman" in parts:
            return 0, b'"podman"\t"bridge"\t[{"subnet":"172.28.0.0/16"}]\n', b"", "success"
        return 0, b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.28.0.0/16"}],"Driver":"default","Options":{}}\n', b"", "success"

    namespace["command"] = local_double
    for engine in ("system-docker", "spain-docker", "podman"):
        inventory, networks, inspections = production_source(engine)
        assert inventory[3] == networks[3] == inspections[0][3] == "success"

    assert calls == [
        ["/usr/bin/docker", "--host", "unix:///var/run/docker.sock", "ps", "-a", "--format", "{{.Names}}"],
        ["/usr/bin/docker", "--host", "unix:///var/run/docker.sock", "network", "ls", "-q", "--no-trunc"],
        ["/usr/bin/docker", "--host", "unix:///var/run/docker.sock", "network", "inspect", "--format", "{{json .Name}}\t{{json .Driver}}\t{{json .IPAM}}", network_id],
        ["/opt/amn2-spain/docker/bin/docker", "--host", "unix:///run/amn2-spain-docker/docker.sock", "ps", "-a", "--format", "{{.Names}}"],
        ["/opt/amn2-spain/docker/bin/docker", "--host", "unix:///run/amn2-spain-docker/docker.sock", "network", "ls", "-q", "--no-trunc"],
        ["/opt/amn2-spain/docker/bin/docker", "--host", "unix:///run/amn2-spain-docker/docker.sock", "network", "inspect", "--format", "{{json .Name}}\t{{json .Driver}}\t{{json .IPAM}}", network_id],
        ["/usr/bin/podman", "--url", "unix:///run/podman/podman.sock", "ps", "-a", "--format", "{{.Names}}"],
        ["/usr/bin/podman", "--url", "unix:///run/podman/podman.sock", "network", "ls", "-q", "--no-trunc"],
        ["/usr/bin/podman", "--url", "unix:///run/podman/podman.sock", "network", "inspect", "--format", "{{json .Name}}\t{{json .Driver}}\t{{json .Subnets}}", network_id],
    ]


def test_command_removes_ambient_container_connection_selectors(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    command = namespace["command"]
    captured: dict[str, str] = {}
    for name in ("DOCKER_HOST", "DOCKER_CONTEXT", "CONTAINER_HOST", "CONTAINER_CONNECTION", "PODMAN_HOST", "PODMAN_CONNECTION"):
        monkeypatch.setenv(name, "tcp://remote.invalid:2375")

    class Process:
        stdout = io.BytesIO()
        stderr = io.BytesIO()

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    def popen(_parts, **kwargs):
        captured.update(kwargs["env"])
        return Process()

    monkeypatch.setattr(namespace["subprocess"], "Popen", popen)
    assert command(["/usr/bin/systemctl"])[3] == "success"
    assert captured["LC_ALL"] == "C"
    assert not set(captured).intersection({"DOCKER_HOST", "DOCKER_CONTEXT", "CONTAINER_HOST", "CONTAINER_CONNECTION", "PODMAN_HOST", "PODMAN_CONNECTION"})


def test_strict_docker_network_ids_reject_real_default_truncation():
    parse_ids = collector_helper("_docker_network_ids")
    with pytest.raises(ValueError, match="docker network inventory"):
        parse_ids((0, b"0123456789ab\n", b"", "success"))

    fixture = json.loads((FIXTURES / "ready" / "observations.json").read_text(encoding="utf-8"))
    assert fixture["observations"]["container_capability"]["raw"] == "local-system-docker-spain-docker-and-podman-inventories-readable"
    assert fixture["observations"]["container_name"]["raw"] == "all-local-engine-stopped-container-inventories-free"


def test_systemd_exit_one_is_allowed_only_for_exact_degraded_state():
    classify = collector_helper("classify_systemd_capability")
    assert classify((1, b"degraded\n", b"", "command_failed")) == "pass"
    assert classify((1, b"", b"permission denied\n", "command_failed")) == "stop"
    assert classify((1, b"unknown\n", b"", "command_failed")) == "stop"
    assert classify((0, b"running trailing\n", b"", "success")) == "stop"


def test_phase13_bot_identity_requires_exact_inactive_disabled_state():
    classify = collector_helper("classify_phase13_bot_unit")
    success = "success"
    assert classify((0, b"inactive\n", b"", success), (0, b"disabled\n", b"", success)) == "pass"
    assert classify((0, b"active\n", b"", success), (0, b"enabled\n", b"", success)) == "stop"
    assert classify((0, b"inactive\n", b"warning\n", success), (0, b"disabled\n", b"", success)) == "stop"
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert '[SYSTEMCTL, "show", CURRENT_BOT_UNIT, "--property=ActiveState", "--value"]' in source
    assert '[SYSTEMCTL, "show", CURRENT_BOT_UNIT, "--property=UnitFileState", "--value"]' in source
    assert '["systemctl", "is-active", CURRENT_BOT_UNIT]' not in source
    assert '["systemctl", "is-enabled", CURRENT_BOT_UNIT]' not in source


def test_firewall_fallback_and_parsing_are_fail_closed():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    permission = (1, b"", b"permission denied\n", "command_failed")
    clean_nft = (0, b'{"nftables":[]}\n', b"", "success")
    malformed = (0, b"not-json\n", b"", "success")
    clean_iptables = (0, b"*filter\n:INPUT ACCEPT [0:0]\nCOMMIT\n", b"", "success")

    assert classify(clean_nft, None) == "pass"
    assert classify(unavailable, clean_iptables) == "pass"
    assert classify(permission, clean_iptables) == "stop"
    assert classify(malformed, None) == "stop"
    assert classify((0, b'{"nftables":[],"nftables":[]}\n', b"", "success"), None) == "stop"


def test_firewall_inspects_every_available_backend_without_clean_backend_masking_conflict():
    classify = collector_helper("classify_firewall")
    clean_nft = (0, b'{"nftables":[]}\n', b"", "success")
    conflict_iptables = (0, b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -p udp --dport 30002 -j ACCEPT\nCOMMIT\n", b"", "success")
    unavailable = (127, b"", b"", "unavailable")

    assert classify(clean_nft, conflict_iptables) == "stop"
    assert classify(clean_nft, unavailable, conflict_iptables) == "stop"
    assert classify(clean_nft, unavailable) == "pass"
    assert classify(unavailable, unavailable) == "stop"
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert 'command([IPTABLES_SAVE])' in source
    assert 'command([IPTABLES_LEGACY_SAVE])' in source


@pytest.mark.parametrize(
    "payload",
    [
        b"# comment only\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A MISSING -j ACCEPT\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -p arbitrary -j ACCEPT\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -j MISSING\nCOMMIT\n",
        b"*arbitrary\n:INPUT ACCEPT [0:0]\nCOMMIT\n",
        b"*filter\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -p icmp --icmp-type arbitrary -j ACCEPT\nCOMMIT\n",
    ],
)
def test_iptables_requires_declared_table_chains_and_allowlisted_values(payload: bytes):
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")

    assert classify(unavailable, (0, payload, b"", "success")) == "stop"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"nftables":[{"unknown":{"family":"inet"}}]}\n',
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"payload":{"field":"dport","protocol":"udp"}},"op":"==","right":{"range":[30000,30005]}}}],"family":"inet","table":"filter"}}]}\n',
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"payload":{"field":"saddr","protocol":"ip"}},"op":"==","right":{"prefix":{"addr":"10.212.13.128","len":25}}}}],"family":"inet","table":"filter"}}]}\n',
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"meta":{"key":"iifname"}},"op":"==","right":"amn2sp3br0"}}],"family":"inet","table":"filter"}}]}\n',
    ],
)
def test_nft_structure_ranges_interfaces_and_prefixes_fail_closed_or_conflict(payload: bytes):
    classify = collector_helper("classify_firewall")

    assert classify((0, payload, b"", "success"), None) == "stop"


def test_nft_context_parser_ignores_large_handles_but_detects_host_ip_and_unknown_nodes():
    classify = collector_helper("classify_firewall")
    clean_large_counter = b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"counter":{"bytes":999999999,"packets":777777}}],"family":"inet","handle":999999,"table":"filter"}}]}\n'
    reserved_host = b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"payload":{"field":"saddr","protocol":"ip"}},"op":"==","right":"10.212.13.42"}}],"family":"inet","handle":7,"table":"filter"}}]}\n'
    unknown_nested = b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"mystery":{"value":"clean"}}],"family":"inet","handle":7,"table":"filter"}}]}\n'

    assert classify((0, clean_large_counter, b"", "success"), (127, b"", b"", "unavailable")) == "pass"
    assert classify((0, reserved_host, b"", "success"), (127, b"", b"", "unavailable")) == "stop"
    assert classify((0, unknown_nested, b"", "success"), (127, b"", b"", "unavailable")) == "stop"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[],"family":"arbitrary","handle":7,"table":"filter"}}]}\n',
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[],"family":"inet","handle":true,"table":"filter"}}]}\n',
        b'{"nftables":[{"chain":{"family":"inet","hook":"arbitrary","name":"INPUT","table":"filter","type":"filter"}}]}\n',
    ],
)
def test_nft_context_parser_validates_allowlisted_field_types_and_values(payload: bytes):
    classify = collector_helper("classify_firewall")

    assert classify((0, payload, b"", "success"), (127, b"", b"", "unavailable")) == "stop"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"payload":{"field":"dport","protocol":"ip"}},"op":"==","right":30001}}],"family":"inet","table":"filter"}}]}\n',
        b'{"nftables":[{"rule":{"chain":"INPUT","expr":[{"match":{"left":{"payload":{"field":"saddr","protocol":"tcp"}},"op":"==","right":"192.0.2.1"}}],"family":"inet","table":"filter"}}]}\n',
    ],
)
def test_nft_payload_protocol_must_match_field_semantics(payload: bytes):
    classify = collector_helper("classify_firewall")

    assert classify((0, payload, b"", "success"), (127, b"", b"", "unavailable")) == "stop"


@pytest.mark.parametrize(
    "payload",
    [
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -p udp --dport 30000:30005 -j ACCEPT\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -s 172.29.252.8/29 -j ACCEPT\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -i amn2sp3br0 -j ACCEPT\nCOMMIT\n",
        b"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT --unknown-option value -j ACCEPT\nCOMMIT\n",
    ],
)
def test_iptables_save_ranges_networks_interfaces_and_unknown_syntax_stop(payload: bytes):
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")

    assert classify(unavailable, (0, payload, b"", "success")) == "stop"


def test_iptables_interface_prefix_semantics_detect_reserved_names():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")

    def probe(interface: str):
        return (0, f"*filter\n:INPUT ACCEPT [0:0]\n-A INPUT -i {interface} -j ACCEPT\nCOMMIT\n".encode(), b"", "success")

    assert classify(unavailable, probe("awg+")) == "stop"
    assert classify(unavailable, probe("amn2sp3+")) == "stop"
    assert classify(unavailable, probe("eth+")) == "pass"


def test_route_overlap_udp_and_firewall_outputs_require_strict_parsing():
    classify_routes = collector_helper("classify_routes")
    classify_udp = collector_helper("classify_udp_port")
    success = "success"

    assert classify_routes((0, b'[{"dst":"10.212.13.0/25"}]\n', b"", success)) == ("pass", "stop", "free")
    assert classify_routes((0, b'[{"dst":"172.29.252.8/29"}]\n', b"", success)) == ("pass", "free", "stop")
    assert classify_routes((0, b'{"dst":"default"}\n', b"", success)) == ("stop", "stop", "stop")
    assert classify_udp((0, b"UNCONN 0 0 0.0.0.0:30002 0.0.0.0:*\n", b"", success)) == "stop"
    assert classify_udp((0, b"malformed\n", b"", success)) == "stop"
    assert classify_udp((0, b"", b"", success)) == "free"
    assert classify_udp((0, b"UNCONN 0 0 0.0.0.0:70000 0.0.0.0:*\n", b"", success)) == "stop"
    assert classify_udp((0, b"UNCONN 0 0 0.0.0.0:30001 0.0.0.0:*\n", b"warning\n", success)) == "stop"
    assert classify_udp((0, b"UNCONN   0    0   0.0.0.0:30002    0.0.0.0:*\n", b"", success)) == "stop"
    assert classify_udp((0, b"UNCONN   0    0   0.0.0.0:30001    0.0.0.0:*\n", b"", success)) == "free"


@pytest.mark.parametrize(
    "payload",
    [
        b'[{"dst":"default","dst":"10.212.13.0/24"}]\n',
        b'[{"dst":"default","unknown":"value"}]\n',
        b'[{"dst":"default","metric":NaN}]\n',
        b'[{"dst":"default"}]\r\n',
        b'[{"dst":"default"}]',
    ],
)
def test_route_json_requires_duplicate_free_canonical_lf_and_allowlisted_schema(payload: bytes):
    classify = collector_helper("classify_routes")

    assert classify((0, payload, b"", "success")) == ("stop", "stop", "stop")


@pytest.mark.parametrize(
    "payload",
    [
        b'[{"dst":"default","metric":"one"}]\n',
        b'[{"dev":7,"dst":"default"}]\n',
        b'[{"dst":"default","gateway":"not-an-ip"}]\n',
        b'[{"dst":"default","scope":false}]\n',
    ],
)
def test_route_json_validates_allowlisted_field_types_and_values(payload: bytes):
    classify = collector_helper("classify_routes")

    assert classify((0, payload, b"", "success")) == ("stop", "stop", "stop")


def test_service_absence_requires_exact_stdout_and_empty_stderr():
    classify = collector_helper("classify_service_absence")
    assert classify((0, b"not-found\n", b"", "success")) == "free"
    assert classify((0, b"not-found\n", b"warning\n", "success")) == "stop"
    assert classify((0, b"not-found trailing\n", b"", "success")) == "stop"
    assert classify((1, b"not-found\n", b"", "command_failed")) == "stop"


def test_recovery_marker_scan_uses_explicit_stat_and_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    namespace = collector_python_namespace()
    scan = namespace.get("scan_recovery_markers")
    assert callable(scan), "missing explicit recovery marker scanner"

    clean = tmp_path / "clean"
    clean.mkdir()
    assert scan((clean,))[0] == "absent"

    marker = clean / "phase15-pending.marker"
    marker.write_text("synthetic", encoding="utf-8")
    assert scan((clean,))[0] == "stop"

    os_module = namespace["os"]
    monkeypatch.setattr(os_module, "scandir", lambda _path: (_ for _ in ()).throw(PermissionError()))
    assert scan((clean,))[0] == "stop"


@pytest.mark.parametrize(
    ("handshakes", "expected"),
    [
        (b"A" * 43 + b"=\t1699999940\n", "pass"),
        (b"A" * 43 + b"=\t0\n", "stop"),
        (b"A" * 43 + b"=\t1699999300\n", "stop"),
        (b"malformed\n", "stop"),
        (b"", "stop"),
    ],
)
def test_awg2_health_requires_current_container_netns_interface_and_fresh_strict_handshake(handshakes: bytes, expected: str):
    classify = collector_helper("classify_awg2_health")
    success = "success"
    container = (0, b"true|4242|0\n", b"", success)
    owner = (0, b"active\n", b"", success)
    interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success)
    peer_state = (0, handshakes, b"", success)

    assert classify(owner, container, interface, peer_state, container, owner, now_epoch=1_700_000_000) == expected


def test_awg2_health_fails_closed_on_any_probe_error():
    classify = collector_helper("classify_awg2_health")
    failed = (1, b"", b"failed", "command_failed")
    good_container = (0, b"true|4242|0\n", b"", "success")
    good_owner = (0, b"active\n", b"", "success")
    good_interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", "success")
    fresh = (0, b"A" * 43 + b"=\t1699999940\n", b"", "success")

    assert classify(failed, good_container, good_interface, fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, failed, good_interface, fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, failed, fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, good_interface, failed, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, good_interface, fresh, failed, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, good_interface, fresh, good_container, failed, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, (0, b"true|4242|0\n", b"warning\n", "success"), good_interface, fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, (0, b"7: awg0: <POINTOPOINT,UP>\n", b"warning\n", "success"), fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, good_interface, (0, fresh[1], b"warning\n", "success"), good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, (0, b"not-awg0\n", b"", "success"), fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, good_container, good_interface, (0, fresh[1].rstrip(b"\n"), b"", "success"), good_container, good_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(good_owner, (0, b"false|0|0\n", b"", "success"), good_interface, fresh, good_container, good_owner, now_epoch=1_700_000_000) == "stop"


@pytest.mark.parametrize("owner", [b"inactive\n", b"failed\n", b"unknown\n", b"active\r\n"])
def test_awg2_health_requires_exact_active_phase13_docker_owner_unit(owner: bytes):
    classify = collector_helper("classify_awg2_health")
    success = "success"
    assert classify(
        (0, owner, b"", success),
        (0, b"true|4242|0\n", b"", success),
        (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success),
        (0, b"A" * 43 + b"=\t1699999940\n", b"", success),
        (0, b"true|4242|0\n", b"", success),
        (0, b"active\n", b"", success),
        now_epoch=1_700_000_000,
    ) == "stop"

    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert 'CURRENT_AWG2_OWNER_UNIT = "amn2-spain-docker.service"' in source
    assert source.count('[SYSTEMCTL, "show", CURRENT_AWG2_OWNER_UNIT, "--property=ActiveState", "--value"]') == 2


@pytest.mark.parametrize("after", [b"true|4243|0\n", b"true|4242|1\n", b"false|4242|0\n"])
def test_awg2_health_rejects_pid_restart_or_running_state_race(after: bytes):
    classify = collector_helper("classify_awg2_health")
    success = "success"
    before = (0, b"true|4242|0\n", b"", success)
    interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success)
    handshakes = (0, b"A" * 43 + b"=\t1699999940\n", b"", success)

    owner = (0, b"active\n", b"", success)
    assert classify(owner, before, interface, handshakes, (0, after, b"", success), owner, now_epoch=1_700_000_000) == "stop"
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert source.count('"{{.State.Running}}|{{.State.Pid}}|{{.RestartCount}}"') == 2


def run_powershell(body: str):
    require_file(RUNNER, "runner")
    harness = f". '{RUNNER}'\n{body}"
    return subprocess.run(
        [
            str(POWERSHELL),
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            harness,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_runner_rejects_missing_future_claim_before_any_acceptance():
    result = run_powershell(
        "$claim = Read-Phase15FutureClaim -ClaimPath 'Z:\\missing-phase15-claim.json'; "
        "$ok = $null -ne $claim -and (Test-Phase15FutureClaim -Claim $claim "
        f"-ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{'a' * 64}' "
        f"-ExpectedCollectorSha256 '{'b' * 64}' -ExpectedHost 'spain.test.invalid'); "
        "[Console]::Out.Write($ok.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_validates_claim_lifetime_against_fresh_pre_reservation_time(tmp_path: Path):
    claim_path = valid_runner_claim(
        tmp_path,
        issued_at="2026-08-16T00:00:00Z",
        expires_at="2026-08-16T00:10:00Z",
    )
    escaped = str(claim_path).replace("'", "''")
    result = run_powershell(
        f"$claim = Read-Phase15FutureClaim -ClaimPath '{escaped}'; "
        f"$atIssued = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -At '2026-08-16T00:00:00Z'; "
        f"$before = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -At '2026-08-15T23:59:59Z'; "
        f"$expired = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -At '2026-08-16T00:10:00Z'; "
        "[Console]::Out.Write(\"$($atIssued.ToString().ToLowerInvariant())|$($before.ToString().ToLowerInvariant())|$($expired.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    lifetime_checks = [match.start() for match in re.finditer("Test-Phase15FutureClaim", main)]
    launch = source[source.index("function Start-Phase15AuthorizedSshProcess") : source.index("function Invoke-Phase15OneSshTransport")]
    assert len(lifetime_checks) == 2
    assert main.index("$startedAt =") < main.index("Read-Phase15ManifestArtifact")
    assert main.index("Test-Phase15ClaimIdentity") < lifetime_checks[0] < main.index("Initialize-Phase15ProductionStateRoot")
    assert main.index("Reconcile-Phase15Transaction") < main.index("$reservationAt =")
    assert main.index("$reservationAt =") < lifetime_checks[1]
    assert launch.index("Test-Phase15FutureClaim") < launch.index("$Process.Start()")
    assert "-At $startedAt" not in main
    assert "-At $reservationAt" in main
    assert "-ReservedAt $reservationAt" in main


def valid_runner_claim(tmp_path: Path, **overrides: object) -> Path:
    claim = {
        "claim_id": "phase15-preflight-test-001",
        "collector_sha256": "b" * 64,
        "consumed_at": None,
        "expected_host": "spain.test.invalid",
        "expires_at": "2099-08-11T12:00:00Z",
        "future_gate": "PREFLIGHT",
        "issued_at": "2025-08-11T11:00:00Z",
        "manifest_sha256": "a" * 64,
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase15.readonly-preflight-claim.v1",
        "status": "issued",
    }
    claim.update(overrides)
    path = tmp_path / "claim.json"
    path.write_bytes((json.dumps(claim, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    return path


def test_runner_acceptance_requires_package_collector_host_and_schema_binding(tmp_path: Path):
    claim = valid_runner_claim(tmp_path)
    claim_path = str(claim).replace("'", "''")
    result = run_powershell(
        f"$claim = Read-Phase15FutureClaim -ClaimPath '{claim_path}'; "
        f"$valid = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{'a' * 64}' -ExpectedCollectorSha256 '{'b' * 64}' "
        "-ExpectedHost 'spain.test.invalid'; "
        f"$wrongHost = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{'a' * 64}' -ExpectedCollectorSha256 '{'b' * 64}' "
        "-ExpectedHost 'other.test.invalid'; "
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$($wrongHost.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false"


@pytest.mark.parametrize(
    "host",
    [
        "-oProxyCommand=bad",
        "user@spain.test.invalid",
        "spain.test.invalid;touch-bad",
        "Spain.test.invalid",
        "spain..test.invalid",
        "spain_test.invalid",
        "127.0.0.1 -v",
    ],
)
def test_runner_rejects_unsafe_expected_host_grammar(host: str):
    encoded = base64.b64encode(host.encode()).decode()
    result = run_powershell(
        f"$hostValue = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')); "
        "$valid = Test-Phase15ExpectedHost -ExpectedHost $hostValue; "
        "[Console]::Out.Write($valid.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_rejects_future_issued_or_noncanonical_claim(tmp_path: Path):
    future = valid_runner_claim(tmp_path, issued_at="2098-08-11T11:00:00Z")
    future_path = str(future).replace("'", "''")
    pretty = tmp_path / "pretty.json"
    pretty_value = json.loads(future.read_text())
    pretty_value["issued_at"] = "2025-08-11T11:00:00Z"
    pretty.write_text(json.dumps(pretty_value, indent=2) + "\n", encoding="utf-8")
    pretty_path = str(pretty).replace("'", "''")
    call = (
        f"-ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{'a' * 64}' "
        f"-ExpectedCollectorSha256 '{'b' * 64}' -ExpectedHost 'spain.test.invalid'"
    )
    result = run_powershell(
        f"$futureClaim = Read-Phase15FutureClaim -ClaimPath '{future_path}'; "
        f"$prettyClaim = Read-Phase15FutureClaim -ClaimPath '{pretty_path}'; "
        f"$future = $null -ne $futureClaim -and (Test-Phase15FutureClaim -Claim $futureClaim {call}); "
        f"$pretty = $null -ne $prettyClaim -and (Test-Phase15FutureClaim -Claim $prettyClaim {call}); "
        "[Console]::Out.Write(\"$($future.ToString().ToLowerInvariant())|$($pretty.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false|false"


def test_runner_validates_one_immutable_claim_object_after_single_canonical_read(tmp_path: Path):
    claim = valid_runner_claim(tmp_path)
    claim_path = str(claim).replace("'", "''")
    invalid = base64.b64encode(b'{"schema":"replaced-after-read"}\n').decode()
    result = run_powershell(
        f"$claim = Read-Phase15FutureClaim -ClaimPath '{claim_path}'; "
        f"[IO.File]::WriteAllBytes('{claim_path}', [Convert]::FromBase64String('{invalid}')); "
        f"$valid = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' "
        "-ExpectedHost 'spain.test.invalid'; "
        "[Console]::Out.Write($valid.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    assert main.count("Read-Phase15FutureClaim -ClaimPath $FutureClaimPath") == 1
    assert "ConvertFrom-Phase15CanonicalJsonFile -Path $FutureClaimPath" not in main


@pytest.mark.parametrize(
    "field",
    [
        "schema",
        "package_id",
        "manifest_sha256",
        "collector_sha256",
        "expected_host",
        "claim_id",
        "future_gate",
        "status",
        "issued_at",
        "expires_at",
    ],
)
def test_runner_rejects_singleton_array_claim_scalars(tmp_path: Path, field: str):
    claim_path = valid_runner_claim(tmp_path)
    value = json.loads(claim_path.read_text(encoding="utf-8"))
    canonical_scalar = {
        "schema": "amn2.phase15.readonly-preflight-claim.v1",
        "package_id": PACKAGE_ID,
        "manifest_sha256": MANIFEST_SHA256,
        "collector_sha256": COLLECTOR_SHA256,
        "expected_host": "spain.test.invalid",
        "claim_id": "phase15-preflight-test-001",
        "future_gate": "PREFLIGHT",
        "status": "issued",
        "issued_at": "2025-08-11T11:00:00Z",
        "expires_at": "2099-08-11T12:00:00Z",
    }[field]
    value[field] = [canonical_scalar]
    claim_path.write_bytes((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
    escaped = str(claim_path).replace("'", "''")
    result = run_powershell(
        f"$claim = Read-Phase15FutureClaim -ClaimPath '{escaped}'; "
        f"$valid = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' "
        f"-ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' "
        "-ExpectedHost 'spain.test.invalid'; "
        "[Console]::Out.Write($valid.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_builds_positional_remote_envelope_with_safe_option_boundary():
    result = run_powershell(
        f"$arguments = New-Phase15SshArguments -ExpectedHost 'spain.test.invalid' -ClaimId 'phase15-preflight-test-001' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}'; "
        "[Console]::Out.Write(($arguments | ConvertTo-Json -Compress))"
    )

    assert result.returncode == 0, result.stderr
    arguments = json.loads(result.stdout)
    assert arguments[-3:] == [
        "--",
        "root@spain.test.invalid",
        f"/usr/bin/bash -s -- '{PACKAGE_ID}' '{MANIFEST_SHA256}' '{COLLECTOR_SHA256}' 'phase15-preflight-test-001' 'spain.test.invalid'",
    ]
    assert "$start.Environment['AMN2_PHASE15_" not in require_file(RUNNER, "runner").read_text(encoding="utf-8")


def test_runner_hashes_and_transports_one_immutable_collector_byte_array(tmp_path: Path):
    artifact_path = tmp_path / "collector.sh"
    original = b"#!/bin/sh\nprintf immutable\n"
    artifact_path.write_bytes(original)
    escaped = str(artifact_path).replace("'", "''")
    replacement = base64.b64encode(b"replaced-after-read\n").decode()
    result = run_powershell(
        f"$artifact = Read-Phase15CollectorArtifact -Path '{escaped}'; "
        f"[IO.File]::WriteAllBytes('{escaped}', [Convert]::FromBase64String('{replacement}')); "
        "[Console]::Out.Write(\"$($artifact.Sha256)|$([Convert]::ToBase64String($artifact.Bytes))\")"
    )

    assert result.returncode == 0, result.stderr
    digest, encoded = result.stdout.split("|", 1)
    assert digest == hashlib.sha256(original).hexdigest()
    assert base64.b64decode(encoded) == original
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    artifact_reader = source[source.index("function Read-Phase15CollectorArtifact") : source.index("function ConvertTo-Phase15CanonicalJsonText")]
    assert artifact_reader.count("Read-Phase15BoundedFileBytes -Path $Path") == 1
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    assert main.count("Read-Phase15CollectorArtifact -Path $collectorPath") == 1
    assert "Get-Phase15FileSha256 -Path $collectorPath" not in main
    assert "ReadAllBytes($collectorPath)" not in main


def test_runner_canonical_parses_and_hashes_one_immutable_manifest_byte_array(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    original_value = {"entries": [], "package_id": PACKAGE_ID}
    original = (json.dumps(original_value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    manifest_path.write_bytes(original)
    escaped = str(manifest_path).replace("'", "''")
    replacement = base64.b64encode(b'{"package_id":"replaced-after-read"}\n').decode()
    result = run_powershell(
        f"$artifact = Read-Phase15ManifestArtifact -Path '{escaped}'; "
        f"[IO.File]::WriteAllBytes('{escaped}', [Convert]::FromBase64String('{replacement}')); "
        "[Console]::Out.Write(\"$($artifact.Sha256)|$($artifact.Value.package_id)|$([Convert]::ToBase64String($artifact.Bytes))\")"
    )

    assert result.returncode == 0, result.stderr
    digest, package_id, encoded = result.stdout.split("|", 2)
    assert digest == hashlib.sha256(original).hexdigest()
    assert package_id == PACKAGE_ID
    assert base64.b64decode(encoded) == original
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    reader = source[source.index("function Read-Phase15ManifestArtifact") : source.index("function Read-Phase15CollectorArtifact")]
    assert reader.count("Read-Phase15BoundedFileBytes -Path $Path") == 1
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    assert main.count("Read-Phase15ManifestArtifact -Path $manifestPath") == 1
    assert "ConvertFrom-Phase15CanonicalJsonFile -Path $manifestPath" not in main
    assert "Get-Phase15FileSha256 -Path $manifestPath" not in main


def test_transport_success_requires_empty_stderr_and_bounded_io_starts_before_stdin():
    result = run_powershell(
        "$clean = Test-Phase15TransportCompletion -ExitCode 0 -StderrLength 0; "
        "$stderr = Test-Phase15TransportCompletion -ExitCode 0 -StderrLength 1; "
        "$failed = Test-Phase15TransportCompletion -ExitCode 1 -StderrLength 0; "
        "[Console]::Out.Write(\"$($clean.ToString().ToLowerInvariant())|$($stderr.ToString().ToLowerInvariant())|$($failed.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    transport = source[source.index("function Invoke-Phase15OneSshTransport") : source.index("function Write-Phase15CreateNewJson")]
    assert transport.index("$clock = [Diagnostics.Stopwatch]::StartNew()") < transport.index("WriteAsync")
    assert transport.index("StandardOutput.BaseStream.ReadAsync") < transport.index("WriteAsync")
    assert transport.index("StandardError.BaseStream.ReadAsync") < transport.index("WriteAsync")
    assert "[ref]$Started" in transport
    assert transport.index("$Started.Value = $true") > transport.index("Start-Phase15AuthorizedSshProcess")


def test_transport_abort_kills_alive_child_and_waits_bounded_before_dispose():
    result = run_powershell(
        "$script:killed = $false; $script:waited = 0; "
        "$process = [pscustomobject]@{HasExited=$false}; "
        "$process | Add-Member -MemberType ScriptMethod -Name Kill -Value {$script:killed=$true; $this.HasExited=$true}; "
        "$process | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value {param($milliseconds) $script:waited=$milliseconds; return $true}; "
        "Stop-Phase15TransportProcess -Process $process -WaitMilliseconds 2000; "
        "[Console]::Out.Write(\"$($script:killed.ToString().ToLowerInvariant())|$script:waited\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|2000"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    transport = source[source.index("function Invoke-Phase15OneSshTransport") : source.index("function Write-Phase15CreateNewJson")]
    assert "catch {" in transport
    assert "Stop-Phase15TransportProcess -Process $process" in transport
    assert transport.index("Stop-Phase15TransportProcess -Process $process") < transport.index("$process.Dispose()")


def valid_collector_document(*, stopped: bool = False) -> dict[str, object]:
    observations = [
        {
            "name": name,
            "observation_sha256": hashlib.sha256(name.encode()).hexdigest(),
            "state": "stop" if stopped and name == "udp_30002" else ("free" if name in {"interface_awg3", "bridge_amn2sp3br0", "udp_30002", "vpn_cidr_10_212_13_0_24", "container_cidr_172_29_252_0_28", "container_name", "service_name", "config_path", "state_root"} else "pass"),
        }
        for name in sorted(EXPECTED_OBSERVATIONS)
    ]
    return {
        "blocking_reasons": ["resource_conflict"] if stopped else [],
        "claim_id": "phase15-preflight-test-001",
        "collector_sha256": COLLECTOR_SHA256,
        "decision": "stop" if stopped else "pass",
        "host_identity": "spain.test.invalid",
        "manifest_sha256": MANIFEST_SHA256,
        "observed_at": "2026-08-16T00:00:00Z",
        "observations": observations,
        "package_id": PACKAGE_ID,
        "safety": {
            "live_mutation": False,
            "raw_output_persisted": False,
            "remote_file_written": False,
        },
        "schema": "amn2.phase15.spain-readonly-collector.v1",
    }


def runner_document_result(document: dict[str, object], expression: str):
    encoded = base64.b64encode(json.dumps(document, separators=(",", ":")).encode()).decode()
    return run_powershell(
        f"$document = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')) | ConvertFrom-Json; {expression}"
    )


def test_runner_collector_validation_is_exact_and_reconstructs_allowlisted_canonical_evidence():
    document = valid_collector_document()
    result = runner_document_result(
        document,
        f"$valid = Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' -ExpectedClaimId 'phase15-preflight-test-001' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -StartedAt '2026-08-15T23:59:59Z' -EndedAt '2026-08-16T00:00:01Z'; "
        "$evidence = ConvertTo-Phase15Evidence -Document $document -ManifestSha256 ('a' * 64) -CollectorSha256 ('b' * 64) -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:01Z' -EndedAt '2026-08-16T00:00:02Z'; "
        "$json = ConvertTo-Phase15CanonicalJsonText -Value $evidence; "
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$json\")",
    )

    assert result.returncode == 0, result.stderr
    valid, rendered = result.stdout.split("|", 1)
    assert valid == "true"
    evidence = json.loads(rendered)
    assert list(evidence) == sorted(evidence)
    assert list(evidence["safety"]) == sorted(evidence["safety"])
    assert all(list(item) == ["name", "observation_sha256", "state"] for item in evidence["observations"])
    assert evidence["observations"] == document["observations"]
    assert "observed_at" not in evidence
    assert "claim_id" not in evidence


@pytest.mark.parametrize("observed_at", ["2026-08-15T23:59:58Z", "2026-08-16T00:00:02Z"])
def test_runner_binds_remote_observed_at_to_local_execution_window(observed_at: str):
    document = valid_collector_document()
    document["observed_at"] = observed_at
    result = runner_document_result(
        document,
        f"$valid = Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' -ExpectedClaimId 'phase15-preflight-test-001' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -StartedAt '2026-08-15T23:59:59Z' -EndedAt '2026-08-16T00:00:01Z'; [Console]::Out.Write($valid.ToString().ToLowerInvariant())",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


@pytest.mark.parametrize(
    "mutation",
    [
        "extra_top_level",
        "extra_safety",
        "unknown_reason",
        "unknown_observation",
        "unsorted_observations",
        "decision_mismatch",
        "reason_mismatch",
        "scalar_reasons",
        "numeric_safety",
        "scalar_observations",
        "numeric_decision",
        "numeric_reason",
        "numeric_name",
        "numeric_state",
        "manifest_mismatch",
        "collector_mismatch",
        "array_schema",
        "array_package_id",
        "array_manifest_sha256",
        "array_collector_sha256",
        "array_host_identity",
        "array_claim_id",
        "array_observed_at",
        "array_decision",
    ],
)
def test_runner_rejects_non_schema_equivalent_collector_documents(mutation: str):
    document = valid_collector_document(stopped=True)
    if mutation == "extra_top_level":
        document["raw"] = "not-allowed"
    elif mutation == "extra_safety":
        document["safety"]["ssh_used"] = False
    elif mutation == "unknown_reason":
        document["blocking_reasons"] = ["arbitrary_reason"]
    elif mutation == "unknown_observation":
        document["observations"][0]["name"] = "Bearer synthetic-sensitive-value"
    elif mutation == "unsorted_observations":
        document["observations"] = list(reversed(document["observations"]))
    elif mutation == "decision_mismatch":
        document["decision"] = "pass"
    elif mutation == "reason_mismatch":
        document["blocking_reasons"] = ["observation_failed"]
    elif mutation == "scalar_reasons":
        document["blocking_reasons"] = "resource_conflict"
    elif mutation == "numeric_safety":
        document["safety"]["live_mutation"] = 0
    elif mutation == "scalar_observations":
        document["observations"] = document["observations"][0]
    elif mutation == "numeric_decision":
        document["decision"] = 0
    elif mutation == "numeric_reason":
        document["blocking_reasons"] = [1]
    elif mutation == "numeric_name":
        document["observations"][0]["name"] = 1
    elif mutation == "numeric_state":
        document["observations"][0]["state"] = 1
    elif mutation == "manifest_mismatch":
        document["manifest_sha256"] = "c" * 64
    elif mutation == "collector_mismatch":
        document["collector_sha256"] = "d" * 64
    elif mutation.startswith("array_"):
        field = mutation.removeprefix("array_")
        document[field] = [document[field]]
    result = runner_document_result(
        document,
        f"$valid = Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' -ExpectedClaimId 'phase15-preflight-test-001' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -StartedAt '2026-08-15T23:59:59Z' -EndedAt '2026-08-16T00:00:01Z'; [Console]::Out.Write($valid.ToString().ToLowerInvariant())",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_runner_requires_canonical_collector_json_bytes():
    document = valid_collector_document()
    canonical = (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()
    pretty = (json.dumps(document, indent=2) + "\n").encode()
    canonical_encoded = base64.b64encode(canonical).decode()
    pretty_encoded = base64.b64encode(pretty).decode()
    result = run_powershell(
        f"$canonical = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{canonical_encoded}')); "
        f"$pretty = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{pretty_encoded}')); "
        "$accepted = $null -ne (ConvertFrom-Phase15CanonicalJsonText -Text $canonical); "
        "$rejected = $null -eq (ConvertFrom-Phase15CanonicalJsonText -Text $pretty); "
        "[Console]::Out.Write(\"$($accepted.ToString().ToLowerInvariant())|$($rejected.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true"


def test_runner_claim_reservation_is_create_new_and_terminal_transition_is_canonical(tmp_path: Path):
    claim = valid_runner_claim(tmp_path)
    renamed = tmp_path / "renamed-claim.json"
    renamed.write_bytes(claim.read_bytes())
    renamed_path = str(renamed).replace("'", "''")
    lifecycle_root = str(tmp_path / "lifecycle").replace("'", "''")
    result = run_powershell(
        f"$null = [IO.Directory]::CreateDirectory('{lifecycle_root}'); "
        f"$lifecycle = Reserve-Phase15Claim -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        f"$replayed = $false; try {{ Reserve-Phase15Claim -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:01Z' }} catch {{ $replayed = $true }}; "
        f"$renamedClaim = Read-Phase15FutureClaim -ClaimPath '{renamed_path}'; "
        f"$renamedAccepted = Test-Phase15FutureClaim -Claim $renamedClaim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid'; "
        "$reserved = [IO.File]::ReadAllText($lifecycle); "
        "$null = Set-Phase15ClaimTerminal -LifecyclePath $lifecycle -ClaimId 'phase15-preflight-test-001' -Status 'completed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'not_applicable'; "
        "$terminal = [IO.File]::ReadAllText($lifecycle); "
        "[Console]::Out.Write(\"$($replayed.ToString().ToLowerInvariant())|$($renamedAccepted.ToString().ToLowerInvariant())|$lifecycle|$reserved|$terminal\")"
    )

    assert result.returncode == 0, result.stderr
    replayed, renamed_accepted, lifecycle_path, reserved_raw, terminal_raw = result.stdout.split("|", 4)
    assert replayed == "true"
    assert renamed_accepted == "true"
    assert Path(lifecycle_path).parent == tmp_path / "lifecycle"
    assert Path(lifecycle_path).name == "phase15-preflight-test-001.json"
    reserved = json.loads(reserved_raw)
    terminal = json.loads(terminal_raw)
    assert list(reserved) == sorted(reserved)
    assert reserved["status"] == "reserved"
    assert terminal["status"] == "completed"
    assert terminal["reason_code"] == "not_applicable"
    assert claim.read_text(encoding="utf-8") == json.dumps(json.loads(claim.read_text()), sort_keys=True, separators=(",", ":")) + "\n"


def test_lifecycle_paths_are_collision_safe_and_claim_id_scoped(tmp_path: Path):
    lifecycle_root = str(tmp_path / "lifecycle").replace("'", "''")
    result = run_powershell(
        f"$first = Get-Phase15LifecyclePath -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$second = Get-Phase15LifecyclePath -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-002'; "
        "[Console]::Out.Write(\"$first|$second\")"
    )

    assert result.returncode == 0, result.stderr
    first, second = map(Path, result.stdout.split("|", 1))
    assert first != second
    assert first.parent == second.parent == tmp_path / "lifecycle"
    assert {first.name, second.name} == {"phase15-preflight-test-001.json", "phase15-preflight-test-002.json"}


def test_production_lifecycle_root_is_stable_and_not_derived_from_user_paths(tmp_path: Path):
    first_cwd = str(tmp_path).replace("'", "''")
    second_cwd = str(tmp_path / "other").replace("'", "''")
    result = run_powershell(
        f"$null = [IO.Directory]::CreateDirectory('{second_cwd}'); "
        f"Set-Location '{first_cwd}'; $first = Get-Phase15ProductionStateRoot; "
        f"Set-Location '{second_cwd}'; $second = Get-Phase15ProductionStateRoot; "
        "[Console]::Out.Write(\"$first|$second\")"
    )

    assert result.returncode == 0, result.stderr
    first, second = result.stdout.split("|", 1)
    assert first == second == r"C:\ProgramData\AMN2\phase15\readonly-preflight"


def test_claim_lock_is_exclusive_for_whole_transaction_and_contender_cannot_reconcile(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$owner = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $owner; "
        "$before = [IO.File]::ReadAllBytes($tx.JournalPath); $message = ''; "
        f"try {{ $null = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' }} catch {{ $message = $_.Exception.Message }}; "
        "$after = [IO.File]::ReadAllBytes($tx.JournalPath); "
        "$same = [Convert]::ToBase64String($before) -ceq [Convert]::ToBase64String($after); "
        "$owner.Stream.Dispose(); "
        f"$next = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; $next.Stream.Dispose(); "
        "[Console]::Out.Write(\"$message|$($same.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "claim_replay|true"


def test_journal_durable_writer_surfaces_mid_write_failure_before_flush():
    result = run_powershell(
        "$script:count = 0; $script:flushed = $false; "
        "$stream = [pscustomobject]@{}; "
        "$stream | Add-Member -MemberType ScriptMethod -Name WriteByte -Value {param($value) if ($script:count -eq 3) { throw 'synthetic_write_failure' }; $script:count++}; "
        "$stream | Add-Member -MemberType ScriptMethod -Name Flush -Value {param($durable) $script:flushed = $true}; "
        "$message = ''; try { Write-Phase15DurableBytes -Stream $stream -Bytes ([byte[]](1,2,3,4,5)) } catch { $message = $_.Exception.Message }; "
        "[Console]::Out.Write(\"$message|$script:count|$($script:flushed.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert "synthetic_write_failure" in result.stdout
    assert result.stdout.endswith("|3|false")


def test_initial_journal_publish_is_atomic_and_cleans_stale_owned_temp(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$transactionRoot = Join-Path '{state_root}' 'transactions'; $null = [IO.Directory]::CreateDirectory($transactionRoot); "
        f"$journalPath = Get-Phase15TransactionPath -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        "$stale = $journalPath + '.phase15-phase15-preflight-test-001.create-deadbeefdeadbeefdeadbeefdeadbeef.tmp'; [IO.File]::WriteAllBytes($stale, [byte[]](1,2,3)); "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$journal = ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath; $staleGone = -not (Test-Path -LiteralPath $stale); $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($staleGone.ToString().ToLowerInvariant())|$($journal.phase)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|owned"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    durable = source[source.index("function Write-Phase15DurableBytes") : source.index("function Write-Phase15AtomicCreateNewJson")]
    atomic = source[source.index("function Write-Phase15AtomicCreateNewJson") : source.index("function Write-Phase15AtomicJson")]
    assert "Flush($true)" in durable
    assert "Write-Phase15DurableBytes -Stream $stream -Bytes $bytes" in atomic
    assert "[IO.File]::Move($temporaryPath, $fullPath)" in atomic
    starter = source[source.index("function Start-Phase15Transaction") : source.index("function Set-Phase15TransactionPhase")]
    assert "Write-Phase15AtomicCreateNewJson -Path $journalPath -Value $journal" in starter


def test_atomic_journal_publish_never_overwrites_existing_final_and_cleans_temp(tmp_path: Path):
    journal_path = tmp_path / "transaction.json"
    original = b'{"owner":"existing"}\n'
    journal_path.write_bytes(original)
    escaped = str(journal_path).replace("'", "''")
    result = run_powershell(
        f"$failed = $false; try {{ Write-Phase15AtomicCreateNewJson -Path '{escaped}' -Value ([ordered]@{{owner='contender'}}) -OwnerId 'phase15-preflight-test-001' }} catch {{ $failed = $true }}; "
        f"$bytes = [IO.File]::ReadAllBytes('{escaped}'); $temps = @([IO.Directory]::GetFiles((Split-Path -Parent '{escaped}'), 'transaction.json.phase15-phase15-preflight-test-001.create-*.tmp')); "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$([Convert]::ToBase64String($bytes))|$($temps.Count)\")"
    )

    assert result.returncode == 0, result.stderr
    failed, encoded, temp_count = result.stdout.split("|", 2)
    assert failed == "true"
    assert base64.b64decode(encoded) == original
    assert temp_count == "0"


def test_outcome_slot_is_atomically_reserved_and_claim_owned(tmp_path: Path):
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$reservation = Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        "$secondRejected = $false; try { "
        f"Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-002' -ReservedAt '2026-08-16T00:00:01Z' "
        "} catch { $secondRejected = $true }; "
        "$firstOwner = Test-Phase15OutcomeOwnership -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        "$secondOwner = Test-Phase15OutcomeOwnership -ReservationPath $reservation -ClaimId 'phase15-preflight-test-002'; "
        "Release-Phase15OutcomeSlot -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        "$residue = Test-Path -LiteralPath $reservation; "
        "[Console]::Out.Write(\"$($secondRejected.ToString().ToLowerInvariant())|$($firstOwner.ToString().ToLowerInvariant())|$($secondOwner.ToString().ToLowerInvariant())|$($residue.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|false|false"


def test_runner_reserves_claim_before_transport_and_has_terminal_failure_path():
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    publisher = source[source.index("function Publish-Phase15TerminalOutcome") : source.index("function New-Phase15FailureOutcome")]

    assert main.index("Start-Phase15Transaction") < main.index("Invoke-Phase15OneSshTransport")
    assert "Publish-Phase15TerminalOutcome" in main
    assert "$pendingPath = [IO.Path]::GetFullPath($OutcomePath) + '.phase15-' + $ClaimId + '.staged'" in publisher
    assert "$pendingPath = [string]$journal.staged_path" not in publisher
    assert publisher.index("Test-Phase15ExactNonterminalTransactionJournal") < publisher.index("$journal.terminal_ended_at = $EndedAt")
    assert publisher.index("Set-Phase15ClaimTerminal") < publisher.index("[IO.File]::Replace")
    assert "amn2.phase15.readonly-preflight-failure.v1" in source


def test_runner_reconciles_before_atomic_transaction_ownership_and_transport():
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]
    lifetime_checks = [match.start() for match in re.finditer("Test-Phase15FutureClaim", main)]
    launch = source[source.index("function Start-Phase15AuthorizedSshProcess") : source.index("function Invoke-Phase15OneSshTransport")]

    assert len(lifetime_checks) == 2
    assert main.index("Test-Phase15ClaimIdentity") < lifetime_checks[0] < main.index("Initialize-Phase15ProductionStateRoot")
    assert main.index("Enter-Phase15ClaimLock") < main.index("Reconcile-Phase15Transaction")
    assert main.index("Reconcile-Phase15Transaction") < lifetime_checks[1]
    assert lifetime_checks[1] < main.index("Start-Phase15Transaction")
    assert launch.index("Test-Phase15FutureClaim") < launch.index("$Process.Start()")
    assert main.index("Start-Phase15Transaction") < main.index("Invoke-Phase15OneSshTransport")
    assert "-TransactionPath $transaction.JournalPath" in main
    assert "$transaction.OutcomeLock.Stream.Dispose()" in main
    assert "$claimLock.Stream.Dispose()" in main


@pytest.mark.parametrize(
    "crash_point",
    ["owned", "terminal_lifecycle", "orphan_outcome"],
)
def test_interrupted_transaction_reconciles_to_one_sanitized_terminal_failure(tmp_path: Path, crash_point: str):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    setup = ""
    if crash_point == "terminal_lifecycle":
        setup = (
            "$null = Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath "
            "-ClaimId 'phase15-preflight-test-001' -Status 'completed' "
            "-EndedAt '2026-08-16T00:00:01Z' -ReasonCode 'not_applicable'; "
        )
    elif crash_point == "orphan_outcome":
        setup = (
            "[IO.File]::Delete($tx.LifecyclePath); "
            "[IO.File]::WriteAllText($tx.ReservationPath, '{\"decision\":\"pass\",\"schema\":\"synthetic\"}' + \"`n\", [Text.UTF8Encoding]::new($false)); "
        )
    result = run_powershell(
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' "
        f"-ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' "
        f"-ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        f"{setup}"
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock; "
        "$lifecycle = ConvertFrom-Phase15CanonicalJsonFile -Path $tx.LifecyclePath; "
        "$published = ConvertFrom-Phase15CanonicalJsonFile -Path $reconciled.OutcomePath; "
        "$originalRaw = if (Test-Path -LiteralPath $tx.ReservationPath) { [IO.File]::ReadAllText($tx.ReservationPath) } else { '' }; "
        "$journalExists = Test-Path -LiteralPath $tx.JournalPath; "
        "$owned = Test-Phase15OutcomeOwnership -ReservationPath $tx.ReservationPath -ClaimId 'phase15-preflight-test-001'; "
        "$lock.Stream.Dispose(); "
        "[Console]::Out.Write((@{journal_exists=$journalExists;lifecycle=$lifecycle;original_raw=$originalRaw;outcome=$published;outcome_path=$reconciled.OutcomePath;owned=$owned;reconciled=$reconciled.Recovered} | ConvertTo-Json -Compress -Depth 10))"
    )

    assert result.returncode == 0, result.stderr
    state = json.loads(result.stdout)
    assert state["reconciled"] is True
    assert state["journal_exists"] is False
    assert state["owned"] is False
    assert state["lifecycle"]["status"] == "failed"
    assert state["lifecycle"]["reason_code"] == "transport_failed"
    assert state["outcome"]["schema"] == "amn2.phase15.readonly-preflight-failure.v1"
    assert state["outcome"]["decision"] == "stop"
    assert state["outcome"]["reason_code"] == "transport_failed"
    assert state["outcome"]["safety"] == {
        "live_mutation": False,
        "raw_output_persisted": False,
        "remote_file_written": False,
        "ssh_used": False,
    }
    if crash_point == "orphan_outcome":
        assert Path(state["outcome_path"]) != tmp_path / "outcome.json"
        assert state["original_raw"] == '{"decision":"pass","schema":"synthetic"}\n'
    else:
        assert Path(state["outcome_path"]) == tmp_path / "outcome.json"


@pytest.mark.parametrize(
    ("phase", "ssh_used"),
    [
        ("owned", False),
        ("transport_attempted", True),
        ("ssh_started", True),
        ("outcome_staged", True),
        ("finalizing", True),
    ],
)
def test_recovery_safety_is_conservative_for_every_persisted_crash_phase(tmp_path: Path, phase: str, ssh_used: bool):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        + (
            f"$null = Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase '{phase}' -Lock $lock; "
            if phase != "owned"
            else ""
        )
        + f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock; "
        "$failure = ConvertFrom-Phase15CanonicalJsonFile -Path $reconciled.OutcomePath; $lock.Stream.Dispose(); "
        "[Console]::Out.Write($failure.safety.ssh_used.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == str(ssh_used).lower()


def test_recovery_never_overwrites_another_claim_outcome_owner(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "[IO.File]::Delete($tx.ReservationPath); "
        f"$null = Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-002' -ReservedAt '2026-08-16T00:00:01Z'; "
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock; "
        "$otherStillOwns = Test-Phase15OutcomeOwnership -ReservationPath $tx.ReservationPath -ClaimId 'phase15-preflight-test-002'; "
        "$failure = ConvertFrom-Phase15CanonicalJsonFile -Path $reconciled.OutcomePath; $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($otherStillOwns.ToString().ToLowerInvariant())|$($reconciled.OutcomePath)|$($failure.reason_code)\")"
    )

    assert result.returncode == 0, result.stderr
    still_owned, recovery_path, reason = result.stdout.split("|", 2)
    assert still_owned == "true"
    assert Path(recovery_path) != tmp_path / "outcome.json"
    assert reason == "transport_failed"


def test_expired_claim_identity_can_recover_prior_transport_but_cannot_start_new_transport(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    claim_path = valid_runner_claim(tmp_path, issued_at="2026-08-16T00:00:00Z", expires_at="2026-08-16T00:01:00Z")
    escaped_claim = str(claim_path).replace("'", "''")
    result = run_powershell(
        f"$claim = Read-Phase15FutureClaim -ClaimPath '{escaped_claim}'; "
        f"$identity = Test-Phase15ClaimIdentity -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid'; "
        f"$current = Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId '{PACKAGE_ID}' -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -At '2026-08-16T00:02:00Z'; "
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId $claim.claim_id; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId $claim.claim_id -ReservedAt '2026-08-16T00:00:30Z' "
        f"-ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$null = Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claim.claim_id -Phase 'transport_attempted' -Lock $lock; "
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId $claim.claim_id -EndedAt '2026-08-16T00:02:00Z' -Lock $lock -OutcomeLock $tx.OutcomeLock; "
        "$failure = ConvertFrom-Phase15CanonicalJsonFile -Path $reconciled.OutcomePath; $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($identity.ToString().ToLowerInvariant())|$($current.ToString().ToLowerInvariant())|$($failure.safety.ssh_used.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|true"


def test_terminal_outcome_is_staged_and_not_published_when_terminal_transition_fails(tmp_path: Path):
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    missing_lifecycle = str(tmp_path / "missing.lifecycle").replace("'", "''")
    result = run_powershell(
        f"$reservation = Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        "$failed = $false; try { "
        f"Publish-Phase15TerminalOutcome -LifecyclePath '{missing_lifecycle}' -ReservationPath $reservation -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        "-Status 'completed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'not_applicable' -Outcome ([ordered]@{schema='synthetic'}) "
        "} catch { $failed = $true }; "
        "$reserved = Test-Phase15OutcomeOwnership -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        "Release-Phase15OutcomeSlot -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        f"$published = Test-Path -LiteralPath '{outcome}'; "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($reserved.ToString().ToLowerInvariant())|$($published.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|false"


@pytest.mark.parametrize(("status", "reason"), [("completed", "not_applicable"), ("failed", "transport_failed")])
def test_terminal_outcome_and_lifecycle_finalize_consistently(tmp_path: Path, status: str, reason: str):
    lifecycle_root = str(tmp_path / "lifecycle").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$null = [IO.Directory]::CreateDirectory('{lifecycle_root}'); "
        f"$lifecycle = Reserve-Phase15Claim -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        f"$reservation = Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        f"Publish-Phase15TerminalOutcome -LifecyclePath $lifecycle -ReservationPath $reservation -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-Status '{status}' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode '{reason}' -Outcome ([ordered]@{{decision='stop';schema='synthetic'}}); "
        "Release-Phase15OutcomeSlot -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        f"$published = [IO.File]::ReadAllText('{outcome}'); $terminal = [IO.File]::ReadAllText($lifecycle); "
        "$residue = Test-Phase15OutcomeOwnership -ReservationPath $reservation -ClaimId 'phase15-preflight-test-001'; "
        "[Console]::Out.Write(\"$published|$terminal|$($residue.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    published_raw, terminal_raw, residue = result.stdout.split("|", 2)
    assert json.loads(published_raw) == {"decision": "stop", "schema": "synthetic"}
    terminal = json.loads(terminal_raw)
    assert terminal["status"] == status
    assert terminal["reason_code"] == reason
    assert residue == "false"


def test_runner_bounded_buffer_keeps_only_limit_plus_one_bytes():
    payload = base64.b64encode(b"0123456789").decode()
    result = run_powershell(
        f"$buffer = [IO.MemoryStream]::new(); $bytes = [Convert]::FromBase64String('{payload}'); "
        "$overflow = Add-Phase15BoundedBytes -Buffer $buffer -Bytes $bytes -Count $bytes.Length -MaximumBytes 4; "
        "[Console]::Out.Write(\"$($overflow.ToString().ToLowerInvariant())|$($buffer.Length)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|5"


def test_collector_aggregate_limits_stop_network_container_and_recovery_inventory(tmp_path: Path):
    namespace = collector_python_namespace()
    parse_ids = namespace["_docker_network_ids"]
    classify_inventory = namespace["classify_container_inventory"]
    scan_recovery = namespace["scan_recovery_markers"]
    success = "success"
    max_networks = namespace["MAX_NETWORK_IDS"]
    max_containers = namespace["MAX_CONTAINER_ROWS"]
    max_recovery = namespace["MAX_RECOVERY_ENTRIES"]

    network_lines = b"".join(f"{index:064x}\n".encode() for index in range(max_networks + 1))
    with pytest.raises(ValueError, match="network inventory limit"):
        parse_ids((0, network_lines, b"", success))

    container_lines = b"".join(f"container-{index}\n".encode() for index in range(max_containers + 1))
    assert classify_inventory([("synthetic", (0, container_lines, b"", success))]) == ("stop", "stop")

    recovery_root = tmp_path / "recovery"
    recovery_root.mkdir()
    for index in range(max_recovery + 1):
        (recovery_root / f"entry-{index}").write_bytes(b"")
    assert scan_recovery((recovery_root,)) == ("stop", "entry_limit_exceeded")


def test_collector_global_deadline_stops_before_starting_another_command(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    namespace["_collector_deadline"] = namespace["time"].monotonic() - 1
    started = []

    class Process:
        stdout = io.BytesIO()
        stderr = io.BytesIO()

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    def popen(*_args, **_kwargs):
        started.append(True)
        return Process()

    monkeypatch.setattr(namespace["subprocess"], "Popen", popen)

    assert namespace["command"](["synthetic"]) == (124, b"", b"", "work_budget_exceeded")
    assert started == []


@pytest.mark.parametrize("reservation", ["claim", "outcome"])
def test_reservations_are_durable_atomic_and_mid_write_never_publishes_partial_file(tmp_path: Path, reservation: str):
    lifecycle_root = str(tmp_path / "claims").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    body = f"$null = [IO.Directory]::CreateDirectory('{lifecycle_root}'); "
    if reservation == "claim":
        target = str(tmp_path / "claims" / "phase15-preflight-test-001.json").replace("'", "''")
        invocation = f"Reserve-Phase15Claim -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'"
    else:
        target = outcome
        invocation = f"Reserve-Phase15OutcomeSlot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'"
    result = run_powershell(
        body
        + "function Write-Phase15DurableBytes { param($Stream,$Bytes) $Stream.WriteByte($Bytes[0]); throw 'synthetic_power_loss' }; "
        + f"$failed=$false; try {{ $null = {invocation} }} catch {{ $failed=$true }}; "
        + f"$published=Test-Path -LiteralPath '{target}'; $temps=@([IO.Directory]::GetFiles((Split-Path -Parent '{target}'), '*.create-*.tmp')); "
        + "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($published.ToString().ToLowerInvariant())|$($temps.Count)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|0"


def test_journal_phase_rewrite_is_durable_atomic_on_mid_write_failure(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$before=[IO.File]::ReadAllBytes($tx.JournalPath); function Write-Phase15DurableBytes { param($Stream,$Bytes) $Stream.WriteByte($Bytes[0]); throw 'synthetic_power_loss' }; "
        "$failed=$false; try { $null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'transport_attempted' -Lock $lock } catch { $failed=$true }; "
        "$after=[IO.File]::ReadAllBytes($tx.JournalPath); $same=[Convert]::ToBase64String($before) -ceq [Convert]::ToBase64String($after); $temps=@([IO.Directory]::GetFiles((Split-Path -Parent $tx.JournalPath), '*.atomic-*')); $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($same.ToString().ToLowerInvariant())|$($temps.Count)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|0"


def test_terminal_lifecycle_rewrite_is_durable_atomic_on_mid_write_failure(tmp_path: Path):
    lifecycle_root = str(tmp_path / "claims").replace("'", "''")
    result = run_powershell(
        f"$null=[IO.Directory]::CreateDirectory('{lifecycle_root}'); $path=Reserve-Phase15Claim -LifecycleRoot '{lifecycle_root}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z'; "
        "$before=[IO.File]::ReadAllBytes($path); function Write-Phase15DurableBytes { param($Stream,$Bytes) $Stream.WriteByte($Bytes[0]); throw 'synthetic_power_loss' }; "
        "$failed=$false; try { $null=Set-Phase15ClaimTerminal -LifecyclePath $path -ClaimId 'phase15-preflight-test-001' -Status 'failed' -EndedAt '2026-08-16T00:00:01Z' -ReasonCode 'transport_failed' } catch { $failed=$true }; "
        "$after=[IO.File]::ReadAllBytes($path); $same=[Convert]::ToBase64String($before) -ceq [Convert]::ToBase64String($after); $temps=@([IO.Directory]::GetFiles((Split-Path -Parent $path), '*.terminal-*')); "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($same.ToString().ToLowerInvariant())|$($temps.Count)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|0"


def test_transaction_start_preserves_durable_journal_and_owned_outcome_on_lifecycle_uncertainty(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        "function Reserve-Phase15Claim { throw 'synthetic_lifecycle_uncertain' }; $failed=$false; "
        f"try {{ $null=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock }} catch {{ $failed=$true }}; "
        f"$journal=Get-Phase15TransactionPath -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; $journalExists=Test-Path -LiteralPath $journal; $owned=Test-Phase15OutcomeOwnership -ReservationPath '{outcome}' -ClaimId 'phase15-preflight-test-001'; $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($journalExists.ToString().ToLowerInvariant())|$($owned.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|true"


def test_round8_runner_binds_authoritative_phase13_spain_trust_and_no_ambient_ssh():
    result = run_powershell(
        f"$contract=Get-Phase15SpainTrustContract; $args=New-Phase15SshArguments -ExpectedHost '138.124.181.246' "
        f"-ClaimId 'phase15-preflight-test-001' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}'; "
        "[Console]::Out.Write(($contract | ConvertTo-Json -Compress) + \"`n\" + (($args | ConvertTo-Json -Compress)))"
    )

    assert result.returncode == 0, result.stderr
    contract_text, arguments_text = result.stdout.splitlines()
    contract = json.loads(contract_text)
    arguments = json.loads(arguments_text)
    assert contract["TargetUser"] == "root"
    assert contract["TrustRoot"].endswith(r"post-release\spain-migration\spain-fresh-20260720-001")
    assert contract["KeyPath"].endswith(r"spain-fresh-20260720-001\id_ed25519_spain")
    assert contract["KnownHostsPath"].endswith(r"spain-fresh-20260720-001\known_hosts_spain")
    assert contract["ExpectedHostKeySha256"] == "SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU"
    assert arguments[-3:] == [
        "--",
        "root@138.124.181.246",
        f"/usr/bin/bash -s -- '{PACKAGE_ID}' '{MANIFEST_SHA256}' '{COLLECTOR_SHA256}' 'phase15-preflight-test-001' '138.124.181.246'",
    ]
    for required in (
        "BatchMode=yes",
        "IdentitiesOnly=yes",
        "StrictHostKeyChecking=yes",
        "IdentityAgent=none",
        "PasswordAuthentication=no",
        "KbdInteractiveAuthentication=no",
        "GSSAPIAuthentication=no",
        f"UserKnownHostsFile={contract['KnownHostsPath']}",
        contract["KeyPath"],
    ):
        assert required in arguments
    assert "-F" in arguments and arguments[arguments.index("-F") + 1] == "none"


def test_round8_runner_rejects_host_options_and_uses_bounded_artifact_reads(tmp_path: Path):
    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"x" * 65)
    escaped = str(oversized).replace("'", "''")
    result = run_powershell(
        f"$bad=@('root@host','-oProxyCommand=x','host value','host/part'); $rejected=@($bad | %{{-not (Test-Phase15ExpectedHost -ExpectedHost $_)}}); "
        f"$bounded=$false; try {{ Read-Phase15BoundedFileBytes -Path '{escaped}' -MaximumBytes 64 }} catch {{ $bounded=$true }}; "
        "[Console]::Out.Write(\"$((@($rejected | ?{$_}).Count))|$($bounded.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "4|true"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    assert "[IO.File]::ReadAllBytes" not in source


def test_round8_collector_uses_fixed_isolated_executables_and_minimal_environment(monkeypatch: pytest.MonkeyPatch):
    namespace = collector_python_namespace()
    command = namespace["command"]
    captured: dict[str, str] = {}
    for name in ("PYTHONPATH", "PYTHONHOME", "GIT_CONFIG_GLOBAL", "DOCKER_HOST", "DOCKER_CONTEXT", "CONTAINER_HOST", "CONTAINER_CONNECTION", "PODMAN_HOST", "PODMAN_CONNECTION"):
        monkeypatch.setenv(name, "unsafe-ambient-value")

    class Process:
        stdout = io.BytesIO()
        stderr = io.BytesIO()

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    def popen(_parts, **kwargs):
        captured.update(kwargs["env"])
        assert kwargs["cwd"] == "/"
        return Process()

    monkeypatch.setattr(namespace["subprocess"], "Popen", popen)
    assert command(["/usr/bin/systemctl"])[3] == "success"
    assert captured == {
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": "/root",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/sbin:/usr/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONSAFEPATH": "1",
    }
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert "PHASE15_PYTHON" not in source
    assert "exec /usr/bin/python3 -I -B -" in source
    assert "socket.getfqdn" not in source
    for relative in ('"systemctl"', '["ip"', '["nsenter"', '["ss"', '["nft"', '["iptables-save"', '["iptables-legacy-save"'):
        assert relative not in source


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (b'ID=debian\nVERSION_ID="12"\n', ("pass", b"debian:12")),
        (b'ID=ubuntu\nVERSION_ID="24.04"\n', ("stop", b"unsupported-os")),
        (b'ID=debian\nVERSION_ID="13"\n', ("stop", b"unsupported-os")),
        (b'ID=debian\r\nVERSION_ID="12"\r\n', ("stop", b"malformed-os-release")),
        (b'ID=debian\nID=debian\nVERSION_ID="12"\n', ("stop", b"malformed-os-release")),
        (b'ID=debian\nVERSION_ID="12"\nBROKEN="unterminated\n', ("stop", b"malformed-os-release")),
    ],
)
def test_round8_os_release_parser_is_strict_and_exact_debian_12(raw: bytes, expected: tuple[str, bytes]):
    assert collector_helper("classify_os_release")(raw) == expected


def test_round8_docker_none_network_is_the_only_empty_ipam_exception():
    classify = collector_helper("classify_dedicated_spain_docker")
    success = "success"
    inventory = (0, b"other\n", b"", success)
    ids = (0, (b"a" * 64) + b"\n", b"", success)
    none = (0, b'"none"\t"null"\t{"Config":[],"Driver":"default","Options":null}\n', b"", success)
    bridge_empty = (0, b'"bridge"\t"bridge"\t{"Config":[],"Driver":"default","Options":{}}\n', b"", success)
    malformed_none = (0, b'"none"\t"bridge"\t{"Config":[],"Driver":"default","Options":{}}\n', b"", success)

    assert classify(inventory, ids, [none]) == ("pass", "free", "free")
    assert classify(inventory, ids, [bridge_empty]) == ("stop", "stop", "stop")
    assert classify(inventory, ids, [malformed_none]) == ("stop", "stop", "stop")


def test_round8_container_limits_are_shared_across_all_engines():
    classify = collector_helper("classify_spain_docker_sources")
    success = "success"
    none = (0, b'"none"\t"null"\t{"Config":[],"Driver":"default","Options":null}\n', b"", success)
    source_a = ((0, b"".join(f"a-{i}\n".encode() for i in range(256)), b"", success), (0, (b"a" * 64) + b"\n", b"", success), [none])
    source_b = ((0, b"".join(f"b-{i}\n".encode() for i in range(256)), b"", success), (0, (b"b" * 64) + b"\n", b"", success), [none])
    overflow = ((0, b"extra\n", b"", success), (0, (b"c" * 64) + b"\n", b"", success), [none])

    assert classify(source_a, source_b, overflow) == ("stop", "stop", "stop")


def test_round8_global_deadline_covers_filesystem_scan_and_final_emission(tmp_path: Path):
    namespace = collector_python_namespace()
    namespace["_collector_deadline"] = namespace["time"].monotonic() - 1
    assert namespace["scan_recovery_markers"]((tmp_path,)) == ("stop", "work_budget_exceeded")
    with pytest.raises(TimeoutError, match="work budget"):
        namespace["ensure_work_budget"]()


def test_round8_unknown_journal_phase_cannot_transition_and_recovers_terminal_failure(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath; $journal.phase='corrupt'; Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        "$transitionRejected=$false; try{$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'transport_attempted' -Lock $lock}catch{$transitionRejected=$true}; "
        f"$recovered=Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock; "
        "$terminal=ConvertFrom-Phase15CanonicalJsonFile -Path $recovered.OutcomePath; $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($transitionRejected.ToString().ToLowerInvariant())|$($recovered.Recovered.ToString().ToLowerInvariant())|$($terminal.reason_code)|$($terminal.safety.ssh_used.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true|transport_failed|true"


def test_round8_awg2_requires_final_owner_unit_recheck():
    classify = collector_helper("classify_awg2_health")
    success = "success"
    owner = (0, b"active\n", b"", success)
    changed_owner = (0, b"inactive\n", b"", success)
    container = (0, b"true|4242|0\n", b"", success)
    interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success)
    handshakes = (0, b"A" * 43 + b"=\t1699999940\n", b"", success)

    assert classify(owner, container, interface, handshakes, container, changed_owner, now_epoch=1_700_000_000) == "stop"
    assert classify(owner, container, interface, handshakes, container, owner, now_epoch=1_700_000_000) == "pass"


def test_round8_startup_cleanup_removes_only_exact_claim_owned_temp_and_backup_residues(tmp_path: Path):
    transaction = tmp_path / "transactions" / "phase15-preflight-test-001.json"
    lifecycle = tmp_path / "claims" / "phase15-preflight-test-001.json"
    outcome = tmp_path / "outcome.json"
    transaction.parent.mkdir()
    lifecycle.parent.mkdir()
    own_guid = "a" * 32
    other_guid = "b" * 32
    own = [
        Path(str(transaction) + f".phase15-phase15-preflight-test-001.atomic-{own_guid}"),
        Path(str(transaction) + f".phase15-phase15-preflight-test-001.backup-{own_guid}"),
        Path(str(lifecycle) + f".phase15-phase15-preflight-test-001.terminal-{own_guid}"),
        Path(str(lifecycle) + f".phase15-phase15-preflight-test-001.backup-{own_guid}"),
        Path(str(outcome) + f".phase15-phase15-preflight-test-001.reservation-backup-{own_guid}"),
    ]
    other = Path(str(outcome) + f".phase15-phase15-preflight-test-002.reservation-backup-{other_guid}")
    for path in [*own, other]:
        path.write_bytes(b"synthetic")
    transaction_ps = str(transaction).replace("'", "''")
    lifecycle_ps = str(lifecycle).replace("'", "''")
    outcome_ps = str(outcome).replace("'", "''")
    result = run_powershell(
        f"Remove-Phase15TransactionTemps -TransactionPath '{transaction_ps}' -ClaimId 'phase15-preflight-test-001'; "
        f"Remove-Phase15OwnedStateResidues -LifecyclePath '{lifecycle_ps}' -OutcomePath '{outcome_ps}' -ClaimId 'phase15-preflight-test-001'; "
        "[Console]::Out.Write('clean')"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "clean"
    assert all(not path.exists() for path in own)
    assert other.read_bytes() == b"synthetic"


def test_round9_private_trust_buffers_are_cleared_when_second_read_fails():
    result = run_powershell(
        "$script:keyBuffer=[Text.ASCIIEncoding]::new().GetBytes('-----BEGIN OPENSSH PRIVATE KEY-----`nYWJj`n-----END OPENSSH PRIVATE KEY-----`n'); "
        "$script:readCount=0; "
        "function Get-Phase15SpainTrustContract { [pscustomobject]@{TrustRoot='C:\\synthetic'; KeyPath='C:\\synthetic\\key'; KnownHostsPath='C:\\synthetic\\known'; ExpectedHostKeySha256='SHA256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'; TargetUser='root'; AnchorPath='C:\\'} }; "
        "function Assert-Phase15TrustAnchor { param($Path) }; function Assert-Phase15TrustParentChain { param($AnchorPath,$TrustRoot,$ExpectedOwnerSid) }; function Assert-Phase15TrustPath { param($Path,$ExpectedOwnerSid,[switch]$RequireLeaf) }; "
        "function Read-Phase15BoundedFileBytes { param($Path,$MaximumBytes) $script:readCount++; if($script:readCount -eq 1){Write-Output -NoEnumerate $script:keyBuffer; return}; throw 'synthetic_second_read_failure' }; "
        "$failed=$false; try{$null=Assert-Phase15SpainTrustBundle -ExpectedHost 'spain.test.invalid'}catch{$failed=$true}; "
        "$cleared=(@($script:keyBuffer | Where-Object {$_ -ne 0}).Count -eq 0); "
        "[Console]::Out.Write(\"$($failed.ToString().ToLowerInvariant())|$($cleared.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true"


def test_round9_private_key_framing_is_validated_directly_over_mutable_ascii_bytes():
    valid = base64.b64encode(
        b"-----BEGIN OPENSSH PRIVATE KEY-----\nYWJj\n-----END OPENSSH PRIVATE KEY-----\n"
    ).decode("ascii")
    missing_footer = base64.b64encode(
        b"-----BEGIN OPENSSH PRIVATE KEY-----\nYWJj\n"
    ).decode("ascii")
    nul = base64.b64encode(
        b"-----BEGIN OPENSSH PRIVATE KEY-----\nYW\x00Jj\n-----END OPENSSH PRIVATE KEY-----\n"
    ).decode("ascii")
    result = run_powershell(
        f"$valid=Test-Phase15PrivateKeyBytes -Bytes ([Convert]::FromBase64String('{valid}')); "
        f"$missing=Test-Phase15PrivateKeyBytes -Bytes ([Convert]::FromBase64String('{missing_footer}')); "
        f"$nul=Test-Phase15PrivateKeyBytes -Bytes ([Convert]::FromBase64String('{nul}')); "
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$($missing.ToString().ToLowerInvariant())|$($nul.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"
    trust = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    trust = trust[trust.index("function Assert-Phase15SpainTrustBundle") : trust.index("function Assert-Phase15LocalExecutable")]
    assert "GetString($keyBytes)" not in trust
    assert "$keyText" not in trust


def test_round9_trust_parent_chain_enumerates_every_fixed_component_below_localappdata(tmp_path: Path):
    anchor = str(tmp_path / "Local").replace("'", "''")
    trust = str(
        tmp_path
        / "Local"
        / "AMN2"
        / "private-artifacts"
        / "post-release"
        / "spain-migration"
        / "spain-fresh-20260720-001"
    ).replace("'", "''")
    result = run_powershell(
        f"$paths=@(Get-Phase15TrustParentPaths -AnchorPath '{anchor}' -TrustRoot '{trust}'); "
        "[Console]::Out.Write(($paths | ForEach-Object {[IO.Path]::GetFileName($_)}) -join '|')"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "AMN2|private-artifacts|post-release|spain-migration|spain-fresh-20260720-001"


def test_round9_os_release_accepts_only_exact_debian_symlink_layout(tmp_path: Path):
    namespace = collector_python_namespace()
    read_os_release = namespace.get("bounded_os_release_bytes")
    assert callable(read_os_release)
    etc = tmp_path / "etc"
    canonical = tmp_path / "usr" / "lib" / "os-release"
    etc.mkdir()
    canonical.parent.mkdir(parents=True)
    canonical.write_bytes(b"ID=debian\nVERSION_ID=12\n")
    link = etc / "os-release"
    link.symlink_to("../usr/lib/os-release")

    assert read_os_release(str(link), str(canonical)) == b"ID=debian\nVERSION_ID=12\n"

    link.unlink()
    link.write_bytes(canonical.read_bytes())
    with pytest.raises(OSError):
        read_os_release(str(link), str(canonical))
    link.unlink()
    link.symlink_to("../usr/lib/not-os-release")
    with pytest.raises(OSError):
        read_os_release(str(link), str(canonical))


def test_round9_transport_uses_one_monotonic_65_second_total_budget():
    result = run_powershell(
        "$clock=[Diagnostics.Stopwatch]::StartNew(); "
        "$first=Get-Phase15TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds 65000; "
        "Start-Sleep -Milliseconds 25; "
        "$second=Get-Phase15TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds 65000; "
        "[Console]::Out.Write(\"$($first -le 65000 -and $first -gt 64000)|$($second -lt $first)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.lower() == "true|true"
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    transport = source[source.index("function Invoke-Phase15OneSshTransport") : source.index("function Write-Phase15CreateNewJson")]
    assert "[Diagnostics.Stopwatch]::StartNew()" in transport
    assert "[DateTimeOffset]::UtcNow" not in transport
    assert "65000" in source


def test_round9_cleanup_covers_every_exact_writer_residue_including_recovery(tmp_path: Path):
    lifecycle = tmp_path / "claims" / "phase15-preflight-test-001.json"
    outcome = tmp_path / "outcome.json"
    recovery = tmp_path / "recovery-outcomes" / "phase15-preflight-test-001.json"
    lifecycle.parent.mkdir()
    recovery.parent.mkdir()
    guid = "c" * 32
    claim_id = "phase15-preflight-test-001"
    owned = [
        Path(str(lifecycle) + f".phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(lifecycle) + f".phase15-{claim_id}.atomic-{guid}"),
        Path(str(lifecycle) + f".phase15-{claim_id}.atomic-{guid}.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(lifecycle) + f".phase15-{claim_id}.terminal-{guid}.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(outcome) + f".phase15-{claim_id}.staged.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(outcome) + f".phase15-{claim_id}.pending-{guid}.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(outcome) + f".phase15-{claim_id}.atomic-{guid}.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(recovery) + f".phase15-{claim_id}.atomic-{guid}"),
        Path(str(recovery) + f".phase15-{claim_id}.atomic-{guid}.phase15-{claim_id}.create-{guid}.tmp"),
        Path(str(recovery) + f".phase15-{claim_id}.backup-{guid}"),
    ]
    unrelated = Path(str(outcome) + ".phase15-other-claim.staged.phase15-other-claim.create-" + guid + ".tmp")
    for path in [*owned, unrelated]:
        path.write_bytes(b"synthetic")
    lifecycle_ps = str(lifecycle).replace("'", "''")
    outcome_ps = str(outcome).replace("'", "''")
    recovery_ps = str(recovery).replace("'", "''")
    result = run_powershell(
        f"Remove-Phase15OwnedStateResidues -LifecyclePath '{lifecycle_ps}' -OutcomePath '{outcome_ps}' -RecoveryOutcomePath '{recovery_ps}' -ClaimId '{claim_id}'; "
        "[Console]::Out.Write('clean')"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "clean"
    assert all(not path.exists() for path in owned)
    assert unrelated.read_bytes() == b"synthetic"


def test_round10_managed_state_acl_rejects_reparse_inheritance_and_unapproved_writers():
    result = run_powershell(
        "$authorized='S-1-5-21-1000'; $system='S-1-5-18'; $admins='S-1-5-32-544'; "
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl; "
        "$inherit=[int][Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [int][Security.AccessControl.InheritanceFlags]::ObjectInherit; "
        "function New-Rule($sid,$inherited=$false){[pscustomobject]@{Sid=$sid;Type='Allow';Rights=$full;IsInherited=$inherited;Inheritance=$inherit;Propagation=0}}; "
        "$rules=@((New-Rule $authorized),(New-Rule $system),(New-Rule $admins)); "
        "$valid=[pscustomobject]@{Exists=$true;FullName='C:\\ProgramData\\AMN2';IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=$rules}; "
        "$validResult=Test-Phase15ManagedStateDirectoryFacts -Facts $valid -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized; "
        "$reparse=$valid.PSObject.Copy(); $reparse.IsReparse=$true; "
        "$unprotected=$valid.PSObject.Copy(); $unprotected.Protected=$false; "
        "$inherited=$valid.PSObject.Copy(); $inherited.Rules=@((New-Rule $authorized $true),(New-Rule $system),(New-Rule $admins)); "
        "$users=$valid.PSObject.Copy(); $users.Rules=@($rules + [pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64][Security.AccessControl.FileSystemRights]::Write;IsInherited=$false;Inheritance=$inherit;Propagation=0}); "
        "$badOwner=$valid.PSObject.Copy(); $badOwner.OwnerSid=$users.Rules[-1].Sid; "
        "[Console]::Out.Write(\"$($validResult.ToString().ToLowerInvariant())|$((Test-Phase15ManagedStateDirectoryFacts -Facts $reparse -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized).ToString().ToLowerInvariant())|$((Test-Phase15ManagedStateDirectoryFacts -Facts $unprotected -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized).ToString().ToLowerInvariant())|$((Test-Phase15ManagedStateDirectoryFacts -Facts $inherited -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized).ToString().ToLowerInvariant())|$((Test-Phase15ManagedStateDirectoryFacts -Facts $users -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized).ToString().ToLowerInvariant())|$((Test-Phase15ManagedStateDirectoryFacts -Facts $badOwner -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized).ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false|false|false|false"


def test_round10_programdata_anchor_requires_exact_protected_platform_acl():
    result = run_powershell(
        "$rules=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$false;Inheritance=3;Propagation=2},[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$false;Inheritance=1;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$false;Inheritance=3;Propagation=0}); "
        "$valid=[pscustomobject]@{Exists=$true;FullName='C:\\ProgramData';IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-18';Protected=$true;Rules=$rules}; "
        "$extra=$valid.PSObject.Copy();$extra.Rules=@($rules+[pscustomobject]@{Sid='S-1-1-0';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0}); "
        "$inherited=$valid.PSObject.Copy();$copied=@($rules|ForEach-Object{$_.PSObject.Copy()});$copied[0].IsInherited=$true;$inherited.Rules=$copied; "
        "$ok=Test-Phase15ProgramDataAnchorFacts -Facts $valid -ExpectedPath 'C:\\ProgramData';$badExtra=Test-Phase15ProgramDataAnchorFacts -Facts $extra -ExpectedPath 'C:\\ProgramData';$badInherited=Test-Phase15ProgramDataAnchorFacts -Facts $inherited -ExpectedPath 'C:\\ProgramData'; "
        "[Console]::Out.Write(\"$($ok.ToString().ToLowerInvariant())|$($badExtra.ToString().ToLowerInvariant())|$($badInherited.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false"


def test_round10_state_root_is_provisioned_under_one_global_lock_with_synthetic_acl_doubles():
    result = run_powershell(
        "$script:events=[Collections.Generic.List[string]]::new(); $script:facts=@{}; $authorized='S-1-5-21-1000'; "
        "$anchor='C:\\SyntheticProgramData'; $root='C:\\SyntheticProgramData\\AMN2\\phase15\\readonly-preflight'; "
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl; $inherit=3; "
        "$anchorRules=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$false;Inheritance=3;Propagation=2},[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$false;Inheritance=1;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$false;Inheritance=3;Propagation=0}); "
        "function New-ManagedFacts($path){$rules=@('S-1-5-21-1000','S-1-5-18','S-1-5-32-544' | ForEach-Object {[pscustomobject]@{Sid=$_;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}}); [pscustomobject]@{Exists=$true;FullName=$path;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-21-1000';Protected=$true;Rules=$rules}}; "
        "$script:facts[$anchor]=[pscustomobject]@{Exists=$true;FullName=$anchor;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-18';Protected=$true;Rules=$anchorRules}; "
        "function Enter-Phase15StateRootCreationLock{$script:events.Add('lock');[pscustomobject]@{Acquired=$true}}; "
        "function Exit-Phase15StateRootCreationLock{param($Lock)$script:events.Add('unlock')}; "
        "function Get-Phase15StateDirectoryFacts{param($Path)$script:events.Add('facts:'+([IO.Path]::GetFileName($Path)));if($script:facts.ContainsKey($Path)){return $script:facts[$Path]};[pscustomobject]@{Exists=$false;FullName=$Path}}; "
        "function New-Phase15SecureStateDirectory{param($ParentPath,$Path,$AuthorizedSid)$script:events.Add('create:'+([IO.Path]::GetFileName($Path)));$script:facts[$Path]=New-ManagedFacts $Path}; "
        "$actual=Initialize-Phase15TrustedStateRoot -AnchorPath $anchor -StateRoot $root -AuthorizedSid $authorized; "
        "$created=@($script:events | Where-Object {$_ -like 'create:*'} | ForEach-Object {$_.Substring(7)}); "
        "$locked=$script:events[0] -eq 'lock' -and $script:events[-1] -eq 'unlock'; "
        "[Console]::Out.Write(\"$($actual -ceq $root)|$($locked.ToString().ToLowerInvariant())|$($created -join ',')\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "True|true|AMN2,phase15,readonly-preflight,locks,outcome-locks,claims,transactions,recovery-outcomes,outcomes"


def test_round10_attacker_precreated_managed_tree_is_rejected_without_provisioning():
    result = run_powershell(
        "$script:createCount=0; $authorized='S-1-5-21-1000'; $anchor='C:\\SyntheticProgramData'; $root='C:\\SyntheticProgramData\\AMN2\\phase15\\readonly-preflight'; "
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl; $inherit=3; "
        "$anchorRules=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$false;Inheritance=3;Propagation=2},[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$false;Inheritance=1;Propagation=0},[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$false;Inheritance=3;Propagation=0}); "
        "$goodRules=@('S-1-5-21-1000','S-1-5-18','S-1-5-32-544' | ForEach-Object {[pscustomobject]@{Sid=$_;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}}); "
        "$badRules=@($goodRules + [pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64][Security.AccessControl.FileSystemRights]::Write;IsInherited=$false;Inheritance=$inherit;Propagation=0}); "
        "function Enter-Phase15StateRootCreationLock{[pscustomobject]@{Acquired=$true}}; function Exit-Phase15StateRootCreationLock{param($Lock)}; "
        "function Get-Phase15StateDirectoryFacts{param($Path)if($Path -ceq $anchor){return [pscustomobject]@{Exists=$true;FullName=$anchor;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-18';Protected=$true;Rules=$anchorRules}};if($Path -ceq 'C:\\SyntheticProgramData\\AMN2'){return [pscustomobject]@{Exists=$true;FullName=$Path;IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=$badRules}};[pscustomobject]@{Exists=$false;FullName=$Path}}; "
        "function New-Phase15SecureStateDirectory{param($ParentPath,$Path,$AuthorizedSid)$script:createCount++}; "
        "$message='';try{$null=Initialize-Phase15TrustedStateRoot -AnchorPath $anchor -StateRoot $root -AuthorizedSid $authorized}catch{$message=$_.Exception.Message}; "
        "[Console]::Out.Write(\"$message|$script:createCount\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "state_root_invalid|0"


def test_round10_outcome_path_lock_is_canonical_exclusive_and_claim_independent(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "result.json").replace("'", "''")
    equivalent = str(tmp_path / "unused" / ".." / "result.json").replace("'", "''")
    result = run_powershell(
        f"$null=[IO.Directory]::CreateDirectory((Join-Path '{state_root}' 'outcome-locks')); "
        f"$firstPath=Get-Phase15OutcomeLockPath -StateRoot '{state_root}' -OutcomePath '{outcome}'; "
        f"$samePath=Get-Phase15OutcomeLockPath -StateRoot '{state_root}' -OutcomePath '{equivalent}'; "
        f"$owner=Enter-Phase15OutcomeLock -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001'; "
        "$message=''; try { "
        f"$null=Enter-Phase15OutcomeLock -StateRoot '{state_root}' -OutcomePath '{equivalent}' -ClaimId 'phase15-preflight-test-002' "
        "} catch {$message=$_.Exception.Message}; $owner.Stream.Dispose(); "
        f"$next=Enter-Phase15OutcomeLock -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-002'; $next.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($firstPath -ceq $samePath)|$message\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "True|outcome_replay"


def test_round10_outcome_lock_blocks_contender_before_owner_residue_cleanup(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome_path = tmp_path / "result.json"
    outcome = str(outcome_path).replace("'", "''")
    claim_a = "phase15-preflight-test-001"
    claim_b = "phase15-preflight-test-002"
    owner_temp = Path(str(outcome_path) + f".phase15-{claim_a}.create-{'a' * 32}.tmp")
    owner_temp.write_bytes(b"owner-in-progress")
    result = run_powershell(
        f"$null=[IO.Directory]::CreateDirectory((Join-Path '{state_root}' 'outcome-locks')); "
        f"$owner=Enter-Phase15OutcomeLock -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId '{claim_a}'; "
        "$message=''; try { "
        f"$null=Enter-Phase15OutcomeLock -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId '{claim_b}' "
        "} catch {$message=$_.Exception.Message}; "
        f"$still=[IO.File]::ReadAllText('{str(owner_temp).replace("'", "''")}'); $owner.Stream.Dispose(); "
        "[Console]::Out.Write(\"$message|$still\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "outcome_replay|owner-in-progress"


def test_round10_distinct_claim_transaction_contender_cannot_touch_active_outcome_owner(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome_path = tmp_path / "result.json"
    outcome = str(outcome_path).replace("'", "''")
    claim_a = "phase15-preflight-test-001"
    claim_b = "phase15-preflight-test-002"
    owner_temp = Path(str(outcome_path) + f".phase15-{claim_a}.create-{'a' * 32}.tmp")
    result = run_powershell(
        f"$firstClaim=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId '{claim_a}'; "
        f"$tx=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId '{claim_a}' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $firstClaim; "
        f"[IO.File]::WriteAllText('{str(owner_temp).replace("'", "''")}', 'owner-in-progress', [Text.UTF8Encoding]::new($false)); $before=[IO.File]::ReadAllBytes($tx.JournalPath); "
        f"$secondClaim=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId '{claim_b}'; $message=''; try {{ "
        f"$null=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId '{claim_b}' -ReservedAt '2026-08-16T00:00:01Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $secondClaim "
        "} catch {$message=$_.Exception.Message}; "
        f"$after=[IO.File]::ReadAllBytes($tx.JournalPath); $same=[Convert]::ToBase64String($before) -ceq [Convert]::ToBase64String($after); $owned=Test-Phase15OutcomeOwnership -ReservationPath '{outcome}' -ClaimId '{claim_a}'; $temp=[IO.File]::ReadAllText('{str(owner_temp).replace("'", "''")}'); "
        "$tx.OutcomeLock.Stream.Dispose(); $secondClaim.Stream.Dispose(); $firstClaim.Stream.Dispose(); "
        "[Console]::Out.Write(\"$message|$($same.ToString().ToLowerInvariant())|$($owned.ToString().ToLowerInvariant())|$temp\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "outcome_replay|true|true|owner-in-progress"


def test_round10_atomic_writer_temp_name_is_exactly_claim_owned(tmp_path: Path):
    artifact = str(tmp_path / "artifact.json").replace("'", "''")
    claim_id = "phase15-preflight-test-001"
    result = run_powershell(
        "$script:temporaryName=''; "
        "function Write-Phase15DurableBytes{param($Stream,$Bytes)$script:temporaryName=[IO.Path]::GetFileName($Stream.Name);foreach($value in $Bytes){$Stream.WriteByte($value)};$Stream.Flush($true)}; "
        f"Write-Phase15AtomicCreateNewJson -Path '{artifact}' -Value ([ordered]@{{status='reserved'}}) -OwnerId '{claim_id}'; "
        "[Console]::Out.Write($script:temporaryName)"
    )

    assert result.returncode == 0, result.stderr
    assert re.fullmatch(rf"artifact\.json\.phase15-{re.escape(claim_id)}\.create-[0-9a-f]{{32}}\.tmp", result.stdout)


@pytest.mark.parametrize(
    ("issued_at", "expires_at"),
    [
        ("2099-08-16T00:00:00Z", "2100-08-16T00:00:00Z"),
        ("2020-08-16T00:00:00Z", "2021-08-16T00:00:00Z"),
    ],
    ids=("future", "expired"),
)
def test_round11_time_invalid_claim_never_initializes_production_state(
    tmp_path: Path, issued_at: str, expires_at: str
):
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        "$FutureAuthorization=$true; $FutureClaimPath='synthetic-claim.json'; $PackageRoot='C:\\synthetic-package'; "
        f"$OutcomePath='{outcome}'; $ExpectedHost='spain.test.invalid'; $script:initializerCount=0; "
        f"$script:claim=[pscustomobject][ordered]@{{claim_id='phase15-preflight-test-001';collector_sha256='{COLLECTOR_SHA256}';consumed_at=$null;expected_host='spain.test.invalid';expires_at='{expires_at}';future_gate='PREFLIGHT';issued_at='{issued_at}';manifest_sha256='{MANIFEST_SHA256}';package_id='{PACKAGE_ID}';schema='amn2.phase15.readonly-preflight-claim.v1';status='issued'}}; "
        f"function Read-Phase15ManifestArtifact{{[pscustomobject]@{{Value=[pscustomobject]@{{package_id='{PACKAGE_ID}';entries=@([pscustomobject]@{{path='tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh';sha256='{COLLECTOR_SHA256}'}})}};Sha256='{MANIFEST_SHA256}'}}}}; "
        f"function Read-Phase15CollectorArtifact{{[pscustomobject]@{{Bytes=[byte[]]@(1);Sha256='{COLLECTOR_SHA256}'}}}}; "
        "function Assert-Phase15SpainTrustBundle{param($ExpectedHost)[pscustomobject]@{Validated=$true}}; "
        "function Read-Phase15FutureClaim{param($ClaimPath)$script:claim}; "
        "function Initialize-Phase15ProductionStateRoot{$script:initializerCount++;throw 'initializer_called'}; "
        "$message='';try{Invoke-Phase15RunnerMain}catch{$message=$_.Exception.Message}; "
        "[Console]::Out.Write(\"$message|$script:initializerCount\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "claim_invalid|0"


@pytest.mark.parametrize(
    ("authorized_sid", "expected_sids"),
    [
        ("S-1-5-18", "S-1-5-18,S-1-5-32-544"),
        ("S-1-5-32-544", "S-1-5-32-544,S-1-5-18"),
        ("S-1-5-21-1000", "S-1-5-21-1000,S-1-5-18,S-1-5-32-544"),
    ],
    ids=("system", "administrators", "ordinary-runner"),
)
def test_round11_managed_acl_creation_and_validation_share_unique_sid_set(
    authorized_sid: str, expected_sids: str
):
    result = run_powershell(
        f"$authorized='{authorized_sid}'; $expected='{expected_sids}'; "
        "$security=New-Phase15ManagedStateDirectorySecurity -AuthorizedSid $authorized; "
        "$actual=@($security.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]) | ForEach-Object {$_.IdentityReference.Value}); "
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl; $inherit=[int][Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [int][Security.AccessControl.InheritanceFlags]::ObjectInherit; "
        "$facts=[pscustomobject]@{Exists=$true;FullName='C:\\ProgramData\\AMN2';IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=@($actual | ForEach-Object {[pscustomobject]@{Sid=$_;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}})}; "
        "$valid=Test-Phase15ManagedStateDirectoryFacts -Facts $facts -ExpectedPath 'C:\\ProgramData\\AMN2' -AuthorizedSid $authorized; "
        "[Console]::Out.Write(\"$($actual -join ',')|$($security.GetOwner([Security.Principal.SecurityIdentifier]).Value)|$($valid.ToString().ToLowerInvariant())|$($actual.Count)\")"
    )

    assert result.returncode == 0, result.stderr
    expected_count = len(expected_sids.split(","))
    actual_sids, owner_sid, valid, actual_count = result.stdout.split("|", 3)
    assert set(actual_sids.split(",")) == set(expected_sids.split(","))
    assert owner_sid == authorized_sid
    assert valid == "true"
    assert actual_count == str(expected_count)


def test_round12_claim_expiring_during_package_reads_never_initializes_state(tmp_path: Path):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_at = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expires_at = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        "$FutureAuthorization=$true; $FutureClaimPath='synthetic-claim.json'; $PackageRoot='C:\\synthetic-package'; "
        f"$OutcomePath='{outcome}'; $ExpectedHost='spain.test.invalid'; $script:initializerCount=0; "
        f"$script:claim=[pscustomobject][ordered]@{{claim_id='phase15-preflight-test-001';collector_sha256='{COLLECTOR_SHA256}';consumed_at=$null;expected_host='spain.test.invalid';expires_at='{expires_at}';future_gate='PREFLIGHT';issued_at='{issued_at}';manifest_sha256='{MANIFEST_SHA256}';package_id='{PACKAGE_ID}';schema='amn2.phase15.readonly-preflight-claim.v1';status='issued'}}; "
        f"function Read-Phase15ManifestArtifact{{[pscustomobject]@{{Value=[pscustomobject]@{{package_id='{PACKAGE_ID}';entries=@([pscustomobject]@{{path='tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh';sha256='{COLLECTOR_SHA256}'}})}};Sha256='{MANIFEST_SHA256}'}}}}; "
        f"function Read-Phase15CollectorArtifact{{[pscustomobject]@{{Bytes=[byte[]]@(1);Sha256='{COLLECTOR_SHA256}'}}}}; "
        "function Assert-Phase15SpainTrustBundle{param($ExpectedHost)[pscustomobject]@{Validated=$true}}; "
        "function Read-Phase15FutureClaim{param($ClaimPath)$script:claim}; "
        f"$script:Phase15AuthorizationClock={{[DateTimeOffset]::ParseExact('{expires_at}','yyyy-MM-ddTHH:mm:ssZ',[Globalization.CultureInfo]::InvariantCulture,[Globalization.DateTimeStyles]::AssumeUniversal)}}; "
        "function Initialize-Phase15ProductionStateRoot{$script:initializerCount++;throw 'initializer_called'}; "
        "$message='';try{Invoke-Phase15RunnerMain}catch{$message=$_.Exception.Message}; "
        "[Console]::Out.Write(\"$message|$script:initializerCount\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "claim_invalid|0"


@pytest.mark.parametrize("boundary", ["reservation", "transport", "reset_failure"])
def test_round12_fresh_clock_stops_expired_claim_before_reservation_or_transport(tmp_path: Path, boundary: str):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_at = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expires_at = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    valid_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    clock_values = (valid_at, expires_at) if boundary == "reservation" else (valid_at, valid_at, expires_at)
    reset_override = "function Reset-Phase15UnstartedTransaction{throw 'reset_failed'}; " if boundary == "reset_failure" else ""
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome_path = tmp_path / "outcome.json"
    outcome = str(outcome_path).replace("'", "''")
    enqueue = "".join(
        f"$script:clock.Enqueue([DateTimeOffset]::ParseExact('{value}','yyyy-MM-ddTHH:mm:ssZ',[Globalization.CultureInfo]::InvariantCulture,[Globalization.DateTimeStyles]::AssumeUniversal));"
        for value in clock_values
    )
    result = run_powershell(
        "$FutureAuthorization=$true; $FutureClaimPath='synthetic-claim.json'; $PackageRoot='C:\\synthetic-package'; "
        f"$OutcomePath='{outcome}'; $ExpectedHost='spain.test.invalid'; $script:initializerCount=0; $script:sshCount=0; "
        f"$script:stateRoot='{state_root}'; foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $script:stateRoot $leaf))}}; "
        "$script:clock=[Collections.Generic.Queue[DateTimeOffset]]::new(); "
        f"{enqueue} $script:Phase15AuthorizationClock={{if($script:clock.Count -eq 0){{throw 'clock_exhausted'}};$script:clock.Dequeue()}}; "
        f"$script:claim=[pscustomobject][ordered]@{{claim_id='phase15-preflight-test-001';collector_sha256='{COLLECTOR_SHA256}';consumed_at=$null;expected_host='spain.test.invalid';expires_at='{expires_at}';future_gate='PREFLIGHT';issued_at='{issued_at}';manifest_sha256='{MANIFEST_SHA256}';package_id='{PACKAGE_ID}';schema='amn2.phase15.readonly-preflight-claim.v1';status='issued'}}; "
        f"function Read-Phase15ManifestArtifact{{[pscustomobject]@{{Value=[pscustomobject]@{{package_id='{PACKAGE_ID}';entries=@([pscustomobject]@{{path='tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh';sha256='{COLLECTOR_SHA256}'}})}};Sha256='{MANIFEST_SHA256}'}}}}; "
        f"function Read-Phase15CollectorArtifact{{[pscustomobject]@{{Bytes=[byte[]]@(1);Sha256='{COLLECTOR_SHA256}'}}}}; "
        "function Assert-Phase15SpainTrustBundle{param($ExpectedHost)[pscustomobject]@{Validated=$true}}; "
        "function Read-Phase15FutureClaim{param($ClaimPath)$script:claim}; "
        "function Initialize-Phase15ProductionStateRoot{$script:initializerCount++;$script:stateRoot}; function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}; function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        f"{reset_override}"
        "function Invoke-Phase15OneSshTransport{param($ExpectedHost,$CollectorBytes,$Claim,$ClaimId,$ManifestSha256,$CollectorSha256,$ExpectedOutcomePath,$ReservedAt,[ref]$Started,$TransactionPath,$Lock) "
        "$process=[pscustomobject]@{}; $process|Add-Member -MemberType ScriptMethod -Name Start -Value {$script:sshCount++;return $true}; "
        "[void](Start-Phase15AuthorizedSshProcess -Process $process -Claim $Claim -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -TransactionPath $TransactionPath -Lock $Lock); $Started.Value=$true; throw 'ssh_double_called'}; "
        "$message='';try{Invoke-Phase15RunnerMain}catch{$message=$_.Exception.Message}; "
        "$lifecyclePath=Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $script:stateRoot 'claims') -ClaimId $script:claim.claim_id; $journalPath=Get-Phase15TransactionPath -StateRoot $script:stateRoot -ClaimId $script:claim.claim_id; "
        "$lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $lifecyclePath; $outcome=ConvertFrom-Phase15CanonicalJsonFile -Path $OutcomePath; "
        "$terminalOutcome=$null -ne $outcome -and @($outcome.PSObject.Properties.Name) -contains 'reason_code'; $outcomeStatus=if(-not $terminalOutcome){'absent'}else{'failed'}; $outcomeReason=if(-not $terminalOutcome){'absent'}else{$outcome.reason_code}; $outcomeSsh=if(-not $terminalOutcome){'absent'}else{$outcome.safety.ssh_used.ToString().ToLowerInvariant()}; $disposition=if(-not $terminalOutcome){'absent'}else{$outcome.transport_disposition}; "
        "$lifecycleState=if($null -eq $lifecycle){'absent'}else{$lifecycle.status+':'+$lifecycle.reason_code}; $journalExists=(Test-Path -LiteralPath $journalPath).ToString().ToLowerInvariant(); "
        "[Console]::Out.Write(\"$message|$script:initializerCount|$script:sshCount|$outcomeStatus|$outcomeReason|$outcomeSsh|$disposition|$lifecycleState|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    if boundary == "reservation":
        assert result.stdout == "claim_invalid|1|0|absent|absent|absent|absent|absent|false"
    elif boundary == "transport":
        assert result.stdout == "claim_invalid|1|0|failed|claim_invalid|false|not_run|failed:claim_invalid|false"
    else:
        assert result.stdout == "reset_failed|1|0|failed|transport_failed|true|read_only_failed|failed:transport_failed|false"


def test_round13_fresh_claim_gate_is_adjacent_to_actual_process_start():
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    launch = source[source.index("function Start-Phase15AuthorizedSshProcess") : source.index("function Invoke-Phase15OneSshTransport")]
    transport = source[source.index("function Invoke-Phase15OneSshTransport") : source.index("function Write-Phase15CreateNewJson")]

    attempted = launch.index("-Phase 'transport_attempted'")
    lifetime = launch.index("Test-Phase15FutureClaim")
    reset = launch.index("Reset-Phase15UnstartedTransaction")
    process_start = launch.index("$Process.Start()")
    assert attempted < lifetime < reset < process_start
    assert "Assert-Phase15LocalExecutable" not in launch[lifetime:process_start]
    assert "Write-Phase15AtomicJson" not in launch[lifetime:process_start]
    assert "[DateTimeOffset]::UtcNow" not in transport
    assert "-Claim $Claim" in transport


@pytest.mark.parametrize(
    "mutation",
    [
        "$journal.PSObject.Properties.Remove('schema')",
        "$journal | Add-Member -MemberType NoteProperty -Name unexpected -Value 'x'",
        "$journal.schema='wrong'",
        "$journal.manifest_sha256='0'",
        "$journal.manifest_sha256=('c'*64 -join '')",
        "$journal.collector_sha256='0'",
        "$journal.collector_sha256=('d'*64 -join '')",
        "$journal.expected_host='bad host'",
        "$journal.expected_host='other.test.invalid'",
        "$journal.outcome_path='relative.json'",
        "$journal.outcome_path=[IO.Path]::GetFullPath($journal.outcome_path+'.other')",
        "$journal.staged_path=$journal.outcome_path+'.wrong'",
        "$journal.PSObject.Properties.Remove('started_at')",
        "$journal.started_at=1",
        "$journal.started_at='not-a-time'",
        "$journal.reserved_at='not-a-time'",
        "$journal.reserved_at='2026-08-16T00:00:01Z'",
        "$journal.terminal_reason_code='claim_invalid'",
    ],
)
def test_round15_malformed_owned_or_partial_reset_journal_is_always_conservative(tmp_path: Path, mutation: str):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$lock=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' "
        f"-ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        f"$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath; {mutation}; "
        "$null=Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        f"$conservative=Test-Phase15TransactionRequiresConservativeSshUsed -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ReservedAt '2026-08-16T00:00:00Z' -Lock $lock; "
        "$journal.phase='transport_attempted'; $journal.ssh_used=$true; $null=Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        f"$resetRejected=$false; try{{$null=Reset-Phase15UnstartedTransaction -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ReservedAt '2026-08-16T00:00:00Z' -Lock $lock}}catch{{$resetRejected=$true}}; "
        "$tx.OutcomeLock.Stream.Dispose(); $lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$($conservative.ToString().ToLowerInvariant())|$($resetRejected.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|true"


def test_round16_real_catch_never_publishes_to_malformed_journal_staged_path(tmp_path: Path):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_at = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expires_at = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    valid_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    off_path = str(tmp_path / "attacker-selected.json").replace("'", "''")
    result = run_powershell(
        "$FutureAuthorization=$true; $FutureClaimPath='synthetic-claim.json'; $PackageRoot='C:\\synthetic-package'; "
        f"$OutcomePath='{outcome}'; $ExpectedHost='spain.test.invalid'; $script:stateRoot='{state_root}'; $script:offPath=[IO.Path]::GetFullPath('{off_path}'); $script:offPathWrites=0; $script:unboundTerminalWrites=0; "
        "foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes')){$null=[IO.Directory]::CreateDirectory((Join-Path $script:stateRoot $leaf))}; "
        "$script:clock=[Collections.Generic.Queue[DateTimeOffset]]::new(); "
        f"foreach($value in @('{valid_at}','{valid_at}','{expires_at}')){{$script:clock.Enqueue([DateTimeOffset]::ParseExact($value,'yyyy-MM-ddTHH:mm:ssZ',[Globalization.CultureInfo]::InvariantCulture,[Globalization.DateTimeStyles]::AssumeUniversal))}}; "
        "$script:Phase15AuthorizationClock={if($script:clock.Count -eq 0){throw 'clock_exhausted'};$script:clock.Dequeue()}; "
        f"$script:claim=[pscustomobject][ordered]@{{claim_id='phase15-preflight-test-001';collector_sha256='{COLLECTOR_SHA256}';consumed_at=$null;expected_host='spain.test.invalid';expires_at='{expires_at}';future_gate='PREFLIGHT';issued_at='{issued_at}';manifest_sha256='{MANIFEST_SHA256}';package_id='{PACKAGE_ID}';schema='amn2.phase15.readonly-preflight-claim.v1';status='issued'}}; "
        f"function Read-Phase15ManifestArtifact{{[pscustomobject]@{{Value=[pscustomobject]@{{package_id='{PACKAGE_ID}';entries=@([pscustomobject]@{{path='tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh';sha256='{COLLECTOR_SHA256}'}})}};Sha256='{MANIFEST_SHA256}'}}}}; "
        f"function Read-Phase15CollectorArtifact{{[pscustomobject]@{{Bytes=[byte[]]@(1);Sha256='{COLLECTOR_SHA256}'}}}}; "
        "function Assert-Phase15SpainTrustBundle{param($ExpectedHost)[pscustomobject]@{Validated=$true}}; function Read-Phase15FutureClaim{param($ClaimPath)$script:claim}; function Initialize-Phase15ProductionStateRoot{$script:stateRoot}; function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}; function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        "$script:originalAtomicJson=${function:Write-Phase15AtomicJson}; function Write-Phase15AtomicJson{param($Path,$Value,$OwnerId) if($null -ne $Value.terminal_ended_at -and $Value.staged_path -ceq $script:offPath){$script:unboundTerminalWrites++}; & $script:originalAtomicJson -Path $Path -Value $Value -OwnerId $OwnerId}; "
        "function Write-Phase15CreateNewJson{param($Path,$Value,$OwnerId) if([IO.Path]::GetFullPath($Path) -ceq $script:offPath){$script:offPathWrites++}; Write-Phase15AtomicCreateNewJson -Path $Path -Value $Value -OwnerId $OwnerId}; "
        "function Reset-Phase15UnstartedTransaction{param($TransactionPath,$ClaimId,$ManifestSha256,$CollectorSha256,$ExpectedHost,$ExpectedOutcomePath,$ReservedAt,$Lock) $journal=ConvertFrom-Phase15CanonicalJsonFile -Path $TransactionPath; $journal.staged_path=$script:offPath; Write-Phase15AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId; throw 'reset_failed'}; "
        "function Invoke-Phase15OneSshTransport{param($ExpectedHost,$CollectorBytes,$Claim,$ClaimId,$ManifestSha256,$CollectorSha256,$ExpectedOutcomePath,$ReservedAt,[ref]$Started,$TransactionPath,$Lock) $process=[pscustomobject]@{}; $process|Add-Member -MemberType ScriptMethod -Name Start -Value {throw 'ssh_must_not_start'}; [void](Start-Phase15AuthorizedSshProcess -Process $process -Claim $Claim -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -TransactionPath $TransactionPath -Lock $Lock)}; "
        "$message='';try{Invoke-Phase15RunnerMain}catch{$message=$_.Exception.Message}; $journalPath=Get-Phase15TransactionPath -StateRoot $script:stateRoot -ClaimId $script:claim.claim_id; $lifecyclePath=Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $script:stateRoot 'claims') -ClaimId $script:claim.claim_id; "
        "$terminal=ConvertFrom-Phase15CanonicalJsonFile -Path $OutcomePath; $lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $lifecyclePath; $offExists=(Test-Path -LiteralPath $script:offPath).ToString().ToLowerInvariant(); $journalExists=(Test-Path -LiteralPath $journalPath).ToString().ToLowerInvariant(); "
        "[Console]::Out.Write(\"$message|$script:offPathWrites|$script:unboundTerminalWrites|$offExists|$($terminal.reason_code)|$($terminal.safety.ssh_used.ToString().ToLowerInvariant())|$($terminal.transport_disposition)|$($lifecycle.status):$($lifecycle.reason_code)|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "reset_failed|0|0|false|transport_failed|true|read_only_failed|failed:transport_failed|false"


@pytest.mark.parametrize(
    "mutation",
    [
        f"$journal.manifest_sha256='{'c' * 64}'",
        f"$journal.collector_sha256='{'d' * 64}'",
        "$journal.expected_host='other.test.invalid'",
        "$journal.reserved_at='2026-08-16T00:00:01Z'",
    ],
)
def test_round17_real_catch_never_reconciles_valid_looking_forged_binding(tmp_path: Path, mutation: str):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_at = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expires_at = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    valid_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        "$FutureAuthorization=$true; $FutureClaimPath='synthetic-claim.json'; $PackageRoot='C:\\synthetic-package'; "
        f"$OutcomePath='{outcome}'; $ExpectedHost='spain.test.invalid'; $script:stateRoot='{state_root}'; "
        "foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){$null=[IO.Directory]::CreateDirectory((Join-Path $script:stateRoot $leaf))}; "
        "$script:clock=[Collections.Generic.Queue[DateTimeOffset]]::new(); "
        f"foreach($value in @('{valid_at}','{valid_at}','{expires_at}')){{$script:clock.Enqueue([DateTimeOffset]::ParseExact($value,'yyyy-MM-ddTHH:mm:ssZ',[Globalization.CultureInfo]::InvariantCulture,[Globalization.DateTimeStyles]::AssumeUniversal))}}; "
        "$script:Phase15AuthorizationClock={if($script:clock.Count -eq 0){throw 'clock_exhausted'};$script:clock.Dequeue()}; "
        f"$script:claim=[pscustomobject][ordered]@{{claim_id='phase15-preflight-test-001';collector_sha256='{COLLECTOR_SHA256}';consumed_at=$null;expected_host='spain.test.invalid';expires_at='{expires_at}';future_gate='PREFLIGHT';issued_at='{issued_at}';manifest_sha256='{MANIFEST_SHA256}';package_id='{PACKAGE_ID}';schema='amn2.phase15.readonly-preflight-claim.v1';status='issued'}}; "
        f"function Read-Phase15ManifestArtifact{{[pscustomobject]@{{Value=[pscustomobject]@{{package_id='{PACKAGE_ID}';entries=@([pscustomobject]@{{path='tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh';sha256='{COLLECTOR_SHA256}'}})}};Sha256='{MANIFEST_SHA256}'}}}}; "
        f"function Read-Phase15CollectorArtifact{{[pscustomobject]@{{Bytes=[byte[]]@(1);Sha256='{COLLECTOR_SHA256}'}}}}; "
        "function Assert-Phase15SpainTrustBundle{param($ExpectedHost)[pscustomobject]@{Validated=$true}}; function Read-Phase15FutureClaim{param($ClaimPath)$script:claim}; function Initialize-Phase15ProductionStateRoot{$script:stateRoot}; function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}; function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        f"function Reset-Phase15UnstartedTransaction{{param($TransactionPath,$ClaimId,$ManifestSha256,$CollectorSha256,$ExpectedHost,$ExpectedOutcomePath,$ReservedAt,$Lock) $journal=ConvertFrom-Phase15CanonicalJsonFile -Path $TransactionPath; {mutation}; Write-Phase15AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId; throw 'reset_failed'}}; "
        "function Invoke-Phase15OneSshTransport{param($ExpectedHost,$CollectorBytes,$Claim,$ClaimId,$ManifestSha256,$CollectorSha256,$ExpectedOutcomePath,$ReservedAt,[ref]$Started,$TransactionPath,$Lock) $process=[pscustomobject]@{}; $process|Add-Member -MemberType ScriptMethod -Name Start -Value {throw 'ssh_must_not_start'}; [void](Start-Phase15AuthorizedSshProcess -Process $process -Claim $Claim -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -TransactionPath $TransactionPath -Lock $Lock)}; "
        "$message='';try{Invoke-Phase15RunnerMain}catch{$message=$_.Exception.Message}; $journalPath=Get-Phase15TransactionPath -StateRoot $script:stateRoot -ClaimId $script:claim.claim_id; $lifecyclePath=Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $script:stateRoot 'claims') -ClaimId $script:claim.claim_id; "
        "$journalExists=(Test-Path -LiteralPath $journalPath).ToString().ToLowerInvariant(); $outcomeDoc=ConvertFrom-Phase15CanonicalJsonFile -Path $OutcomePath; $lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $lifecyclePath; $isTerminal=$null -ne $outcomeDoc -and @($outcomeDoc.PSObject.Properties.Name) -contains 'reason_code'; $terminal=$isTerminal.ToString().ToLowerInvariant(); $outcomeState=if($isTerminal){'terminal'}elseif($null -eq $outcomeDoc){'absent'}else{$outcomeDoc.status}; "
        "[Console]::Out.Write(\"$message|$terminal|$outcomeState|$($lifecycle.status)|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|false|reserved|reserved|true"


def test_round17_trusted_outcome_parent_facts_reject_off_root_reparse_and_unapproved_writer():
    result = run_powershell(
        "$authorized='S-1-5-21-1000'; $stateRoot='C:\\ProgramData\\AMN2\\phase15\\readonly-preflight'; $outcome=$stateRoot+'\\outcomes\\result.json'; $parent=$stateRoot+'\\outcomes'; "
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl; $inherit=3; function New-Rule($sid){[pscustomobject]@{Sid=$sid;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}}; $rules=@((New-Rule $authorized),(New-Rule 'S-1-5-18'),(New-Rule 'S-1-5-32-544')); "
        "$valid=[pscustomobject]@{Exists=$true;FullName=$parent;IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=$rules}; $reparse=$valid.PSObject.Copy();$reparse.IsReparse=$true; $offRoot=$valid.PSObject.Copy();$offRoot.FullName='C:\\Synthetic\\outcomes'; $writer=$valid.PSObject.Copy();$writer.Rules=@($rules+[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}); "
        "$a=Test-Phase15TrustedOutcomeParentFacts -Facts $valid -StateRoot $stateRoot -OutcomePath $outcome -AuthorizedSid $authorized; $b=Test-Phase15TrustedOutcomeParentFacts -Facts $reparse -StateRoot $stateRoot -OutcomePath $outcome -AuthorizedSid $authorized; $c=Test-Phase15TrustedOutcomeParentFacts -Facts $offRoot -StateRoot $stateRoot -OutcomePath $outcome -AuthorizedSid $authorized; $d=Test-Phase15TrustedOutcomeParentFacts -Facts $writer -StateRoot $stateRoot -OutcomePath $outcome -AuthorizedSid $authorized; "
        "[Console]::Out.Write(\"$($a.ToString().ToLowerInvariant())|$($b.ToString().ToLowerInvariant())|$($c.ToString().ToLowerInvariant())|$($d.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false|false"


def test_round17_publisher_stops_if_trusted_outcome_parent_changes_before_replace(tmp_path: Path):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}'; foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$authorized='S-1-5-21-1000'; $lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'transport_attempted' -Lock $lock; $script:parentChecks=0; "
        "function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)$script:parentChecks++;if($script:parentChecks -eq 3){throw 'outcome_parent_invalid'};[IO.Path]::GetFullPath($OutcomePath)}; function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        f"$failure=New-Phase15FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true; "
        f"$message='';try{{Publish-Phase15TerminalOutcome -LifecyclePath $tx.LifecyclePath -ReservationPath $tx.ReservationPath -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'transport_failed' -Outcome $failure -TransactionPath $tx.JournalPath -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ReservedAt '2026-08-16T00:00:00Z' -StateRoot $stateRoot -AuthorizedSid $authorized -Lock $lock -OutcomeLock $tx.OutcomeLock}}catch{{$message=$_.Exception.Message}}; "
        "$outcomeDoc=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath; $lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.LifecyclePath; $staged=(Test-Path -LiteralPath $tx.StagedPath).ToString().ToLowerInvariant(); $journal=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant(); $tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$message|$script:parentChecks|$($outcomeDoc.status)|$($lifecycle.status)|$staged|$journal\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "outcome_parent_invalid|3|reserved|failed|false|true"


@pytest.mark.parametrize(
    ("target", "raw"),
    [
        ("lifecycle", "{"),
        ("lifecycle", '{"claim_id":"phase15-preflight-test-001", "reason_code":"not_applicable","reserved_at":"2026-08-16T00:00:00Z","status":"reserved"}\n'),
        ("lifecycle", '{"status":"unknown"}\n'),
        ("lifecycle", '{"claim_id":"phase15-preflight-test-001","ended_at":"2026-08-16T00:00:02Z","reason_code":"not_applicable","status":"Completed"}\n'),
        ("lifecycle", '{"claim_id":"phase15-preflight-test-001","ended_at":"2026-08-16T00:00:02Z","reason_code":"transport_failed","status":"Failed"}\n'),
        ("outcome", "{"),
        ("outcome", '{"claim_id":"phase15-preflight-test-001", "reserved_at":"2026-08-16T00:00:00Z","status":"reserved"}\n'),
        ("outcome", '{"status":"unknown"}\n'),
    ],
)
def test_round18_reconcile_preserves_existing_malformed_or_noncanonical_reservation(tmp_path: Path, target: str, raw: str):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    encoded = base64.b64encode(raw.encode()).decode()
    result = run_powershell(
        f"$lock=Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        f"$target=if('{target}' -ceq 'lifecycle'){{$tx.LifecyclePath}}else{{$tx.ReservationPath}}; $raw=[Convert]::FromBase64String('{encoded}'); [IO.File]::WriteAllBytes($target,$raw); "
        "$message='';try{$null=Reconcile-Phase15Transaction -StateRoot $tx.JournalPath.Replace('\\transactions\\phase15-preflight-test-001.json','') -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock}catch{$message=$_.Exception.Message}; "
        "$same=[Convert]::ToBase64String([IO.File]::ReadAllBytes($target)) -ceq [Convert]::ToBase64String($raw); $journal=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant(); $recovery=Get-Phase15LifecyclePath -LifecycleRoot (Join-Path ([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($tx.JournalPath))) 'recovery-outcomes') -ClaimId 'phase15-preflight-test-001'; $recoveryExists=(Test-Path -LiteralPath $recovery).ToString().ToLowerInvariant(); $tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose(); "
        "[Console]::Out.Write(\"$message|$journal|$($same.ToString().ToLowerInvariant())|$recoveryExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|true|true|false"


@pytest.mark.parametrize("case", ["off_path", "invalid_pair", "recovery_completed", "current_invalid_outcome"])
def test_round18_reconcile_rejects_forged_terminal_semantics_without_deleting_journal(tmp_path: Path, case: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    forged = str(tmp_path / "forged.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        "$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        f"$recovery=Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $stateRoot 'recovery-outcomes') -ClaimId 'phase15-preflight-test-001';$terminalPath=if('{case}' -ceq 'off_path'){{'{forged}'}}elseif('{case}' -ceq 'recovery_completed'){{$recovery}}else{{$tx.ReservationPath}};$status=if('{case}' -in @('off_path','current_invalid_outcome')){{'failed'}}else{{'completed'}};$reason=if('{case}' -ceq 'recovery_completed'){{'not_applicable'}}else{{'transport_failed'}}; "
        "$published=[ordered]@{marker='forged'};Write-Phase15AtomicJson -Path $terminalPath -Value $published -OwnerId 'phase15-preflight-test-001';Write-Phase15AtomicJson -Path $tx.LifecyclePath -Value ([ordered]@{claim_id='phase15-preflight-test-001';ended_at='2026-08-16T00:00:02Z';reason_code=$reason;status=$status}) -OwnerId 'phase15-preflight-test-001';$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.phase='finalizing';$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $published;$journal.terminal_path=$terminalPath;$journal.terminal_reason_code=$reason;$journal.terminal_status=$status;Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        f"$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized}}catch{{$message=$_.Exception.Message}}; "
        "$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$terminalExists=(Test-Path -LiteralPath $terminalPath).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$journalExists|$terminalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|true|true"


def test_round18_terminal_journal_binding_derives_recovery_path_from_state_identity(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "state" / "outcomes" / "outcome.json").replace("'", "''")
    forged_recovery = str(tmp_path / "forged-recovery.json").replace("'", "''")
    result = run_powershell(
        f"$journal=[pscustomobject]@{{phase='finalizing';terminal_path='{forged_recovery}';terminal_status='failed';terminal_reason_code='transport_failed';terminal_ended_at='2026-08-16T00:00:02Z';terminal_outcome_sha256=('a'*64)}}; "
        f"$accepted=Test-Phase15ExactTerminalJournalBinding -Journal $journal -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -ExpectedOutcomePath '{outcome}' -RecoveryOutcomePath '{forged_recovery}'; "
        "[Console]::Out.Write($accepted.ToString().ToLowerInvariant())"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false"


def test_round19_published_evidence_rejects_mixed_case_decision():
    document = valid_collector_document()
    result = runner_document_result(
        document,
        "$evidence=ConvertTo-Phase15Evidence -Document $document -ManifestSha256 ('a'*64) -CollectorSha256 ('b'*64) -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z'; "
        "$evidence=ConvertFrom-Phase15CanonicalJsonText -Text ((ConvertTo-Phase15CanonicalJsonText -Value $evidence)+\"`n\"); "
        "$journal=[pscustomobject]@{manifest_sha256=('a'*64);collector_sha256=('b'*64);expected_host='spain.test.invalid';terminal_status='completed';terminal_reason_code='not_applicable';terminal_ended_at='2026-08-16T00:00:02Z';ssh_used=$true}; "
        "$lower=Test-Phase15ExactPublishedTerminalOutcome -Document $evidence -Journal $journal;$evidence.decision='PASS';$mixed=Test-Phase15ExactPublishedTerminalOutcome -Document $evidence -Journal $journal; [Console]::Out.Write(\"$($lower.ToString().ToLowerInvariant())|$($mixed.ToString().ToLowerInvariant())\")",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false"


@pytest.mark.parametrize("crash_point", ["tuple", "staged", "lifecycle", "finalizing", "replaced"])
def test_round19_reconcile_completes_only_exact_legitimate_partial_publication(tmp_path: Path, crash_point: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome_path = state_root_path / "outcomes" / "outcome.json"
    outcome = str(outcome_path).replace("'", "''")
    setup = ""
    if crash_point in {"staged", "lifecycle", "finalizing", "replaced"}:
        setup += "Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId 'phase15-preflight-test-001'; "
    if crash_point in {"lifecycle", "finalizing", "replaced"}:
        setup += "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'outcome_staged' -Lock $lock; $null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId 'phase15-preflight-test-001' -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed'; "
    if crash_point in {"finalizing", "replaced"}:
        setup += "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'finalizing' -Lock $lock; "
    if crash_point == "replaced":
        setup += "$backup=$tx.ReservationPath+'.phase15-test-backup';[IO.File]::Replace($tx.StagedPath,$tx.ReservationPath,$backup,$true);if(Test-Path -LiteralPath $backup){[IO.File]::Delete($backup)}; "
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        "$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'ssh_started' -Lock $lock; "
        f"$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true; "
        "$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        f"{setup}"
        f"$message='';$reconciled=$null;try{{$reconciled=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized}}catch{{$message=$_.Exception.Message}}; "
        "$published=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.LifecyclePath;$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$stagedExists=(Test-Path -LiteralPath $tx.StagedPath).ToString().ToLowerInvariant();$outcomeReason=if($null-ne$published-and@($published.PSObject.Properties.Name)-ccontains'reason_code'){$published.reason_code}else{'absent'};$outcomeSsh=if($null-ne$published-and@($published.PSObject.Properties.Name)-ccontains'safety'){$published.safety.ssh_used}else{$false};$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose(); "
        "[Console]::Out.Write((@{message=$message;recovered=($null-ne$reconciled-and$reconciled.Recovered);journal=$journalExists;staged=$stagedExists;outcome_reason=$outcomeReason;outcome_ssh=$outcomeSsh;lifecycle_status=$lifecycle.status;lifecycle_reason=$lifecycle.reason_code} | ConvertTo-Json -Compress))"
    )

    assert result.returncode == 0, result.stderr
    state = json.loads(result.stdout)
    assert state == {
        "journal": "false",
        "lifecycle_reason": "transport_failed" if crash_point == "tuple" else "collector_failed",
        "lifecycle_status": "failed",
        "message": "",
        "outcome_reason": "transport_failed" if crash_point == "tuple" else "collector_failed",
        "outcome_ssh": True,
        "recovered": True,
        "staged": "false",
    }


@pytest.mark.parametrize("case", ["staged_digest", "lifecycle_mismatch", "published_wrong_phase"])
def test_round19_reconcile_preserves_mixed_partial_publication_for_manual_recovery(tmp_path: Path, case: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome_path = state_root_path / "outcomes" / "outcome.json"
    outcome = str(outcome_path).replace("'", "''")
    setup = "Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId 'phase15-preflight-test-001'; "
    if case == "staged_digest":
        setup += "$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_outcome_sha256=('f'*64);Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
    elif case == "lifecycle_mismatch":
        setup += "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'outcome_staged' -Lock $lock;$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId 'phase15-preflight-test-001' -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'transport_failed'; "
    else:
        setup += "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'outcome_staged' -Lock $lock;$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId 'phase15-preflight-test-001' -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed';$backup=$tx.ReservationPath+'.phase15-test-backup';[IO.File]::Replace($tx.StagedPath,$tx.ReservationPath,$backup,$true);if(Test-Path -LiteralPath $backup){[IO.File]::Delete($backup)}; "
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId 'phase15-preflight-test-001' -Phase 'ssh_started' -Lock $lock; "
        f"$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId 'phase15-preflight-test-001'; "
        f"{setup}"
        f"$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized}}catch{{$message=$_.Exception.Message}}; "
        "$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$stagedExists=Test-Path -LiteralPath $tx.StagedPath -PathType Leaf;$outcomeDoc=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$published=($null-ne$outcomeDoc-and@($outcomeDoc.PSObject.Properties.Name)-ccontains'reason_code');$durable=($stagedExists-or$published).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$journalExists|$durable\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|true|true"


def test_round18_outcomes_namespace_lock_serializes_cooperating_runners(tmp_path: Path):
    state_root = str(tmp_path / "state").replace("'", "''")
    result = run_powershell(
        f"$null=[IO.Directory]::CreateDirectory((Join-Path '{state_root}' 'outcome-locks'));$first=Enter-Phase15OutcomesNamespaceLock -StateRoot '{state_root}';$busy='';try{{$null=Enter-Phase15OutcomesNamespaceLock -StateRoot '{state_root}'}}catch{{$busy=$_.Exception.Message}};$first.Stream.Dispose();$second=Enter-Phase15OutcomesNamespaceLock -StateRoot '{state_root}';$secondOk=$second.Stream.CanWrite;$second.Stream.Dispose();[Console]::Out.Write(\"$busy|$($secondOk.ToString().ToLowerInvariant())\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "outcome_namespace_busy|true"


@pytest.mark.parametrize("failure_at", [2, 3, 4, 5, 6])
def test_round18_reconcile_revalidates_managed_chain_before_each_cleanup_or_write(tmp_path: Path, failure_at: int):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001'; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$script:checks=0; "
        "function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$script:checks++;"
        f"if($script:checks -eq {failure_at}){{throw 'state_root_changed'}};$StateRoot}}; "
        f"$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid 'S-1-5-21-1000'}}catch{{$message=$_.Exception.Message}};$journal=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$script:checks|$journal\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"state_root_changed|{failure_at}|true"


@pytest.mark.parametrize("decision", ["PASS", "STOP"])
def test_round20_collector_ingress_rejects_mixed_case_before_evidence_publication(decision: str):
    document = valid_collector_document()
    document["decision"] = decision
    result = runner_document_result(
        document,
        "$valid=Test-Phase15CollectorDocument -Document $document -ExpectedHost 'spain.test.invalid' "
        "-ExpectedClaimId 'phase15-preflight-test-001' -ExpectedManifestSha256 ('a'*64) "
        "-ExpectedCollectorSha256 ('b'*64) -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z'; "
        "$published=$false;if($valid){$null=ConvertTo-Phase15Evidence -Document $document -ManifestSha256 ('a'*64) -CollectorSha256 ('b'*64) -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z';$published=$true};"
        "[Console]::Out.Write(\"$($valid.ToString().ToLowerInvariant())|$($published.ToString().ToLowerInvariant())\")",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false|false"


@pytest.mark.parametrize("lifecycle_state", ["reserved", "terminal"])
def test_round20_current_finalizing_transport_failure_reconstructs_missing_outcome(
    tmp_path: Path, lifecycle_state: str
):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    terminalize = (
        "$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId $claimId -Status 'failed' "
        "-EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'transport_failed'; "
        if lifecycle_state == "terminal"
        else ""
    )
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}; "
        "$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'transport_attempted' -Lock $lock; "
        f"$failure=New-Phase15FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true; "
        "$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.phase='finalizing';$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='transport_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId; "
        f"{terminalize}"
        f"$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized}}catch{{$message=$_.Exception.Message}}; "
        "$published=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.LifecyclePath;$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$($published.reason_code)|$($published.safety.ssh_used.ToString().ToLowerInvariant())|$($lifecycle.status):$($lifecycle.reason_code)|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "|transport_failed|true|failed:transport_failed|false"


@pytest.mark.parametrize("phase", ["owned", "transport_attempted"])
def test_round20_early_terminal_staged_write_is_exactly_recoverable(tmp_path: Path, phase: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    reason = "claim_invalid" if phase == "owned" else "transport_failed"
    ssh_used = "$false" if phase == "owned" else "$true"
    advance = (
        "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'transport_attempted' -Lock $lock; "
        if phase == "transport_attempted"
        else ""
    )
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}}; "
        "$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)};function Assert-Phase15TrustedManagedStateChain{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;{advance}"
        f"$failure=New-Phase15FailureOutcome -ReasonCode '{reason}' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed {ssh_used};$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='{reason}';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId $claimId; "
        f"$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized}}catch{{$message=$_.Exception.Message}};$published=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$lifecycle=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.LifecyclePath;$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$($published.reason_code)|$($published.safety.ssh_used.ToString().ToLowerInvariant())|$($lifecycle.status):$($lifecycle.reason_code)|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"|{reason}|{'false' if phase == 'owned' else 'true'}|failed:{reason}|false"


@pytest.mark.parametrize("state", ["staged", "finalizing", "replaced"])
def test_round20_terminal_resume_requires_current_immutable_bindings(tmp_path: Path, state: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    setup = "Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId $claimId; "
    if state in {"finalizing", "replaced"}:
        setup += "$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'outcome_staged' -Lock $lock;$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId $claimId -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed';$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'finalizing' -Lock $lock; "
    if state == "replaced":
        setup += "$backup=$tx.ReservationPath+'.phase15-test-backup';[IO.File]::Replace($tx.StagedPath,$tx.ReservationPath,$backup,$true);if(Test-Path -LiteralPath $backup){[IO.File]::Delete($backup)}; "
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'ssh_started' -Lock $lock; "
        f"$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;{setup}"
        "$message='';try{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock}catch{$message=$_.Exception.Message};$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$journalExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|true"


def test_round20_published_recovery_cleans_exact_owned_reservation_and_recovery_backups(tmp_path: Path):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}};function Assert-Phase15TrustedManagedStateChain{{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'ssh_started' -Lock $lock;$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.phase='finalizing';$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId $claimId -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed';$replaceBackup=$tx.ReservationPath+'.phase15-test-backup';Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId $claimId;[IO.File]::Replace($tx.StagedPath,$tx.ReservationPath,$replaceBackup,$true);if(Test-Path -LiteralPath $replaceBackup){{[IO.File]::Delete($replaceBackup)}};$reservationBackup=$tx.ReservationPath+'.phase15-'+$claimId+'.reservation-backup-'+('a'*32);$recoveryBackup=$tx.ReservationPath+'.phase15-'+$claimId+'.recovery-backup-'+('b'*32);[IO.File]::WriteAllText($reservationBackup,'owned');[IO.File]::WriteAllText($recoveryBackup,'owned');$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized;$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$reservationExists=(Test-Path -LiteralPath $reservationBackup).ToString().ToLowerInvariant();$recoveryExists=(Test-Path -LiteralPath $recoveryBackup).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$journalExists|$reservationExists|$recoveryExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false|false|false"


def test_round21_publisher_cleans_replace_backup_before_journal_delete(tmp_path: Path):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}};function Assert-Phase15TrustedManagedStateChain{{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'ssh_started' -Lock $lock;$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$script:backupSeen=$false;function Remove-Phase15OwnedStateResidues{{param($LifecyclePath,$OutcomePath,$RecoveryOutcomePath,$ClaimId)$script:backupSeen=@([IO.Directory]::EnumerateFiles([IO.Path]::GetDirectoryName($OutcomePath),[IO.Path]::GetFileName($OutcomePath)+'.phase15-'+$ClaimId+'.reservation-backup-*')).Count -eq 1;throw 'cleanup_failed'}};$message='';try{{Publish-Phase15TerminalOutcome -LifecyclePath $tx.LifecyclePath -ReservationPath $tx.ReservationPath -OutcomePath '{outcome}' -ClaimId $claimId -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed' -Outcome $failure -TransactionPath $tx.JournalPath -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ReservedAt '2026-08-16T00:00:00Z' -StateRoot $stateRoot -AuthorizedSid $authorized -Lock $lock -OutcomeLock $tx.OutcomeLock}}catch{{$message=$_.Exception.Message}};$journal=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$published=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$($script:backupSeen.ToString().ToLowerInvariant())|$journal|$($published.reason_code)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "cleanup_failed|true|true|collector_failed"


def test_round21_published_recovery_cleans_generic_atomic_outcome_backup(tmp_path: Path):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}};function Assert-Phase15TrustedManagedStateChain{{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'ssh_started' -Lock $lock;$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.phase='finalizing';$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;$null=Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath -ClaimId $claimId -Status 'failed' -EndedAt '2026-08-16T00:00:02Z' -ReasonCode 'collector_failed';$replaceBackup=$tx.ReservationPath+'.phase15-test-backup';Write-Phase15CreateNewJson -Path $tx.StagedPath -Value $failure -OwnerId $claimId;[IO.File]::Replace($tx.StagedPath,$tx.ReservationPath,$replaceBackup,$true);if(Test-Path -LiteralPath $replaceBackup){{[IO.File]::Delete($replaceBackup)}};$atomicBackup=$tx.ReservationPath+'.phase15-'+$claimId+'.backup-'+('c'*32);[IO.File]::WriteAllText($atomicBackup,'owned');$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid $authorized;$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$backupExists=(Test-Path -LiteralPath $atomicBackup).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$journalExists|$backupExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "false|false"


def test_round21_finalizing_reconstruction_uses_persisted_actual_started_at(tmp_path: Path):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';$authorized='S-1-5-21-1000';function Assert-Phase15TrustedOutcomeParent{{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}};function Assert-Phase15TrustedManagedStateChain{{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId; "
        f"$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -StartedAt '2026-08-16T00:00:00Z' -ReservedAt '2026-08-16T00:00:07Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'transport_attempted' -Lock $lock;$failure=New-Phase15FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:09Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.phase='finalizing';$journal.terminal_ended_at='2026-08-16T00:00:09Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='transport_failed';$journal.terminal_status='failed';Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:10Z' -Lock $lock -OutcomeLock $tx.OutcomeLock -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:07Z' -AuthorizedSid $authorized;$published=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.ReservationPath;$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$($published.reason_code)|$($published.started_at)\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transport_failed|2026-08-16T00:00:00Z"


@pytest.mark.parametrize("case", ["unbound", "invalid_terminal"])
def test_round21_unbound_or_invalid_terminal_reconcile_preserves_transaction_backup(tmp_path: Path, case: str):
    state_root_path = tmp_path / "state"
    state_root = str(state_root_path).replace("'", "''")
    outcome = str(state_root_path / "outcomes" / "outcome.json").replace("'", "''")
    mutation = "$journal.terminal_status='Completed';" if case == "invalid_terminal" else ""
    bindings = (
        f" -ExpectedManifestSha256 '{MANIFEST_SHA256}' -ExpectedCollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -ExpectedOutcomePath '{outcome}' -ExpectedReservedAt '2026-08-16T00:00:00Z' -AuthorizedSid 'S-1-5-21-1000'"
        if case == "invalid_terminal"
        else ""
    )
    result = run_powershell(
        f"$stateRoot='{state_root}';foreach($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')){{$null=[IO.Directory]::CreateDirectory((Join-Path $stateRoot $leaf))}};$claimId='phase15-preflight-test-001';function Assert-Phase15TrustedOutcomeParent{{param($StateRoot,$OutcomePath,$AuthorizedSid)[IO.Path]::GetFullPath($OutcomePath)}};function Assert-Phase15TrustedManagedStateChain{{param($StateRoot,$AuthorizedSid,$RequiredChildren)$StateRoot}};$lock=Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claimId;$tx=Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath '{outcome}' -ClaimId $claimId -ReservedAt '2026-08-16T00:00:00Z' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock;$null=Set-Phase15TransactionPhase -TransactionPath $tx.JournalPath -ClaimId $claimId -Phase 'ssh_started' -Lock $lock;$failure=New-Phase15FailureOutcome -ReasonCode 'collector_failed' -ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -StartedAt '2026-08-16T00:00:00Z' -EndedAt '2026-08-16T00:00:02Z' -SshUsed $true;$journal=ConvertFrom-Phase15CanonicalJsonFile -Path $tx.JournalPath;$journal.terminal_ended_at='2026-08-16T00:00:02Z';$journal.terminal_outcome_sha256=Get-Phase15CanonicalJsonSha256 -Value $failure;$journal.terminal_path=$tx.ReservationPath;$journal.terminal_reason_code='collector_failed';$journal.terminal_status='failed';{mutation}Write-Phase15AtomicJson -Path $tx.JournalPath -Value $journal -OwnerId $claimId;$backup=$tx.JournalPath+'.phase15-'+$claimId+'.backup-'+('d'*32);[IO.File]::WriteAllText($backup,'owned');$message='';try{{$null=Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claimId -EndedAt '2026-08-16T00:00:03Z' -Lock $lock -OutcomeLock $tx.OutcomeLock{bindings}}}catch{{$message=$_.Exception.Message}};$journalExists=(Test-Path -LiteralPath $tx.JournalPath).ToString().ToLowerInvariant();$backupExists=(Test-Path -LiteralPath $backup).ToString().ToLowerInvariant();$tx.OutcomeLock.Stream.Dispose();$lock.Stream.Dispose();[Console]::Out.Write(\"$message|$journalExists|$backupExists\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "transaction_invalid|true|true"
