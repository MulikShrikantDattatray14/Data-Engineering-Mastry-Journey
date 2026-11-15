#!/usr/bin/env python3
"""Original, unchanged supplier SQL for PNP Q076: native PostgreSQL 16 forensic replay.

Read-only Git-blob-pinned source verification; ephemeral PostgreSQL 16 tables.
The expected source output has a 12-month calendar spine, while the bundled key
groups only months with orders. This verifier deliberately reproduces that gap.
Other probes are auditor-created synthetic contracts, NOT authenticated provider
answers, learner work, Commerce v2 full-dataset validation, or mastery.
"""
import hashlib
import os
import re
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("12. Dates and Time/"
                   "P076. Order value from new vs returning customers by month.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_BLOB = "5c991b66eb5a87e858a021b0c94f0e93c173f190"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def original_sql():
    assert git_blob(QUESTION) == QUESTION_BLOB, "Q076 original question changed"
    assert git_blob(KEY) == KEY_BLOB, "original supplied SQL key changed"
    question = QUESTION.read_text(encoding="utf-8")
    for marker in (
        "# PNP Q076.", "NOT SOLVED YET",
        "For each of the last 12 calendar months",
        "2025-02-01", "2026-01-01",
        "### Sample input and expected output", "## Schema",
        "## My solution — SQLite\n\nPending.",
        "## My solution — SQL Server\n\nPending.",
        "## Official solution\n\nPending",
    ):
        assert marker in question, f"original Q076 marker missing: {marker!r}"
    key = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q76\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, "original Q76 supplier query missing"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS (") and sql.endswith(";")
    assert "GROUP BY t.order_month" in sql
    assert "FROM monthly AS m" in sql
    assert "MIN(o.OrderDate) OVER (PARTITION BY o.CustomerID)" in sql
    assert "generate_series" not in sql.lower()
    return sql


SQL = original_sql()
EXAMPLE = [
    (1, 10, "2025-01-01", 100),
    (2, 10, "2025-12-01", 50),
    (3, 20, "2025-12-05", 100),
    (4, 10, "2026-01-05", 75),
    (5, 20, "2026-01-07", 25),
    (6, 30, "2026-01-10", 50),
]


def run_native(orders):
    """Execute the original key unchanged; table and rows disappear at commit."""
    with psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True,
    ) as conn:
        with conn.transaction():
            conn.execute(
                "CREATE TEMP TABLE Orders("
                "OrderID INTEGER, CustomerID INTEGER, OrderDate DATE,"
                "Total_Order_Amount NUMERIC) ON COMMIT DROP"
            )
            if orders:
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO Orders VALUES (%s,%s,%s,%s)", orders
                    )
            rows = conn.execute(SQL).fetchall()
    return rows


class OriginalQ076NativeCalendarForensics(unittest.TestCase):
    def test_01_immutable_archives_and_pending_history(self):
        self.assertEqual(git_blob(QUESTION), QUESTION_BLOB)
        self.assertEqual(git_blob(KEY), KEY_BLOB)
        self.assertIn("GROUP BY t.order_month", SQL)

    def test_02_uses_native_postgres_major_16(self):
        with psycopg.connect(
            host=os.getenv("PGHOST", "127.0.0.1"),
            port=os.getenv("PGPORT", "5432"),
            dbname=os.getenv("PGDATABASE", "audit"),
            user=os.getenv("PGUSER", "audit"),
            password=os.getenv("PGPASSWORD", "audit"),
        ) as conn:
            n = int(conn.execute("SHOW server_version_num").fetchone()[0])
            self.assertTrue(160000 <= n < 170000, n)

    def test_03_original_example_matches_only_two_populated_source_rows(self):
        self.assertEqual(run_native(EXAMPLE), [
            (date(2025, 12, 1), 1, 1, Decimal(100), Decimal(50), Decimal("33.33")),
            (date(2026, 1, 1), 1, 2, Decimal(50), Decimal(100), Decimal("66.67")),
        ])

    def test_04_source_requires_12_rows_but_native_key_omits_10_empty_months(self):
        rows = run_native(EXAMPLE)
        expected = [date(2025, month, 1) for month in range(2, 13)]
        expected.append(date(2026, 1, 1))
        observed = {r[0] for r in rows}
        missing = [month for month in expected if month not in observed]
        self.assertEqual(missing, [date(2025, m, 1) for m in range(2, 12)])
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(expected), 12)
        # Passing this test confirms a source/key discrepancy, NOT full Q076 success.

    def test_05_full_history_outside_reporting_window_sets_returning_class(self):
        rows = run_native([
            (1, 10, "2024-01-01", 900),
            (2, 10, "2026-06-01", 50),
            (3, 20, "2026-06-05", 20),
        ])
        self.assertEqual(rows, [
            (date(2026, 6, 1), 1, 1, Decimal(20), Decimal(50), Decimal("71.43"))
        ])

    def test_06_multiple_orders_first_month_all_new_then_returning(self):
        rows = run_native([
            (1, 10, "2026-01-01", 5),
            (2, 10, "2026-01-31", 7),
            (3, 10, "2026-02-01", 8),
        ])
        self.assertEqual(rows, [
            (date(2026, 1, 1), 2, 0, Decimal(12), Decimal(0), Decimal(0)),
            (date(2026, 2, 1), 0, 1, Decimal(0), Decimal(8), Decimal(100)),
        ])

    def test_07_leap_day_first_order_and_next_year_return(self):
        rows = run_native([
            (1, 70, "2024-02-29", 15),
            (2, 70, "2025-02-01", 10),
            (3, 71, "2025-02-28", 25),
        ])
        self.assertEqual(rows, [
            (date(2025, 2, 1), 1, 1, Decimal(25), Decimal(10), Decimal("28.57"))
        ])

    def test_08_null_and_zero_order_values_count_orders_but_no_percentage(self):
        rows = run_native([
            (1, 10, "2026-01-01", None),
            (2, 10, "2026-01-31", 0),
        ])
        self.assertEqual(rows, [
            (date(2026, 1, 1), 2, 0, Decimal(0), Decimal(0), None)
        ])

    def test_09_opposing_signed_amounts_zero_denominator_yields_null(self):
        rows = run_native([
            (1, 10, "2025-12-01", 20),
            (2, 10, "2026-01-05", -100),
            (3, 20, "2026-01-06", 100),
        ])
        self.assertEqual(rows[-1], (
            date(2026, 1, 1), 1, 1, Decimal(100), Decimal(-100), None
        ))

    def test_10_invalid_null_customer_latest_order_shifts_anchor(self):
        # The anchor reads ALL dates, but tagged excludes NULL CustomerID.
        rows = run_native([
            (1, 10, "2026-03-01", 50),
            (2, None, "2027-03-01", 999),
        ])
        self.assertEqual(rows, [])
        self.assertEqual(run_native([(1, 10, "2026-03-01", 50)]), [
            (date(2026, 3, 1), 1, 0, Decimal(50), Decimal(0), Decimal(0))
        ])
        # Conditional data-quality concern; not proof actual Commerce v2 has NULL customers.

    def test_11_missing_order_date_excluded_without_affecting_date_anchor(self):
        self.assertEqual(run_native([
            (1, 10, None, 900),
            (2, 10, "2026-01-01", 30),
        ]), [
            (date(2026, 1, 1), 1, 0, Decimal(30), Decimal(0), Decimal(0))
        ])

    def test_12_fully_populated_12_months_are_returned_by_original_key(self):
        data = [(i, i, f"2025-{i + 1:02d}-01", 1)
                for i in range(1, 12)]
        data.append((12, 12, "2026-01-01", 1))
        rows = run_native(data)
        self.assertEqual(len(rows), 12)
        self.assertEqual([r[0] for r in rows],
                         [date(2025, i, 1) for i in range(2, 13)] +
                         [date(2026, 1, 1)])
        self.assertTrue(all(r[1:] == (
            1, 0, Decimal(1), Decimal(0), Decimal(0)
        ) for r in rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
