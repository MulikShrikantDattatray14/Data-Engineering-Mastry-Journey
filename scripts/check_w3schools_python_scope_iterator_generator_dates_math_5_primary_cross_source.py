#!/usr/bin/env python3
"""Read-only reviewer of five hosted W3 Python lesson contracts vs original archive.

All examples below are reviewer-authored tests, not W3 hosted-editor answers,
not original PDF visual parity and not learner submissions.
"""
from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
FOUNDATIONS = BASE / "2. Python Foundations"
ADVANCED = BASE / "3. Advanced Python"
ORDERS = BASE / "python_de_dataset" / "orders.csv"
ORIGINALS = (
    (FOUNDATIONS / "03. Numbers strings and dates.md",
     "91de7da6ba563322381b46dce78a2ebcb2ce7e61", "page 27 of 80"),
    (FOUNDATIONS / "06. Loops comprehensions and unpacking.md",
     "587219b8e48cdd899b757319e54ae94774780969", "page 30 of 80"),
    (FOUNDATIONS / "07. Functions scope and closures.md",
     "add60d3123e71a8d576f3ce1569f1134a2ece821", "page 31 of 80"),
    (ADVANCED / "01. Iterators and generators.md",
     "3c0917fe25c30c03357d1c6dd54c9f015c376379", "page 35 of 80"),
)
ORDERS_SHA = "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class W3PythonScopeIteratorsGeneratorsDatesMathCrossSource(unittest.TestCase):
    def test_01_four_immutable_original_pages_source_links_and_orders(self):
        texts = []
        for path, sha, marker in ORIGINALS:
            with self.subTest(source=path.name):
                content = path.read_bytes()
                self.assertEqual(sha, git_blob_sha(content))
                text = content.decode("utf-8-sig")
                self.assertIn(marker, text)
                texts.append(text)
        self.assertIn("https://www.w3schools.com/python/python_datetime.asp", texts[0])
        self.assertIn("https://www.w3schools.com/python/python_lists_comprehension.asp", texts[1])
        self.assertIn("https://www.w3schools.com/python/python_scope.asp", texts[2])
        self.assertIn("https://www.w3schools.com/python/python_generators.asp", texts[3])
        self.assertIn("yield from", texts[3])
        self.assertEqual(ORDERS_SHA, git_blob_sha(ORDERS.read_bytes()))

    def test_02_builtin_iter_vs_instance_method_and_iterator_identity(self):
        values = [1, 2]
        self.assertFalse(hasattr(values, "iter"))
        cursor = iter(values)
        self.assertIs(iter(cursor), cursor)
        self.assertEqual((1, 2), (next(cursor), next(cursor)))
        with self.assertRaises(StopIteration):
            next(cursor)

    def test_03_bounded_custom_iterator_stop_and_reset(self):
        class Counter:
            def __init__(self, maximum):
                self.maximum = maximum
                self.current = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.current >= self.maximum:
                    raise StopIteration
                self.current += 1
                return self.current

        cursor = Counter(3)
        self.assertEqual([1, 2, 3], list(cursor))
        self.assertEqual([], list(cursor))
        self.assertEqual("finished", next(cursor, "finished"))
        self.assertEqual([1, 2, 3], list(Counter(3)))

    def test_04_iterator_generator_laziness_before_first_next(self):
        seen = []

        def produce():
            seen.append("start")
            for x in (1, 2):
                seen.append(x)
                yield x

        cursor = produce()
        self.assertEqual([], seen)
        self.assertEqual(1, next(cursor))
        self.assertEqual(["start", 1], seen)
        self.assertEqual([2], list(cursor))
        self.assertEqual(["start", 1, 2], seen)
        self.assertEqual([], list(cursor))

    def test_05_generator_expression_re_reads_mutable_input_at_consumption(self):
        values = [10, 20]
        generator = (value * 2 for value in values)
        values[0] = 50
        self.assertEqual([100, 40], list(generator))
        self.assertEqual([], list(generator))

    def test_06_yield_from_nested_lists_and_tuple_extension(self):
        def flatten(items):
            for item in items:
                if isinstance(item, (list, tuple)):
                    yield from flatten(item)
                else:
                    yield item

        self.assertEqual([1, 2, 3, 4, 5], list(flatten([1, (2, [3, 4]), 5])))
        self.assertEqual([], list(flatten([])))

    def test_07_real_immutable_orders_csv_one_pass_generator_pipeline(self):
        with ORDERS.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(15, len(rows))
        self.assertEqual(12, sum(r["status"] == "delivered" for r in rows))
        pipeline = (Decimal(row["amount"]) for row in rows
                    if row["status"] == "delivered")
        self.assertEqual(Decimal("18972.00"), sum(pipeline, Decimal("0")))
        self.assertEqual(Decimal("0"), sum(pipeline, Decimal("0")))
        self.assertEqual(ORDERS_SHA, git_blob_sha(ORDERS.read_bytes()))

    def test_08_scope_lexical_lookup_and_nested_nonlocal(self):
        outside = "global-label"

        def outer():
            outside = "enclosing-label"

            def read():
                return outside

            def update():
                nonlocal outside
                outside = "updated-label"

            self.assertEqual("enclosing-label", read())
            update()
            return read()

        self.assertEqual("updated-label", outer())
        self.assertEqual("global-label", outside)

    def test_09_scope_unboundlocal_and_frozen_vs_late_closures(self):
        count = 3

        def broken():
            count += 1
            return count

        with self.assertRaises(UnboundLocalError):
            broken()
        late = [lambda: i for i in range(3)]
        fixed = [lambda i=i: i for i in range(3)]
        self.assertEqual([2, 2, 2], [fn() for fn in late])
        self.assertEqual([0, 1, 2], [fn() for fn in fixed])

    def test_10_datetime_constructor_iso_calendar_and_leap_boundaries(self):
        self.assertEqual("2024-02-29", date.fromisoformat("2024-02-29").isoformat())
        self.assertEqual(date(2024, 3, 1), date(2024, 2, 29) + timedelta(days=1))
        with self.assertRaises(ValueError):
            date.fromisoformat("2025-02-29")
        self.assertEqual("2025-04", datetime(2025, 4, 1).strftime("%Y-%m"))

    def test_11_datetime_utc_offset_crosses_local_day_boundary(self):
        offset = timezone(timedelta(hours=5, minutes=30))
        local = datetime(2025, 1, 1, 1, 15, tzinfo=offset)
        self.assertEqual("2024-12-31T19:45:00+00:00",
                         local.astimezone(timezone.utc).isoformat())
        self.assertEqual("2025-01-01T01:15:00+05:30", local.isoformat())

    def test_12_naive_aware_datetime_comparison_is_error(self):
        naive = datetime(2025, 1, 1, 0, 0)
        aware = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
        with self.assertRaises(TypeError):
            _ = naive < aware
        with self.assertRaises(TypeError):
            _ = aware - naive

    def test_13_math_builtins_floor_ceil_negative_division(self):
        self.assertEqual((5, 25, 7.25, 64), (min(5, 10, 25),
                         max(5, 10, 25), abs(-7.25), pow(4, 3)))
        self.assertEqual(-4, -7 // 2)
        self.assertEqual(-2, math.floor(-1.4))
        self.assertEqual(-1, math.ceil(-1.4))
        self.assertEqual(2, math.ceil(1.4))
        self.assertEqual(1, math.floor(1.4))

    def test_14_math_sqrt_finite_domain_and_float_precision(self):
        self.assertEqual(8.0, math.sqrt(64))
        with self.assertRaises(ValueError):
            math.sqrt(-1)
        self.assertFalse(math.isfinite(float("nan")))
        self.assertFalse(math.isfinite(float("inf")))
        self.assertNotEqual(0.3, 0.1 + 0.2)
        self.assertTrue(math.isclose(0.3, 0.1 + 0.2, abs_tol=1e-12))

    def test_15_decimal_from_string_and_rounding_policy(self):
        self.assertEqual(Decimal("0.3"), Decimal("0.1") + Decimal("0.2"))
        self.assertNotEqual(Decimal("0.1"), Decimal(0.1))
        self.assertEqual(Decimal("2.68"), Decimal("2.675").quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP))
        self.assertEqual((2, 4), (round(2.5), round(3.5)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
