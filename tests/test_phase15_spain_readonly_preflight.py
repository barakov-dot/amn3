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
        f"#!/usr/bin/env bash\nexec {shlex.quote(python_path)} {shlex.quote(harness_path)} \"$@\"\n",
        encoding="utf-8",
        newline="\n",
    )
    environment = os.environ.copy()
    environment["PHASE15_PYTHON"] = str(wrapper).replace("\\", "/")
    result = subprocess.run(
        [str(BASH), str(COLLECTOR), *expected],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
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


def test_collector_requires_exact_positional_remote_envelope():
    require_file(COLLECTOR, "collector")
    env = os.environ.copy()
    env["PHASE15_PYTHON"] = sys.executable.replace("\\", "/")

    result = subprocess.run(
        [str(BASH), str(COLLECTOR)],
        check=False,
        capture_output=True,
        env=env,
        timeout=10,
    )

    assert result.returncode == 64
    assert result.stdout == b""
    assert result.stderr == b"collector_envelope_invalid\n"


def test_collector_has_no_production_fixture_environment_bypass():
    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert "PHASE15_PREFLIGHT_FIXTURE_ROOT" not in source


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
    command = collector_helper("command")
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
    assert command(["missing-binary"]) == (127, b"", b"", "unavailable")

    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError()))
    assert command(["permission-denied-binary"])[3] == "launch_failed"


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
    assert command(["synthetic"])[3] == "incomplete_output"

    release = threading.Event()
    monkeypatch.setattr(subprocess_module, "Popen", lambda *_args, **_kwargs: FakeProcess(BlockingStream(release), io.BytesIO()))
    try:
        assert command(["synthetic"])[3] == "incomplete_output"
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
    result = command(["synthetic"], timeout_seconds=0)

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
    assert '[SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "ps", "-a", "--format", "{{.Names}}"]' in require_file(COLLECTOR, "collector").read_text(encoding="utf-8")


def test_phase13_current_spain_identity_and_dedicated_docker_inventory_are_exact():
    classify = collector_helper("classify_dedicated_spain_docker")
    identity = collector_helper("current_spain_identity")()
    success = "success"
    inventory = (0, b"amn2-spain-awg\nother\n", b"", success)
    networks = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [(0, b"172.28.0.0/16\n", b"", success)]
    conflict_subnets = [(0, b"172.29.252.8/29\n", b"", success)]

    assert classify(inventory, networks, clean_subnets) == ("pass", "free", "free")
    assert classify((0, b"amn2-spain-awg3\n", b"", success), networks, clean_subnets) == ("pass", "stop", "free")
    assert classify(inventory, networks, conflict_subnets) == ("pass", "free", "stop")
    assert classify(inventory, (0, b"malformed-id\n", b"", success), clean_subnets) == ("stop", "stop", "stop")
    assert classify(inventory, networks, [(0, b"172.28.0.0/16\n", b"warning\n", success)]) == ("stop", "stop", "stop")
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
    assert '[SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "ps", "-a", "--format", "{{.Names}}"]' in source
    assert '[SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "network", "ls", "-q", "--no-trunc"]' in source


def test_candidate_inventory_combines_system_and_dedicated_docker_with_exact_absence_semantics():
    classify = collector_helper("classify_spain_docker_sources")
    success = "success"
    unavailable = (127, b"", b"", "unavailable")
    failed = (126, b"", b"permission denied\n", "launch_failed")
    clean_inventory = (0, b"other\n", b"", success)
    candidate_inventory = (0, b"amn2-spain-awg3\n", b"", success)
    network_ids = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [(0, b"172.28.0.0/16\n", b"", success)]
    conflict_subnets = [(0, b"172.29.252.8/29\n", b"", success)]
    dedicated = (clean_inventory, network_ids, clean_subnets)

    assert classify((unavailable, None, []), dedicated) == ("pass", "free", "free")
    assert classify((candidate_inventory, network_ids, clean_subnets), dedicated) == ("pass", "stop", "free")
    assert classify((clean_inventory, network_ids, conflict_subnets), dedicated) == ("pass", "free", "stop")
    assert classify((failed, None, []), dedicated) == ("stop", "stop", "stop")
    assert classify((unavailable, None, []), (unavailable, None, [])) == ("stop", "stop", "stop")

    source = require_file(COLLECTOR, "collector").read_text(encoding="utf-8")
    assert '["docker", "ps", "-a", "--format", "{{.Names}}"]' in source
    assert '["docker", "network", "ls", "-q", "--no-trunc"]' in source
    assert '[SPAIN_DOCKER, "--host", SPAIN_DOCKER_HOST, "network", "ls", "-q", "--no-trunc"]' in source


def test_strict_docker_network_ids_reject_real_default_truncation():
    parse_ids = collector_helper("_docker_network_ids")
    with pytest.raises(ValueError, match="docker network inventory"):
        parse_ids((0, b"0123456789ab\n", b"", "success"))

    fixture = json.loads((FIXTURES / "ready" / "observations.json").read_text(encoding="utf-8"))
    assert fixture["observations"]["container_capability"]["raw"] == "system-and-dedicated-docker-inventories-readable"
    assert fixture["observations"]["container_name"]["raw"] == "system-and-dedicated-stopped-container-inventories-free"


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
    assert '["systemctl", "show", CURRENT_BOT_UNIT, "--property=ActiveState", "--value"]' in source
    assert '["systemctl", "show", CURRENT_BOT_UNIT, "--property=UnitFileState", "--value"]' in source
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
    assert 'command(["iptables-save"])' in source
    assert 'command(["iptables-legacy-save"])' in source


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
    interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success)
    peer_state = (0, handshakes, b"", success)

    assert classify(container, interface, peer_state, container, now_epoch=1_700_000_000) == expected


def test_awg2_health_fails_closed_on_any_probe_error():
    classify = collector_helper("classify_awg2_health")
    failed = (1, b"", b"failed", "command_failed")
    good_container = (0, b"true|4242|0\n", b"", "success")
    good_interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", "success")
    fresh = (0, b"A" * 43 + b"=\t1699999940\n", b"", "success")

    assert classify(failed, good_interface, fresh, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, failed, fresh, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, good_interface, failed, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, good_interface, fresh, failed, now_epoch=1_700_000_000) == "stop"
    assert classify((0, b"true|4242|0\n", b"warning\n", "success"), good_interface, fresh, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, (0, b"7: awg0: <POINTOPOINT,UP>\n", b"warning\n", "success"), fresh, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, good_interface, (0, fresh[1], b"warning\n", "success"), good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, (0, b"not-awg0\n", b"", "success"), fresh, good_container, now_epoch=1_700_000_000) == "stop"
    assert classify(good_container, good_interface, (0, fresh[1].rstrip(b"\n"), b"", "success"), good_container, now_epoch=1_700_000_000) == "stop"
    assert classify((0, b"false|0|0\n", b"", "success"), good_interface, fresh, good_container, now_epoch=1_700_000_000) == "stop"


@pytest.mark.parametrize("after", [b"true|4243|0\n", b"true|4242|1\n", b"false|4242|0\n"])
def test_awg2_health_rejects_pid_restart_or_running_state_race(after: bytes):
    classify = collector_helper("classify_awg2_health")
    success = "success"
    before = (0, b"true|4242|0\n", b"", success)
    interface = (0, b"7: awg0: <POINTOPOINT,UP>\n", b"", success)
    handshakes = (0, b"A" * 43 + b"=\t1699999940\n", b"", success)

    assert classify(before, interface, handshakes, (0, after, b"", success), now_epoch=1_700_000_000) == "stop"
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
    assert main.index("$startedAt =") < main.index("Read-Phase15ManifestArtifact")
    assert main.index("Reconcile-Phase15Transaction") < main.index("$reservationAt =")
    assert main.index("$reservationAt =") < main.index("Test-Phase15FutureClaim")
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
        "spain.test.invalid",
        f"bash -s -- '{PACKAGE_ID}' '{MANIFEST_SHA256}' '{COLLECTOR_SHA256}' 'phase15-preflight-test-001' 'spain.test.invalid'",
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
    assert artifact_reader.count("[IO.File]::ReadAllBytes($Path)") == 1
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
    assert reader.count("[IO.File]::ReadAllBytes($Path)") == 1
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
    assert transport.index("$deadline") < transport.index("WriteAsync")
    assert transport.index("StandardOutput.BaseStream.ReadAsync") < transport.index("WriteAsync")
    assert transport.index("StandardError.BaseStream.ReadAsync") < transport.index("WriteAsync")
    assert "[ref]$Started" in transport
    assert transport.index("$Started.Value = $true") > transport.index("$process.Start()")


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
        "$stale = $journalPath + '.create-deadbeefdeadbeefdeadbeefdeadbeef.tmp'; [IO.File]::WriteAllBytes($stale, [byte[]](1,2,3)); "
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
        f"$failed = $false; try {{ Write-Phase15AtomicCreateNewJson -Path '{escaped}' -Value ([ordered]@{{owner='contender'}}) }} catch {{ $failed = $true }}; "
        f"$bytes = [IO.File]::ReadAllBytes('{escaped}'); $temps = @([IO.Directory]::GetFiles((Split-Path -Parent '{escaped}'), 'transaction.json.create-*.tmp')); "
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
    assert publisher.index("Set-Phase15ClaimTerminal") < publisher.index("[IO.File]::Replace")
    assert "amn2.phase15.readonly-preflight-failure.v1" in source


def test_runner_reconciles_before_atomic_transaction_ownership_and_transport():
    source = require_file(RUNNER, "runner").read_text(encoding="utf-8")
    main = source[source.index("function Invoke-Phase15RunnerMain") :]

    assert main.index("Enter-Phase15ClaimLock") < main.index("Reconcile-Phase15Transaction")
    assert main.index("Reconcile-Phase15Transaction") < main.index("Test-Phase15FutureClaim")
    assert main.index("Test-Phase15FutureClaim") < main.index("Start-Phase15Transaction")
    assert main.index("Start-Phase15Transaction") < main.index("Invoke-Phase15OneSshTransport")
    assert "-TransactionPath $transaction.JournalPath" in main
    assert "finally { $claimLock.Stream.Dispose() }" in main


@pytest.mark.parametrize(
    "crash_point",
    ["owned", "corrupt_outcome_reservation", "terminal_lifecycle", "orphan_outcome"],
)
def test_interrupted_transaction_reconciles_to_one_sanitized_terminal_failure(tmp_path: Path, crash_point: str):
    state_root = str(tmp_path / "state").replace("'", "''")
    outcome = str(tmp_path / "outcome.json").replace("'", "''")
    setup = ""
    if crash_point == "corrupt_outcome_reservation":
        setup = "[IO.File]::WriteAllText($tx.ReservationPath, '{}', [Text.UTF8Encoding]::new($false)); "
    elif crash_point == "terminal_lifecycle":
        setup = (
            "$null = Set-Phase15ClaimTerminal -LifecyclePath $tx.LifecyclePath "
            "-ClaimId 'phase15-preflight-test-001' -Status 'completed' "
            "-EndedAt '2026-08-16T00:00:01Z' -ReasonCode 'not_applicable'; "
        )
    elif crash_point == "orphan_outcome":
        setup = (
            "[IO.File]::Delete($tx.LifecyclePath); "
            "[IO.File]::WriteAllText($tx.ReservationPath, '{\"decision\":\"pass\",\"schema\":\"synthetic\"}' + [Environment]::NewLine, [Text.UTF8Encoding]::new($false)); "
        )
    result = run_powershell(
        f"$lock = Enter-Phase15ClaimLock -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001'; "
        f"$tx = Start-Phase15Transaction -StateRoot '{state_root}' -OutcomePath '{outcome}' "
        f"-ClaimId 'phase15-preflight-test-001' -ReservedAt '2026-08-16T00:00:00Z' "
        f"-ManifestSha256 '{MANIFEST_SHA256}' -CollectorSha256 '{COLLECTOR_SHA256}' -ExpectedHost 'spain.test.invalid' -Lock $lock; "
        f"{setup}"
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock; "
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
    if crash_point in {"corrupt_outcome_reservation", "orphan_outcome"}:
        assert Path(state["outcome_path"]) != tmp_path / "outcome.json"
        assert state["original_raw"] in {"{}", '{"decision":"pass","schema":"synthetic"}\r\n', '{"decision":"pass","schema":"synthetic"}\n'}
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
        + f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock; "
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
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId 'phase15-preflight-test-001' -EndedAt '2026-08-16T00:00:02Z' -Lock $lock; "
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
        f"$reconciled = Reconcile-Phase15Transaction -StateRoot '{state_root}' -ClaimId $claim.claim_id -EndedAt '2026-08-16T00:02:00Z' -Lock $lock; "
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
