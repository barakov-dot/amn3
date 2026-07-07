import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_SCRIPT = REPO_ROOT / "scripts" / "phase9_progress_harness.py"


def _load_harness_module():
    spec = importlib.util.spec_from_file_location("phase9_progress_harness", HARNESS_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Phase9ProgressHarnessTests(unittest.TestCase):
    def test_extracts_operator_steps_after_model_label(self) -> None:
        harness = _load_harness_module()

        steps = harness.extract_steps(
            "CURRENT_MODEL -> START_CONFIG_SHARE_TOKEN_REDEEM_SLICE "
            "→ RUN_SCOPED_TESTS_FOR_SELECTED_SLICE"
        )

        self.assertEqual(
            steps,
            [
                "START_CONFIG_SHARE_TOKEN_REDEEM_SLICE",
                "RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
            ],
        )

    def test_rejects_loop_only_command_when_product_step_required(self) -> None:
        harness = _load_harness_module()

        checks = harness.evaluate_next_command(
            "КОДЕКС SPARK → READY_FOR_OPERATOR_NEXT_DOCS_REQUEST → AWAIT_OPERATOR_EXACT_CMD",
            require_product_step=True,
        )

        self.assertFalse(all(check.ok for check in checks))
        self.assertIn("next-command-loop-guard", [check.name for check in checks if not check.ok])
        self.assertIn(
            "next-command-product-signal",
            [check.name for check in checks if not check.ok],
        )

    def test_accepts_real_product_slice_command(self) -> None:
        harness = _load_harness_module()

        checks = harness.evaluate_next_command(
            "КОДЕКС SPARK → START_CONFIG_SHARE_RESTORE_SCHEMA_INDEX_DECLARATION_CONTRACT_SLICE "
            "→ RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
            require_product_step=True,
        )

        self.assertTrue(all(check.ok for check in checks))

    def test_rejects_real_product_slice_without_scoped_tests(self) -> None:
        harness = _load_harness_module()

        checks = harness.evaluate_next_command(
            "КОДЕКС SPARK → START_CONFIG_SHARE_RESTORE_SCHEMA_INDEX_DECLARATION_CONTRACT_SLICE",
            require_product_step=True,
            require_scoped_tests=True,
        )

        failed_checks = {check.name: check.ok for check in checks if not check.ok}
        self.assertIn("next-command-scoped-tests", failed_checks)

    def test_rejects_selected_slice_placeholder_without_concrete_slice(self) -> None:
        harness = _load_harness_module()

        checks = harness.evaluate_next_command(
            "SELECT_NEXT_REAL_PHASE10_PRODUCT_SLICE_AFTER_P6_I007_INTERACTIVE_CLI_OUTPUT_SLICE "
            "-> START_SELECTED_PHASE10_PRODUCT_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
            require_product_step=True,
        )

        self.assertFalse(all(check.ok for check in checks))
        self.assertIn(
            "next-command-concrete-slice",
            [check.name for check in checks if not check.ok],
        )

    def test_placeholder_rejection_includes_concrete_command_hint(self) -> None:
        harness = _load_harness_module()

        checks = harness.evaluate_next_command(
            "SELECT_NEXT_REAL_PHASE10_PRODUCT_SLICE_AFTER_P6_I007_INTERACTIVE_CLI_OUTPUT_SLICE "
            "-> START_SELECTED_PHASE10_PRODUCT_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
            require_product_step=True,
        )
        failed_checks = {check.name: check.detail for check in checks if not check.ok}

        self.assertIn("next-command-concrete-slice", failed_checks)
        self.assertIn("START_PHASE10_<REAL_TOPIC>_SLICE", failed_checks["next-command-concrete-slice"])
        self.assertIn("RUN_SCOPED_TESTS_FOR_SELECTED_SLICE", failed_checks["next-command-concrete-slice"])

    def test_classifies_diff_scopes(self) -> None:
        harness = _load_harness_module()

        self.assertEqual(harness.classify_paths([]), "clean")
        self.assertEqual(harness.classify_paths(["docs/status.md"]), "docs-only")
        self.assertEqual(harness.classify_paths(["app/service.py", "tests/test_service.py"]), "product-only")
        self.assertEqual(
            harness.classify_paths(["app/service.py", "docs/status.md"]),
            "product-and-docs",
        )

    def test_parses_untracked_paths_from_git_status(self) -> None:
        harness = _load_harness_module()

        paths = harness.parse_status_paths(
            "\n".join(
                [
                    " M README.md",
                    "?? scripts/phase9_progress_harness.py",
                    "R  old.txt -> tests/test_phase9_progress_harness.py",
                ]
            )
        )

        self.assertEqual(
            paths,
            [
                "README.md",
                "scripts/phase9_progress_harness.py",
                "tests/test_phase9_progress_harness.py",
            ],
        )

    def test_skips_stop_lines_when_status_doc_is_absent(self) -> None:
        harness = _load_harness_module()

        with tempfile.TemporaryDirectory() as tmp_dir:
            checks = harness.check_stop_lines(Path(tmp_dir))

        self.assertEqual(len(checks), 1)
        self.assertTrue(checks[0].ok)
        self.assertEqual(checks[0].name, "stop-lines-source")

    def test_require_product_diff_explains_clean_tree_is_not_closure(self) -> None:
        harness = _load_harness_module()

        with tempfile.TemporaryDirectory() as tmp_dir:
            checks = harness.check_diff_scope(Path(tmp_dir), require_product_diff=True)

        self.assertFalse(all(check.ok for check in checks))
        self.assertEqual(checks[0].name, "working-tree-scope")
        self.assertIn("no product diff", checks[0].detail)
        self.assertIn("not product-slice closure evidence", checks[0].detail)


if __name__ == "__main__":
    unittest.main()
