"""Integration tests: real disposable Git repositories, never production remotes."""
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_changelog.py"
ENTRY = "# Changelog\n\n## 2026-09-20\n\n- Added the import check; verified offline.\n"


class ChangelogGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="changelog-test-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        PYTHONDONTWRITEBYTECODE="1")
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Changelog Test")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.hooksPath", str(self.repo / "unused-hooks"))
        self.write("README.md", "Baseline\n")
        self.git("add", "README.md")
        self.commit("baseline")
        self.baseline = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", check=check)

    def write(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, message):
        return self.git("commit", "-q", "-m", message)

    def changed(self):
        self.write("README.md", "Changed instructions\n")
        self.git("add", "README.md")

    def log(self, text=ENTRY):
        self.write("CHANGELOG.md", text)
        self.git("add", "CHANGELOG.md")

    def check_gate(self, *args, input=None):
        return subprocess.run([sys.executable, str(CHECKER), *args],
                              cwd=self.repo, env=self.env, input=input,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")

    def staged(self, message="docs: change instructions"):
        self.write("message.txt", message)
        return self.check_gate("--staged", "--message-file", "message.txt")

    def range_check(self, base=None, head="HEAD"):
        return self.check_gate("--range", base or self.baseline, head,
                               "--policy-start", self.baseline)

    def assert_result(self, result, code):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)

    def test_staged_record_passes(self):
        self.changed()
        self.log()
        self.assert_result(self.staged(), 0)

    def test_missing_record_blocks_docs_too(self):
        self.changed()
        self.assert_result(self.staged(), 1)

    def test_unstaged_changelog_cannot_cover_commit(self):
        self.changed()
        self.write("CHANGELOG.md", ENTRY)
        self.assert_result(self.staged(), 1)

    def test_previous_commit_cannot_cover_new_change(self):
        self.log()
        self.commit("log")
        self.changed()
        self.assert_result(self.staged(), 1)

    def test_whitespace_only_changelog_edit_is_not_record(self):
        self.log()
        self.commit("log")
        self.changed()
        self.log(ENTRY.replace("Added the", "Added   the") + "\n")
        self.assert_result(self.staged(), 1)

    def test_date_only_edit_is_not_record(self):
        self.log()
        self.commit("log")
        self.changed()
        self.log(ENTRY.replace("2026-09-20", "2026-09-21"))
        self.assert_result(self.staged(), 1)

    def test_deleted_changelog_is_not_record(self):
        self.log()
        self.commit("log")
        self.changed()
        self.git("rm", "CHANGELOG.md")
        self.assert_result(self.staged(), 1)

    def test_empty_generic_or_undated_record_blocks(self):
        self.changed()
        for text in ["", "# Changelog\n- New work done.\n",
                     "## 2026-09-20\n- Updated.\n",
                     "## 2026-09-20\n- Обновлено.\n",
                     "## 2026-99-01\n- Specific work done.\n"]:
            with self.subTest(text=text):
                self.log(text)
                self.assert_result(self.staged(), 1)

    def test_reasoned_exception_passes(self):
        self.changed()
        result = self.staged("docs: typo\n\nChangelog: not-needed (correct spelling only)")
        self.assert_result(result, 0)
        self.assertIn("EXCEPTION", result.stdout)

    def test_empty_or_generic_exception_blocks(self):
        self.changed()
        for trailer in ["Changelog: not-needed", "Changelog: not-needed ()",
                        "Changelog: not-needed (docs-only)",
                        "Changelog: not-needed (reason)",
                        "Changelog: not-needed (причина)"]:
            with self.subTest(trailer=trailer):
                self.assert_result(self.staged("docs: edit\n\n" + trailer), 1)

    def test_exception_in_subject_or_quoted_body_does_not_count(self):
        self.changed()
        for message in ["Changelog: not-needed (correct spelling only)",
                        "docs: change\n\n> Changelog: not-needed (correct spelling only)",
                        "docs: change\n\nChangelog: not-needed (correct spelling only)\n\nMore body."]:
            with self.subTest(message=message):
                self.assert_result(self.staged(message), 1)

    def test_literal_comment_after_trailer_is_not_final_exception(self):
        self.changed()
        message = ("docs: change\n\nChangelog: not-needed (correct spelling only)"
                   "\n\n# Further body text")
        self.assert_result(self.staged(message), 1)
        self.git("commit", "--cleanup=verbatim", "-q", "-m", message)
        self.assert_result(self.range_check(), 1)

    def test_later_record_does_not_cover_earlier_commit(self):
        self.changed()
        self.commit("undocumented change")
        bad = self.git("rev-parse", "HEAD").stdout.strip()
        self.log()
        self.commit("late record")
        result = self.range_check()
        self.assert_result(result, 1)
        self.assertIn(bad[:12], result.stdout + result.stderr)

    def test_range_accepts_record_then_reasoned_exception(self):
        self.changed()
        self.log()
        self.commit("documented change")
        self.write("README.md", "Corrected spelling\n")
        self.git("add", "README.md")
        self.commit("typo\n\nChangelog: not-needed (correct spelling only)")
        self.assert_result(self.range_check(), 0)

    def test_range_ignores_history_before_policy(self):
        self.changed()
        self.log()
        self.commit("documented change")
        self.assert_result(self.range_check(base="0" * 40), 0)

    def test_missing_revision_fails_closed(self):
        self.assert_result(self.range_check(base="a" * 40), 2)

    def test_missing_policy_start_fails_closed(self):
        self.assert_result(self.check_gate("--range", self.baseline, "HEAD",
                                          "--policy-start", "a" * 40), 2)

    def test_partial_clone_fails_without_implicitly_fetching_blobs(self):
        self.changed()
        self.log()
        self.commit("documented change")
        self.git("config", "uploadpack.allowFilter", "true")
        partial = Path(self.temp.name) / "partial"
        self.git("clone", "--filter=blob:none", "--no-checkout", "-q",
                 self.repo.as_uri(), str(partial))
        self.repo = partial
        before = self.git("rev-list", "--objects", "--all", "--missing=print").stdout
        self.assertIn("?", before, "Fixture must have missing blobs")
        self.assert_result(self.range_check(), 2)
        after = self.git("rev-list", "--objects", "--all", "--missing=print").stdout
        self.assertEqual(before, after, "The checker must not fetch missing blobs")

    def test_empty_commit_needs_no_record(self):
        self.git("commit", "--allow-empty", "-q", "-m", "empty")
        self.assert_result(self.range_check(), 0)

    def test_merge_checked_against_first_parent_and_all_side_commits(self):
        self.git("checkout", "-q", "-b", "side")
        self.write("side.txt", "undocumented side change\n")
        self.git("add", "side.txt")
        self.commit("bad side change")
        bad = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", "-b", "main-test", self.baseline)
        self.log()
        self.commit("main log")
        self.git("merge", "--no-ff", "-q", "-m", "merge side", "side")
        result = self.range_check()
        self.assert_result(result, 1)
        self.assertIn(bad[:12], result.stdout + result.stderr)

    def test_pre_push_checks_each_ref_and_new_branch(self):
        self.changed()
        self.commit("missing record")
        head = self.git("rev-parse", "HEAD").stdout.strip()
        for remote in [self.baseline, "0" * 40]:
            with self.subTest(remote=remote):
                data = f"HEAD {head} refs/heads/test {remote}\n"
                self.assert_result(self.check_gate("--pre-push", "--policy-start",
                                                  self.baseline, input=data), 1)

    def test_pre_push_deletion_is_not_a_new_commit(self):
        data = f"(delete) {'0' * 40} refs/heads/test {self.baseline}\n"
        self.assert_result(self.check_gate("--pre-push", "--policy-start",
                                          self.baseline, input=data), 0)

    def test_pre_push_malformed_input_fails_closed(self):
        self.assert_result(self.check_gate("--pre-push", input="invalid\n"), 2)

    def install_hooks(self):
        self.git("config", "core.hooksPath", str(ROOT / ".githooks"))
        self.git("config", "changelog.python", sys.executable.replace("\\", "/"))
        # A disposable repository has its own policy introduction commit.
        local_source, count = re.subn(r'POLICY_START = "[0-9a-f]+"',
                                     f'POLICY_START = "{self.baseline}"',
                                     CHECKER.read_text(encoding="utf-8"), count=1)
        self.assertEqual(count, 1)
        self.write("scripts/check_changelog.py", local_source)

    def test_staged_from_subdirectory_resolves_message_path(self):
        self.changed()
        self.write("sub/message.txt", "typo\n\nChangelog: not-needed (correct spelling only)")
        result = subprocess.run([sys.executable, str(CHECKER), "--staged",
                                 "--message-file", "message.txt"],
                                cwd=self.repo / "sub", env=self.env,
                                capture_output=True, text=True)
        self.assert_result(result, 0)

    def test_real_pre_push_hook_checks_local_bare_remote_without_network(self):
        remote = Path(self.temp.name) / "remote.git"
        self.git("init", "--bare", "-q", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-q", "origin", "HEAD:refs/heads/test")
        self.changed()
        self.log()
        self.commit("documented")
        good = self.git("rev-parse", "HEAD").stdout.strip()
        self.install_hooks()
        self.git("push", "-q", "origin", "HEAD:refs/heads/test")
        self.assertIn(good, self.git("ls-remote", "origin", "refs/heads/test").stdout)
        self.write("README.md", "Another change\n")
        self.git("add", "README.md")
        # Simulate a commit arriving from a caller which bypassed the local hook.
        self.git("-c", "core.hooksPath=unused-hooks", "commit", "-q", "-m", "unlogged")
        blocked = self.git("push", "-q", "origin", "HEAD:refs/heads/test", check=False)
        self.assert_result(blocked, 1)
        self.assertIn(good, self.git("ls-remote", "origin", "refs/heads/test").stdout)

    def test_real_commit_hook_blocks_and_allows_staged_changes(self):
        self.install_hooks()
        self.changed()
        blocked = self.git("commit", "-q", "-m", "missing", check=False)
        self.assert_result(blocked, 1)
        self.log()
        self.commit("documented")
        self.assertNotEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.baseline)


if __name__ == "__main__":
    unittest.main()
