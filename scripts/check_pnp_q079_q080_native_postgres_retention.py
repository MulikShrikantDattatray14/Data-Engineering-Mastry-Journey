#!/usr/bin/env python3
"""Source-pinned native PostgreSQL 16 replay: PNP Q079 and Q080.

Execute *unchanged* archived supplier PostgreSQL queries in disposable temporary
tables. Original illustrative examples and independent boundary fixtures only.
Passing a discrepancy-reproduction test is NOT official grading, a compliant
supplier answer, complete Commerce v2 data parity or learner completion.
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
FILES = {
    79: ("9. Windowing Functions/P079. At which order does a customer cross 10,000 in spend.md",
         "8446d5ea1b09182909e452ce05b4c62141f6bdb4"),
    80: ("6. SubQueries/P080. Sub-category repurchase rate within 90 days.md",
         "49c42503bdf27ed5369854f47011360329e6ab45"),
}
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def load_original_sql():
    assert git_blob(KEY) == KEY_BLOB, "the supplier key changed"
    source = KEY.read_text(encoding="utf-8")
    statements = {}
    for q, (relpath, sha) in FILES.items():
        path = BASE / relpath
        assert git_blob(path) == sha, f"original Q{q} source changed"
        question = path.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{q:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## My solution — SQLite\n\nPending.",
                       "## My solution — SQL Server\n\nPending.",
                       "## Official solution\n\nPending"):
            assert marker in question, f"Q{q} historical marker missing: {marker}"
        match = re.search(rf"(?ms)^-- Q{q}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
        assert match, f"no Q{q} supplier SQL"
        query = match.group(1).strip()
        assert query.startswith("WITH ") and query.endswith(";")
        statements[q] = query
    assert "SELECT DISTINCT ON (r.CustomerID)" in statements[79]
    assert "WHERE r.running_spend >= 10000" in statements[79]
    assert "later.Sub_Category   = e.Sub_Category" in statements[80]
    assert "HAVING COUNT(*) >= 30" in statements[80]
    return statements


SQL = load_original_sql()


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True,
    )


def native(q, orders, products=(), details=()):
    """Run unchanged query; temporary schema/data discarded on commit."""
    with connect() as conn:
        with conn.transaction():
            conn.execute(
                "CREATE TEMP TABLE Orders("
                "OrderID INT, CustomerID INT, OrderDate DATE,"
                "Total_Order_Amount NUMERIC) ON COMMIT DROP")
            if q == 80:
                conn.execute(
                    "CREATE TEMP TABLE Products("
                    "ProductID INT, Sub_Category TEXT) ON COMMIT DROP")
                conn.execute(
                    "CREATE TEMP TABLE OrderDetails("
                    "OrderID INT, ProductID INT) ON COMMIT DROP")
            with conn.cursor() as cur:
                if orders:
                    cur.executemany(
                        "INSERT INTO Orders VALUES (%s,%s,%s,%s)", orders)
                if q == 80 and products:
                    cur.executemany("INSERT INTO Products VALUES (%s,%s)", products)
                if q == 80 and details:
                    cur.executemany("INSERT INTO OrderDetails VALUES (%s,%s)", details)
            rows = conn.execute(SQL[q]).fetchall()
    return rows


def tea_fixture(first="2026-01-01", anchor="2026-04-15", category="Tea"):
    orders = [(i, i, first, None) for i in range(1, 31)]
    details = [(i, 101) for i in range(1, 31)]
    orders.append((500, 99, anchor, None))
    details.append((500, 102))
    products = [(101, category), (102, "Other")]
    return orders, products, details


class OriginalQ079Q080NativeForensics(unittest.TestCase):
    def test_01_source_git_blobs_exact_and_historical_solution_sections_pending(self):
        self.assertEqual(git_blob(KEY), KEY_BLOB)
        for _, (rel, sha) in FILES.items():
            self.assertEqual(git_blob(BASE / rel), sha)

    def test_02_native_postgresql_major_16(self):
        with connect() as conn:
            version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= version < 170000, version)

    def test_03_q079_original_four_order_example(self):
        orders = [(1, 10, "2026-01-01", 4000),
                  (2, 10, "2026-01-05", 3000),
                  (3, 10, "2026-01-10", 3000),
                  (4, 20, "2026-01-10", 2000)]
        self.assertEqual(native(79, orders),
                         [(10, 3, date(2026, 1, 10), 9, Decimal(10000))])

    def test_04_q079_same_day_tie_deterministic_by_order_id(self):
        orders = [(90, 7, "2026-02-02", 6000),
                  (20, 7, "2026-02-02", 3000),
                  (50, 7, "2026-02-02", 8000)]
        # The sorted order is ID20 (3000), ID50 (8000), ID90 (6000).
        self.assertEqual(native(79, orders),
                         [(7, 2, date(2026, 2, 2), 0, Decimal(11000))])

    def test_05_q079_first_crossing_kept_after_later_refund_drop(self):
        orders = [(1, 3, "2026-01-01", 10000),
                  (2, 3, "2026-01-03", -8000),
                  (3, 3, "2026-01-05", 9000)]
        self.assertEqual(native(79, orders),
                         [(3, 1, date(2026, 1, 1), 0, Decimal(10000))])
        # This confirms first-crossing semantics; it does not authenticate a refund policy.

    def test_06_q079_null_amount_counts_order_and_contributes_zero(self):
        orders = [(1, 42, "2026-03-01", 5000),
                  (2, 42, "2026-03-02", None),
                  (3, 42, "2026-03-04", 5000)]
        self.assertEqual(native(79, orders),
                         [(42, 3, date(2026, 3, 4), 3, Decimal(10000))])

    def test_07_q079_invalid_identity_date_exclusions_and_non_crossers(self):
        orders = [(1, None, "2026-01-01", 20000),
                  (2, 1, None, 20000),
                  (3, 2, "2026-01-01", 9999)]
        self.assertEqual(native(79, orders), [])

    def test_08_q080_original_thirty_buyers_six_repeaters(self):
        orders, products, details = tea_fixture()
        orders += [(100 + i, i, "2026-01-20", None) for i in range(1, 7)]
        details += [(100 + i, 101) for i in range(1, 7)]
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 6, Decimal("20.00"))])

    def test_09_q080_same_day_new_order_not_repurchase_even_with_join_duplicates(self):
        orders, products, details = tea_fixture()
        orders += [(100 + i, i, "2026-01-01", None) for i in range(1, 7)]
        details += [(100 + i, 101) for i in range(1, 7)]
        details += [(i, 101) for i in range(1, 7)]  # duplicate SKU lines
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 0, Decimal("0.00"))])

    def test_10_q080_90_day_boundary_inclusive_but_day_91_excluded(self):
        orders, products, details = tea_fixture()
        # Jan 1 + 90 days = April 1 in non-leap 2026.
        orders += [(101, 1, "2026-04-01", None),
                   (102, 2, "2026-04-02", None)]
        details += [(101, 101), (102, 101)]
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 1, Decimal("3.33"))])

    def test_11_q080_first_buy_on_exact_eligibility_cutoff_included(self):
        orders, products, details = tea_fixture(first="2026-01-15")
        orders.append((201, 31, "2026-01-16", None))
        details.append((201, 101))
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 0, Decimal("0.00"))])

    def test_12_q080_different_category_is_not_same_category_repurchase(self):
        orders, products, details = tea_fixture()
        orders += [(100 + i, i, "2026-01-20", None) for i in range(1, 7)]
        details += [(100 + i, 102) for i in range(1, 7)]
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 0, Decimal("0.00"))])

    def test_13_q080_null_subcategory_all_real_repeaters_missed_by_join(self):
        orders, products, details = tea_fixture(category=None)
        orders += [(100 + i, i, "2026-01-20", None) for i in range(1, 31)]
        details += [(100 + i, 101) for i in range(1, 31)]
        # The source's NULL equality is UNKNOWN, so it counts zero,
        # despite all 30 people purchasing again. Conditional data policy.
        self.assertEqual(native(80, orders, products, details),
                         [(None, 30, 0, Decimal("0.00"))])

    def test_14_q080_null_customer_counted_as_eligible_buyer(self):
        orders, products, details = tea_fixture()
        # Replace exactly one of the 30 distinct identified customer IDs.
        orders[0] = (1, None, "2026-01-01", None)
        # SQL groups NULL into a buyer row, although no customer identity exists.
        self.assertEqual(native(80, orders, products, details),
                         [("Tea", 30, 0, Decimal("0.00"))])
        # Not proof that original Commerce v2 permits NULL CustomerID.

    def test_15_q080_no_eligible_first_buyers_and_empty_input(self):
        self.assertEqual(native(80, [], [], []), [])
        orders, products, details = tea_fixture(first="2026-05-01",
                                                anchor="2026-05-15")
        self.assertEqual(native(80, orders, products, details), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
