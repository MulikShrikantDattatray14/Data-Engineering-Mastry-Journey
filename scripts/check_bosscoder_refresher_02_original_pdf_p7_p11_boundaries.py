#!/usr/bin/env python3
"""Reviewer-authored Python 3 boundary probes for Bosscoder Refresher-2 PDF pp.7-11.

Private original observed as 11 rendered pages, SHA-256
09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010.
Only small observed input/output facts are cited, not the private source itself.
GitHub CI cannot authenticate the private PDF bytes, native Colab cell history,
Academy answer keys, grades, learner submissions, or course mastery.
"""
from __future__ import annotations

import builtins
import unittest

SOURCE_PDF_SHA256 = "09ba1141054463b6eac814da13eaa0c401822298eded114fe831d89d5a3ff010"
SOURCE_PAGES = (7, 8, 9, 10, 11)


def rotation(a: str, b: str) -> bool:
    """Independent reviewer implementation of the visible p.7 question."""
    return len(a) == len(b) and b in (a + a)


def first_unique(s: str) -> str | None:
    """Independent reviewer oracle; not a learner's submission."""
    return next((c for c in s if s.count(c) == 1), None)


def longest_palindrome(s: str) -> str:
    """Same enumerating/tie policy as the visible sample; reviewer authored."""
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            part = s[i:j]
            if part == part[::-1] and len(part) > len(best):
                best = part
    return best


def isomorphic(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    return [a.find(c) for c in a] == [b.find(c) for c in b]


def is_subsequence(needle: str, haystack: str) -> bool:
    i = 0
    for ch in haystack:
        if i < len(needle) and needle[i] == ch:
            i += 1
    return i == len(needle)


class OriginalPdfPages7To11Boundaries(unittest.TestCase):
    def test_01_private_pdf_identity_scope_is_not_ci_authenticated(self):
        self.assertEqual(len(SOURCE_PDF_SHA256), 64)
        self.assertEqual(SOURCE_PAGES, (7, 8, 9, 10, 11))
        self.assertEqual(set(range(7, 12)), set(SOURCE_PAGES))

    def test_02_p7_rotation_visible_example(self):
        self.assertTrue(rotation("waterbottle", "erbottlewat"))

    def test_03_p7_rotation_negative_length_and_empty_boundaries(self):
        self.assertFalse(rotation("waterbottle", "bottlewater!"))
        self.assertFalse(rotation("abcd", "abdc"))
        self.assertTrue(rotation("", ""))
        self.assertTrue(rotation("aaaa", "aaaa"))

    def test_04_p7_first_unique_visible_example(self):
        self.assertEqual(first_unique("swiss"), "w")

    def test_05_p7_first_unique_all_duplicate_and_empty_boundaries(self):
        for word in ("aabb", "aaaa", ""):
            with self.subTest(word=word):
                self.assertIsNone(first_unique(word))
        self.assertEqual(first_unique("aabbZ"), "Z")

    def test_06_p7_longest_palindrome_visible_example_and_tie(self):
        self.assertEqual(longest_palindrome("babad"), "bab")
        self.assertEqual(longest_palindrome("cbbd"), "bb")
        self.assertEqual(longest_palindrome(""), "")

    def test_07_p8_isomorphism_visible_example(self):
        self.assertTrue(isomorphic("egg", "add"))

    def test_08_p8_isomorphism_injectivity_length_and_unicode(self):
        self.assertFalse(isomorphic("ab", "aa"))
        self.assertFalse(isomorphic("foo", "bar"))
        self.assertFalse(isomorphic("abc", "ab"))
        self.assertTrue(isomorphic("紙紙x", "zz7"))

    def test_09_p8_one_way_subsequence_visible_example(self):
        self.assertTrue(is_subsequence("abc", "ahbgdc"))
        self.assertFalse(is_subsequence("ahbgdc", "abc"))

    def test_10_p8_bidirectionality_wording_is_not_what_code_tests(self):
        self.assertTrue(is_subsequence("a", "ab"))
        self.assertFalse(is_subsequence("ab", "a"))
        self.assertTrue(is_subsequence("", "abc"))
        self.assertFalse(is_subsequence("aac", "abc"))

    def test_11_p8_p9_tuple_count_and_index_original_printed_values(self):
        values = (1, 2, 3, 2, 2, 4)
        self.assertEqual(values.count(2), 3)
        self.assertEqual(values.index(3), 2)
        self.assertEqual(values.index(2, 2), 3)

    def test_12_p9_tuple_index_absent_and_python3_cmp_mismatch(self):
        values = (1, 2, 3)
        with self.assertRaises(ValueError):
            values.index(9)
        self.assertFalse(hasattr(builtins, "cmp"))
        self.assertTrue((1, 2) < (1, 3))

    def test_13_p9_nested_tuple_loop_is_only_one_level_deep(self):
        values = (1, (2, 3), (4, (5, 6), 7))
        output = []
        for element in values:
            if isinstance(element, tuple):
                output.extend(element)
            else:
                output.append(element)
        self.assertEqual(output, [1, 2, 3, 4, (5, 6), 7])

    def test_14_p8_p9_tuple_immutability_is_shallow(self):
        values = (1, [2])
        with self.assertRaises(TypeError):
            values[0] = 99
        values[1].append(3)
        self.assertEqual(values, (1, [2, 3]))
        self.assertEqual(tuple([1, 2, 3, 4]), (1, 2, 3, 4))

    def test_15_p10_set_operations_absent_removal_and_pop_policy(self):
        a, b = {1, 2, 3}, {3, 4, 5}
        self.assertEqual(a | b, {1, 2, 3, 4, 5})
        self.assertEqual(a & b, {3})
        self.assertEqual(a - b, {1, 2})
        self.assertEqual(a ^ b, {1, 2, 4, 5})
        self.assertEqual(set(), set())
        self.assertIsInstance({}, dict)
        x = {1, 2}
        x.discard(999)
        with self.assertRaises(KeyError):
            x.remove(999)
        popped = x.pop()
        self.assertIn(popped, {1, 2})
        self.assertEqual(len(x), 1)

    def test_16_p11_python37_plus_dict_insertion_order_and_unique_keys(self):
        row = {"name": "Alice", "age": 25, "city": "New York"}
        self.assertEqual(list(row), ["name", "age", "city"])
        row["age"] = 26
        self.assertEqual(list(row), ["name", "age", "city"])
        row["new"] = None
        self.assertEqual(list(row), ["name", "age", "city", "new"])
        self.assertEqual({"x": 1, "x": 2}, {"x": 2})


if __name__ == "__main__":
    unittest.main(verbosity=2)
