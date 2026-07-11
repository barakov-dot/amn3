#!/usr/bin/env python
"""Guard Phase 9 work against command loops and docs-only drift."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


LOOP_STEPS = {
    "AWAIT_OPERATOR_EXACT_CMD",
    "AWAIT_OPERATOR_EXACT_DOCS_ONLY_REQUEST",
    "CONFIRM_HOLD_STATE",
    "READY_FOR_OPERATOR_NEXT_DOCS_REQUEST",
}

MODEL_LABEL_TOKENS = {
    "CODEX_SPARK",
    "CURRENT_MODEL",
    "GPT_5",
    "GPT_5_5",
    "GPT_5_3",
}

DOCS_ONLY_STEP_MARKERS = (
    "DOCS_ONLY",
    "HANDOFF",
    "HOLD",
    "NEXT_CHAT",
    "STATUS_REFRESH",
    "STATUS_SYNC",
)

PRODUCT_STEP_MARKERS = (
    "LOCAL_PRODUCT_SLICE",
    "RUN_SCOPED_TESTS",
    "SELECT_NEXT_LOCAL_PRODUCT_SLICE",
    "SELECT_NEXT_NON_SERVER_CONFIG_PRODUCT_SLICE",
    "_SLICE_DIFF",
)

PRODUCT_PREFIXES = (
    "START_",
    "REVIEW_",
    "STAGE_AND_COMMIT_",
    "PUSH_",
)

PLACEHOLDER_PRODUCT_STEPS = {
    "START_SELECTED_PHASE10_PRODUCT_SLICE",
    "RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
}

KNOWN_PHASE10_SLICE_STEPS = {
    "START_PHASE10_44287D4_VPS_PACKAGE_PREP_SLICE",
    "START_PHASE10_4E44C5D_VPS_PACKAGE_PREP_SLICE",
    "START_PHASE10_CLIENT_COMPATIBILITY_BRANCH_BROAD_SCOPED_REGRESSION_SLICE",
    "START_PHASE10_CONFIG_SHARE_RESTORE_SCHEMA_INDEX_TEST_VERIFICATION_SLICE",
    "START_PHASE10_ECF8563_VPS_PACKAGE_PREP_SLICE",
    "START_PHASE10_PROGRESS_HARNESS_KNOWN_SLICE_REGISTRY_SLICE",
    "START_PHASE10_TELEGRAM_SINGLE_ADMIN_TRANSIENT_SMOKE_RUNNER_HARDENING_SLICE",
}

SCOPED_TESTS_REQUIRED_FOR_SLICE = {"RUN_SCOPED_TESTS_FOR_SELECTED_SLICE"}

REQUIRED_FALSE_MARKERS = {
    "execution_go",
    "config_generation",
    "config_delivery",
    "peer_creation",
    "live_vps_ssh_telegram_public",
}

PRODUCT_PATH_PREFIXES = (
    "app/",
    "dist/amn2-vps-update-and-smoke-kit-",
    "scripts/",
    "tests/",
)
DOCS_PATH_PREFIXES = ("docs/", "ideas/", "research/", "watch-notes/", "prototypes/")
DOCS_FILES = {"README.md"}


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def normalize_command(command: str) -> str:
    return command.replace("→", "->")


def extract_steps(command: str) -> list[str]:
    steps: list[str] = []
    for part in normalize_command(command).split("->"):
        token = part.strip().upper()
        if token in MODEL_LABEL_TOKENS:
            continue
        if re.fullmatch(r"[A-Z0-9_]+", token):
            steps.append(token)
    return steps


def is_docs_only_step(step: str) -> bool:
    if step.startswith("SYNC_AMN3_STATUS"):
        return True
    if step.startswith("STAGE_AND_COMMIT_AMN3_"):
        return True
    if step.startswith("PUSH_AMN3_"):
        return True
    return any(marker in step for marker in DOCS_ONLY_STEP_MARKERS)


def is_product_step(step: str) -> bool:
    if step in LOOP_STEPS or is_docs_only_step(step):
        return False
    if any(marker in step for marker in PRODUCT_STEP_MARKERS):
        return True
    return step.startswith(PRODUCT_PREFIXES) and "SLICE" in step


def is_concrete_product_slice_step(step: str) -> bool:
    if step in PLACEHOLDER_PRODUCT_STEPS:
        return False
    if step.startswith("SELECT_NEXT_"):
        return False
    return is_product_step(step)


def is_known_phase10_slice_step(step: str) -> bool:
    if not step.startswith("START_PHASE10_"):
        return True
    return step in KNOWN_PHASE10_SLICE_STEPS


def evaluate_next_command(
    command: str,
    *,
    allow_hold: bool = False,
    require_product_step: bool = False,
    require_scoped_tests: bool = False,
) -> list[Check]:
    steps = extract_steps(command)
    checks: list[Check] = []
    if not steps:
        checks.append(
            Check(
                "next-command-parsed",
                False,
                "No machine-readable COMMAND_STEP tokens were found.",
            )
        )
        return checks

    loop_steps = [step for step in steps if step in LOOP_STEPS]
    loop_only = len(loop_steps) == len(steps)
    checks.append(
        Check(
            "next-command-loop-guard",
            allow_hold or not loop_only,
            "loop-only command rejected"
            if loop_only and not allow_hold
            else f"steps={','.join(steps)}",
        )
    )

    product_steps = [step for step in steps if is_product_step(step)]
    checks.append(
        Check(
            "next-command-product-signal",
            (not require_product_step) or bool(product_steps),
            "product step required but not found"
            if require_product_step and not product_steps
            else f"product_steps={','.join(product_steps) if product_steps else 'none'}",
        )
    )
    concrete_steps = [step for step in product_steps if is_concrete_product_slice_step(step)]
    checks.append(
        Check(
            "next-command-concrete-slice",
            (not require_product_step) or bool(concrete_steps),
            "concrete product slice required; SELECT/START_SELECTED/RUN_SCOPED_TESTS placeholders are not enough; "
            "use START_PHASE10_<REAL_TOPIC>_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE"
            if require_product_step and not concrete_steps
            else f"concrete_steps={','.join(concrete_steps) if concrete_steps else 'none'}",
        )
    )
    unknown_phase10_steps = [
        step for step in concrete_steps if not is_known_phase10_slice_step(step)
    ]
    checks.append(
        Check(
            "next-command-known-phase10-slice",
            (not require_product_step) or not unknown_phase10_steps,
            "unknown Phase 10 slice command rejected; known="
            f"{','.join(sorted(KNOWN_PHASE10_SLICE_STEPS))}"
            if unknown_phase10_steps
            else "all Phase 10 slice commands are known",
        )
    )

    if require_scoped_tests:
        checks.append(
            Check(
                "next-command-scoped-tests",
                any(step in SCOPED_TESTS_REQUIRED_FOR_SLICE for step in steps),
                "scoped tests required for real product slice commands; add RUN_SCOPED_TESTS_FOR_SELECTED_SLICE",
            )
        )
    return checks


def read_status_markers(root: Path) -> dict[str, str]:
    status_path = root / "docs" / "PROJECT_STATUS_CURRENT.ru.md"
    markers: dict[str, str] = {}
    if not status_path.exists():
        return markers

    for line in status_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip("` -*")
        value = value.strip("` ")
        if key:
            markers[key] = value
    return markers


def check_stop_lines(root: Path) -> list[Check]:
    status_path = root / "docs" / "PROJECT_STATUS_CURRENT.ru.md"
    if not status_path.exists():
        return [
            Check(
                "stop-lines-source",
                True,
                "docs/PROJECT_STATUS_CURRENT.ru.md not found; stop-line check skipped",
            )
        ]

    markers = read_status_markers(root)
    checks: list[Check] = []
    for key in sorted(REQUIRED_FALSE_MARKERS):
        value = markers.get(key)
        checks.append(
            Check(
                f"stop-line-{key}",
                value == "false",
                f"{key}={value!r}" if value is not None else f"{key} missing",
            )
        )
    return checks


def run_git_name_only(root: Path, args: Sequence[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args, "--name-only"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def parse_status_paths(status_output: str) -> list[str]:
    paths: list[str] = []
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            paths.append(path.strip('"').replace("\\", "/"))
    return paths


def run_git_status_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return parse_status_paths(result.stdout)


def changed_paths(root: Path) -> list[str]:
    paths = set(run_git_name_only(root, ["diff"]))
    paths.update(run_git_name_only(root, ["diff", "--cached"]))
    paths.update(run_git_status_paths(root))
    return sorted(paths)


def classify_paths(paths: Iterable[str]) -> str:
    paths = list(paths)
    if not paths:
        return "clean"

    has_product = any(path.startswith(PRODUCT_PATH_PREFIXES) for path in paths)
    has_docs = any(path.startswith(DOCS_PATH_PREFIXES) or path in DOCS_FILES for path in paths)
    has_other = any(
        not path.startswith(PRODUCT_PATH_PREFIXES)
        and not path.startswith(DOCS_PATH_PREFIXES)
        and path not in DOCS_FILES
        for path in paths
    )

    if has_product and not has_docs and not has_other:
        return "product-only"
    if has_docs and not has_product and not has_other:
        return "docs-only"
    if has_product and has_docs and not has_other:
        return "product-and-docs"
    return "mixed-or-other"


def check_diff_scope(root: Path, *, require_product_diff: bool = False) -> list[Check]:
    paths = changed_paths(root)
    scope = classify_paths(paths)
    detail = f"scope={scope}; paths={','.join(paths) if paths else 'none'}"
    if require_product_diff and scope == "clean":
        detail += "; no product diff: valid next-command is not product-slice closure evidence"
    return [
        Check(
            "working-tree-scope",
            (not require_product_diff) or scope in {"product-only", "product-and-docs"},
            detail,
        )
    ]


def format_checks(checks: Sequence[Check]) -> str:
    lines = []
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        lines.append(f"{status} {check.name}: {check.detail}")
    verdict = "PASS" if all(check.ok for check in checks) else "FAIL"
    return f"Phase 9 progress harness: {verdict}\n" + "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail fast on Phase 9 hold loops and docs-only drift.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--next-command", default="")
    parser.add_argument("--allow-hold", action="store_true")
    parser.add_argument("--require-product-step", action="store_true")
    parser.add_argument("--require-product-diff", action="store_true")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    checks: list[Check] = []
    checks.extend(check_stop_lines(root))
    checks.extend(check_diff_scope(root, require_product_diff=args.require_product_diff))
    if args.next_command:
        checks.extend(
            evaluate_next_command(
                args.next_command,
                allow_hold=args.allow_hold,
                require_product_step=args.require_product_step,
                require_scoped_tests=args.require_product_step,
            )
        )

    print(format_checks(checks))
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
