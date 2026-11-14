#!/usr/bin/env python3
"""Source-pinned review: five hosted W3 Python casting/operators/string pages.

The source files are immutable references. All executable cases below are
auditor-authored Python probes, not official editor grading, learner submissions,
original PDF page verification, or additional source-example coverage.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry" / "1. Python from Zero"
ORIGINALS = (
    ("03. Numbers and maths.md", "1e0079262aadcdfa1c92a15dd5575fc5a52a9113", "PDF page 7"),
    ("04. Strings - working with text.md", "efd9df91f7af2cb988eb406a1982350243dfc11a", "PDF page 8"),
    ("05. True False and comparisons.md", "810c49664e586b951295e03a8672938b241cbc74", "PDF page 9"),
    ("06. Input and output.md", "abeee9779392bbd199e73ef30d35cddae73d0611", "PDF page 10"),
)
HOSTED = (
    "https://www.w3schools.com/python/python_casting.asp",
    "https://www.w3schools.com/python/python_operators.asp",
    "https://www.w3schools.com/python/python_strings_slicing.asp",
    "https://www.w3schools.com/python/python_strings_modify.asp",
    "https://www.w3schools.com/python/python_strings_format.asp",
)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class W3PythonCastingOperatorsStringsFiveCrossSource(unittest.TestCase):
    def test_01_four_original_git_blobs_page_refs_and_existing_hosted_links(self):
        combined = ""
        for name, sha, page in ORIGINALS:
            with self.subTest(original=name):
                raw = (BASE / name).read_bytes()
                self.assertEqual(sha, git_blob_sha(raw))
                decoded = raw.decode("utf-8-sig")
                self.assertIn(page, decoded)
                combined += decoded
        # Only 2 of the 5 selected hosted URLs are linked in these local
        # companions; absent additional links are NOT evidence of source loss.
        self.assertIn(HOSTED[0], combined)
        self.assertIn(HOSTED[1], combined)
        self.assertIn("https://www.w3schools.com/python/python_strings.asp", combined)
        self.assertIn("https://www.w3schools.com/python/python_string_formatting.asp", combined)

    def test_02_casting_truncates_toward_zero_both_signs(self):
        self.assertEqual((2, -2, 2), (int(2.9), int(-2.9), int("2")))
        self.assertEqual((2.9, -2.9), (float("2.9"), float("-2.9")))

    def test_03_invalid_decimal_integer_text_and_thousands_separator(self):
        for value in ("3.5", "1,499", "", "abc"):
            with self.subTest(raw=value), self.assertRaises(ValueError):
                int(value)
        self.assertEqual(1499, int("1,499".replace(",", "")))
        self.assertEqual(3.5, float("3.5"))

    def test_04_casting_bool_nan_and_infinity_are_not_valid_money(self):
        self.assertEqual(1, int(True))
        self.assertIsInstance(True, int)
        self.assertTrue(float("nan") != float("nan"))
        self.assertFalse(Decimal("NaN").is_finite())
        self.assertFalse(Decimal("Infinity").is_finite())
        with self.assertRaises(ValueError):
            int(Decimal("NaN"))

    def test_05_negative_floor_and_remainder_follow_invariant(self):
        cases = ((-7, 2, -4, 1), (7, -2, -4, -1), (-7, -2, 3, -1))
        for a, b, quotient, remainder in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual((quotient, remainder), divmod(a, b))
                self.assertEqual(a, b * quotient + remainder)

    def test_06_short_circuit_and_or_return_operands_not_just_bools(self):
        self.assertEqual("", "" and "accepted")
        self.assertEqual("fallback", "" or "fallback")
        self.assertEqual([3], [] or [3])
        def crash():
            raise AssertionError("short circuit failed")
        self.assertEqual(0, 0 and crash())
        self.assertEqual("ok", "ok" or crash())

    def test_07_membership_and_identity_are_not_value_equality(self):
        a, b = [1], [1]
        self.assertEqual(a, b)
        self.assertIsNot(a, b)
        self.assertIn(1, a)
        self.assertIsNone({"discount": None}.get("discount"))
        self.assertEqual(0, {"discount": 0}.get("discount"))
        self.assertNotEqual({"discount": None}.get("discount"),
                            {"discount": 0}.get("discount"))

    def test_08_mixed_boolean_precedence_needs_parentheses_for_policy(self):
        status, amount, refund = "cancelled", 1200, True
        loose = status == "delivered" and amount > 1000 or refund
        strict = status == "delivered" and (amount > 1000 or refund)
        self.assertTrue(loose)
        self.assertFalse(strict)

    def test_09_string_slices_are_half_open_and_can_reverse(self):
        text = "Bengaluru"
        self.assertEqual(("Beng", "aluru", "uru", "urulagneB"),
                         (text[:4], text[4:], text[-3:], text[::-1]))
        self.assertEqual("llo", "Hello, World!"[2:5])

    def test_10_slicing_out_of_bounds_is_safe_indexing_is_not(self):
        self.assertEqual("", "abc"[100:110])
        self.assertEqual("abc", "abc"[-100:100])
        with self.assertRaises(IndexError):
            _ = "abc"[100]
        with self.assertRaises(ValueError):
            _ = "abc"[::0]

    def test_11_unicode_code_points_are_not_grapheme_clusters(self):
        composed, decomposed = "é", "e\u0301"
        self.assertEqual(1, len(composed))
        self.assertEqual(2, len(decomposed))
        self.assertNotEqual(composed, decomposed)
        self.assertEqual("e", decomposed[:1])

    def test_12_strip_case_replace_return_new_strings(self):
        original = "  Delivered \t"
        clean = original.strip().lower()
        self.assertEqual("delivered", clean)
        self.assertEqual("  Delivered \t", original)
        self.assertEqual("de livered", "de-livered".replace("-", " "))
        self.assertEqual("a  b", "a  b".strip())
        self.assertEqual("ss", "ß".casefold())

    def test_13_split_explicit_delimiter_and_default_whitespace_differ(self):
        self.assertEqual(["a", "", "b"], "a,,b".split(","))
        self.assertEqual(["a", "b"], " a   b ".split())
        self.assertEqual(["a", " b"], "a, b".split(","))
        # Literal splitting is not a CSV parser: a quoted comma is data.
        self.assertNotEqual(2, len('"Mumbai, West",delivered'.split(",")))

    def test_14_float_binary_rounding_differs_from_decimal_money(self):
        self.assertNotEqual(Decimal("0.3"), Decimal(str(0.1 + 0.2)))
        self.assertEqual(Decimal("0.30"), Decimal("0.1") + Decimal("0.2"))
        self.assertEqual("2.68", format(Decimal("2.675").quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN), ".2f"))
        self.assertEqual("49.00", f"{49:.2f}")

    def test_15_fstring_precision_alignment_and_legacy_format(self):
        self.assertEqual("4,143.00", f"{4143:,.2f}")
        self.assertEqual("003", f"{3:03d}")
        self.assertEqual("Diya    |    Diya|", f"{'Diya':<8}|{'Diya':>8}|")
        self.assertEqual("25.6%", f"{0.256:.1%}")
        self.assertEqual("Item 101", "Item {}".format(101))
        with self.assertRaises(TypeError):
            _ = "Quantity " + 3

    def test_16_dirty_text_normalization_does_not_validate_numbers(self):
        rows = [" Delivered ", "DELIVERED", " cancelled "]
        self.assertEqual(["delivered", "delivered", "cancelled"],
                         [s.strip().lower() for s in rows])
        raw = "nan"
        self.assertTrue(float(raw) != float(raw))  # parses but not usable as money
        with self.assertRaises(ValueError):
            Decimal("2,500")


if __name__ == "__main__":
    unittest.main(verbosity=2)
