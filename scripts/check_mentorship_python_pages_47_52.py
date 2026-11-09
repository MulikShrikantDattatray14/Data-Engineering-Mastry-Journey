"""Read-only source/output audit for preserved mentorship DSA PDF pages 47–52.

Each example is extracted from the pinned, unmodified archived Markdown at
runtime. Synthetic boundary cases are separate reviewer tests and must NEVER be
recorded as official keys, graded assignments, or learner solutions.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
          / "2. Python Mastry" / "4. DSA and Complexity")

# PDF page -> archived filename, original Git blob SHA-1, linked Python examples
LESSONS = {
    47: ("07. Sliding windows.md", "55d2e66857c95715526fa13b8f2aadfb877cbcdc", 4),
    48: ("08. Stacks and queues.md", "10b60e9cbb74f2575d2c9a642d35ae5d7b0b957e", 4),
    49: ("09. Linked lists.md", "683623c5e6a3002f92aeb8e04d373295d41b2201", 4),
    50: ("10. Binary search.md", "a982b080d1be848300c1e4871be2dd8517eaed20", 4),
    51: ("11. Sorting.md", "8fe1f4da2b34375901fdfc58034727dd1ec4196e", 4),
    52: ("12. Recursion and backtracking.md", "7a1cb64839d6336c124a5be9518294a62ebc90cd", 5),
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=4&lesson=(\d+)&snippet=(\d+)>\)"
)
PYTHON = re.compile(r"(?ms)^~~~python[ \t]*\n(.*?)^~~~[ \t]*$")
TEXT = re.compile(r"(?ms)^~~~text[ \t]*\n(.*?)^~~~[ \t]*$")


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def linked_examples(page: int) -> dict[int, tuple[str, str]]:
    filename, expected_sha, count = LESSONS[page]
    raw = (SOURCE / filename).read_bytes()
    assert blob_sha(raw) == expected_sha, f"Preserved p.{page} source SHA changed"
    source = raw.decode("utf-8-sig")
    links = list(LINK.finditer(source))
    found: dict[int, tuple[str, str]] = {}
    for i, match in enumerate(links):
        lesson, snippet = map(int, match.groups())
        assert lesson == page - 40, f"Unexpected original lesson ID p.{page}"
        end = links[i + 1].start() if i + 1 < len(links) else len(source)
        region = source[match.end():end]
        code, output = PYTHON.search(region), TEXT.search(region)
        assert code is not None and output is not None, (
            f"Missing original code/output pair: p.{page} snippet {snippet}"
        )
        assert snippet not in found, f"Repeated source snippet ID p.{page} #{snippet}"
        found[snippet] = (code.group(1).strip("\n"), output.group(1).strip("\n"))
    assert sorted(found) == list(range(1, count + 1)), (
        f"Original source inventory differs p.{page}: {sorted(found)}"
    )
    return found


def standard_stdout(s: str) -> str:
    # Normalize only Markdown trailing/leading newline layout and line-end blanks.
    return "\n".join(line.rstrip() for line in s.strip("\n").splitlines())


def run_source(code: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="mentor47-52-") as temp:
        script = Path(temp) / "archived_example.py"
        script.write_text(code + "\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            cwd=temp, capture_output=True, text=True, input="", timeout=15,
            check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )


def source_namespace(page: int, snippet: int) -> dict:
    code, _ = linked_examples(page)[snippet]
    scope: dict = {"__name__": "audited_source"}
    exec(compile(code, f"original-p{page}-example{snippet}", "exec"), scope)
    return scope


class MentorDSAPages47To52(unittest.TestCase):
    def test_original_source_integrity_and_inventory(self):
        self.assertEqual(list(LESSONS), list(range(47, 53)))
        self.assertEqual([x[2] for x in LESSONS.values()], [4, 4, 4, 4, 4, 5])
        self.assertEqual(sum(x[2] for x in LESSONS.values()), 25)
        for page, (filename, _sha, count) in LESSONS.items():
            with self.subTest(page=page, original_filename=filename):
                self.assertEqual(len(linked_examples(page)), count)

    def test_all_25_unmodified_archived_code_output_contracts(self):
        verified = 0
        for page in LESSONS:
            for number, (code, expected) in linked_examples(page).items():
                with self.subTest(pdf_page=page, original_example=number):
                    result = run_source(code)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "", "Unexpected stderr")
                    self.assertEqual(standard_stdout(result.stdout),
                                     standard_stdout(expected),
                                     f"Archived output mismatch p.{page} #{number}")
                    verified += 1
        self.assertEqual(verified, 25)

    # All remaining tests are REVISION-ONLY SYNTHETIC TESTS, not official answers.
    def test_synthetic_p47_window_boundaries(self):
        self.assertEqual(source_namespace(47, 1)["longest_unique"]("abba"), 2)
        self.assertEqual(source_namespace(47, 1)["longest_unique"](""), 0)
        shortest = source_namespace(47, 2)["shortest_with_sum"]
        self.assertEqual(shortest([1, 1, 4], 4), 1)
        self.assertEqual(shortest([1, 2], 9), 0)

    def test_synthetic_p48_brackets_and_strictly_higher(self):
        balanced = source_namespace(48, 1)["balanced"]
        self.assertFalse(balanced("([)]"))
        self.assertTrue(balanced(""))
        higher = source_namespace(48, 2)["days_until_higher"]
        self.assertEqual(higher([5, 5, 4]), [0, 0, 0])
        self.assertEqual(higher([1, 3, 3, 4]), [1, 2, 1, 0])

    def test_synthetic_p49_empty_merge_and_cycle_free(self):
        scope = source_namespace(49, 3)
        self.assertEqual(scope["build"]([]), None)
        merged = scope["merge"](scope["build"]([]), scope["build"]([2, 5]))
        self.assertEqual([merged.value, merged.next.value], [2, 5])
        self.assertIsNone(merged.next.next)
        cycle = source_namespace(49, 2)
        self.assertFalse(cycle["has_cycle"](None))

    def test_synthetic_p50_lower_bound_absence_and_ties(self):
        lower = source_namespace(50, 1)["lower_bound"]
        self.assertEqual(lower([], 2), 0)
        self.assertEqual(lower([1, 2, 2, 4], 2), 1)
        self.assertEqual(lower([1, 2, 2, 4], 5), 4)

    def test_synthetic_p51_sorting_duplicates_and_zero(self):
        merge_sort = source_namespace(51, 1)["merge_sort"]
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([3, -1, 3, 2]), [-1, 2, 3, 3])
        largest = source_namespace(51, 3)["largest_number"]
        self.assertEqual(largest([0, 0, 0]), "0")

    def test_synthetic_p52_recursion_empty_and_small(self):
        depth = source_namespace(52, 1)["depth"]
        self.assertEqual(depth({}), 0)
        self.assertEqual(depth([{}]), 1)
        subsets = source_namespace(52, 2)["subsets"]
        self.assertEqual(subsets([]), [[]])
        brackets = source_namespace(52, 4)["valid_brackets"]
        self.assertEqual(brackets(2), ["(())", "()()"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
