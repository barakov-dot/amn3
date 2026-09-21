"""Fixed candidate, isolated Linux tests only. Import has no side effects."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import threading
import time
import xml.etree.ElementTree as ET
import zipfile

ARTIFACT_ID = 'phase16-bot-candidate-20260921-6e68235-001'
BUNDLE_SHA = 'e19abc5c132acae035503267d41d38fdd1e272951b2ebfd0f2a73e2f7c660cb7'
BUNDLE_SIZE = 30485208
MANIFEST_SHA = '6792cb2cd28b0ce70ae031cac04b29f40db908f5e8bad0770e689de390a9a37d'
SOURCE_SHA = '6e682356ed14a62d636ee58039fd3a389e794809'
DESTINATION = Path('/opt/amn2-spain/bot-candidates') / ARTIFACT_ID
APPROVAL = 'PHASE16_ISOLATED_LINUX_TEST_6e68235_001'
MAX_BUNDLE = 64 * 1024 * 1024
MAX_UNPACKED = 128 * 1024 * 1024
MAX_OUTPUT = 256 * 1024


class GateError(RuntimeError):
    """Fixed, secret-free reason only."""


def require(condition, reason):
    if not condition:
        raise GateError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    require(isinstance(name, str) and bool(name), 'archive_path')
    require('\\' not in name and ':' not in name and '\x00' not in name, 'archive_path')
    require(not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')), 'archive_path')
    require(str(PurePosixPath(name)) == name, 'archive_path')
    return name


def zip_inventory(data, maximum=MAX_UNPACKED):
    result = {}
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        require(len(archive.infolist()) <= 5000, 'archive_size')
        for member in archive.infolist():
            name = safe_name(member.filename)
            mode = member.external_attr >> 16
            require(not member.is_dir() and stat.S_IFMT(mode) in (0, stat.S_IFREG), 'archive_type')
            require(name not in result, 'archive_duplicate')
            total += member.file_size
            require(total <= maximum and not member.flag_bits & 1, 'archive_size')
            result[name] = archive.read(member)
    return result


def tar_inventory(data):
    result, seen, total = {}, set(), 0
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        for member in archive:
            require(member.isdir() or member.isfile(), 'archive_type')
            name = safe_name(member.name.rstrip('/') if member.isdir() else member.name)
            require(name not in seen, 'archive_duplicate')
            seen.add(name)
            require(len(seen) <= 5000, 'archive_size')
            if member.isfile():
                total += member.size
                require(total <= MAX_UNPACKED, 'archive_size')
                result[name] = archive.extractfile(member).read()
    return result


def validate_bundle(data):
    require(len(data) == BUNDLE_SIZE and sha(data) == BUNDLE_SHA, 'bundle_binding')
    payload = zip_inventory(data)
    require('manifest.json' in payload and sha(payload['manifest.json']) == MANIFEST_SHA, 'manifest_binding')
    manifest = json.loads(payload['manifest.json'])
    require(manifest['source_commit'] == SOURCE_SHA and manifest['artifact_id'] == ARTIFACT_ID, 'source_binding')
    expected = {'manifest.json'}
    items = [manifest['source'], manifest['test_support'], *manifest['wheels'], *manifest['auxiliary']]
    for item in items:
        name = safe_name(item['file'])
        require(name not in expected and name in payload, 'payload_inventory')
        expected.add(name)
        require(len(payload[name]) == item['size'] and sha(payload[name]) == item['sha256'], 'payload_binding')
    require(set(payload) == expected, 'payload_inventory')
    source = {}
    for item in (manifest['source'], manifest['test_support']):
        contents = tar_inventory(payload[item['file']])
        entries = {e['path']: e for e in item['entries']}
        require(set(contents) == set(entries), 'source_inventory')
        for name, body in contents.items():
            require(name not in source, 'source_duplicate')
            require(len(body) == entries[name]['size'] and sha(body) == entries[name]['sha256'], 'source_binding')
            source[name] = body
    require(sum(len(body) for body in source.values()) <= MAX_UNPACKED, 'archive_size')
    return payload, source, manifest


def claim_directory(root):
    try:
        root.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise GateError('destination_exists') from exc


def clean_environment(root):
    return {'PATH': '/usr/bin:/bin', 'HOME': str(root), 'TMPDIR': str(root),
            'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1',
            'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'VPS_APPLY_ENABLED': 'false',
            'AWG3_BOOTSTRAP_ENABLED': 'false', 'OPERATOR_DEVICE_CREATE_ENABLED': 'false',
            'PIP_CONFIG_FILE': '/dev/null', 'PIP_NO_INDEX': '1'}


def run_process(command, *, cwd, env, timeout, cap=MAX_OUTPUT, input_bytes=b''):
    require(0 < timeout <= 330 and 0 < cap <= MAX_OUTPUT and len(input_bytes) <= MAX_BUNDLE + 65544, 'process_limits')
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=(os.name == 'posix'), shell=False)
    output = bytearray()
    overflow, io_error = threading.Event(), threading.Event()

    def read():
        try:
            while chunk := process.stdout.read(4096):
                if len(output) + len(chunk) > cap:
                    overflow.set()
                    return
                output.extend(chunk)
        except (OSError, ValueError):
            io_error.set()

    def write():
        try:
            process.stdin.write(input_bytes)
            process.stdin.flush()
        except (OSError, ValueError):
            io_error.set()
        finally:
            process.stdin.close()

    reader = threading.Thread(target=read, daemon=True)
    writer = threading.Thread(target=write, daemon=True)
    reader.start(); writer.start()
    started = time.monotonic()
    def terminate_owned():
        if os.name == 'posix':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        process.wait(timeout=3)
    try:
        while process.poll() is None:
            require(not overflow.is_set(), 'process_output_cap')
            require(time.monotonic() - started < timeout, 'process_timeout')
            time.sleep(.02)
        reader.join(timeout=1); writer.join(timeout=1)
        require(not overflow.is_set(), 'process_output_cap')
        require(not reader.is_alive() and not writer.is_alive(), 'process_unclosed_pipe')
        require(not io_error.is_set(), 'process_io')
        return process.returncode, bytes(output)
    except BaseException:
        terminate_owned()
        reader.join(timeout=1); writer.join(timeout=1)
        raise
    finally:
        if process.poll() is None:
            terminate_owned()
        process.stdout.close()


def negative_helper(text):
    anchor = '    class Controller(StopController):\n'
    require(text.count(anchor) == 1, 'negative_anchor')
    return text.replace(anchor, anchor + '        def attach(self, loop):\n'
                        '            self._pending = False\n'
                        '            super().attach(loop)\n\n', 1)


def check_junit(path, *, negative):
    require(path.is_file() and path.stat().st_size <= MAX_OUTPUT, 'junit_size')
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.findall('testsuite'))
    require(len(suites) == 1, 'junit_counts')
    suite = suites[0]
    expected = {'tests': 1 if negative else 6, 'failures': 1 if negative else 0, 'errors': 0, 'skipped': 0}
    require(all(suite.get(k) == str(v) for k, v in expected.items()), 'junit_counts')
    cases = suite.findall('testcase')
    require(len(cases) == expected['tests'], 'junit_counts')
    require(len(suite.findall('.//failure')) == expected['failures'] and not suite.findall('.//error') and not suite.findall('.//skipped'), 'junit_counts')
    if negative:
        failure = suite.find('.//failure')
        require('Invalid synthetic trace order' in ''.join(failure.itertext()), 'negative_reason')
    return {'passed': 0 if negative else 6, 'expected_failure': negative}


def write_tree(root, entries):
    root.mkdir(mode=0o700)
    for name, body in entries.items():
        path = root / safe_name(name)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open('xb') as stream:
            stream.write(body)


def verify_tree(root, entries):
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual == set(entries), 'source_after_test')
    require(all(not (root/n).is_symlink() and sha((root/n).read_bytes()) == sha(b) for n,b in entries.items()), 'source_after_test')


def precheck_parent():
    for parent in (Path('/opt'), Path('/opt/amn2-spain')):
        metadata = parent.lstat()
        require(stat.S_ISDIR(metadata.st_mode) and metadata.st_uid in (0, os.geteuid()) and not metadata.st_mode & 0o022, 'unsafe_parent')
    parent = DESTINATION.parent
    if parent.exists() or parent.is_symlink():
        metadata = parent.lstat()
        require(stat.S_ISDIR(metadata.st_mode) and metadata.st_uid in (0, os.geteuid()) and not metadata.st_mode & 0o022, 'unsafe_parent')
    require(not DESTINATION.exists() and not DESTINATION.is_symlink(), 'destination_exists')
    require(shutil.disk_usage('/opt/amn2-spain').free >= 512*1024*1024, 'disk_space')


def execute(data):
    # Platform, exact bytes, nofollow parent and exclusivity all precede writes.
    require(sys.platform == 'linux' and sys.version_info[:2] == (3,12), 'platform_python')
    require(platform.machine() == 'x86_64' and platform.libc_ver() == ('glibc','2.39'), 'platform_abi')
    payload, source, manifest = validate_bundle(data)
    precheck_parent()
    import importlib.util
    require(all(importlib.util.find_spec(name) is not None for name in ('venv','ensurepip')), 'venv_unavailable')
    unshare = Path('/usr/bin/unshare')
    require(unshare.is_file(), 'network_namespace_unavailable')
    rc, _ = run_process([str(unshare),'--net','/usr/bin/true'],cwd='/opt/amn2-spain',env=clean_environment(Path('/nonexistent')),timeout=5)
    require(rc == 0, 'network_namespace_unavailable')
    DESTINATION.parent.mkdir(mode=0o700, exist_ok=True)
    claim_directory(DESTINATION)
    result = {'schema':'phase16.bot-linux-gate.v1','artifact_id':ARTIFACT_ID,'bundle_sha256':BUNDLE_SHA,
              'source_commit':SOURCE_SHA,'status':'UNKNOWN','service_actions':0,'live_database_opened':False,
              'telegram_polling':False,'runtime_activation':False,'steps':[]}
    started = time.monotonic()
    try:
        (DESTINATION/'claim.json').write_text(json.dumps({'attempt':1,'scope':APPROVAL,'bundle_sha256':BUNDLE_SHA})+'\n')
        payload_dir, source_dir = DESTINATION/'payload', DESTINATION/'source'
        write_tree(payload_dir, payload); write_tree(source_dir, source)
        scratch = DESTINATION/'scratch'; scratch.mkdir(mode=0o700)
        env = clean_environment(scratch)
        venv = DESTINATION/'test-venv'; python = venv/'bin/python'
        deadline = started + 290

        def run(label, args, timeout, expected=0):
            remaining = deadline-time.monotonic()
            require(remaining > 0, 'wall_cap')
            rc, output = run_process([str(unshare),'--net',*map(str,args)],cwd=scratch,env=env,timeout=min(timeout,remaining))
            result['steps'].append({'step':label,'returncode':rc,'output_bytes':len(output),'output_sha256':sha(output)})
            require(rc == expected, label+'_exit')
            return output

        run('venv',['/usr/bin/python3','-I','-B','-m','venv',str(venv)],45)
        run('offline_install',[python,'-I','-B','-m','pip','--isolated','--disable-pip-version-check','--no-cache-dir','install',
            '--no-index','--require-hashes','--only-binary=:all:','--find-links',payload_dir/'wheelhouse/runtime',
            '--find-links',payload_dir/'wheelhouse/test-only','-r',payload_dir/'requirements/phase15-test-py312.lock'],100)
        run('pip_check',[python,'-I','-B','-m','pip','--isolated','check'],15)
        metadata_code = ('import importlib.metadata as m,json,sys; from pathlib import Path; '
            'print(json.dumps({"isolated":sys.prefix!=sys.base_prefix,"packages":[[d.metadata["Name"],d.version,'
            'Path(d.locate_file("")).resolve().is_relative_to(Path(sys.prefix).resolve())] for d in m.distributions()]}))')
        metadata = json.loads(run('metadata',[python,'-I','-B','-c',metadata_code],15))
        expected = {w['name']:w['version'] for w in manifest['wheels']}
        installed = {}
        for name, version, inside in metadata['packages']:
            name = re.sub(r'[-_.]+','-',name).lower()
            require(inside and name not in installed, 'dependency_origin')
            installed[name] = version
        require(metadata['isolated'] and all(installed.get(n)==v for n,v in expected.items()), 'dependency_binding')
        require(set(installed)-set(expected) <= {'pip','setuptools'}, 'dependency_extra')

        negative_dir = DESTINATION/'negative-source'
        negative = dict(source)
        helper = 'tests/bot/lifecycle_signal_child.py'
        negative[helper] = negative_helper(source[helper].decode('utf-8')).encode('utf-8')
        negative['test_pending_negative.py'] = (
            'import signal\nfrom tests.bot.test_lifecycle_signals import run_owned_child\n'
            'def test_pending_delivery_negative(tmp_path):\n'
            '    run_owned_child(tmp_path, signal.SIGTERM, "PRE_LOOP")\n').encode()
        write_tree(negative_dir, negative)
        bootstrap = 'import sys; sys.path.insert(0,sys.argv.pop(1)); import pytest; raise SystemExit(pytest.main(sys.argv[1:]))'
        def pytest_args(directory, selector, label):
            return [python,'-I','-B','-c',bootstrap,directory,str(directory/selector),'-q','--tb=short','--maxfail=1',
                    '-p','no:cacheprovider','--rootdir='+str(directory),'--confcutdir='+str(directory),
                    '--basetemp='+str(scratch/(label+'-temp')),'--junitxml='+str(scratch/(label+'.xml'))]
        run('negative',pytest_args(negative_dir,'test_pending_negative.py','negative'),25,expected=1)
        result['negative'] = check_junit(scratch/'negative.xml',negative=True)
        verify_tree(source_dir,source)
        run('green',pytest_args(source_dir,'tests/bot/test_lifecycle_signals.py','green'),95)
        result['green'] = check_junit(scratch/'green.xml',negative=False)
        verify_tree(source_dir,source)
        result['status'] = 'ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED'
    except BaseException as exc:
        result['status'] = 'STOP_RETAINED_NO_RETRY'
        result['reason'] = str(exc) if isinstance(exc,GateError) else type(exc).__name__
    finally:
        result['seconds'] = round(time.monotonic()-started,3)
        (DESTINATION/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    def alarm(signum, frame):
        raise GateError('wall_cap')
    if sys.platform == 'linux':
        signal.signal(signal.SIGALRM,alarm); signal.alarm(290)
    try:
        require(sys.argv[1:] == [APPROVAL], 'approval_argument')
        data = sys.stdin.buffer.read(MAX_BUNDLE+1)
        require(len(data) <= MAX_BUNDLE,'bundle_size')
        result = execute(data)
    except BaseException as exc:
        result = {'schema':'phase16.bot-linux-gate.v1','status':'STOP_BEFORE_GATE_OR_UNKNOWN',
                  'reason':str(exc) if isinstance(exc,GateError) else type(exc).__name__}
    finally:
        if sys.platform == 'linux': signal.alarm(0)
    print(json.dumps(result),flush=True)
    return 0 if result['status']=='ISOLATED_LINUX_SIGNALS_PASS_NOT_DEPLOYED' else 3


if __name__ == '__main__':
    raise SystemExit(main())
