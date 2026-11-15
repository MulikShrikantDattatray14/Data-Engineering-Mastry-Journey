#!/usr/bin/env python3
"""Bounded independent review of private Bosscoder Refresher-2 PDF pages 1–3.

The original 11-page PDF was visually inspected in its private ChatGPT Library.
It is NOT committed or accessible in public CI. Small observed shape facts below
are reimplemented by the auditor, not copies of original notebook cells,
official assignment answers, or independently completed learner exercises.

Private PDF provenance from previous independent audit:
SHA256 09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-02"
SOURCE_PINS = {
    "01-patterns-and-nested-loops.md": "0cdb98ea14fb53ee0dcc0fbe20e810d3de178bbe",
    "assignments/q03-hollow-square.md": "7a1be61fc9ca0ade2e14647f951f9b335a88f3a1",
}
PDF_SHA256 = "09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010"

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def rectangle(rows: int, cols: int) -> str:
    # Auditor-authored concise equivalent of the visible nested-loop output.
    return "".join("*" * max(0, cols) + "\n" for _ in range(max(0, rows)))

def stair(height: int, reverse: bool = False) -> str:
    seq = range(height, 0, -1) if reverse else range(1, height + 1)
    return "".join("*" * width + "\n" for width in seq)

def pyramid(height: int) -> str:
    return "".join(" " * (height - i) + "*" * (2 * i - 1) + "\n"
                   for i in range(1, height + 1))

def diamond(height: int) -> str:
    up = pyramid(height)
    down = "".join(" " * (height - i) + "*" * (2 * i - 1) + "\n"
                   for i in range(height - 1, 0, -1))
    return up + down

def hollow_spaced(height: int) -> str:
    # Mirrors *displayed PDF p.3's spacing*, not archived Journey's compact '#'.
    if height <= 0:
        return ""
    return "".join("".join(("*" if i in (0, height - 1)
                            or j in (0, height - 1) else " ") + " "
                           for j in range(height)) + "\n"
                   for i in range(height))

def hollow_compact(height: int, mark: str) -> str:
    return "".join("".join(mark if i in (0, height - 1)
                            or j in (0, height - 1) else " "
                           for j in range(height)) + "\n"
                   for i in range(height))

class OriginalPdfPages1To3PatternContracts(unittest.TestCase):
    def test_01_archived_note_and_assignment_still_git_blob_identical(self):
        for rel, sha in SOURCE_PINS.items():
            with self.subTest(path=rel):
                self.assertEqual(git_blob_sha((ARCHIVE / rel).read_bytes()), sha)

    def test_02_original_assignment_q03_remains_unsolved_and_n_is_bounded(self):
        source = (ARCHIVE / "assignments/q03-hollow-square.md").read_text()
        self.assertIn("**Attempt:** Pending", source)
        self.assertIn("**Academy platform completion:** Unverified", source)
        self.assertIn("1≤N≤10", source)

    def test_03_fixed_single_row_and_three_by_five_p1(self):
        self.assertEqual(rectangle(1, 5), "*****\n")
        self.assertEqual(rectangle(3, 5), "*****\n" * 3)

    def test_04_p1_example_four_by_two_vs_executed_input_five_by_six(self):
        # The task prose illustrates 4x2; its visible executed input is 5,6.
        self.assertEqual(rectangle(4, 2), "**\n" * 4)
        self.assertEqual(rectangle(5, 6), "******\n" * 5)
        self.assertNotEqual(rectangle(4, 2), rectangle(5, 6))

    def test_05_rectangle_degenerate_dimensions_not_assigned_coursework(self):
        self.assertEqual(rectangle(0, 6), "")
        self.assertEqual(rectangle(3, 0), "\n\n\n")
        self.assertEqual(rectangle(3, -2), "\n\n\n")
        self.assertEqual(rectangle(-1, 4), "")

    def test_06_p2_increasing_five_row_stair(self):
        self.assertEqual(stair(5), "*\n**\n***\n****\n*****\n")

    def test_07_p2_reverse_fifteen_row_stair(self):
        result = stair(15, True).splitlines()
        self.assertEqual(len(result), 15)
        self.assertEqual([len(s) for s in result], list(range(15, 0, -1)))
        self.assertEqual(result[0], "*" * 15)
        self.assertEqual(result[-1], "*")

    def test_08_p2_p3_seven_row_pyramid_visible_geometry(self):
        lines = pyramid(7).splitlines()
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[0], "      *")
        self.assertEqual(lines[-1], "*" * 13)
        for idx, line in enumerate(lines, 1):
            self.assertEqual(len(line) - len(line.lstrip(" ")), 7 - idx)
            self.assertEqual(line.count("*"), 2 * idx - 1)

    def test_09_p2_six_row_diamond_has_eleven_visible_rows(self):
        lines = diamond(6).splitlines()
        self.assertEqual(len(lines), 11)
        self.assertEqual(lines[0], "     *")
        self.assertEqual(lines[5], "*" * 11)
        self.assertEqual(lines[-1], "     *")
        self.assertEqual(lines, list(reversed(lines)))

    def test_10_diamond_small_height_boundary_and_no_double_center(self):
        self.assertEqual(diamond(1), "*\n")
        self.assertEqual(diamond(2), " *\n***\n *\n")
        self.assertEqual(diamond(0), "")
        for n in range(1, 12):
            self.assertEqual(len(diamond(n).splitlines()), 2 * n - 1)

    def test_11_p3_six_row_hollow_square_visible_spacing(self):
        lines = hollow_spaced(6).splitlines()
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines[0], "* * * * * * ")
        self.assertEqual(lines[-1], lines[0])
        self.assertEqual(lines[1], "*         * ")
        self.assertEqual(lines[1:-1], ["*         * "] * 4)

    def test_12_p3_hollow_square_one_two_and_zero_boundaries(self):
        self.assertEqual(hollow_spaced(1), "* \n")
        self.assertEqual(hollow_spaced(2), "* * \n* * \n")
        self.assertEqual(hollow_spaced(0), "")

    def test_13_p3_rendered_whitespace_vs_raw_python_stdout(self):
        # The PDF renders stars and gaps; it does not prove trailing-space bytes.
        raw = hollow_spaced(6)
        self.assertTrue(all(line.endswith(" ") for line in raw.splitlines()))
        self.assertTrue(raw.endswith("\n"))
        self.assertEqual(raw.splitlines()[0].rstrip(), "* * * * * *")

    def test_14_p3_original_pdf_vs_rephrased_archive_and_assignment(self):
        # p3 is spaced '*' while archived teaching note uses compact '#'.
        # The pending assignment example is compact '*'; do not call them
        # byte-exact identical or treat this test as solving that assignment.
        pdf = hollow_spaced(4)
        journey = hollow_compact(4, "#")
        assignment_example = hollow_compact(4, "*")
        self.assertNotEqual(pdf, journey)
        self.assertNotEqual(pdf, assignment_example)
        self.assertEqual(assignment_example, "****\n*  *\n*  *\n****\n")
        self.assertEqual(pdf.replace(" ", "").splitlines()[0], "****")

    def test_15_finite_shape_counts_independent_oracle(self):
        # 81 reviewer-only boundary cases: not hosted Colab/Academy grading.
        for n in range(1, 10):
            for m in range(1, 10):
                with self.subTest(n=n, m=m):
                    text = rectangle(n, m)
                    self.assertEqual(text.count("*"), n * m)
                    self.assertEqual(text.count("\n"), n)
        for n in range(1, 10):
            self.assertEqual(stair(n).count("*"), n * (n + 1) // 2)
            self.assertEqual(pyramid(n).count("*"), n * n)
            self.assertEqual(diamond(n).count("*"), 2 * n * n - 2 * n + 1)
            self.assertEqual(hollow_spaced(n).count("*"),
                             1 if n == 1 else 4 * n - 4)

if __name__ == "__main__":
    unittest.main(verbosity=2)
