"""Reviewer-only semantic boundary tests for eight pending Bosscoder Refresher-1 tasks.

Source snapshots are SHA-pinned and never mutated. These models are independently
authored by the auditor; no Academy supplied answer, platform grade or learner
solution is evaluated here. Hidden tests and original private screenshots remain
unavailable. See the adjacent additive evidence ledger for contract limitations.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments"
RECORDS = {
    "q01-even-odd": ("refresher-1-q01-even-odd.md", "32a5083078b54df0d1f9dcabaffad62f25a4fa0b"),
    "q03-maximum": ("refresher-1-q03-maximum-integer.md", "77df82be9da103c269350c87ceee1b798dc55301"),
    "q04-positive": ("refresher-1-q04-check-positive.md", "fde63f9bf512c28d08b12efd2706e178f89ce3b9"),
    "q05-divisible3": ("refresher-1-q05-multiple-of-three.md", "2287d8db1992cedd1e2e60a045c4b94f0308677e"),
    "q06-multiples5": ("refresher-1-q06-multiple-of-five.md", "f8d9cf397fcd90ad5ec2af4b45434a3b4e4bd1bc"),
    "q07-count-positive": ("refresher-1-q07-positive-number-count.md", "c4921902ee8d312ab4bf3d1a0aec3b5489fceab6"),
    "q08-last-word": ("refresher-1-q08-length-of-last-word.md", "8531637b58825c933c7fccbe6c7e3bf86b4805a6"),
    "q09-palindrome": ("refresher-1-q09-palindrome-number.md", "c37b5373dd45781953d139ea31b86d7823986f71"),
}

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

# Reviewer models use loop/branch forms; the assertions cross-check against
# separately expressed stdlib/math/string contracts rather than themselves.
def parity(n: int) -> bool:
    return n % 2 == 0

def greater(a: int, b: int) -> int:
    if a >= b:
        return a
    return b

def positive(n: int) -> bool:
    return n > 0

def divisible_three(n: int) -> bool:
    return n % 3 == 0

def multiples_five(n: int) -> list[int]:
    result = []
    value = 5
    while value <= n:
        result.append(value)
        value += 5
    return result

def count_positive(values: list[int]) -> int:
    count = 0
    for v in values:
        if v > 0:
            count += 1
    return count

def last_word_length(value: str) -> int:
    end = len(value) - 1
    while end >= 0 and value[end] == " ":
        end -= 1
    total = 0
    while end >= 0 and value[end] != " ":
        total += 1
        end -= 1
    return total

def palindrome_number(n: int) -> bool:
    if n < 0:
        return False
    original, reverse = n, 0
    while n:
        reverse = reverse * 10 + n % 10
        n //= 10
    return original == reverse

class RefresherOneRemainingReviewerAudit(unittest.TestCase):
    def test_source_pins_and_historical_pending_statuses(self):
        for ident, (filename, sha) in RECORDS.items():
            with self.subTest(id=ident):
                data = (SOURCE / filename).read_bytes()
                self.assertEqual(git_blob_sha(data), sha)
                text = data.decode("utf-8")
                self.assertIn("## Learning record", text)
                self.assertRegex(text.lower(), r"(pending|not attempted)")
                self.assertNotIn("**Status:** Solved", text)
        print("Q01/Q03-Q09 PASS: 8 immutable source blob pins; learner work still pending")

    def test_q01_parity_complete_integer_domain(self):
        self.assertIs(parity(4), True)
        self.assertIs(parity(7), False)
        for n in range(1, 10001):
            self.assertIs(parity(n), n in range(2, 10001, 2), n)
        self.assertEqual((parity(1), parity(10000)), (False, True))
        print("Q01 PASS: both source examples and all 10000 allowed integers")

    def test_q03_maximum_all_constraint_pairs(self):
        self.assertEqual((greater(2, 4), greater(7, 6)), (4, 7))
        for a, b in itertools.product(range(1, 11), repeat=2):
            self.assertEqual(greater(a, b), max((a, b)), (a, b))
        self.assertEqual(greater(5, 5), 5)
        print("Q03 PASS: both examples and all 100 allowed ordered pairs (incl. ties)")

    def test_q04_positive_every_allowed_integer(self):
        self.assertEqual((positive(7), positive(-17)), (True, False))
        for n in range(-10000, 10001):
            self.assertIs(positive(n), (1 <= n <= 10000), n)
        self.assertEqual((positive(-10000), positive(0), positive(10000)), (False, False, True))
        print("Q04 PASS: both examples, zero and all 20001 allowed integers")

    def test_q05_divisible_three_every_allowed_integer(self):
        self.assertEqual((divisible_three(9), divisible_three(17)), (True, False))
        for n in range(-10000, 10001):
            # Independent multiplication/division identity; negative numbers included.
            expected = (n // 3) * 3 == n
            self.assertIs(divisible_three(n), expected, n)
        self.assertEqual((divisible_three(-9), divisible_three(0), divisible_three(-10000)),
                         (True, True, False))
        print("Q05 PASS: both examples, negative/zero and all 20001 allowed integers")

    def test_q06_multiples_five_all_allowed_upper_bounds(self):
        self.assertEqual(multiples_five(15), [5, 10, 15])
        self.assertEqual(multiples_five(7), [5])
        for n in range(5, 10001):
            self.assertEqual(multiples_five(n), [v for v in range(1, n + 1) if v % 5 == 0], n)
        self.assertEqual((multiples_five(5), len(multiples_five(10000))), ([5], 2000))
        print("Q06 PASS: both examples, all 9996 allowed upper bounds and 2000-element maximum output")

    def test_q07_positive_count_all_short_arrays_and_long_boundaries(self):
        self.assertEqual(count_positive([-2, 5, 7, -1, 3]), 3)
        self.assertEqual(count_positive([-2, -10]), 0)
        checked = 0
        for size in range(1, 7):
            for item in itertools.product((-10000, -1, 0, 1, 10000), repeat=size):
                values = list(item)
                self.assertEqual(count_positive(values), sum(1 for v in values if v > 0), item)
                checked += 1
        for values, expected in [
            ([0] * 10000, 0),
            ([-10000] * 10000, 0),
            ([10000] * 10000, 10000),
            ([-1, 0, 1, 10000] * 2500, 5000),
        ]:
            self.assertEqual(count_positive(values), expected)
        self.assertEqual(checked, 19530)
        print("Q07 PASS: 2 examples, 19530 exhaustive nonempty short arrays and four 10000-element arrays")

    def test_q08_last_word_spaces_and_length_boundaries(self):
        self.assertEqual(last_word_length("Hello World"), 5)
        self.assertEqual(last_word_length(" fly me to the moon "), 4)
        checked = 0
        for length in range(1, 11):
            for letters in itertools.product("A ", repeat=length):
                s = "".join(letters)
                if "A" not in s:
                    continue  # archive contract requires at least one word
                independent = len(s.rstrip(" ").split(" ")[-1])
                self.assertEqual(last_word_length(s), independent, repr(s))
                checked += 1
        for s, expected in [("A", 1), (" " * 9999 + "Z", 1),
                            ("Z" + " " * 9999, 1), ("a" * 10000, 10000),
                            ("a" * 4999 + " " * 2 + "b" * 4999, 4999)]:
            self.assertEqual(last_word_length(s), expected)
        self.assertEqual(checked, 2036)
        print("Q08 PASS: 2 examples, 2036 all-small binary strings with a word, 10000-char limits")

    def test_q09_palindrome_full_small_domain_and_32bit_boundaries(self):
        self.assertEqual((palindrome_number(1771), palindrome_number(556)), (True, False))
        for n in range(-10000, 10001):
            self.assertIs(palindrome_number(n), str(n) == str(n)[::-1], n)
        rng = random.Random(20261113)
        for _ in range(20000):
            n = rng.randint(-(2 ** 31), 2 ** 31 - 1)
            self.assertIs(palindrome_number(n), str(n) == str(n)[::-1], n)
        for n, expected in [(-2147483648, False), (2147483647, False),
                            (0, True), (1, True), (-121, False),
                            (10, False), (1000000001, True),
                            (1000000000, False)]:
            self.assertIs(palindrome_number(n), expected)
        print("Q09 PASS: 2 examples, 20001 small-domain and 20000 seeded 32-bit integers")

if __name__ == "__main__":
    unittest.main(verbosity=2)
