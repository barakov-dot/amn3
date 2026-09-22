"""Single-attempt remote supervisor for the synthetic readback guard only."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import sqlite3
import stat
import subprocess
import sys
import threading
import time


APPROVAL = "PHASE16_SYNTHETIC_READBACK_GUARD_20260922_001"
DESTINATION = "/opt/amn2-spain/bot-candidates/phase16-readback-guard-20260922-001"
MAGIC = b"P16RBG01"
CORE_NAME = "phase16_bot_integration_readback.py"
SMOKE_NAME = "phase16_bot_readback_guard_smoke.py"
CORE_SIZE = 23282
SMOKE_SIZE = 6975
CORE_SHA256 = "f6b152a3439a3c89d6ea900133df4e6806ca0cc01e0bb893c22d59f82b5adaee"
SMOKE_SHA256 = "b860899e269528baaa0beaa69a760ff2aab643fb8e6e8c9e6c5d6dab230141c8"
PAYLOAD_SHA256 = "2898ecdc1476a3144c2438c1237990cbe6c9e249bb302f1848c01521dabb6224"
PAYLOAD_SIZE = 30281
MAX_OUTPUT = 65536
REMOTE_SECONDS = 45
_OWNED_DESTINATION = False


class RemoteStop(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise RemoteStop(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_payload(payload):
    require(type(payload) is bytes and len(payload) == PAYLOAD_SIZE and
            sha(payload) == PAYLOAD_SHA256 and payload[:8] == MAGIC, "payload_binding")
    try:
        core_size = int(payload[8:16])
        smoke_size = int(payload[16:24])
    except ValueError:
        raise RemoteStop("payload_binding") from None
    require((core_size, smoke_size) == (CORE_SIZE, SMOKE_SIZE), "payload_binding")
    core = payload[24:24 + core_size]
    smoke = payload[24 + core_size:]
    require(sha(core) == CORE_SHA256 and sha(smoke) == SMOKE_SHA256, "payload_binding")
    compile(core, CORE_NAME, "exec")
    compile(smoke, SMOKE_NAME, "exec")
    return {CORE_NAME: core, SMOKE_NAME: smoke}


def terminate_group(process):
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        raise RemoteStop("process_cleanup") from None


def run_bounded(command, *, timeout, cap):
    require(type(command) is list and 0 < timeout <= REMOTE_SECONDS and 0 < cap <= MAX_OUTPUT,
            "process_contract")
    try:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True, shell=False,
                                   env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"})
    except OSError:
        raise RemoteStop("process_start") from None
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    observed = {"stdout": 0, "stderr": 0}
    overflow = threading.Event()
    failures = threading.Event()
    lock = threading.Lock()

    def read(name):
        try:
            stream = getattr(process, name)
            while chunk := stream.read(4096):
                with lock:
                    observed[name] += len(chunk)
                    left = cap - sum(len(value) for value in buffers.values())
                    buffers[name].extend(chunk[:max(0, left)])
                    if len(chunk) > max(0, left):
                        overflow.set()
                        return
        except (OSError, ValueError):
            failures.set()

    threads = [threading.Thread(target=read, args=(name,), daemon=True) for name in buffers]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    stop_reason = None
    pending = None
    try:
        while process.poll() is None:
            if overflow.is_set():
                stop_reason = "process_output_cap"
                break
            if time.monotonic() >= deadline:
                stop_reason = "process_timeout"
                break
            time.sleep(.01)
    except BaseException as error:
        pending = error
    finally:
        if process.poll() is None and (stop_reason is not None or pending is not None):
            terminate_group(process)
        for thread in threads:
            thread.join(timeout=1)
        for name, thread in zip(buffers, threads):
            if not thread.is_alive():
                getattr(process, name).close()
    if pending is not None:
        raise pending
    if overflow.is_set() and stop_reason is None:
        stop_reason = "process_output_cap"
    if stop_reason:
        raise RemoteStop(stop_reason)
    require(not failures.is_set() and not any(thread.is_alive() for thread in threads),
            "process_io")
    diagnostics = {name + "_bytes": observed[name] for name in buffers}
    diagnostics["stderr_present"] = observed["stderr"] > 0
    return process.returncode, bytes(buffers["stdout"]), diagnostics


def checked_parent(path):
    path = Path(path)
    require(path.is_absolute(), "destination_parent")
    for current in reversed((path, *path.parents)):
        try:
            value = current.lstat()
        except OSError:
            raise RemoteStop("destination_parent") from None
        require(stat.S_ISDIR(value.st_mode) and not stat.S_ISLNK(value.st_mode),
                "destination_parent")
    return path


def write_exclusive(path, data, mode):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        raise RemoteStop("destination_write") from None
    require(sha(Path(path).read_bytes()) == sha(data), "destination_write")


def validate_smoke(value):
    require(isinstance(value, dict) and set(value) == {
                "status", "production_db_opened", "services_touched", "scratch_retained", "cases"
            } and value.get("status") == "SYNTHETIC_LINUX_GUARD_PASS" and
            value.get("production_db_opened") is False and value.get("services_touched") is False and
            value.get("scratch_retained") is True, "synthetic_receipt")
    cases = value.get("cases")
    require(isinstance(cases, list) and len(cases) == 3, "synthetic_receipt")
    expected = [("wal", "SHAPE_READ_WRITE_BLOCKED", {"case", "status", "table_count"}),
                ("missing_shm", "EXPECTED_STOP", {"case", "status", "reason"}),
                ("journal", "EXPECTED_STOP", {"case", "status", "reason"})]
    for item, (name, status_name, keys) in zip(cases, expected, strict=True):
        require(isinstance(item, dict) and set(item) == keys and item.get("case") == name and
                item.get("status") == status_name, "synthetic_receipt")
    return cases


def receipt_common():
    return {"schema": "phase16.readback-guard-remote.v1", "destination": DESTINATION,
            "service_actions": 0, "live_database_opened": False,
            "production_source_read": False, "production_units_read": False,
            "runtime_activation": False}


def pass_receipt_for_tests():
    value = receipt_common()
    value.update({"status": "SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE",
                  "payload_sha256": PAYLOAD_SHA256, "core_sha256": CORE_SHA256,
                  "smoke_sha256": SMOKE_SHA256,
                  "cases": [{"case": "wal", "status": "SHAPE_READ_WRITE_BLOCKED", "table_count": 1},
                            {"case": "missing_shm", "status": "EXPECTED_STOP", "reason": "sqlite_sidecars"},
                            {"case": "journal", "status": "EXPECTED_STOP", "reason": "sqlite_journal_present"}],
                  "process": {"stdout_bytes": 0, "stderr_bytes": 0, "stderr_present": False},
                  "completed_at": "2026-09-22T00:00:00+00:00",
                  "scratch_retained": True, "result_persisted": True})
    return value


def stop_receipt(reason, *, retained, persisted):
    require(re.fullmatch(r"[a-z0-9_]{1,80}", reason) is not None, "receipt_reason")
    value = receipt_common()
    if not retained:
        status = "STOP_BEFORE_DESTINATION_NO_RETRY"
        persisted = False
    elif persisted:
        status = "STOP_RETAINED_NO_RETRY"
    else:
        status = "STOP_RETAINED_NO_RECEIPT"
    value.update({"status": status, "reason": reason,
                  "scratch_retained": retained, "result_persisted": persisted})
    return value


def persist_receipt(destination, receipt):
    data = (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode()
    write_exclusive(Path(destination) / "remote-result.json", data, 0o600)


def destination_exists():
    path = Path(DESTINATION)
    return _OWNED_DESTINATION and path.is_dir() and not path.is_symlink()


def install_deadline(seconds=REMOTE_SECONDS):
    require(sys.platform == "linux" and 0 < seconds <= REMOTE_SECONDS, "platform_contract")

    def expired(_signum, _frame):
        raise RemoteStop("remote_timeout")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)


def clear_deadline():
    if hasattr(signal, "setitimer"):
        signal.setitimer(signal.ITIMER_REAL, 0)


def execute(payload):
    global _OWNED_DESTINATION
    require(sys.platform == "linux" and platform.machine() == "x86_64" and
            sys.version_info[:2] == (3, 12) and sqlite3.sqlite_version_info >= (3, 37, 0),
            "platform_contract")
    require(Path("/usr/bin/unshare").is_file() and Path("/usr/bin/mount").is_file(),
            "synthetic_prerequisites")
    parts = parse_payload(payload)
    destination = Path(DESTINATION)
    checked_parent(destination.parent)
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError:
        raise RemoteStop("destination_exists") from None
    except OSError:
        raise RemoteStop("destination_create") from None
    _OWNED_DESTINATION = True
    for name, data in parts.items():
        write_exclusive(destination / name, data, 0o700 if name == SMOKE_NAME else 0o600)
    scratch = destination / "phase16-readback-guard-synthetic"
    command = ["/usr/bin/python3", "-I", "-S", "-B", str(destination / SMOKE_NAME),
               "--scratch-root", str(scratch), "--approve",
               "PHASE16_SYNTHETIC_READBACK_GUARD_ONLY"]
    returncode, output, process = run_bounded(command, timeout=REMOTE_SECONDS, cap=MAX_OUTPUT)
    require(returncode == 0, "synthetic_child")
    try:
        smoke = json.loads(output)
    except (UnicodeError, json.JSONDecodeError):
        raise RemoteStop("synthetic_receipt") from None
    cases = validate_smoke(smoke)
    receipt = pass_receipt_for_tests()
    receipt["cases"] = cases
    receipt["process"] = process
    receipt["completed_at"] = datetime.now(timezone.utc).isoformat()
    return receipt


def main():
    global _OWNED_DESTINATION
    _OWNED_DESTINATION = False
    try:
        install_deadline()
        require(sys.argv[1:] == [APPROVAL], "approval_binding")
        payload = sys.stdin.buffer.read(PAYLOAD_SIZE + 1)
        receipt = execute(payload)
        try:
            persist_receipt(Path(DESTINATION), receipt)
        except RemoteStop:
            receipt = stop_receipt("receipt_persist", retained=True, persisted=False)
        print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
        return 0 if receipt["status"] == "SYNTHETIC_LINUX_GUARD_PASS_NOT_LIVE" else 3
    except RemoteStop as error:
        reason = str(error) if re.fullmatch(r"[a-z0-9_]{1,80}", str(error)) else "remote_gate"
        retained = destination_exists()
        receipt = stop_receipt(reason, retained=retained, persisted=retained)
        if retained:
            try:
                persist_receipt(Path(DESTINATION), receipt)
            except RemoteStop:
                receipt = stop_receipt(reason, retained=True, persisted=False)
        print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    except Exception:
        retained = destination_exists()
        receipt = stop_receipt("remote_exception", retained=retained, persisted=retained)
        if retained:
            try:
                persist_receipt(Path(DESTINATION), receipt)
            except RemoteStop:
                receipt = stop_receipt("remote_exception", retained=True, persisted=False)
        print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    finally:
        clear_deadline()
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
