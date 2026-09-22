"""Gate-008 records only a closed diagnostic boundary for rejected receipts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase16_bot_integration_readback_gate_008.py"
SECRET = "PRIVATE_MARKER_DO_NOT_PERSIST"


def load_gate():
    assert SCRIPT.is_file(), "diagnostic gate-008 is not implemented"
    spec = importlib.util.spec_from_file_location("phase16_readback_gate008", SCRIPT)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


class ActualReadbackGate008Tests(unittest.TestCase):
    def test_rejected_source_receipt_names_stage_without_copying_value(self):
        gate = load_gate()
        receipt = gate.base.remote.stop_receipt("remote_gate", {
            "source": {"unexpected": SECRET}
        })
        diagnostic = gate.diagnose_rejection(receipt, 3)
        self.assertEqual(diagnostic, "source")
        self.assertNotIn(SECRET, json.dumps(diagnostic))

    def test_unexpected_envelope_stays_generic(self):
        gate = load_gate()
        receipt = {"status": SECRET, "partial": {"source": {"unexpected": SECRET}}}
        self.assertEqual(gate.diagnose_rejection(receipt, 3), "envelope")

    def test_one_transport_rejects_receipt_and_persists_only_boundary(self):
        gate = load_gate()
        manifest = gate.validate_gate_manifest(gate.gate_manifest(ROOT), ROOT)
        receipt = gate.base.remote.stop_receipt("remote_gate", {
            "source": {"unexpected": SECRET}
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
            evidence = Path(scratch) / "execution-008"
            result = gate.execute_once(
                evidence, approval=gate.APPROVAL,
                approved_remote_sha=gate.sha(gate.remote_script(ROOT)),
                approved_manifest_sha=gate.base.remote.MANIFEST_SHA256,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda _role: binding, transport=transport,
            )
            persisted = (evidence / "result.json").read_text(encoding="utf-8")
        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "UNKNOWN_NO_RETRY")
        self.assertEqual(result["reason"], "receipt_binding")
        self.assertEqual(result["validation_failure"], "source")
        self.assertNotIn("remote", result)
        self.assertNotIn(SECRET, persisted)


if __name__ == "__main__":
    unittest.main()
