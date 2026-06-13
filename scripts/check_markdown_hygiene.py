#!/usr/bin/env python
"""Check Markdown/operator docs for accidental ASCII control characters."""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence


ALLOWED_CONTROL_CODES = {0x09, 0x0A, 0x0D}

POWERSHELL_ESCAPE_HINTS = {
    0x07: "PowerShell backtick escape `a (BEL) may have eaten a literal backtick.",
    0x08: "PowerShell backtick escape `b (BS) may have eaten a literal backtick.",
    0x0B: "PowerShell backtick escape `v (VT) may have eaten a literal backtick.",
}


class ControlCharFinding(NamedTuple):
    path: Path
    line: int
    column: int
    codepoint: str
    name: str
    hint: str


def _char_name(value: int) -> str:
    try:
        return unicodedata.name(chr(value))
    except ValueError:
        return "ASCII control character"


def find_disallowed_control_chars(text: str, path: Path) -> list[ControlCharFinding]:
    findings: list[ControlCharFinding] = []
    line = 1
    column = 1

    for char in text:
        value = ord(char)
        if (value < 0x20 or value == 0x7F) and value not in ALLOWED_CONTROL_CODES:
            findings.append(
                ControlCharFinding(
                    path=path,
                    line=line,
                    column=column,
                    codepoint=f"U+{value:04X}",
                    name=_char_name(value),
                    hint=POWERSHELL_ESCAPE_HINTS.get(
                        value,
                        "Unexpected control character in Markdown/operator text.",
                    ),
                )
            )
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1

    return findings


def format_findings(findings: Iterable[ControlCharFinding]) -> str:
    lines = []
    for finding in findings:
        lines.append(
            f"{finding.path}:{finding.line}:{finding.column}: "
            f"{finding.codepoint} {finding.name}. {finding.hint}"
        )
    return "\n".join(lines)


def scan_paths(paths: Sequence[Path]) -> list[ControlCharFinding]:
    findings: list[ControlCharFinding] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        findings.extend(find_disallowed_control_chars(text, path=path))
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when Markdown/operator docs contain accidental ASCII control chars.",
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)

    findings = scan_paths(args.paths)
    if findings:
        print(format_findings(findings), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
