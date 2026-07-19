import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vps" / "post_release_spain_ssh_onboarding.ps1"
DOC = ROOT / "docs" / "POST_RELEASE_SPAIN_SSH_ONBOARDING.ru.md"
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
EXPECTED_PIN = "SHA256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"


def run_script(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    if not SCRIPT.exists():
        raise AssertionError("Spain SSH onboarding script is missing")
    command = [
        str(POWERSHELL),
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        *args,
    ]
    child_env = os.environ.copy()
    # pwsh exports a module path that is incompatible with Windows PowerShell 5.1.
    child_env.pop("PSModulePath", None)
    child_env.update(env or {})
    return subprocess.run(
        command,
        cwd=ROOT,
        env=child_env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def write_mock_icacls(directory: Path) -> tuple[Path, Path]:
    log = directory / "icacls.log"
    mock = directory / "icacls.cmd"
    mock.write_text(f'@echo off\r\necho %*>>"{log}"\r\nexit /b 0\r\n', encoding="ascii")
    return mock, log


def write_mock_keygen(directory: Path, key_path: Path, pin: str = EXPECTED_PIN) -> Path:
    mock = directory / "ssh-keygen.cmd"
    mock.write_text(
        "@echo off\r\n"
        "if \"%1\"==\"-t\" (\r\n"
        f'  echo private>"{key_path}"\r\n'
        f'  echo ssh-ed25519 QUJDRA== test>"{key_path}.pub"\r\n'
        "  exit /b 0\r\n"
        ")\r\n"
        "if \"%1\"==\"-y\" (\r\n"
        "  echo ssh-ed25519 QUJDRA==\r\n"
        "  exit /b 0\r\n"
        ")\r\n"
        f"echo 256 {pin} host (ED25519)\r\n"
        "exit /b 0\r\n",
        encoding="ascii",
    )
    return mock


def onboarding_env(mock_keygen: Path, pin: str = EXPECTED_PIN) -> dict[str, str]:
    return {
        "AMN2_SPAIN_TARGET_HOST": "spain.example.invalid",
        "AMN2_SPAIN_TARGET_USER": "amn2operator",
        "AMN2_SPAIN_EXPECTED_HOST_KEY_SHA256": pin,
        "AMN2_SPAIN_HOST_KEY_LINE": "ssh-ed25519 QUJDRA==",
        "AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES": "1",
        "AMN2_SPAIN_TEST_SSH_KEYGEN_EXE": str(mock_keygen),
    }


def prepare_and_bind(tmp: Path, run_id: str, pin: str = EXPECTED_PIN) -> tuple[Path, dict[str, str]]:
    root = tmp / "artifacts"
    key_path = root / run_id / "id_ed25519_spain"
    env = onboarding_env(write_mock_keygen(tmp, key_path, pin), pin)
    prepared = run_script("-Mode", "prepare-key", "-RunId", run_id, "-ArtifactRoot", str(root), env=env)
    if prepared.returncode != 0:
        raise AssertionError(prepared.stderr)
    bound = run_script("-Mode", "write-binding", "-RunId", run_id, "-ArtifactRoot", str(root), env=env)
    if bound.returncode != 0:
        raise AssertionError(bound.stderr)
    return root / run_id, env


@unittest.skipUnless(POWERSHELL.exists(), "Windows PowerShell is required")
class SpainSshOnboardingTests(unittest.TestCase):
    def test_script_declares_only_local_modes_and_hardened_future_ssh_contract(self) -> None:
        self.assertTrue(SCRIPT.exists(), "Spain SSH onboarding script is missing")
        source = SCRIPT.read_text(encoding="utf-8")
        for marker in (
            '"prepare-key"',
            '"write-binding"',
            '"verify-pin"',
            '"print-public-key"',
            r'C:\Windows\System32\OpenSSH\ssh.exe',
            r'C:\Windows\System32\OpenSSH\ssh-keygen.exe',
            '"-F", "none"',
            '"BatchMode=yes"',
            '"IdentitiesOnly=yes"',
            '"StrictHostKeyChecking=yes"',
            'UserKnownHostsFile=',
            'id_ed25519_spain',
            'known_hosts_spain',
            'private-artifacts/post-release/spain-migration',
            'TARGET_HOST',
            'TARGET_USER',
            'SSH_KEY_PATH',
            'EXPECTED_HOST_KEY_SHA256',
            'AMN2 Spain dedicated operator key',
            '& $SshKeygenExe -t ed25519',
            '/inheritance:r',
            '/grant:r',
            'SetAccessRuleProtection($true, $false)',
            'Get-Acl -LiteralPath',
        ):
            self.assertIn(marker, source)

        lowered = source.casefold()
        for forbidden in (
            "password",
            "sshpass",
            "plink",
            "putty",
            "stricthostkeychecking=no",
            "accept-new",
            "userknownhostsfile=nul",
            r".ssh\known_hosts",
            "invoke-expression",
            "ssh-keyscan",
        ):
            self.assertNotIn(forbidden, lowered)
        self.assertNotRegex(source, r"(?im)^\s*&\s*\$SshExe\b")
        self.assertNotIn("AMN2_SPAIN_TEST_ICACLS_EXE", source)
        self.assertNotIn('Move-Item -LiteralPath $CandidatePath -Destination $KnownHostsPath -Force', source)
        self.assertNotIn('@("/T", "/C")', source)
        verify = source.split('"verify-pin" {', 1)[1].split('"print-public-key" {', 1)[0]
        self.assertLess(verify.index("Assert-PrivatePath $BindingPath"), verify.index("$Binding = Read-Binding"))

    def test_write_binding_writes_exactly_four_private_lines_without_echoing_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            mock_icacls, acl_log = write_mock_icacls(tmp)
            env = {
                "AMN2_SPAIN_TARGET_HOST": "spain.example.invalid",
                "AMN2_SPAIN_TARGET_USER": "amn2operator",
                "AMN2_SPAIN_EXPECTED_HOST_KEY_SHA256": EXPECTED_PIN,
                "AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES": "1",
            }
            run_dir = tmp / "artifacts" / "test-run-001"
            run_dir.mkdir(parents=True)
            (run_dir / "id_ed25519_spain").write_text("private", encoding="ascii")
            (run_dir / "id_ed25519_spain.pub").write_text("ssh-ed25519 QUJDRA== test", encoding="ascii")
            env["AMN2_SPAIN_TEST_SSH_KEYGEN_EXE"] = str(write_mock_keygen(tmp, run_dir / "id_ed25519_spain"))
            result = run_script(
                "-Mode",
                "write-binding",
                "-RunId",
                "test-run-001",
                "-ArtifactRoot",
                str(tmp / "artifacts"),
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            binding = tmp / "artifacts" / "test-run-001" / "target.env"
            self.assertTrue(binding.read_bytes().startswith(b"TARGET_HOST="))
            lines = binding.read_text(encoding="utf-8-sig").splitlines()
            self.assertEqual(
                lines,
                [
                    "TARGET_HOST=spain.example.invalid",
                    "TARGET_USER=amn2operator",
                    f"SSH_KEY_PATH={tmp / 'artifacts' / 'test-run-001' / 'id_ed25519_spain'}",
                    f"EXPECTED_HOST_KEY_SHA256={EXPECTED_PIN}",
                ],
            )
            combined_output = result.stdout + result.stderr
            self.assertNotIn("spain.example.invalid", combined_output)
            self.assertNotIn("amn2operator", combined_output)
            self.assertNotIn(EXPECTED_PIN, combined_output)

    def test_write_binding_rejects_shell_metacharacters_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            mock_icacls, _ = write_mock_icacls(tmp)
            result = run_script(
                "-Mode",
                "write-binding",
                "-RunId",
                "test-run-002",
                "-ArtifactRoot",
                str(tmp / "artifacts"),
                env={
                    "AMN2_SPAIN_TARGET_HOST": "host.invalid;whoami",
                    "AMN2_SPAIN_TARGET_USER": "amn2operator",
                    "AMN2_SPAIN_EXPECTED_HOST_KEY_SHA256": EXPECTED_PIN,
                    "AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES": "1",
                },
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((tmp / "artifacts" / "test-run-002" / "target.env").exists())

    def test_write_binding_refuses_to_leave_a_stale_known_hosts_pin(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            run_dir = tmp / "artifacts" / "test-run-003"
            run_dir.mkdir(parents=True)
            (run_dir / "id_ed25519_spain").write_text("private", encoding="ascii")
            (run_dir / "id_ed25519_spain.pub").write_text("public", encoding="ascii")
            known_hosts = run_dir / "known_hosts_spain"
            known_hosts.write_text("old.invalid ssh-ed25519 QUJDRA==\n", encoding="ascii")
            mock_icacls, _ = write_mock_icacls(tmp)
            result = run_script(
                "-Mode", "write-binding", "-RunId", "test-run-003",
                "-ArtifactRoot", str(tmp / "artifacts"),
                env={
                    "AMN2_SPAIN_TARGET_HOST": "new.invalid",
                    "AMN2_SPAIN_TARGET_USER": "amn2operator",
                    "AMN2_SPAIN_EXPECTED_HOST_KEY_SHA256": EXPECTED_PIN,
                    "AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES": "1",
                },
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "target.env").exists())
            self.assertEqual(known_hosts.read_text(encoding="ascii"), "old.invalid ssh-ed25519 QUJDRA==\n")

    def test_verify_pin_requires_the_dedicated_key_pair(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            run_dir = tmp / "artifacts" / "test-run-004"
            run_dir.mkdir(parents=True)
            key_path = run_dir / "id_ed25519_spain"
            (run_dir / "target.env").write_text(
                "\n".join((
                    "TARGET_HOST=spain.example.invalid",
                    "TARGET_USER=amn2operator",
                    f"SSH_KEY_PATH={key_path}",
                    f"EXPECTED_HOST_KEY_SHA256={EXPECTED_PIN}",
                )) + "\n",
                encoding="utf-8",
            )
            mock_icacls, _ = write_mock_icacls(tmp)
            mock_keygen = write_mock_keygen(tmp, key_path)
            result = run_script(
                "-Mode", "verify-pin", "-RunId", "test-run-004",
                "-ArtifactRoot", str(tmp / "artifacts"),
                env={
                    "AMN2_SPAIN_HOST_KEY_LINE": "ssh-ed25519 QUJDRA==",
                    "AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES": "1",
                    "AMN2_SPAIN_TEST_SSH_KEYGEN_EXE": str(mock_keygen),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "known_hosts_spain").exists())

    def test_verify_pin_succeeds_once_and_refuses_existing_pin(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            run_dir, env = prepare_and_bind(tmp, "test-run-005")
            args = ("-Mode", "verify-pin", "-RunId", "test-run-005", "-ArtifactRoot", str(tmp / "artifacts"))
            first = run_script(*args, env=env)
            self.assertEqual(first.returncode, 0, first.stderr)
            known_hosts = run_dir / "known_hosts_spain"
            first_bytes = known_hosts.read_bytes()
            second = run_script(*args, env=env)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(known_hosts.read_bytes(), first_bytes)

    def test_write_binding_rejects_mismatched_ed25519_public_key(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            root = tmp / "artifacts"
            run_dir = root / "test-run-006"
            run_dir.mkdir(parents=True)
            key_path = run_dir / "id_ed25519_spain"
            key_path.write_text("private", encoding="ascii")
            (run_dir / "id_ed25519_spain.pub").write_text("ssh-ed25519 RUZHSA== wrong\n", encoding="ascii")
            env = onboarding_env(write_mock_keygen(tmp, key_path))
            result = run_script("-Mode", "write-binding", "-RunId", "test-run-006", "-ArtifactRoot", str(root), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "target.env").exists())

    def test_write_binding_rejects_invalid_private_key(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            root = tmp / "artifacts"
            run_dir = root / "test-run-009"
            run_dir.mkdir(parents=True)
            key_path = run_dir / "id_ed25519_spain"
            key_path.write_text("not-a-private-key", encoding="ascii")
            (run_dir / "id_ed25519_spain.pub").write_text("ssh-ed25519 QUJDRA== test\n", encoding="ascii")
            mock = tmp / "ssh-keygen-invalid.cmd"
            mock.write_text('@echo off\r\nif "%1"=="-y" exit /b 1\r\nexit /b 0\r\n', encoding="ascii")
            env = onboarding_env(mock)
            result = run_script("-Mode", "write-binding", "-RunId", "test-run-009", "-ArtifactRoot", str(root), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "target.env").exists())

    def test_verify_pin_rejects_fingerprint_mismatch_without_publishing(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            run_dir, env = prepare_and_bind(tmp, "test-run-007")
            mismatched = "SHA256:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
            env["AMN2_SPAIN_TEST_SSH_KEYGEN_EXE"] = str(write_mock_keygen(tmp, run_dir / "id_ed25519_spain", mismatched))
            result = run_script("-Mode", "verify-pin", "-RunId", "test-run-007", "-ArtifactRoot", str(tmp / "artifacts"), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "known_hosts_spain").exists())
            self.assertFalse((run_dir / "known_hosts_spain.candidate").exists())

    def test_verify_pin_rejects_broadened_binding_acl_before_read(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            run_dir, env = prepare_and_bind(tmp, "test-run-008")
            binding = run_dir / "target.env"
            acl = subprocess.run(
                [r"C:\Windows\System32\icacls.exe", str(binding), "/grant", "*S-1-5-32-545:R"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(acl.returncode, 0, acl.stderr)
            result = run_script("-Mode", "verify-pin", "-RunId", "test-run-008", "-ArtifactRoot", str(tmp / "artifacts"), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((run_dir / "known_hosts_spain").exists())

    def test_documentation_keeps_the_only_remote_step_interactive_and_out_of_band(self) -> None:
        self.assertTrue(DOC.exists(), "Spain SSH onboarding runbook is missing")
        doc = DOC.read_text(encoding="utf-8")
        for marker in (
            "provider console",
            "authorized_keys",
            "print-public-key",
            "verify-pin",
            "out-of-band",
            "private-artifacts/post-release/spain-migration/<run_id>/",
        ):
            self.assertIn(marker, doc)
        self.assertNotRegex(doc, r"(?i)sshpass|accept-new|StrictHostKeyChecking\s*=\s*no")


if __name__ == "__main__":
    unittest.main()
