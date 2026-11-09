"""Execute source examples in archived Python mentorship companion lessons, PDF pages 5–10.

Checks original displayed outputs, not learner submissions, official W3Schools
examples, or all 80 pages. Never rewrites the 744-file source archive.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
          / "2. Python Mastry" / "1. Python from Zero")
LESSONS = {
    1: "01. Your first Python program.md",
    2: "02. Variables and names.md",
    3: "03. Numbers and maths.md",
    4: "04. Strings - working with text.md",
    5: "05. True False and comparisons.md",
    6: "06. Input and output.md",
}
EXPECTED_COUNTS = {1: 12, 2: 7, 3: 8, 4: 8, 5: 6, 6: 7}
EXCEPTION_EXAMPLES = {(1, 3): "NameError", (1, 6): "IndentationError",
                      (2, 4): "NameError"}
REQUIRES_CONTEXT = {(4, 3): 'status = "  Delivered  "\n'}
INPUTS = {(6, 2): "Meera\n3\n249\n", (6, 7): "3\n"}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?lesson=(\d+)&snippet=(\d+)>\)"
)
PYTHON_FENCE = re.compile(
    r"(?ms)^(?P<delim>~~~|```)python\s*\n"
    r"(?P<body>.*?)(?:^\s*(?P=delim)\s*$)"
)
TEXT_FENCE = re.compile(
    r"(?ms)^(?P<delim>~~~|```)text\s*\n"
    r"(?P<body>.*?)(?:^\s*(?P=delim)\s*$)"
)


def snippets(lesson: int) -> dict[int, tuple[str, str]]:
    path = SOURCE / LESSONS[lesson]
    body = path.read_text(encoding="utf-8-sig")
    links = list(LINK.finditer(body))
    result: dict[int, tuple[str, str]] = {}
    for idx, link in enumerate(links):
        linked_lesson, number = map(int, link.groups())
        if linked_lesson != lesson:
            raise AssertionError(f"{path.name}: link points at {linked_lesson}")
        section = body[link.end():links[idx + 1].start()
                       if idx + 1 < len(links) else len(body)]
        code = PYTHON_FENCE.search(section)
        output = TEXT_FENCE.search(section)
        if not code or not output or number in result:
            raise AssertionError(f"{path.name}, snippet {number}: "
                                 "missing/duplicate Python code or text output")
        result[number] = (code.group("body").strip("\n"),
                          output.group("body").strip("\n"))
    expected = set(range(1, EXPECTED_COUNTS[lesson] + 1))
    if set(result) != expected:
        raise AssertionError(f"{path.name}: expected {sorted(expected)}, "
                             f"found {sorted(result)}")
    return result


def canonical_output(text: str) -> str:
    # Preserve in-line spacing (e.g. aligned receipt columns).
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


class ArchivedPythonMentorshipOutputChecks(unittest.TestCase):
    def test_all_48_archived_linked_examples(self) -> None:
        checked = 0
        for lesson in LESSONS:
            for number, (code, expected) in snippets(lesson).items():
                key = (lesson, number)
                with self.subTest(pdf_page=lesson + 4, snippet=number):
                    source = REQUIRES_CONTEXT.get(key, "") + code
                    run = subprocess.run(
                        [sys.executable, "-I", "-B", "-c", source],
                        input=INPUTS.get(key, ""),
                        capture_output=True, text=True, timeout=5,
                        check=False,
                    )
                    if key in EXCEPTION_EXAMPLES:
                        self.assertNotEqual(run.returncode, 0)
                        self.assertIn(EXCEPTION_EXAMPLES[key], run.stderr)
                        self.assertIn(EXCEPTION_EXAMPLES[key], expected)
                    elif key == (6, 2):
                        # A blank line is claimed in the source, but print()
                        # after the input prompt creates only one newline.
                        self.assertEqual(run.returncode, 0, run.stderr)
                        self.assertEqual(canonical_output(run.stdout),
                                         "Your name: How many items? Price per item:\n"
                                         "Hi Meera, your total is 747.00")
                        self.assertEqual(canonical_output(expected),
                                         "Your name: How many items? Price per item:\n\n"
                                         "Hi Meera, your total is 747.00")
                    elif key == (6, 7):
                        # Source shows terminal-echoed input ("Quantity: 3").
                        # Captured stdin does not echo characters back to stdout.
                        self.assertEqual(run.returncode, 0, run.stderr)
                        self.assertEqual(canonical_output(run.stdout),
                                         "Quantity: Units: 3")
                        self.assertEqual(canonical_output(expected),
                                         "Quantity: 3\nUnits: 3")
                    else:
                        self.assertEqual(run.returncode, 0, run.stderr)
                        self.assertEqual(canonical_output(run.stdout),
                                         canonical_output(expected))
                    checked += 1
        self.assertEqual(checked, sum(EXPECTED_COUNTS.values()))

    def test_standalone_vs_context_and_input_are_documented(self) -> None:
        self.assertEqual(sum(EXPECTED_COUNTS.values()), 48)
        self.assertEqual(set(REQUIRES_CONTEXT), {(4, 3)})
        self.assertEqual(set(INPUTS), {(6, 2), (6, 7)})
        self.assertEqual(set(EXCEPTION_EXAMPLES),
                         {(1, 3), (1, 6), (2, 4)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
