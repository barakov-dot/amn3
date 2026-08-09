from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts/phase13_spain_awg2_predicate_diagnosis.py"
REMOTE = ROOT / "scripts/vps/phase13_spain_awg2_predicate_diagnosis_remote.py"
FOUNDATION = ROOT / "scripts/vps/phase13_bot_web_migration_production_stage_remote.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def future() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=2)


def good_observation(module) -> dict[str, object]:
    return {
        "configured_ip_forward_equal": True,
        "container_running": True,
        "forward_comments_equal": True,
        "forward_rule_count": 3,
        "image_present": True,
        "listen_port_equal": True,
        "live_ip_forward_equal": True,
        "live_peer_count": 7,
        "network_mode_equal": True,
        "peer_sets_equal": True,
        "persistent_peer_count": 7,
        "restart_count_current": module.EXPECTED_RESTART_COUNT,
        "route_equal": True,
        "units_active_enabled": True,
    }


def package_inputs(module):
    return module.DiagnosticPackageInputs(
        outcome_id="spain-awg2-diagnosis-test-001",
        expires_at=future(),
        tooling_head="a" * 40,
        runner_bytes=b"runner-bytes",
        remote_bytes=b"remote-bytes",
        foundation_bytes=b"foundation-bytes",
    )


def test_restart_count_only_drift_is_distinguished_from_structural_awg2_drift() -> None:
    module = load("phase13_awg2_diagnosis_remote_restart", REMOTE)
    observation = good_observation(module)
    observation["restart_count_current"] = module.EXPECTED_RESTART_COUNT + 1

    result = module.evaluate_awg2_observation(observation)

    assert result["awg2_equal"] is False
    assert result["awg2_equal_without_restart_count"] is True
    assert result["restart_count_equal"] is False
    assert result["failed_predicates"] == ["restart_count_equal"]


def test_structural_drift_lists_only_allowlisted_failed_predicates() -> None:
    module = load("phase13_awg2_diagnosis_remote_structural", REMOTE)
    observation = good_observation(module)
    observation["listen_port_equal"] = False
    observation["persistent_peer_count"] = 6

    result = module.evaluate_awg2_observation(observation)

    assert result["awg2_equal_without_restart_count"] is False
    assert result["failed_predicates"] == [
        "listen_port_equal",
        "persistent_peer_count_equal",
    ]
    assert set(result).isdisjoint({"peer_public_keys", "host", "user", "stderr"})


def test_remote_receipt_is_strict_secret_safe_and_read_only() -> None:
    module = load("phase13_awg2_diagnosis_remote_receipt", REMOTE)

    class FakeBackend:
        def collect_awg2_observation(self) -> dict[str, object]:
            return good_observation(module)

        def foreign_equal(self) -> bool:
            return True

    receipt = module.execute_diagnosis(
        {
            "expires_at": future().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_attempts": 1,
            "outcome_id": "spain-awg2-diagnosis-test-001",
            "schema": module.PAYLOAD_SCHEMA,
        },
        FakeBackend(),
    )

    assert receipt["outcome"] == "success"
    assert receipt["awg2_equal"] is True
    assert receipt["foreign_equal"] is True
    assert receipt["mutation_performed"] is False
    assert receipt["raw_output_persisted"] is False
    serialized = canonical(receipt).decode("utf-8")
    for forbidden in ("peer_public_key", "target_host", "target_user", "stderr", "stdout"):
        assert forbidden not in serialized


def test_foreign_observation_failure_preserves_completed_awg2_diagnosis() -> None:
    module = load("phase13_awg2_diagnosis_foreign_unavailable", REMOTE)

    class FakeBackend:
        def collect_awg2_observation(self) -> dict[str, object]:
            return good_observation(module)

        def foreign_equal(self) -> bool:
            raise module.DiagnosisError("foreign", "foreign_observation_failed")

    receipt = module.execute_diagnosis(
        {
            "expires_at": future().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_attempts": 1,
            "outcome_id": "spain-awg2-diagnosis-test-001",
            "schema": module.PAYLOAD_SCHEMA,
        },
        FakeBackend(),
    )

    assert receipt["outcome"] == "success"
    assert receipt["awg2_equal"] is True
    assert receipt["failed_predicates"] == []
    assert receipt["foreign_observed"] is False
    assert receipt["foreign_equal"] is False
    assert receipt["reason"] == "diagnosed_foreign_unavailable"
    local = load("phase13_awg2_diagnosis_foreign_unavailable_parser", LOCAL)
    parsed = local._parse_remote_receipt(
        canonical(receipt), "spain-awg2-diagnosis-test-001"
    )
    assert parsed["awg2_equal"] is True


def test_package_is_deterministic_strict_and_approval_bound(tmp_path: Path) -> None:
    module = load("phase13_awg2_diagnosis_package", LOCAL)
    inputs = package_inputs(module)
    first = module.materialize_diagnostic_package(inputs, tmp_path / "first")
    second = module.materialize_diagnostic_package(inputs, tmp_path / "second")
    first_binding = module.verify_local_diagnostic_package(
        first.package_root, now=datetime.now(timezone.utc)
    )
    second_binding = module.verify_local_diagnostic_package(
        second.package_root, now=datetime.now(timezone.utc)
    )

    assert first_binding.manifest_sha256 == second_binding.manifest_sha256
    assert first_binding.artifact_sha256 == second_binding.artifact_sha256
    assert first_binding.safety == module.SAFETY
    phrase = module.exact_approval_phrase(first_binding)
    assert "ONE_SSH_READ_ONLY" in phrase
    assert "NO_AWG_MUTATION" in phrase
    assert first_binding.manifest_sha256 in phrase

    remote = first.package_root / "remote.py"
    remote.write_bytes(remote.read_bytes() + b"x")
    with pytest.raises(module.DiagnosticError, match="checksum"):
        module.verify_local_diagnostic_package(
            first.package_root, now=datetime.now(timezone.utc)
        )


def test_runner_claims_before_exactly_one_fixed_spain_ssh(tmp_path: Path) -> None:
    module = load("phase13_awg2_diagnosis_runner", LOCAL)
    inputs = replace(
        package_inputs(module),
        runner_bytes=LOCAL.read_bytes(),
        remote_bytes=REMOTE.read_bytes(),
        foundation_bytes=FOUNDATION.read_bytes(),
    )
    package = module.materialize_diagnostic_package(inputs, tmp_path / "packages")
    binding = module.verify_local_diagnostic_package(
        package.package_root, now=datetime.now(timezone.utc)
    )
    private_root = tmp_path / "private"
    calls: list[tuple[str, tuple[str, ...], bytes]] = []

    def fake_process(executable, arguments, input_bytes, **kwargs):
        claim = private_root / "outcomes/spain-awg2-diagnosis-test-001.claim.json"
        assert claim.is_file()
        calls.append((executable, tuple(arguments), input_bytes))
        result = module.safe_success_receipt(binding.outcome_id)
        return canonical(result)

    result = module.run_diagnostic_gate(
        package.package_root,
        module.exact_approval_phrase(binding),
        process_runner=fake_process,
        binding_loader=lambda: module.FixedSpainBinding(
            target_host="fixed-host",
            target_user="fixed-user",
            key_path=tmp_path / "id",
            known_hosts_path=tmp_path / "known_hosts",
        ),
        private_root=private_root,
        now=datetime.now(timezone.utc),
    )

    assert result.status == "success"
    assert result.ssh_process_count == 1
    assert len(calls) == 1
    assert "BatchMode=yes" in calls[0][1]
    assert "StrictHostKeyChecking=yes" in calls[0][1]


@pytest.mark.parametrize(
    ("reason", "exit_code", "expected"),
    [
        ("success", 0, "not_applicable"),
        ("timeout", -1, "timeout"),
        ("output_oversized", -1, "output_oversized"),
        ("process_failure", -1, "local_process_failure"),
        ("process_failure", 255, "ssh_client_failure"),
        ("process_failure", 127, "remote_command_unavailable"),
        ("process_failure", 42, "remote_exit_unclassified"),
        ("process_failure", 0, "transport_internal_failure"),
    ],
)
def test_diagnostic_transport_mapping_preserves_allowlisted_subreason(
    reason: str, exit_code: int, expected: str
) -> None:
    module = load(
        f"phase13_awg2_diagnosis_transport_mapping_{reason}_{exit_code}", LOCAL
    )

    assert module._classify_transport_subreason(reason, exit_code) == expected


def test_diagnostic_process_boundary_classifies_ssh_exit_without_raw_stderr() -> None:
    module = load("phase13_awg2_diagnosis_process_boundary", LOCAL)

    with pytest.raises(module.DiagnosticTransportError) as caught:
        module._run_diagnostic_process(
            sys.executable,
            (
                "-c",
                "import sys;sys.stdin.buffer.read();"
                "sys.stderr.write('raw-sensitive-detail');sys.exit(255)",
            ),
            b"bounded-input",
            timeout_seconds=5.0,
            maximum_input_bytes=1024,
            maximum_output_bytes=1024,
        )

    assert caught.value.subreason == "ssh_client_failure"
    assert "raw-sensitive-detail" not in str(caught.value)


def test_runner_writes_strict_sanitized_transport_failure_v2(tmp_path: Path) -> None:
    module = load("phase13_awg2_diagnosis_transport_receipt", LOCAL)
    inputs = replace(
        package_inputs(module),
        runner_bytes=LOCAL.read_bytes(),
        remote_bytes=REMOTE.read_bytes(),
        foundation_bytes=FOUNDATION.read_bytes(),
    )
    package = module.materialize_diagnostic_package(inputs, tmp_path / "packages")
    binding = module.verify_local_diagnostic_package(
        package.package_root, now=datetime.now(timezone.utc)
    )
    private_root = tmp_path / "private"

    def fail_process(*args, **kwargs):
        raise module.DiagnosticTransportError("ssh_client_failure")

    with pytest.raises(module.DiagnosticError, match="diagnosis failed"):
        module.run_diagnostic_gate(
            package.package_root,
            module.exact_approval_phrase(binding),
            process_runner=fail_process,
            binding_loader=lambda: module.FixedSpainBinding(
                target_host="fixed-host",
                target_user="fixed-user",
                key_path=tmp_path / "id",
                known_hosts_path=tmp_path / "known_hosts",
            ),
            private_root=private_root,
            now=datetime.now(timezone.utc),
        )

    failure = json.loads(
        (
            private_root
            / "receipts/spain-awg2-diagnosis-test-001.failure.json"
        ).read_text(encoding="utf-8")
    )
    assert failure == {
        "outcome": "failure",
        "outcome_id": "spain-awg2-diagnosis-test-001",
        "raw_output_persisted": False,
        "reason": "transport_or_remote_failure",
        "schema": "amn2.phase13.spain-awg2-predicate-diagnosis-local-failure.v2",
        "ssh_process_count": 1,
        "transport_subreason": "ssh_client_failure",
    }
    serialized = canonical(failure).decode("utf-8")
    for forbidden in (
        "raw-sensitive-detail",
        "stderr",
        "stdout",
        "target_host",
        "target_user",
        "key_path",
        "fingerprint",
        "system_error",
    ):
        assert forbidden not in serialized


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("awg2_equal", "true"),
        ("reason", "raw remote detail"),
        ("stage", "unexpected-stage"),
    ],
)
def test_runner_rejects_type_confused_or_unallowlisted_remote_receipt(
    field: str, unsafe_value: object
) -> None:
    module = load(f"phase13_awg2_diagnosis_strict_{field}", LOCAL)
    receipt = module.safe_success_receipt("spain-awg2-diagnosis-test-001")
    receipt[field] = unsafe_value
    with pytest.raises(module.DiagnosticError, match="remote receipt invalid"):
        module._parse_remote_receipt(
            canonical(receipt), "spain-awg2-diagnosis-test-001"
        )
