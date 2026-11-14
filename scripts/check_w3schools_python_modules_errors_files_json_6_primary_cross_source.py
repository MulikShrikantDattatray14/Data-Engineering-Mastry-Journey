#!/usr/bin/env python3
"""Six hosted W3 Python pages vs immutable mentorship L16-L18: audit-only.

Reviewer-authored bounded tests; original source and original dataset read-only.
Neither hosted W3 editor acceptance nor original PDF/learner/provider verification.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
LESSONS = BASE / "1. Python from Zero"
DATA = BASE / "python_de_dataset" / "customers.json"

SOURCES = (
    ("16. Modules packages and pip.md", "2002d657a4bb52dcd1e369a9083dfd1d7b5c37eb", "page 20 of 80"),
    ("17. Reading errors.md", "9159ef47b425806d4622584284b1a145543f5222", "page 21 of 80"),
    ("18. Files - read and write.md", "d47356de0ec044cc16cd61377535266af3a3c50f", "page 22 of 80"),
)
JSON_SHA = "d6125fce237e7f7e3193667946d1eb117cd19db0"


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class W3PythonModulesErrorsFilesJsonSourceContracts(unittest.TestCase):
    def test_01_immutable_original_lessons_pages_links_and_json_fixture(self):
        read = {}
        for name, sha, page in SOURCES:
            with self.subTest(name=name):
                content = (LESSONS / name).read_bytes()
                self.assertEqual(sha, git_blob_id(content))
                read[name[:2]] = content.decode("utf-8-sig")
                self.assertIn(page, read[name[:2]])
        self.assertIn("https://www.w3schools.com/python/python_modules.asp", read["16"])
        self.assertIn("https://www.w3schools.com/python/python_try_except.asp", read["17"])
        self.assertIn("https://www.w3schools.com/python/python_json.asp", read["18"])
        self.assertIn('with open("scratch_report.txt", "a"', read["18"])
        self.assertEqual(JSON_SHA, git_blob_id(DATA.read_bytes()))

    def test_02_module_import_alias_and_main_guard_in_disposable_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "helpers.py").write_text(
                'def clean(value):\n    return value.strip().lower()\n',
                encoding="utf-8",
            )
            (d / "tool.py").write_text(
                'import helpers as h\n'
                'def main():\n    print(h.clean("  DELIVERED  "))\n'
                'if __name__ == "__main__":\n    main()\n',
                encoding="utf-8",
            )
            command = subprocess.run(
                [sys.executable, "-c",
                 'from helpers import clean; import tool; print("import:", clean(" X "))'],
                cwd=d, text=True, capture_output=True, check=True,
            )
            self.assertEqual("import: x\n", command.stdout)
            direct = subprocess.run(
                [sys.executable, "tool.py"], cwd=d, text=True,
                capture_output=True, check=True,
            )
            self.assertEqual("delivered\n", direct.stdout)

    def test_03_module_import_top_level_effect_runs_once_per_process(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "rates.py").write_text(
                'print("initialising rates")\nMULTIPLIER = 2\n', encoding="utf-8"
            )
            run = subprocess.run(
                [sys.executable, "-c",
                 'import rates; import rates; from rates import MULTIPLIER; print(MULTIPLIER)'],
                cwd=d, text=True, capture_output=True, check=True,
            )
            self.assertEqual("initialising rates\n2\n", run.stdout)

    def test_04_try_except_else_finally_specific_bad_data_and_good_data(self):
        trace = []
        def parse(value):
            try:
                amount = float(value)
            except ValueError:
                trace.append("bad-value")
                return None
            else:
                trace.append("good")
                return amount
            finally:
                trace.append("finally")
        self.assertIsNone(parse("bad"))
        self.assertEqual(["bad-value", "finally"], trace)
        trace.clear()
        self.assertEqual(12.5, parse("12.5"))
        self.assertEqual(["good", "finally"], trace)
        trace.clear()
        with self.assertRaises(TypeError):
            parse(None)
        self.assertEqual(["finally"], trace)

    def test_05_exception_raise_and_finally_on_propagation(self):
        trace = []
        def validate(amount):
            try:
                if amount < 0:
                    raise ValueError("negative")
                return amount
            finally:
                trace.append("cleanup")
        with self.assertRaisesRegex(ValueError, "negative"):
            validate(-1)
        self.assertEqual([ "cleanup" ], trace)
        self.assertEqual(9, validate(9))
        self.assertEqual(["cleanup", "cleanup"], trace)

    def test_06_file_read_default_and_missing_file_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            target = d / "orders.txt"
            with self.assertRaises(FileNotFoundError):
                target.open(encoding="utf-8")
            target.write_text("a\nb\n", encoding="utf-8")
            with target.open(encoding="utf-8") as handle:
                self.assertEqual("a\n", handle.readline())
                self.assertEqual("b\n", handle.readline())
                self.assertEqual("", handle.readline())
            self.assertTrue(handle.closed)

    def test_07_file_modes_w_a_x_and_read_only_origin_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "report.txt"
            target.write_text("yesterday\n", encoding="utf-8")
            with target.open("a", encoding="utf-8") as handle:
                handle.write("today\n")
            self.assertEqual("yesterday\ntoday\n", target.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                target.open("x", encoding="utf-8")
            with target.open("w", encoding="utf-8") as handle:
                handle.write("replacement\n")
            self.assertEqual("replacement\n", target.read_text(encoding="utf-8"))
            with (Path(temp) / "new.txt").open("x", encoding="utf-8") as handle:
                handle.write("created\n")
            self.assertTrue((Path(temp) / "new.txt").exists())

    def test_08_with_closes_file_after_exception(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "source.txt"
            target.write_text("intact\n", encoding="utf-8")
            handle = None
            with self.assertRaisesRegex(RuntimeError, "synthetic"):
                with target.open(encoding="utf-8") as handle:
                    self.assertEqual("intact\n", handle.readline())
                    raise RuntimeError("synthetic")
            self.assertTrue(handle.closed)
            self.assertEqual("intact\n", target.read_text(encoding="utf-8"))

    def test_09_text_read_size_readline_and_unicode_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "unicode.txt"
            target.write_text("Sana,पुणे\nDiya,Mumbai\n", encoding="utf-8")
            with target.open(encoding="utf-8") as handle:
                self.assertEqual("Sana,", handle.read(5))
                self.assertEqual("पुणे\n", handle.readline())
                self.assertEqual("Diya,Mumbai\n", handle.readline())
            with target.open(encoding="utf-8") as handle:
                self.assertEqual(["Sana,पुणे", "Diya,Mumbai"], handle.read().splitlines())

    def test_10_naive_csv_split_vs_quoted_comma_csv_module(self):
        record = 'order_id,city,amount\n101,"Pune, Maharashtra",1198.00\n'
        naive = record.splitlines()[1].split(",")
        self.assertEqual(4, len(naive))
        parsed = list(csv.DictReader(io.StringIO(record)))
        self.assertEqual([{"order_id": "101", "city": "Pune, Maharashtra",
                           "amount": "1198.00"}], parsed)

    def test_11_json_boolean_null_tuples_and_round_trip(self):
        payload = {"active": True, "city": None, "tags": ("new", "vip")}
        encoded = json.dumps(payload, sort_keys=True)
        self.assertEqual('{"active": true, "city": null, "tags": ["new", "vip"]}', encoded)
        self.assertEqual({"active": True, "city": None, "tags": ["new", "vip"]},
                         json.loads(encoded))
        self.assertIsInstance(json.loads("[1, 2]"), list)
        self.assertEqual("hello", json.loads('"hello"'))

    def test_12_json_invalid_trailing_and_duplicate_keys(self):
        for bad in ('{"a":1,}', '{"a":1} trailing', '{"a":', "{a:1}"):
            with self.subTest(bad=bad):
                with self.assertRaises(json.JSONDecodeError):
                    json.loads(bad)
        sample = '{"status":"delivered","status":"cancelled"}'
        self.assertEqual("cancelled", json.loads(sample)["status"])
        def reject_duplicate(pairs):
            seen = {}
            for key, val in pairs:
                if key in seen:
                    raise ValueError("duplicate field: " + key)
                seen[key] = val
            return seen
        with self.assertRaisesRegex(ValueError, "duplicate field"):
            json.loads(sample, object_pairs_hook=reject_duplicate)

    def test_13_json_nonfinite_number_is_not_strict_json(self):
        import math
        self.assertEqual("NaN", json.dumps(float("nan")))
        self.assertTrue(math.isnan(json.loads("NaN")))
        with self.assertRaises(ValueError):
            json.dumps(float("nan"), allow_nan=False)
        with self.assertRaises(ValueError):
            json.loads("NaN", parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError("nonfinite: " + constant)
            ))

    def test_14_original_customers_json_8_rows_and_null_city_contract(self):
        customers = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(8, len(customers))
        self.assertEqual(list(range(1, 9)), [x["customer_id"] for x in customers])
        self.assertEqual(("Sana", None),
                         (customers[5]["name"], customers[5]["address"]["city"]))
        self.assertEqual({"Bengaluru", "Mumbai", "Delhi", "Pune", "Hyderabad"},
                         {x["address"]["city"] for x in customers
                          if x["address"]["city"] is not None})


if __name__ == "__main__":
    unittest.main(verbosity=2)
