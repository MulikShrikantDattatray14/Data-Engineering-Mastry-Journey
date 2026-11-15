#!/usr/bin/env python3
"""Read-only Bosscoder Python Refresher 2 source-companion reviewer.

Original lecture snippets are executed verbatim in isolated namespaces.
Pending graded assignment *statements* are checked, not solved/submitted.
The SHA pins refer to preserved Git blobs, not independent Academy PDFs.
"""
import ast
import contextlib
import hashlib
import io
import itertools
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-02")
SOURCES = {
    "patterns": ("01-patterns-and-nested-loops.md", "0cdb98ea14fb53ee0dcc0fbe20e810d3de178bbe", 5),
    "lists": ("02-lists-and-strings.md", "fb88fbd9bfa142fca6fc48b03638c21b5fa307fa", 4),
    "collections": ("03-tuples-sets-dictionaries.md", "0177eb35b9a3c8440407e9da17fd913185e227ff", 4),
}
ASSIGNMENTS = {
    "q01": ("q01-alphabet-triangle.md", "ad53f8699c8f15a9b6e5f8ce0742a3001c3f046f"),
    "q02": ("q02-inverted-star-triangle.md", "8f154967ea2c4615347818dba135c3988ab0e4ee"),
    "q03": ("q03-hollow-square.md", "7a1be61fc9ca0ade2e14647f951f9b335a88f3a1"),
    "q04": ("q04-132-pattern.md", "107db65ad457f4fac5ba0d0c0216b5fed744bf5a"),
}
INDEX_SHA = "5d16545ba612c210fd46ea560e20753edb3e6468"

# These output strings were independently transcribed from the visible
# literal code (the companion chapters do not publish output fences).
# A None entry is intentionally verified as a set, with order ignored.
PRINTS = {
    "patterns": [
        "####\n####\n####\n",
        "#\n##\n###\n####\n####\n###\n##\n#\n",
        "   ^\n  ^^^\n ^^^^^\n^^^^^^^\n",
        "  ^\n ^^^\n^^^^^\n ^^^\n  ^\n",
        "####\n#  #\n#  #\n####\n",
    ],
    "lists": [
        "101 103 [101, 102]\n",
        "2\nmelon ['plum', 'pear', 'kiwi', 'date', 'apple']\n[]\n",
        "Order ReadyOrder Ready True\nE\nT\nL\n",
        "paid|pending|paid\nABCabc\n2 4\nTrue True True\n0007 ..x..\nrows=3 rows=3\n",
    ],
    "collections": [
        "2 3\n4 2 5 (1, 2)\n",
        "1 paid\n2 pending\n",
        None,
        "{'name': 'Asha', 'age': 26, 'city': 'Pune'} {'name': 'Asha', 'age': 26}\n",
    ],
}

def read_pinned(path, sha):
    raw = (ROOT / BASE / path).read_bytes()
    blob_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob_hash != sha:
        raise AssertionError(f"Immutable source blob changed: {path} ({blob_hash})")
    return raw.decode("utf-8")

def fences(text):
    fence = re.escape(chr(96) * 3)
    return re.findall(fence + r"python[ \t]*\n(.*?)\n" + fence, text, re.S)

def capture_original(code):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(code, "<original-lecture-02-fence>", "exec"), {"__name__": "__audit__"})
    return output.getvalue()

def short_witness(nums):
    # Reviewer-only finite sample oracle; intentionally NOT an efficient
    # learner answer for the source constraint n <= 200,000.
    return any(nums[i] < nums[k] < nums[j]
               for i in range(len(nums))
               for j in range(i + 1, len(nums))
               for k in range(j + 1, len(nums)))

class SourceAndExamples(unittest.TestCase):
    def test_original_three_chapter_blob_hashes(self):
        for key, (path, sha, _) in SOURCES.items():
            with self.subTest(chapter=key):
                self.assertTrue(read_pinned(Path(path), sha).startswith("# "))

    def test_13_original_python_fence_inventory(self):
        for key, (path, sha, count) in SOURCES.items():
            with self.subTest(chapter=key):
                self.assertEqual(len(fences(read_pinned(Path(path), sha))), count)

    def test_every_original_python_fence_parses(self):
        for key, (path, sha, _) in SOURCES.items():
            for index, code in enumerate(fences(read_pinned(Path(path), sha)), 1):
                with self.subTest(chapter=key, fence=index):
                    compile(code, f"{path}#{index}", "exec")

    def test_all_13_original_python_fences_replay(self):
        seen = 0
        for key, (path, sha, _) in SOURCES.items():
            for index, code in enumerate(fences(read_pinned(Path(path), sha))):
                with self.subTest(chapter=key, fence=index + 1):
                    actual = capture_original(code)
                    expected = PRINTS[key][index]
                    if expected is None:
                        self.assertEqual([ast.literal_eval(s) for s in actual.splitlines()],
                                         [{1, 2, 3, 4}, {3}, {1, 2}, {1, 2, 4}])
                    else:
                        self.assertEqual(actual, expected)
                    seen += 1
        self.assertEqual(seen, 13)

    def test_four_source_assignment_hashes_and_pending_attempts(self):
        for key, (path, sha) in ASSIGNMENTS.items():
            with self.subTest(question=key):
                text = read_pinned(Path("assignments") / path, sha)
                self.assertIn("**Attempt:** Pending", text)
                self.assertIn("**Reviewed:** Pending", text)
                self.assertIn("**Academy platform completion:** Unverified", text)
                self.assertIn("## Review checklist", text)

    def test_source_assignment_index_remains_pending(self):
        text = read_pinned(Path("assignments/README.md"), INDEX_SHA)
        self.assertIn("0/4 independently solved or reviewed", text)
        self.assertEqual(text.count("| Pending |"), 4)
        self.assertIn("Solutions withheld", text)

    def test_q01_alphabet_example_contract(self):
        text = read_pinned(Path("assignments") / ASSIGNMENTS["q01"][0], ASSIGNMENTS["q01"][1])
        self.assertIn("N=4: a / ab / abc / abcd", text)
        self.assertIn("1≤N≤10", text)
        for n in range(1, 11):
            rows = ["".join(chr(97 + c) for c in range(row)) for row in range(1, n + 1)]
            self.assertEqual(len(rows), n)
            self.assertEqual([len(r) for r in rows], list(range(1, n + 1)))
            self.assertTrue(all(row.startswith("a") for row in rows))

    def test_q02_inverted_star_example_contract(self):
        text = read_pinned(Path("assignments") / ASSIGNMENTS["q02"][0], ASSIGNMENTS["q02"][1])
        self.assertIn("N=4: **** / *** / ** / *", text)
        for n in range(1, 11):
            lengths = list(range(n, 0, -1))
            self.assertEqual(sum(lengths), n * (n + 1) // 2)
            self.assertEqual(lengths[-1], 1)

    def test_q03_hollow_square_example_contract(self):
        text = read_pinned(Path("assignments") / ASSIGNMENTS["q03"][0], ASSIGNMENTS["q03"][1])
        self.assertIn("N=4: **** / *  * / *  * / ****", text)
        for n in range(1, 11):
            rows = ["".join("*" if r in (0, n - 1) or c in (0, n - 1) else " "
                            for c in range(n)) for r in range(n)]
            self.assertEqual([len(row) for row in rows], [n] * n)
            self.assertEqual(sum(row.count("*") for row in rows),
                             1 if n == 1 else 4 * (n - 1))
            self.assertEqual(rows[0], "*" * n)

    def test_q04_132_sample_witness_contract(self):
        text = read_pinned(Path("assignments") / ASSIGNMENTS["q04"][0], ASSIGNMENTS["q04"][1])
        self.assertIn("i<j<k", text)
        self.assertIn("1≤n≤200000", text)
        self.assertIn("-10^9≤nums[i]≤10^9", text)
        self.assertFalse(short_witness([1, 2, 3, 4]))
        self.assertTrue(short_witness([3, 1, 4, 2]))
        self.assertTrue(short_witness([-1, 3, 2, 0]))

    def test_132_strict_and_ordered_counterexamples(self):
        for numbers, expected in [
            ([1], False), ([1, 1, 1], False), ([1, 3, 3], False),
            ([3, 2, 1], False), ([1, 3, 2], True), ([3, 1, 9, 4, 2], True),
            ([-10**9, 10**9, 0], True),
        ]:
            with self.subTest(numbers=numbers):
                self.assertIs(short_witness(numbers), expected)

    def test_132_finite_reviewer_oracle_small_tuples(self):
        # 3^1 + ... + 3^5 = 363 reviewer-only tiny arrays. No platform grading.
        arrays = 0
        yes = 0
        for n in range(1, 6):
            for case in itertools.product((-1, 0, 1), repeat=n):
                outcome = short_witness(case)
                self.assertEqual(outcome, any(case[i] < case[k] < case[j]
                                              for i, j, k in itertools.combinations(range(n), 3)))
                arrays += 1
                yes += int(outcome)
        self.assertEqual(arrays, 363)
        self.assertGreater(yes, 0)

    def test_python3_cmp_not_callable(self):
        # Archived note correctly flags legacy Python 2 cmp() as unavailable.
        with self.assertRaises(NameError):
            eval("cmp((1, 2), (1, 3))", {"__builtins__": {}})

    def test_list_mutation_is_independent_of_prior_code_fences(self):
        self.assertEqual(capture_original(fences(read_pinned(
            Path(SOURCES["lists"][0]), SOURCES["lists"][1]))[1]),
            PRINTS["lists"][1])

    def test_tuple_nested_mutability_caveat(self):
        embedded = (1, [2, 3])
        embedded[1].append(4)
        self.assertEqual(embedded, (1, [2, 3, 4]))
        with self.assertRaises(TypeError):
            hash(embedded)

    def test_set_output_has_no_order_requirement(self):
        output = capture_original(fences(read_pinned(
            Path(SOURCES["collections"][0]), SOURCES["collections"][1]))[2])
        self.assertEqual(len(output.splitlines()), 4)
        self.assertTrue(all(isinstance(ast.literal_eval(line), set)
                            for line in output.splitlines()))

if __name__ == "__main__":
    unittest.main(verbosity=2)
