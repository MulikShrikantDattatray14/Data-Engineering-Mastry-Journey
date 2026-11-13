#!/usr/bin/env python3
"""Reviewer-only checks of Bosscoder Lecture-02 archived assignment statements.

No learner answers, course-platform submissions, original PDF answer keys, or
provider solution code is used or generated. The models below are auditor-authored.
"""
import hashlib
import itertools
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT_DIR = ROOT / '99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-02/assignments'
PINS = {
    'q01-alphabet-triangle.md': 'ad53f8699c8f15a9b6e5f8ce0742a3001c3f046f',
    'q02-inverted-star-triangle.md': '8f154967ea2c4615347818dba135c3988ab0e4ee',
    'q03-hollow-square.md': '7a1be61fc9ca0ade2e14647f951f9b335a88f3a1',
    'q04-132-pattern.md': '107db65ad457f4fac5ba0d0c0216b5fed744bf5a',
}

def archived_text(name, expected_sha):
    raw = (ASSIGNMENT_DIR / name).read_bytes()
    git_blob_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()
    if git_blob_sha != expected_sha:
        raise AssertionError(f'Original assignment changed: {name}: {git_blob_sha} != {expected_sha}')
    return raw.decode('utf-8')

def triangle(n):
    return [''.join(chr(ord('a') + col) for col in range(row))
            for row in range(1, n + 1)]

def inverted(n):
    return ['*' * row for row in range(n, 0, -1)]

def hollow(n):
    return [''.join('*' if r in (0, n - 1) or c in (0, n - 1) else ' '
                    for c in range(n)) for r in range(n)]

def brute_132(nums):
    return any(nums[i] < nums[k] < nums[j]
               for i in range(len(nums))
               for j in range(i + 1, len(nums))
               for k in range(j + 1, len(nums)))

def reviewer_linear_132(nums):
    # Auditor model only. NOT an official solution or independent learner answer.
    stack = []
    middle = float('-inf')
    for current in reversed(nums):
        if current < middle:
            return True
        while stack and current > stack[-1]:
            middle = stack.pop()
        stack.append(current)
    return False

class OriginalSourcePreservation(unittest.TestCase):
    def test_four_pinned_original_pending_records(self):
        for name, sha in PINS.items():
            with self.subTest(file=name):
                content = archived_text(name, sha)
                self.assertIn('**Attempt:** Pending', content)
                self.assertIn('**Reviewed:** Pending', content)
                self.assertIn('**Academy platform completion:** Unverified', content)
                self.assertIn('## Task', content)
                self.assertIn('## Examples', content)
        self.assertEqual(len(PINS), 4)

class ReviewerOnlyStatementSemantics(unittest.TestCase):
    def test_q01_all_allowed_n_and_two_source_examples(self):
        self.assertEqual(triangle(4), ['a', 'ab', 'abc', 'abcd'])
        self.assertEqual(triangle(2), ['a', 'ab'])
        for n in range(1, 11):
            rows = triangle(n)
            self.assertEqual(len(rows), n)
            self.assertEqual([len(row) for row in rows], list(range(1, n + 1)))
            self.assertEqual(rows[-1], 'abcdefghij'[:n])

    def test_q02_all_allowed_n_and_two_source_examples(self):
        self.assertEqual(inverted(4), ['****', '***', '**', '*'])
        self.assertEqual(inverted(2), ['**', '*'])
        for n in range(1, 11):
            rows = inverted(n)
            self.assertEqual(len(rows), n)
            self.assertEqual([len(row) for row in rows], list(range(n, 0, -1)))
            self.assertTrue(all(set(row) == {'*'} for row in rows))

    def test_q03_all_allowed_n_and_two_source_examples(self):
        self.assertEqual(hollow(4), ['****', '*  *', '*  *', '****'])
        self.assertEqual(hollow(3), ['***', '* *', '***'])
        for n in range(1, 11):
            rows = hollow(n)
            self.assertEqual(len(rows), n)
            self.assertTrue(all(len(row) == n for row in rows))
            self.assertEqual(sum(row.count('*') for row in rows),
                             1 if n == 1 else 4 * n - 4)
            for r, row in enumerate(rows):
                for c, char in enumerate(row):
                    self.assertEqual(char == '*',
                                     r in (0, n - 1) or c in (0, n - 1))

    def test_q04_source_examples_and_strict_equalities(self):
        examples = [([1, 2, 3, 4], False), ([3, 1, 4, 2], True),
                    ([-1, 3, 2, 0], True)]
        for nums, expected in examples:
            self.assertEqual(brute_132(nums), expected)
            self.assertEqual(reviewer_linear_132(nums), expected)
        for nums, expected in [([1], False), ([1, 2], False),
                               ([1, 1, 1], False), ([1, 2, 2], False),
                               ([1, 3, 2], True),
                               ([-10**9, 10**9, 0], True),
                               ([10**9, -10**9, 0], False)]:
            self.assertEqual(reviewer_linear_132(nums), expected)

    def test_q04_exhaustive_short_inputs_vs_independent_cubic_oracle(self):
        total = 0
        for n in range(1, 8):
            for values in itertools.product((-1, 0, 1, 2), repeat=n):
                self.assertEqual(reviewer_linear_132(values),
                                 brute_132(values), (n, values))
                total += 1
        self.assertEqual(total, 21844)
        print(f'Q04 exhaustive auditor comparisons: {total} PASS')

    def test_q04_maximum_length_200000_review_only(self):
        n = 200000
        self.assertFalse(reviewer_linear_132(range(n)))
        self.assertFalse(reviewer_linear_132(range(n, 0, -1)))
        self.assertTrue(reviewer_linear_132([0, 2, 1] + [1] * (n - 3)))
        self.assertFalse(reviewer_linear_132([7] * n))
        print('Q04 200000-element auditor inputs: 4 PASS')

if __name__ == '__main__':
    unittest.main(verbosity=2)
