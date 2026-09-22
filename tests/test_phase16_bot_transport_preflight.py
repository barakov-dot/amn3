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
SCRIPT = ROOT / "scripts/phase16_bot_transport_preflight_gate.py"


class TransportPreflightTests(unittest.TestCase):
    def load_gate(self):
        self.assertTrue(SCRIPT.is_file(), "zero-input preflight gate is not implemented")
        spec = importlib.util.spec_from_file_location("phase16_transport_preflight", SCRIPT)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        return gate

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def binding(self):
        return type("Binding", (), {
            "role": "spain",
            "target_host": "example.invalid",
            "target_user": "tester",
            "key_path": Path("key"),
            "known_hosts_path": Path("known_hosts"),
        })()

    def test_remote_command_is_exact_zero_input_probe(self):
        gate = self.load_gate()
        command = gate.remote_command()
        argv = shlex.split(command)
        self.assertEqual(argv[:5], ["/usr/bin/python3", "-I", "-S", "-B", "-c"])
        self.assertEqual(argv[-1], gate.APPROVAL)
        argv[0] = sys.executable
        result = subprocess.run(argv, input=b"PRIVATE_INPUT_MUST_BE_IGNORED",
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), gate.pass_receipt())
        self.assertEqual(result.stderr, b"")

    def test_receipt_schema_is_closed(self):
        gate = self.load_gate()
        receipt = gate.pass_receipt()
        self.assertEqual(gate.validate_receipt(receipt, 0), receipt)
        for key, value in (("extra", "x"), ("status", "UNKNOWN"),
                           ("approval", "old")):
            changed = dict(receipt)
            changed[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(
                    gate.Stop, "^receipt_binding$"):
                gate.validate_receipt(changed, 0)

    def test_old_marker_stops_before_claim_binding_or_transport(self):
        gate = self.load_gate()
        calls = []
        with self.assertRaisesRegex(gate.Stop, "^approval_binding$"):
            gate.execute_once(
                self.root / "attempt",
                approval="PHASE16_ACTUAL_INTEGRATION_READBACK_20260922_004",
                approved_gate_sha="0" * 64,
                manifest={},
                loader=lambda role: calls.append("loader"),
                transport=lambda *args, **kwargs: calls.append("transport"),
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.root / "attempt").exists())

    def test_execute_uses_one_transport_with_empty_stdin(self):
        gate = self.load_gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []

        def transport(args, **kwargs):
            calls.append((args, kwargs))
            kwargs["diagnostics"].update({
                "schema": "phase16.bot-transport.v1",
                "returncode": 0,
                "failure_stage": None,
                "stdin_bytes_requested": 0,
                "stdin_bytes_accepted": 0,
                "stdin_complete": True,
                "output_complete": True,
                "stdout": {"bytes_observed": 1, "bytes_retained": 1,
                           "prefix_sha256": hashlib.sha256(b"x").hexdigest()},
                "stderr": {"bytes_observed": 0, "bytes_retained": 0,
                           "prefix_sha256": hashlib.sha256(b"").hexdigest()},
                "pipe_failures": [],
                "stderr_classification": "EMPTY",
            })
            return 0, json.dumps(gate.pass_receipt()).encode()

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt",
                approval=gate.APPROVAL,
                approved_gate_sha=gate.gate_sha(ROOT),
                manifest=manifest,
                loader=lambda role: self.binding(),
                transport=transport,
            )

        self.assertEqual(result["status"], "SSH_ZERO_INPUT_PREFLIGHT_PASS")
        self.assertEqual(result["ssh_attempts"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]["input_bytes"], b"")
        self.assertEqual(calls[0][1]["timeout"], 20)
        self.assertEqual(json.loads((self.root / "attempt" / "result.json").read_text()),
                         result)

    def test_empty_output_is_unknown_without_retry(self):
        gate = self.load_gate()
        manifest = gate.gate_manifest(ROOT)
        calls = []

        def transport(*args, **kwargs):
            calls.append(1)
            kwargs["diagnostics"].update({"returncode": 255,
                                           "failure_stage": "stdin_write"})
            return 255, b""

        with patch.object(gate, "ssh_environment", return_value={"PROGRAMDATA": "x"}), \
             patch.object(gate, "binding_digest",
                          return_value=manifest["target_binding_sha256"]):
            result = gate.execute_once(
                self.root / "attempt",
                approval=gate.APPROVAL,
                approved_gate_sha=gate.gate_sha(ROOT),
                manifest=manifest,
                loader=lambda role: self.binding(),
                transport=transport,
            )

        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "UNKNOWN_NO_RETRY")
        self.assertEqual(result["reason"], "transport_no_remote_receipt")
        self.assertNotIn("raw", json.dumps(result).lower())


if __name__ == "__main__":
    unittest.main()
