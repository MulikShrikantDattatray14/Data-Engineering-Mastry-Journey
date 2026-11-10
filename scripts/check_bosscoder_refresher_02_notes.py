#!/usr/bin/env python3
"""Read-only, SHA-pinned Bosscoder Lecture-02 *archived Journey notes* checks.

The private original Academy PDF is NOT available in GitHub Actions and this
script does not validate Academy grading or learner-submitted solutions.
"""
import ast
import contextlib
import hashlib
import io
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-02'
NOTES = [
    ('01-patterns-and-nested-loops.md', '0cdb98ea14fb53ee0dcc0fbe20e810d3de178bbe', [
        '####\n####\n####\n',
        '#\n##\n###\n####\n####\n###\n##\n#\n',
        '   ^\n  ^^^\n ^^^^^\n^^^^^^^\n',
        '  ^\n ^^^\n^^^^^\n ^^^\n  ^\n',
        '####\n#  #\n#  #\n####\n',
    ]),
    ('02-lists-and-strings.md', 'fb88fbd9bfa142fca6fc48b03638c21b5fa307fa', [
        '101 103 [101, 102]\n',
        "2\nmelon ['plum', 'pear', 'kiwi', 'date', 'apple']\n[]\n",
        'Order ReadyOrder Ready True\nE\nT\nL\n',
        'paid|pending|paid\nABCabc\n2 4\nTrue True True\n0007 ..x..\nrows=3 rows=3\n',
    ]),
    ('03-tuples-sets-dictionaries.md', '0177eb35b9a3c8440407e9da17fd913185e227ff', [
        '2 3\n4 2 5 (1, 2)\n',
        '1 paid\n2 pending\n',
        None,  # set order cannot be checked as a literal string
        "{'name': 'Asha', 'age': 26, 'city': 'Pune'} {'name': 'Asha', 'age': 26}\n",
    ]),
]
ASSIGNMENTS = {
    'q01-alphabet-triangle.md': 'ad53f8699c8f15a9b6e5f8ce0742a3001c3f046f',
    'q02-inverted-star-triangle.md': '8f154967ea2c4615347818dba135c3988ab0e4ee',
    'q03-hollow-square.md': '7a1be61fc9ca0ade2e14647f951f9b335a88f3a1',
    'q04-132-pattern.md': '107db65ad457f4fac5ba0d0c0216b5fed744bf5a',
}

def anchored(path, expected):
    raw = path.read_bytes()
    found = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if found != expected:
        raise AssertionError(f'Archived file drift {path}: {found} != {expected}')
    return raw.decode('utf-8')

class OriginalArchivedNotes(unittest.TestCase):
    def test_13_fenced_examples(self):
        count = 0
        for name, sha, wanted in NOTES:
            text = anchored(SRC / name, sha)
            blocks = re.findall(r'\x60\x60\x60python\s*\n(.*?)\n\x60\x60\x60', text, re.S)
            self.assertEqual(len(blocks), len(wanted), name)
            for index, (block, expected) in enumerate(zip(blocks, wanted), 1):
                with self.subTest(name=name, block=index):
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        exec(compile(block, f'{name}#{index}', 'exec'), {'__name__': '__main__'})
                    got = out.getvalue()
                    if expected is None:
                        lines = got.strip().splitlines()
                        self.assertEqual(len(lines), 4)
                        self.assertEqual([ast.literal_eval(x) for x in lines],
                                         [{1, 2, 3, 4}, {3}, {1, 2}, {1, 2, 4}])
                    else:
                        self.assertEqual(got, expected)
                    count += 1
        self.assertEqual(count, 13)

    def test_four_immutable_pending_assignment_statements(self):
        for name, sha in ASSIGNMENTS.items():
            with self.subTest(name=name):
                text = anchored(SRC / 'assignments' / name, sha)
                self.assertIn('**Attempt:** Pending', text)
                self.assertIn('**Academy platform completion:** Unverified', text)
                self.assertIn('## Task', text)
        self.assertEqual(len(ASSIGNMENTS), 4)

class ReviewerOnlySyntheticBoundaries(unittest.TestCase):
    def test_zero_and_one_row_print_shapes(self):
        def shape(rows, cols):
            return '\n'.join('#' * cols for _ in range(rows))
        self.assertEqual(shape(1, 1), '#')
        self.assertEqual(shape(0, 6), '')
        self.assertEqual(shape(3, 0), '\n\n')

    def test_mutation_and_list_method_returns(self):
        seq = [2, 2, 1]
        seq.remove(2)
        self.assertEqual(seq, [2, 1])
        self.assertIsNone(seq.sort())
        self.assertEqual(seq, [1, 2])
        self.assertIsNone(seq.append([3, 4]))
        self.assertEqual(seq, [1, 2, [3, 4]])
        with self.assertRaises(IndexError):
            [].pop()

    def test_missing_index_and_strip_characters(self):
        self.assertEqual('blue'.find('z'), -1)
        with self.assertRaises(ValueError):
            'blue'.index('z')
        self.assertEqual('abbaHELLOabba'.strip('ab'), 'HELLO')
        self.assertEqual('ababa'.count('aba'), 1)

    def test_mutable_nested_tuple_and_dictionary_order(self):
        inner = [1]
        frozen = (inner,)
        inner.append(2)
        self.assertEqual(frozen, ([1, 2],))
        d = {'x': 1, 'y': 2}
        d['x'] = 3
        self.assertEqual(list(d), ['x', 'y'])

    def test_set_semantics_without_repr_order_assumption(self):
        a, b = {3, 2, 1}, {4, 3}
        self.assertEqual(a | b, {1, 2, 3, 4})
        self.assertEqual(a ^ b, {1, 2, 4})
        self.assertEqual(a - b, {1, 2})
        self.assertEqual({1, 2} & {3}, set())

if __name__ == '__main__':
    unittest.main(verbosity=2)
