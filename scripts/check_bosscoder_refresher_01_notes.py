"""Read-only execution/inventory audit of archived Bosscoder Refresher-1 *derived notes*.

Checks archived independent Journey lesson-note code against the printed/expected
results and individually pins twelve paraphrased assignment records. This is
NOT a run of the proprietary 13-page original academy PDF, platform grading,
official answer verification, or a learner's solved assignment.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder"
LESSONS = {
    "lecture-01/01-basics-and-types.md": ("cdbc0cd8cf013e06596ba1b0ea21b221dd64f25d", 10),
    "lecture-01/02-operators-and-slicing.md": ("5757682e6e90e91d7f0901fac93d204ee8047c53", 10),
    "lecture-01/03-control-flow-and-practice.md": ("3770ffc1e58b3d27cd72b71c7b5defc3ada3d97b", 7),
}
ASSIGNMENTS = {
    "refresher-1-q01-even-odd.md": "32a5083078b54df0d1f9dcabaffad62f25a4fa0b",
    "refresher-1-q02-leap-year.md": "12e283590b5a17fe3adfb8ff90e04c7b2444c2f3",
    "refresher-1-q03-maximum-integer.md": "77df82be9da103c269350c87ceee1b798dc55301",
    "refresher-1-q04-check-positive.md": "fde63f9bf512c28d08b12efd2706e178f89ce3b9",
    "refresher-1-q05-multiple-of-three.md": "2287d8db1992cedd1e2e60a045c4b94f0308677e",
    "refresher-1-q06-multiple-of-five.md": "f8d9cf397fcd90ad5ec2af4b45434a3b4e4bd1bc",
    "refresher-1-q07-positive-number-count.md": "c4921902ee8d312ab4bf3d1a0aec3b5489fceab6",
    "refresher-1-q08-length-of-last-word.md": "8531637b58825c933c7fccbe6c7e3bf86b4805a6",
    "refresher-1-q09-palindrome-number.md": "c37b5373dd45781953d139ea31b86d7823986f71",
    "refresher-1-q10-factorial-recursion.md": "d4c9f2cde6e9b3954bf16a6f6a99a701578167ec",
    "refresher-1-q11-reverse-integer.md": "a76c70d01531821c6801ac8c20f4f74c8e5c0035",
    "refresher-1-q12-armstrong-number.md": "4067fa0f0f82b158d7813b3fa64c7c70adea460c",
}
FENCE = re.compile(r"(?ms)^" + re.escape(chr(96) * 3) +
                   r"python[ \t]*\n(.*?)^" + re.escape(chr(96) * 3) + r"[ \t]*$")
# Exact transcript contracts for deterministic blocks; others checked separately.
EXACT = {
    (1, 0): "Hello, data engineering!\n",
    (1, 2): "3 2 {'order_id': 101, 'amount': 500, 'status': 'paid'}\n",
    (1, 3): "str bytes\ncafé\n",
    (1, 4): "Asha 28\n10 10 10 7 3\n",
    (1, 5): "[1, 2, 3]\n",
    (1, 6): "101 pending\npaid\n",
    (1, 7): "The name is no longer defined\n",
    (2, 0): "22\n12\n85\n3.4\n3\n2\n1419857\n",
    (2, 1): "False\nTrue\nTrue\nFalse\nTrue\nFalse\n",
    (2, 2): "6.0\n",
    (2, 3): "False\nTrue\nTrue\n",
    (2, 4): "2\n7\n5\n-7\n12\n3\n",
    (2, 5): "True\nTrue\n",
    (2, 6): "True\nFalse\nTrue\n",
    (2, 7): "7.5\nfloat\n",
    (2, 9): "p\ne\npipe\npeline\nppln\nenilepip\npipeline\n",
    (3, 0): "moderate\n",
    (3, 1): "101\n102\n103\n104\nPAID\nPENDING\nCANCELLED\n",
    (3, 2): "Attempt 1\nAttempt 2\nAttempt 3\n",
    (3, 3): "2\n4\n",
    (3, 4): "No failures found\n",
    (3, 5): "finished\n",
}
# 22 literal outputs, 3 descriptive stdout checks + 1 no-output structural
# check + 1 counted but deliberately unexecuted interactive-input example.
DYNAMIC = {(1, 1), (1, 8), (2, 8), (3, 6)}
SKIPPED = {(1, 9)}


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def get_blocks(lesson_index: int) -> list[str]:
    key = list(LESSONS)[lesson_index - 1]
    path = BASE / key
    sha, count = LESSONS[key]
    assert blob_sha(path) == sha, f"Original archived note changed: {key}"
    blocks = [m.group(1).strip("\n") for m in FENCE.finditer(path.read_text(encoding="utf-8"))]
    assert len(blocks) == count, f"{key}: expected {count}, found {len(blocks)}"
    for index, code in enumerate(blocks):
        compile(code, f"{key}::block-{index}", "exec")
    return blocks


def run_original_note_block(lesson: int, index: int) -> str:
    assert (lesson, index) not in SKIPPED
    code = get_blocks(lesson)[index]
    process = subprocess.run([sys.executable, "-I", "-B", "-c", code],
                             text=True, capture_output=True, timeout=5, check=False)
    assert process.returncode == 0, (lesson, index, process.stdout, process.stderr)
    assert process.stderr == "", (lesson, index, process.stderr)
    return process.stdout


class RefresherOneSourceAudit(unittest.TestCase):
    def test_note_code_inventory_and_assignment_archive(self):
        self.assertEqual([len(get_blocks(i)) for i in (1, 2, 3)], [10, 10, 7])
        self.assertEqual(len(EXACT), 22)
        self.assertEqual(len(DYNAMIC), 4)
        self.assertEqual(len(SKIPPED), 1)
        self.assertEqual(len(EXACT) + len(DYNAMIC) + len(SKIPPED), 27)
        for filename, pinned_sha in ASSIGNMENTS.items():
            with self.subTest(assignment=filename):
                path = BASE / "assignments" / filename
                self.assertEqual(blob_sha(path), pinned_sha)
                body = path.read_text(encoding="utf-8")
                self.assertIn("## Learning record", body)
                self.assertRegex(body.lower(), r"pending|not attempted|unverified")
                self.assertNotIn("**Status:** Solved", body)
        self.assertEqual(len(ASSIGNMENTS), 12)

    def test_dynamic_note_outputs_and_unrun_input(self):
        value_types = run_original_note_block(1, 1).splitlines()
        self.assertEqual(len(value_types), 11)
        self.assertEqual([s.split()[-1] for s in value_types],
                         ["int", "float", "complex", "bool", "str", "list", "tuple",
                          "set", "frozenset", "dict", "bytes"])
        keyword_lines = run_original_note_block(1, 8).splitlines()
        self.assertEqual(keyword_lines[:2], ["True", "False"])
        self.assertGreaterEqual(int(keyword_lines[2]), 30)
        casts = run_original_note_block(2, 8).splitlines()
        self.assertEqual(casts[0:5], ["42", "12.75", "123", "['a', 'b', 'c']", "(1, 2)"])
        self.assertIn("1", casts[5])
        self.assertIn("2", casts[5])
        self.assertEqual(casts[6:], ["{'a': 10, 'b': 20}", "True"])
        self.assertEqual(run_original_note_block(3, 6), "")
        self.assertIn("orders = [", get_blocks(3)[6])
        self.assertIn("input(", get_blocks(1)[9])
        # Input example is compiled but deliberately NOT executed; it requires
        # a human-supplied stdin contract absent from the archived notes.

    def test_four_synthetic_concept_boundaries(self):
        # Auditor-authored calculations, not graded assignment submissions.
        self.assertEqual((-7 // 3, -7 % 3), (-3, 2))
        self.assertEqual((bool("False"), bool("")), (True, False))
        a, b = [10], [10]
        self.assertTrue(a == b)
        self.assertFalse(a is b)
        for items, expected in [([1, 2, 3], "normal"), ([1, 0, 3], "break")]:
            result = "normal"
            for item in items:
                if item == 0:
                    result = "break"
                    break
            self.assertEqual(result, expected)


def make_literal_test(lesson: int, index: int, transcript: str):
    def case(self):
        self.assertEqual(run_original_note_block(lesson, index), transcript)
    return case


for (_lesson, _index), _expected in EXACT.items():
    setattr(RefresherOneSourceAudit, f"test_note_l{_lesson:02d}_block_{_index:02d}",
            make_literal_test(_lesson, _index, _expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
