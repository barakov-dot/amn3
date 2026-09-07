"""Pure d1 lifecycle traces: no native calls, sockets, sleeps or child processes."""
import importlib
import json
import unittest


def event(kind, at_ms, **values):
    return dict(kind=kind, at_ms=at_ms, **values)


def reply(kind, at_ms, status="success", records=1, answers=1, owned=True):
    return event(kind, at_ms, status=status, record_count=records,
                 answer_a_count=answers, records_owned=owned)


class DnsLifecycleTest(unittest.TestCase):
    def run_trace(self, events, sequence=1):
        # Missing implementation is an explicit RED assertion, not an import error.
        spec = importlib.util.find_spec("scripts.vps.phase16_dns_lifecycle")
        self.assertIsNotNone(spec, "DNS lifecycle model not implemented")
        module = importlib.import_module("scripts.vps.phase16_dns_lifecycle")
        return module.replay(events, sequence=sequence)

    def kinds(self, result):
        return [item["kind"] for item in result["effects"]]

    def test_sync_success_waits_for_cleanup_ack_and_releases_once(self):
        prefix = [event("dispatch", 10), reply("api_sync", 20)]
        before = self.run_trace(prefix)
        self.assertFalse(before["cleanup_confirmed"])
        self.assertEqual(before["outcome"], "pending_cleanup")
        self.assertEqual(self.kinds(before), ["dispatch", "free_records", "free_context"])
        got = self.run_trace(prefix + [event("cleanup_done", 25, ok=True),
                                       event("cleanup_done", 26, ok=True), event("tick", 5000)])
        self.assertEqual(got["outcome"], "success")
        self.assertEqual(got["query_duration_ms"], 10)
        self.assertEqual(got["total_elapsed_ms"], 25)
        self.assertEqual(got["answer_a_count"], 1)
        self.assertTrue(got["cleanup_confirmed"])
        self.assertFalse(got["deadline_exceeded"])
        self.assertEqual(self.kinds(got), ["dispatch", "free_records", "free_context"])

    def test_pending_callback_result_does_not_free_while_callback_active(self):
        prefix = [event("dispatch", 0), event("api_pending", 1), reply("callback_result", 20)]
        self.assertEqual(self.kinds(self.run_trace(prefix)), ["dispatch"])
        got = self.run_trace(prefix + [event("callback_exit", 21), event("cleanup_done", 22, ok=True)])
        self.assertEqual(got["outcome"], "success")
        self.assertEqual(got["effects"][1], dict(kind="free_records", at_ms=21))
        self.assertEqual(got["effects"][2], dict(kind="free_context", at_ms=21))

    def test_callback_before_api_return_requires_both_lifetime_boundaries(self):
        prefix = [event("dispatch", 0), reply("callback_result", 2), event("callback_exit", 3)]
        self.assertEqual(self.kinds(self.run_trace(prefix)), ["dispatch"])
        got = self.run_trace(prefix + [event("api_pending", 5), event("cleanup_done", 6, ok=True)])
        self.assertEqual(got["outcome"], "success")
        self.assertEqual(got["effects"][1]["at_ms"], 5)

    def test_cancel_before_completion_never_upgrades_late_success(self):
        got = self.run_trace([
            event("dispatch", 0), event("api_pending", 1),
            event("cancel", 10), event("cancel", 11), event("cancel_return", 12),
            reply("callback_result", 20), event("callback_exit", 21),
            event("cleanup_done", 22, ok=True),
        ])
        self.assertEqual(got["outcome"], "canceled")
        self.assertEqual(got["query_duration_ms"], 10)
        self.assertTrue(got["cancel_requested"])
        self.assertTrue(got["cleanup_confirmed"])
        self.assertEqual(self.kinds(got).count("request_cancel"), 1)

    def test_completion_before_cancel_wins_but_still_waits_for_callback_exit(self):
        got = self.run_trace([
            event("dispatch", 0), event("api_pending", 1), reply("callback_result", 10),
            event("cancel", 11), event("callback_exit", 12), event("cleanup_done", 13, ok=True),
        ])
        self.assertEqual(got["outcome"], "success")
        self.assertFalse(got["cancel_requested"])
        self.assertNotIn("request_cancel", self.kinds(got))

    def test_cancel_during_api_call_is_deferred_until_pending_return(self):
        prefix = [event("dispatch", 0), event("cancel", 5)]
        self.assertNotIn("request_cancel", self.kinds(self.run_trace(prefix)))
        got = self.run_trace(prefix + [event("api_pending", 10), event("cancel_return", 11)])
        self.assertEqual(got["effects"][-1], dict(kind="request_cancel", at_ms=10))
        self.assertFalse(got["cleanup_confirmed"])
        self.assertNotIn("free_context", self.kinds(got))

    def test_work_deadline_requests_cancel_once_and_total_deadline_stops(self):
        got = self.run_trace([
            event("dispatch", 0), event("api_pending", 1), event("tick", 1800),
            event("cancel_return", 1801), event("tick", 1900), event("tick", 2000),
        ])
        self.assertEqual(got["outcome"], "cleanup_unconfirmed")
        self.assertFalse(got["cleanup_confirmed"])
        self.assertTrue(got["stop_required"])
        self.assertIsNone(got["total_elapsed_ms"])
        self.assertEqual(self.kinds(got), ["dispatch", "request_cancel", "stop"])

    def test_late_cleanup_frees_once_but_does_not_erase_deadline_failure(self):
        got = self.run_trace([
            event("dispatch", 0), event("api_pending", 1), event("tick", 2000),
            event("cancel_return", 2001),
            reply("callback_result", 2200), event("callback_exit", 2201),
            event("cleanup_done", 2202, ok=True),
        ])
        self.assertEqual(got["outcome"], "cleanup_unconfirmed")
        self.assertTrue(got["cleanup_confirmed"])
        self.assertTrue(got["deadline_exceeded"])
        self.assertTrue(got["stop_required"])
        self.assertEqual(got["total_elapsed_ms"], 2202)
        self.assertEqual(self.kinds(got).count("free_records"), 1)
        self.assertEqual(got["effects"][-1]["at_ms"], 2201)

    def test_callback_exit_cannot_release_context_while_cancel_call_is_inflight(self):
        prefix = [event("dispatch", 0), event("api_pending", 1), event("cancel", 10),
                  reply("callback_result", 11), event("callback_exit", 12)]
        got = self.run_trace(prefix)
        self.assertEqual(self.kinds(got), ["dispatch", "request_cancel"])
        self.assertFalse(got["cleanup_confirmed"])
        with self.assertRaisesRegex(ValueError, r"^invalid_dns_trace$"):
            self.run_trace(prefix + [event("cleanup_done", 13, ok=True)])
        done = self.run_trace(prefix + [event("cancel_return", 14),
                                       event("cleanup_done", 15, ok=True)])
        self.assertEqual(done["outcome"], "canceled")
        self.assertEqual(done["effects"][-1], dict(kind="free_context", at_ms=14))

    def test_cleanup_at_exact_budget_is_allowed_but_missing_ack_is_not(self):
        base = [event("dispatch", 0), reply("api_sync", 100)]
        done = self.run_trace(base + [event("cleanup_done", 2000, ok=True)])
        self.assertEqual(done["outcome"], "success")
        self.assertEqual(done["total_elapsed_ms"], 2000)
        self.assertFalse(done["deadline_exceeded"])
        missing = self.run_trace(base + [event("tick", 2000)])
        self.assertEqual(missing["outcome"], "cleanup_unconfirmed")
        self.assertTrue(missing["stop_required"])

    def test_cleanup_failure_never_retries_free_or_becomes_success(self):
        got = self.run_trace([
            event("dispatch", 0), reply("api_sync", 10),
            event("cleanup_done", 11, ok=False), event("tick", 2000),
        ])
        self.assertEqual(got["outcome"], "cleanup_unconfirmed")
        self.assertTrue(got["stop_required"])
        self.assertFalse(got["cleanup_confirmed"])
        self.assertEqual(self.kinds(got).count("free_context"), 1)

    def test_errors_empty_answer_and_answer_limit_keep_ownership_correct(self):
        cases = [("success", 0, 0, False, "no_data"),
                 ("nxdomain", 0, 0, False, "nxdomain"),
                 ("server_error", 1, 0, True, "server_error"),
                 ("native_timeout", 0, 0, False, "native_timeout"),
                 ("start_error", 0, 0, False, "start_error"),
                 ("success", 33, 1, True, "answer_limit")]
        for status, records, answers, owned, want in cases:
            with self.subTest(status=status, records=records):
                got = self.run_trace([event("dispatch", 0),
                                      reply("api_sync", 5, status, records, answers, owned),
                                      event("cleanup_done", 6, ok=True)])
                self.assertEqual(got["outcome"], want)
                self.assertEqual(self.kinds(got).count("free_records"), int(owned))
                self.assertEqual(self.kinds(got).count("free_context"), 1)

    def test_pre_dispatch_cancel_invalid_input_and_exhausted_setup_do_not_dispatch(self):
        for events, want in [
            ([event("cancel", 0)], "canceled"),
            ([event("invalid_input", 0)], "invalid_request"),
            ([event("dispatch", 1800)], "canceled"),
        ]:
            with self.subTest(want=want):
                got = self.run_trace(events)
                self.assertEqual(got["outcome"], want)
                self.assertEqual(got["effects"], [])
                self.assertTrue(got["cleanup_confirmed"])

    def test_pre_dispatch_overrun_is_reported_for_every_terminal_event(self):
        for kind in ("cancel", "invalid_input", "dispatch", "tick"):
            with self.subTest(kind=kind):
                got = self.run_trace([event(kind, 2001)])
                self.assertTrue(got["deadline_exceeded"])
                self.assertTrue(got["cleanup_confirmed"])
                self.assertEqual(got["total_elapsed_ms"], 2001)
                self.assertEqual(got["effects"], [])

    def test_invalid_order_schema_and_raw_fields_fail_closed_without_echo(self):
        cases = [
            [event("callback_exit", 0)], [event("cleanup_done", 0, ok=True)],
            [event("dispatch", 2), event("api_pending", 1)],
            [event("dispatch", 0), event("dispatch", 1)],
            [event("dispatch", 0, endpoint="secret-fixture")],
            [event("tick", True)], [event("tick", float("nan"))],
            [event("secret-fixture", 0)],
            [event("dispatch", 0), reply("api_sync", 1, records=1, answers=2)],
            [event("dispatch", 0), reply("api_sync", 1, owned=False)],
            [event("tick", i) for i in range(65)],
        ]
        for events in cases:
            with self.subTest(events=events):
                with self.assertRaisesRegex(ValueError, r"^invalid_dns_trace$") as caught:
                    self.run_trace(events)
                self.assertNotIn("secret-fixture", str(caught.exception))

    def test_model_is_not_native_evidence_or_acceptance_and_output_is_bounded(self):
        got = self.run_trace([event("dispatch", 0), reply("api_sync", 1),
                              event("cleanup_done", 2, ok=True)], sequence=5)
        self.assertTrue(got["model_only"])
        self.assertEqual(got["sequence"], 5)
        self.assertLessEqual(len(json.dumps(got).encode()), 4096)
        self.assertNotIn("PASS", json.dumps(got))
        for bad in (0, 6, True, "1"):
            with self.assertRaisesRegex(ValueError, r"^invalid_dns_trace$"):
                self.run_trace([], sequence=bad)


if __name__ == "__main__":
    unittest.main()
