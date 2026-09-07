"""Pure, serialized d1 ownership model; NOT a native DNS adapter or live runner.

Time and completion facts are supplied by an offline trace. Effects are symbolic
decisions, never executed here. In particular callback_exit and cleanup_done
need independent native evidence before this policy could inform a live bridge.
No imports, threads, processes, clocks, sockets, file IO or native handles.
"""

_REPLY_FIELDS = {"status", "record_count", "answer_a_count", "records_owned"}
_EVENT_FIELDS = {
    "dispatch": set(), "api_pending": set(), "api_sync": _REPLY_FIELDS,
    "callback_result": _REPLY_FIELDS, "callback_exit": set(),
    "cancel": set(), "cancel_return": set(), "tick": set(),
    "cleanup_done": {"ok"}, "invalid_input": set(),
}
_STATUSES = {"success", "nxdomain", "no_data", "server_error", "native_timeout",
             "start_error", "canceled"}


def _require(condition):
    if not condition:
        raise ValueError("invalid_dns_trace")


def _validate(events, sequence):
    _require(type(sequence) is int and 1 <= sequence <= 5)
    _require(type(events) is list and len(events) <= 64)
    previous = 0
    for item in events:
        _require(type(item) is dict)
        kind = item.get("kind")
        _require(type(kind) is str and kind in _EVENT_FIELDS)
        _require(set(item) == {"kind", "at_ms"} | _EVENT_FIELDS[kind])
        now = item["at_ms"]
        _require(type(now) is int and previous <= now <= 60000)
        previous = now
        if kind in ("api_sync", "callback_result"):
            _require(type(item["status"]) is str and item["status"] in _STATUSES)
            for key in ("record_count", "answer_a_count"):
                _require(type(item[key]) is int and 0 <= item[key] <= 65535)
            _require(item["answer_a_count"] <= item["record_count"])
            _require(type(item["records_owned"]) is bool)
            _require(item["records_owned"] or item["record_count"] == 0)
        if kind == "cleanup_done":
            _require(type(item["ok"]) is bool)


def replay(events, *, sequence=1):
    """Evaluate <=64 normalized events; reject unknown/raw fields without echo.

    Same-time races follow supplied order. The model tests event interleavings,
    not OS-thread synchronization. No success is published before a cleanup ACK.
    A STOP at 2000ms is sticky even if a later trace proves safe resource release.
    Deadlines are observed only on supplied events, not autonomous timers.
    """
    _validate(events, sequence)
    dispatched_at = api_mode = response = terminal_at = total_elapsed = None
    callback_active = callback_finished = False
    cancel_requested = cancel_sent = cancel_returned = free_requested = False
    cleanup_done = cleanup_failed = stopped = deadline_exceeded = False
    early_outcome = None
    effects = []

    def emit(kind, now):
        effects.append({"kind": kind, "at_ms": now})

    def accept_cancel(now):
        nonlocal cancel_requested, terminal_at
        if response is None and not cancel_requested:
            cancel_requested = True
            terminal_at = now

    def stop(now):
        nonlocal stopped
        if not stopped:
            stopped = True
            emit("stop", now)

    for item in events:
        kind, now = item["kind"], item["at_ms"]
        # A completed lifecycle cannot be re-opened or retrospectively timed out.
        if cleanup_done or early_outcome is not None:
            _require(kind in ("tick", "cancel") or
                     (kind == "cleanup_done" and cleanup_done and item["ok"]))
            continue
        if now > 2000:
            deadline_exceeded = True
        if dispatched_at is not None:
            if now >= 1800:
                accept_cancel(now)
            if now >= 2000 and not (kind == "cleanup_done" and free_requested and now == 2000):
                stop(now)

        if kind == "invalid_input":
            _require(dispatched_at is None)
            early_outcome, total_elapsed = "invalid_request", now
        elif kind == "dispatch":
            _require(dispatched_at is None)
            if now >= 1800:
                early_outcome, total_elapsed = "canceled", now
                cancel_requested = True
                deadline_exceeded = now > 2000
            else:
                dispatched_at = now
                emit("dispatch", now)
        elif kind == "cancel":
            if dispatched_at is None:
                early_outcome, total_elapsed = "canceled", now
                cancel_requested = True
            else:
                accept_cancel(now)
        elif kind == "tick":
            if dispatched_at is None and now >= 1800:
                early_outcome, total_elapsed = "canceled", now
                cancel_requested = True
                deadline_exceeded = now > 2000
        elif kind == "api_pending":
            _require(dispatched_at is not None and api_mode is None)
            api_mode = "pending"
        elif kind in ("api_sync", "callback_result"):
            _require(dispatched_at is not None and response is None)
            if kind == "api_sync":
                _require(api_mode is None and not callback_active and not callback_finished)
                api_mode = "sync"
            else:
                _require(api_mode in (None, "pending"))
                callback_active = True
            response = item
            if terminal_at is None:
                terminal_at = now
        elif kind == "callback_exit":
            _require(callback_active)
            callback_active, callback_finished = False, True
        elif kind == "cancel_return":
            _require(cancel_sent)
            # Return ends this call's lifetime, but is not query completion.
            cancel_returned = True
        elif kind == "cleanup_done":
            _require(free_requested and not cleanup_failed)
            if item["ok"]:
                cleanup_done, total_elapsed = True, now
            else:
                cleanup_failed = True
                stop(now)

        # Cancel only when a pending handle could be valid; defer while API runs.
        if cancel_requested and not cancel_sent and api_mode == "pending" and response is None:
            emit("request_cancel", now)
            cancel_sent = True
        safe_to_release = (response is not None and (not cancel_sent or cancel_returned)
                           and (api_mode == "sync" or
                                (api_mode == "pending" and callback_finished)))
        if safe_to_release and not free_requested:
            if response["records_owned"]:
                emit("free_records", now)
            emit("free_context", now)
            free_requested = True

    if stopped or cleanup_failed:
        outcome = "cleanup_unconfirmed"
    elif early_outcome is not None:
        outcome = early_outcome
    elif not cleanup_done:
        outcome = "pending_cleanup" if free_requested else "pending"
    elif cancel_requested:
        outcome = "canceled"
    elif response["record_count"] > 32:
        outcome = "answer_limit"
    elif response["status"] == "success" and response["answer_a_count"] == 0:
        outcome = "no_data"
    else:
        outcome = response["status"]
    return {
        "schema": "amn2.phase16.dns-lifecycle-model.v1", "model_only": True,
        "sequence": sequence, "outcome": outcome,
        "query_duration_ms": (None if dispatched_at is None or terminal_at is None
                              else terminal_at - dispatched_at),
        "total_elapsed_ms": total_elapsed,
        "answer_a_count": (None if response is None or response["record_count"] > 32
                           else response["answer_a_count"]),
        "cancel_requested": cancel_requested,
        "cleanup_confirmed": cleanup_done or dispatched_at is None,
        "deadline_exceeded": deadline_exceeded,
        "stop_required": stopped,
        "effects": effects,
    }
