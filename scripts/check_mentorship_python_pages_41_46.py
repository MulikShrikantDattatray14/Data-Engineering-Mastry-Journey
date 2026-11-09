"""Read-only independent source audit: mentorship DSA PDF pages 41–46.

The original archived Markdown and its published stdout are read at test time:
no example solutions or expected outputs are reconstructed by this checker.
The additional explicitly synthetic edge checks are reviewer-authored, NOT
official course answers or independently solved learner assignments.
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
# PDF page: exact preserved source filename, pinned Git blob SHA, linked example count
LESSONS = {
    41: ("01. Big-O in plain words.md", "d4d65ea509be56ee9dba6845f30ec4ffe9e3e668", 3),
    42: ("02. Space complexity.md", "b713f5865c894dbfa1295f8c6ec2b1ac3b963c10", 4),
    43: ("03. Time versus space trade-offs.md", "aadac5bde7e76de73454b2b449445503d233ce10", 3),
    44: ("04. What Python operations cost.md", "828b7cf28e0852d8041f9b42a35b26934dac26d1", 3),
    45: ("05. Arrays and strings with two pointers.md", "4d92eab2014270c728cd4a4b077ef426f87bd617", 5),
    46: ("06. Hashing.md", "4711d0c8b1e6cc7823776c988287ce273cb33fe0", 5),
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
    assert blob_sha(raw) == expected_sha, f"Archived source changed p.{page}: {filename}"
    content = raw.decode("utf-8-sig")
    links = list(LINK.finditer(content))
    found: dict[int, tuple[str, str]] = {}
    for index, match in enumerate(links):
        lesson, snippet = map(int, match.groups())
        assert lesson == page - 40, f"Unexpected original lesson ID on p.{page}"
        end = links[index + 1].start() if index + 1 < len(links) else len(content)
        region = content[match.end():end]
        code = PYTHON.search(region)
        shown = TEXT.search(region)
        assert code is not None and shown is not None, f"Unpaired p.{page} snippet {snippet}"
        assert snippet not in found, f"Duplicate p.{page} snippet {snippet}"
        found[snippet] = (code.group(1).strip("\n"), shown.group(1).strip("\n"))
    assert sorted(found) == list(range(1, count + 1)), (
        f"Source inventory mismatch p.{page}: {sorted(found)} != 1..{count}"
    )
    return found


def canonical_stdout(output: str) -> str:
    # Ignore only layout-related leading/trailing newlines and line-end blanks.
    return "\n".join(row.rstrip() for row in output.strip("\n").splitlines())


def run_archived(code: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="mentor-dsa41-46-") as tmp:
        script = Path(tmp) / "original_snippet.py"
        script.write_text(code + "\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-I", "-B", str(script)], cwd=tmp, input="",
            text=True, capture_output=True, timeout=15, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )


def source_namespace(page: int, snippet: int) -> dict:
    """Load the ORIGINAL function definitions plus sample invocations.

    These independent boundary assertions are intentionally *not* official
    source expected outputs; the original snippet itself is not edited.
    """
    code, _ = linked_examples(page)[snippet]
    namespace: dict = {"__name__": "audited_source"}
    exec(compile(code, f"archived-p{page}-example-{snippet}", "exec"), namespace)
    return namespace


class MentorshipDSAPages41To46(unittest.TestCase):
    def test_all_six_pinned_source_hashes_and_23_links(self):
        self.assertEqual(list(LESSONS), list(range(41, 47)))
        self.assertEqual([row[2] for row in LESSONS.values()], [3, 4, 3, 3, 5, 5])
        self.assertEqual(sum(row[2] for row in LESSONS.values()), 23)
        for page, row in LESSONS.items():
            with self.subTest(page=page):
                self.assertEqual(len(linked_examples(page)), row[2])

    def test_all_23_archived_code_outputs(self):
        checked = 0
        for page in LESSONS:
            for number, (code, displayed) in linked_examples(page).items():
                with self.subTest(source_pdf_page=page, linked_example=number):
                    process = run_archived(code)
                    self.assertEqual(process.returncode, 0,
                                     f"p.{page} #{number}: {process.stderr}")
                    self.assertEqual(canonical_stdout(process.stdout),
                                     canonical_stdout(displayed),
                                     f"Published output mismatch p.{page} #{number}")
                    self.assertEqual(process.stderr, "",
                                     f"Unexpected stderr p.{page} #{number}")
                    checked += 1
        self.assertEqual(checked, 23)

    # The following tests use deliberately invented boundary inputs.
    # Evidence tier: reviewer synthetic, NOT official-answer verified.
    def test_synthetic_p43_sorted_lookup_boundaries(self):
        lookup = source_namespace(43, 1)["contains_sorted"]
        self.assertFalse(lookup([], 99))
        self.assertFalse(lookup([1, 2, 3], 4))
        self.assertTrue(lookup([1, 3, 3], 3))

    def test_synthetic_p45_pair_requires_distinct_positions(self):
        pair = source_namespace(45, 1)["pair_with_sum"]
        self.assertIsNone(pair([5], 10))
        self.assertEqual(pair([5, 5], 10), (5, 5))
        self.assertIsNone(pair([], 100))

    def test_synthetic_p45_sorted_dedupe_empty_and_duplicates(self):
        dedupe = source_namespace(45, 2)["dedupe_sorted"]
        empty = []
        self.assertEqual(dedupe(empty), 0)
        self.assertEqual(empty, [])
        repeated = [7, 7, 7]
        self.assertEqual(dedupe(repeated), 1)
        self.assertEqual(repeated, [7])

    def test_synthetic_p46_two_sum_requires_two_records(self):
        solve = source_namespace(46, 1)["two_sum"]
        self.assertIsNone(solve([5], 10))
        self.assertEqual(solve([5, 5], 10), (0, 1))
        self.assertIsNone(solve([], 0))

    def test_synthetic_p46_prefix_count_with_negatives(self):
        solve = source_namespace(46, 3)["subarrays_with_sum"]
        self.assertEqual(solve([-1, 1, 0], 0), 3)
        self.assertEqual(solve([], 0), 0)
        self.assertEqual(solve([0, 0], 0), 3)

    def test_synthetic_p46_first_unique_none_case(self):
        solve = source_namespace(46, 4)["first_unique"]
        self.assertEqual(solve(["x", "y", "x"]), "y")
        self.assertIsNone(solve(["a", "a"]))
        self.assertIsNone(solve([]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
