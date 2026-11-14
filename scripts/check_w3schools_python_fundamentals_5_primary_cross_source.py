"""Read-only reviewer checks for five hosted W3Schools Python fundamentals pages.

The immutable original companion lessons 01-05 are pinned by Git blob SHA.
Reviewer-only synthetic tests below are NOT official hosted editor outcomes,
original PDF page parity, graded coursework, learner submissions or mastery.
"""
from __future__ import annotations

from decimal import Decimal
import hashlib
from pathlib import Path
import random
import unittest
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = (ROOT / '99. Reference Materials' / 'Original Mastery Snapshot'
           / '2. Python Mastry' / '1. Python from Zero')

# Every archived blob was independently fetched on 2026-11-14.
SOURCES = (
    ('01. Your first Python program.md', '5fd194caa2280c436371fb94cee97f1ee4c5f5fb',
     'https://www.w3schools.com/python/python_syntax.asp', 5),
    ('02. Variables and names.md', '798106aadd2458a8a8f416dca0225a29c080fa0e',
     'https://www.w3schools.com/python/python_variables.asp', 6),
    ('03. Numbers and maths.md', '1e0079262aadcdfa1c92a15dd5575fc5a52a9113',
     'https://www.w3schools.com/python/python_numbers.asp', 7),
    ('04. Strings - working with text.md', 'efd9df91f7af2cb988eb406a1982350243dfc11a',
     'https://www.w3schools.com/python/python_strings.asp', 8),
    ('05. True False and comparisons.md', '810c49664e586b951295e03a8672938b241cbc74',
     'https://www.w3schools.com/python/python_booleans.asp', 9),
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


class HostedPythonFundamentalsCrossSource(unittest.TestCase):
    def test_01_five_original_archive_blobs_pdf_page_and_hosted_topic_links(self):
        for name, sha, url, page in SOURCES:
            with self.subTest(lesson=name):
                raw = (ARCHIVE / name).read_bytes()
                self.assertEqual(sha, git_blob_sha(raw))
                text = raw.decode('utf-8-sig')
                self.assertIn(f'PDF page {page}', text)
                self.assertIn(url, text)

    def test_02_w3_syntax_missing_and_inconsistent_indentation_are_distinct_errors(self):
        valid = 'amount = 1198\nif amount > 1000:\n    print("big")\nprint("done")'
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(valid, '<reviewer>', 'exec'), {})
        self.assertEqual('big\ndone\n', output.getvalue())
        for invalid in (
            'if True:\nprint("missing block")',
            'if True:\n    print("first")\n  print("inconsistent")',
        ):
            with self.subTest(code=invalid), self.assertRaises(IndentationError):
                compile(invalid, '<reviewer>', 'exec')

    def test_03_w3_variables_case_and_rebinding_without_implicit_conversion(self):
        scope = {}
        exec('Amount = 100\namount = 200\namount = "200"', scope)
        self.assertEqual((100, '200'), (scope['Amount'], scope['amount']))
        self.assertIs(type(scope['amount']), str)
        self.assertEqual(201, int(scope['amount']) + 1)
        with self.assertRaises(TypeError):
            _ = scope['amount'] + 1

    def test_04_numeric_conversion_and_boolean_integer_subclass(self):
        self.assertEqual((int, float, complex), tuple(type(v) for v in (1, 1.0, 1j)))
        self.assertEqual(-2, int(-2.9))  # int truncates, NOT floor
        self.assertTrue(isinstance(True, int))
        self.assertIs(type(True), bool)
        self.assertEqual(1499, int('1,499'.replace(',', '')))
        with self.assertRaises(ValueError):
            int('1,499')
        with self.assertRaises(TypeError):
            float(1j)

    def test_05_signed_floor_division_and_remainder_identity_exhaustive_grid(self):
        for numerator in range(-17, 18):
            for divisor in (-7, -3, -2, -1, 1, 2, 3, 7):
                with self.subTest(a=numerator, b=divisor):
                    q, r = divmod(numerator, divisor)
                    self.assertEqual(numerator, divisor * q + r)
                    self.assertEqual(q, numerator // divisor)
                    self.assertEqual(r, numerator % divisor)
                    self.assertTrue(0 <= r < divisor if divisor > 0 else divisor < r <= 0)
        self.assertEqual((-4, 1), divmod(-7, 2))

    def test_06_currency_float_warning_is_not_decimal_exactness(self):
        self.assertNotEqual(Decimal('0.3'), Decimal(0.1 + 0.2))
        self.assertEqual(Decimal('0.3'), Decimal('0.1') + Decimal('0.2'))
        self.assertEqual('1.00', f'{Decimal("1.005").quantize(Decimal("0.01")):,.2f}')
        # Default Decimal context rounds halfway-to-even; this is not a finance policy.

    def test_07_w3_random_range_upper_bound_exclusive(self):
        rng = random.Random(104)
        samples = [rng.randrange(1, 10) for _ in range(500)]
        self.assertTrue(all(1 <= n < 10 for n in samples))
        self.assertEqual(set(range(1, 10)), set(samples))

    def test_08_w3_strings_unicode_code_points_vs_grapheme_clusters(self):
        self.assertEqual(2, len('e\u0301'))
        self.assertEqual(1, len('\u00e9'))
        self.assertEqual('e', 'e\u0301'[:1])
        self.assertEqual(unicodedata.normalize('NFC', 'e\u0301'), '\u00e9')
        self.assertNotEqual('e\u0301', '\u00e9')

    def test_09_source_strip_lower_returns_new_string_not_in_place(self):
        status = '  Delivered  '
        normalized = status.strip().lower()
        self.assertEqual('delivered', normalized)
        self.assertEqual('  Delivered  ', status)
        self.assertEqual('a b', '  a b  '.strip())
        self.assertNotEqual('a b', '  a  b  '.strip())

    def test_10_casefold_and_unicode_normalization_are_not_implicit(self):
        self.assertNotEqual('strasse', 'Stra\u00dfe'.lower())
        self.assertEqual('strasse', 'Stra\u00dfe'.casefold())
        self.assertEqual('MUMBAI', 'mumbai'.upper())

    def test_11_w3_truthiness_must_not_conflate_zero_missing_and_text(self):
        values = [None, 0, 0.0, '', '0', 'False', [], {}, [0], {'v': 0}]
        self.assertEqual([False, False, False, False, True, True, False, False, True, True],
                         list(map(bool, values)))
        self.assertIsNot(0, None)
        self.assertTrue(None is None)

    def test_12_logical_short_circuit_returns_operand_not_forced_boolean(self):
        self.assertEqual('fallback', '' or 'fallback')
        self.assertEqual([], [] and 'next')
        self.assertEqual(2, 1 and 2)
        self.assertIs(type(1 and 2), int)
        self.assertEqual(1, 5 & 3)
        self.assertEqual(7, 5 | 3)
        self.assertNotEqual(5 & 3, 5 and 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
