import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase16_bot_frame_preflight_gate.py"


class FramePreflightTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def gate(self):
        self.assertTrue(SCRIPT.is_file(), "bound frame preflight gate is not implemented")
        spec = importlib.util.spec_from_file_location("phase16_frame_preflight", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def binding(self):
        return type("Binding", (), {
            "role": "spain", "target_host": "example.invalid", "target_user": "tester",
            "key_path": Path("key"), "known_hosts_path": Path("known_hosts"),
        })()

    def test_exact_synthetic_frame_roundtrip_and_tamper_stop(self):
        gate = self.gate()
        frame = gate.frame_bytes()
        self.assertEqual(len(frame), 68077)
        argv = shlex.split(gate.remote_command())
        self.assertEqual(argv[:5], ["/usr/bin/python3", "-I", "-S", "-B", "-c"])
        self.assertEqual(argv[-1], gate.APPROVAL)
        argv[0] = sys.executable
        passed = subprocess.run(argv, input=frame, capture_output=True, timeout=5)
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(json.loads(passed.stdout), gate.pass_receipt())
        self.assertEqual(passed.stderr, b"")
        changed = frame[:-1] + bytes([frame[-1] ^ 1])
        stopped = subprocess.run(argv, input=changed, capture_output=True, timeout=5)
        self.assertEqual(stopped.returncode, 3)
        self.assertEqual(json.loads(stopped.stdout), gate.stop_receipt())
        self.assertEqual(stopped.stderr, b"")

    def test_manifest_binds_frame_runner_helper_and_one_attempt_limits(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        self.assertEqual(gate.validate_gate_manifest(manifest, ROOT), manifest)
        changed = json.loads(json.dumps(manifest))
        changed["sha256_lf"]["frame"] = "0" * 64
        with self.assertRaisesRegex(gate.Stop, "^manifest_binding$"):
            gate.validate_gate_manifest(changed, ROOT)
        self.assertEqual(manifest["limits"]["ssh_attempts"], 1)
        self.assertFalse(manifest["limits"]["retry"])

    def test_old_marker_rejected_before_claim_or_transport(self):
        gate = self.gate()
        calls = []
        with self.assertRaisesRegex(gate.Stop, "^approval_binding$"):
            gate.execute_once(
                self.root / "attempt", approval="PHASE16_SSH_ZERO_INPUT_PREFLIGHT_20260922_005",
                approved_gate_sha="0" * 64, manifest={},
                loader=lambda role: calls.append("loader"),
                transport=lambda *args, **kwargs: calls.append("transport"),
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.root / "attempt").exists())

    def test_one_transport_receives_exact_frame_and_accepts_only_closed_receipt(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []

        def transport(args, **kwargs):
            calls.append(kwargs)
            kwargs["diagnostics"].update({"returncode": 0, "stdin_complete": True})
            return 0, json.dumps(gate.pass_receipt()).encode()

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt", approval=gate.APPROVAL,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda role: self.binding(), transport=transport,
            )
        self.assertEqual(result["status"], "SSH_BOUND_FRAME_PREFLIGHT_PASS")
        self.assertEqual(result["ssh_attempts"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["input_bytes"], gate.frame_bytes())
        self.assertEqual(calls[0]["timeout"], 25)
        self.assertEqual(json.loads((self.root / "attempt" / "result.json").read_text()), result)

    def test_empty_output_stops_without_retry(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []

        def transport(*args, **kwargs):
            calls.append(1)
            kwargs["diagnostics"].update({"returncode": 255})
            return 255, b""

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt", approval=gate.APPROVAL,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda role: self.binding(), transport=transport,
            )
        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "UNKNOWN_NO_RETRY")
        self.assertEqual(result["reason"], "transport_no_remote_receipt")

    def test_remote_frame_mismatch_is_exact_stop_not_pass(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)

        def transport(*args, **kwargs):
            kwargs["diagnostics"].update({"returncode": 3, "stdin_complete": True})
            return 3, json.dumps(gate.stop_receipt()).encode()

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt", approval=gate.APPROVAL,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda role: self.binding(), transport=transport,
            )
        self.assertEqual(result["status"], "STOP_NO_RETRY")
        self.assertEqual(result["remote"], gate.stop_receipt())


if __name__ == "__main__":
    unittest.main()
