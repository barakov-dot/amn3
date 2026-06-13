import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HYGIENE_SCRIPT = REPO_ROOT / "scripts" / "check_markdown_hygiene.py"


def _load_hygiene_module():
    spec = importlib.util.spec_from_file_location("check_markdown_hygiene", HYGIENE_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarkdownHygieneTests(unittest.TestCase):
    def test_detects_powershell_backtick_escape_control_chars(self) -> None:
        hygiene = _load_hygiene_module()
        text = "\n".join(
            [
                "Keep latest head as \x083102db.",
                "Run \x07mn2_apply_source_zip.sh.",
                "Do not publish \x0bpn:// links.",
                "",
            ]
        )

        findings = hygiene.find_disallowed_control_chars(text, path=Path("operator.md"))

        self.assertEqual(
            [(item.line, item.column, item.codepoint) for item in findings],
            [
                (1, 21, "U+0008"),
                (2, 5, "U+0007"),
                (3, 16, "U+000B"),
            ],
        )
        rendered = hygiene.format_findings(findings)
        self.assertIn("operator.md:1:21: U+0008", rendered)
        self.assertIn("PowerShell backtick escape", rendered)

    def test_allows_common_markdown_whitespace_controls(self) -> None:
        hygiene = _load_hygiene_module()
        text = "heading\r\n\t- item\n"

        self.assertEqual(hygiene.find_disallowed_control_chars(text, path=Path("operator.md")), [])


if __name__ == "__main__":
    unittest.main()
