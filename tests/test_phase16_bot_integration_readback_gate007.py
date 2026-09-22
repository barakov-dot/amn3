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
SCRIPT = ROOT / "scripts/phase16_bot_integration_readback_gate_007.py"


class ActualReadbackGate007Tests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def gate(self):
        self.assertTrue(SCRIPT.is_file(), "actual readback gate-007 is not implemented")
        spec = importlib.util.spec_from_file_location("phase16_readback_gate007", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def binding(self):
        return type("Binding", (), {
            "role": "spain", "target_host": "example.invalid", "target_user": "tester",
            "key_path": Path("key"), "known_hosts_path": Path("known_hosts"),
        })()

    def test_remote_script_changes_only_exact_approval_marker(self):
        gate = self.gate()
        original = gate.base.remote_script(ROOT)
        self.assertEqual(original.count(gate.OLD_APPROVAL.encode()), 1)
        expected = original.replace(gate.OLD_APPROVAL.encode(), gate.APPROVAL.encode())
        self.assertEqual(gate.remote_script(ROOT), expected)
        self.assertNotIn(gate.OLD_APPROVAL.encode(), expected)
        compile(expected, "<gate-007-remote>", "exec")

    def test_frame_bootstrap_uses_new_marker_and_exact_payload(self):
        gate = self.gate()
        script = b'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())'
        payload = gate.base.build_payload(ROOT)
        command, frame = gate.frame_request(script, payload)
        argv = shlex.split(command)
        self.assertEqual(argv[-1], gate.APPROVAL)
        argv[0] = sys.executable
        process = subprocess.run(argv, input=frame, capture_output=True, timeout=5)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.strip().decode(), hashlib.sha256(payload).hexdigest())
        self.assertEqual(process.stderr, b"")

    def test_manifest_binds_runner_transformed_remote_payload_and_limits(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        self.assertEqual(gate.validate_gate_manifest(manifest, ROOT), manifest)
        for key in ("local_runner", "remote_supervisor", "transport_helper", "payload"):
            changed = json.loads(json.dumps(manifest))
            changed["sha256_lf"][key] = "0" * 64
            with self.subTest(key=key), self.assertRaisesRegex(gate.Stop, "^manifest_binding$"):
                gate.validate_gate_manifest(changed, ROOT)
        self.assertEqual(manifest["limits"]["ssh_attempts"], 1)
        self.assertFalse(manifest["limits"]["retry"])

    def test_old_marker_rejected_before_claim_binding_or_transport(self):
        gate = self.gate()
        calls = []
        with self.assertRaisesRegex(gate.Stop, "^approval_binding$"):
            gate.execute_once(
                self.root / "attempt", approval=gate.OLD_APPROVAL,
                approved_remote_sha="0" * 64, approved_manifest_sha="0" * 64,
                approved_gate_sha="0" * 64, manifest={},
                loader=lambda role: calls.append("loader"),
                transport=lambda *args, **kwargs: calls.append("transport"),
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.root / "attempt").exists())

    def test_one_transport_accepts_only_validated_remote_receipt(self):
        gate = self.gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []

        def transport(args, **kwargs):
            calls.append(kwargs)
            kwargs["diagnostics"].update({"returncode": 0, "stdin_complete": True})
            return 0, json.dumps(gate.base.pass_receipt_for_tests()).encode()

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt", approval=gate.APPROVAL,
                approved_remote_sha=gate.sha(gate.remote_script(ROOT)),
                approved_manifest_sha=gate.base.remote.MANIFEST_SHA256,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda role: self.binding(), transport=transport,
            )
        self.assertEqual(result["status"], "READBACK_COMPLETE_WITH_LIMITATIONS")
        self.assertEqual(result["ssh_attempts"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["timeout"], 60)
        self.assertGreater(len(calls[0]["input_bytes"]), 68000)

    def test_empty_output_is_unknown_without_retry(self):
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
                approved_remote_sha=gate.sha(gate.remote_script(ROOT)),
                approved_manifest_sha=gate.base.remote.MANIFEST_SHA256,
                approved_gate_sha=gate.gate_sha(ROOT), manifest=manifest,
                loader=lambda role: self.binding(), transport=transport,
            )
        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "UNKNOWN_NO_RETRY")
        self.assertEqual(result["reason"], "transport_no_remote_receipt")


if __name__ == "__main__":
    unittest.main()
