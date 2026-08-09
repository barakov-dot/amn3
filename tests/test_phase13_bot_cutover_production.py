from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts/phase13_bot_cutover.py"
REMOTE = ROOT / "scripts/vps/phase13_bot_cutover_remote.py"


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


def package_inputs(module):
    return module.CutoverPackageInputs(
        outcome_id="bot-cutover-test-001",
        expires_at=future(),
        tooling_head="a" * 40,
        runner_bytes=b"runner",
        remote_bytes=b"remote",
        foundation_bytes=b"foundation",
        bot_unit_bytes=(
            b"[Unit]\nConditionPathExists=/etc/amn2-spain/bot-enabled\n"
            b"[Install]\nWantedBy=multi-user.target\n"
        ),
        runtime_stage_receipt=canonical(
            {
                "awg2_equal": True,
                "bot_disabled": True,
                "database_equal": True,
                "foreign_equal": True,
                "marker_absent": True,
                "outcome": "success",
                "outcome_id": "spain-bot-runtime-stage-20260809-113453",
                "raw_output_persisted": False,
                "reason": "completed",
                "rolled_back": False,
                "runtime_delta_equal": True,
                "schema": "amn2.phase13.spain-bot-runtime-stage-receipt.v1",
                "service_action_performed": False,
                "source_equal": True,
                "stage": "post_verify",
                "web_loopback_healthy": True,
            }
        ),
    )


def test_red_production_modules_exist() -> None:
    assert LOCAL.is_file()
    assert REMOTE.is_file()


def test_package_is_checksum_bound_deterministic_and_exact_approval(tmp_path: Path) -> None:
    module = load("phase13_cutover_package", LOCAL)
    inputs = package_inputs(module)
    first = module.materialize_cutover_package(inputs, tmp_path / "first")
    second = module.materialize_cutover_package(inputs, tmp_path / "second")
    first_binding = module.verify_local_cutover_package(first.package_root, now=datetime.now(timezone.utc))
    second_binding = module.verify_local_cutover_package(second.package_root, now=datetime.now(timezone.utc))
    assert first_binding.manifest_sha256 == second_binding.manifest_sha256
    assert first_binding.artifact_sha256 == second_binding.artifact_sha256
    phrase = module.exact_approval_phrase(first_binding)
    assert "TWO-HOST SINGLE-INSTANCE BOT CUTOVER" in phrase
    assert "MAX_SSH_PROCESSES_10" in phrase
    assert "USA_ALREADY_ZERO_ALLOWED" in phrase
    assert "SPAIN_BOT_UNIT_ATOMIC_UPDATE" in phrase
    assert first_binding.bot_unit_sha256 in phrase
    assert "NO_USA_SERVER_SHUTDOWN" in phrase
    assert "NO_AWG_MUTATION" in phrase
    assert first_binding.manifest_sha256 in phrase
    diagnosis_phrase = module.exact_dual_diagnosis_approval_phrase(first_binding)
    assert "TWO-HOST BOT ROLLBACK READ-ONLY DIAGNOSIS" in diagnosis_phrase
    assert "TWO_SSH_READ_ONLY" in diagnosis_phrase
    assert "NO_SERVICE_ACTION" in diagnosis_phrase
    assert first_binding.manifest_sha256 in diagnosis_phrase


def test_cutover_transport_bounds_do_not_exceed_shared_foundation() -> None:
    module = load("phase13_cutover_transport_bounds", LOCAL)
    assert module.MAX_INPUT_BYTES == module.FOUNDATION_MAX_TRANSPORT_INPUT_BYTES
    assert module.MAX_INPUT_BYTES == 1024 * 1024
    assert module.MAX_OUTPUT_BYTES <= module.FOUNDATION_MAX_TRANSPORT_OUTPUT_BYTES


def test_package_rejects_tamper_and_unknown_artifact(tmp_path: Path) -> None:
    module = load("phase13_cutover_tamper", LOCAL)
    receipt = module.materialize_cutover_package(package_inputs(module), tmp_path)
    path = receipt.package_root / "remote.py"
    path.write_bytes(path.read_bytes() + b"x")
    with pytest.raises(module.CutoverError, match="checksum"):
        module.verify_local_cutover_package(receipt.package_root, now=datetime.now(timezone.utc))
    path.write_bytes(b"remote")
    (receipt.package_root / "unknown").write_bytes(b"x")
    with pytest.raises(module.CutoverError, match="artifact set"):
        module.verify_local_cutover_package(receipt.package_root, now=datetime.now(timezone.utc))


class FakeTransport:
    def __init__(
        self, module, *, fail_spain_start: bool = False,
        start_failure_reason: str = "spain_bot_admission_failed",
        usa_initial: int = 1,
    ) -> None:
        self.module = module
        self.fail_spain_start = fail_spain_start
        self.start_failure_reason = start_failure_reason
        self.calls: list[tuple[str, str]] = []
        self.usa = usa_initial
        self.spain = 0
        self.marker = False

    def __call__(self, role: str, mode: str, continuation: dict[str, str] | None = None):
        self.calls.append((role, mode))
        if role == "usa" and mode == "preflight":
            return {"outcome": "success", "reason": "completed", "bot_active": self.usa == 1, "bot_enabled": self.usa == 1, "bot_process_count": self.usa, "continuation": {}}
        if role == "spain" and mode == "preflight":
            return {"outcome": "success", "reason": "completed", "bot_active": False, "bot_enabled": False, "bot_process_count": self.spain, "marker_present": self.marker, "continuation": {"state": "a" * 64}}
        if role == "usa" and mode == "stop":
            self.usa = 0
            return {"outcome": "success", "reason": "completed", "bot_active": False, "bot_enabled": False, "bot_process_count": 0, "continuation": {}}
        if role == "spain" and mode == "start":
            if self.fail_spain_start:
                return {"outcome": "failure", "reason": self.start_failure_reason, "bot_active": False, "bot_enabled": False, "bot_process_count": 0, "continuation": {}}
            self.spain = 1
            self.marker = True
            return {"outcome": "success", "reason": "completed", "bot_active": True, "bot_enabled": True, "bot_process_count": 1, "marker_present": True, "continuation": {}}
        if role == "usa" and mode == "postflight":
            return {"outcome": "success", "reason": "completed", "bot_active": self.usa == 1, "bot_enabled": self.usa == 1, "bot_process_count": self.usa, "continuation": {}}
        if role == "spain" and mode == "postflight":
            return {"outcome": "success", "reason": "completed", "bot_active": self.spain == 1, "bot_enabled": self.spain == 1, "bot_process_count": self.spain, "marker_present": self.marker, "continuation": {}}
        if role == "spain" and mode == "rollback_stop":
            self.spain = 0
            self.marker = False
            return {"outcome": "success", "reason": "completed", "bot_active": False, "bot_enabled": False, "bot_process_count": 0, "marker_present": False, "continuation": {}}
        if role == "usa" and mode == "rollback_start":
            self.usa = 1
            return {"outcome": "success", "reason": "completed", "bot_active": True, "bot_enabled": True, "bot_process_count": 1, "continuation": {}}
        raise AssertionError((role, mode))


def test_success_sequence_never_starts_spain_before_usa_zero() -> None:
    module = load("phase13_cutover_sequence", LOCAL)
    transport = FakeTransport(module)
    result = module.execute_cutover_state_machine(transport)
    assert result["outcome"] == "success"
    assert result["single_owner"] is True
    assert result["usa_active"] is False
    assert result["spain_active"] is True
    assert result["rolled_back"] is False
    assert transport.calls == [
        ("usa", "preflight"),
        ("spain", "preflight"),
        ("usa", "stop"),
        ("spain", "start"),
        ("usa", "postflight"),
        ("spain", "postflight"),
    ]


def test_already_zero_usa_is_safe_and_skips_redundant_stop() -> None:
    module = load("phase13_cutover_already_zero", LOCAL)
    transport = FakeTransport(module, usa_initial=0)
    result = module.execute_cutover_state_machine(transport)
    assert result["outcome"] == "success"
    assert result["single_owner"] is True
    assert result["usa_active"] is False
    assert result["spain_active"] is True
    assert ("usa", "stop") not in transport.calls
    assert transport.calls[:3] == [
        ("usa", "preflight"),
        ("spain", "preflight"),
        ("spain", "start"),
    ]


def test_spain_admission_failure_restores_exact_single_usa_owner() -> None:
    module = load("phase13_cutover_rollback", LOCAL)
    transport = FakeTransport(module, fail_spain_start=True)
    result = module.execute_cutover_state_machine(transport)
    assert result["outcome"] == "failure"
    assert result["reason"] == "SPAIN_BOT_ADMISSION_FAILED"
    assert result["rolled_back"] is True
    assert result["single_owner"] is True
    assert result["usa_active"] is True
    assert result["spain_active"] is False
    assert transport.calls[-4:] == [
        ("spain", "rollback_stop"),
        ("usa", "rollback_start"),
        ("usa", "postflight"),
        ("spain", "postflight"),
    ]


def test_spain_start_failure_preserves_only_allowlisted_terminal_reason() -> None:
    module = load("phase13_cutover_start_reason", LOCAL)
    known = module.execute_cutover_state_machine(
        FakeTransport(
            module,
            fail_spain_start=True,
            start_failure_reason="service_action_failed",
        )
    )
    assert known["reason"] == "SPAIN_SERVICE_ACTION_FAILED"
    unknown = module.execute_cutover_state_machine(
        FakeTransport(
            module,
            fail_spain_start=True,
            start_failure_reason="raw untrusted detail",
        )
    )
    assert unknown["reason"] == "SPAIN_BOT_ADMISSION_FAILED"


def test_remote_pure_state_machine_is_role_and_mode_closed() -> None:
    module = load("phase13_cutover_remote_contract", REMOTE)

    class Backend:
        def observe(self, role: str, continuation=None):
            return {"bot_active": role == "usa", "bot_process_count": 1 if role == "usa" else 0, "marker_present": False, "continuation": {"state": "b" * 64} if role == "spain" else {}}

        def mutate(self, role: str, mode: str, continuation=None):
            return {"bot_active": role == "spain", "bot_process_count": 1 if role == "spain" else 0, "marker_present": role == "spain", "continuation": {}}

    ok = module.execute({"role": "usa", "mode": "preflight", "continuation": {}}, Backend())
    assert ok["outcome"] == "success"
    assert ok["service_action_performed"] is False
    rejected = module.execute({"role": "usa", "mode": "start", "continuation": {}}, Backend())
    assert rejected["outcome"] == "failure"
    assert rejected["reason"] == "unsupported_transition"
    assert set(rejected) == module.RECEIPT_KEYS


def test_readonly_diagnosis_preserves_only_allowlisted_subreason() -> None:
    module = load("phase13_cutover_diagnosis", LOCAL)
    receipt = module.preflight_diagnosis_receipt(
        {
            "bot_active": False,
            "bot_process_count": 0,
            "outcome": "failure",
            "reason": "service_action_failed",
        },
        "bot-cutover-diagnosis-test-001",
    )
    assert receipt == {
        "awg2_equal": False,
        "bot_active": False,
        "bot_process_count": 0,
        "database_equal": False,
        "foreign_equal": False,
        "marker_present": False,
        "outcome": "failure",
        "outcome_id": "bot-cutover-diagnosis-test-001",
        "raw_output_persisted": False,
        "reason": "service_action_failed",
        "role": "usa",
        "runtime_equal": False,
        "schema": "amn2.phase13.bot-cutover-preflight-diagnosis.v2",
        "service_action_performed": False,
        "source_equal": False,
        "ssh_process_count": 1,
        "web_loopback_healthy": False,
    }
    unknown = module.preflight_diagnosis_receipt(
        {"outcome": "failure", "reason": "raw secret-like detail"},
        "bot-cutover-diagnosis-test-002",
    )
    assert unknown["reason"] == "unclassified_failure"


def test_spain_diagnosis_preserves_safe_predicate_booleans() -> None:
    module = load("phase13_cutover_spain_diagnosis", LOCAL)
    receipt = module.preflight_diagnosis_receipt(
        {
            "awg2_equal": True,
            "bot_active": False,
            "bot_process_count": 0,
            "database_equal": True,
            "foreign_equal": False,
            "marker_present": False,
            "outcome": "failure",
            "reason": "spain_preflight_failed",
            "role": "spain",
            "runtime_equal": True,
            "source_equal": True,
            "web_loopback_healthy": True,
        },
        "bot-cutover-diagnosis-test-003",
    )
    assert receipt["role"] == "spain"
    assert receipt["foreign_equal"] is False
    assert receipt["awg2_equal"] is True
    assert receipt["database_equal"] is True
    assert receipt["service_action_performed"] is False


def test_foreign_snapshot_uses_verified_stable_row_digest_not_tuple_key_json() -> None:
    module = load("phase13_cutover_foreign_digest", REMOTE)

    class FoundationBackend:
        calls = 0

        def _collect_foreign_rows(self):
            self.calls += 1
            return {
                ("unit", "example.service"): {
                    "kind": "unit",
                    "name": "example.service",
                    "state": "active",
                }
            }

        def _phase12_stable_digest(self, rows):
            assert rows == [
                {
                    "kind": "unit",
                    "name": "example.service",
                    "state": "active",
                }
            ]
            return "c" * 64

    backend = module.LiveBackend.__new__(module.LiveBackend)
    backend.spain = FoundationBackend()
    assert backend._foreign_sha() == "c" * 64
    assert backend.spain.calls == 2


def test_hardened_spain_bot_unit_contract_is_exact_and_persistent() -> None:
    module = load("phase13_cutover_bot_unit", REMOTE)
    value = (
        b"[Unit]\nConditionPathExists=/etc/amn2-spain/bot-enabled\n"
        b"[Service]\nEnvironment=TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot "
        b"TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30 "
        b"TELEGRAM_POLLING_TIMEOUT_SECONDS=20\n"
        b"TimeoutStartSec=40s\nExecStart=/usr/bin/python3 -B -m app.main\n"
        b"[Install]\nWantedBy=multi-user.target\n"
    )
    assert module.validate_bot_unit(value) == value
    with pytest.raises(module.RemoteCutoverError, match="bot_unit_invalid"):
        module.validate_bot_unit(value.replace(b"WantedBy=multi-user.target\n", b""))
    with pytest.raises(module.RemoteCutoverError, match="bot_unit_invalid"):
        module.validate_bot_unit(
            value.replace(
                b"Environment=TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot ",
                b"",
            )
        )


def test_packaged_spain_bot_unit_binds_required_admission_identity() -> None:
    value = (ROOT / "packaging/phase12-spain/units/amn2-spain-bot.service").read_text(
        encoding="utf-8"
    )
    assert (
        "Environment=TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot "
        "TELEGRAM_ADMISSION_TIMEOUT_SECONDS=30 "
        "TELEGRAM_POLLING_TIMEOUT_SECONDS=20\n"
    ) in value
    assert "TimeoutStartSec=40s\n" in value


def test_dual_recovery_diagnosis_reports_both_roles_without_mutation() -> None:
    module = load("phase13_cutover_dual_diagnosis", LOCAL)
    usa = module.preflight_diagnosis_receipt(
        {"role": "usa", "outcome": "success", "reason": "completed", "bot_active": True, "bot_process_count": 1},
        "dual-test-001",
    )
    spain = module.preflight_diagnosis_receipt(
        {"role": "spain", "outcome": "failure", "reason": "spain_preflight_failed", "bot_active": False, "bot_process_count": 0, "marker_present": False},
        "dual-test-001",
    )
    receipt = module.dual_diagnosis_receipt(usa, spain, "dual-test-001")
    assert receipt["outcome"] == "failure"
    assert receipt["reason"] == "role_observation_failed"
    assert receipt["usa_active"] is True
    assert receipt["spain_active"] is False
    assert receipt["single_owner"] is True
    assert receipt["service_action_performed"] is False
    assert receipt["ssh_process_count"] == 2

    completed = module.dual_diagnosis_receipt(
        usa,
        module.preflight_diagnosis_receipt(
            {"role": "spain", "outcome": "success", "reason": "completed", "bot_active": False, "bot_process_count": 0, "marker_present": False},
            "dual-test-001",
        ),
        "dual-test-001",
    )
    assert completed["outcome"] == "success"
    assert completed["reason"] == "completed"


def test_spain_start_timeout_exceeds_bot_admission_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load("phase13_cutover_spain_start_timeout", REMOTE)
    marker = tmp_path / "bot-enabled"
    monkeypatch.setattr(module, "SPAIN_MARKER", marker)
    backend = module.LiveBackend.__new__(module.LiveBackend)
    backend._stage_bot_unit = lambda: None
    calls: list[tuple[tuple[str, ...], int]] = []

    def run(arguments: tuple[str, ...], *, require_success: bool = True, timeout_seconds: int = 20) -> bytes:
        calls.append((arguments, timeout_seconds))
        return b""

    backend._run = run
    backend.observe = lambda role, continuation=None: {
        "bot_active": True,
        "bot_enabled": True,
        "bot_process_count": 1,
        "continuation": {},
        "marker_present": True,
    }
    state = backend.mutate("spain", "start", {})
    assert state["bot_active"] is True
    assert calls == [
        (("/usr/bin/systemctl", "enable", "--now", module.SPAIN_UNIT), 45)
    ]
    assert 45 > 30
