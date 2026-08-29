from __future__ import annotations

import base64
import configparser
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/vps/phase16_awg31_client_recovery.py"
I1 = (
    "<r 2><b 0x8580000100010000000004796162730679616e6465780272750000010001"
    "c00c000100010000026d000457fa27d1>"
)


def key(byte: int) -> str:
    return base64.b64encode(bytes([byte]) * 32).decode("ascii")


def base_profile() -> str:
    return f"""[Interface]
PrivateKey = {key(1)}
Address = 10.212.13.2/32
DNS = 9.9.9.9, 149.112.112.112
MTU = 1280
S1 = 12
S2 = 12
S3 = 12
S4 = 12
H1 = 1
H2 = 2
H3 = 3
H4 = 4
HeaderProtectionKey = {key(2)}
ContentPaddingAddition = 0
RekeyAfterTime = 120
RekeyTimeout = 5
RejectAfterTime = 180
KeepaliveTimeout = 10
MaxHandshakeAttempts = 18
RandomTrailers = on
DisableCookies = on

[Peer]
PublicKey = {key(3)}
PresharedKey = {key(4)}
Endpoint = 138.124.181.246:30002
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""


def parse(text: str) -> configparser.ConfigParser:
    value = configparser.ConfigParser(interpolation=None, strict=True)
    value.optionxform = str
    value.read_string(text)
    return value


def run_tool(input_path: Path, output_path: Path, expected_sha256: str):
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(SOURCE),
            "--input",
            str(input_path),
            "--expected-input-sha256",
            expected_sha256,
            "--output",
            str(output_path),
        ],
        capture_output=True,
        timeout=10,
    )


class ClientRecoveryTests(unittest.TestCase):
    def test_jc6_i1_variant_adds_only_upstream_recovery_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            original = base_profile()
            input_path = directory / "base.conf"
            output_path = directory / "candidate.conf"
            input_path.write_text(original, encoding="ascii", newline="\n")

            result = run_tool(input_path, output_path, hashlib.sha256(original.encode("ascii")).hexdigest())

            self.assertEqual(result.returncode, 0, result.stderr.decode("ascii", errors="replace"))
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt, {
                "changed_keys": ["I1", "Jc", "Jmax", "Jmin"],
                "input_sha256": hashlib.sha256(original.encode("ascii")).hexdigest(),
                "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
                "result": "client_recovery_candidate_created",
                "secret_output": False,
            })

            before = parse(original)
            after = parse(output_path.read_text(encoding="ascii"))
            self.assertEqual(after["Interface"]["Jc"], "6")
            self.assertEqual(after["Interface"]["Jmin"], "10")
            self.assertEqual(after["Interface"]["Jmax"], "50")
            self.assertEqual(after["Interface"]["I1"], I1)
            for field in ("Jc", "Jmin", "Jmax", "I1"):
                del after["Interface"][field]
            self.assertEqual(
                {section: dict(after[section]) for section in after.sections()},
                {section: dict(before[section]) for section in before.sections()},
            )

    def test_candidate_fails_closed_on_hash_mismatch_existing_output_or_existing_field(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            sentinel = "PRIVATE_SENTINEL_MUST_NOT_ESCAPE"
            original = base_profile().replace(key(1), sentinel)
            input_path = directory / "base.conf"
            output_path = directory / "candidate.conf"
            input_path.write_text(original, encoding="ascii", newline="\n")

            bad_hash = run_tool(input_path, output_path, "0" * 64)
            self.assertEqual(bad_hash.returncode, 65)
            self.assertFalse(output_path.exists())
            self.assertNotIn(sentinel.encode(), bad_hash.stdout + bad_hash.stderr)

            input_path.write_text(base_profile(), encoding="ascii", newline="\n")
            output_path.write_text("do not overwrite", encoding="ascii")
            exists = run_tool(input_path, output_path, hashlib.sha256(base_profile().encode("ascii")).hexdigest())
            self.assertEqual(exists.returncode, 65)
            self.assertEqual(output_path.read_text(encoding="ascii"), "do not overwrite")

            output_path.unlink()
            with_field = base_profile().replace("MTU = 1280\n", "MTU = 1280\nJc = 3\n")
            input_path.write_text(with_field, encoding="ascii", newline="\n")
            duplicate = run_tool(input_path, output_path, hashlib.sha256(with_field.encode("ascii")).hexdigest())
            self.assertEqual(duplicate.returncode, 65)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
