#!/usr/bin/env python3
"""Independent bounded replay of original Python DE p71-p74; immutable archive.

Runs the unchanged archived p72 source example and its extracted functions on
separate synthetic fixtures. Other probes document contract limitations.
Neither official PDF parity nor native Spark/Airflow/learner mastery is claimed.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
SOURCES = {
    "p71": ("6. Python for Data Engineering/03. Python and databases.md",
            "02af93e471c9f933274981230981102c72e76d69"),
    "p72": ("6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md",
            "fc859b44748d06318f2d0bdb4ae36266715253e7"),
    "p73": ("6. Python for Data Engineering/05. Testing and data quality.md",
            "05b4ff35d2666ef5908237686f2a517dd718301a"),
    "p74": ("6. Python for Data Engineering/06. From pandas to PySpark and Airflow.md",
            "17b999bcc639f184c5ca7bac4c3a325d4d05e763"),
    "orders": ("python_de_dataset/orders.csv",
               "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2"),
}
DAY = "2025-04-20"

def read_source(key):
    rel, sha = SOURCES[key]
    data = (BASE / rel).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != sha:
        raise AssertionError(f"archive blob mismatch {key}: {actual} != {sha}")
    return data.decode("utf-8-sig")

def code_fence(key, index=0):
    snippets = re.findall(r"(?ms)^" + r"\x60{3}python[^\n]*\n" +
                          r"(.*?)^\x60{3}[ \t]*$", read_source(key))
    if len(snippets) <= index:
        raise AssertionError(f"missing original Python fence {key}/{index}")
    return snippets[index]

def source_functions():
    full = code_fence("p72")
    before, separator, _ = full.rpartition("connection = sqlite3.connect(':memory:')")
    assert separator and "def load(" in before and "def extract(" in before
    namespace = {"__name__": "auditor_p72_replay"}
    exec(compile(before, "<p72 original ETL functions>", "exec"), namespace)
    return namespace

def new_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE fact_orders (order_id INT PRIMARY KEY, "
               "customer_id INT, order_date TEXT, status TEXT, amount REAL)")
    return db

class OriginalSourceETLReviewer(unittest.TestCase):
    def test_five_immutable_source_blobs(self):
        for key in SOURCES:
            with self.subTest(key=key):
                self.assertGreater(len(read_source(key)), 50)
        self.assertIn("NotImplementedError('Connect a warehouse MERGE here')",
                      read_source("p74"))
        self.assertIn("def run_checks(", read_source("p73"))

    def test_original_p72_three_runs_and_exact_stdout(self):
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            data = tmp / "python_de_dataset"
            data.mkdir()
            (data / "orders.csv").write_bytes((BASE / SOURCES["orders"][0]).read_bytes())
            program = tmp / "original_p72.py"
            program.write_text(code_fence("p72"), encoding="utf-8")
            result = subprocess.run([sys.executable, str(program)], cwd=tmp,
                                    text=True, capture_output=True, timeout=12,
                                    check=True)
            self.assertEqual(result.stdout.strip().splitlines(), [
                "INFO orders_daily: date=2025-04-20 loaded=1 table_rows=1",
                "INFO orders_daily: date=2025-04-20 loaded=1 table_rows=1",
                "INFO orders_daily: date=2025-04-28 loaded=1 table_rows=2"])
            self.assertEqual(result.stderr, "")

    def test_original_extract_is_exact_day_not_month(self):
        n = source_functions()
        path = BASE / SOURCES["orders"][0]
        selected = list(n["extract"](path, DAY))
        self.assertEqual([r["order_id"] for r in selected], ["114"])
        self.assertEqual(list(n["extract"](path, "2030-01-01")), [])

    def test_original_transform_normalizes_and_casts(self):
        n = source_functions()
        row = {"order_id": "17", "customer_id": "2",
               "order_date": DAY, "status": "  DELIVERED ",
               "amount": "12.50"}
        self.assertEqual(list(n["transform"]([row])),
                         [(17, 2, DAY, "delivered", 12.5)])

    def test_rerun_replaces_changed_amount_without_duplicate(self):
        n = source_functions()
        with new_db() as db:
            self.assertEqual(n["load"](db, DAY, [(114, 1, DAY, "delivered", 2397.0)]), 1)
            self.assertEqual(n["load"](db, DAY, [(114, 1, DAY, "delivered", 17.5)]), 1)
            self.assertEqual(db.execute(
                "SELECT order_id, amount FROM fact_orders").fetchall(), [(114, 17.5)])

    def test_duplicate_mid_batch_rolls_back_delete_and_first_insert(self):
        n = source_functions()
        with new_db() as db:
            n["load"](db, DAY, [(114, 1, DAY, "delivered", 2397.0)])
            with self.assertRaises(sqlite3.IntegrityError):
                n["load"](db, DAY, [(114, 1, DAY, "delivered", 20.0),
                                    (114, 1, DAY, "delivered", 30.0)])
            self.assertEqual(db.execute(
                "SELECT order_id, amount FROM fact_orders").fetchall(), [(114, 2397.0)])

    def test_parse_failure_mid_batch_rolls_back_prior_day(self):
        n = source_functions()
        with new_db() as db:
            n["load"](db, DAY, [(114, 1, DAY, "delivered", 2397.0)])
            good = {"order_id": "114", "customer_id": "1",
                    "order_date": DAY, "status": "delivered", "amount": "5"}
            bad = dict(good, order_id="115", amount="bad_amount")
            with self.assertRaises(ValueError):
                n["load"](db, DAY, n["transform"]([good, bad]))
            self.assertEqual(db.execute(
                "SELECT order_id, amount FROM fact_orders").fetchall(), [(114, 2397.0)])

    def test_cross_day_order_id_conflict_is_unresolved_contract(self):
        n = source_functions()
        with new_db() as db:
            n["load"](db, DAY, [(114, 1, DAY, "delivered", 2397.0)])
            with self.assertRaises(sqlite3.IntegrityError):
                n["load"](db, "2025-04-28",
                          [(114, 1, "2025-04-28", "delivered", 30.0)])
            self.assertEqual(db.execute(
                "SELECT order_date, amount FROM fact_orders").fetchall(),
                [(DAY, 2397.0)])

    def test_p72_does_not_call_p73_quality_validation(self):
        n = source_functions()
        bad = {"order_id": "404", "customer_id": "1", "order_date": DAY,
               "status": "shipped", "amount": "-5"}
        self.assertEqual(list(n["transform"]([bad])),
                         [(404, 1, DAY, "shipped", -5.0)])
        ns = {"__name__": "auditor_p73_transform"}
        exec(compile(code_fence("p73"), "<p73 status+amount>", "exec"), ns)
        with self.assertRaisesRegex(ValueError, "amount must be"):
            ns["to_amount"]("-5")
        self.assertEqual(ns["normalize_status"]("shipped"), "unknown")
        with new_db() as db:
            n["load"](db, DAY, n["transform"]([bad]))
            self.assertEqual(db.execute(
                "SELECT status, amount FROM fact_orders").fetchone(), ("shipped", -5.0))

    def test_missing_day_returns_zero_and_existing_other_day_survives(self):
        n = source_functions()
        with new_db() as db:
            n["load"](db, DAY, [(114, 1, DAY, "delivered", 2397.0)])
            self.assertEqual(n["load"](db, "2030-01-01", []), 0)
            self.assertEqual(db.execute(
                "SELECT order_date FROM fact_orders").fetchall(), [(DAY,)])

    def test_p72_argparse_caught_demo_is_not_scheduler_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "args.py"
            path.write_text(code_fence("p72", 1), encoding="utf-8")
            output = subprocess.run([sys.executable, str(path)], text=True,
                                    capture_output=True, timeout=10)
            self.assertEqual(output.returncode, 0)
            self.assertEqual(output.stdout.strip(), "bad arguments, exit code 2")
            self.assertIn("required", output.stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
