"""Bounded production read-only integration collector; no application imports."""
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
import types

APPROVAL = "PHASE16_ACTUAL_INTEGRATION_READBACK_20260923_011"
MAGIC = b"P16IRB02"
CORE_SIZE = 24447
MANIFEST_SIZE = 23472
CORE_SHA256 = 'eb81cb68d271d73a08434919c94876f58aa9f04a43a57d4b5caac675be22c21f'
MANIFEST_SHA256 = 'faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4'
PAYLOAD_SIZE = 47943
PAYLOAD_SHA256 = 'c876d261b3e1e5c01ae05f93fdd5ad0934cf7597cf2b06f6108d3af858d76739'
SOURCE_ROOT = Path("/opt/amn2-spain/runtime/source/app")
DEPENDENCY_ROOT = Path("/opt/amn2-spain/runtime/site-packages")
DATABASE = Path("/var/lib/amn2-spain/amn2.sqlite3")
UNITS = {"bot": "amn2-spain-bot.service", "web": "amn2-spain-web.service"}
REMOTE_SECONDS = 50
WORK_SECONDS = 44
CLEANUP_SECONDS = 4
FINALIZATION_SECONDS = 2
MAX_OUTPUT = 65536
MAX_STDERR = 8192
PARTIAL = {}
OUTER_DEADLINE = 0.0
CORE_REASONS = frozenset({
    'dependency_cap', 'dependency_duplicate', 'file_cap', 'file_changed',
    'file_identity', 'file_type', 'linux_guard_unverified', 'manifest_path',
    'manifest_pins', 'manifest_schema', 'manifest_source', 'metadata_encoding',
    'metadata_headers', 'metadata_name', 'metadata_version', 'mount_cap',
    'mount_directory', 'mount_format', 'mount_identity', 'mount_nested',
    'mount_propagation', 'mount_setup', 'mount_writable', 'namespace_identity',
    'namespace_parent', 'output_cap', 'path_link', 'proc_cap', 'proc_stat',
    'schema_cap', 'schema_changed', 'schema_expression_index', 'schema_timeout',
    'schema_transaction', 'schema_unknown', 'schema_virtual', 'source_cap',
    'source_depth', 'source_root', 'sqlite_guard', 'sqlite_journal',
    'sqlite_journal_present', 'sqlite_read', 'sqlite_sidecars', 'sqlite_version',
    'unit_pid', 'unit_properties',
})
STAGES = frozenset({'host', 'units_before', 'source', 'dependencies',
                    'database_files_before', 'database', 'holders',
                    'database_files_after', 'units_after'})
STOP_REASONS = frozenset({
    'approval_binding', 'database_child', 'database_file_changed', 'database_path',
    'file_type', 'host_contract', 'namespace_identity', 'output_cap',
    'partial_summary', 'payload_binding', 'platform_contract', 'process_cleanup',
    'process_contract', 'process_io', 'process_start', 'process_timeout',
    'process_output_cap', 'process_stderr_cap', 'readback_root_changed',
    'receipt_reason', 'remote_timeout', 'unit_file', 'unit_files',
    'unit_identity_drift', 'unit_probe', 'unit_property', 'unit_role',
    'stage_contract', 'remote_gate', 'remote_exception', 'partial_output_cap',
}) | frozenset(stage + '_' + reason for stage in STAGES for reason in
              CORE_REASONS | {'core_stop', 'path_missing', 'permission_denied',
                              'os_error', 'exception'}) | frozenset(
              'database_' + reason for reason in CORE_REASONS | {'payload_binding', 'db_child'})
UNIT_PROPERTIES = (
    "LoadState", "ActiveState", "SubState", "Type", "Restart", "KillMode",
    "MainPID", "TimeoutStartUSec", "TimeoutStopUSec", "WatchdogUSec",
    "KillSignal", "FinalKillSignal", "ExecStart", "WorkingDirectory",
    "ExecStartPre", "ExecStartPost", "ExecStop", "ExecStopPost", "ExecReload",
    "ExecCondition", "FragmentPath", "DropInPaths", "ControlGroup",
)


class RemoteStop(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise RemoteStop(reason)


def at_stage(core, stage, function, *args):
    """Retain fixed classifications, never exception messages or filenames."""
    require(stage in STAGES, 'stage_contract')
    try:
        return function(*args)
    except RemoteStop:
        raise
    except core.Stop as error:
        code = error.args[0] if len(error.args) == 1 else None
        reason = code if type(code) is str and code in CORE_REASONS else 'core_stop'
    except FileNotFoundError:
        reason = 'path_missing'
    except PermissionError:
        reason = 'permission_denied'
    except OSError:
        reason = 'os_error'
    except Exception:
        reason = 'exception'
    raise RemoteStop(stage + '_' + reason) from None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_payload(payload):
    require(type(payload) is bytes and len(payload) == PAYLOAD_SIZE and
            sha(payload) == PAYLOAD_SHA256 and payload[:8] == MAGIC, "payload_binding")
    try:
        core_size = int(payload[8:16])
        manifest_size = int(payload[16:24])
    except ValueError:
        raise RemoteStop("payload_binding") from None
    require((core_size, manifest_size) == (CORE_SIZE, MANIFEST_SIZE), "payload_binding")
    core_data = payload[24:24 + core_size]
    manifest_data = payload[24 + core_size:]
    require(sha(core_data) == CORE_SHA256 and sha(manifest_data) == MANIFEST_SHA256,
            "payload_binding")
    compile(core_data, "phase16_bot_integration_readback.py", "exec")
    try:
        manifest = json.loads(manifest_data)
    except (UnicodeError, json.JSONDecodeError):
        raise RemoteStop("payload_binding") from None
    require(isinstance(manifest, dict) and manifest.get("schema") ==
            "phase16.integration-manifest.v2" and len(manifest.get("source", {})) == 126 and
            len(manifest.get("runtime_pins", {})) == 40 and
            manifest.get("source_commit") == "6e682356ed14a62d636ee58039fd3a389e794809",
            "payload_binding")
    return {"core": core_data, "manifest": manifest}


def load_core(data):
    module = types.ModuleType("phase16_readback_core")
    module.__file__ = "<bound-phase16-readback-core>"
    exec(compile(data, module.__file__, "exec"), module.__dict__)
    return module


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
        process.wait(timeout=1.5)
    except subprocess.TimeoutExpired:
        raise RemoteStop("process_cleanup") from None


def run_bounded(command, *, input_bytes=b"", timeout, cap):
    require(type(command) is list and type(input_bytes) is bytes and
            0 < timeout <= WORK_SECONDS and 0 < cap <= MAX_OUTPUT and
            len(input_bytes) <= 131072, "process_contract")
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE if input_bytes else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True, shell=False,
                                   env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"})
    except OSError:
        raise RemoteStop("process_start") from None
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    observed = {"stdout": 0, "stderr": 0}
    overflow = {"stdout": threading.Event(), "stderr": threading.Event()}
    failure = threading.Event()
    lock = threading.Lock()

    def reader(name):
        try:
            stream = getattr(process, name)
            while chunk := stream.read(4096):
                with lock:
                    observed[name] += len(chunk)
                    limit = cap if name == "stdout" else MAX_STDERR
                    left = limit - len(buffers[name])
                    buffers[name].extend(chunk[:max(0, left)])
                    if len(chunk) > max(0, left):
                        overflow[name].set()
                        return
        except (OSError, ValueError):
            failure.set()

    threads = [threading.Thread(target=reader, args=(name,), daemon=True) for name in buffers]
    for thread in threads:
        thread.start()
    pending = None
    stop_reason = None
    try:
        if input_bytes:
            process.stdin.write(input_bytes)
            process.stdin.close()
        deadline = time.monotonic() + timeout
        while process.poll() is None:
            if overflow["stdout"].is_set() or overflow["stderr"].is_set():
                stop_reason = ("process_stderr_cap" if overflow["stderr"].is_set()
                               else "process_output_cap")
                break
            if time.monotonic() >= deadline:
                stop_reason = "process_timeout"
                break
            time.sleep(.01)
    except BaseException as error:
        pending = error
    finally:
        if process.poll() is None and (pending is not None or stop_reason is not None):
            terminate_group(process)
        for thread in threads:
            thread.join(timeout=.75)
        for name, thread in zip(buffers, threads):
            if not thread.is_alive():
                getattr(process, name).close()
    if pending is not None:
        raise pending
    if stop_reason is None and (overflow["stdout"].is_set() or overflow["stderr"].is_set()):
        stop_reason = ("process_stderr_cap" if overflow["stderr"].is_set()
                       else "process_output_cap")
    if stop_reason:
        raise RemoteStop(stop_reason)
    require(not failure.is_set() and not any(thread.is_alive() for thread in threads), "process_io")
    return process.returncode, bytes(buffers["stdout"]), {
        "stdout_bytes": observed["stdout"], "stderr_bytes": observed["stderr"],
        "stderr_present": observed["stderr"] > 0,
    }


def unit_command(name, property_name):
    require(name in UNITS.values(), "unit_role")
    require(property_name in UNIT_PROPERTIES, "unit_property")
    return ["/usr/bin/systemctl", "show", "--no-pager", "--value",
            "--property=" + property_name, name]


def unit_probe_stop(role, property_name, stage, returncode=-1,
                    stdout_bytes=0, stderr_bytes=0):
    require(role in UNITS and property_name in UNIT_PROPERTIES and
            stage in {"command", "decode", "format", "process_timeout",
                      "process_output_cap", "process_stderr_cap", "process_io"} and
            type(returncode) is int and -255 <= returncode <= 255 and
            type(stdout_bytes) is int and 0 <= stdout_bytes <= 8192 and
            type(stderr_bytes) is int and 0 <= stderr_bytes <= MAX_STDERR,
            "unit_probe")
    PARTIAL["unit_probe"] = {
        "role": role, "property": property_name, "stage": stage,
        "returncode": returncode, "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
    }
    raise RemoteStop("unit_property")


def fixed_unit_file(path):
    path = Path(path)
    require(path.is_absolute() and not path.is_symlink() and
            any(path == root or root in path.parents for root in
                (Path("/etc/systemd/system"), Path("/usr/lib/systemd/system"))),
            "unit_file")
    return path


def collect_unit(core, role):
    values = {}
    for key in UNIT_PROPERTIES:
        try:
            returncode, output, diagnostics = run_bounded(
                unit_command(UNITS[role], key), timeout=0.75, cap=8192)
        except RemoteStop as error:
            stage = str(error)
            if stage not in {"process_timeout", "process_output_cap",
                             "process_stderr_cap", "process_io"}:
                stage = "process_io"
            unit_probe_stop(role, key, stage)
        if returncode != 0 or diagnostics["stderr_bytes"] != 0:
            unit_probe_stop(role, key, "command", returncode,
                            diagnostics["stdout_bytes"], diagnostics["stderr_bytes"])
        if output == b"":
            values[key] = ""
        else:
            try:
                text = output.decode("utf-8")
            except UnicodeError:
                unit_probe_stop(role, key, "decode", returncode,
                                diagnostics["stdout_bytes"], diagnostics["stderr_bytes"])
            if not text.endswith("\n") or "\n" in text[:-1] or "\r" in text:
                unit_probe_stop(role, key, "format", returncode,
                                diagnostics["stdout_bytes"], diagnostics["stderr_bytes"])
            values[key] = text[:-1]
    normalized = core.parse_unit("\n".join(
        f"{key}={values[key]}" for key in UNIT_PROPERTIES
        if key not in {"FragmentPath", "DropInPaths", "ControlGroup"}), role)
    paths = []
    if values["FragmentPath"]:
        paths.append(fixed_unit_file(values["FragmentPath"]))
    if values["DropInPaths"]:
        for item in values["DropInPaths"].split(" "):
            require(item and len(paths) < 9, "unit_files")
            paths.append(fixed_unit_file(item))
    digests = [sha(core.safe_read(path, 65536)) for path in paths]
    normalized["unit_file_count"] = len(paths)
    normalized["unit_files_digest"] = sha(json.dumps(sorted(digests)).encode())
    expected_cgroup = "/system.slice/" + UNITS[role]
    normalized["cgroup_matches"] = values["ControlGroup"] == expected_cgroup
    pid = normalized["pid"]
    normalized["start_ticks"] = core.start_ticks(Path("/proc") / str(pid) / "stat") if pid else None
    return normalized


def collect_units(core):
    return {role: collect_unit(core, role) for role in ("bot", "web")}


def database_files(core):
    parent = core.checked_path(DATABASE.parent)
    require(parent.is_dir(), "database_path")
    result = {}
    identities = {}
    for key, suffix in (("database", ""), ("wal", "-wal"), ("shm", "-shm"), ("journal", "-journal")):
        path = DATABASE.with_name(DATABASE.name + suffix)
        if not os.path.lexists(path):
            result[key] = {"present": False}
            continue
        path = core.checked_path(path)
        value = path.stat()
        require(stat.S_ISREG(value.st_mode), "file_type")
        result[key] = {"present": True, "device": value.st_dev,
                       "inode": value.st_ino, "bytes": value.st_size}
        identities[key] = core.identity(value)
    require(result["database"]["present"], "database_path")
    return result, identities


def stable_roots(before, after):
    require(set(before) == set(after), "readback_root_changed")
    for key in before:
        left, right = before[key], after[key]
        require(left["present"] == right["present"], "database_file_changed")
        if left["present"]:
            require((left["device"], left["inode"]) == (right["device"], right["inode"]),
                    "database_file_changed")
    return before == after


def stable_collect(core, root, collector, *args):
    path = core.checked_path(root)
    before = path.stat()
    result = collector(path, *args)
    after = core.checked_path(root).stat()
    require(core.identity(before) == core.identity(after) and
            before.st_mtime_ns == after.st_mtime_ns, "readback_root_changed")
    return result


CHILD_BOOTSTRAP = r'''import hashlib,json,os,sys,types
p=sys.stdin.buffer.read(47944)
def stop(r): print(json.dumps({'schema':'phase16.integration-db-child.v1','status':'STOP','reason':r},sort_keys=True,separators=(',',':')));sys.exit(3)
if len(p)!=47943 or hashlib.sha256(p).hexdigest()!='c876d261b3e1e5c01ae05f93fdd5ad0934cf7597cf2b06f6108d3af858d76739' or p[:8]!=b'P16IRB02': stop('payload_binding')
c=int(p[8:16]);m=int(p[16:24])
if (c,m)!=(24447,23472): stop('payload_binding')
core=p[24:24+c]; manifest=p[24+c:]
if hashlib.sha256(core).hexdigest()!='eb81cb68d271d73a08434919c94876f58aa9f04a43a57d4b5caac675be22c21f' or hashlib.sha256(manifest).hexdigest()!='faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4': stop('payload_binding')
mod=types.ModuleType('phase16_readback_core');mod.__file__='<bound-phase16-readback-core>'
try:
 exec(compile(core,mod.__file__,'exec'),mod.__dict__); man=json.loads(manifest); parent=sys.argv[1]
 mod.prepare_readonly_view('/var/lib/amn2-spain',parent)
 result=mod.read_database('/var/lib/amn2-spain/amn2.sqlite3',man['schema_allowlist'],parent)
 print(mod.encode_result({'schema':'phase16.integration-db-child.v1','status':'PASS','database':result}).decode())
except mod.Stop as e: stop(str(e) if __import__('re').fullmatch('[a-z0-9_]{1,80}',str(e)) else 'db_child')
except Exception: stop('db_child')'''


def db_child_command(parent_ns):
    require(re.fullmatch(r"mnt:\[[0-9]+\]", parent_ns), "namespace_identity")
    return ["/usr/bin/unshare", "--mount", "--net", "--propagation", "private",
            "/usr/bin/python3", "-I", "-S", "-B", "-c", CHILD_BOOTSTRAP, parent_ns]


def collect_database(payload):
    parent_ns = os.readlink("/proc/self/ns/mnt")
    returncode, output, process = run_bounded(db_child_command(parent_ns), input_bytes=payload,
                                             timeout=5, cap=MAX_OUTPUT)
    require(returncode in (0, 3) and process["stderr_bytes"] == 0, "database_child")
    try:
        value = json.loads(output)
    except (UnicodeError, json.JSONDecodeError):
        raise RemoteStop("database_child") from None
    if returncode == 3:
        require(isinstance(value, dict) and set(value) == {'schema', 'status', 'reason'} and
                value.get('schema') == 'phase16.integration-db-child.v1' and
                value.get('status') == 'STOP' and type(value.get('reason')) is str and
                value['reason'] in CORE_REASONS | {'payload_binding', 'db_child'},
                'database_child')
        raise RemoteStop('database_' + value['reason'])
    require(isinstance(value, dict) and set(value) == {"schema", "status", "database"} and
            value.get("schema") == "phase16.integration-db-child.v1" and
            value.get("status") == "PASS" and isinstance(value.get("database"), dict),
            "database_child")
    return value["database"], process


def host_receipt(core):
    resolved_python = Path("/usr/bin/python3").resolve(strict=True)
    require(resolved_python.parent == Path("/usr/bin") and
            re.fullmatch(r"python3(?:\.[0-9]+)?", resolved_python.name), "host_contract")
    python = core.checked_path(resolved_python).stat()
    require(stat.S_ISREG(python.st_mode) and Path("/usr/bin/unshare").is_file() and
            Path("/usr/bin/mount").is_file(), "host_contract")
    return {"system": platform.system(), "machine": platform.machine(),
            "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
            "python_device": python.st_dev, "python_inode": python.st_ino}


def pass_receipt_for_tests():
    return {"schema": "phase16.integration-readback-remote.v2",
            "status": "READBACK_COMPLETE_WITH_LIMITATIONS",
            "host": {}, "units_before": {}, "source": {}, "dependencies": {},
            "database_files": {}, "database": {"status": "SHAPE_ONLY"}, "database_child": {},
            "holders": {}, "units_after": {}, "unit_identity_stable": True,
            "service_actions": 0, "database_write_attempted": False,
            "application_imported": False, "production_source_read": True,
            "production_units_read": True, "runtime_activation": False,
            "completed_at": "2026-09-22T00:00:00+00:00",
            "limitations": ["STATIC_SOURCE_SCOPE_ONLY", "STATIC_DEPENDENCY_METADATA_ONLY",
                            "SCHEMA_SHAPE_ONLY", "RUNTIME_BINDING_UNKNOWN",
                            "WRITER_COMPLETENESS_UNKNOWN", "SEMANTIC_COMPATIBILITY_UNKNOWN"]}


def execute(payload):
    global PARTIAL
    PARTIAL = {}
    require(sys.platform == "linux" and platform.machine() == "x86_64" and
            sys.version_info[:2] == (3, 12) and sqlite3.sqlite_version_info >= (3, 37, 0),
            "platform_contract")
    parts = parse_payload(payload)
    core = load_core(parts["core"])
    manifest = parts["manifest"]
    host = at_stage(core, 'host', host_receipt, core)
    PARTIAL["host"] = host
    units_before = at_stage(core, 'units_before', collect_units, core)
    PARTIAL["units_before"] = units_before
    source = at_stage(core, 'source', stable_collect, core, SOURCE_ROOT,
                      core.collect_source, manifest["source"])
    PARTIAL["source"] = source
    dependencies = at_stage(core, 'dependencies', stable_collect, core, DEPENDENCY_ROOT,
                            core.collect_dependencies, manifest["runtime_pins"])
    PARTIAL["dependencies"] = dependencies
    files_before, identities = at_stage(core, 'database_files_before', database_files, core)
    PARTIAL["database_files_before"] = files_before
    database, child = at_stage(core, 'database', collect_database, payload)
    PARTIAL["database"] = database
    PARTIAL["database_child"] = child
    holders = at_stage(core, 'holders', core.collect_holders, "/proc", identities,
        {item["pid"]: (role, item["start_ticks"]) for role, item in units_before.items()
         if item["pid"] and item["start_ticks"] is not None})
    PARTIAL["holders"] = holders
    files_after, _ = at_stage(core, 'database_files_after', database_files, core)
    sizes_stable = stable_roots(files_before, files_after)
    units_after = at_stage(core, 'units_after', collect_units, core)
    PARTIAL["units_after"] = units_after
    stable = all((units_before[role]["pid"], units_before[role]["start_ticks"]) ==
                 (units_after[role]["pid"], units_after[role]["start_ticks"])
                 for role in UNITS)
    require(stable, "unit_identity_drift")
    receipt = pass_receipt_for_tests()
    receipt.update({"host": host, "units_before": units_before, "source": source,
                    "dependencies": dependencies,
                    "database_files": {"before": files_before, "after": files_after,
                                       "sizes_stable": sizes_stable},
                    "database": database, "database_child": child, "holders": holders,
                    "units_after": units_after, "unit_identity_stable": stable,
                    "completed_at": datetime.now(timezone.utc).isoformat()})
    return receipt


def stop_receipt(reason, partial=None):
    require(re.fullmatch(r"[a-z0-9_]{1,80}", reason), "receipt_reason")
    return {"schema": "phase16.integration-readback-remote.v2", "status": "STOP_NO_RETRY",
            "reason": reason, "service_actions": 0, "database_write_attempted": False,
            "application_imported": False, "runtime_activation": False,
            "partial": partial if isinstance(partial, dict) else {}}


def partial_summary(value):
    require(isinstance(value, dict), "partial_summary")
    return {"stages": sorted(value),
            "digests": {name: sha(json.dumps(item, sort_keys=True,
                                             separators=(",", ":")).encode())
                        for name, item in sorted(value.items())}}


def install_deadline():
    global OUTER_DEADLINE
    OUTER_DEADLINE = time.monotonic() + REMOTE_SECONDS
    def expired(_signum, _frame):
        raise RemoteStop("remote_timeout")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, WORK_SECONDS)


def arm_finalization():
    remaining = OUTER_DEADLINE - time.monotonic()
    if remaining <= 0:
        os._exit(124)
    seconds = min(FINALIZATION_SECONDS, remaining)
    signal.signal(signal.SIGALRM, lambda _signum, _frame: os._exit(124))
    signal.setitimer(signal.ITIMER_REAL, seconds)


def main():
    try:
        install_deadline()
        require(sys.argv[1:] == [APPROVAL], "approval_binding")
        payload = sys.stdin.buffer.read(PAYLOAD_SIZE + 1)
        receipt = execute(payload)
        arm_finalization()
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        require(len(encoded.encode()) <= MAX_OUTPUT, "output_cap")
        print(encoded, flush=True)
        return 0
    except RemoteStop as error:
        arm_finalization()
        code = error.args[0] if len(error.args) == 1 else None
        reason = code if type(code) is str and code in STOP_REASONS else "remote_gate"
        receipt = stop_receipt(reason, PARTIAL)
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        if len(encoded.encode()) > MAX_OUTPUT:
            encoded = json.dumps(stop_receipt("partial_output_cap",
                                              {"summary": partial_summary(PARTIAL)}), sort_keys=True,
                                 separators=(",", ":"))
        print(encoded, flush=True)
    except Exception:
        arm_finalization()
        receipt = stop_receipt("remote_exception", PARTIAL)
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        if len(encoded.encode()) > MAX_OUTPUT:
            encoded = json.dumps(stop_receipt("partial_output_cap",
                                              {"summary": partial_summary(PARTIAL)}), sort_keys=True,
                                 separators=(",", ":"))
        print(encoded, flush=True)
    finally:
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, 0)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
