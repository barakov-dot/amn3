"""Bounded diagnostic transport, not wired to any live gate.

Keeps the proven process/pipe limits from phase16_bot_linux_gate.run_transport
at 66bbc8a. That frozen transport and stage001 retain their original hashes.
Only fixed stderr hints, byte counts/hashes and monotonic timings are returned;
raw output stays in memory. Hints do not establish root cause. No CLI/SSH setup,
target loader, remote command construction, persistence, retry or approval logic.
A future caller needs its own exact manifest and authorization.
"""
import os
import re
import signal
import subprocess
import threading
import time
from scripts.vps import phase16_bot_linux_gate_remote as gate


def classify_stderr(data, *, output_cap_hit):
    """Classify bounded bytes without returning user-controlled strings."""
    if not isinstance(data, bytes) or len(data) > 65536 or type(output_cap_hit) is not bool:
        raise ValueError('stderr_diagnostic_limits')
    markers = (
        (b'Permission denied (publickey)', 'SSH_AUTHENTICATION_HINT'),
        (b'Host key verification failed', 'SSH_HOST_KEY_HINT'),
        (b'SyntaxError:', 'PYTHON_SYNTAX_HINT'),
        (b'Traceback (most recent call last):', 'PYTHON_TRACEBACK_HINT'),
        (b'Connection timed out', 'SSH_CONNECT_TIMEOUT_HINT'),
        (b'Connection refused', 'SSH_CONNECTION_REFUSED_HINT'),
        (b'kex_exchange_identification:', 'SSH_KEX_HINT'),
        (b'banner exchange:', 'SSH_BANNER_HINT'),
        (b'Connection reset', 'SSH_CONNECTION_RESET_HINT'),
        (b'Connection closed', 'SSH_CONNECTION_CLOSED_HINT'),
        (b'Broken pipe', 'SSH_BROKEN_PIPE_HINT'),
        (b'client_loop: send disconnect:', 'SSH_SEND_DISCONNECT_HINT'),
        (b'Software caused connection abort', 'SSH_CONNECTION_ABORT_HINT'),
        (b'No route to host', 'SSH_NO_ROUTE_HINT'),
        (b'Network is unreachable', 'SSH_NETWORK_UNREACHABLE_HINT'),
    )
    hints = [label for marker, label in markers if marker in data]
    if re.search(rb'(?:^|[\r\n])Timeout, server [^\r\n]{1,255} not responding\.', data):
        hints.append('SSH_SERVER_ALIVE_TIMEOUT_HINT')
    try:
        data.decode('utf-8')
        utf8_valid = True
    except UnicodeDecodeError:
        utf8_valid = False
    return dict(status='EMPTY' if not data else 'HINTS_ONLY' if hints else 'UNCLASSIFIED',
                hints=hints, root_cause='NOT_ESTABLISHED', utf8_valid=utf8_valid,
                output_cap_hit=output_cap_hit)


def run_transport(command, *, cwd, env, timeout, cap=65536, input_bytes=b'', diagnostics):
    """Single child; diagnostic metadata only. No retry or target loading."""
    gate.require(0 < timeout <= 330 and 0 < cap <= 65536 and
                 len(input_bytes) <= gate.MAX_BUNDLE + 65544, 'transport_limits')
    started = time.monotonic()
    diagnostics.update(schema='phase16.bot-transport-diagnostic.v1', returncode=None,
                       last_stdin_progress_seconds=None, termination_action='NONE',
                       failure_stage=None, stdin_bytes_requested=len(input_bytes),
                       stdin_bytes_accepted=0, stdin_complete=False, output_complete=False)
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    observed = {'stdout': 0, 'stderr': 0}
    eof = {name: threading.Event() for name in buffers}
    failures = {name: threading.Event() for name in ('stdin_write', 'stdin_close', 'stdout_read', 'stderr_read')}
    overflow = threading.Event()
    lock = threading.Lock()

    def summarize(stage, rc):
        with lock:
            diagnostics.update(returncode=rc, failure_stage=stage,
                               elapsed_seconds=round(time.monotonic()-started, 6),
                               output_complete=all(event.is_set() for event in eof.values()) and not overflow.is_set())
            for name, data in buffers.items():
                diagnostics[name] = {'bytes_observed': observed[name], 'bytes_retained': len(data),
                                     'prefix_sha256': gate.sha(bytes(data))}
            stderr = bytes(buffers['stderr'])
        diagnostics['pipe_failures'] = [name for name, event in failures.items() if event.is_set()]
        diagnostics['stderr_diagnostic'] = classify_stderr(stderr, output_cap_hit=overflow.is_set())


    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   bufsize=0, shell=False, start_new_session=(os.name == 'posix'))
    except OSError:
        diagnostics['termination_action'] = 'NOT_STARTED'
        summarize('start', None)
        raise gate.GateError('transport_start') from None

    def read(name):
        try:
            while chunk := getattr(process, name).read(4096):
                with lock:
                    observed[name] += len(chunk)
                    remaining = cap - sum(len(data) for data in buffers.values())
                    buffers[name].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        overflow.set()
                        return
            eof[name].set()
        except (OSError, ValueError):
            failures[name+'_read'].set()

    def write():
        try:
            data = memoryview(input_bytes)
            accepted = 0
            while accepted < len(data):
                count = process.stdin.write(data[accepted:accepted+32768])
                if not count:
                    raise OSError('zero_write')
                accepted += count
                diagnostics['stdin_bytes_accepted'] = accepted
                diagnostics['last_stdin_progress_seconds'] = round(time.monotonic()-started, 6)
            diagnostics['stdin_complete'] = True
        except (OSError, ValueError):
            failures['stdin_write'].set()
        finally:
            try:
                process.stdin.close()
            except (OSError, ValueError):
                failures['stdin_close'].set()

    threads = [threading.Thread(target=read, args=(name,), daemon=True) for name in buffers]
    threads.append(threading.Thread(target=write, daemon=True))
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    stage = None
    try:
        while process.poll() is None:
            if overflow.is_set():
                stage = 'output_cap'
                break
            if time.monotonic() >= deadline:
                stage = 'timeout'
                break
            time.sleep(.01)
    finally:
        if process.poll() is None:
            diagnostics['termination_action'] = 'KILL_LOCAL_CHILD'
            if os.name == 'posix':
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                stage = 'cleanup_wait'
        for thread in threads:
            thread.join(timeout=1)
        if stage is None:
            stage = ('output_cap' if overflow.is_set() else
                     'unclosed_pipe' if any(t.is_alive() for t in threads) else
                     next((name for name, event in failures.items() if event.is_set()), None))
        # Do not block closing a pipe still owned by a live reader thread.
        for name, thread in zip(buffers, threads):
            if not thread.is_alive():
                getattr(process, name).close()
        summarize(stage, process.returncode)
    if stage is not None:
        raise gate.GateError('transport_'+stage)
    return process.returncode, bytes(buffers['stdout'])
