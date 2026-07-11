import hashlib
import os
import shlex
import stat
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APPLY_SCRIPT = REPO_ROOT / "scripts" / "vps" / "amn2_apply_source_zip.sh"
GIT_BASH = Path(r"C:\Program Files\Git\bin\bash.exe")


def _to_bash_path(path: Path) -> str:
    result = subprocess.run(
        [str(GIT_BASH), "-lc", f"cygpath -u {shlex.quote(str(path))}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _bash(command: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [str(GIT_BASH), "-lc", command],
        capture_output=True,
        env=merged_env,
        text=True,
    )


def _write_minimal_source_zip(source_zip: Path) -> str:
    files = {
        "pyproject.toml": "\n".join(
            [
                "[build-system]",
                'requires = ["setuptools>=64"]',
                'build-backend = "setuptools.build_meta"',
                "",
                "[project]",
                'name = "amn2-apply-source-zip-test"',
                'version = "0.0.0"',
                "",
            ]
        ),
        "fastapi.py": "",
        "uvicorn.py": "",
        "app/__init__.py": "",
        "app/cli.py": "",
        "app/api/__init__.py": "",
        "app/api/app.py": "",
        "app/services/__init__.py": "",
        "app/services/api_smoke.py": "",
        "app/services/integration_status.py": "",
    }
    with zipfile.ZipFile(source_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return hashlib.sha256(source_zip.read_bytes()).hexdigest().upper()


class Amn2ApplySourceZipTests(unittest.TestCase):
    def test_overlay_tar_stream_does_not_include_staging_root_metadata(self) -> None:
        script = APPLY_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn("require_cmd tar", script)
        self.assertNotIn('tar -C "$STAGING" -cf - .', script)
        self.assertIn("permission_strategy=target-root-metadata-preserved", script)
        self.assertIn("service-readable source permissions", script)

    @unittest.skipUnless(GIT_BASH.exists(), "Git Bash is required for the live apply-script regression")
    def test_apply_preserves_target_directory_mode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amn2-apply-source-zip-") as temp_name:
            temp_dir = Path(temp_name)
            target = temp_dir / "target"
            run_root = temp_dir / "run-root"
            source_zip = temp_dir / "source.zip"
            target.mkdir()
            run_root.mkdir()
            (target / ".env").write_text("VPS_APPLY_ENABLED=false\n", encoding="utf-8")
            (target / "data").mkdir()

            venv_bin = target / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            python_wrapper = venv_bin / "python"
            python_wrapper.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        'if [ "${1:-}" = "-m" ] && [ "${2:-}" = "pip" ]; then',
                        '  echo "pip install stub"',
                        "  exit 0",
                        "fi",
                        'exec python "$@"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            python_wrapper.chmod(python_wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            source_sha = _write_minimal_source_zip(source_zip)
            target_posix = _to_bash_path(target)
            run_root_posix = _to_bash_path(run_root)
            source_zip_posix = _to_bash_path(source_zip)
            script_posix = _to_bash_path(APPLY_SCRIPT)

            chmod = _bash(f"chmod 755 {shlex.quote(target_posix)}")
            self.assertEqual(chmod.returncode, 0, chmod.stderr)
            before = _bash(f"stat -c %a {shlex.quote(target_posix)}")
            self.assertEqual(before.returncode, 0, before.stderr)
            self.assertEqual(before.stdout.strip(), "755")

            result = _bash(
                f"bash {shlex.quote(script_posix)}",
                env={
                    "AMN2_DIR": target_posix,
                    "AMN2_SOURCE_ZIP": source_zip_posix,
                    "AMN2_EXPECTED_SOURCE_SHA": source_sha,
                    "AMN2_EXPECTED_SOURCE_COMMIT": "test-commit",
                    "AMN2_UPDATE_LOG_DIR": run_root_posix,
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            after = _bash(f"stat -c %a {shlex.quote(target_posix)}")
            self.assertEqual(after.returncode, 0, after.stderr)
            self.assertEqual(after.stdout.strip(), "755")
            app_mode = _bash(f"stat -c %a {shlex.quote(target_posix + '/app')}")
            self.assertEqual(app_mode.returncode, 0, app_mode.stderr)
            self.assertEqual(int(app_mode.stdout.strip(), 8) & 0o050, 0o050)
            app_py_mode = _bash(f"stat -c %a {shlex.quote(target_posix + '/app/api/app.py')}")
            self.assertEqual(app_py_mode.returncode, 0, app_py_mode.stderr)
            self.assertEqual(int(app_py_mode.stdout.strip(), 8) & 0o040, 0o040)
            self.assertTrue((target / ".env").exists())
            self.assertTrue((target / "data").is_dir())
            self.assertEqual((target / ".amn2_source_overlay_commit").read_text(encoding="utf-8"), "test-commit\n")

    @unittest.skipUnless(GIT_BASH.exists(), "Git Bash is required for the live apply-script regression")
    def test_expected_offline_build_failure_uses_verified_source_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amn2-apply-offline-fallback-") as temp_name:
            temp_dir = Path(temp_name)
            target = temp_dir / "target"
            run_root = temp_dir / "run-root"
            source_zip = temp_dir / "source.zip"
            target.mkdir()
            run_root.mkdir()

            venv_bin = target / "venv" / "bin"
            venv_bin.mkdir(parents=True)
            python_wrapper = venv_bin / "python"
            python_wrapper.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        'if [ "${1:-}" = "-m" ] && [ "${2:-}" = "pip" ]; then',
                        '  echo "Could not find a version that satisfies the requirement setuptools>=69" >&2',
                        '  echo "No matching distribution found for setuptools>=69" >&2',
                        "  exit 1",
                        "fi",
                        'exec python "$@"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            python_wrapper.chmod(
                python_wrapper.stat().st_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )

            source_sha = _write_minimal_source_zip(source_zip)
            result = _bash(
                f"bash {shlex.quote(_to_bash_path(APPLY_SCRIPT))}",
                env={
                    "AMN2_DIR": _to_bash_path(target),
                    "AMN2_SOURCE_ZIP": _to_bash_path(source_zip),
                    "AMN2_EXPECTED_SOURCE_SHA": source_sha,
                    "AMN2_EXPECTED_SOURCE_COMMIT": "offline-test-commit",
                    "AMN2_UPDATE_LOG_DIR": _to_bash_path(run_root),
                },
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn(
                "pip_install_status=skipped_existing_source_path_after_expected_offline_build_stop",
                result.stdout,
            )
            source_import_check = run_root / "source-import-check.txt"
            self.assertTrue(source_import_check.exists())
            self.assertIn(
                str((target / "app" / "__init__.py").resolve()),
                source_import_check.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
