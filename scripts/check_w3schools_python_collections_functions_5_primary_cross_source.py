#!/usr/bin/env python3
"""Read-only five-primary-page W3 Python collection/functions cross-source review.

Original mentorship companions are pinned as immutable Git blobs. All executable
cases are reviewer-authored synthetic fixtures, NOT official keys, hosted W3
editor grades or independent learner submissions.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry" / "1. Python from Zero"
SOURCES = (
    ("11. Tuples and sets.md", "3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e", "page 15 of 80"),
    ("12. Dictionaries - key and value.md", "3602334cd9cc779f89eface11b82f844954068a8", "page 16 of 80"),
    ("13. Which data structure.md", "1142a434f0bda23d683eaf2de5176a4c13020438", "page 17 of 80"),
    ("14. Functions - reusable steps.md", "cb497c2660c6e3ae34b330f372ef087fa3550d4b", "page 18 of 80"),
    ("15. Functions part 2 - mini pipeline.md", "abf9377580230db87cc4632ae933478e89bc4df2", "page 19 of 80"),
)
HOSTED_LINKS = (
    ("11. Tuples and sets.md", "https://www.w3schools.com/python/python_tuples.asp"),
    ("11. Tuples and sets.md", "https://www.w3schools.com/python/python_sets.asp"),
    ("12. Dictionaries - key and value.md", "https://www.w3schools.com/python/python_dictionaries.asp"),
    ("14. Functions - reusable steps.md", "https://www.w3schools.com/python/python_functions.asp"),
)


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class PythonCollectionsFunctionsCrossSource(unittest.TestCase):
    def test_01_five_original_sha_pages_links_and_lambda_anchor(self):
        texts = {}
        for name, sha, page in SOURCES:
            with self.subTest(name=name):
                data = (ARCHIVE / name).read_bytes()
                self.assertEqual(blob_id(data), sha)
                texts[name] = data.decode("utf-8-sig")
                self.assertIn(page, texts[name])
        for name, url in HOSTED_LINKS:
            self.assertIn(url, texts[name])
        self.assertIn("lambda item: item[1]", texts["15. Functions part 2 - mini pipeline.md"])

    def test_02_tuple_singleton_unpack_and_assignment_error(self):
        self.assertIsInstance((101,), tuple)
        self.assertIsInstance((101), int)
        record = ("2025-04-20", 2397, 2397)
        day, amount, duplicate = record
        self.assertEqual((day, amount, duplicate), record)
        self.assertEqual(2, record.count(2397))
        with self.assertRaises(TypeError):
            record[0] = "2026-04-20"

    def test_03_tuple_nested_mutable_and_unhashable_members(self):
        item = (101, ["delivered"])
        item[1].append("returned")
        self.assertEqual((101, ["delivered", "returned"]), item)
        with self.assertRaises(TypeError):
            hash(item)
        self.assertEqual({(101, "Pune")}, {(101, "Pune"), (101, "Pune")})

    def test_04_set_duplicate_bool_integer_equivalence(self):
        self.assertEqual(2, len({True, 1, False, 0}))
        self.assertEqual({0, 1}, {True, 1, False, 0})
        self.assertEqual({101, 102, 103}, set([101, 102, 101, 103]))
        self.assertTrue(1 in {True})

    def test_05_set_snapshot_operations_and_deterministic_reporting(self):
        yesterday, today = {101, 102, 103}, {102, 103, 104}
        self.assertEqual([104], sorted(today - yesterday))
        self.assertEqual([101], sorted(yesterday - today))
        self.assertEqual([102, 103], sorted(today & yesterday))
        self.assertEqual([101, 102, 103, 104], sorted(today | yesterday))
        self.assertEqual([101, 104], sorted(today ^ yesterday))

    def test_06_empty_set_versus_dict_and_unhashable_list(self):
        self.assertIsInstance({}, dict)
        self.assertIsInstance(set(), set)
        with self.assertRaises(TypeError):
            _ = {[101, 102]}
        with self.assertRaises(TypeError):
            _ = {("city", ["Pune"])}

    def test_07_dictionary_duplicate_key_update_retains_position(self):
        d = {"a": 1, "b": 2, "a": 3}
        self.assertEqual({"a": 3, "b": 2}, d)
        self.assertEqual(["a", "b"], list(d))
        d["a"] = 4
        self.assertEqual(["a", "b"], list(d))
        d["c"] = 4
        self.assertEqual(["a", "b", "c"], list(d))
        self.assertEqual(2, list(d.values()).count(4))

    def test_08_dict_missing_key_vs_present_none_and_counts(self):
        d = {"city": None}
        self.assertIsNone(d.get("city", "UNKNOWN"))
        self.assertEqual("UNKNOWN", d.get("country", "UNKNOWN"))
        with self.assertRaises(KeyError):
            _ = d["country"]
        counts = {}
        for status in ["delivered", "cancelled", "delivered"]:
            counts[status] = counts.get(status, 0) + 1
        self.assertEqual({"delivered": 2, "cancelled": 1}, counts)

    def test_09_dict_bool_key_collisions_and_zip_truncation(self):
        self.assertEqual(1, len({True: "a", 1: "b"}))
        self.assertEqual("b", {True: "a", 1: "b"}[True])
        self.assertEqual({101: 1198, 102: 796}, dict(zip([101, 102, 103], [1198, 796])))
        self.assertEqual([101, 102], list(dict(zip([101, 102, 103], [1198, 796]))))

    def test_10_order_preserving_dedup_vs_nondeterministic_set_order(self):
        names = ["Aarav", "Diya", "Aarav", "Kabir", "Diya"]
        self.assertEqual(["Aarav", "Diya", "Kabir"], list(dict.fromkeys(names)))
        self.assertEqual({"Aarav", "Diya", "Kabir"}, set(names))
        self.assertEqual([101, 102], [id_ for id_ in [101, 102, 101] if id_ in {101, 102}][:2])
        self.assertEqual((747, 3498), (min([747, 3498, 1048]), max([747, 3498, 1048])))

    def test_11_function_printing_not_returning_and_call_count(self):
        seen = []
        def total_print(a, b):
            print(a + b)
        def total_return(a, b):
            seen.append("called")
            return a + b
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            x = total_print(2, 3)
        self.assertEqual("5\n", stream.getvalue())
        self.assertIsNone(x)
        self.assertEqual(5, total_return(2, 3))
        self.assertEqual(["called"], seen)

    def test_12_function_default_keyword_and_local_scope(self):
        def order_label(order_id, status="pending"):
            local_only = str(order_id)
            return local_only + ": " + status
        self.assertEqual("101: pending", order_label(101))
        self.assertEqual("102: delivered", order_label(status="delivered", order_id=102))
        self.assertNotIn("local_only", locals())
        with self.assertRaises(TypeError):
            order_label()

    def test_13_lambda_sort_key_ties_and_late_binding(self):
        items = [("Mouse", 799), ("Hub", 1499), ("Lamp", 1499), ("Pens", 149)]
        self.assertEqual(["Hub", "Lamp", "Mouse", "Pens"],
                         [x[0] for x in sorted(items, key=lambda x: x[1], reverse=True)])
        self.assertEqual(("Hub", 1499), max(items, key=lambda x: x[1]))
        deferred = [lambda: i for i in range(3)]
        self.assertEqual([2, 2, 2], [f() for f in deferred])
        bound = [lambda i=i: i for i in range(3)]
        self.assertEqual([0, 1, 2], [f() for f in bound])

    def test_14_original_pipeline_policy_does_not_catch_invalid_numeric(self):
        def parse(line):
            parts = line.split(",")
            if len(parts) != 3:
                return None
            order_id, status, amount = parts
            return {"id": int(order_id), "status": status.strip().lower(),
                    "amount": float(amount)}
        self.assertIsNone(parse("bad row"))
        self.assertEqual({"id": 101, "status": "delivered", "amount": 1198.0},
                         parse("101, Delivered ,1198"))
        with self.assertRaises(ValueError):
            parse("102,delivered,not-a-number")
        with self.assertRaises(ValueError):
            parse("not-an-id,delivered,5")
        self.assertEqual(-5.0, parse("102,delivered,-5")["amount"])
        self.assertEqual("unknown", parse("103,UNKNOWN,5")["status"])

    def test_15_dedup_first_policy_and_raw_duplicate_revenue(self):
        orders = [
            {"id": 101, "status": "delivered", "amount": 1198.0},
            {"id": 101, "status": "delivered", "amount": 1499.0},
            {"id": 102, "status": "cancelled", "amount": 796.0},
            {"id": 103, "status": "delivered", "amount": 500.0},
        ]
        raw = sum(r["amount"] for r in orders if r["status"] == "delivered")
        self.assertEqual(3197.0, raw)
        seen, unique = set(), []
        for row in orders:
            if row["id"] not in seen:
                seen.add(row["id"])
                unique.append(row)
        self.assertEqual([101, 102, 103], [x["id"] for x in unique])
        self.assertEqual(1698.0, sum(r["amount"] for r in unique if r["status"] == "delivered"))
        self.assertNotEqual(raw, 1698.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
