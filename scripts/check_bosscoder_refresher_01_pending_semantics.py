"""Reviewer-only bounded semantics for four PENDING Bosscoder Refresher-1 tasks.

Not original Academy answer execution, private screenshot/PDF parity, a learner
solution, a graded submission, or proof of mastery. Archived records are read-only.
"""
from __future__ import annotations

import calendar
import hashlib
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments"
RECORDS = {
    "refresher-1-q02-leap-year.md": "12e283590b5a17fe3adfb8ff90e04c7b2444c2f3",
    "refresher-1-q10-factorial-recursion.md": "d4c9f2cde6e9b3954bf16a6f6a99a701578167ec",
    "refresher-1-q11-reverse-integer.md": "a76c70d01531821c6801ac8c20f4f74c8e5c0035",
    "refresher-1-q12-armstrong-number.md": "4067fa0f0f82b158d7813b3fa64c7c70adea460c",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


# Independently authored reviewer models; never placed into learner source files.
def leap_arithmetic(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def reverse_arithmetic(n: int) -> int:
    result = 0
    while n:
        result = result * 10 + n % 10
        n //= 10
    return result


def armstrong_arithmetic(n: int) -> bool:
    digits = len(str(n))
    remaining, total = n, 0
    while remaining:
        remaining, digit = divmod(remaining, 10)
        total += digit ** digits
    return total == n


def factorial_recursion(n: int) -> int:
    if n == 1:
        return 1
    return n * factorial_recursion(n - 1)


class RefresherOnePendingReviewerAudit(unittest.TestCase):
    def test_original_records_pinned_and_pending(self):
        for name, sha in RECORDS.items():
            with self.subTest(name=name):
                data = (SOURCE / name).read_bytes()
                self.assertEqual(git_blob_sha(data), sha)
                body = data.decode("utf-8")
                self.assertIn("## Learning record", body)
                self.assertRegex(body.lower(), r"(pending|not attempted)")
                self.assertNotIn("**Status:** Solved", body)

    def test_q02_every_year_in_inclusive_constraint(self):
        # Independent stdlib Gregorian calendar oracle, not the Academy answer.
        self.assertEqual((leap_arithmetic(2000), leap_arithmetic(2017)), (True, False))
        for year in range(1700, 9001):
            self.assertEqual(leap_arithmetic(year), calendar.isleap(year), year)
        for year, expected in [(1700, False), (1800, False), (1900, False),
                               (2000, True), (2024, True), (2100, False),
                               (2400, True), (9000, False)]:
            self.assertEqual(leap_arithmetic(year), expected)
        print("Q02 PASS: 7301 candidate years vs calendar.isleap")

    def test_q11_every_integer_in_inclusive_constraint(self):
        self.assertEqual((reverse_arithmetic(25), reverse_arithmetic(71)), (52, 17))
        for n in range(1, 10001):
            self.assertEqual(reverse_arithmetic(n), int(str(n)[::-1]), n)
        self.assertEqual(reverse_arithmetic(10000), 1)
        print("Q11 PASS: 10000 candidate integers vs independent text reversal")

    def test_q12_every_integer_in_inclusive_constraint(self):
        self.assertEqual((armstrong_arithmetic(371), armstrong_arithmetic(71)), (True, False))
        accepted = set()
        for n in range(1, 10001):
            independent = sum(int(ch) ** len(str(n)) for ch in str(n)) == n
            self.assertEqual(armstrong_arithmetic(n), independent, n)
            if independent:
                accepted.add(n)
        self.assertEqual(accepted, set(range(1, 10)) | {153, 370, 371, 407, 1634, 8208, 9474})
        print("Q12 PASS: 10000 candidate integers, 16 matching positives")

    def test_q10_recursion_small_and_moderate_inputs(self):
        self.assertEqual((factorial_recursion(2), factorial_recursion(5)), (2, 120))
        for n in range(1, 201):
            self.assertEqual(factorial_recursion(n), math.factorial(n), n)
        print("Q10 PASS: 200 candidate recursive values vs math.factorial")

    def test_q10_maximum_input_runtime_contract_is_unresolved(self):
        # Isolated CPython probe. A controlled 1000-frame recursion ceiling
        # demonstrates why upper-bound support cannot be assumed for recursion.
        probe = """import sys, math
sys.setrecursionlimit(1000)
def f(n):
    return 1 if n == 1 else n * f(n-1)
try:
    f(10000)
except RecursionError:
    print('RECURSION_LIMIT_REPRODUCED')
else:
    raise AssertionError('unexpected unlimited naive recursion')
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
print('FACTORIAL_10000_DECIMAL_DIGITS', len(str(math.factorial(10000))))
"""
        done = subprocess.run([sys.executable, "-I", "-B", "-c", probe],
                              check=True, text=True, capture_output=True, timeout=20)
        self.assertEqual(done.stderr, "")
        self.assertEqual(done.stdout.splitlines(),
                         ["RECURSION_LIMIT_REPRODUCED", "FACTORIAL_10000_DECIMAL_DIGITS 35660"])
        print("Q10 PASS: 1000-frame recursion failure and 35660-digit size reproduced; "
              "Academy runtime/format UNKNOWN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
