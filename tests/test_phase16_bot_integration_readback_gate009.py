"""Gate-009 accepts only bounded numeric systemd signals from the collector."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase16_bot_integration_readback_gate_009.py"


def load_gate():
    assert SCRIPT.is_file(), "numeric-signal gate-009 is not implemented"
    spec = importlib.util.spec_from_file_location("phase16_readback_gate009", SCRIPT)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def numeric_units(gate):
    units = gate.base.pass_receipt_for_tests()["units_before"]
    for role in ("bot", "web"):
        units[role]["KillSignal"] = "15"
        units[role]["FinalKillSignal"] = "9"
    return units


class ActualReadbackGate009Tests(unittest.TestCase):
    def test_stop_receipt_with_bounded_numeric_signals_is_validated(self):
        gate = load_gate()
        receipt = gate.base.remote.stop_receipt("database_child", {
            "units_before": numeric_units(gate)
        })
        self.assertEqual(gate.validate_receipt_numeric(receipt, 3), receipt)
        self.assertEqual(receipt["partial"]["units_before"]["bot"]["KillSignal"], "15")

    def test_pass_receipt_with_bounded_numeric_signals_is_validated(self):
        gate = load_gate()
        receipt = gate.base.pass_receipt_for_tests()
        receipt["units_before"] = numeric_units(gate)
        receipt["units_after"] = numeric_units(gate)
        self.assertEqual(gate.validate_receipt_numeric(receipt, 0), receipt)

    def test_numeric_signal_outside_range_or_extra_unit_field_still_rejected(self):
        gate = load_gate()
        for invalid in ("0", "65", "015", "PRIVATE_MARKER"):
            receipt = gate.base.remote.stop_receipt("remote_gate", {
                "units_before": numeric_units(gate)
            })
            receipt["partial"]["units_before"]["bot"]["KillSignal"] = invalid
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    gate.Stop, "^receipt_binding$"):
                gate.validate_receipt_numeric(receipt, 3)
        receipt = gate.base.remote.stop_receipt("remote_gate", {
            "units_before": numeric_units(gate)
        })
        receipt["partial"]["units_before"]["bot"]["Environment"] = "PRIVATE_MARKER"
        with self.assertRaisesRegex(gate.Stop, "^receipt_binding$"):
            gate.validate_receipt_numeric(receipt, 3)

    def test_one_transport_persists_validated_stop_without_retry(self):
        gate = load_gate()
        manifest = gate.validate_gate_manifest(gate.gate_manifest(ROOT), ROOT)
        receipt = gate.base.remote.stop_receipt("database_child", {
            "units_before": numeric_units(gate)
        })
        calls = []

        def transport(_args, **kwargs):
            calls.append(1)
            kwargs["diagnostics"].update(returncode=3, stdin_complete=True)
            return 3, json.dumps(receipt).encode()

        binding = type("Binding", (), {
            "role": "spain", "target_host": "example.invalid", "target_user": "tester",
            "key_path": Path("key"), "known_hosts_path": Path("known_hosts"),
        })()
        with tempfile.TemporaryDirectory() as scratch, \
             patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            evidence = Path(scratch) / "execution-009"
            result = gate.execute_once(
                evidence, approval=gate.APPROVAL,
                approved_remote_sha=gate.sha(gate.remote_script(ROOT)),
                approved_manifest_sha=gate.base.remote.MANIFEST_SHA256,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda _role: binding, transport=transport,
            )
            persisted = json.loads((evidence / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "STOP_NO_RETRY")
        self.assertEqual(result["ssh_attempts"], 1)
        self.assertEqual(persisted["remote"]["reason"], "database_child")


if __name__ == "__main__":
    unittest.main()
