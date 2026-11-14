"""Independent READ-ONLY cross-source replay of original Python-from-Zero lessons 16-20.

Original archive blobs are immutable; snippets run only in disposable folders.
These checks are NOT original PDF image parity, provider grading, learner attempts,
newly achieved mastery, or validation of W3Schools hosted editor behavior.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
LESSONS = BASE / "1. Python from Zero"
DATA = BASE / "python_de_dataset"
SOURCES = {
    16: ("16. Modules packages and pip.md", "2002d657a4bb52dcd1e369a9083dfd1d7b5c37eb"),
    17: ("17. Reading errors.md", "9159ef47b425806d4622584284b1a145543f5222"),
    18: ("18. Files - read and write.md", "d47356de0ec044cc16cd61377535266af3a3c50f"),
    19: ("19. Mini project - monthly sales report.md", "30992048e800aa0aaf8e8940546993d5b48be366"),
    20: ("20. Practice set 0 - first steps.md", "5c5ee4773abcf2b797bd08d46a6a6421388b0962"),
}
DATA_PINS = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "events.jsonl": "975c007a68c336007023a9ebd92ba82f02a6b7c3",
}
FENCE = chr(96) * 3
PY_BLOCK = re.compile(r"(?ms)^" + FENCE + r"python[ \t]*\n(.*?)^" + FENCE + r"[ \t]*$")
TILDE_BLOCK = re.compile(r"(?ms)^~~~python[ \t]*\n(.*?)^~~~[ \t]*$")


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source(n: int) -> str:
    name, expected = SOURCES[n]
    raw = (LESSONS / name).read_bytes()
    actual = blob_sha(raw)
    if actual != expected:
        raise AssertionError(f"Original lesson {n} changed: {actual} != {expected}")
    return raw.decode("utf-8-sig")


def snippets(n: int, tilde: bool = False) -> list[str]:
    matches = (TILDE_BLOCK if tilde else PY_BLOCK).findall(source(n))
    if not matches:
        raise AssertionError(f"Missing archived code fences for lesson {n}")
    return matches


def run_original(n: int, ids: list[int], extra: str = "", tilde: bool = False,
                 seed_files: bool = False) -> subprocess.CompletedProcess[str]:
    codes = snippets(n, tilde)
    if any(i >= len(codes) for i in ids):
        raise AssertionError(f"Lesson {n} missing source block {ids}; found {len(codes)}")
    script = "\n\n".join(codes[i] for i in ids) + "\n" + extra
    with tempfile.TemporaryDirectory(prefix="original-py-source-audit-") as td:
        directory = Path(td)
        if seed_files:
            target = directory / "python_de_dataset"
            target.mkdir()
            for filename, expected in DATA_PINS.items():
                item = DATA / filename
                raw = item.read_bytes()
                assert blob_sha(raw) == expected, f"Original data changed: {filename}"
                shutil.copyfile(item, target / filename)
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=directory, capture_output=True, text=True, check=False, timeout=15,
        )


class ImmutablePython16To20(unittest.TestCase):
    def test_01_all_five_lessons_and_three_csv_json_sources_have_original_blob_ids(self):
        for page in SOURCES:
            with self.subTest(lesson=page):
                self.assertIn(f"# {page}.", source(page).lstrip("\ufeff"))
        for filename, expected in DATA_PINS.items():
            with self.subTest(dataset=filename):
                self.assertEqual(expected, blob_sha((DATA / filename).read_bytes()))

    def test_02_module_stdlib_snippet_has_source_published_output(self):
        proc = run_original(16, [0])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            "12.0 5 4\n2 Pune\n2025-05-01\n1164.3333333333333 1198\n",
            proc.stdout,
        )

    def test_03_source_created_module_and_main_guard_separate_import_from_run(self):
        proc = run_original(16, [5])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            "delivered ['cancelled', 'delivered', 'returned']\n"
            "imported; its __name__ is tool\n"
            "run directly: running the tool\n",
            proc.stdout,
        )
        w3 = run_original(16, [1, 2], tilde=True)
        self.assertEqual(0, w3.returncode, w3.stderr)
        self.assertEqual("600.0\n", w3.stdout)

    def test_04_archived_zero_division_failure_and_guarded_repair(self):
        bad = run_original(17, [0])
        self.assertNotEqual(0, bad.returncode)
        self.assertIn("ZeroDivisionError: division by zero", bad.stderr)
        fixed = run_original(17, [1])
        self.assertEqual(0, fixed.returncode, fixed.stderr)
        self.assertEqual("0\n997.0\n", fixed.stdout)

    def test_05_source_dirty_amounts_and_debug_output(self):
        bad = run_original(17, [2])
        self.assertEqual(0, bad.returncode, bad.stderr)
        self.assertEqual("total: 3493.0 | could not read: ['abc', '']\n", bad.stdout)
        debug = run_original(17, [3])
        self.assertEqual(0, debug.returncode, debug.stderr)
        self.assertEqual(
            "DEBUG 101 '1198' str\nDEBUG 102 796 int\n"
            "total: 1994.0\ncheck passed\n", debug.stdout,
        )
        w3 = run_original(17, [0], tilde=True)
        self.assertEqual(0, w3.returncode, w3.stderr)
        self.assertEqual("Quantity must be a whole number\nCheck complete\n", w3.stdout)

    def test_06_original_small_csv_line_and_stream_examples(self):
        proc = run_original(18, [0, 1, 3])
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            "'order_id,customer_id,order_date,status,amount\\n'\n"
            "['101', '1', '2025-01-10', 'delivered', '1198.00']\n"
            "4 lines; last: 103,1,2025-01-12,delivered,796.00\n"
            "delivered revenue: 1,994.00\n", proc.stdout,
        )

    def test_07_supplied_fifteen_order_csv_replay_and_independent_oracle(self):
        proc = run_original(18, [2], seed_files=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            "16 lines including the header\n"
            "first order: 101,1,2025-01-10,delivered,1198.00\n"
            "last order: 115,5,2025-04-28,delivered,1598.00\n",
            proc.stdout,
        )
        with (DATA / "orders.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(15, len(rows))
        self.assertEqual(Decimal("18972.00"), sum(
            (Decimal(row["amount"]) for row in rows if row["status"] == "delivered"),
            Decimal("0"),
        ))
        self.assertEqual(Counter({"delivered": 12, "cancelled": 2, "returned": 1}),
                         Counter(row["status"] for row in rows))

    def test_08_file_append_paths_and_archived_customers_json_example(self):
        text = run_original(18, [0, 4, 5], seed_files=True)
        self.assertEqual(0, text.returncode, text.stderr)
        self.assertIn("date,revenue\n2025-04-20,2397\n2025-04-28,1598\n", text.stdout)
        self.assertIn("True False\n", text.stdout)
        self.assertIn("['customers.json', 'events.jsonl']\n", text.stdout)
        self.assertIn("reports/2025-04/summary.txt", text.stdout)
        w3 = run_original(18, [0], tilde=True, seed_files=True)
        self.assertEqual(0, w3.returncode, w3.stderr)
        self.assertEqual('8\nSana None\n{"active": true, "city": null}\n', w3.stdout)

    def test_09_literal_monthly_sales_project_exact_published_output(self):
        proc = run_original(19, [0, 1, 2, 3], seed_files=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            "15 orders read\n"
            "month     orders    revenue   average     best\n"
            "----------------------------------------------\n"
            "2025-01        2   1,994.00    997.00    1,198\n"
            "2025-02        2   2,847.00  1,423.50    1,499\n"
            "2025-03        4   7,291.00  1,822.75    3,498\n"
            "2025-04        4   6,840.00  1,710.00    2,397\n"
            "----------------------------------------------\n"
            "total             18,972.00\n",
            proc.stdout,
        )

    def test_10_monthly_sales_oracle_reconciles_every_month_independently(self):
        with (DATA / "orders.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        buckets = defaultdict(list)
        for row in rows:
            if row["status"] == "delivered":
                buckets[row["order_date"][:7]].append(Decimal(row["amount"]))
        expect = {month: (len(amounts), sum(amounts), max(amounts))
                  for month, amounts in sorted(buckets.items())}
        self.assertEqual({
            "2025-01": (2, Decimal("1994.00"), Decimal("1198.00")),
            "2025-02": (2, Decimal("2847.00"), Decimal("1499.00")),
            "2025-03": (4, Decimal("7291.00"), Decimal("3498.00")),
            "2025-04": (4, Decimal("6840.00"), Decimal("2397.00")),
        }, expect)
        small = run_original(19, [1, 4])
        self.assertEqual(0, small.returncode, small.stderr)
        self.assertEqual(
            "{'2025-01': {'orders': 2, 'revenue': 1994.0, 'best': 1198.0}}\n",
            small.stdout,
        )

    def test_11_original_five_practice_answer_examples_not_learner_solutions(self):
        expected = [
            "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz\n",
            "747 3498\n",
            "{'data': 3, 'pipelines': 2, 'move': 1, 'and': 1, 'fail': 1}\n",
            "True False\n",
            "delivered  12  80.0%\ncancelled   2  13.3%\nreturned    1  6.7%\n",
        ]
        for idx, output in enumerate(expected):
            with self.subTest(question=idx + 1):
                proc = run_original(20, [idx], seed_files=idx == 4)
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertEqual(output, proc.stdout)

    def test_12_synthetic_dirty_data_boundaries_are_not_source_dataset_failures(self):
        proc = run_original(
            19, [0, 1],
            extra=(
                "\nfrom pathlib import Path\n"
                "Path('quoted.csv').write_text("
                "'order_id,customer_id,order_date,status,amount\\n'"
                "'1,1,2025-01-01,delivered,\"1,200\"\\n')\n"
                "try:\n"
                "    build_report(read_orders('quoted.csv'))\n"
                "except ValueError as exc:\n"
                "    print(type(exc).__name__)\n"
                "print(build_report([{'order_date': '2025-99-01',"
                "'status': 'delivered', 'amount': '-5'}]))\n"
            ),
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("ValueError\n", proc.stdout)
        self.assertIn("'2025-99': {'orders': 1, 'revenue': -5.0, 'best': 0.0}",
                      proc.stdout)
        nan = run_original(17, [2], extra="\nprint(float('nan') == float('nan'))\n")
        self.assertEqual(0, nan.returncode, nan.stderr)
        self.assertIn("False\n", nan.stdout)
        palindrome = run_original(20, [3], extra="\nprint(is_palindrome('!?'))\n")
        self.assertEqual(0, palindrome.returncode, palindrome.stderr)
        self.assertEqual("True False\nTrue\n", palindrome.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
