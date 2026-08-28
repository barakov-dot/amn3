from __future__ import annotations

import base64
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/vps/phase16_awg31_minimal_pilot.py"


def module():
    spec = importlib.util.spec_from_file_location("minimal_pilot", SOURCE)
    value = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = value
    spec.loader.exec_module(value)
    return value


def synthetic_keys():
    return {name: base64.b64encode(bytes([i]) * 32).decode("ascii") for i, name in enumerate(
        ("server_private", "server_public", "client_private", "client_public", "psk", "hpk"), 1
    )}


class FakeDocker:
    def __init__(self, failure=None):
        self.calls = []
        self.failure = failure

    def __call__(self, *args, **kwargs):
        self.calls.append(args)
        if self.failure and self.failure(args):
            raise RuntimeError("SYNTHETIC_PRIVATE_MATERIAL_MUST_NOT_ESCAPE")
        if args[:2] == ("network", "create"):
            return "a" * 64
        if args and args[0] == "create":
            return "b" * 64
        if args[:2] == ("container", "inspect"):
            return "running"
        return ""


class MinimalPilotTests(unittest.TestCase):
    def test_userspace_profiles_omit_kernel_only_advanced_security(self):
        m = module()
        keys = synthetic_keys()
        profiles = m.render_pair(keys, dns="1.1.1.1", mtu=1280)
        for body in profiles.values():
            self.assertNotIn("AdvancedSecurity", body)
            self.assertIn("HeaderProtectionKey = " + keys["hpk"], body)
            for field in ("S1", "S2", "S3", "S4"):
                self.assertIn(field + " = 12\n", body)
            self.assertEqual(body.count("[Peer]"), 1)
        self.assertEqual(m.INPUT_DIR, Path("/var/lib/amn2-phase16/pilot-input-v2"))
        m.validate_pair(profiles)
        incompatible = dict(profiles)
        incompatible["server.conf"] += "AdvancedSecurity = on\n"
        with self.assertRaises(m.PilotError):
            m.validate_pair(incompatible)

    def test_00_runtime_only_contract_exists(self):
        self.assertTrue(SOURCE.is_file(), "missing independent runtime-only implementation")
        m = module()
        self.assertEqual(m.PEER_COUNT, 1)

    def test_pilot_inputs_use_root_owned_phase16_namespace(self):
        m = module()
        self.assertEqual(m.INPUT_DIR, Path("/var/lib/amn2-phase16/pilot-input-v2"))
        self.assertEqual(m.INPUT_DIR.parent, m.CLAIM_ROOT.parent)
        nonroot_parent = SimpleNamespace(
            parents=(), exists=lambda: True, is_symlink=lambda: False,
            lstat=lambda: SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_uid=1000),
        )
        with patch.object(m, "os", SimpleNamespace(name="posix")):
            with self.assertRaisesRegex(m.PilotError, "^unsafe_parent_directory$"):
                m.secure_parent_chain(nonroot_parent)

    def test_default_cli_is_declarative_and_secret_free(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(SOURCE)], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        value = json.loads(result.stdout)
        self.assertFalse(value["executes_commands"])
        self.assertFalse(value["general_issuance_enabled"])
        self.assertEqual(value["peer_count"], 1)
        self.assertEqual(value["target"], "138.124.181.246")

    def test_profiles_are_native_and_share_server_parameters(self):
        m = module()
        profiles = m.render_pair(synthetic_keys(), dns="1.1.1.1", mtu=1280)
        self.assertEqual(set(profiles), {"server.conf", "windows.conf"})
        for text in profiles.values():
            self.assertEqual(text.count("[Peer]"), 1)
            for line in ("S1 = 12", "S2 = 12", "S3 = 12", "S4 = 12", "RandomTrailers = on", "DisableCookies = on"):
                self.assertIn(line, text)
        self.assertIn("AllowedIPs = 10.212.13.2/32", profiles["server.conf"])
        self.assertIn("AllowedIPs = 0.0.0.0/0, ::/0", profiles["windows.conf"])
        self.assertIn("Endpoint = 138.124.181.246:30002", profiles["windows.conf"])
        self.assertNotIn("Address =", profiles["server.conf"])
        m.validate_pair(profiles)

    def test_invalid_inputs_are_rejected_without_echoing_values(self):
        m = module()
        for field, bad in (("hpk", "PRIVATE_SENTINEL\nPostUp = evil"), ("client_private", "bad")):
            with self.subTest(field=field):
                keys = dict(synthetic_keys(), **{field: bad})
                with self.assertRaises(m.PilotError) as caught:
                    m.render_pair(keys, dns="1.1.1.1", mtu=1280)
                self.assertNotIn(bad, str(caught.exception))
        for dns, mtu in (("1.1.1.1\nPostUp=evil", 1280), ("1.1.1.1", 500), ("1.1.1.1", True)):
            with self.assertRaises(m.PilotError):
                m.render_pair(synthetic_keys(), dns=dns, mtu=mtu)

    def test_pair_mismatch_extra_peer_and_hooks_fail_closed(self):
        m = module()
        original = m.render_pair(synthetic_keys(), dns="1.1.1.1", mtu=1280)
        for changed in (original["windows.conf"].replace("S1 = 12", "S1 = 13"),
                        original["windows.conf"] + "\n[Peer]\nPublicKey = bogus\n",
                        original["windows.conf"].replace("[Interface]", "[Interface]\nPostUp = evil")):
            with self.assertRaises(m.PilotError):
                m.validate_pair(dict(original, **{"windows.conf": changed}))

    def test_container_startup_scripts_have_valid_shell_syntax(self):
        m = module()
        bash = Path("C:/Program Files/Git/bin/bash.exe")
        self.assertTrue(bash.exists(), "local shell syntax check requires Git Bash")
        for script in (m.NATIVE_CHECK, m.RUNTIME_START, m.RUNTIME_HEALTH):
            result = subprocess.run([str(bash), "--noprofile", "--norc", "-n"], input=script.encode(), capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertIn("awg-quick strip", m.NATIVE_CHECK)
        self.assertIn("awg setconf", m.NATIVE_CHECK)
        self.assertIn("amneziawg-go -f", m.RUNTIME_START)

    def prepare_apply(self, m, directory, docker):
        profiles = m.render_pair(synthetic_keys(), dns="1.1.1.1", mtu=1280)
        hashes = {name: hashlib.sha256(value.encode()).hexdigest() for name, value in profiles.items()}
        state = {"target": m.TARGET, "awg2_snapshot": "1" * 64, "ready": True}
        stack = contextlib.ExitStack()
        stack.enter_context(patch.object(m, "INPUT_DIR", directory / "inputs"))
        stack.enter_context(patch.object(m, "CLAIM_ROOT", directory / "claims"))
        stack.enter_context(patch.object(m, "load_profiles", return_value=profiles))
        stack.enter_context(patch.object(m, "preflight", return_value=state))
        stack.enter_context(patch.object(m, "awg2_snapshot", return_value="1" * 64))
        stack.enter_context(patch.object(m, "require_linux_root"))
        self.addCleanup(stack.close)
        request = dict(script_sha256=m.script_sha256(), state_sha256=m.fingerprint(state),
                       server_sha256=hashes["server.conf"], client_sha256=hashes["windows.conf"], claim="pilot-test-001")
        return request, state

    def test_wrong_bindings_cannot_create_claim_or_docker_resources(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            docker = FakeDocker()
            request, _ = self.prepare_apply(m, directory, docker)
            for field in ("script_sha256", "state_sha256", "server_sha256", "client_sha256"):
                with self.subTest(field=field), self.assertRaises(m.PilotError):
                    m.apply_pilot(docker, **dict(request, **{field: "0" * 64}))
            self.assertFalse((directory / "claims").exists())
            self.assertEqual(docker.calls, [])

    def test_native_check_precedes_resource_creation_and_port_publication(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker()
            request, _ = self.prepare_apply(m, Path(temp), docker)
            result = m.apply_pilot(docker, **request)
            self.assertEqual(result["result"], "pilot_started_client_test_pending")
            native = next(i for i, args in enumerate(docker.calls) if args and args[0] == "run")
            network = next(i for i, args in enumerate(docker.calls) if args[:2] == ("network", "create"))
            create = next(args for args in docker.calls if args and args[0] == "create")
            self.assertLess(native, network)
            self.assertIn("none", docker.calls[native])
            self.assertIn("--pull=never", create)
            self.assertIn("30002:30002/udp", create)
            self.assertIn("net.ipv4.ip_forward=1", create)
            self.assertNotIn("--privileged", create)
            self.assertNotIn("--network=host", create)
            self.assertFalse(any("awg2" in str(args) for args in docker.calls))
            self.assertTrue((Path(temp) / "claims" / request["claim"]).is_file())
            with self.assertRaises(m.PilotError):
                m.apply_pilot(docker, **request)

    def test_native_check_failure_keeps_claim_but_creates_no_network(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker(lambda args: args and args[0] == "run")
            request, _ = self.prepare_apply(m, Path(temp), docker)
            with self.assertRaises(m.PilotError) as caught:
                m.apply_pilot(docker, **request)
            self.assertNotIn("SYNTHETIC_PRIVATE", str(caught.exception))
            self.assertFalse(any(args[:2] == ("network", "create") for args in docker.calls))
            self.assertTrue((Path(temp) / "claims" / request["claim"]).is_file())

    def test_failed_start_removes_only_returned_owned_resource_ids(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker(lambda args: args and args[0] == "start")
            request, _ = self.prepare_apply(m, Path(temp), docker)
            with self.assertRaises(m.PilotError):
                m.apply_pilot(docker, **request)
            self.assertIn(("rm", "-f", "b" * 64), docker.calls)
            self.assertIn(("network", "rm", "a" * 64), docker.calls)
            self.assertFalse(any("prune" in args for args in docker.calls))

    def test_awg2_state_change_forces_pilot_rollback_without_awg2_write(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker()
            request, _ = self.prepare_apply(m, Path(temp), docker)
            with patch.object(m, "awg2_snapshot", return_value="2" * 64), self.assertRaises(m.PilotError):
                m.apply_pilot(docker, **request)
            self.assertIn(("rm", "-f", "b" * 64), docker.calls)

    def test_docker_argv_is_dedicated_and_raw_errors_are_not_returned(self):
        m = module()
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(m.DOCKER_PATH, "/opt/amn2-spain/docker/bin/docker")
        self.assertNotIn("paramiko", source)
        failed = subprocess.CompletedProcess([], 1, b"PRIVATE_SENTINEL", b"PRIVATE_SENTINEL")
        with patch.object(m.subprocess, "run", return_value=failed) as run:
            with self.assertRaises(m.PilotError) as caught:
                m.Docker()("version")
        self.assertNotIn("PRIVATE_SENTINEL", str(caught.exception))
        self.assertEqual(run.call_args.args[0][:3], [m.DOCKER_PATH, "--host", m.DOCKER_SOCKET])

    def test_outcome_write_failure_rolls_back_started_runtime(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker()
            request, _ = self.prepare_apply(m, Path(temp), docker)
            original = m.append_record
            def append(descriptor, record):
                if record.get("result") == "pilot_started_client_test_pending":
                    raise OSError("SYNTHETIC_DISK_FAILURE")
                return original(descriptor, record)
            with patch.object(m, "append_record", side_effect=append), self.assertRaises(m.PilotError):
                m.apply_pilot(docker, **request)
            self.assertIn(("rm", "-f", "b" * 64), docker.calls)
            self.assertIn(("network", "rm", "a" * 64), docker.calls)

    def test_rollback_failure_is_not_reported_as_restored(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker(lambda args: args and args[0] in ("start", "rm"))
            request, _ = self.prepare_apply(m, Path(temp), docker)
            with self.assertRaisesRegex(m.PilotError, "failed_or_unknown"):
                m.apply_pilot(docker, **request)
            self.assertIn(("network", "rm", "a" * 64), docker.calls)
            records = (Path(temp) / "claims" / request["claim"]).read_text().splitlines()
            self.assertEqual(json.loads(records[-1])["rollback"], "failed_or_unknown")

    def test_apply_uses_its_own_config_snapshot(self):
        m = module()
        with tempfile.TemporaryDirectory() as temp:
            docker = FakeDocker()
            request, _ = self.prepare_apply(m, Path(temp), docker)
            m.apply_pilot(docker, **request)
            snapshot = Path(temp) / "claims" / (request["claim"] + "-files")
            self.assertEqual(hashlib.sha256((snapshot / "server.conf").read_bytes()).hexdigest(), request["server_sha256"])
            create = next(args for args in docker.calls if args and args[0] == "create")
            self.assertIn(f"type=bind,src={snapshot / 'server.conf'},dst=/input/server.conf,readonly", create)
            self.assertNotIn("windows.conf", str(create))

    def test_preflight_accepts_builtin_null_ipam_and_rejects_conflicts(self):
        m = module()
        for case in ("free", "wrong_host", "udp_busy", "route_overlap", "docker_overlap", "verifier_exists"):
            with self.subTest(case=case):
                def host_command(args, **kwargs):
                    if "address" in args:
                        return json.dumps([{"addr_info": [{"local": "127.0.0.1" if case == "wrong_host" else m.TARGET}]}])
                    if "route" in args:
                        return json.dumps([{"dst": "10.212.13.0/24"}] if case == "route_overlap" else [{"dst": "default"}])
                    return "occupied" if case == "udp_busy" else ""
                def docker(*args, **kwargs):
                    if args[0] == "version":
                        return "linux/amd64"
                    if args[:2] == ("network", "inspect"):
                        config = [{"Subnet": "172.29.252.0/28"}] if case == "docker_overlap" else None
                        return json.dumps([{"IPAM": {"Config": config}}])
                    if args == ("network", "ls", "-q"):
                        return "existing-network"
                    if case == "verifier_exists" and any("-check$" in arg for arg in args):
                        return "existing-container"
                    return ""
                with patch.object(m, "require_host_prerequisites"), patch.object(m, "command", side_effect=host_command), patch.object(m, "awg2_snapshot", return_value="1" * 64):
                    if case == "free":
                        self.assertTrue(m.preflight(docker)["ready"])
                    else:
                        with self.assertRaises(m.PilotError):
                            m.preflight(docker)

    def test_awg2_snapshot_uses_observed_spain_container_and_interface_read_only(self):
        m = module()
        calls = []
        def docker(*args, **kwargs):
            calls.append(args)
            if args[0] == "ps":
                return "a" * 12
            if args[0] == "inspect":
                return json.dumps([{"Id": "a" * 64, "Image": "image", "HostConfig": {}, "Mounts": [],
                                    "RestartCount": 0, "State": {"Running": True, "StartedAt": "fixed"}}])
            return "SYNTHETIC_PEER_PUBLIC_KEY"
        with patch.object(m, "command", return_value="active\nrunning\nenabled"):
            digest = m.awg2_snapshot(docker)
        self.assertEqual(len(digest), 64)
        self.assertIn(("exec", "amn2-spain-awg", "/usr/bin/awg", "show", "awgsp0", "peers"), calls)
        self.assertTrue(all(args[0] in ("ps", "inspect", "exec") for args in calls))

    def test_awg2_fingerprint_ignores_peer_order_but_preserves_peer_changes(self):
        m = module()
        fingerprints = []
        for peers in ("PEER_A\nPEER_B", "PEER_B\nPEER_A", "PEER_A\nPEER_C", "PEER_A\nPEER_A\nPEER_B"):
            def docker(*args, **kwargs):
                if args[0] == "ps":
                    return "a" * 12
                if args[0] == "inspect":
                    return json.dumps([{"Id": "a" * 64, "Image": "fixed", "HostConfig": {}, "Mounts": [],
                                        "RestartCount": 0, "State": {"Running": True, "StartedAt": "fixed"}}])
                return peers
            with patch.object(m, "command", return_value="active\nrunning\nenabled"):
                fingerprints.append(m.awg2_snapshot(docker))
        self.assertEqual(fingerprints[0], fingerprints[1])
        self.assertNotEqual(fingerprints[0], fingerprints[2])
        self.assertNotEqual(fingerprints[0], fingerprints[3])

    def test_live_cli_modes_refuse_windows_before_any_external_command(self):
        m = module()
        for argv in (["check"], ["render", "--key-directory", "missing", "--dns", "1.1.1.1"]):
            with patch.object(m.sys, "platform", "win32"), patch.object(m, "command") as command:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(m.main(argv), 64)
                self.assertEqual(json.loads(output.getvalue())["reason"], "linux_amd64_root_required")
                command.assert_not_called()

    def test_readonly_check_does_not_require_uncreated_keys_or_profiles(self):
        m = module()
        state = {"target": m.TARGET, "ready": True, "awg2_snapshot": "1" * 64}
        with patch.object(m, "require_linux_root"), patch.object(m, "preflight", return_value=state):
            with patch.object(m, "load_profiles", side_effect=AssertionError("must not read profiles")) as load:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(m.main(["check"]), 0)
                self.assertEqual(json.loads(output.getvalue())["state_sha256"], m.fingerprint(state))
                load.assert_not_called()
            profiles = m.render_pair(synthetic_keys(), dns="1.1.1.1", mtu=1280)
            with patch.object(m, "load_profiles", return_value=profiles) as load:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(m.main(["check", "--with-profiles"]), 0)
                self.assertEqual(set(json.loads(output.getvalue())["sha256"]), set(m.PROFILES))
                load.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
