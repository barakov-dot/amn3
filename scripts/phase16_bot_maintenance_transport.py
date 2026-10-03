"""Bounded local transport for one explicitly approved maintenance packet.

This does not construct a command, find a target, authorize SSH, validate a remote
receipt, or retry. The caller supplies an exact command and environment. Killing
or reaping local SSH does NOT stop a manager-owned remote coordinator; preserve
its claim and reconcile manually. Never replay an ambiguous packet.

Derived from the proven threaded pipe mechanics in the frozen diagnostic
transport; that historical transport retains its original 330-second bound.
Here input is <=2MiB, combined retained output <=65536 bytes, total local budget
<=1590s. The final min(3s, timeout/4) is reserved for local kill/reap/join; with
1590s the child I/O deadline is 1587s. OS scheduling/kernel kill latency cannot be
proved by Python; cleanup uncertainty always raises a fixed failure.
"""
import hashlib
import math
import os
import signal
import subprocess
import threading
import time
from scripts.phase16_bot_transport_diagnostics import classify_stderr

MAX_INPUT = 2 * 1024 * 1024
MAX_OUTPUT = 65536
MAX_TIMEOUT = 1590


class TransportError(RuntimeError):
    """Only fixed transport reasons may cross the boundary."""
    CODES = frozenset(('limits', 'start', 'output_cap', 'timeout', 'stdin_write', 'stdin_close',
        'stdout_read', 'stderr_read', 'unclosed_pipe', 'cleanup_kill', 'cleanup_wait',
        'thread_start', 'observer_unsupported', 'incomplete'))

    def __init__(self, reason):
        suffix = reason if type(reason) is str and reason in self.CODES else 'incomplete'
        super().__init__('transport_' + suffix)


def run_transport(command, *, cwd, env, timeout, cap=MAX_OUTPUT, input_bytes=b'',
                  diagnostics, stdout_observer=None):
    """One local child with concurrent pipes and EOF-complete input/output.

    Returns the exit status even if nonzero plus bounded stdout. The caller must
    validate its remote receipt before claiming any maintenance result. Raw stderr
    never leaves this function; diagnostics contain fixed hints/counts/hashes only.
    Non-None stdout observers are rejected before launch: arbitrary callbacks
    cannot satisfy this synchronous bounded transport contract.
    No retry is performed and no diagnostics field grants replay permission.
    """
    if stdout_observer is not None:
        raise TransportError('observer_unsupported')
    valid = (type(timeout) in (int, float) and math.isfinite(timeout) and 0 < timeout <= MAX_TIMEOUT
        and type(cap) is int and 0 < cap <= MAX_OUTPUT and type(input_bytes) is bytes
        and len(input_bytes) <= MAX_INPUT and type(diagnostics) is dict
        and type(command) in (list, tuple) and 0 < len(command) <= 256
        and all(type(v) is str and v and '\x00' not in v for v in command)
        and sum(len(v) for v in command) <= 131072)
    if not valid:
        raise TransportError('limits')
    started = time.monotonic()
    deadline = started + timeout
    io_deadline = deadline - min(3.0, timeout / 4)
    diagnostics.update(schema='phase16.bot-maintenance-transport.v1', returncode=None,
        failure_stage=None, stdin_bytes_requested=len(input_bytes), stdin_bytes_accepted=0,
        stdin_complete=False, output_complete=False, last_stdin_progress_seconds=None,
        termination_action='NONE', termination_scope='LOCAL_TRANSPORT_ONLY',
        local_child_reaped=False, remote_coordinator_status='UNKNOWN_MAY_CONTINUE',
        replay_allowed=False, automatic_retry=False)
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    observed = dict.fromkeys(buffers, 0)
    eof = {name: threading.Event() for name in buffers}
    failures = {name: threading.Event() for name in ('stdin_write', 'stdin_close', 'stdout_read', 'stderr_read')}
    overflow = threading.Event()
    lock = threading.Lock()
    state = dict(accepted=0, stdin_complete=False, last_progress=None)
    process = None
    threads = []

    def summarize(stage):
        with lock:
            diagnostics.update(returncode=None if process is None else process.returncode,
                failure_stage=stage, elapsed_seconds=round(time.monotonic() - started, 6),
                stdin_bytes_accepted=state['accepted'], stdin_complete=state['stdin_complete'],
                last_stdin_progress_seconds=state['last_progress'],
                output_complete=all(v.is_set() for v in eof.values()) and not overflow.is_set()
                    and not failures['stdout_read'].is_set() and not failures['stderr_read'].is_set())
            for name, data in buffers.items():
                diagnostics[name] = dict(bytes_observed=observed[name], bytes_retained=len(data),
                    prefix_sha256=hashlib.sha256(data).hexdigest())
            stderr, stdout = bytes(buffers['stderr']), bytes(buffers['stdout'])
        diagnostics['pipe_failures'] = [name for name, event in failures.items() if event.is_set()]
        diagnostics['stderr_diagnostic'] = classify_stderr(stderr, output_cap_hit=overflow.is_set())
        return stdout

    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, shell=False,
            close_fds=True, start_new_session=(os.name == 'posix'))
    except Exception:
        diagnostics['termination_action'] = 'NOT_STARTED'
        summarize('start')
        raise TransportError('start') from None

    def read(name):
        try:
            while True:
                chunk = getattr(process, name).read(4096)
                if not chunk:
                    eof[name].set()
                    return
                with lock:
                    observed[name] += len(chunk)
                    remaining = cap - sum(len(data) for data in buffers.values())
                    buffers[name].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        overflow.set()
                        return
        except Exception:
            failures[name + '_read'].set()
        finally:
            # If a foreign local descendant outlives the deadline, this owner
            # still closes its descriptor when EOF eventually arrives.
            try:
                getattr(process, name).close()
            except Exception:
                failures[name + '_read'].set()

    def write():
        complete = False
        try:
            data = memoryview(input_bytes)
            accepted = 0
            while accepted < len(data):
                chunk = data[accepted:accepted + 32768]
                count = process.stdin.write(chunk)
                if type(count) is not int or not 0 < count <= len(chunk):
                    raise OSError('short_write')
                accepted += count
                with lock:
                    state['accepted'] = accepted
                    state['last_progress'] = round(time.monotonic() - started, 6)
            complete = True
        except Exception:
            failures['stdin_write'].set()
        finally:
            try:
                process.stdin.close()  # EOF is part of successful complete input.
                with lock:
                    state['stdin_complete'] = complete
            except Exception:
                failures['stdin_close'].set()

    candidates = [threading.Thread(target=read, args=(name,), daemon=True) for name in buffers]
    candidates.append(threading.Thread(target=write, daemon=True))
    stage = None
    try:
        for thread in candidates:
            thread.start()
            threads.append(thread)
        while True:
            if overflow.is_set():
                stage = 'output_cap'
                break
            stage = next((name for name, event in failures.items() if event.is_set()), None)
            if stage is not None:
                break
            if process.poll() is not None and not any(t.is_alive() for t in threads):
                break
            if time.monotonic() >= io_deadline:
                stage = 'timeout'
                break
            time.sleep(min(.01, max(0, io_deadline - time.monotonic())))
    except Exception:
        stage = 'thread_start' if len(threads) < len(candidates) else 'incomplete'
    finally:
        cleanup_deadline = min(deadline, time.monotonic() + min(3.0, timeout / 4))
        # Even when SSH has exited, its POSIX session may still own a pipe.
        # This kills only the session we created, never a remote service.
        if process.poll() is None or (stage is not None and any(t.is_alive() for t in threads)):
            diagnostics['termination_action'] = 'KILL_LOCAL_CHILD'
            try:
                if os.name == 'posix':
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                elif process.poll() is None:
                    process.kill()
            except Exception:
                stage = 'cleanup_kill'
        try:
            process.wait(timeout=max(0.001, cleanup_deadline - time.monotonic()))
            diagnostics['local_child_reaped'] = True
        except Exception:
            stage = 'cleanup_wait'
        for thread in threads:
            thread.join(timeout=max(0, cleanup_deadline - time.monotonic()))
        if any(t.is_alive() for t in threads):
            stage = stage or 'unclosed_pipe'
        if stage is None:
            stage = ('output_cap' if overflow.is_set() else
                     next((name for name, event in failures.items() if event.is_set()), None))
        # Never synchronously close a stream still owned by a blocked thread.
        for index, name in enumerate(('stdout', 'stderr', 'stdin')):
            if candidates[index] not in threads or not candidates[index].is_alive():
                try:
                    getattr(process, name).close()
                except Exception:
                    stage = stage or 'incomplete'
        if stage is None and (not state['stdin_complete'] or not all(v.is_set() for v in eof.values())):
            stage = 'incomplete'
        output = summarize(stage)
    if stage is not None:
        raise TransportError(stage)
    return process.returncode, output
