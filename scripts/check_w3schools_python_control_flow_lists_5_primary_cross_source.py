#!/usr/bin/env python3
"""Read-only W3 Python control-flow/list semantics vs immutable mentor companions.

Reviewer-authored fixture tests, NOT W3 editor grades, provider keys or learner attempts.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry" / "1. Python from Zero"
SOURCES = (
    ("06. Input and output.md", "abeee9779392bbd199e73ef30d35cddae73d0611",
     "https://www.w3schools.com/python/python_user_input.asp", "PDF page 10"),
    ("07. Making decisions.md", "2db16f4f3ff4f909bb7b7404cd54556772bf210f",
     "https://www.w3schools.com/python/python_conditions.asp", "PDF page 11"),
    ("08. Loops part 1 - for and range.md", "68150cbef1e85eb81dac8af1d00a927bec7d0ba4",
     "https://www.w3schools.com/python/python_for_loops.asp", "PDF page 12"),
    ("09. Loops part 2 - while break continue.md", "4f511d8624dac0911d9681d8cd37e6a1a65edb91",
     "https://www.w3schools.com/python/python_while_loops.asp", "PDF page 13"),
    ("10. Lists - ordered collections.md", "bc2b6ec4ec0b77409570b19044e7ade55a51e961",
     "https://www.w3schools.com/python/python_lists.asp", "page 14 of 80"),
)


def blob_id(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


class PythonControlFlowListsCrossSource(unittest.TestCase):
    def test_01_original_five_blob_ids_pdf_pages_and_hosted_links(self):
        for name, sha, url, page in SOURCES:
            with self.subTest(source=name):
                data = (ARCHIVE / name).read_bytes()
                self.assertEqual(sha, blob_id(data))
                original = data.decode("utf-8-sig")
                self.assertIn(page, original)
                self.assertIn(url, original)

    def test_02_input_stays_string_numeric_text_requires_conversion(self):
        with patch("builtins.input", side_effect=["0003", "3.5", "three"]):
            raw = input("Quantity: ")
            self.assertEqual("0003", raw)
            self.assertEqual(3, int(raw))
            self.assertEqual(3.5, float(input("Price: ")))
            with self.assertRaises(ValueError):
                int(input("Quantity: "))
        with self.assertRaises(ValueError):
            int("3.5")
        self.assertEqual(3.5, float("3.5"))

    def test_03_hosted_sqrt_code_is_not_standalone_without_math_import(self):
        # Hosted numeric input example does not display an import math line.
        snippet = ('x = input("Enter a number:")\n'
                   'y = math.sqrt(float(x))\n'
                   'print(f"The square root of {x} is {y}")')
        with patch("builtins.print"):
            with self.assertRaisesRegex(NameError, "math"):
                exec(snippet, {"input": lambda prompt: "9"})
            globals_ = {"input": lambda prompt: "9", "math": math}
            exec(snippet, globals_)
            self.assertEqual(3.0, globals_["y"])
            with self.assertRaises(ValueError):
                exec(snippet, {"input": lambda prompt: "-9", "math": math})

    def test_04_numeric_retry_needs_finite_validation_and_eof_policy(self):
        entries = iter(["oops", "3.5", "NaN"])
        kept = []
        for _ in range(3):
            try:
                number = float(next(entries))
            except ValueError:
                continue
            if math.isfinite(number):
                kept.append(number)
        self.assertEqual([3.5], kept)
        self.assertFalse(math.isfinite(float("nan")))
        self.assertFalse(math.isfinite(float("-inf")))
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(EOFError):
                input("Quantity: ")

    def test_05_if_elif_order_and_tier_boundaries(self):
        def grade(amount):
            if amount >= 2000:
                return "A"
            if amount >= 1000:
                return "B"
            return "C"
        self.assertEqual(["C", "C", "B", "B", "A", "A"],
                         [grade(n) for n in [-1, 999, 1000, 1999, 2000, 2500]])
        wrong_order = "B" if 2500 >= 1000 else ("A" if 2500 >= 2000 else "C")
        self.assertNotEqual(grade(2500), wrong_order)

    def test_06_nonempty_text_false_is_truthy_but_not_an_explicit_status(self):
        self.assertTrue(bool("False"))
        self.assertFalse(bool(""))
        self.assertFalse(bool(0))
        self.assertFalse(bool(None))
        self.assertTrue(bool(-3))
        self.assertTrue(bool("cancelled"))
        self.assertNotEqual("cancelled", "delivered")
        self.assertIsNot(0, None)

    def test_07_archived_match_alternatives_and_guard(self):
        def classify(status, fee):
            match status:
                case "delivered" | "shipped":
                    return "close"
                case "returned" if fee > 0:
                    return "refund"
                case _:
                    return "review"
        self.assertEqual(["close", "close", "refund", "review", "review"],
                         [classify(s, f) for s, f in
                          [("delivered", 0), ("shipped", 0), ("returned", 50),
                           ("returned", 0), ("cancelled", 10)]])

    def test_08_for_break_before_vs_after_print_and_continue(self):
        items = ["apple", "banana", "cherry"]
        before = []
        after = []
        for x in items:
            before.append(x)
            if x == "banana":
                break
        for x in items:
            if x == "banana":
                break
            after.append(x)
        self.assertEqual(["apple", "banana"], before)
        self.assertEqual(["apple"], after)
        self.assertEqual(["apple", "cherry"], [x for x in items if x != "banana"])

    def test_09_range_exclusive_stop_direction_and_zero_step(self):
        self.assertEqual([0, 1, 2, 3, 4], list(range(5)))
        self.assertEqual([2, 5, 8], list(range(2, 9, 3)))
        self.assertEqual([7, 5, 3, 1], list(range(7, 0, -2)))
        self.assertEqual([], list(range(7, 0, 2)))
        self.assertEqual([], list(range(0, 5, -1)))
        with self.assertRaises(ValueError):
            range(1, 10, 0)

    def test_10_for_else_runs_on_empty_and_exhaustion_but_not_break(self):
        def result(items):
            seen = []
            for item in items:
                if item == "STOP":
                    break
                seen.append(item)
            else:
                seen.append("done")
            return seen
        self.assertEqual(["done"], result([]))
        self.assertEqual(["ok", "done"], result(["ok"]))
        self.assertEqual(["ok"], result(["ok", "STOP", "ignored"]))

    def test_11_while_continue_updates_first_and_break_skips_else(self):
        attempt, seen = 0, []
        while attempt < 3:
            attempt += 1
            if attempt == 2:
                continue
            seen.append(attempt)
        else:
            seen.append("normal")
        self.assertEqual([1, 3, "normal"], seen)
        attempt, after = 0, []
        while attempt < 3:
            attempt += 1
            if attempt == 2:
                break
        else:
            after.append("normal")
        self.assertEqual(2, attempt)
        self.assertEqual([], after)

    def test_12_list_mutable_duplicates_remove_first_and_pop_value(self):
        amounts = [1198, 796, 1198]
        alias = amounts
        amounts.remove(1198)
        self.assertEqual([796, 1198], alias)
        self.assertEqual(1198, amounts.pop())
        amounts.insert(0, 1499)
        amounts.extend([796, 796])
        self.assertEqual([1499, 796, 796, 796], amounts)
        self.assertEqual(3, amounts.count(796))
        with self.assertRaises(ValueError):
            amounts.remove(999)
        with self.assertRaises(IndexError):
            _ = [][0]

    def test_13_sorted_vs_sort_and_shallow_nested_copy(self):
        amounts = [1499, 796, 1198]
        result = sorted(amounts)
        self.assertEqual([796, 1198, 1499], result)
        self.assertEqual([1499, 796, 1198], amounts)
        self.assertIsNone(amounts.sort())
        self.assertEqual(result, amounts)
        rows = [[101, 1198], [102, 796]]
        shallow = rows.copy()
        shallow[0][1] = 1499
        self.assertEqual(1499, rows[0][1])
        shallow.append([103, 899])
        self.assertEqual(2, len(rows))

    def test_14_second_rank_policy_duplicate_max_and_slice(self):
        values = [1499, 796, 1499, 1000]
        ranked = sorted(values, reverse=True)
        self.assertEqual([1499, 1499, 1000, 796], ranked)
        self.assertEqual(1499, ranked[1])
        self.assertEqual(1000, sorted(set(values), reverse=True)[1])
        self.assertEqual([796, 1499], values[1:3])
        self.assertEqual([1000, 1499, 796, 1499], values[::-1])
        with self.assertRaises(IndexError):
            _ = sorted(set([5, 5]), reverse=True)[1]


if __name__ == "__main__":
    unittest.main(verbosity=2)
