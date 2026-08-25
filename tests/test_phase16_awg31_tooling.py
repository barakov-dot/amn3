from __future__ import annotations

import base64
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "phase16-awg3-family-3-1-spain-pilot-20260824-011"
SOURCE_BRANCH = "codex/phase16-awg3-family-3-1-spain-pilot"
TOOLING_BRANCH = "codex/phase16-awg3-family-3-1-spain-pilot-011"
HISTORIC_PACKAGE_003 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-003"
)
HISTORIC_PACKAGE_004 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-004"
)
HISTORIC_PACKAGE_005 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-005"
)
HISTORIC_PACKAGE_006 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-006"
)
HISTORIC_PACKAGE_007 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-007"
)
HISTORIC_PACKAGE_008 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-008"
)
HISTORIC_PACKAGE_009 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-009"
)
HISTORIC_PACKAGE_010 = (
    ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-20260824-010"
)
RUNTIME_IDENTITY = (
    "docker.io/amneziavpn/amneziawg-go@"
    "sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d"
)
CLIENT_IDENTITY = (
    "github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/"
    "AmneziaWG-3.1.202060814.apk@"
    "sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697"
)
PACKAGE_SCRIPT = ROOT / "scripts" / "phase16_awg31_package.py"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "phase16_preflight_contract.py"
CONTRACT_ROOT = ROOT / "packaging" / "phase16-awg3-family-3-1-spain-pilot-contract"
APPLICATION_STAGE = ROOT / "scripts" / "vps" / "phase16_application_stage_remote.sh"
RUNTIME_STAGE = ROOT / "scripts" / "vps" / "phase16_awg31_runtime_stage_remote.sh"
COLLECTOR = ROOT / "scripts" / "vps" / "phase16_spain_readonly_preflight_remote.sh"
RUNNER = ROOT / "scripts" / "vps" / "phase16_spain_readonly_preflight_ssh_runner.ps1"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
PHASE16_OBSERVATIONS = [
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
    "recovery_markers_phase14_phase15_phase16",
    "routes",
    "service_capability",
    "service_name",
    "state_root",
    "telegram_prerequisites",
    "udp_30002",
    "vpn_cidr_10_212_13_0_24",
]


def run_powershell(body: str):
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


def phase16_collector_document(*, observed_at: str) -> dict[str, object]:
    return {
        "blocking_reasons": [],
        "claim_id": "phase16-preflight-test-001",
        "collector_sha256": "b" * 64,
        "decision": "pass",
        "host_identity": "138.124.181.246",
        "manifest_sha256": "a" * 64,
        "observed_at": observed_at,
        "observations": [
            {
                "name": name,
                "observation_sha256": hashlib.sha256(name.encode()).hexdigest(),
                "state": "pass",
            }
            for name in PHASE16_OBSERVATIONS
        ],
        "package_id": PACKAGE_ID,
        "safety": {
            "live_mutation": False,
            "raw_output_persisted": False,
            "remote_file_written": False,
        },
        "schema": "amn2.phase16.spain-readonly-collector.v1",
    }


def phase16_runner_document_result(document: dict[str, object], expression: str):
    encoded = base64.b64encode(
        json.dumps(document, separators=(",", ":")).encode()
    ).decode()
    return run_powershell(
        "$document=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"
        + encoded
        + "'))|ConvertFrom-Json;"
        + expression
    )


def load_module(path: Path, name: str):
    if not path.is_file():
        pytest.fail(f"missing Phase 16 tooling: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def collector_python_namespace() -> dict[str, object]:
    source = COLLECTOR.read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^exec /usr/bin/python3 -I -B - \"\$1\" \"\$2\" \"\$3\" \"\$4\" \"\$5\" <<'PHASE16_PY'\n(?P<body>.*)\nPHASE16_PY$",
        source,
    )
    if match is None:
        pytest.fail("Phase 16 collector embedded Python not found")
    prefix = match.group("body").split("\ntry:\n    claim_id", 1)[0]
    namespace: dict[str, object] = {"__name__": "phase16_collector_test"}
    exec(compile(prefix, str(COLLECTOR), "exec"), namespace)
    return namespace


def collector_helper(name: str):
    helper = collector_python_namespace().get(name)
    if not callable(helper):
        pytest.fail(f"missing Phase 16 collector helper: {name}")
    return helper


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (b'ID=ubuntu\nVERSION_ID="24.04"\n', ("pass", b"ubuntu:24.04")),
        (b'ID=debian\nVERSION_ID="12"\n', ("stop", b"unsupported-os")),
        (b'ID=ubuntu\nVERSION_ID="22.04"\n', ("stop", b"unsupported-os")),
        (b'ID=ubuntu\r\nVERSION_ID="24.04"\r\n', ("stop", b"malformed-os-release")),
    ],
)
def test_phase16_spain_os_admission_is_exact_ubuntu_2404(
    raw: bytes, expected: tuple[str, bytes]
):
    assert collector_helper("classify_os_release")(raw) == expected


def test_phase16_accepts_clean_dedicated_docker_when_optional_engines_are_unavailable():
    classify = collector_helper("classify_spain_docker_sources")
    success = "success"
    unavailable = (127, b"", b"", "unavailable")
    inventory = (0, b"other\n", b"", success)
    network_ids = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [
        (
            0,
            b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.28.0.0/16"}],"Driver":"default","Options":{}}\n',
            b"",
            success,
        )
    ]
    dedicated = (inventory, network_ids, clean_subnets)

    assert classify((unavailable, None, []), dedicated, (unavailable, None, [])) == (
        "pass",
        "free",
        "free",
    )


def test_phase16_optional_container_engine_launch_failure_still_stops():
    classify = collector_helper("classify_spain_docker_sources")
    success = "success"
    unavailable = (127, b"", b"", "unavailable")
    failed = (126, b"", b"permission denied\n", "launch_failed")
    inventory = (0, b"other\n", b"", success)
    network_ids = (0, (b"a" * 64) + b"\n", b"", success)
    clean_subnets = [
        (
            0,
            b'"bridge"\t"bridge"\t{"Config":[{"Subnet":"172.28.0.0/16"}],"Driver":"default","Options":{}}\n',
            b"",
            success,
        )
    ]
    dedicated = (inventory, network_ids, clean_subnets)

    assert classify((failed, None, []), dedicated, (unavailable, None, [])) == (
        "stop",
        "stop",
        "stop",
    )


def test_phase16_awg2_probe_uses_observed_interface_and_container_mount_namespace():
    namespace = collector_python_namespace()
    build = collector_helper("awg2_runtime_command")

    assert namespace["CURRENT_AWG2_INTERFACE"] == "awgsp0"
    assert build(4242, "latest-handshakes") == [
        "/usr/bin/nsenter",
        "--mount=/proc/4242/ns/mnt",
        "--net=/proc/4242/ns/net",
        "/usr/bin/awg",
        "show",
        "awgsp0",
        "latest-handshakes",
    ]


def test_phase16_awg2_health_admits_the_observed_awgsp0_interface():
    classify = collector_helper("classify_awg2_health")
    success = "success"
    owner = (0, b"active\n", b"", success)
    container = (0, b"true|4242|59\n", b"", success)
    interface = (0, b"7: awgsp0: <POINTOPOINT,UP>\n", b"", success)
    handshakes = (0, b"A" * 43 + b"=\t1699999940\n", b"", success)

    assert classify(
        owner,
        container,
        interface,
        handshakes,
        container,
        owner,
        now_epoch=1_700_000_000,
    ) == "pass"


def test_phase16_docker_builtin_null_ipam_is_empty_only_for_host_and_none():
    parse = collector_helper("_parse_network_inspection")
    success = "success"

    host = (
        0,
        b'"host"\t"host"\t{"Config":null,"Driver":"default","Options":null}\n',
        b"",
        success,
    )
    none = (
        0,
        b'"none"\t"null"\t{"Config":null,"Driver":"default","Options":null}\n',
        b"",
        success,
    )
    custom = (
        0,
        b'"custom"\t"bridge"\t{"Config":null,"Driver":"default","Options":null}\n',
        b"",
        success,
    )

    assert parse(host) == ("host", "host", [])
    assert parse(none) == ("none", "null", [])
    with pytest.raises(ValueError, match="docker ipam config"):
        parse(custom)


def test_phase16_route_pref_enum_is_admitted_without_weakening_unknown_values():
    classify = collector_helper("classify_routes")
    success = "success"

    for preference in ("low", "medium", "high"):
        payload = canonical([{"dev": "eth0", "dst": "default", "pref": preference}])
        assert classify((0, payload, b"", success)) == ("pass", "free", "free")

    invalid = canonical([{"dev": "eth0", "dst": "default", "pref": "urgent"}])
    assert classify((0, invalid, b"", success)) == ("stop", "stop", "stop")


def test_phase16_empty_successful_legacy_iptables_backend_is_no_conflict():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    empty_legacy = (0, b"", b"", "success")

    assert classify(unavailable, unavailable, empty_legacy) == "pass"


def test_phase16_observed_nft_metainfo_types_are_admitted_without_resource_conflicts():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    observed_metainfo = (
        0,
        canonical(
            {
                "nftables": [
                    {
                        "metainfo": {
                            "json_schema_version": 1,
                            "release_name": "fixture-release",
                            "version": "fixture-version",
                        }
                    }
                ]
            }
        ),
        b"",
        "success",
    )

    assert classify(observed_metainfo, unavailable) == "pass"


@pytest.mark.parametrize(
    "metainfo",
    [
        {
            "json_schema_version": "1",
            "release_name": "fixture-release",
            "version": "fixture-version",
        },
        {
            "json_schema_version": True,
            "release_name": "fixture-release",
            "version": "fixture-version",
        },
        {
            "json_schema_version": 1,
            "release_name": 5,
            "version": "fixture-version",
        },
        {
            "json_schema_version": 1,
            "release_name": "fixture-release",
            "version": 109,
        },
        {
            "json_schema_version": 1,
            "release_name": "fixture-release",
            "unknown": "fixture-value",
            "version": "fixture-version",
        },
    ],
)
def test_phase16_nft_metainfo_contract_remains_exact_and_fail_closed(
    metainfo: dict[str, object],
):
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    nft_probe = (
        0,
        canonical({"nftables": [{"metainfo": metainfo}]}),
        b"",
        "success",
    )

    assert classify(nft_probe, unavailable) == "stop"


def test_phase16_observed_nft_expression_shapes_are_admitted_without_resource_conflicts():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    observed_safe_shapes = (
        0,
        canonical(
            {
                "nftables": [
                    {
                        "rule": {
                            "chain": "postrouting",
                            "expr": [
                                {
                                    "dnat": {
                                        "addr": "192.0.2.10",
                                        "family": "ip",
                                        "port": 443,
                                    }
                                },
                                {"limit": {"burst": 10, "per": "second", "rate": 5}},
                                {"masquerade": None},
                                {
                                    "match": {
                                        "left": {
                                            "payload": {
                                                "field": "protocol",
                                                "protocol": "ip",
                                            }
                                        },
                                        "op": "==",
                                        "right": "tcp",
                                    }
                                },
                                {
                                    "match": {
                                        "left": {"meta": {"key": "l4proto"}},
                                        "op": "==",
                                        "right": "ipv6-icmp",
                                    }
                                },
                                {
                                    "match": {
                                        "left": {"ct": {"key": "state"}},
                                        "op": "in",
                                        "right": ["established", "related"],
                                    }
                                },
                                {
                                    "match": {
                                        "left": {"ct": {"key": "status"}},
                                        "op": "in",
                                        "right": "dnat",
                                    }
                                },
                                {
                                    "match": {
                                        "left": {"meta": {"key": "oifname"}},
                                        "op": "!=",
                                        "right": "docker0",
                                    }
                                },
                                {"xt": {"name": "comment", "type": "match"}},
                            ],
                            "family": "ip",
                            "table": "nat",
                        }
                    }
                ]
            }
        ),
        b"",
        "success",
    )

    assert classify(observed_safe_shapes, unavailable) == "pass"


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"addr": "192.0.2.10", "family": "ip", "port": 443}, False),
        ({"addr": "10.212.13.42", "family": "ip", "port": 443}, True),
        ({"addr": "192.0.2.10", "family": "ip", "port": 30002}, True),
    ],
)
def test_phase16_observed_nft_dnat_preserves_address_and_port_conflict_detection(
    payload: dict[str, object], expected: bool
):
    parse = collector_helper("_parse_nft_expression")

    assert parse({"dnat": payload}) is expected


@pytest.mark.parametrize(
    "expression",
    [
        {
            "match": {
                "left": {"payload": {"field": "protocol", "protocol": "ip"}},
                "op": "==",
                "right": "tcp",
            }
        },
        {
            "match": {
                "left": {"meta": {"key": "l4proto"}},
                "op": "==",
                "right": "ipv6-icmp",
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "state"}},
                "op": "in",
                "right": ["established", "related"],
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "status"}},
                "op": "in",
                "right": "dnat",
            }
        },
        {
            "match": {
                "left": {"meta": {"key": "oifname"}},
                "op": "!=",
                "right": "docker0",
            }
        },
    ],
)
def test_phase16_observed_nft_match_contracts_are_admitted_without_resource_conflicts(
    expression: dict[str, object],
):
    parse = collector_helper("_parse_nft_expression")

    assert parse(expression) is False


@pytest.mark.parametrize("target_interface", ["awg3", "amn2sp3br0"])
def test_phase16_observed_nft_oifname_not_equal_preserves_target_conflict_detection(
    target_interface: str,
):
    parse = collector_helper("_parse_nft_expression")
    expression = {
        "match": {
            "left": {"meta": {"key": "oifname"}},
            "op": "!=",
            "right": target_interface,
        }
    }

    assert parse(expression) is True


@pytest.mark.parametrize(
    "expression",
    [
        {
            "match": {
                "left": {"payload": {"field": "protocol", "protocol": "ip"}},
                "op": "==",
                "right": "TCP",
            }
        },
        {
            "match": {
                "left": {"payload": {"field": "protocol", "protocol": "ip"}},
                "op": "==",
                "right": "a" * 17,
            }
        },
        {
            "match": {
                "left": {"payload": {"field": "protocol", "protocol": "ip6"}},
                "op": "==",
                "right": "tcp",
            }
        },
        {
            "match": {
                "left": {"meta": {"key": "l4proto"}},
                "op": "in",
                "right": "tcp",
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "state"}},
                "op": "in",
                "right": "established",
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "state"}},
                "op": "in",
                "right": [],
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "state"}},
                "op": "in",
                "right": ["established", "established"],
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "state"}},
                "op": "in",
                "right": ["established", "private-state"],
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "status"}},
                "op": "in",
                "right": "private-status",
            }
        },
        {
            "match": {
                "left": {"ct": {"key": "status"}},
                "op": "==",
                "right": "dnat",
            }
        },
        {
            "match": {
                "left": {"meta": {"key": "iifname"}},
                "op": "!=",
                "right": "docker0",
            }
        },
    ],
)
def test_phase16_observed_nft_match_contracts_remain_bounded_and_fail_closed(
    expression: dict[str, object],
):
    parse = collector_helper("_parse_nft_expression")

    with pytest.raises(ValueError, match="nft"):
        parse(expression)


@pytest.mark.parametrize(
    "expression",
    [
        {"dnat": {"addr": "192.0.2.10", "family": "ip", "port": True}},
        {"dnat": {"addr": "192.0.2.10", "extra": 1, "family": "ip", "port": 443}},
        {"limit": {"burst": 0, "per": "second", "rate": 5}},
        {"limit": {"burst": 10, "per": "", "rate": 5}},
        {"masquerade": {}},
        {"xt": {"name": "comment", "type": "match", "unknown": "value"}},
        {"xt": {"name": "bad value", "type": "match"}},
    ],
)
def test_phase16_observed_nft_expression_shapes_remain_exact_and_fail_closed(
    expression: dict[str, object],
):
    parse = collector_helper("_parse_nft_expression")

    with pytest.raises(ValueError, match="nft"):
        parse(expression)


def test_phase16_observed_successful_single_comment_iptables_is_no_conflict():
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")
    comment_only = (0, b"# iptables-save output is provided by nftables\n", b"", "success")

    assert classify(unavailable, comment_only) == "pass"


@pytest.mark.parametrize(
    "payload",
    [
        b"# first comment\n# second comment\n",
        b"# comment\nnot-a-comment\n",
        b"# non-ascii: \xff\n",
        b"# missing newline",
    ],
)
def test_phase16_comment_only_iptables_admission_remains_single_line_and_fail_closed(
    payload: bytes,
):
    classify = collector_helper("classify_firewall")
    unavailable = (127, b"", b"", "unavailable")

    assert classify(unavailable, (0, payload, b"", "success")) == "stop"


def test_phase16_telegram_prerequisite_requires_stable_active_enabled_state():
    observe = collector_helper("observe_phase13_bot_unit")
    success = "success"
    active = (0, b"active\n", b"", success)
    enabled = (0, b"enabled\n", b"", success)
    inactive = (0, b"inactive\n", b"", success)

    calls: list[list[str]] = []
    responses = iter((active, enabled, active, enabled))

    def stable_command(arguments: list[str]):
        calls.append(arguments)
        return next(responses)

    state, _raw = observe(stable_command)
    assert state == "pass"
    assert calls == [
        ["/usr/bin/systemctl", "show", "amn2-spain-bot.service", "--property=ActiveState", "--value"],
        ["/usr/bin/systemctl", "show", "amn2-spain-bot.service", "--property=UnitFileState", "--value"],
        ["/usr/bin/systemctl", "show", "amn2-spain-bot.service", "--property=ActiveState", "--value"],
        ["/usr/bin/systemctl", "show", "amn2-spain-bot.service", "--property=UnitFileState", "--value"],
    ]

    drifted = iter((active, enabled, inactive, enabled))
    state, _raw = observe(lambda _arguments: next(drifted))
    assert state == "stop"


def test_phase16_package_and_preflight_identities_are_exact():
    package = load_module(PACKAGE_SCRIPT, "phase16_package")
    preflight = load_module(PREFLIGHT_SCRIPT, "phase16_preflight")

    assert package.PACKAGE_ID == PACKAGE_ID
    assert package.SOURCE_BRANCH == SOURCE_BRANCH
    assert package.TOOLING_BRANCH == TOOLING_BRANCH
    assert package.MANIFEST_SCHEMA == "amn2.phase16.package-manifest.v1"
    assert preflight.PACKAGE_ID == PACKAGE_ID
    assert preflight.CLAIM_SCHEMA == "amn2.phase16.readonly-preflight-claim.v1"
    assert preflight.EVIDENCE_SCHEMA == "amn2.phase16.readonly-preflight-evidence.v1"
    for schema_name in (
        "failure-outcome.schema.json",
        "package-manifest.schema.json",
        "preflight-evidence.schema.json",
    ):
        schema = json.loads((CONTRACT_ROOT / schema_name).read_text(encoding="utf-8"))
        assert schema["properties"]["package_id"] == {"const": PACKAGE_ID}


def test_phase16_materializer_applies_distinct_source_and_tooling_branch_gates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    package = load_module(PACKAGE_SCRIPT, "phase16_package_branch_gates")
    source = tmp_path / "source"
    tooling = tmp_path / "tooling"
    source.mkdir()
    tooling.mkdir()
    observed: list[tuple[Path, str]] = []

    def checked_repo(root: Path, expected_branch: str):
        observed.append((Path(root), expected_branch))
        if len(observed) == 2:
            raise package.PackageContractError("halt after branch gates")
        return Path(root), "a" * 40

    monkeypatch.setattr(package, "_checked_repo", checked_repo)

    with pytest.raises(package.PackageContractError, match="halt after branch gates"):
        package.materialize_package(
            source_root=source,
            source_head="a" * 40,
            package_id=PACKAGE_ID,
            output_root=tmp_path / "package",
            tooling_root=tooling,
        )

    assert observed == [(source, SOURCE_BRANCH), (tooling, TOOLING_BRANCH)]


def test_historic_phase16_package_003_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_003 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_003
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_003
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "526ed0afda915f3ded0679a48899922c0081bf664b97849ee73f8892b205408c"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "971b2fb1d49f09c448ecbe9a33e942eb065261b21e57bc546b6e5a4043f7093a"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "6b3ed7fd32a4db2ef8c27feac4d09bb854310b7bdf9b60fbdf833b5cb2972ce6"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "d47a189a86fb4ca3a475e2ec3acde20ededf0ae12a82a2d06f8e086daef4e128"


def test_historic_phase16_package_004_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_004 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_004
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_004
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48"


def test_historic_phase16_package_005_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_005 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_005
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_005
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306"


def test_historic_phase16_package_006_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_006 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_006
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_006
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4"


def test_historic_phase16_package_007_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_007 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_007
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_007
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "24eb848d13845b4a0abf9a8200a6c30d2bd67be28ea904c8e08e1aaf830e312b"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "c3ca7538c556555121da29e2b361bc3139a6b1e76f579856416259aac7bbca37"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "7aca3daa62d0552ef533c47cbca68a1c4fcf622156423936183069d0499a9060"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2"


def test_historic_phase16_package_008_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_008 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_008
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_008
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "065d3369b8dd11783572365f06f84c6ec3ed207e71c758dea2f1d57a02baf24e"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "b2e112eec77a3a6c272be8d79c7fd010a8f54ad1f6d833002f76d1fcfba03ada"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "dfc47725248376a0c3e816a9e8681385c615cf3a713ef7cba079fbfbd8d32828"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3"


def test_historic_phase16_package_009_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_009 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_009
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_009
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "084302df340f4741109103dc7baf94601dd24163406d002b82756fde8d9c80c1"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "80b3347b8787ca1490b40f1763ccff01fb4428233ca4f240c068fd02e35cef15"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "f0d0843c05c341b340dce8721d30f55380b6a8493aff70da7013185875301fbf"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d"


def test_historic_phase16_package_010_remains_checksum_immutable():
    manifest_path = HISTORIC_PACKAGE_010 / "manifest.json"
    collector_path = (
        HISTORIC_PACKAGE_010
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_remote.sh"
    )
    runner_path = (
        HISTORIC_PACKAGE_010
        / "tooling"
        / "scripts"
        / "vps"
        / "phase16_spain_readonly_preflight_ssh_runner.ps1"
    )

    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "e79ce27b34d175495ff3f5eebb3e19b1a2cbe6c51c47493fab01113fe2a63805"
    )
    assert hashlib.sha256(collector_path.read_bytes()).hexdigest() == (
        "da54841074b70b1cdd0c2704ceefa23b81a79cae6c26e70722b7371e728efc45"
    )
    assert hashlib.sha256(runner_path.read_bytes()).hexdigest() == (
        "70cb93f165bb4578ee8d5de3bd4cc71b8b54ed66bce34352fc074aff1468742c"
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8"))[
        "package_identity_sha256"
    ] == "0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658"


def test_resource_plan_binds_awg31_runtime_client_capabilities_and_rollback():
    package = load_module(PACKAGE_SCRIPT, "phase16_package_resource")
    raw = (CONTRACT_ROOT / "resource-plan.json").read_bytes()
    value = json.loads(raw.decode("utf-8"))

    assert raw == canonical(value)
    assert value == package.RESOURCE_PLAN
    assert value["package_id"] == PACKAGE_ID
    assert value["protocol"] == {
        "config_revision": "amneziawg_v3_1",
        "family": "awg3",
        "revision": "3.1",
    }
    assert value["runtime"] == {
        "artifact_identity": RUNTIME_IDENTITY,
        "capabilities": ["disable_cookies", "random_trailers"],
        "source_commit": "1f50ad736ecca22a9bfc7b4606805ec9ca49fe48",
    }
    assert value["pilot_client"] == {
        "application": "amneziawg",
        "artifact_identity": CLIENT_IDENTITY,
        "build": "12",
        "platform": "android",
        "release_kind": "stable",
        "version": "v3.1.20260814",
    }
    assert value["controls"] == {
        "awg2_untouched": True,
        "general_issuance_enabled": False,
        "rollback_required": True,
        "stage_requires_separate_claim": True,
    }


def test_preflight_claim_remains_checksum_host_and_one_time_bound():
    contract = load_module(PREFLIGHT_SCRIPT, "phase16_preflight_claim")
    claim = {
        "claim_id": "phase16-preflight-test-001",
        "collector_sha256": "b" * 64,
        "consumed_at": None,
        "expected_host": "spain.test.invalid",
        "expires_at": "2026-08-24T13:00:00Z",
        "future_gate": "PREFLIGHT",
        "issued_at": "2025-08-24T12:00:00Z",
        "manifest_sha256": "a" * 64,
        "package_id": PACKAGE_ID,
        "schema": "amn2.phase16.readonly-preflight-claim.v1",
        "status": "issued",
    }

    validated = contract.validate_claim(
        claim,
        package_id=PACKAGE_ID,
        manifest_sha256="a" * 64,
        collector_sha256="b" * 64,
        expected_host="spain.test.invalid",
        now=dt.datetime(2026, 8, 24, 12, 30, tzinfo=dt.timezone.utc),
    )
    assert validated == claim
    changed = dict(claim, manifest_sha256="c" * 64)
    with pytest.raises(contract.PreflightContractError, match="checksum"):
        contract.validate_claim(
            changed,
            package_id=PACKAGE_ID,
            manifest_sha256="a" * 64,
            collector_sha256="b" * 64,
            expected_host="spain.test.invalid",
            now=dt.datetime(2026, 8, 24, 12, 30, tzinfo=dt.timezone.utc),
        )


def stage_claim(script: Path, gate: str, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "claim_id": "phase16-stage-test-001",
        "consumed_at": None,
        "expected_current_state_sha256": "c" * 64,
        "expires_at": "2099-08-24T13:00:00Z",
        "future_gate": gate,
        "issued_at": "2025-08-24T12:00:00Z",
        "manifest_sha256": "d" * 64,
        "package_id": PACKAGE_ID,
        "package_identity_sha256": "e" * 64,
        "rollback_scope_sha256": "f" * 64,
        "schema": "amn2.phase16.stage-claim.v1",
        "stage_script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "status": "issued",
    }
    value.update(overrides)
    return value


def local_stage(tmp_path: Path, source: Path) -> Path:
    text = source.read_text(encoding="utf-8")
    text = text.replace(
        "/usr/bin/python3 -I -B -",
        f"{shlex.quote(sys.executable.replace(chr(92), '/'))} -I -B -",
    )
    target = tmp_path / source.name
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def run_stage(tmp_path: Path, source: Path, gate: str, *, overrides: dict[str, object] | None = None):
    runtime = local_stage(tmp_path, source)
    claim_path = tmp_path / f"{gate.lower()}-claim.json"
    claim = stage_claim(runtime, gate, **(overrides or {}))
    claim_path.write_bytes(canonical(claim))
    env = os.environ.copy()
    env.update(
        {
            "PHASE16_EXPECTED_CURRENT_STATE_SHA256": "c" * 64,
            "PHASE16_FUTURE_GATE": gate,
            "PHASE16_MANIFEST_SHA256": "d" * 64,
            "PHASE16_PACKAGE_ID": PACKAGE_ID,
            "PHASE16_PACKAGE_IDENTITY_SHA256": "e" * 64,
            "PHASE16_ROLLBACK_SCOPE_SHA256": "f" * 64,
            "PHASE16_STAGE_CLAIM_FILE": str(claim_path).replace("\\", "/"),
        }
    )
    before = claim_path.read_bytes()
    result = subprocess.run(
        [str(BASH), str(runtime)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return result, before, claim_path.read_bytes()


@pytest.mark.parametrize(
    ("script", "gate"),
    ((APPLICATION_STAGE, "APPLICATION_STAGE"), (RUNTIME_STAGE, "AWG31_RUNTIME_STAGE")),
)
def test_valid_stage_claim_reaches_input_gate_without_mutation(
    tmp_path: Path, script: Path, gate: str
):
    result, before, after = run_stage(tmp_path, script, gate)

    assert result.returncode == 66
    assert result.stdout == ""
    assert result.stderr == "stage_inputs_required\n"
    assert after == before


@pytest.mark.parametrize(
    ("script", "gate"),
    ((APPLICATION_STAGE, "APPLICATION_STAGE"), (RUNTIME_STAGE, "AWG31_RUNTIME_STAGE")),
)
def test_stage_claim_rejects_wrong_rollback_binding(
    tmp_path: Path, script: Path, gate: str
):
    result, before, after = run_stage(
        tmp_path, script, gate, overrides={"rollback_scope_sha256": "0" * 64}
    )

    assert result.returncode == 65
    assert result.stdout == ""
    assert result.stderr == "claim_invalid\n"
    assert after == before


def test_application_stage_is_backup_first_claim_bound_and_rollback_aware():
    source = APPLICATION_STAGE.read_text(encoding="utf-8")

    assert PACKAGE_ID in source
    assert source.index("create_checksum_bound_db_backup") < source.index(
        "stage_application_snapshot"
    )
    assert "rollback_application_stage" in source
    assert "trap rollback_application_stage ERR" in source
    assert "package_identity_sha256" in source
    assert "rollback_scope_sha256" in source
    assert "ENABLE_ISSUANCE" not in source


def test_runtime_stage_is_pinned_capability_checked_and_awg2_isolated():
    source = RUNTIME_STAGE.read_text(encoding="utf-8")

    assert PACKAGE_ID in source
    assert RUNTIME_IDENTITY in source
    assert "verify_runtime_capabilities" in source
    assert "random_trailers" in source
    assert "disable_cookies" in source
    assert "rollback_awg31_stage" in source
    assert "trap rollback_awg31_stage ERR" in source
    assert "amn2-spain-awg3" in source
    assert "amn2sp3br0" in source
    assert "30002" in source
    assert re.search(r"systemctl\s+(?:restart|stop)\s+amn2-spain-awg2", source) is None
    assert re.search(r"docker\s+rm[^\n]*amn2-spain-awg2", source) is None
    assert "ENABLE_ISSUANCE" not in source


def test_phase16_preflight_transport_assets_are_read_only_and_phase_exact():
    contract = PREFLIGHT_SCRIPT.read_text(encoding="utf-8")
    collector = COLLECTOR.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    combined = "\n".join((contract, collector, runner))

    assert PACKAGE_ID in collector
    assert PACKAGE_ID in runner
    assert "phase15-dual-protocol-bootstrap-20260811-001" not in combined
    assert "recovery_markers_phase14_phase15_phase16" in contract
    assert "recovery_markers_phase14_phase15_phase16" in collector
    assert "phase14_phase16_phase16" not in combined
    assert "phase16_spain_readonly_preflight_remote.sh" in runner
    assert "$script:Phase16PackageId" in runner
    for pattern in (
        r"systemctl\s+(?:restart|stop|start|enable)\b",
        r"(?:docker|podman)\s+(?:run|rm|pull)\b",
        r"iptables\s+-(?:A|D)\b",
        r"nft\s+(?:add|delete)\b",
        r"ip\s+link\s+(?:add|delete|set)\b",
        r"\bsqlite3\s",
    ):
        assert re.search(pattern, collector, flags=re.IGNORECASE) is None


def test_phase16_ssh_process_environment_keeps_windows_openssh_runnable():
    result = run_powershell(
        "$start=New-Phase16SshProcessStartInfo -Arguments @('-V');"
        "$process=[Diagnostics.Process]::new();$process.StartInfo=$start;"
        "try{if(-not $process.Start()){throw 'ssh_start_failed'};"
        "$stdoutTask=$process.StandardOutput.ReadToEndAsync();"
        "$stderrTask=$process.StandardError.ReadToEndAsync();"
        "if(-not $process.WaitForExit(5000)){$process.Kill();throw 'ssh_timeout'};"
        "$stdout=$stdoutTask.GetAwaiter().GetResult();"
        "$stderr=$stderrTask.GetAwaiter().GetResult();"
        "[Console]::Out.Write(($process.ExitCode.ToString()+'|'+$stdout.Length.ToString()+'|'+$stderr.Trim()))"
        "}finally{$process.Dispose()}"
    )

    assert result.returncode == 0, result.stderr
    exit_code, stdout_length, version = result.stdout.split("|", 2)
    assert exit_code == "0"
    assert stdout_length == "0"
    assert version.startswith("OpenSSH_for_Windows_")


def test_phase16_byte_hash_accepts_empty_array():
    result = run_powershell(
        "$bytes=[byte[]]::new(0);"
        "[Console]::Out.Write((Get-Phase16BytesSha256 -Bytes $bytes))"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855"
    )
    assert result.stderr == ""


def test_phase16_void_task_completion_emits_no_pipeline_output():
    result = run_powershell(
        "$task=[Threading.Tasks.Task]::CompletedTask;"
        "Complete-Phase16VoidTask -Task $task;"
        "[Console]::Out.Write('clean')"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "clean"
    assert result.stderr == ""


def test_phase16_powershell5_stdin_filter_accepts_zero_or_one_bom_and_binds_hash():
    result = run_powershell(
        "$code=Get-Phase16PowerShell5StdinFilterCode;"
        "$bytes=[Text.UTF8Encoding]::new($false).GetBytes($code);"
        "[Console]::Out.Write([Convert]::ToBase64String($bytes))"
    )

    assert result.returncode == 0, result.stderr
    code = base64.b64decode(result.stdout).decode("utf-8")
    collector = b"#!/usr/bin/env bash\nprintf 'collector-ok\\n'\n"
    expected_hash = hashlib.sha256(collector).hexdigest()

    def run_filter(value: bytes):
        return subprocess.run(
            [sys.executable, "-I", "-B", "-c", code, expected_hash],
            input=value,
            capture_output=True,
            check=False,
            timeout=10,
        )

    for accepted in (collector, b"\xef\xbb\xbf" + collector):
        filtered = run_filter(accepted)
        assert filtered.returncode == 0
        assert filtered.stdout == collector
        assert filtered.stderr == b""

    for rejected in (collector + b"x", b"\xef\xbb\xbf\xef\xbb\xbf" + collector):
        filtered = run_filter(rejected)
        assert filtered.returncode == 65
        assert filtered.stdout == b""
        assert filtered.stderr == b""


def test_phase16_ssh_remote_command_uses_fail_closed_bom_filter():
    result = run_powershell(
        "$arguments=New-Phase16SshArguments -ExpectedHost '138.124.181.246' "
        "-ClaimId 'phase16-preflight-test-001' -ManifestSha256 ('a'*64) "
        "-CollectorSha256 ('b'*64);"
        "$remote=$arguments[$arguments.Count-1];"
        "$bytes=[Text.UTF8Encoding]::new($false).GetBytes($remote);"
        "[Console]::Out.Write([Convert]::ToBase64String($bytes))"
    )

    assert result.returncode == 0, result.stderr
    remote = base64.b64decode(result.stdout).decode("utf-8")
    assert remote.startswith("/usr/bin/bash -o pipefail -c '")
    assert "/usr/bin/python3 -I -B -c \"" in remote
    assert '" "$3" | /usr/bin/bash -s -- "$@"' in remote
    assert "| /usr/bin/bash -s -- \"$@\"" in remote
    assert remote.endswith(
        "' -- 'phase16-awg3-family-3-1-spain-pilot-20260824-011' "
        "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' "
        "'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' "
        "'phase16-preflight-test-001' '138.124.181.246'"
    )


@pytest.mark.parametrize(
    ("observed_at", "expected"),
    [
        ("2026-08-24T12:00:25Z", "true"),
        ("2026-08-24T12:00:26Z", "false"),
        ("2026-08-24T11:59:59Z", "false"),
    ],
)
def test_phase16_collector_window_allows_at_most_15_seconds_future_skew(
    observed_at: str, expected: str
):
    document = phase16_collector_document(observed_at=observed_at)
    result = phase16_runner_document_result(
        document,
        "$valid=Test-Phase16CollectorDocument -Document $document "
        "-ExpectedHost '138.124.181.246' "
        "-ExpectedClaimId 'phase16-preflight-test-001' "
        "-ExpectedManifestSha256 ('a'*64) -ExpectedCollectorSha256 ('b'*64) "
        "-StartedAt '2026-08-24T12:00:00Z' -EndedAt '2026-08-24T12:00:10Z';"
        "[Console]::Out.Write($valid.ToString().ToLowerInvariant())",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


@pytest.mark.parametrize("program_data", ("", r"C:\Windows"))
def test_phase16_ssh_process_environment_rejects_untrusted_programdata(program_data: str):
    escaped = program_data.replace("'", "''")
    result = run_powershell(
        f"$env:ProgramData='{escaped}';"
        "try{$null=New-Phase16SshProcessStartInfo -Arguments @('-V');"
        "[Console]::Out.Write('accepted')}"
        "catch{[Console]::Out.Write($_.Exception.Message)}"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "local_environment_invalid"


def test_existing_safe_shared_amn2_namespace_allows_managed_phase16_leaf_provisioning():
    result = run_powershell(
        "$script:events=[Collections.Generic.List[string]]::new();$script:facts=@{};"
        "$authorized='S-1-5-21-1000';$anchor='C:\\ProgramData';"
        "$root='C:\\ProgramData\\AMN2\\phase16\\readonly-preflight';"
        "$full=[int64][Security.AccessControl.FileSystemRights]::FullControl;$inherit=3;"
        "$platform=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$false;Inheritance=3;Propagation=2},"
        "[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$false;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$false;Inheritance=1;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$false;Inheritance=3;Propagation=0});"
        "$shared=@($platform|ForEach-Object{$copy=$_.PSObject.Copy();$copy.IsInherited=$true;$copy});"
        "function New-ManagedFacts($path){$rules=@('S-1-5-21-1000','S-1-5-18','S-1-5-32-544'|ForEach-Object{[pscustomobject]@{Sid=$_;Type='Allow';Rights=$full;IsInherited=$false;Inheritance=$inherit;Propagation=0}});[pscustomobject]@{Exists=$true;FullName=$path;IsDirectory=$true;IsReparse=$false;OwnerSid=$authorized;Protected=$true;Rules=$rules}};"
        "$script:facts[$anchor]=[pscustomobject]@{Exists=$true;FullName=$anchor;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-18';Protected=$true;Rules=$platform};"
        "$amn2=Join-Path $anchor 'AMN2';$script:facts[$amn2]=[pscustomobject]@{Exists=$true;FullName=$amn2;IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-32-544';Protected=$false;Rules=$shared};"
        "function Enter-Phase16StateRootCreationLock{$script:events.Add('lock');[pscustomobject]@{Acquired=$true}};"
        "function Exit-Phase16StateRootCreationLock{param($Lock)$script:events.Add('unlock')};"
        "function Get-Phase16StateDirectoryFacts{param($Path)if($script:facts.ContainsKey($Path)){return $script:facts[$Path]};[pscustomobject]@{Exists=$false;FullName=$Path}};"
        "function New-Phase16SecureStateDirectory{param($ParentPath,$Path,$AuthorizedSid)$script:events.Add('create:'+([IO.Path]::GetFileName($Path)));$script:facts[$Path]=New-ManagedFacts $Path};"
        "$message='';$actual='';$chain='';try{$actual=Initialize-Phase16TrustedStateRoot -AnchorPath $anchor -StateRoot $root -AuthorizedSid $authorized;$chain=Assert-Phase16TrustedManagedStateChain -StateRoot $root -AuthorizedSid $authorized -RequiredChildren @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')}catch{$message=$_.Exception.Message};"
        "$created=@($script:events|Where-Object{$_ -like 'create:*'}|ForEach-Object{$_.Substring(7)});"
        "[Console]::Out.Write(\"$message|$($actual -ceq $root)|$($chain -ceq $root)|$($created -join ',')\")"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "|True|True|phase16,readonly-preflight,locks,outcome-locks,claims,"
        "transactions,recovery-outcomes,outcomes"
    )


def test_shared_amn2_namespace_rejects_reparse_extra_acl_and_wrong_owner():
    result = run_powershell(
        "$rules=@([pscustomobject]@{Sid='S-1-3-0';Type='Allow';Rights=[int64]268435456;IsInherited=$true;Inheritance=3;Propagation=2},"
        "[pscustomobject]@{Sid='S-1-5-18';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-544';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]278;IsInherited=$true;Inheritance=1;Propagation=0},"
        "[pscustomobject]@{Sid='S-1-5-32-545';Type='Allow';Rights=[int64]1179817;IsInherited=$true;Inheritance=3;Propagation=0});"
        "$valid=[pscustomobject]@{Exists=$true;FullName='C:\\ProgramData\\AMN2';IsDirectory=$true;IsReparse=$false;OwnerSid='S-1-5-32-544';Protected=$false;Rules=$rules};"
        "$reparse=$valid.PSObject.Copy();$reparse.IsReparse=$true;"
        "$extra=$valid.PSObject.Copy();$extra.Rules=@($rules+[pscustomobject]@{Sid='S-1-1-0';Type='Allow';Rights=[int64]2032127;IsInherited=$true;Inheritance=3;Propagation=0});"
        "$owner=$valid.PSObject.Copy();$owner.OwnerSid='S-1-5-32-545';"
        "$values=@($valid,$reparse,$extra,$owner|ForEach-Object{(Test-Phase16SharedNamespaceDirectoryFacts -Facts $_ -ExpectedPath 'C:\\ProgramData\\AMN2').ToString().ToLowerInvariant()});"
        "[Console]::Out.Write(($values -join '|'))"
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "true|false|false|false"


def test_phase16_manifest_schema_matches_closed_package_inventory():
    package = load_module(PACKAGE_SCRIPT, "phase16_package_schema")
    schema_path = CONTRACT_ROOT / "package-manifest.schema.json"
    raw = schema_path.read_bytes()
    schema = json.loads(raw.decode("utf-8"))

    assert raw == canonical(schema)
    assert schema["$id"] == "amn2.phase16.package-manifest.v1"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["package_id"] == {"const": PACKAGE_ID}
    assert schema["properties"]["source"]["properties"]["branch"] == {
        "const": package.SOURCE_BRANCH
    }
    assert schema["properties"]["tooling"]["properties"]["branch"] == {
        "const": package.TOOLING_BRANCH
    }
    _entry_contract, closed_inventory = schema["properties"]["entries"]["items"][
        "allOf"
    ]
    fixed_paths = {
        branch["properties"]["path"]["const"]
        for branch in closed_inventory["oneOf"]
        if "const" in branch["properties"]["path"]
    }
    assert fixed_paths == set(package.REQUIRED_ENTRY_SPECS)
