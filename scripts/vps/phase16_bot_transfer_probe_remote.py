"""Receive synthetic bytes in memory; no files, child processes or application access."""
import hashlib
import json
import signal
import sys

APPROVAL = 'PHASE16_SSH_TRANSFER_DIAGNOSTIC_20260927_001'
SCHEMA = 'phase16.transfer-probe-event.v1'
PAYLOAD_BYTES = 30485208
PAYLOAD_SHA256 = '2be558efdf53a6a0be148ffec0535e3d2a5de583ba365ef6e570a2b7a0de0fd1'
CHECKPOINT = 1048576
REMOTE_SECONDS = 90
REASONS = frozenset({'INPUT_EOF','INPUT_EXTRA','PAYLOAD_HASH','TIME_LIMIT','RECEIVER_FAILURE'})


def receive(stream, output):
    count = 0
    seq = 0
    next_checkpoint = CHECKPOINT
    digest = hashlib.sha256()

    def emit(event, **fields):
        nonlocal seq
        output(dict(schema=SCHEMA, approval=APPROVAL, seq=seq, event=event, bytes=count, **fields))
        seq += 1

    try:
        emit('READY')
        while count < PAYLOAD_BYTES:
            data = stream.read(min(65536, PAYLOAD_BYTES-count, next_checkpoint-count))
            if not data:
                emit('STOP', reason='INPUT_EOF'); return 3
            count += len(data)
            digest.update(data)
            if count == next_checkpoint:
                emit('PROGRESS')
                next_checkpoint += CHECKPOINT
        if stream.read(1):
            emit('STOP', reason='INPUT_EXTRA'); return 3
        if digest.hexdigest() != PAYLOAD_SHA256:
            emit('STOP', reason='PAYLOAD_HASH'); return 3
        emit('COMPLETE', sha256=PAYLOAD_SHA256)
        return 0
    except TimeoutError:
        emit('STOP', reason='TIME_LIMIT'); return 3
    except Exception:
        emit('STOP', reason='RECEIVER_FAILURE'); return 3


def main():
    if sys.argv[1:] != [APPROVAL]:
        return 64
    def timeout(signum, frame):
        raise TimeoutError()
    if sys.platform == 'linux':
        signal.signal(signal.SIGALRM, timeout)
        signal.alarm(REMOTE_SECONDS)
    try:
        return receive(sys.stdin.buffer, lambda value: print(json.dumps(value), flush=True))
    finally:
        if sys.platform == 'linux':
            signal.alarm(0)


if __name__ == '__main__':
    raise SystemExit(main())
