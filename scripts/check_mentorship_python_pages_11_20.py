"""Runtime audit of archived mentorship companion lesson snippets (PDF pp. 11–20).

Checks the literal source-linked snippets and displayed text outputs with a
fresh Python process. This is not a check of every printed PDF page or any
student's independent solution. Source archives are never altered.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
          / "2. Python Mastry" / "1. Python from Zero")
LESSONS = {
    11: "07. Making decisions.md",
    12: "08. Loops part 1 - for and range.md",
    13: "09. Loops part 2 - while break continue.md",
    14: "10. Lists - ordered collections.md",
    15: "11. Tuples and sets.md",
    16: "12. Dictionaries - key and value.md",
    17: "13. Which data structure.md",
    18: "14. Functions - reusable steps.md",
    19: "15. Functions part 2 - mini pipeline.md",
    20: "16. Modules packages and pip.md",
}
COUNTS = {11: 7, 12: 7, 13: 6, 14: 5, 15: 5,
          16: 7, 17: 3, 18: 6, 19: 6, 20: 9}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?lesson=(\d+)&snippet=(\d+)>\)"
)
DELIMITER = r"(?:~~~|" + re.escape(chr(96) * 3) + r")"
PYTHON_FENCE = re.compile(
    r"(?ms)^" + DELIMITER + r"python[ \t]*\n(.*?)^\s*" + DELIMITER + r"\s*$"
)
TEXT_FENCE = re.compile(
    r"(?ms)^" + DELIMITER + r"text[ \t]*\n(.*?)^\s*" + DELIMITER + r"\s*$"
)

# Source deliberately omits an "Output:" block for examples that declare
# a variable/function/module, or shows non-portable timing instead of a
# fixed output transcript.
NO_TEXT_OUTPUT = {(17, 1), (19, 3), (19, 4), (20, 2), (20, 4), (20, 7)}
EXCEPTION_EXAMPLES = {(18, 4): "NameError"}
MODULE_EXAMPLES = {(20, 3): ("helpers.py", (20, 2)),
                   (20, 5): ("tool.py", (20, 4)),
                   (20, 8): ("pricing.py", (20, 7))}
CONTEXT_EXAMPLES = {(19, 5): [(19, 3), (19, 4)]}


def parse_snippets(page: int) -> dict[int, tuple[str, str | None]]:
    path = SOURCE / LESSONS[page]
    body = path.read_text(encoding="utf-8-sig")
    links = list(LINK.finditer(body))
    found: dict[int, tuple[str, str | None]] = {}
    for i, link in enumerate(links):
        linked_lesson, number = map(int, link.groups())
        if linked_lesson != page - 4:
            raise AssertionError(f"{path.name}: link's lesson is {linked_lesson}, "
                                 f"expected {page - 4}")
        span = body[link.end():links[i+1].start()
                    if i + 1 < len(links) else len(body)]
        code = PYTHON_FENCE.search(span)
        shown = TEXT_FENCE.search(span)
        if not code or number in found:
            raise AssertionError(f"{path.name} #{number}: code missing or duplicate")
        text = shown.group(1).strip("\n") if shown else None
        if (page, number) in NO_TEXT_OUTPUT:
            if shown:
                raise AssertionError(f"{path.name} #{number}: previously no text")
        elif shown is None:
            raise AssertionError(f"{path.name} #{number}: expected text block absent")
        found[number] = (code.group(1).strip("\n"), text)
    if set(found) != set(range(1, COUNTS[page] + 1)):
        raise AssertionError(f"{path.name}: found {sorted(found)}, "
                             f"wanted 1..{COUNTS[page]}")
    return found


def compact(text: str) -> str:
    # Only trim display-only final spaces and outer newlines, not interior
    # spaces or the fixed width tabular layout in source examples.
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def execute(code: str, modules: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="source-python-audit-") as td:
        for filename, content in (modules or {}).items():
            (Path(td) / filename).write_text(content + "\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", "-c", code],
            input="", capture_output=True, text=True, timeout=15,
            cwd=td, check=False,
            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
        )


class ArchivedMentorshipPages11To20(unittest.TestCase):
    def test_all_61_source_linked_examples(self) -> None:
        all_examples = {page: parse_snippets(page) for page in LESSONS}
        inspected = 0
        for page, sections in all_examples.items():
            for number, (code, shown) in sections.items():
                with self.subTest(pdf_page=page, original_snippet=number):
                    key = (page, number)
                    if key in CONTEXT_EXAMPLES:
                        earlier = [all_examples[p][n][0] for p, n
                                   in CONTEXT_EXAMPLES[key]]
                        code = "\n\n".join(earlier + [code])
                    modules = None
                    if key in MODULE_EXAMPLES:
                        filename, (p, n) = MODULE_EXAMPLES[key]
                        modules = {filename: all_examples[p][n][0]}
                    result = execute(code, modules)
                    if key in EXCEPTION_EXAMPLES:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(EXCEPTION_EXAMPLES[key], result.stderr)
                        self.assertIn(EXCEPTION_EXAMPLES[key], shown or "")
                    else:
                        self.assertEqual(result.returncode, 0,
                                         f"{key}: {result.stderr}")
                        if key == (17, 1):
                            # Benchmark uses live wall clock; printed durations
                            # cannot be expected to match a static transcript.
                            lines = compact(result.stdout).split("\n")
                            self.assertEqual(lines[:2], ["True", "True"])
                            self.assertRegex(lines[2], r"^list \d+\.\d{2} ms vs set \d+\.\d{4} ms$")
                            self.assertEqual(len(lines), 3)
                        elif key == (17, 3):
                            # Set/list conversion is intentionally unordered.
                            rows = compact(result.stdout).splitlines()
                            self.assertEqual(set(ast.literal_eval(rows[0])),
                                             {"Aarav", "Diya", "Kabir"})
                            self.assertEqual(set(ast.literal_eval(rows[1])),
                                             {"b", "a", "n"})
                            self.assertEqual(len(rows), 2)
                        elif key == (20, 4):
                            # tool.py deliberately prints when executed as
                            # main, but importing it in #5 must stay quiet.
                            # The source shows no fixed transcript for #4.
                            self.assertEqual(compact(result.stdout),
                                             "running the tool")
                        elif shown is None:
                            self.assertEqual(result.stdout, "",
                                             f"{key}: expected declarations only")
                        else:
                            self.assertEqual(compact(result.stdout), compact(shown))
                    inspected += 1
        self.assertEqual(inspected, 61)

    def test_source_special_cases_explicitly_documented(self) -> None:
        self.assertEqual(sum(COUNTS.values()), 61)
        self.assertEqual(len(NO_TEXT_OUTPUT), 6)
        self.assertEqual(set(EXCEPTION_EXAMPLES), {(18, 4)})
        self.assertEqual(set(CONTEXT_EXAMPLES), {(19, 5)})
        self.assertEqual(set(MODULE_EXAMPLES), {(20, 3), (20, 5), (20, 8)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
