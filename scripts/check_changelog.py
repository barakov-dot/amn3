#!/usr/bin/env python3
"""Enforce per-commit changelog records. Stdlib only; no network or Git writes."""
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
import re
import subprocess
import sys

POLICY_START = "5bb1b14ad3109f7df796e009a31d1f555444e9cd"
CHANGELOG = "CHANGELOG.md"
GENERIC = {"updated", "update", "changed", "обновлено", "изменено", "обновление"}
PLACEHOLDERS = {"reason", "причина", "docs-only", "docs only", "documentation",
                "документация", "<reason>", "<причина>"}


class GateError(Exception):
    """Cannot determine compliance; fail closed."""


def git(*args: str, input: str | None = None, allowed=(0,)) -> str:
    result = subprocess.run(["git", "--no-lazy-fetch", *args], input=input, capture_output=True,
                            text=True, encoding="utf-8", errors="strict")
    if result.returncode not in allowed:
        # Never print a diff or a commit body, which could contain private data.
        raise GateError("Git read failed; require --no-lazy-fetch support, local objects and complete history.")
    return result.stdout


def resolve(ref: str) -> str:
    return git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}").strip()


def ancestor(older: str, newer: str) -> bool:
    result = subprocess.run(["git", "--no-lazy-fetch", "merge-base", "--is-ancestor", older, newer],
                            capture_output=True)
    if result.returncode not in (0, 1):
        raise GateError("Cannot determine policy ancestry; fetch complete history.")
    return result.returncode == 0


def changelog_at(ref: str | None, *, staged: bool = False) -> str:
    if staged:
        listing = git("ls-files", "--stage", "-z", "--", CHANGELOG)
        target = ":" + CHANGELOG
    elif ref:
        listing = git("ls-tree", "-z", ref, "--", CHANGELOG)
        target = ref + ":" + CHANGELOG
    else:
        return ""
    if not listing:
        return ""
    if listing.split()[0] != "100644":
        raise GateError("CHANGELOG.md must be a regular non-executable file.")
    return git("show", target)


def records(text: str) -> set[str]:
    """Compare dated bullet text, ignoring line wrapping and date-only edits."""
    found: set[str] = set()
    dated = False
    current: list[str] = []

    def finish():
        if dated and current:
            entry = " ".join(" ".join(current).split()).strip()
            if entry and entry.casefold().strip(" .!;:-") not in GENERIC:
                found.add(entry)
        current.clear()

    for line in text.splitlines():
        if re.match(r"^#{1,2} ", line):
            finish()
            match = re.match(r"^## (\d{4}-\d{2}-\d{2})(?:\s|$)", line)
            dated = False
            if match:
                try:
                    date.fromisoformat(match[1])
                    dated = True
                except ValueError:
                    pass
        elif re.match(r"^###", line):
            finish()
        elif re.match(r"^[-*] ", line):
            finish()
            current.append(line[2:])
        elif line.startswith((" ", "\t")) and current:
            current.append(line.strip())
        elif line.strip():
            finish()
    finish()
    return found


def exception_reason(message: str) -> str | None:
    # The exception belongs in the final trailer block, never the subject/quote.
    message = git("stripspace", input=message).strip()
    blocks = re.split(r"\n\s*\n", message)
    if len(blocks) < 2:
        return None
    lines = blocks[-1].splitlines()
    if not all(re.fullmatch(r"[A-Za-z][A-Za-z-]*: .+", line) for line in lines):
        return None
    candidates = [line for line in lines if line.startswith("Changelog:")]
    if len(candidates) != 1:
        return None
    match = re.fullmatch(r"Changelog: not-needed \(([^()\r\n]+)\)", candidates[0])
    if not match:
        return None
    reason = " ".join(match[1].split()).strip()
    if not reason or reason.casefold().strip(" .") in PLACEHOLDERS:
        return None
    return reason


def check_change(before: str | None, after: str | None, message: str) -> bool:
    if after is None:
        if git("diff", "--cached", "--name-only", "--diff-filter=U", "-z"):
            raise GateError("Unmerged index; resolve conflicts before checking.")
        changed = git("diff", "--cached", "--name-only", "--no-renames", "-z")
    else:
        changed = git("diff-tree", "--root", "--no-commit-id", "--name-only",
                      "--no-renames", "-r", "-z", *([before, after] if before else [after]))
    if not changed:
        print("PASS: no tree changes.")
        return True
    new = records(changelog_at(after, staged=after is None))
    old = records(changelog_at(before))
    if CHANGELOG in changed.split("\0") and new - old:
        print("PASS: changed dated changelog record.")
        return True
    if exception_reason(message):
        print("EXCEPTION: reasoned trailer; meaning must be reviewed by a human.")
        return True
    print("FAIL: add a dated, specific CHANGELOG.md record to the same commit; "
          "only non-semantic fixes may use a reasoned Changelog: not-needed (...) trailer.")
    return False


def zero(ref: str) -> bool:
    return bool(re.fullmatch(r"0{40}|0{64}", ref))


def check_range(base: str, head: str, policy_start: str) -> bool:
    policy = resolve(policy_start)
    tip = resolve(head)
    start = policy if zero(base) else resolve(base)
    commits = git("rev-list", "--reverse", tip, "^" + start).splitlines()
    ok = True
    checked = 0
    for commit in commits:
        if ancestor(commit, policy):
            continue  # The introduction commit and all its ancestors are historical.
        if not ancestor(policy, commit):
            raise GateError("Commit outside policy lineage; review history before checking.")
        parents = git("rev-list", "--parents", "-n", "1", commit).split()[1:]
        print(commit[:12] + ":", end=" ")
        passed = check_change(parents[0] if parents else None, commit,
                              git("log", "-1", "--format=%B", commit))
        ok = passed and ok
        checked += 1
    print(f"Checked {checked} commit(s) after policy introduction.")
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--staged", action="store_true")
    modes.add_argument("--range", nargs=2, metavar=("BASE", "HEAD"))
    modes.add_argument("--pre-push", action="store_true")
    parser.add_argument("--message-file", type=Path)
    parser.add_argument("--policy-start", default=POLICY_START,
                        help="Policy introduction commit; override for disposable tests only.")
    args = parser.parse_args(argv)
    if args.message_file and not args.staged:
        parser.error("--message-file is only valid with --staged")
    try:
        # Hooks run at the worktree root; make standalone calls from subdirs equivalent.
        if args.message_file:
            args.message_file = args.message_file.resolve()
        root = git("rev-parse", "--show-toplevel").strip()
        os.chdir(root)
        if args.staged:
            head = git("rev-parse", "--verify", "HEAD", allowed=(0, 128)).strip() or None
            message = args.message_file.read_text(encoding="utf-8") if args.message_file else ""
            ok = check_change(head, None, message)
        elif args.range:
            ok = check_range(*args.range, args.policy_start)
        else:
            ok = True
            for line in sys.stdin:
                fields = line.split()
                if len(fields) != 4 or not all(
                    re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)
                    for value in (fields[1], fields[3])
                ):
                    raise GateError("Malformed pre-push input.")
                _, local_oid, _, remote_oid = fields
                if zero(local_oid):
                    continue  # No commits to inspect; this does not authorize deletion.
                passed = check_range(remote_oid, local_oid, args.policy_start)
                ok = passed and ok
        return 0 if ok else 1
    except (GateError, OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
