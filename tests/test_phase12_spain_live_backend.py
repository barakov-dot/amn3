from __future__ import annotations

import json
import hashlib
import inspect
import io
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from scripts import phase12_spain_live_backend as live_backend

from scripts.phase12_spain_live_backend import (
    BackendError,
    FixedCommandRunner,
    LinuxBackend,
    MutationLedger,
    DurableMutationLedgerStore,
    OwnedOperation,
    SystemOwnedAdapter,
    build_directory_action,
    build_file_action,
    build_posix_identity_actions,
    build_fixed_identity_bundle,
    StructuredPosixIdentityObserver,
    IDENTITY_COMMAND_ALLOWLIST,
    build_network_contour_action,
    network_contour_identity,
    build_clean_database_action,
    build_production_clean_database_action,
    build_deferred_production_clean_database_action,
    source_tree_identity,
    build_systemd_unit_actions,
    build_source_tree_action,
    build_wheel_tree_action,
    build_deferred_source_tree_action,
    build_deferred_wheel_tree_action,
    read_canonical_root_json,
    SafeFs,
    AWG_IMAGE_CONFIG_DIGEST,
    AWG_LOCAL_IMAGE_TAG,
    AWG_IMAGE_REFERENCE,
    STATIC_DOCKER_RELATIVE_PATHS,
    build_container_create_argv,
    build_docker_network_argv,
    verify_loaded_awg_image,
    initialize_clean_database,
    generate_server_keypair,
    render_awg_config,
    render_servers_yml,
    strict_postinstall_observation,
    REQUIRED_CLOSED_DELTA_OBJECTS,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "packaging" / "phase12-spain" / "templates"


class FixedCommandRunnerTests(unittest.TestCase):
    def test_rejects_non_absolute_or_unregistered_argv(self) -> None:
        runner = FixedCommandRunner(allowed_argv={(sys.executable, "-c", "print('ok')")})
        with self.assertRaisesRegex(BackendError, "absolute"):
            runner(("python", "-c", "print('ok')"))
        with self.assertRaisesRegex(BackendError, "allowlist"):
            runner((sys.executable, "-c", "print('different')"))

    def test_runs_without_shell_and_bounds_timeout_and_combined_output(self) -> None:
        ok = (sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'ok')")
        timeout = (sys.executable, "-c", "import time; time.sleep(2)")
        oversized = (sys.executable, "-c", "print('x' * 1100000)")
        runner = FixedCommandRunner(
            allowed_argv={ok, timeout, oversized}, timeout_seconds=0.05
        )
        self.assertEqual(runner(ok), b"ok")
        with self.assertRaisesRegex(BackendError, "timed out"):
            runner(timeout)
        with self.assertRaisesRegex(BackendError, "output exceeded"):
            FixedCommandRunner(allowed_argv={oversized})(oversized)

    def test_failure_redacts_registered_secrets_and_stderr(self) -> None:
        secret = "private-value"
        argv = (sys.executable, "-c", f"import sys; sys.stderr.write('{secret}'); sys.exit(7)")
        runner = FixedCommandRunner(allowed_argv={argv}, redactions={secret})
        with self.assertRaises(BackendError) as caught:
            runner(argv)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, repr(caught.exception))

    def test_streams_large_regular_fd_without_the_small_input_bytes_limit(self) -> None:
        argv = (
            sys.executable,
            "-c",
            "import sys; print(len(sys.stdin.buffer.read()))",
        )
        payload = b"x" * (1024 * 1024 + 17)
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "image.tar"
            path.write_bytes(payload)
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
            try:
                runner = FixedCommandRunner(allowed_argv={argv})
                self.assertEqual(
                    runner(argv, input_fd=descriptor, input_size=len(payload)).strip(),
                    str(len(payload)).encode("ascii"),
                )
            finally:
                os.close(descriptor)

    def test_fd_stream_requires_exact_regular_stable_size_and_excludes_bytes(self) -> None:
        argv = (sys.executable, "-c", "pass")
        runner = FixedCommandRunner(allowed_argv={argv})
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "image.tar"
            path.write_bytes(b"payload")
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
            try:
                with self.assertRaisesRegex(BackendError, "boundary"):
                    runner(argv, input_fd=descriptor, input_size=8)
                with self.assertRaisesRegex(BackendError, "boundary"):
                    runner(
                        argv,
                        input_bytes=b"payload",
                        input_fd=descriptor,
                        input_size=7,
                    )
            finally:
                os.close(descriptor)

    def test_fd_stream_timeout_is_not_blocked_by_child_that_never_reads(self) -> None:
        argv = (sys.executable, "-c", "import time; time.sleep(2)")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "image.tar"
            path.write_bytes(b"x" * (2 * 1024 * 1024))
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
            try:
                runner = FixedCommandRunner(
                    allowed_argv={argv}, timeout_seconds=0.05
                )
                with self.assertRaisesRegex(BackendError, "timed out"):
                    runner(argv, input_fd=descriptor, input_size=path.stat().st_size)
            finally:
                os.close(descriptor)

    def test_small_bytes_input_timeout_is_not_blocked_by_child_that_never_reads(self) -> None:
        argv = (sys.executable, "-c", "import time; time.sleep(2)")
        runner = FixedCommandRunner(allowed_argv={argv}, timeout_seconds=0.05)
        with self.assertRaisesRegex(BackendError, "timed out"):
            runner(argv, input_bytes=b"x" * live_backend.MAX_COMMAND_INPUT)

    def test_fd_stream_rejects_successful_short_read(self) -> None:
        argv = (
            sys.executable,
            "-c",
            "import os,sys; os.read(sys.stdin.fileno(),1)",
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "image.tar"
            path.write_bytes(b"payload")
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
            try:
                runner = FixedCommandRunner(allowed_argv={argv})
                with self.assertRaisesRegex(BackendError, "truncated"):
                    runner(argv, input_fd=descriptor, input_size=7)
            finally:
                os.close(descriptor)


class SafeFsTests(unittest.TestCase):
    def test_safe_fs_binds_expected_gid_as_well_as_uid(self) -> None:
        self.assertIn("expected_gid", inspect.signature(SafeFs).parameters)

    def test_write_is_root_relative_nofollow_and_exact_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fs = SafeFs(root=root, expected_uid=os.getuid() if hasattr(os, "getuid") else None)
            fs.mkdir("etc/amn2-spain", 0o700)
            identity = fs.write_file("etc/amn2-spain/runtime.env", b"VPS_APPLY_ENABLED=false\n", 0o600)
            path = root / "etc" / "amn2-spain" / "runtime.env"
            self.assertEqual(path.read_bytes(), b"VPS_APPLY_ENABLED=false\n")
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(identity, fs.identity("etc/amn2-spain/runtime.env"))

    def test_rejects_traversal_and_symlink_component(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside:
            root = Path(raw)
            fs = SafeFs(root=root, expected_uid=os.getuid() if hasattr(os, "getuid") else None)
            with self.assertRaisesRegex(BackendError, "relative"):
                fs.write_file("../escape", b"x", 0o600)
            (root / "etc").mkdir()
            try:
                (root / "etc" / "link").symlink_to(Path(outside), target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(BackendError, "symlink"):
                fs.write_file("etc/link/escape", b"x", 0o600)

    def test_parent_swap_to_symlink_cannot_redirect_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside_raw:
            root = Path(raw)
            outside = Path(outside_raw)
            (root / "etc" / "owned").mkdir(parents=True)
            probe = root / "symlink-probe"
            try:
                probe.symlink_to(outside, target_is_directory=True)
                probe.unlink()
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")

            class RacingSafeFs(SafeFs):
                raced = False

                def _path(self, relative: str, *, allow_missing_leaf: bool = True) -> Path:
                    result = super()._path(relative, allow_missing_leaf=allow_missing_leaf)
                    if relative == "etc/owned" and not self.raced:
                        self.raced = True
                        result.rmdir()
                        result.symlink_to(outside, target_is_directory=True)
                    return result

            fs = RacingSafeFs(root=root, expected_uid=os.getuid() if hasattr(os, "getuid") else None)
            with self.assertRaisesRegex(BackendError, "symlink"):
                fs.write_file("etc/owned/secret", b"must-stay-contained", 0o600)
            self.assertFalse((outside / "secret").exists())

    @unittest.skipIf(os.name == "nt", "POSIX dirfd semantics")
    def test_posix_mutations_and_removal_use_dirfd_nofollow(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fs = SafeFs(root=root, expected_uid=os.getuid())
            real_open = os.open
            calls: list[dict[str, object]] = []

            def recording_open(*args: object, **kwargs: object) -> int:
                calls.append(dict(kwargs))
                return real_open(*args, **kwargs)

            with patch(
                "scripts.phase12_spain_live_backend.os.open",
                side_effect=recording_open,
            ):
                fs.mkdir("etc", 0o700)
                fs.mkdir("etc/amn2-spain", 0o700)
                identity = fs.write_file(
                    "etc/amn2-spain/runtime.env", b"x\n", 0o600
                )
                fs.remove_exact("etc/amn2-spain/runtime.env", identity)
            self.assertTrue(any("dir_fd" in call for call in calls))

    @unittest.skipIf(os.name == "nt", "POSIX fchown semantics")
    def test_new_directories_and_files_are_fchowned_to_exact_uid_gid(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            uid = os.getuid()
            gid = os.getgid()
            fs = SafeFs(root=root, expected_uid=uid, expected_gid=gid)
            with patch(
                "scripts.phase12_spain_live_backend.os.fchown", wraps=os.fchown
            ) as fchown:
                fs.mkdir("owned", 0o750)
                fs.write_file("owned/config", b"safe\n", 0o640)
            self.assertGreaterEqual(fchown.call_count, 2)
            for path, mode in (
                (root / "owned", 0o750),
                (root / "owned/config", 0o640),
            ):
                info = os.lstat(path)
                self.assertEqual((info.st_uid, info.st_gid), (uid, gid))
                self.assertEqual(stat.S_IMODE(info.st_mode), mode)


class MutationLedgerTests(unittest.TestCase):
    def test_intent_commit_remove_chain_and_round_trip(self) -> None:
        ledger = MutationLedger(allowed_objects={"file:/etc/amn2-spain/runtime.env"})
        desired = "sha256:" + "1" * 64
        actual = "sha256:" + "2" * 64
        ledger.intent("files", "file:/etc/amn2-spain/runtime.env", desired)
        ledger.commit("files", "file:/etc/amn2-spain/runtime.env", actual)
        ledger.removed("files", "file:/etc/amn2-spain/runtime.env", actual)
        restored = MutationLedger.from_mapping(
            json.loads(json.dumps(ledger.to_mapping())),
            allowed_objects={"file:/etc/amn2-spain/runtime.env"},
        )
        self.assertEqual(restored.state("file:/etc/amn2-spain/runtime.env"), "removed")

    def test_rejects_forged_torn_or_out_of_order_events(self) -> None:
        allowed = {"file:/etc/amn2-spain/runtime.env"}
        ledger = MutationLedger(allowed_objects=allowed)
        ledger.intent("files", next(iter(allowed)), "sha256:" + "1" * 64)
        forged = ledger.to_mapping()
        forged["events"][0]["desired_identity"] = "sha256:forged"
        with self.assertRaisesRegex(BackendError, "chain"):
            MutationLedger.from_mapping(forged, allowed_objects=allowed)
        with self.assertRaisesRegex(BackendError, "intent"):
            MutationLedger(allowed_objects=allowed).commit(
                "files", next(iter(allowed)), "sha256:" + "2" * 64
            )

    def test_canonical_bytes_reject_torn_trailing_and_oversized_ledger(self) -> None:
        allowed = {"file:/etc/amn2-spain/runtime.env"}
        ledger = MutationLedger(allowed_objects=allowed)
        ledger.intent("files", next(iter(allowed)), "sha256:" + "1" * 64)
        payload = ledger.to_bytes()
        restored = MutationLedger.from_bytes(payload, allowed_objects=allowed)
        self.assertEqual(restored.state(next(iter(allowed))), "intent")
        for malformed in (payload[:-1], payload + b"x", b"{" + b"x" * (1024 * 1024)):
            with self.subTest(length=len(malformed)):
                with self.assertRaisesRegex(BackendError, "ledger"):
                    MutationLedger.from_bytes(malformed, allowed_objects=allowed)

    def test_every_transition_is_persisted_and_failed_persist_is_not_adopted(self) -> None:
        snapshots: list[bytes] = []
        owned = "file:/etc/amn2-spain/runtime.env"
        ledger = MutationLedger(allowed_objects={owned}, persist=snapshots.append)
        ledger.intent("files", owned, "sha256:" + "1" * 64)
        ledger.commit("files", owned, "sha256:" + "1" * 64)
        ledger.removed("files", owned, "sha256:" + "1" * 64)
        self.assertEqual(len(snapshots), 3)
        self.assertEqual(
            MutationLedger.from_bytes(snapshots[-1], allowed_objects={owned}).state(owned),
            "removed",
        )

        def fail(_payload: bytes) -> None:
            raise OSError("disk full")

        failed = MutationLedger(allowed_objects={owned}, persist=fail)
        with self.assertRaisesRegex(BackendError, "persist"):
            failed.intent("files", owned, "sha256:" + "1" * 64)
        self.assertIsNone(failed.state(owned))

    def test_durable_store_round_trips_atomic_private_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "mutation-ledger.json"
            store = DurableMutationLedgerStore(
                path,
                expected_uid=os.getuid() if hasattr(os, "getuid") else None,
            )
            owned = "file:/etc/amn2-spain/runtime.env"
            ledger = store.load_or_create({owned})
            ledger.intent("files", owned, "sha256:" + "1" * 64)
            restored = store.load_or_create({owned})
            self.assertEqual(restored.state(owned), "intent")
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)


class _FakeOwnedAdapter:
    def __init__(self) -> None:
        self.objects: dict[str, str] = {}
        self.calls: list[str] = []
        self.fail_before: str | None = None
        self.fail_after: str | None = None

    def observe(self, operation: OwnedOperation) -> str | None:
        return self.objects.get(operation.owned_object)

    def create(self, operation: OwnedOperation) -> None:
        self.calls.append("create:" + operation.owned_object)
        if self.fail_before == operation.owned_object:
            raise BackendError("fault before mutation")
        self.objects[operation.owned_object] = operation.desired_identity
        if self.fail_after == operation.owned_object:
            raise BackendError("fault after mutation")

    def remove(self, operation: OwnedOperation, identity: str) -> None:
        self.calls.append("remove:" + operation.owned_object)
        if self.objects.get(operation.owned_object) != identity:
            raise BackendError("adapter CAS drift")
        del self.objects[operation.owned_object]


def _operations() -> tuple[OwnedOperation, ...]:
    categories = (
        ("identity", "group:amn2-spain"),
        ("directories", "dir:/etc/amn2-spain"),
        ("files", "file:/etc/amn2-spain/runtime.env"),
        ("secrets", "secret:/etc/amn2-spain/awgsp0.conf"),
        ("database", "database:/var/lib/amn2-spain/amn2.sqlite3"),
        ("units", "unit:amn2-spain-docker.service"),
        ("image", "image:" + AWG_IMAGE_CONFIG_DIGEST),
        ("network", "network:amn2-spain-net"),
        ("container", "container:amn2-spain-awg"),
        ("services", "service:amn2-spain-web.service"),
    )
    return tuple(
        OwnedOperation(stage, owned, "sha256:" + f"{index:064x}")
        for index, (stage, owned) in enumerate(categories, start=1)
    )


class LinuxBackendReconcileTests(unittest.TestCase):
    def test_fault_before_and_after_every_mutation_is_reconcilable(self) -> None:
        for operation in _operations():
            with self.subTest(operation=operation.owned_object, fault="before"):
                adapter = _FakeOwnedAdapter()
                adapter.fail_before = operation.owned_object
                ledger = MutationLedger(allowed_objects={item.owned_object for item in _operations()})
                backend = LinuxBackend(adapter=adapter, ledger=ledger)
                with self.assertRaisesRegex(BackendError, "before"):
                    backend.apply(_operations())
                self.assertEqual(ledger.state(operation.owned_object), "intent")
                adapter.fail_before = None
                backend.apply(_operations())
                self.assertEqual(ledger.state(operation.owned_object), "committed")
            with self.subTest(operation=operation.owned_object, fault="after"):
                adapter = _FakeOwnedAdapter()
                adapter.fail_after = operation.owned_object
                ledger = MutationLedger(allowed_objects={item.owned_object for item in _operations()})
                backend = LinuxBackend(adapter=adapter, ledger=ledger)
                with self.assertRaisesRegex(BackendError, "after"):
                    backend.apply(_operations())
                calls_before = adapter.calls.count("create:" + operation.owned_object)
                adapter.fail_after = None
                backend.apply(_operations())
                self.assertEqual(
                    adapter.calls.count("create:" + operation.owned_object), calls_before
                )
                self.assertEqual(ledger.state(operation.owned_object), "committed")

    def test_rollback_reverse_closes_services_container_and_network_first(self) -> None:
        adapter = _FakeOwnedAdapter()
        operations = _operations()
        ledger = MutationLedger(allowed_objects={item.owned_object for item in operations})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)
        backend.apply(operations)
        backend.rollback(operations)
        removed = [value for value in adapter.calls if value.startswith("remove:")]
        self.assertEqual(
            removed[:3],
            [
                "remove:network:amn2-spain-net",
                "remove:service:amn2-spain-web.service",
                "remove:container:amn2-spain-awg",
            ],
        )
        backend.rollback(operations)
        self.assertEqual([value for value in adapter.calls if value.startswith("remove:")], removed)

    def test_composite_host_network_contour_is_rollback_ingress_first(self) -> None:
        operations = (
            OwnedOperation(
                "host_network_applied",
                "network-contour:amn2-spain",
                "sha256:" + "1" * 64,
            ),
            OwnedOperation(
                "web_started",
                "systemd-active:amn2-spain-web.service",
                "sha256:" + "2" * 64,
            ),
        )
        adapter = _FakeOwnedAdapter()
        ledger = MutationLedger(allowed_objects={item.owned_object for item in operations})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)
        backend.apply(operations)
        backend.rollback(operations)
        self.assertEqual(
            [value for value in adapter.calls if value.startswith("remove:")],
            [
                "remove:network-contour:amn2-spain",
                "remove:systemd-active:amn2-spain-web.service",
            ],
        )

    def test_rollback_rejects_object_drift_and_does_not_remove_pending_absent(self) -> None:
        adapter = _FakeOwnedAdapter()
        operations = _operations()
        ledger = MutationLedger(allowed_objects={item.owned_object for item in operations})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)
        first = operations[0]
        ledger.intent(first.stage, first.owned_object, first.desired_identity)
        backend.rollback(operations)
        self.assertIsNone(adapter.objects.get(first.owned_object))
        self.assertEqual(ledger.state(first.owned_object), "abandoned")
        restored = MutationLedger.from_bytes(
            ledger.to_bytes(),
            allowed_objects={item.owned_object for item in operations},
        )
        self.assertEqual(restored.state(first.owned_object), "abandoned")

        ledger2 = MutationLedger(allowed_objects={item.owned_object for item in operations})
        backend2 = LinuxBackend(adapter=adapter, ledger=ledger2)
        backend2.apply(operations)
        adapter.objects[operations[-1].owned_object] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(BackendError, "drift"):
            backend2.rollback(operations)


class SystemOwnedAdapterTests(unittest.TestCase):
    def test_safe_filesystem_actions_create_observe_and_cas_remove(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            (Path(raw) / "etc").mkdir()
            fs = SafeFs(
                root=Path(raw),
                expected_uid=os.getuid() if hasattr(os, "getuid") else None,
            )
            directory = build_directory_action(fs, "directories", "etc/amn2-spain", 0o700)
            runtime = build_file_action(
                fs,
                "files",
                "etc/amn2-spain/runtime.env",
                b"VPS_APPLY_ENABLED=false\n",
                0o600,
            )
            adapter = SystemOwnedAdapter(
                actions={
                    directory.operation.owned_object: directory,
                    runtime.operation.owned_object: runtime,
                }
            )
            operations = (directory.operation, runtime.operation)
            ledger = MutationLedger(allowed_objects={item.owned_object for item in operations})
            backend = LinuxBackend(adapter=adapter, ledger=ledger)
            backend.apply(operations)
            self.assertEqual(adapter.observe(runtime.operation), runtime.operation.desired_identity)
            backend.rollback(operations)
            self.assertFalse((Path(raw) / "etc" / "amn2-spain" / "runtime.env").exists())

    def test_adapter_rejects_unregistered_or_forged_operation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            fs = SafeFs(root=Path(raw), expected_uid=os.getuid() if hasattr(os, "getuid") else None)
            action = build_directory_action(fs, "directories", "etc/amn2-spain", 0o700)
            adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
            forged = OwnedOperation(
                action.operation.stage,
                action.operation.owned_object,
                "sha256:" + "f" * 64,
            )
            with self.assertRaisesRegex(BackendError, "sealed action"):
                adapter.observe(forged)
            missing = OwnedOperation("files", "file:/missing", "sha256:" + "1" * 64)
            with self.assertRaisesRegex(BackendError, "sealed action"):
                adapter.create(missing)


class LiveInputLoaderTests(unittest.TestCase):
    def test_reads_only_canonical_bounded_regular_private_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "authorization.json"
            payload = b'{"approved":true,"nonce":"abc"}\n'
            path.write_bytes(payload)
            if os.name != "nt":
                path.chmod(0o600)
            self.assertEqual(
                read_canonical_root_json(
                    path,
                    expected_keys={"approved", "nonce"},
                    expected_uid=os.getuid() if hasattr(os, "getuid") else None,
                ),
                {"approved": True, "nonce": "abc"},
            )
            path.write_bytes(b'{"nonce":"abc", "approved":true}\n')
            with self.assertRaisesRegex(BackendError, "canonical"):
                read_canonical_root_json(
                    path,
                    expected_keys={"approved", "nonce"},
                    expected_uid=os.getuid() if hasattr(os, "getuid") else None,
                )

    def test_rejects_symlink_wrong_mode_and_oversized_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            path = root / "input.json"
            path.write_bytes(b'{"ok":true}\n')
            if os.name != "nt":
                path.chmod(0o644)
                with self.assertRaisesRegex(BackendError, "owner/mode"):
                    read_canonical_root_json(path, expected_keys={"ok"})
                path.chmod(0o600)
            link = root / "link.json"
            try:
                link.symlink_to(path)
            except (OSError, NotImplementedError):
                pass
            else:
                with self.assertRaisesRegex(BackendError, "symlink"):
                    read_canonical_root_json(link, expected_keys={"ok"})
            path.write_bytes(b"{" + b"x" * (1024 * 1024) + b"}\n")
            with self.assertRaisesRegex(BackendError, "size"):
                read_canonical_root_json(path, expected_keys={"ok"})


class PosixIdentityActionTests(unittest.TestCase):
    def test_exact_group_user_create_observe_and_reverse_rollback(self) -> None:
        state: dict[str, dict[str, object]] = {}
        commands: list[tuple[str, ...]] = []

        def runner(argv: tuple[str, ...], **_kwargs: object) -> bytes:
            commands.append(argv)
            if argv[0].endswith("groupadd"):
                state["group"] = {"name": "amn2-spain", "gid": 61212}
            elif argv[0].endswith("useradd"):
                state["user"] = {
                    "name": "amn2-spain", "uid": 61212, "gid": 61212,
                    "home": "/var/lib/amn2-spain", "shell": "/usr/sbin/nologin",
                }
            elif argv[0].endswith("userdel"):
                state.pop("user", None)
            elif argv[0].endswith("groupdel"):
                state.pop("group", None)
            return b""

        actions = build_posix_identity_actions(
            runner=runner,
            group_lookup=lambda: state.get("group"),
            user_lookup=lambda: state.get("user"),
        )
        adapter = SystemOwnedAdapter(
            actions={action.operation.owned_object: action for action in actions}
        )
        operations = tuple(action.operation for action in actions)
        backend = LinuxBackend(
            adapter=adapter,
            ledger=MutationLedger(allowed_objects={op.owned_object for op in operations}),
        )
        backend.apply(operations)
        backend.rollback(operations)
        self.assertTrue(commands[0][0].endswith("groupadd"))
        self.assertTrue(commands[1][0].endswith("useradd"))
        self.assertTrue(commands[-2][0].endswith("userdel"))
        self.assertTrue(commands[-1][0].endswith("groupdel"))
        self.assertEqual(state, {})


class ProductionFixedIdentityTests(unittest.TestCase):
    def _observer(self, state: dict[str, dict[str, object]]) -> StructuredPosixIdentityObserver:
        return StructuredPosixIdentityObserver(
            group_by_name=lambda: state.get("group_name"),
            group_by_gid=lambda: state.get("group_gid"),
            user_by_name=lambda: state.get("user_name"),
            user_by_uid=lambda: state.get("user_uid"),
        )

    def test_two_physical_actions_bind_four_aliases_and_rollback_user_first(self) -> None:
        state: dict[str, dict[str, object]] = {}
        commands: list[tuple[str, ...]] = []

        def runner(argv: tuple[str, ...], **_kwargs: object) -> bytes:
            self.assertIn(argv, IDENTITY_COMMAND_ALLOWLIST)
            commands.append(argv)
            executable = Path(argv[0]).name
            if executable == "groupadd":
                record = {"name": "amn2-spain", "gid": 61212, "members": []}
                state["group_name"] = record
                state["group_gid"] = record
            elif executable == "useradd":
                record = {
                    "name": "amn2-spain", "uid": 61212, "gid": 61212,
                    "home": "/nonexistent", "shell": "/usr/sbin/nologin",
                    "supplementary_groups": [],
                }
                state["user_name"] = record
                state["user_uid"] = record
            elif executable == "userdel":
                state.pop("user_name", None)
                state.pop("user_uid", None)
            elif executable == "groupdel":
                state.pop("group_name", None)
                state.pop("group_gid", None)
            return b""

        bundle = build_fixed_identity_bundle(
            runner=runner, observer=self._observer(state)
        )
        self.assertEqual(len(bundle.actions), 2)
        self.assertEqual(
            set(bundle.logical_receipt),
            {"group:amn2-spain", "gid:61212", "user:amn2-spain", "uid:61212"},
        )
        self.assertEqual(
            bundle.logical_receipt["group:amn2-spain"],
            bundle.logical_receipt["gid:61212"],
        )
        self.assertEqual(
            bundle.logical_receipt["user:amn2-spain"],
            bundle.logical_receipt["uid:61212"],
        )
        operations = tuple(action.operation for action in bundle.actions)
        backend = LinuxBackend(
            adapter=SystemOwnedAdapter(
                actions={action.operation.owned_object: action for action in bundle.actions}
            ),
            ledger=MutationLedger(allowed_objects={op.owned_object for op in operations}),
        )
        backend.apply(operations)
        changed_user = dict(state["user_name"])
        changed_user["supplementary_groups"] = ["foreign-group"]
        state["user_name"] = changed_user
        state["user_uid"] = changed_user
        with self.assertRaisesRegex(BackendError, "collision"):
            backend.rollback(operations)
        self.assertNotIn("userdel", [Path(argv[0]).name for argv in commands])
        clean_user = dict(changed_user)
        clean_user["supplementary_groups"] = []
        state["user_name"] = clean_user
        state["user_uid"] = clean_user
        backend.rollback(operations)
        self.assertEqual(
            [Path(argv[0]).name for argv in commands],
            ["groupadd", "useradd", "userdel", "groupdel"],
        )
        self.assertEqual(state, {})

    def test_name_and_numeric_collisions_fail_both_directions(self) -> None:
        group_operation_index = 0
        for state in (
            {"group_name": {"name": "amn2-spain", "gid": 999, "members": []}},
            {"group_gid": {"name": "foreign", "gid": 61212, "members": []}},
            {"user_name": {
                "name": "amn2-spain", "uid": 61212, "gid": 999,
                "home": "/nonexistent", "shell": "/usr/sbin/nologin",
                "supplementary_groups": [],
            }},
            {"user_uid": {
                "name": "foreign", "uid": 61212, "gid": 61212,
                "home": "/nonexistent", "shell": "/usr/sbin/nologin",
                "supplementary_groups": [],
            }},
        ):
            with self.subTest(state=state):
                bundle = build_fixed_identity_bundle(
                    runner=lambda *_args, **_kwargs: b"",
                    observer=self._observer(state),
                )
                action = bundle.actions[
                    1 if "user_name" in state or "user_uid" in state else group_operation_index
                ]
                with self.assertRaisesRegex(BackendError, "collision"):
                    SystemOwnedAdapter(
                        actions={item.operation.owned_object: item for item in bundle.actions}
                    ).observe(action.operation)

    def test_pending_exact_group_is_adopted_without_repeating_groupadd(self) -> None:
        group = {"name": "amn2-spain", "gid": 61212, "members": []}
        state: dict[str, dict[str, object]] = {
            "group_name": group,
            "group_gid": group,
        }
        commands: list[tuple[str, ...]] = []

        def runner(argv: tuple[str, ...], **_kwargs: object) -> bytes:
            commands.append(argv)
            if Path(argv[0]).name == "useradd":
                user = {
                    "name": "amn2-spain", "uid": 61212, "gid": 61212,
                    "home": "/nonexistent", "shell": "/usr/sbin/nologin",
                    "supplementary_groups": [],
                }
                state["user_name"] = user
                state["user_uid"] = user
            return b""

        bundle = build_fixed_identity_bundle(runner=runner, observer=self._observer(state))
        operations = tuple(action.operation for action in bundle.actions)
        ledger = MutationLedger(allowed_objects={op.owned_object for op in operations})
        group_operation = operations[0]
        ledger.intent(
            group_operation.stage,
            group_operation.owned_object,
            group_operation.desired_identity,
        )
        LinuxBackend(
            adapter=SystemOwnedAdapter(
                actions={action.operation.owned_object: action for action in bundle.actions}
            ),
            ledger=ledger,
        ).apply(operations)
        self.assertNotIn("groupadd", [Path(argv[0]).name for argv in commands])
        self.assertIn("useradd", [Path(argv[0]).name for argv in commands])

    def test_group_members_and_user_supplementary_memberships_are_cas_bound(self) -> None:
        group = {"name": "amn2-spain", "gid": 61212, "members": []}
        user = {
            "name": "amn2-spain", "uid": 61212, "gid": 61212,
            "home": "/nonexistent", "shell": "/usr/sbin/nologin",
            "supplementary_groups": [],
        }
        state: dict[str, dict[str, object]] = {
            "group_name": group,
            "group_gid": group,
            "user_name": user,
            "user_uid": user,
        }
        bundle = build_fixed_identity_bundle(
            runner=lambda *_args, **_kwargs: b"", observer=self._observer(state)
        )
        adapter = SystemOwnedAdapter(
            actions={action.operation.owned_object: action for action in bundle.actions}
        )
        changed_group = {"name": "amn2-spain", "gid": 61212, "members": ["foreign"]}
        state["group_name"] = changed_group
        state["group_gid"] = changed_group
        with self.assertRaisesRegex(BackendError, "collision"):
            adapter.observe(bundle.actions[0].operation)
        state["group_name"] = group
        state["group_gid"] = group
        changed_user = dict(user)
        changed_user["supplementary_groups"] = ["foreign-group"]
        state["user_name"] = changed_user
        state["user_uid"] = changed_user
        with self.assertRaisesRegex(BackendError, "collision"):
            adapter.observe(bundle.actions[1].operation)


class CompositeNetworkActionTests(unittest.TestCase):
    def test_systemd_network_service_and_contour_are_one_physical_action(self) -> None:
        state = {"active": False, "ledger": None, "exact": False}
        active_identity = "sha256:" + "9" * 64

        class Controller:
            def read_ledger(self) -> dict[str, object] | None:
                return state["ledger"]

            def assert_absent(self) -> None:
                if state["exact"]:
                    raise BackendError("network contour collision")

            def is_exact(self, _ledger: dict[str, object]) -> bool:
                return bool(state["exact"])

            def apply(self) -> dict[str, object]:
                raise AssertionError("composite must mutate through systemd only")

            def rollback(self, _ledger: dict[str, object]) -> None:
                state["exact"] = False

            def remove_ledger(self, _ledger: dict[str, object]) -> None:
                state["ledger"] = None

        active_action = live_backend.SystemAction(
            operation=OwnedOperation(
                "host_network_applied",
                "systemd-active:amn2-spain-network.service",
                active_identity,
            ),
            observe_identity=lambda: active_identity if state["active"] else None,
            create_exact=lambda: state.update(
                active=True, ledger={"schema": "prepared-and-final"}, exact=True
            ),
            remove_exact=lambda identity: (
                (_ for _ in ()).throw(BackendError("systemd active CAS drift"))
                if identity != active_identity
                else state.update(active=False, ledger=None, exact=False)
            ),
        )
        action = live_backend.build_network_service_contour_action(
            systemd_active_action=active_action,
            controller=Controller(),
        )
        self.assertEqual(action.operation.stage, "host_network_applied")
        self.assertEqual(action.operation.owned_object, "network-contour:amn2-spain")
        adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
        ledger = MutationLedger(allowed_objects={action.operation.owned_object})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)

        backend.apply((action.operation,))
        self.assertTrue(state["active"])
        self.assertTrue(state["exact"])
        backend.rollback((action.operation,))
        self.assertEqual(state, {"active": False, "ledger": None, "exact": False})

    def test_partial_ledger_before_installer_intent_is_a_collision(self) -> None:
        class Controller:
            ledger: dict[str, object] | None = {"prepared": True}
            apply_calls = 0

            def read_ledger(self) -> dict[str, object] | None:
                return self.ledger

            def assert_absent(self) -> None:
                return None

            def is_exact(self, _ledger: dict[str, object]) -> bool:
                return False

            def apply(self) -> dict[str, object]:
                self.apply_calls += 1
                return {"prepared": True}

            def rollback(self, _ledger: dict[str, object]) -> None:
                return None

            def remove_ledger(self, _ledger: dict[str, object]) -> None:
                return None

        controller = Controller()
        action = build_network_contour_action(controller)
        adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
        ledger = MutationLedger(allowed_objects={action.operation.owned_object})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)

        with self.assertRaisesRegex(BackendError, "network contour collision"):
            backend.apply((action.operation,))
        self.assertEqual(controller.apply_calls, 0)
        self.assertIsNone(ledger.event_for(action.operation.owned_object))

    def test_one_physical_action_recovers_prepared_ledger_and_rolls_back_once(self) -> None:
        class Controller:
            ledger: dict[str, object] | None = None
            exact = False
            apply_calls = 0
            rollback_calls = 0

            def read_ledger(self) -> dict[str, object] | None:
                return self.ledger

            def assert_absent(self) -> None:
                if self.exact:
                    raise BackendError("network contour collision")

            def is_exact(self, _ledger: dict[str, object]) -> bool:
                return self.exact

            def apply(self) -> dict[str, object]:
                self.apply_calls += 1
                if self.ledger is None:
                    self.ledger = {"prepared": True}
                self.exact = True
                return self.ledger

            def rollback(self, _ledger: dict[str, object]) -> None:
                self.rollback_calls += 1
                self.exact = False

            def remove_ledger(self, _ledger: dict[str, object]) -> None:
                self.ledger = None

        controller = Controller()
        action = build_network_contour_action(controller)
        self.assertEqual(action.operation.owned_object, "network-contour:amn2-spain")
        self.assertEqual(action.operation.desired_identity, network_contour_identity())
        adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
        ledger = MutationLedger(allowed_objects={action.operation.owned_object})
        backend = LinuxBackend(adapter=adapter, ledger=ledger)
        backend.apply((action.operation,))
        self.assertEqual(controller.apply_calls, 1)
        backend.rollback((action.operation,))
        self.assertEqual(controller.rollback_calls, 1)
        self.assertIsNone(controller.ledger)


class ProductionInstallActionPlanTests(unittest.TestCase):
    @staticmethod
    def _action(stage: str, owned_object: str, digit: str) -> live_backend.SystemAction:
        identity = "sha256:" + digit * 64
        return live_backend.SystemAction(
            operation=OwnedOperation(stage, owned_object, identity),
            observe_identity=lambda: None,
            create_exact=lambda: None,
            remove_exact=lambda _identity: None,
        )

    def test_sealed_plan_replaces_network_service_active_with_composite_owner(self) -> None:
        identity = self._action("identity_created", "group:amn2-spain", "1")
        filesystem = self._action("filesystem_staged", "runtime:docker-static", "2")
        secrets = self._action("secrets_configs_rendered", "secret:app-runtime", "3")
        database = self._action("clean_db_initialized", "database:/var/lib/amn2-spain/amn2.sqlite3", "4")
        unit = self._action("units_installed", "file:/etc/systemd/system/amn2-spain-network.service", "5")
        docker_active = self._action("docker_started", "systemd-active:amn2-spain-docker.service", "6")
        image = self._action("awg_image_loaded", "image:awg", "7")
        container = self._action("network_container_started", "container:amn2-spain-awg", "8")
        network_enabled = self._action("host_network_applied", "systemd-enabled:amn2-spain-network.service", "9")
        network_active = self._action("host_network_applied", "systemd-active:amn2-spain-network.service", "a")
        composite = self._action("host_network_applied", "network-contour:amn2-spain", "b")
        web_active = self._action("web_started", "systemd-active:amn2-spain-web.service", "c")

        plan = live_backend.compose_production_install_actions(
            identity_actions=(identity,),
            filesystem_actions=(filesystem, secrets),
            database_action=database,
            systemd_actions=(unit, docker_active, network_enabled, network_active, web_active),
            docker_actions=(image, container),
            network_service_contour_action=composite,
        )

        self.assertNotIn(network_active.operation, plan.operations)
        self.assertIn(composite.operation, plan.operations)
        self.assertEqual(
            tuple(plan.operations_by_stage),
            live_backend.PRODUCTION_INSTALL_MUTATING_STAGES,
        )
        flattened = tuple(
            operation
            for stage in live_backend.PRODUCTION_INSTALL_MUTATING_STAGES
            for operation in plan.operations_by_stage[stage]
        )
        self.assertEqual(flattened, plan.operations)
        self.assertLess(plan.operations.index(network_enabled.operation), plan.operations.index(composite.operation))
        self.assertEqual(
            set(plan.actions),
            {
                identity, filesystem, secrets, database, unit, docker_active,
                image, container, network_enabled, composite, web_active,
            },
        )


class SystemdActionTests(unittest.TestCase):
    def test_enable_and_active_are_separate_reconcilable_actions(self) -> None:
        state = {"UnitFileState": "disabled", "ActiveState": "inactive"}
        calls: list[tuple[str, ...]] = []

        def runner(argv: tuple[str, ...], **_kwargs: object) -> bytes:
            calls.append(argv)
            verb = argv[1]
            if verb == "enable": state["UnitFileState"] = "enabled"
            elif verb == "disable": state["UnitFileState"] = "disabled"
            elif verb == "start": state["ActiveState"] = "active"
            elif verb == "stop": state["ActiveState"] = "inactive"
            return b""

        actions = build_systemd_unit_actions(
            unit="amn2-spain-web.service",
            stage="web",
            runner=runner,
            lookup=lambda: dict(state),
            start_active=True,
        )
        operations = tuple(action.operation for action in actions)
        backend = LinuxBackend(
            adapter=SystemOwnedAdapter(
                actions={action.operation.owned_object: action for action in actions}
            ),
            ledger=MutationLedger(allowed_objects={op.owned_object for op in operations}),
        )
        backend.apply(operations)
        self.assertEqual(state, {"UnitFileState": "enabled", "ActiveState": "active"})
        backend.rollback(operations)
        self.assertEqual(state, {"UnitFileState": "disabled", "ActiveState": "inactive"})
        self.assertEqual(
            [call[1] for call in calls],
            ["daemon-reload", "enable", "start", "stop", "disable"],
        )


class ProductionSystemdLayerTests(unittest.TestCase):
    class FakeSystemd:
        def __init__(self, root: Path) -> None:
            self.root = root
            self.calls: list[tuple[str, ...]] = []
            self.states = {
                unit: {
                    "LoadState": "not-found",
                    "FragmentPath": "",
                    "UnitFileState": "",
                    "ActiveState": "inactive",
                }
                for unit in live_backend.SYSTEMD_UNITS
            }

        def runner(self, argv: tuple[str, ...], **_kwargs: object) -> bytes:
            if argv not in live_backend.SYSTEMCTL_COMMAND_ALLOWLIST:
                raise AssertionError("non-allowlisted systemctl argv")
            self.calls.append(argv)
            verb = argv[1]
            if verb == "show":
                unit = argv[2]
                state = self.states[unit]
                return "".join(
                    f"{key}={state[key]}\n"
                    for key in ("ActiveState", "FragmentPath", "LoadState", "UnitFileState")
                ).encode("ascii")
            if verb == "daemon-reload":
                for unit, state in self.states.items():
                    target = self.root / "etc/systemd/system" / unit
                    if target.is_file() and not target.is_symlink():
                        state["LoadState"] = "loaded"
                        state["FragmentPath"] = "/etc/systemd/system/" + unit
                        if not state["UnitFileState"]:
                            state["UnitFileState"] = (
                                "static" if unit == "amn2-spain-bot.service" else "disabled"
                            )
                    else:
                        state.update(
                            {
                                "LoadState": "not-found",
                                "FragmentPath": "",
                                "UnitFileState": "",
                                "ActiveState": "inactive",
                            }
                        )
                return b""
            unit = argv[2]
            state = self.states[unit]
            if verb == "enable":
                state["UnitFileState"] = "enabled"
            elif verb == "disable":
                state["UnitFileState"] = "disabled"
            elif verb == "start":
                state["ActiveState"] = "active"
            elif verb == "stop":
                state["ActiveState"] = "inactive"
            else:
                raise AssertionError("unexpected systemctl verb")
            return b""

    @staticmethod
    def _root(root: Path) -> None:
        (root / "etc/systemd/system").mkdir(parents=True)

    @staticmethod
    def _ids() -> tuple[int | None, int | None]:
        return (
            (None, None)
            if os.name == "nt"
            else (os.getuid(), os.getgid())
        )

    def _bundle(self, root: Path, fake: "ProductionSystemdLayerTests.FakeSystemd") -> object:
        uid, gid = self._ids()
        return live_backend.build_production_systemd_bundle(
            root=root,
            runner=fake.runner,
            root_uid=uid,
            root_gid=gid,
        )

    def test_exact_unit_files_desired_states_and_owned_reverse_rollback(self) -> None:
        self.assertTrue(
            hasattr(live_backend, "build_production_systemd_bundle"),
            "production systemd bundle API missing",
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            fake = self.FakeSystemd(root)
            bundle = self._bundle(root, fake)
            operations = tuple(action.operation for action in bundle.actions)
            self.assertEqual(
                [operation.stage for operation in operations],
                ["units_installed"] * 4
                + ["docker_started"] * 2
                + ["host_network_applied"] * 2
                + ["web_started"] * 2,
            )
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action for action in bundle.actions}
                ),
                ledger=MutationLedger(
                    allowed_objects={operation.owned_object for operation in operations}
                ),
            )
            backend.apply(operations)
            for unit in live_backend.SYSTEMD_UNIT_ORDER:
                installed = root / "etc/systemd/system" / unit
                package = ROOT / "packaging/phase12-spain/units" / unit
                self.assertEqual(installed.read_bytes(), package.read_bytes())
                if os.name != "nt":
                    info = os.lstat(installed)
                    self.assertEqual((info.st_uid, info.st_gid), self._ids())
                    self.assertEqual(stat.S_IMODE(info.st_mode), 0o644)
            for unit in (
                "amn2-spain-docker.service",
                "amn2-spain-network.service",
                "amn2-spain-web.service",
            ):
                self.assertEqual(fake.states[unit]["UnitFileState"], "enabled")
                self.assertEqual(fake.states[unit]["ActiveState"], "active")
            self.assertEqual(
                fake.states["amn2-spain-bot.service"]["UnitFileState"], "static"
            )
            self.assertEqual(
                fake.states["amn2-spain-bot.service"]["ActiveState"], "inactive"
            )
            self.assertFalse(
                any(
                    len(argv) > 2
                    and argv[2] == "amn2-spain-bot.service"
                    and argv[1] in {"enable", "start"}
                    for argv in fake.calls
                )
            )
            self.assertTrue(all(argv in live_backend.SYSTEMCTL_COMMAND_ALLOWLIST for argv in fake.calls))
            self.assertFalse(any("foreign" in part for argv in fake.calls for part in argv))
            safe = repr(bundle) + json.dumps(dict(bundle.logical_receipt), sort_keys=True)
            self.assertNotIn("EnvironmentFile", safe)

            backend.rollback(operations)
            for unit in live_backend.SYSTEMD_UNIT_ORDER:
                self.assertFalse((root / "etc/systemd/system" / unit).exists())
                self.assertEqual(fake.states[unit]["LoadState"], "not-found")
            service_commands = [
                (argv[1], argv[2]) for argv in fake.calls if argv[1] in {"start", "stop", "enable", "disable"}
            ]
            self.assertEqual(
                service_commands[-6:],
                [
                    ("stop", "amn2-spain-web.service"),
                    ("disable", "amn2-spain-web.service"),
                    ("stop", "amn2-spain-network.service"),
                    ("disable", "amn2-spain-network.service"),
                    ("stop", "amn2-spain-docker.service"),
                    ("disable", "amn2-spain-docker.service"),
                ],
            )
            self.assertEqual(
                [argv[1] for argv in fake.calls if argv[1] != "show"][-1],
                "daemon-reload",
            )

    def test_pending_exact_unit_file_reloads_without_rewrite_then_adopts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            fake = self.FakeSystemd(root)
            bundle = self._bundle(root, fake)
            action = bundle.actions[0]
            operation = action.operation
            target = root / operation.owned_object.removeprefix("file:/")
            unit = target.name
            target.write_bytes((ROOT / "packaging/phase12-spain/units" / unit).read_bytes())
            if os.name != "nt":
                target.chmod(0o644)
            before = os.lstat(target)
            ledger = MutationLedger(allowed_objects={operation.owned_object})
            ledger.intent(operation.stage, operation.owned_object, operation.desired_identity)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(actions={operation.owned_object: action}),
                ledger=ledger,
            )
            backend.apply((operation,))
            after = os.lstat(target)
            self.assertEqual((before.st_ino, before.st_size, before.st_mtime_ns), (after.st_ino, after.st_size, after.st_mtime_ns))
            self.assertEqual(ledger.state(operation.owned_object), "committed")
            self.assertIn(("/usr/bin/systemctl", "daemon-reload"), fake.calls)
            target.unlink()
            backend.rollback((operation,))
            self.assertFalse(target.exists())
            self.assertEqual(ledger.state(operation.owned_object), "removed")
            self.assertEqual(fake.states[unit]["LoadState"], "not-found")
            self.assertEqual(
                [argv[1] for argv in fake.calls if argv[1] != "show"][-1],
                "daemon-reload",
            )

    def test_missing_file_with_stale_loaded_manager_state_is_preintent_collision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            fake = self.FakeSystemd(root)
            unit = live_backend.SYSTEMD_UNIT_ORDER[0]
            fake.states[unit].update(
                {
                    "LoadState": "loaded",
                    "FragmentPath": "/etc/systemd/system/" + unit,
                    "UnitFileState": "disabled",
                    "ActiveState": "inactive",
                }
            )
            action = self._bundle(root, fake).actions[0]
            ledger = MutationLedger(allowed_objects={action.operation.owned_object})
            with self.assertRaisesRegex(BackendError, "manager|collision|drift"):
                LinuxBackend(
                    adapter=SystemOwnedAdapter(
                        actions={action.operation.owned_object: action}
                    ),
                    ledger=ledger,
                ).apply((action.operation,))
            self.assertIsNone(ledger.event_for(action.operation.owned_object))
            self.assertFalse((root / "etc/systemd/system" / unit).exists())
            self.assertNotIn(
                ("/usr/bin/systemctl", "daemon-reload"), fake.calls
            )

    def test_bot_drift_and_malformed_show_fail_closed_without_secret_or_bot_commands(self) -> None:
        secret = "secret-bearing-show-value"
        for payload in (
            (b"x" * (live_backend.MAX_SYSTEMCTL_SHOW_BYTES + 1)),
            (f"LoadState=loaded\nFragmentPath=/etc/systemd/system/amn2-spain-web.service\nUnitFileState=enabled\nActiveState={secret}\n").encode("ascii"),
        ):
            with self.subTest(size=len(payload)):
                with self.assertRaises(BackendError) as caught:
                    live_backend.parse_systemctl_show(
                        payload, unit="amn2-spain-web.service"
                    )
                self.assertNotIn(secret, str(caught.exception))

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            uid, gid = self._ids()
            leaking = live_backend.build_production_systemd_bundle(
                root=root,
                runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(
                    BackendError(secret)
                ),
                root_uid=uid,
                root_gid=gid,
            )
            first = leaking.actions[0]
            with self.assertRaises(BackendError) as caught:
                LinuxBackend(
                    adapter=SystemOwnedAdapter(
                        actions={first.operation.owned_object: first}
                    ),
                    ledger=MutationLedger(
                        allowed_objects={first.operation.owned_object}
                    ),
                ).apply((first.operation,))
            self.assertNotIn(secret, str(caught.exception))

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            (root / "etc/amn2-spain").mkdir()
            fake = self.FakeSystemd(root)
            bundle = self._bundle(root, fake)
            (root / "etc/amn2-spain/bot-enabled").write_bytes(b"")
            bot = bundle.actions[3]
            with self.assertRaisesRegex(BackendError, "bot enable marker"):
                LinuxBackend(
                    adapter=SystemOwnedAdapter(
                        actions={bot.operation.owned_object: bot}
                    ),
                    ledger=MutationLedger(
                        allowed_objects={bot.operation.owned_object}
                    ),
                ).apply((bot.operation,))
            self.assertFalse(
                any(
                    len(argv) > 2
                    and argv[2] == "amn2-spain-bot.service"
                    and argv[1] in {"enable", "start"}
                    for argv in fake.calls
                )
            )

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._root(root)
            fake = self.FakeSystemd(root)
            bundle = self._bundle(root, fake)
            unit_actions = bundle.actions[:4]
            operations = tuple(action.operation for action in unit_actions)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action for action in unit_actions}
                ),
                ledger=MutationLedger(
                    allowed_objects={operation.owned_object for operation in operations}
                ),
            )
            backend.apply(operations)
            fake.states["amn2-spain-bot.service"]["ActiveState"] = "active"
            with self.assertRaisesRegex(BackendError, "bot|state|drift"):
                backend.rollback(operations)
            self.assertFalse(
                any(
                    len(argv) > 2
                    and argv[2] == "amn2-spain-bot.service"
                    and argv[1] in {"stop", "disable"}
                    for argv in fake.calls
                )
            )


class CanonicalTreeActionTests(unittest.TestCase):
    @staticmethod
    def _source_archive(commit: str, body: bytes) -> bytes:
        stream = io.BytesIO()
        with tarfile.open(
            fileobj=stream,
            mode="w",
            format=tarfile.PAX_FORMAT,
            pax_headers={"comment": commit},
        ) as archive:
            directory = tarfile.TarInfo("source")
            directory.type = tarfile.DIRTYPE
            directory.mode = 0o755
            archive.addfile(directory)
            member = tarfile.TarInfo("source/app.py")
            member.size = len(body)
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(body))
        return stream.getvalue()

    @staticmethod
    def _wheel(body: bytes) -> bytes:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as wheel:
            wheel.writestr("demo.py", body)
            wheel.writestr(
                "demo-1.0.dist-info/METADATA",
                "Metadata-Version: 2.1\nName: demo\nVersion: 1.0\n",
            )
        return stream.getvalue()

    def test_source_pending_partial_is_reconciled_but_preintent_partial_collides(self) -> None:
        commit = "1" * 40
        body = b"print('phase12')\n"
        archive_body = self._source_archive(commit, body)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive = root / "source.tar"
            archive.write_bytes(archive_body)
            target = root / "runtime" / "source"
            target.parent.mkdir()
            action = build_source_tree_action(
                archive_path=archive,
                target_dir=target,
                expected_sha256=hashlib.sha256(archive_body).hexdigest(),
                expected_size=len(archive_body),
                expected_commit=commit,
                stage="filesystem_staged",
            )
            adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
            ledger = MutationLedger(allowed_objects={action.operation.owned_object})
            ledger.intent(
                action.operation.stage,
                action.operation.owned_object,
                action.operation.desired_identity,
            )
            target.mkdir()
            (target / "partial").write_bytes(b"crash")
            backend = LinuxBackend(adapter=adapter, ledger=ledger)
            backend.apply((action.operation,))
            self.assertEqual((target / "app.py").read_bytes(), body)
            self.assertFalse((target / "partial").exists())
            (target / "app.py").write_bytes(b"drift\n")
            with self.assertRaisesRegex(BackendError, "drift"):
                backend.rollback((action.operation,))
            (target / "app.py").write_bytes(body)
            backend.rollback((action.operation,))
            self.assertFalse(target.exists())

            target.mkdir()
            (target / "foreign").write_bytes(b"collision")
            fresh = LinuxBackend(
                adapter=adapter,
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            with self.assertRaisesRegex(BackendError, "collision"):
                fresh.apply((action.operation,))

    def test_deferred_trees_seal_identity_before_future_parent_exists(self) -> None:
        commit = "2" * 40
        source_body = self._source_archive(commit, b"VALUE = 'source'\n")
        wheel_body = self._wheel(b"VALUE = 'wheel'\n")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source_archive = root / "source.tar"
            source_archive.write_bytes(source_body)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            wheel_name = "demo-1.0-py3-none-any.whl"
            (wheelhouse / wheel_name).write_bytes(wheel_body)
            inventory_path = wheelhouse / "wheelhouse-inventory.json"
            inventory_path.write_text(
                json.dumps(
                    {
                        "schema": "amn2.spain-wheelhouse.v1",
                        "target": {
                            "architecture": "x86_64",
                            "python_major_minor": "3.12",
                        },
                        "wheels": [
                            {
                                "filename": wheel_name,
                                "sha256": hashlib.sha256(wheel_body).hexdigest(),
                                "size": len(wheel_body),
                            }
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="ascii",
            )
            runtime = root / "future" / "runtime"
            source = build_deferred_source_tree_action(
                archive_path=source_archive,
                target_dir=runtime / "source",
                expected_sha256=hashlib.sha256(source_body).hexdigest(),
                expected_size=len(source_body),
                expected_commit=commit,
                stage="filesystem_staged",
            )
            wheel = build_deferred_wheel_tree_action(
                wheelhouse_dir=wheelhouse,
                inventory_path=inventory_path,
                target_dir=runtime / "site-packages",
                stage="filesystem_staged",
            )
            self.assertTrue(source.operation.desired_identity.startswith("sha256:"))
            self.assertTrue(wheel.operation.desired_identity.startswith("sha256:"))
            runtime.mkdir(parents=True)
            actions = (source, wheel)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action for action in actions}
                ),
                ledger=MutationLedger(
                    allowed_objects={action.operation.owned_object for action in actions}
                ),
            )
            backend.apply(action.operation for action in actions)
            self.assertTrue((runtime / "source" / "app.py").is_file())
            self.assertTrue((runtime / "site-packages" / "demo.py").is_file())

    def test_wheel_tree_is_planned_before_mutation_and_cas_removed(self) -> None:
        wheel_body = self._wheel(b"VALUE = 12\n")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            filename = "demo-1.0-py3-none-any.whl"
            (wheelhouse / filename).write_bytes(wheel_body)
            inventory = {
                "schema": "amn2.spain-wheelhouse.v1",
                "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
                "wheels": [{
                    "filename": filename,
                    "sha256": hashlib.sha256(wheel_body).hexdigest(),
                    "size": len(wheel_body),
                }],
            }
            inventory_path = wheelhouse / "wheelhouse-inventory.json"
            inventory_path.write_text(
                json.dumps(inventory, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            target = root / "runtime" / "site-packages"
            target.parent.mkdir()
            action = build_wheel_tree_action(
                wheelhouse_dir=wheelhouse,
                inventory_path=inventory_path,
                target_dir=target,
                stage="filesystem_staged",
            )
            adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
            backend = LinuxBackend(
                adapter=adapter,
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            backend.apply((action.operation,))
            self.assertEqual((target / "demo.py").read_bytes(), b"VALUE = 12\n")
            backend.rollback((action.operation,))
            self.assertFalse(target.exists())

    def test_wheel_explicit_directory_after_member_is_not_a_false_duplicate(self) -> None:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as wheel:
            wheel.writestr("namespace/mod.py", b"VALUE = 1\n")
            directory = zipfile.ZipInfo("namespace/")
            directory.create_system = 3
            directory.external_attr = (stat.S_IFDIR | 0o755) << 16
            wheel.writestr(directory, b"")
        wheel_body = stream.getvalue()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            filename = "demo-1.0-py3-none-any.whl"
            (wheelhouse / filename).write_bytes(wheel_body)
            inventory = {
                "schema": "amn2.spain-wheelhouse.v1",
                "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
                "wheels": [{
                    "filename": filename,
                    "sha256": hashlib.sha256(wheel_body).hexdigest(),
                    "size": len(wheel_body),
                }],
            }
            inventory_path = wheelhouse / "wheelhouse-inventory.json"
            inventory_path.write_text(
                json.dumps(inventory, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            target = root / "site-packages"
            action = build_wheel_tree_action(
                wheelhouse_dir=wheelhouse,
                inventory_path=inventory_path,
                target_dir=target,
                stage="filesystem_staged",
            )
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action}
                ),
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            backend.apply((action.operation,))
            self.assertEqual((target / "namespace" / "mod.py").read_bytes(), b"VALUE = 1\n")

    def test_wheelhouse_rejects_unexpected_top_level_directory(self) -> None:
        wheel_body = self._wheel(b"VALUE = 12\n")
        with tempfile.TemporaryDirectory() as raw:
            wheelhouse = Path(raw) / "wheelhouse"
            wheelhouse.mkdir()
            filename = "demo-1.0-py3-none-any.whl"
            (wheelhouse / filename).write_bytes(wheel_body)
            (wheelhouse / "unexpected-directory").mkdir()
            inventory = {
                "schema": "amn2.spain-wheelhouse.v1",
                "target": {"architecture": "x86_64", "python_major_minor": "3.12"},
                "wheels": [{
                    "filename": filename,
                    "sha256": hashlib.sha256(wheel_body).hexdigest(),
                    "size": len(wheel_body),
                }],
            }
            inventory_path = wheelhouse / "wheelhouse-inventory.json"
            inventory_path.write_text(
                json.dumps(inventory, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(BackendError, "regular file"):
                build_wheel_tree_action(
                    wheelhouse_dir=wheelhouse,
                    inventory_path=inventory_path,
                    target_dir=Path(raw) / "site-packages",
                    stage="filesystem_staged",
                )

    @unittest.skipIf(os.name == "nt", "POSIX trusted-root traversal")
    def test_tree_target_rejects_symlinked_ancestor(self) -> None:
        commit = "1" * 40
        archive_body = self._source_archive(commit, b"print('safe')\n")
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside:
            root = Path(raw)
            archive = root / "source.tar"
            archive.write_bytes(archive_body)
            (root / "trusted").mkdir()
            (root / "trusted" / "redirect").symlink_to(
                Path(outside), target_is_directory=True
            )
            with self.assertRaisesRegex(BackendError, "ancestor"):
                build_source_tree_action(
                    archive_path=archive,
                    target_dir=root / "trusted" / "redirect" / "runtime" / "source",
                    expected_sha256=hashlib.sha256(archive_body).hexdigest(),
                    expected_size=len(archive_body),
                    expected_commit=commit,
                    stage="filesystem_staged",
                )


class ExactRuntimeContractTests(unittest.TestCase):
    @staticmethod
    def _static_docker_archive(
        variant: str = "",
    ) -> tuple[bytes, dict[str, bytes]]:
        payloads: dict[str, bytes] = {}
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            directory = tarfile.TarInfo("docker")
            directory.type = tarfile.DIRTYPE
            directory.mode = 0o755
            archive.addfile(directory)
            for index, relative in enumerate(STATIC_DOCKER_RELATIVE_PATHS):
                name = PurePosixPath(relative).name
                body = (
                    b"not-an-elf"
                    if variant == "nonelf" and index == 0
                    else b"\x7fELF\x02\x01\x01"
                    + b"\x00" * 11
                    + b"\x3e\x00"
                    + name.encode("ascii")
                )
                payloads[name] = body
                member_name = (
                    "wrong/" + name
                    if variant == "wrong_top" and index == 0
                    else "docker/" + name
                )
                member = tarfile.TarInfo(member_name)
                member.mode = 0o644 if variant == "wrong_mode" and index == 0 else 0o755
                if variant in {"symlink", "hardlink", "special"} and index == 0:
                    member.type = {
                        "symlink": tarfile.SYMTYPE,
                        "hardlink": tarfile.LNKTYPE,
                        "special": tarfile.FIFOTYPE,
                    }[variant]
                    member.linkname = "docker/runc"
                    archive.addfile(member)
                else:
                    member.size = len(body)
                    archive.addfile(member, io.BytesIO(body))
                if variant == "duplicate" and index == 0:
                    duplicate = tarfile.TarInfo(member_name)
                    duplicate.mode = 0o755
                    duplicate.size = len(body)
                    archive.addfile(duplicate, io.BytesIO(body))
            if variant == "extra":
                extra = tarfile.TarInfo("docker/foreign")
                extra.mode = 0o755
                extra.size = 20
                archive.addfile(extra, io.BytesIO(b"x" * 20))
        return output.getvalue(), payloads

    def test_static_docker_action_streams_exact_eight_0755_binaries_and_rolls_back(self) -> None:
        archive_body, payloads = self._static_docker_archive()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "opt" / "amn2-spain").mkdir(parents=True)
            archive_path = root / "docker.tgz"
            archive_path.write_bytes(archive_body)
            fs = SafeFs(root=root)
            with patch.object(Path, "read_bytes", side_effect=AssertionError("read-all forbidden")):
                action = live_backend.build_static_docker_action(
                    fs=fs,
                    archive_path=archive_path,
                    expected_sha256=hashlib.sha256(archive_body).hexdigest(),
                    expected_size=len(archive_body),
                )
            self.assertEqual(action.operation.owned_object, "runtime:docker-static")
            self.assertIsNone(action.observe_identity())
            action.create_exact()
            self.assertEqual(action.observe_identity(), action.operation.desired_identity)
            target = root / "opt" / "amn2-spain" / "docker" / "bin"
            self.assertEqual({entry.name for entry in target.iterdir()}, set(payloads))
            if os.name != "nt":
                for entry in target.iterdir():
                    self.assertEqual(stat.S_IMODE(entry.stat().st_mode), 0o755)
            (target / sorted(payloads)[0]).unlink()
            self.assertEqual(
                action.observe_rollback_identity(),
                action.operation.desired_identity,
            )
            action.remove_exact(action.operation.desired_identity)
            self.assertFalse((root / "opt" / "amn2-spain" / "docker").exists())
            target.mkdir(parents=True)
            first = sorted(payloads)[0]
            (target / first).write_bytes(payloads[first])
            os.chmod(target / first, 0o755)
            ledger = MutationLedger(
                allowed_objects={action.operation.owned_object}
            )
            ledger.intent(
                action.operation.stage,
                action.operation.owned_object,
                action.operation.desired_identity,
            )
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action}
                ),
                ledger=ledger,
            )
            backend.rollback((action.operation,))
            self.assertFalse((root / "opt" / "amn2-spain" / "docker").exists())
            self.assertEqual(ledger.state(action.operation.owned_object), "removed")

    def test_static_docker_action_reconciles_only_exact_partial_pending_tree(self) -> None:
        archive_body, payloads = self._static_docker_archive()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "opt" / "amn2-spain" / "docker" / "bin"
            target.mkdir(parents=True)
            archive_path = root / "docker.tgz"
            archive_path.write_bytes(archive_body)
            fs = SafeFs(root=root)
            action = live_backend.build_static_docker_action(
                fs=fs,
                archive_path=archive_path,
                expected_sha256=hashlib.sha256(archive_body).hexdigest(),
                expected_size=len(archive_body),
            )
            first = sorted(payloads)[0]
            (target / first).write_bytes(payloads[first])
            os.chmod(target / first, 0o755)
            self.assertIsNone(action.observe_pending_identity())
            action.create_exact()
            self.assertEqual(action.observe_identity(), action.operation.desired_identity)
            (target / "foreign").write_bytes(b"foreign")
            with self.assertRaisesRegex(BackendError, "drift"):
                action.observe_pending_identity()

    def test_static_docker_archive_rejects_every_non_exact_member_variant(self) -> None:
        for variant in (
            "extra", "duplicate", "symlink", "hardlink", "special",
            "wrong_mode", "nonelf", "wrong_top",
        ):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as raw:
                body, _payloads = self._static_docker_archive(variant)
                root = Path(raw)
                (root / "opt" / "amn2-spain").mkdir(parents=True)
                archive = root / "docker.tgz"
                archive.write_bytes(body)
                with self.assertRaisesRegex(BackendError, "static Docker"):
                    live_backend.build_static_docker_action(
                        fs=SafeFs(root=root),
                        archive_path=archive,
                        expected_sha256=hashlib.sha256(body).hexdigest(),
                        expected_size=len(body),
                    )

    def test_static_docker_create_rechecks_archive_hash_size_before_any_write(self) -> None:
        body, _payloads = self._static_docker_archive()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "opt" / "amn2-spain").mkdir(parents=True)
            archive = root / "docker.tgz"
            archive.write_bytes(body)
            action = live_backend.build_static_docker_action(
                fs=SafeFs(root=root),
                archive_path=archive,
                expected_sha256=hashlib.sha256(body).hexdigest(),
                expected_size=len(body),
            )
            archive.write_bytes(body + b"changed")
            with self.assertRaisesRegex(BackendError, "size"):
                action.create_exact()
            self.assertFalse((root / "opt" / "amn2-spain" / "docker").exists())

    def test_static_docker_rejects_symlink_archive_and_symlinked_target_ancestor(self) -> None:
        body, _payloads = self._static_docker_archive()
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as outside_raw:
            root = Path(raw)
            outside = Path(outside_raw)
            real_archive = root / "docker-real.tgz"
            real_archive.write_bytes(body)
            archive_link = root / "docker-link.tgz"
            try:
                archive_link.symlink_to(real_archive)
                (root / "opt").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(BackendError, "symlink"):
                live_backend.build_static_docker_action(
                    fs=SafeFs(root=root),
                    archive_path=archive_link,
                    expected_sha256=hashlib.sha256(body).hexdigest(),
                    expected_size=len(body),
                )
            action = live_backend.build_static_docker_action(
                fs=SafeFs(root=root),
                archive_path=real_archive,
                expected_sha256=hashlib.sha256(body).hexdigest(),
                expected_size=len(body),
            )
            with self.assertRaisesRegex(BackendError, "symlink"):
                action.observe_pending_identity()

    def test_static_docker_paths_and_loaded_image_config_are_exact(self) -> None:
        self.assertEqual(
            STATIC_DOCKER_RELATIVE_PATHS,
            (
                "opt/amn2-spain/docker/bin/containerd",
                "opt/amn2-spain/docker/bin/containerd-shim-runc-v2",
                "opt/amn2-spain/docker/bin/ctr",
                "opt/amn2-spain/docker/bin/docker",
                "opt/amn2-spain/docker/bin/docker-init",
                "opt/amn2-spain/docker/bin/docker-proxy",
                "opt/amn2-spain/docker/bin/dockerd",
                "opt/amn2-spain/docker/bin/runc",
            ),
        )
        observation = {
            "Id": AWG_IMAGE_CONFIG_DIGEST,
            "Architecture": "amd64",
            "Os": "linux",
            "RepoTags": ["amn2-spain-awg:phase12"],
        }
        self.assertEqual(verify_loaded_awg_image(observation), AWG_IMAGE_CONFIG_DIGEST)
        changed = dict(observation)
        changed["Id"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(BackendError, "image"):
            verify_loaded_awg_image(changed)

    def test_docker_daemon_is_dedicated_and_disables_automatic_network_mutation(self) -> None:
        daemon = json.loads((TEMPLATES / "docker-daemon.json").read_text(encoding="utf-8"))
        self.assertEqual(daemon["hosts"], ["unix:///run/amn2-spain-docker/docker.sock"])
        self.assertEqual(daemon["data-root"], "/var/lib/amn2-spain-docker")
        self.assertEqual(daemon["exec-root"], "/run/amn2-spain-docker/exec")
        self.assertEqual(daemon["pidfile"], "/run/amn2-spain-docker/docker.pid")
        for key in ("iptables", "ip6tables", "ip-forward", "ip-masq", "userland-proxy"):
            self.assertIs(daemon[key], False)
        self.assertEqual(daemon["bridge"], "none")

    def test_awg_pid1_and_container_contract_have_no_peer_or_restart_side_effect(self) -> None:
        start = (TEMPLATES / "awg-start.sh").read_text(encoding="utf-8")
        self.assertIn("awg-quick up awgsp0", start)
        self.assertIn("awg show awgsp0 peers", start)
        self.assertIn("trap", start)
        self.assertIn("trap shutdown INT TERM", start)
        self.assertIn("exit 0", start)
        self.assertIn("awg-quick down awgsp0", start)
        self.assertNotIn("docker restart", start)
        argv = build_container_create_argv()
        joined = " ".join(argv)
        self.assertIn("--read-only", argv)
        self.assertIn("--cap-drop ALL", joined)
        self.assertIn("--cap-add NET_ADMIN", joined)
        self.assertIn("--device /dev/net/tun", joined)
        self.assertIn("--tmpfs /run:rw,noexec,nosuid,nodev,size=16m", joined)
        self.assertIn("--restart unless-stopped", joined)
        self.assertIn("--ip 172.29.251.2", joined)
        self.assertEqual(argv[-1], AWG_LOCAL_IMAGE_TAG)
        self.assertNotEqual(argv[-1], AWG_IMAGE_REFERENCE)
        self.assertEqual(
            AWG_IMAGE_CONFIG_DIGEST,
            "sha256:0f21ddfb3313affe3a336693886ced918301335815e4b7db3d15b5a0a5da6afb",
        )
        network = " ".join(build_docker_network_argv())
        self.assertIn("--subnet 172.29.251.0/28", network)
        self.assertIn("--gateway 172.29.251.1", network)
        self.assertIn("com.docker.network.bridge.name=amn2spbr0", network)

    def test_rendered_awg_and_servers_are_write_disabled_and_zero_peer(self) -> None:
        private = "A" * 43 + "="
        public = "B" * 43 + "="
        awg = render_awg_config(private)
        self.assertIn("PrivateKey = " + private, awg)
        for key in ("S1 = 15", "S2 = 18", "S3 = 20", "S4 = 23"):
            self.assertIn(key, awg)
        self.assertNotIn("[Peer]", awg)
        servers = render_servers_yml(endpoint_host="198.51.100.12", public_key=public)
        self.assertIn("name: spain", servers)
        self.assertIn("network_cidr: 10.212.12.0/24", servers)
        self.assertIn("port: 30001", servers)
        self.assertIn("server_public_key: " + public, servers)
        self.assertIn("config_path: /etc/amnezia/amneziawg/awgsp0.conf", servers)
        self.assertIn("open_vpn_port: false", servers)


class _FakeDockerRunner:
    endpoint_id = "a" * 64
    container_id = "b" * 64
    network_id = "c" * 64

    def __init__(self) -> None:
        self.image = "absent"
        self.network = False
        self.container = False
        self.running = False
        self.peers = b""
        self.listen_port = b"30001\n"
        self.calls: list[tuple[tuple[str, ...], dict[str, object]]] = []

    @staticmethod
    def _line(value: dict[str, object]) -> bytes:
        return json.dumps(value, separators=(",", ":")).encode() + b"\n"

    def __call__(self, argv: tuple[str, ...], **kwargs: object) -> bytes:
        self.assert_allowed(argv)
        self.calls.append((argv, dict(kwargs)))
        if argv == live_backend.DOCKER_IMAGE_LIST_ARGV:
            if self.image == "absent":
                return b""
            if self.image == "partial":
                return self._line({
                    "ID": live_backend.AWG_IMAGE_CONFIG_DIGEST,
                    "Repository": "<none>",
                    "Tag": "<none>",
                })
            return self._line({
                "ID": live_backend.AWG_IMAGE_CONFIG_DIGEST,
                "Repository": "amn2-spain-awg",
                "Tag": "phase12",
            })
        if argv in {
            live_backend.DOCKER_IMAGE_INSPECT_TAG_ARGV,
            live_backend.DOCKER_IMAGE_INSPECT_ID_ARGV,
        }:
            return self._line({
                "Architecture": "amd64",
                "Id": live_backend.AWG_IMAGE_CONFIG_DIGEST,
                "Os": "linux",
                "RepoTags": (
                    [live_backend.AWG_LOCAL_IMAGE_TAG]
                    if self.image == "full" else None
                ),
            })
        if argv == live_backend.DOCKER_IMAGE_LOAD_ARGV:
            descriptor = kwargs["input_fd"]
            expected = kwargs["input_size"]
            self.assert_regular_fd(descriptor, expected)
            while os.read(descriptor, 64 * 1024):
                pass
            self.image = "partial"
            return (
                b"Loaded image ID: "
                + live_backend.AWG_IMAGE_CONFIG_DIGEST.encode()
                + b"\n"
            )
        if argv == live_backend.DOCKER_IMAGE_TAG_ARGV:
            self.image = "full"
            return b""
        if argv == live_backend.DOCKER_IMAGE_RM_TAG_ARGV:
            self.image = "partial"
            return b""
        if argv == live_backend.DOCKER_IMAGE_RM_ID_ARGV:
            self.image = "absent"
            return b""
        if argv == live_backend.DOCKER_NETWORK_LIST_ARGV:
            rows = [
                self._line({"ID": "d" * 64, "Name": "host"}),
                self._line({"ID": "e" * 64, "Name": "none"}),
            ]
            if self.network:
                rows.append(
                    self._line({"ID": self.network_id, "Name": "amn2-spain-net"})
                )
            return b"".join(rows)
        if argv == live_backend.DOCKER_NETWORK_INSPECT_ARGV:
            containers: dict[str, object] = {}
            if self.container:
                containers[self.container_id] = {
                    "Name": "amn2-spain-awg",
                    "EndpointID": self.endpoint_id,
                    "MacAddress": "02:42:ac:1d:fb:02",
                    "IPv4Address": "172.29.251.2/28",
                    "IPv6Address": "",
                }
            return self._line({
                "Attachable": False,
                "Bridge": "amn2spbr0",
                "Containers": containers,
                "Driver": "bridge",
                "Gateway": "172.29.251.1",
                "ID": self.network_id,
                "Ingress": False,
                "Internal": False,
                "Name": "amn2-spain-net",
                "Scope": "local",
                "Subnet": "172.29.251.0/28",
            })
        if argv == build_docker_network_argv():
            self.network = True
            return self.network_id.encode() + b"\n"
        if argv == live_backend.DOCKER_NETWORK_RM_ARGV:
            if self.container:
                raise AssertionError("network removed before container")
            self.network = False
            return b"amn2-spain-net\n"
        if argv == live_backend.DOCKER_CONTAINER_LIST_ARGV:
            return (
                self._line({"ID": self.container_id, "Names": "amn2-spain-awg"})
                if self.container else b""
            )
        if argv == live_backend.DOCKER_CONTAINER_INSPECT_ARGV:
            return self._line({
                "CapAdd": ["NET_ADMIN"],
                "CapDrop": ["ALL"],
                "ConfigImage": live_backend.AWG_LOCAL_IMAGE_TAG,
                "Devices": [{
                    "PathOnHost": "/dev/net/tun",
                    "PathInContainer": "/dev/net/tun",
                    "CgroupPermissions": "rwm",
                }],
                "Entrypoint": ["/usr/local/sbin/amn2-awg-start"],
                "ID": self.container_id,
                "Image": live_backend.AWG_IMAGE_CONFIG_DIGEST,
                "Mounts": [
                    {
                        "Type": "bind",
                        "Source": "/etc/amn2-spain/awgsp0.conf",
                        "Destination": "/etc/amnezia/amneziawg/awgsp0.conf",
                        "RW": False,
                    },
                    {
                        "Type": "bind",
                        "Source": "/opt/amn2-spain/runtime/awg-start.sh",
                        "Destination": "/usr/local/sbin/amn2-awg-start",
                        "RW": False,
                    },
                ],
                "Name": "/amn2-spain-awg",
                "NetworkEndpointID": self.endpoint_id,
                "NetworkIPAddress": "172.29.251.2",
                "ReadonlyRootfs": True,
                "RestartCount": 0,
                "RestartName": "unless-stopped",
                "Running": self.running,
                "TmpfsRun": "rw,noexec,nosuid,nodev,size=16m",
            })
        if argv == build_container_create_argv():
            self.container = True
            self.running = False
            return self.container_id.encode() + b"\n"
        if argv == live_backend.DOCKER_CONTAINER_START_ARGV:
            self.running = True
            return b"amn2-spain-awg\n"
        if argv == live_backend.DOCKER_CONTAINER_STOP_ARGV:
            self.running = False
            return b"amn2-spain-awg\n"
        if argv == live_backend.DOCKER_CONTAINER_RM_ARGV:
            if self.running:
                raise AssertionError("running container removed")
            self.container = False
            return b"amn2-spain-awg\n"
        if argv == live_backend.DOCKER_ZERO_PEER_ARGV:
            return self.peers
        if argv == live_backend.DOCKER_LISTEN_PORT_ARGV:
            return self.listen_port
        raise AssertionError(argv)

    @staticmethod
    def assert_allowed(argv: tuple[str, ...]) -> None:
        if argv not in live_backend.DOCKER_COMMAND_ALLOWLIST:
            raise AssertionError("argv outside allowlist")

    @staticmethod
    def assert_regular_fd(descriptor: object, expected: object) -> None:
        if not isinstance(descriptor, int) or not isinstance(expected, int):
            raise AssertionError("fd boundary missing")
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != expected:
            raise AssertionError("fd boundary drift")


class ProductionDockerRuntimeTests(unittest.TestCase):
    CONFIG_BODY = b'{"architecture":"amd64","os":"linux"}'

    def setUp(self) -> None:
        self._config_digest_patch = patch.object(
            live_backend,
            "AWG_IMAGE_CONFIG_DIGEST",
            "sha256:" + hashlib.sha256(self.CONFIG_BODY).hexdigest(),
        )
        self._config_digest_patch.start()

    def tearDown(self) -> None:
        self._config_digest_patch.stop()

    @staticmethod
    def _image_archive(
        *,
        repo_tags: object = None,
        repositories: object = None,
        layer_variant: str = "",
    ) -> bytes:
        config_name = (
            live_backend.AWG_IMAGE_CONFIG_DIGEST.removeprefix("sha256:") + ".json"
        )
        layers = (
            [config_name]
            if layer_variant == "config"
            else ["layer/layer.tar", "layer/layer.tar"]
            if layer_variant == "duplicate"
            else ["layer/layer.tar"]
        )
        members = {
            "manifest.json": json.dumps(
                [{
                    "Config": config_name,
                    "RepoTags": repo_tags,
                    "Layers": layers,
                }],
                separators=(",", ":"),
            ).encode(),
            "repositories": json.dumps(
                {} if repositories is None else repositories,
                separators=(",", ":"),
            ).encode(),
            config_name: ProductionDockerRuntimeTests.CONFIG_BODY,
            "layer/layer.tar": b"layer-bytes",
        }
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w") as archive:
            for name, body in members.items():
                member = tarfile.TarInfo(name)
                member.mode = 0o644
                member.size = len(body)
                archive.addfile(member, io.BytesIO(body))
        return output.getvalue()

    def test_offline_image_network_container_zero_peer_apply_and_reverse_rollback(self) -> None:
        archive_body = self._image_archive()
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "awg-image.tar"
            archive.write_bytes(archive_body)
            runner = _FakeDockerRunner()
            socket_checks: list[str] = []
            bundle = live_backend.build_production_docker_runtime_bundle(
                runner=runner,
                image_archive_path=archive,
                image_archive_sha256=hashlib.sha256(archive_body).hexdigest(),
                image_archive_size=len(archive_body),
                socket_observer=lambda: (
                    socket_checks.append("checked")
                    or {
                        "kind": "unix-socket",
                        "path": "/run/amn2-spain-docker/docker.sock",
                        "mode": "0660",
                        "uid": 0,
                        "gid": 0,
                    }
                ),
            )
            self.assertEqual(
                bundle.dynamic_observation_fields,
                frozenset(
                    {"container_id", "endpoint_id", "mac_address", "network_id"}
                ),
            )
            for alias in (
                "socket:/run/amn2-spain-docker/docker.sock",
                "bridge:amn2spbr0",
                "listener:udp:30001",
                "endpoint:amn2-spain-awg@amn2-spain-net",
            ):
                self.assertIn(alias, bundle.logical_receipt)
            operations = tuple(action.operation for action in bundle.actions)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={
                        action.operation.owned_object: action
                        for action in bundle.actions
                    }
                ),
                ledger=MutationLedger(
                    allowed_objects={
                        action.operation.owned_object for action in bundle.actions
                    }
                ),
            )
            backend.apply(operations)
            self.assertEqual((runner.image, runner.network), ("full", True))
            self.assertTrue(runner.container)
            self.assertTrue(runner.running)
            load = next(
                kwargs for argv, kwargs in runner.calls
                if argv == live_backend.DOCKER_IMAGE_LOAD_ARGV
            )
            self.assertNotIn("input_bytes", load)
            self.assertEqual(load["input_size"], len(archive_body))
            backend.rollback(operations)
            self.assertEqual((runner.image, runner.network), ("absent", False))
            self.assertFalse(runner.container)
            calls = [argv for argv, _kwargs in runner.calls]
            stop_index = calls.index(live_backend.DOCKER_CONTAINER_STOP_ARGV)
            rm_container_index = calls.index(live_backend.DOCKER_CONTAINER_RM_ARGV)
            rm_network_index = calls.index(live_backend.DOCKER_NETWORK_RM_ARGV)
            rm_image_index = calls.index(live_backend.DOCKER_IMAGE_RM_ID_ARGV)
            self.assertLess(stop_index, rm_container_index)
            self.assertLess(rm_container_index, rm_network_index)
            self.assertLess(rm_network_index, rm_image_index)
            self.assertNotIn(
                live_backend.DOCKER_CONTAINER_START_ARGV,
                calls[stop_index + 1:],
            )
            self.assertEqual(len(socket_checks), len(runner.calls))

    def test_crash_after_load_adopts_exact_config_id_without_reloading(self) -> None:
        archive_body = self._image_archive()
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "awg-image.tar"
            archive.write_bytes(archive_body)
            runner = _FakeDockerRunner()
            runner.image = "partial"
            action = live_backend.build_awg_image_action(
                runner=runner,
                archive_path=archive,
                expected_sha256=hashlib.sha256(archive_body).hexdigest(),
                expected_size=len(archive_body),
            )
            self.assertIsNone(action.observe_pending_identity())
            action.create_exact()
            self.assertEqual(action.observe_identity(), action.operation.desired_identity)
            calls = [argv for argv, _kwargs in runner.calls]
            self.assertNotIn(live_backend.DOCKER_IMAGE_LOAD_ARGV, calls)
            self.assertIn(live_backend.DOCKER_IMAGE_TAG_ARGV, calls)

    def test_nonzero_peer_health_fails_closed_without_restart(self) -> None:
        runner = _FakeDockerRunner()
        runner.image = "full"
        runner.network = True
        runner.container = True
        runner.running = True
        runner.peers = b"peer-public-key\n"
        _container, active = live_backend.build_awg_container_actions(runner=runner)
        with self.assertRaisesRegex(BackendError, "zero-peer"):
            active.observe_identity()
        self.assertNotIn(
            live_backend.DOCKER_CONTAINER_START_ARGV,
            [argv for argv, _kwargs in runner.calls],
        )

    def test_image_archive_must_be_untagged_with_empty_repositories_before_mutation(self) -> None:
        for label, body in (
            (
                "tagged",
                self._image_archive(repo_tags=["amneziavpn/amneziawg-go:latest"]),
            ),
            (
                "repositories",
                self._image_archive(
                    repositories={"amneziavpn/amneziawg-go": {"latest": "id"}}
                ),
            ),
            ("duplicate-layer", self._image_archive(layer_variant="duplicate")),
            ("config-as-layer", self._image_archive(layer_variant="config")),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as raw:
                archive = Path(raw) / "awg-image.tar"
                archive.write_bytes(body)
                runner = _FakeDockerRunner()
                with self.assertRaisesRegex(BackendError, "untagged"):
                    live_backend.build_awg_image_action(
                        runner=runner,
                        archive_path=archive,
                        expected_sha256=hashlib.sha256(body).hexdigest(),
                        expected_size=len(body),
                    )
                self.assertEqual(runner.calls, [])

    def test_image_observer_rejects_any_foreign_daemon_image_row(self) -> None:
        class ForeignImageRunner(_FakeDockerRunner):
            def __call__(self, argv: tuple[str, ...], **kwargs: object) -> bytes:
                if argv == live_backend.DOCKER_IMAGE_LIST_ARGV:
                    return self._line({
                        "ID": "sha256:" + "f" * 64,
                        "Repository": "foreign",
                        "Tag": "latest",
                    })
                return super().__call__(argv, **kwargs)

        body = self._image_archive()
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "awg-image.tar"
            archive.write_bytes(body)
            action = live_backend.build_awg_image_action(
                runner=ForeignImageRunner(),
                archive_path=archive,
                expected_sha256=hashlib.sha256(body).hexdigest(),
                expected_size=len(body),
            )
            with self.assertRaisesRegex(BackendError, "closed-delta"):
                action.observe_identity()

    def test_docker_runner_failure_is_generic_and_does_not_leak(self) -> None:
        secret = "foreign-service-secret"

        def fail(_argv: tuple[str, ...], **_kwargs: object) -> bytes:
            raise RuntimeError(secret)

        action = live_backend.build_docker_network_action(runner=fail)
        with self.assertRaises(BackendError) as caught:
            action.observe_identity()
        self.assertEqual(str(caught.exception), "Docker command failed")
        self.assertNotIn(secret, repr(caught.exception))

    def test_socket_guard_rejects_non_root_socket_before_first_docker_command(self) -> None:
        body = self._image_archive()
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "awg-image.tar"
            archive.write_bytes(body)
            runner = _FakeDockerRunner()
            bundle = live_backend.build_production_docker_runtime_bundle(
                runner=runner,
                image_archive_path=archive,
                image_archive_sha256=hashlib.sha256(body).hexdigest(),
                image_archive_size=len(body),
                socket_observer=lambda: {
                    "kind": "unix-socket",
                    "path": "/run/amn2-spain-docker/docker.sock",
                    "mode": "0660",
                    "uid": 0,
                    "gid": 999,
                },
            )
            with self.assertRaisesRegex(BackendError, "Docker command failed"):
                bundle.actions[0].observe_identity()
            self.assertEqual(runner.calls, [])

    def test_foreign_network_or_container_rows_fail_closed(self) -> None:
        class ForeignNetworkRunner(_FakeDockerRunner):
            def __call__(self, argv: tuple[str, ...], **kwargs: object) -> bytes:
                if argv == live_backend.DOCKER_NETWORK_LIST_ARGV:
                    return b"".join([
                        self._line({"ID": "d" * 64, "Name": "host"}),
                        self._line({"ID": "e" * 64, "Name": "none"}),
                        self._line({"ID": "f" * 64, "Name": "foreign-net"}),
                    ])
                return super().__call__(argv, **kwargs)

        class ForeignContainerRunner(_FakeDockerRunner):
            def __call__(self, argv: tuple[str, ...], **kwargs: object) -> bytes:
                if argv == live_backend.DOCKER_CONTAINER_LIST_ARGV:
                    return self._line({
                        "ID": "f" * 64,
                        "Names": "foreign-container",
                    })
                return super().__call__(argv, **kwargs)

        with self.assertRaisesRegex(BackendError, "network list"):
            live_backend.build_docker_network_action(
                runner=ForeignNetworkRunner()
            ).observe_identity()
        container, _active = live_backend.build_awg_container_actions(
            runner=ForeignContainerRunner()
        )
        with self.assertRaisesRegex(BackendError, "container list"):
            container.observe_identity()

    def test_wrong_listen_port_fails_closed_without_restart(self) -> None:
        runner = _FakeDockerRunner()
        runner.image = "full"
        runner.network = True
        runner.container = True
        runner.running = True
        runner.listen_port = b"30002\n"
        _container, active = live_backend.build_awg_container_actions(runner=runner)
        with self.assertRaisesRegex(BackendError, "listen-port"):
            active.observe_identity()
        self.assertNotIn(
            live_backend.DOCKER_CONTAINER_START_ARGV,
            [argv for argv, _kwargs in runner.calls],
        )


class ProductionFilesystemBundleTests(unittest.TestCase):
    def test_generic_runtime_secret_material_is_repr_safe_and_has_no_password_seed(self) -> None:
        values = ("A" * 64, "B" * 64, "C" * 64, "D" * 64)
        with patch(
            "scripts.phase12_spain_live_backend.secrets.token_urlsafe",
            side_effect=values,
        ):
            material = live_backend.generate_runtime_secrets()
        self.assertFalse(any(value in repr(material) for value in values))
        self.assertFalse(hasattr(material, "web_admin_password_seed"))
        self.assertNotIn("WEB_ADMIN_PASSWORD_SEED", repr(material))

    def test_runtime_secret_file_contract_is_root_only_0600(self) -> None:
        self.assertTrue(
            hasattr(live_backend, "PRODUCTION_FILE_SECURITY"),
            "production file security contract missing",
        )

    def test_payload_preparation_needs_no_future_install_parent_and_binding_does_not_regenerate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "future-root"
            secret_factory, secrets_used = self._secret_factory()
            prepared = live_backend.prepare_production_filesystem_payloads(
                source_root=ROOT / "worktrees" / "amn2-p7-c005-write-install",
                endpoint_host="198.51.100.12",
                secret_token_factory=secret_factory,
            )
            self.assertFalse(root.exists())
            self.assertFalse(any(secret in repr(prepared) for secret in secrets_used))
            capsule_specs = live_backend.recovery_capsule_payload_specs(prepared)
            self.assertEqual(
                set(capsule_specs), set(prepared.rendered_payloads)
            )
            self.assertEqual(
                capsule_specs["etc/amn2-spain/runtime.env"]["mode"], "0600"
            )
            self.assertEqual(
                capsule_specs["etc/amn2-spain/runtime.env"]["payload"],
                prepared.rendered_payloads["etc/amn2-spain/runtime.env"],
            )
            recovered = live_backend.recover_production_filesystem_payloads(
                source_root=ROOT / "worktrees" / "amn2-p7-c005-write-install",
                endpoint_host="198.51.100.12",
                expected_source_tree_identity=prepared.source_tree_identity,
                rendered_payloads={
                    path: spec["payload"] for path, spec in capsule_specs.items()
                },
            )
            self.assertEqual(recovered.source_tree_identity, prepared.source_tree_identity)
            self.assertEqual(dict(recovered.rendered_payloads), dict(prepared.rendered_payloads))
            self.assertEqual(
                dict(recovered.package_bound_payloads),
                dict(prepared.package_bound_payloads),
            )
            root.mkdir()
            self._install_root(root)
            uid, gid = self._owner_ids()
            bundle = live_backend.build_production_filesystem_bundle(
                root=root,
                source_root=ROOT / "worktrees" / "amn2-p7-c005-write-install",
                endpoint_host="198.51.100.12",
                root_uid=uid,
                root_gid=gid,
                service_uid=uid,
                service_gid=gid,
                secret_token_factory=lambda _size: (_ for _ in ()).throw(
                    AssertionError("binding regenerated secrets")
                ),
                prepared_payloads=prepared,
            )
            self.assertTrue(bundle.actions)
        self.assertEqual(
            live_backend.PRODUCTION_FILE_SECURITY["etc/amn2-spain/runtime.env"],
            ("root", "root", 0o600),
        )

    @staticmethod
    def _install_root(root: Path) -> None:
        for relative in ("opt", "etc", "var", "var/lib", "run"):
            path = root / relative
            path.mkdir(exist_ok=True)
            if os.name != "nt":
                path.chmod(0o755)

    @staticmethod
    def _owner_ids() -> tuple[int | None, int | None]:
        if os.name == "nt":
            return None, None
        return os.getuid(), os.getgid()

    @staticmethod
    def _secret_factory() -> tuple[object, tuple[str, str, str, str]]:
        values = (
            "bot_" + "A" * 60,
            "app_" + "B" * 60,
            "session_" + "C" * 60,
            "temporary_password_" + "D" * 60,
        )
        iterator = iter(values)
        return (lambda _size: next(iterator)), values

    def _build(self, root: Path, secret_factory: object) -> object:
        uid, gid = self._owner_ids()
        return live_backend.build_production_filesystem_bundle(
            root=root,
            source_root=ROOT / "worktrees" / "amn2-p7-c005-write-install",
            endpoint_host="198.51.100.12",
            root_uid=uid,
            root_gid=gid,
            service_uid=uid,
            service_gid=gid,
            secret_token_factory=secret_factory,
        )

    def test_bundle_renders_exact_files_validates_auth_and_settings_without_bot_marker(self) -> None:
        self.assertTrue(
            hasattr(live_backend, "build_production_filesystem_bundle"),
            "production filesystem bundle API missing",
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._install_root(root)
            secret_factory, secrets_used = self._secret_factory()
            real_loader = live_backend._load_authoritative_module
            calls: list[str] = []

            def observing_loader(source: Path, relative: str, label: str) -> object:
                module = real_loader(source, relative, label)
                if relative == "app/web/auth.py":
                    create = module.create_password_hash
                    require = module.require_web_admin_config

                    def observed_create(password: str) -> str:
                        calls.append("create_password_hash")
                        return create(password)

                    def observed_require(*, password_hash: str, session_secret: str) -> None:
                        calls.append("require_web_admin_config")
                        require(password_hash=password_hash, session_secret=session_secret)

                    module.create_password_hash = observed_create
                    module.require_web_admin_config = observed_require
                return module

            with patch(
                "scripts.phase12_spain_live_backend._load_authoritative_module",
                side_effect=observing_loader,
            ), patch(
                "scripts.phase12_spain_live_backend._validate_authoritative_runtime_settings",
                wraps=live_backend._validate_authoritative_runtime_settings,
            ) as validate_settings:
                bundle = self._build(root, secret_factory)
            self.assertEqual(calls, ["create_password_hash", "require_web_admin_config"])
            validate_settings.assert_called_once()
            operations = tuple(action.operation for action in bundle.actions)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action for action in bundle.actions}
                ),
                ledger=MutationLedger(
                    allowed_objects={operation.owned_object for operation in operations}
                ),
            )
            backend.apply(operations)
            expected_directories = {
                "opt/amn2-spain": 0o755,
                "opt/amn2-spain/runtime": 0o755,
                "etc/amn2-spain": 0o750,
                "var/lib/amn2-spain": 0o750,
                "var/lib/amn2-spain/logs": 0o750,
                "var/lib/amn2-spain/config-templates": 0o750,
                "var/lib/amn2-spain-docker": 0o700,
                "run/amn2-spain-docker": 0o755,
                "opt/amn2-spain/current": 0o755,
                "opt/amn2-spain/current/scripts": 0o755,
                "opt/amn2-spain/current/packaging": 0o755,
                "opt/amn2-spain/current/packaging/phase12-spain": 0o755,
                "opt/amn2-spain/current/packaging/phase12-spain/templates": 0o755,
            }
            expected_files = {
                "etc/amn2-spain/runtime.env": 0o600,
                "etc/amn2-spain/awgsp0.conf": 0o600,
                "etc/amn2-spain/servers.yml": 0o640,
                "etc/amn2-spain/docker-daemon.json": 0o644,
                "opt/amn2-spain/runtime/awg-start.sh": 0o755,
                "opt/amn2-spain/current/scripts/phase12_spain_network.py": 0o644,
                "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf": 0o644,
            }
            for relative, mode in {**expected_directories, **expected_files}.items():
                path = root / relative
                self.assertTrue(path.exists(), relative)
                if os.name != "nt":
                    self.assertEqual(stat.S_IMODE(os.lstat(path).st_mode), mode)
            self.assertFalse((root / "etc/amn2-spain/bot-enabled").exists())
            self.assertFalse((root / "opt/amn2-spain/current").is_symlink())
            runtime = (root / "etc/amn2-spain/runtime.env").read_text(encoding="utf-8")
            awg = (root / "etc/amn2-spain/awgsp0.conf").read_text(encoding="utf-8")
            servers = (root / "etc/amn2-spain/servers.yml").read_text(encoding="utf-8")
            daemon = (root / "etc/amn2-spain/docker-daemon.json").read_text(encoding="utf-8")
            start = (root / "opt/amn2-spain/runtime/awg-start.sh").read_text(encoding="utf-8")
            rendered = (runtime, awg, servers, daemon, start)
            self.assertTrue(all(text.endswith("\n") and "\r" not in text for text in rendered))
            self.assertTrue(all("__AMN2_" not in text for text in rendered))
            self.assertNotIn("[Peer]", awg)
            self.assertNotIn(secrets_used[3], "".join(rendered))
            self.assertIn("VPS_APPLY_ENABLED=false\n", runtime)
            self.assertIn("WEB_ADMIN_ENABLED=true\n", runtime)
            self.assertIn("server_public_key: ", servers)
            self.assertEqual(json.loads(daemon)["bridge"], "none")
            self.assertIn("awg-quick up awgsp0", start)
            self.assertEqual(
                (root / "opt/amn2-spain/current/scripts/phase12_spain_network.py").read_bytes(),
                (ROOT / "scripts/phase12_spain_network.py").read_bytes(),
            )
            self.assertEqual(
                (
                    root
                    / "opt/amn2-spain/current/packaging/phase12-spain/templates/nftables.conf"
                ).read_bytes(),
                (TEMPLATES / "nftables.conf").read_bytes(),
            )

    def test_bundle_receipt_repr_ledger_and_errors_do_not_disclose_raw_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._install_root(root)
            secret_factory, secrets_used = self._secret_factory()
            bundle = self._build(root, secret_factory)
            operations = tuple(action.operation for action in bundle.actions)
            ledger = MutationLedger(
                allowed_objects={operation.owned_object for operation in operations}
            )
            for operation in operations:
                ledger.intent(operation.stage, operation.owned_object, operation.desired_identity)
            safe_surfaces = "\n".join(
                (
                    repr(bundle),
                    repr(bundle.actions),
                    json.dumps(dict(bundle.logical_receipt), sort_keys=True),
                    ledger.to_bytes().decode("ascii"),
                )
            )
            self.assertFalse(any(secret in safe_surfaces for secret in secrets_used))
            self.assertEqual(
                set(bundle.logical_receipt),
                {operation.owned_object for operation in operations},
            )
            self.assertTrue(
                all(
                    MutationLedger._valid_identity(identity)
                    for identity in bundle.logical_receipt.values()
                )
            )
            failing_factory, failing_values = self._secret_factory()
            real_loader = live_backend._load_authoritative_module

            def failing_loader(source: Path, relative: str, label: str) -> object:
                module = real_loader(source, relative, label)
                if relative == "app/web/auth.py":
                    module.require_web_admin_config = lambda **_kwargs: (_ for _ in ()).throw(
                        ValueError("unsafe:" + failing_values[2])
                    )
                return module

            with patch(
                "scripts.phase12_spain_live_backend._load_authoritative_module",
                side_effect=failing_loader,
            ):
                with self.assertRaises(BackendError) as caught:
                    self._build(root, failing_factory)
            self.assertNotIn(failing_values[2], str(caught.exception))
            self.assertNotIn(failing_values[3], repr(caught.exception))

    def test_pending_exact_bundle_is_adopted_and_reverse_rollback_removes_only_owned(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._install_root(root)
            secret_factory, _secrets_used = self._secret_factory()
            bundle = self._build(root, secret_factory)
            operations = tuple(action.operation for action in bundle.actions)
            actions = {action.operation.owned_object: action for action in bundle.actions}
            first = LinuxBackend(
                adapter=SystemOwnedAdapter(actions=actions),
                ledger=MutationLedger(
                    allowed_objects={operation.owned_object for operation in operations}
                ),
            )
            first.apply(operations)
            pending = MutationLedger(
                allowed_objects={operation.owned_object for operation in operations}
            )
            for operation in operations:
                pending.intent(operation.stage, operation.owned_object, operation.desired_identity)
            recovered = LinuxBackend(
                adapter=SystemOwnedAdapter(actions=actions), ledger=pending
            )
            recovered.apply(operations)
            self.assertTrue(
                all(pending.state(operation.owned_object) == "committed" for operation in operations)
            )
            recovered.rollback(operations)
            self.assertFalse((root / "opt/amn2-spain").exists())
            self.assertFalse((root / "etc/amn2-spain").exists())
            self.assertFalse((root / "var/lib/amn2-spain").exists())
            self.assertFalse((root / "var/lib/amn2-spain-docker").exists())
            self.assertFalse((root / "run/amn2-spain-docker").exists())
            for base in ("opt", "etc", "var/lib", "run"):
                self.assertTrue((root / base).is_dir())


class AuthoritativeAppAndObservationTests(unittest.TestCase):
    @staticmethod
    def _minimal_database_source(root: Path) -> Path:
        source = root / "source"
        database_package = source / "app" / "db"
        database_package.mkdir(parents=True)
        for directory in (source, source / "app", database_package):
            directory.chmod(0o755)
        for marker in (source / "app" / "__init__.py", database_package / "__init__.py"):
            marker.write_text("", encoding="utf-8")
            marker.chmod(0o644)
        connection = database_package / "connection.py"
        connection.write_text(
            "import sqlite3\nfrom pathlib import Path\n"
            "def connect(path):\n"
            "    if Path(path).exists():\n"
            "        raise RuntimeError('writable connect used for observation')\n"
            "    value = sqlite3.connect(path)\n"
            "    value.execute('PRAGMA foreign_keys=ON')\n"
            "    return value\n"
            "def connect_read_only(path):\n"
            "    database = Path(path).resolve()\n"
            "    value = sqlite3.connect(f'{database.as_uri()}?mode=ro', uri=True)\n"
            "    value.execute('PRAGMA foreign_keys=ON')\n"
            "    value.execute('PRAGMA query_only=ON')\n"
            "    return value\n",
            encoding="utf-8",
        )
        connection.chmod(0o644)
        schema = database_package / "schema.py"
        schema.write_text(
            "def initialize_schema(connection):\n"
            "    connection.execute('CREATE TABLE users (id INTEGER PRIMARY KEY)')\n",
            encoding="utf-8",
        )
        schema.chmod(0o644)
        return source

    def test_authoritative_key_generation_and_clean_database_have_no_rows(self) -> None:
        source = ROOT / "worktrees" / "amn2-p7-c005-write-install"
        private, public = generate_server_keypair(source)
        self.assertNotEqual(private, public)
        self.assertEqual(len(private), 44)
        material = generate_server_keypair(source)
        self.assertNotIn(material.private_key, repr(material))
        ledger = MutationLedger(allowed_objects={"secret:/etc/amn2-spain/awgsp0.conf"})
        ledger.intent(
            "secrets",
            "secret:/etc/amn2-spain/awgsp0.conf",
            "sha256:" + "1" * 64,
        )
        self.assertNotIn(material.private_key, ledger.to_bytes().decode("ascii"))
        with tempfile.TemporaryDirectory() as raw:
            database = Path(raw) / "amn2.sqlite3"
            result = initialize_clean_database(source, database)
            self.assertEqual(result["integrity_check"], "ok")
            self.assertEqual(result["foreign_key_check"], [])
            self.assertEqual(result["foreign_keys"], 1)
            self.assertGreater(result["application_table_count"], 0)
            self.assertEqual(result["nonempty_tables"], {})

    def test_clean_database_is_one_semantic_action_with_cas_rollback(self) -> None:
        source = ROOT / "worktrees" / "amn2-p7-c005-write-install"
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "amn2.sqlite3"
            uid = os.getuid() if hasattr(os, "getuid") else None
            gid = os.getgid() if hasattr(os, "getgid") else None
            action = build_clean_database_action(
                source, path, expected_uid=uid, expected_gid=gid
            )
            adapter = SystemOwnedAdapter(actions={action.operation.owned_object: action})
            backend = LinuxBackend(
                adapter=adapter,
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            backend.apply((action.operation,))
            self.assertTrue(path.is_file())
            backend.rollback((action.operation,))
            self.assertFalse(path.exists())

    def test_production_clean_db_binds_source_owner_empty_tables_and_cas(self) -> None:
        import sqlite3

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self._minimal_database_source(root)
            source_identity = source_tree_identity(source)
            database = root / "state" / "amn2.sqlite3"
            database.parent.mkdir(mode=0o755)
            uid = os.getuid() if hasattr(os, "getuid") else None
            gid = os.getgid() if hasattr(os, "getgid") else None
            action = build_production_clean_database_action(
                source_root=source,
                expected_source_tree_identity=source_identity,
                database_path=database,
                expected_uid=uid,
                expected_gid=gid,
            )
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(actions={action.operation.owned_object: action}),
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            backend.apply((action.operation,))
            self.assertEqual(source_tree_identity(source), source_identity)
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)
                connection.execute("INSERT INTO users DEFAULT VALUES")
                connection.commit()
            finally:
                connection.close()
            with self.assertRaisesRegex(BackendError, "drift"):
                backend.rollback((action.operation,))
            connection = sqlite3.connect(database)
            try:
                connection.execute("DELETE FROM users")
                connection.commit()
            finally:
                connection.close()
            connection = sqlite3.connect(database)
            try:
                connection.execute(
                    "CREATE TRIGGER unexpected AFTER INSERT ON users BEGIN SELECT 1; END"
                )
                connection.commit()
            finally:
                connection.close()
            with self.assertRaisesRegex(BackendError, "drift"):
                backend.rollback((action.operation,))
            connection = sqlite3.connect(database)
            try:
                connection.execute("DROP TRIGGER unexpected")
                connection.commit()
            finally:
                connection.close()
            backend.rollback((action.operation,))
            self.assertFalse(database.exists())

    def test_deferred_production_clean_db_is_planned_before_future_parent_exists(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self._minimal_database_source(root)
            source_identity = source_tree_identity(source)
            database = root / "future-state" / "amn2.sqlite3"
            uid = os.getuid() if hasattr(os, "getuid") else None
            gid = os.getgid() if hasattr(os, "getgid") else None
            action = build_deferred_production_clean_database_action(
                source_root=source,
                expected_source_tree_identity=source_identity,
                database_path=database,
                expected_uid=uid,
                expected_gid=gid,
            )
            self.assertFalse(database.parent.exists())
            database.parent.mkdir(mode=0o755)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(
                    actions={action.operation.owned_object: action}
                ),
                ledger=MutationLedger(
                    allowed_objects={action.operation.owned_object}
                ),
            )
            backend.apply((action.operation,))
            self.assertTrue(database.is_file())
            backend.rollback((action.operation,))
            self.assertFalse(database.exists())

    def test_production_clean_db_pending_exact_is_adopted_and_source_drift_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self._minimal_database_source(root)
            source_identity = source_tree_identity(source)
            database = root / "state" / "amn2.sqlite3"
            database.parent.mkdir(mode=0o755)
            uid = os.getuid() if hasattr(os, "getuid") else None
            gid = os.getgid() if hasattr(os, "getgid") else None
            action = build_production_clean_database_action(
                source_root=source,
                expected_source_tree_identity=source_identity,
                database_path=database,
                expected_uid=uid,
                expected_gid=gid,
            )
            ledger = MutationLedger(allowed_objects={action.operation.owned_object})
            ledger.intent(
                action.operation.stage,
                action.operation.owned_object,
                action.operation.desired_identity,
            )
            initialize_clean_database(source, database)
            if os.name != "nt":
                os.chown(database, uid if uid is not None else -1, gid if gid is not None else -1)
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(actions={action.operation.owned_object: action}),
                ledger=ledger,
            )
            backend.apply((action.operation,))
            self.assertEqual(ledger.state(action.operation.owned_object), "committed")

            second_database = root / "state" / "second.sqlite3"
            second = build_production_clean_database_action(
                source_root=source,
                expected_source_tree_identity=source_identity,
                database_path=second_database,
                expected_uid=uid,
                expected_gid=gid,
            )
            second_ledger = MutationLedger(
                allowed_objects={second.operation.owned_object}
            )
            second_ledger.intent(
                second.operation.stage,
                second.operation.owned_object,
                second.operation.desired_identity,
            )
            initialize_clean_database(source, second_database)
            if os.name != "nt":
                os.chown(
                    second_database,
                    uid if uid is not None else -1,
                    gid if gid is not None else -1,
                )
            (source / "app" / "db" / "schema.py").write_text(
                "# drift\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(BackendError, "source tree"):
                LinuxBackend(
                    adapter=SystemOwnedAdapter(
                        actions={second.operation.owned_object: second}
                    ),
                    ledger=second_ledger,
                ).apply((second.operation,))

    @unittest.skipIf(os.name == "nt", "POSIX dirfd rollback CAS")
    def test_production_clean_db_rollback_refuses_leaf_swap_after_observation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = self._minimal_database_source(root)
            source_identity = source_tree_identity(source)
            database = root / "state" / "amn2.sqlite3"
            replacement = root / "state" / "replacement.sqlite3"
            database.parent.mkdir(mode=0o755)
            uid = os.getuid()
            gid = os.getgid()
            action = build_production_clean_database_action(
                source_root=source,
                expected_source_tree_identity=source_identity,
                database_path=database,
                expected_uid=uid,
                expected_gid=gid,
            )
            backend = LinuxBackend(
                adapter=SystemOwnedAdapter(actions={action.operation.owned_object: action}),
                ledger=MutationLedger(allowed_objects={action.operation.owned_object}),
            )
            backend.apply((action.operation,))
            initialize_clean_database(source, replacement)
            os.chown(replacement, uid, gid)
            real_open = os.open
            swapped = False

            def swap_before_leaf_open(
                candidate: object,
                flags: int,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> int:
                nonlocal swapped
                if candidate == database.name and dir_fd is not None and not swapped:
                    os.replace(replacement, database)
                    swapped = True
                return real_open(candidate, flags, mode, dir_fd=dir_fd)

            with patch("scripts.phase12_spain_live_backend.os.open", swap_before_leaf_open):
                with self.assertRaisesRegex(BackendError, "swap/drift"):
                    backend.rollback((action.operation,))
            self.assertTrue(swapped)
            self.assertTrue(database.exists())

    def test_strict_observation_binds_evidence_and_exact_closed_delta(self) -> None:
        bindings = {
            key: "sha256:" + f"{index:064x}"
            for index, key in enumerate(
                (
                    "collector_sha256",
                    "executor_sha256",
                    "run009_evidence_sha256",
                    "fingerprint_array_sha256",
                    "package_archive_sha256",
                    "package_manifest_sha256",
                    "resource_plan_sha256",
                    "approval_sha256",
                ),
                start=1,
            )
        }
        expected_objects = set(REQUIRED_CLOSED_DELTA_OBJECTS) | {
            "file:/etc/amn2-spain/runtime.env"
        }
        owned_delta = {
            owned: "sha256:" + f"{index:064x}"
            for index, owned in enumerate(sorted(expected_objects), start=20)
        }
        good = {
            "schema": "amn2.spain-live-postinstall-observation.v1",
            "result": "passed",
            "bindings": dict(bindings),
            "owned_delta": owned_delta,
            "database": {
                "integrity_check": "ok",
                "foreign_key_check": [],
                "foreign_keys": 1,
                "application_table_count": 20,
                "nonempty_tables": {},
            },
            "network": {
                "ledger_sha256": "sha256:" + "a" * 64,
                "nft_semantic_sha256": "sha256:13effd5c80bae2a6381234633c84c89421c35c2b5d873a7132f2189399daf65d",
                "nft_rule_comments": [
                    "amn2_spain:udp30001",
                    "amn2_spain:forward-dnat",
                    "amn2_spain:forward-outbound",
                    "amn2_spain:forward-return",
                    "amn2_spain:masquerade",
                ],
                "route": {"dst": "10.212.12.0/24", "gateway": "172.29.251.2", "dev": "amn2spbr0"},
                "sysctl": {"name": "net.ipv4.ip_forward", "applied": "1"},
            },
            "runtime": {
                "peer_count": 0,
                "container_restart_count": 0,
                "web_listener": "127.0.0.1:3031",
                "udp_listener": "0.0.0.0:30001",
                "docker_socket": "/run/amn2-spain-docker/docker.sock",
                "awg_interface": "awgsp0",
                "vps_apply_enabled": False,
                "bot_enabled": False,
                "bot_active": False,
            },
        }
        self.assertEqual(
            strict_postinstall_observation(
                good,
                expected_owned_objects=expected_objects,
                expected_bindings=bindings,
            ),
            good,
        )
        for key, bad in (
            ("peer_count", 1),
            ("container_restart_count", 1),
            ("web_listener", "0.0.0.0:3031"),
            ("vps_apply_enabled", True),
            ("bot_active", True),
        ):
            with self.subTest(key=key):
                changed = json.loads(json.dumps(good))
                changed["runtime"][key] = bad
                with self.assertRaisesRegex(BackendError, "postinstall"):
                    strict_postinstall_observation(
                        changed,
                        expected_owned_objects=expected_objects,
                        expected_bindings=bindings,
                    )
        changed = json.loads(json.dumps(good))
        changed["owned_delta"]["foreign:service"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(BackendError, "closed delta"):
            strict_postinstall_observation(
                changed,
                expected_owned_objects=expected_objects,
                expected_bindings=bindings,
            )
        changed = json.loads(json.dumps(good))
        changed["bindings"]["collector_sha256"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(BackendError, "binding"):
            strict_postinstall_observation(
                changed,
                expected_owned_objects=expected_objects,
                expected_bindings=bindings,
            )


if __name__ == "__main__":
    unittest.main()
