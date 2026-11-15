"""Independent READ-ONLY audit of original Python Foundations lessons 01-05.

Archived Markdown examples and auditor-authored synthetic probes only.
NOT original PDF visual parity, official grades, learner attempts, or mastery.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from itertools import product
import csv
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = (ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
        / "2. Python Mastry")
LESSONS = BASE / "2. Python Foundations"
CSV_SOURCE = BASE / "python_de_dataset" / "orders.csv"
PINS = {
    1: ("01. The 6-step approach to any coding question.md", "2a176fd611ed9ec50dc8873927b56c349be0651a", 25, 3),
    2: ("02. Names objects and mutability.md", "0e8557654df4677b9bd58c05921b7338cd336203", 26, 4),
    3: ("03. Numbers strings and dates.md", "91de7da6ba563322381b46dce78a2ebcb2ce7e61", 27, 4),
    4: ("04. Lists tuples sets and Big-O.md", "15e912de271e31108a3fabf7e0abab63ff522f3d", 28, 3),
    5: ("05. Dicts defaultdict and Counter.md", "7d372ee509f2e539c8cfa0c8bdcc87a50909edce", 29, 5),
}
CSV_SHA = "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2"
FENCE = re.compile(r"(?ms)^~~~(python|text)[ \t]*\n(.*?)^~~~[ \t]*$")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def original(n: int) -> str:
    filename, sha, page, count = PINS[n]
    raw = (LESSONS / filename).read_bytes()
    actual = git_blob_sha(raw)
    if actual != sha:
        raise AssertionError(f"Original source changed for 0{n}: {actual} != {sha}")
    result = raw.decode("utf-8-sig")
    if f"Original PDF, page {page}" not in result:
        raise AssertionError(f"Missing original PDF page attribution: {page}")
    return result


def published_pairs(n: int) -> list[tuple[str, str]]:
    fences = FENCE.findall(original(n))
    codes = [body for kind, body in fences if kind == "python"]
    outputs = [body for kind, body in fences if kind == "text"]
    if len(codes) != PINS[n][3] or len(outputs) != len(codes):
        raise AssertionError(
            f"Lesson 0{n} source code/output mismatch: "
            f"{len(codes)} code, {len(outputs)} outputs, expected {PINS[n][3]}"
        )
    return list(zip(codes, outputs))


def execute_published(code: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="py-foundations-audit-") as tmp:
        destination = Path(tmp) / "python_de_dataset"
        destination.mkdir()
        raw = CSV_SOURCE.read_bytes()
        if git_blob_sha(raw) != CSV_SHA:
            raise AssertionError("Original orders.csv Git blob changed")
        (destination / "orders.csv").write_bytes(raw)
        env = dict(os.environ, PYTHONIOENCODING="utf-8", LC_ALL="C", TZ="UTC")
        return subprocess.run(
            [sys.executable, "-c", code], cwd=tmp, env=env,
            capture_output=True, text=True, timeout=15, check=False,
        )


class PreservedFiveLessons(unittest.TestCase):
    def test_01_five_immutable_sources_csv_and_nineteen_published_examples(self):
        self.assertEqual(CSV_SHA, git_blob_sha(CSV_SOURCE.read_bytes()))
        self.assertEqual(19, sum(len(published_pairs(n)) for n in PINS))
        for n in PINS:
            with self.subTest(lesson=n):
                self.assertIn(f"# 0{n}.", original(n))

    def test_02_published_lesson_01_six_steps_csv_totals_and_functions(self):
        self._check_page(1)

    def test_03_published_lesson_02_identity_defaults_and_copy(self):
        self._check_page(2)

    def test_04_published_lesson_03_decimal_unicode_and_dates(self):
        self._check_page(3)

    def test_05_published_lesson_04_lists_sets_and_sort(self):
        self._check_page(4)

    def test_06_published_lesson_05_dicts_counter_views_and_insertion_order(self):
        self._check_page(5)

    def _check_page(self, n: int):
        for idx, (source_code, expected) in enumerate(published_pairs(n), start=1):
            with self.subTest(lesson=n, snippet=idx):
                result = execute_published(source_code)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(expected, result.stdout)

    def test_07_full_original_csv_delivered_totals_independent_decimal_oracle(self):
        with CSV_SOURCE.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(15, len(rows))
        self.assertEqual(Counter({"delivered": 12, "cancelled": 2, "returned": 1}),
                         Counter(row["status"] for row in rows))
        keys = {int(r["customer_id"]) for r in rows if r["status"] == "delivered"}
        totals = {
            customer: sum(
                (Decimal(r["amount"]) for r in rows
                 if r["status"] == "delivered" and int(r["customer_id"]) == customer),
                Decimal(0),
            ) for customer in keys
        }
        self.assertEqual([(5, Decimal("5096.00")), (1, Decimal("5094.00")),
                          (2, Decimal("4143.00")), (6, Decimal("1998.00")),
                          (4, Decimal("1048.00")), (7, Decimal("846.00")),
                          (3, Decimal("747.00"))],
                         sorted(totals.items(), key=lambda x: (-x[1], x[0])))
        self.assertNotIn(8, totals)

    def test_08_mutable_default_reuses_state_but_none_guard_isolates_calls(self):
        def bad_add(item, batch=[]):
            batch.append(item)
            return batch
        self.assertEqual(["a"], bad_add("a"))
        self.assertEqual(["a", "b"], bad_add("b"))
        def safe_add(item, batch=None):
            batch = [] if batch is None else batch
            batch.append(item)
            return batch
        self.assertEqual(["a"], safe_add("a"))
        self.assertEqual(["b"], safe_add("b"))

    def test_09_alias_shallow_and_deep_nested_mutation_boundaries(self):
        original_rows = [{"tags": ["new"]}]
        shallow, deep = original_rows.copy(), deepcopy(original_rows)
        shallow[0]["tags"].append("vip")
        self.assertEqual(["new", "vip"], original_rows[0]["tags"])
        self.assertEqual(["new"], deep[0]["tags"])
        self.assertIsNot(original_rows, shallow)
        self.assertIs(original_rows[0], shallow[0])

    def test_10_decimal_from_text_vs_float_and_explicit_rounding(self):
        self.assertEqual(Decimal("0.3"), Decimal("0.1") + Decimal("0.2"))
        self.assertNotEqual(Decimal("0.1"), Decimal(0.1))
        self.assertEqual(Decimal("2.68"), Decimal("2.675").quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP))
        self.assertEqual((2, 4), (round(2.5), round(3.5)))

    def test_11_negative_floor_vs_truncation_and_negative_amount_policy(self):
        self.assertEqual(-4, -7 // 2)
        self.assertEqual(-3, int(-3.5))
        self.assertEqual(Decimal("-5.20"), Decimal("-5.20"))
        # The archived walkthrough does not define refund/money-sign policy.

    def test_12_utf8_bytes_and_delimiter_pitfall_are_distinct(self):
        self.assertEqual((4, 5), (len("café"), len("café".encode("utf-8"))))
        self.assertEqual(3, len("₹".encode("utf-8")))
        self.assertEqual(2, len("1,200".split(",")))  # naive split breaks CSV fields
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "amount.csv"
            path.write_text('id,amount\n1,"1,200"\n', encoding="utf-8")
            with path.open(newline="", encoding="utf-8") as file:
                self.assertEqual("1,200", next(csv.DictReader(file))["amount"])

    def test_13_kolkata_aware_utc_boundary_and_calendar_days(self):
        india = timezone(timedelta(hours=5, minutes=30))
        src = datetime(2025, 4, 1, 10, 0, tzinfo=india)
        self.assertEqual("2025-04-01T04:30:00+00:00",
                         src.astimezone(timezone.utc).isoformat())
        self.assertEqual(date(2025, 4, 1), date(2025, 3, 31) + timedelta(days=1))
        self.assertEqual(47, (date(2025, 4, 28) - date(2025, 3, 12)).days)

    def test_14_naive_and_aware_datetime_comparison_does_not_silently_convert(self):
        naive = datetime(2025, 4, 1, 10)
        aware = naive.replace(tzinfo=timezone.utc)
        with self.assertRaises(TypeError):
            _ = naive < aware
        self.assertEqual(10, aware.hour)
        self.assertIsNone(naive.tzinfo)

    def test_15_stable_sort_and_sort_in_place_return_value(self):
        rows = [("a", 2), ("b", 1), ("a", 2)]
        self.assertEqual([("b", 1), ("a", 2), ("a", 2)],
                         sorted(rows, key=lambda x: x[1]))
        copied = rows.copy()
        self.assertIsNone(copied.sort(key=lambda x: x[1]))
        self.assertEqual(rows, [("a", 2), ("b", 1), ("a", 2)])

    def test_16_set_reconciliation_and_unhashable_list_key(self):
        before, after = {101, 102, 103}, {101, 104}
        self.assertEqual([102, 103], sorted(before - after))
        self.assertEqual([104], sorted(after - before))
        self.assertEqual({101}, before & after)
        with self.assertRaises(TypeError):
            _ = {[1, 2]: "no"}
        self.assertEqual("yes", {(1, 2): "yes"}[(1, 2)])

    def test_17_get_fallback_does_not_replace_present_none(self):
        row = {"city": None}
        self.assertIsNone(row.get("city", "Unknown"))
        self.assertEqual("Unknown", row.get("city") or "Unknown")
        self.assertEqual("Unknown", {}.get("city", "Unknown"))

    def test_18_counter_order_and_distinct_defaultdict_lists(self):
        counts = Counter("aabba")
        self.assertEqual(3, counts["a"])
        self.assertEqual(0, counts["missing"])
        grouped = defaultdict(list)
        grouped[1].append("mouse")
        self.assertEqual([], grouped[2])
        self.assertEqual(["mouse"], grouped[1])

    def test_19_duplicate_lookup_keys_overwrite_without_moving_first_key(self):
        rows = [{"id": 2, "name": "old"}, {"id": 1, "name": "one"},
                {"id": 2, "name": "new"}]
        by_id = {r["id"]: r for r in rows}
        self.assertEqual([2, 1], list(by_id))
        self.assertEqual("new", by_id[2]["name"])
        # Original lesson does not define duplicate source-key conflict policy.

    def test_20_243_synthetic_three_status_combinations_vs_brute_force_oracle(self):
        statuses = ("delivered", "cancelled", "returned")
        for sequence in product(statuses, repeat=5):
            rows = [{"customer_id": i % 3 + 1, "status": status,
                     "amount": Decimal(i + 1)} for i, status in enumerate(sequence)]
            actual = defaultdict(Decimal)
            for row in rows:
                if row["status"] == "delivered":
                    actual[row["customer_id"]] += row["amount"]
            expected = {}
            for cid in {r["customer_id"] for r in rows}:
                subtotal = sum((r["amount"] for r in rows
                                if r["customer_id"] == cid and r["status"] == "delivered"),
                               Decimal(0))
                if any(r["customer_id"] == cid and r["status"] == "delivered"
                       for r in rows):
                    expected[cid] = subtotal
            self.assertEqual(expected, dict(actual))


if __name__ == "__main__":
    unittest.main(verbosity=2)
