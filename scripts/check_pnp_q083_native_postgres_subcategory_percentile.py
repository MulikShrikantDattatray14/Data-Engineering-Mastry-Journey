#!/usr/bin/env python3
"""Immutable-source PNP Q083 native PostgreSQL 16 reviewer, not official grading.

Runs the original supplier SQL without translation on disposable temp tables.
Synthetic tests never establish original Commerce CSV parity or learner mastery.
"""
import hashlib
import os
import re
import unittest
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("15. Analytics and Performance/"
                   "P083. Underperforming sub-categories in the last six months.md")
QUESTION_BLOB = "b1339a417e6f47b85792b43d45f32edf32f281ad"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extract_source():
    assert git_blob(QUESTION) == QUESTION_BLOB, "original Q083 source changed"
    assert git_blob(KEY) == KEY_BLOB, "original supplied SQL changed"
    statement = QUESTION.read_text(encoding="utf-8")
    for marker in ("# PNP Q083.", "NOT SOLVED YET", "## Schema",
                   "### Sample input and expected output",
                   "## My solution — SQLite\n\nPending.",
                   "## My solution — SQL Server\n\nPending.",
                   "## Official solution\n\nPending"):
        assert marker in statement, marker
    key = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q83\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, "Q083 supplier key not found"
    sql = match.group(1).strip()
    assert sql.startswith("WITH bounds AS (") and sql.endswith(";")
    for marker in ("PERCENTILE_CONT(0.25)", "GROUP BY cat.CategoryName, p.Sub_Category",
                   "GROUP BY s.CategoryName", "o.OrderDate >  b.window_start",
                   "WHERE s.units_per_product < t.category_p25"):
        assert marker in sql, marker
    return sql


SQL = extract_source()


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True)


def run(categories=(), products=(), orders=(), details=()):
    """Execute unchanged supplier key on fresh transaction-local tables."""
    with connect() as conn:
        with conn.transaction():
            conn.execute("CREATE TEMP TABLE Category(CategoryID int, CategoryName text, Active text) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE Products(ProductID int, CategoryID int, Sub_Category text) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE Orders(OrderID int, OrderDate date) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE OrderDetails(OrderDetailID int, OrderID int, ProductID int, Quantity int) ON COMMIT DROP")
            for name, rows in (("Category", categories), ("Products", products),
                               ("Orders", orders), ("OrderDetails", details)):
                if rows:
                    with conn.cursor() as cur:
                        cur.executemany(
                            "INSERT INTO " + name + " VALUES (" +
                            ",".join(["%s"] * len(rows[0])) + ")", rows)
            return conn.execute(SQL).fetchall()


def four_products(category=1, first_name="A"):
    return [(101, category, first_name), (102, category, "B"),
            (103, category, "C"), (104, category, "D")]


def three_sales(order_date="2026-06-30"):
    return ([(1, order_date)], [(1, 1, 102, 10),
                                (2, 1, 103, 20), (3, 1, 104, 30)])


SAMPLE = [("Care", "A", 1, 0, Decimal("0.00"), Decimal("7.50"))]


class OriginalQ083NativePostgres(unittest.TestCase):
    def test_01_pinned_sources_and_untouched_pending_attempts(self):
        self.assertEqual(git_blob(QUESTION), QUESTION_BLOB)
        self.assertEqual(git_blob(KEY), KEY_BLOB)
        self.assertIn("## Official solution\n\nPending", QUESTION.read_text(encoding="utf-8"))

    def test_02_postgresql_major_16(self):
        with connect() as conn:
            major = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= major < 170000, major)

    def test_03_exact_original_four_subcategory_p25_illustration(self):
        orders, details = three_sales()
        self.assertEqual(run([(1, "Care", "Y")], four_products(), orders, details), SAMPLE)

    def test_04_six_month_start_exclusive_and_last_day_inclusive(self):
        orders = [(1, "2025-12-30"), (2, "2025-12-31"),
                  (3, "2026-06-30"), (4, "2026-06-30")]
        details = [(1, 1, 101, 999), (2, 2, 102, 10),
                   (3, 3, 103, 20), (4, 4, 104, 30)]
        self.assertEqual(run([(1, "Care", "Y")], four_products(), orders, details), SAMPLE)

    def test_05_inactive_category_ignored_even_with_large_quantity(self):
        orders, details = three_sales()
        categories = [(1, "Care", "yes"), (2, "Dormant", "N")]
        products = four_products() + [(999, 2, "Gone")]
        details.append((4, 1, 999, 9999))
        self.assertEqual(run(categories, products, orders, details), SAMPLE)

    def test_06_duplicate_order_lines_sum_before_subcategory_grouping(self):
        orders = [(1, "2026-06-30")]
        details = [(1, 1, 102, 4), (2, 1, 102, 6),
                   (3, 1, 103, 20), (4, 1, 104, 30)]
        self.assertEqual(run([(1, "Care", "Y")], four_products(), orders, details), SAMPLE)

    def test_07_no_orders_yields_no_below_zero_percentile(self):
        self.assertEqual(run([(1, "Care", "Y")], four_products()), [])

    def test_08_same_name_distinct_category_id_collapses_groups(self):
        categories = [(1, "Care", "Y"), (2, "Care", "Y")]
        products = four_products() + [(201, 2, "A")]
        orders = [(1, "2026-06-30")]
        details = [(1, 1, 102, 10), (2, 1, 103, 20),
                   (3, 1, 104, 30), (4, 1, 201, 100)]
        result = run(categories, products, orders, details)
        self.assertEqual(result, [
            ("Care", "B", 1, 10, Decimal("10.00"), Decimal("17.50"))])
        # The nominal per-CategoryID task would include category 1's A row.
        self.assertNotEqual(result, SAMPLE)

    def test_09_null_category_name_drops_active_category_in_threshold_join(self):
        orders, details = three_sales()
        self.assertEqual(run([(1, None, "Y")], four_products(), orders, details), [])
        # SQL NULL = NULL is UNKNOWN; no statement-licensed exclusion established.

    def test_10_null_subcategory_can_be_a_returned_underperformer(self):
        orders, details = three_sales()
        products = four_products(first_name=None)
        self.assertEqual(run([(1, "Care", "Y")], products, orders, details),
                         [("Care", None, 1, 0, Decimal("0.00"), Decimal("7.50"))])

    def test_11_null_quantities_coalesce_to_zero_units(self):
        orders, details = three_sales()
        details.append((4, 1, 101, None))
        self.assertEqual(run([(1, "Care", "TRUE")], four_products(), orders, details), SAMPLE)

    def test_12_catalogue_count_not_distinct_selling_products(self):
        orders, details = three_sales()
        products = four_products() + [(105, 1, "A")]
        result = run([(1, "Care", "Y")], products, orders, details)
        self.assertEqual(result, [
            ("Care", "A", 2, 0, Decimal("0.00"), Decimal("7.50"))])


if __name__ == "__main__":
    unittest.main(verbosity=2)
