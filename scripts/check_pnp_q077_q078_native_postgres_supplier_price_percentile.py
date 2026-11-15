#!/usr/bin/env python3
"""Independent, read-only PostgreSQL 16 replay of original supplied PNP Q077/Q078 SQL.

Source-pinned original question/key identity; bounded reviewer fixtures only.
A passing conditional discrepancy test is not official grading, original CSV
validation, a verified learner attempt, or complete source-PDF parity.
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
FILES = {
    77: ("2. Joins/P077. Single-source products and the value at risk.md",
         "22d728c1686886684dcea80381b71303aed52056"),
    78: ("9. Windowing Functions/P078. Expensive within their sub-category but selling below its median.md",
         "c8baea659a6c96edd55d0eed03b805907d05a681"),
}
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def original_queries():
    assert blob(KEY) == KEY_SHA, "archived supplier-key bytes changed"
    text = KEY.read_text(encoding="utf-8")
    queries = {}
    for n, (rel, expected_sha) in FILES.items():
        src = BASE / rel
        assert blob(src) == expected_sha, f"Q{n} original question bytes changed"
        question = src.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output",
                       "## My solution — SQLite\n\nPending.",
                       "## My solution — SQL Server\n\nPending.",
                       "## Official solution\n\nPending"):
            assert marker in question, (n, marker)
        match = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",
                          text)
        assert match, f"missing original supplied Q{n} SQL"
        sql = match.group(1).strip()
        assert sql.startswith("WITH ") and sql.endswith(";"), n
        queries[n] = sql
    assert "COUNT(DISTINCT od.SupplierID)" in queries[77]
    assert "ws.lines_without_supplier = 0" in queries[77]
    assert "PERCENTILE_CONT(0.5)" in queries[78]
    assert "s.subcat_products >= 20" in queries[78]
    return queries


SQL = original_queries()


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True)


def native(n, products=(), details=(), suppliers=()):
    """Use only transaction-local temporary tables; run supplier SQL unchanged."""
    with connect() as conn:
        with conn.transaction():
            if n == 77:
                conn.execute("CREATE TEMP TABLE Products("
                             "ProductID INT, Product TEXT, Sale_Price NUMERIC) ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE Suppliers("
                             "SupplierID INT, CompanyName TEXT, Country TEXT) ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE OrderDetails("
                             "OrderDetailID INT, ProductID INT, Quantity INT, SupplierID INT)"
                             " ON COMMIT DROP")
            else:
                conn.execute("CREATE TEMP TABLE Products("
                             "ProductID INT, Product TEXT, Sub_Category TEXT,"
                             " Sale_Price NUMERIC) ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE OrderDetails("
                             "ProductID INT, Quantity INT) ON COMMIT DROP")
            with conn.cursor() as cur:
                if products:
                    cur.executemany("INSERT INTO Products VALUES (" +
                                    ",".join(["%s"] * len(products[0])) + ")", products)
                if details:
                    cur.executemany("INSERT INTO OrderDetails VALUES (" +
                                    ",".join(["%s"] * len(details[0])) + ")", details)
                if n == 77 and suppliers:
                    cur.executemany("INSERT INTO Suppliers VALUES (%s,%s,%s)", suppliers)
            result = conn.execute(SQL[n]).fetchall()
    return result


def q78_products(count=20, tie_top=False, null_price=False, null_subcat=False,
                 all_tied=False):
    rows = []
    for i in range(1, count + 1):
        price = 10 if all_tied else (20 if tie_top and i == 19 else i)
        if null_price and i == 20:
            price = None
        rows.append((i, "Premium shampoo" if i == 20 else "Other",
                     None if null_subcat else "Hair care", price))
    return rows


class OriginalQ077Q078NativeForensics(unittest.TestCase):
    def test_01_git_blob_pins_source_and_historical_pending_state(self):
        self.assertEqual(blob(KEY), KEY_SHA)
        for rel, sha in FILES.values():
            self.assertEqual(blob(BASE / rel), sha)

    def test_02_actual_native_postgresql_major_16(self):
        with connect() as conn:
            major = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= major < 170000, major)

    def test_03_q077_archived_four_line_illustration(self):
        got = native(77,
            products=[(101, "Keyboard", 10), (102, "Mouse", 10), (103, "Cable", 10)],
            suppliers=[(7, "Alpha", "India"), (8, "Beta", "India"),
                       (9, "Gamma", "Nepal")],
            details=[(1, 101, 2, 7), (2, 102, 3, 8),
                     (3, 102, 1, 9), (4, 103, 1, None)])
        self.assertEqual(got, [(101, "Keyboard", "Alpha", "India",
                                Decimal(20), Decimal("28.57"))])

    def test_04_q077_same_supplier_across_multiple_lines_is_single_source(self):
        got = native(77,
            products=[(1, "A", 5), (2, "B", 10)],
            suppliers=[(7, "Alpha", "India")],
            details=[(1, 1, 4, 7), (2, 1, 2, 7), (3, 2, 1, 7)])
        self.assertEqual(got, [
            (1, "A", "Alpha", "India", Decimal(30), Decimal("75.00")),
            (2, "B", "Alpha", "India", Decimal(10), Decimal("25.00"))])

    def test_05_q077_null_supplier_line_invalidates_otherwise_single_source_product(self):
        got = native(77,
            products=[(1, "A", 10), (2, "B", 10)],
            suppliers=[(7, "Alpha", "India")],
            details=[(1, 1, 2, 7), (2, 1, 1, None), (3, 2, 1, 7)])
        # Ineligible product A still belongs in the denominator.
        self.assertEqual(got, [
            (2, "B", "Alpha", "India", Decimal(10), Decimal("25.00"))])

    def test_06_q077_orphan_product_and_supplier_fallbacks_are_visible(self):
        got = native(77,
            products=[(1, "Listed", 5)],
            suppliers=[(7, "Alpha", "India")],
            details=[(1, 1, 2, 8), (2, 999, 1, 7)])
        self.assertEqual(got, [
            (1, "Listed", "Unknown supplier", "Unknown", Decimal(10), Decimal("100.00")),
            (999, "Unknown product", "Alpha", "India", None, None)])
        # Unknown catalogue price means the denominator excludes the orphan line's value.

    def test_07_q077_zero_catalogue_value_has_undefined_percentage(self):
        got = native(77,
            products=[(1, "Zero", 0)],
            suppliers=[(7, "Alpha", "India")],
            details=[(1, 1, 4, 7)])
        self.assertEqual(got, [
            (1, "Zero", "Alpha", "India", Decimal(0), None)])

    def test_08_q077_no_order_lines(self):
        self.assertEqual(native(77, products=[(1, "Never sold", 40)]), [])

    def test_09_q078_archived_twenty_product_illustration(self):
        got = native(78,
            products=q78_products(),
            details=[(i, 10) for i in range(1, 20)])
        self.assertEqual(got, [
            ("Hair care", 20, "Premium shampoo", Decimal(20),
             Decimal("1.00"), 0, 10.0)])

    def test_10_q078_tied_highest_price_both_receive_rank_below_one(self):
        got = native(78,
            products=q78_products(tie_top=True),
            details=[(i, 10) for i in range(1, 19)])
        self.assertEqual(got, [
            ("Hair care", 19, "Other", Decimal(20), Decimal("0.95"), 0, 10.0),
            ("Hair care", 20, "Premium shampoo", Decimal(20), Decimal("0.95"), 0, 10.0)])

    def test_11_q078_nineteen_products_fail_minimum_size(self):
        self.assertEqual(native(78,
            products=q78_products(count=19),
            details=[(i, 10) for i in range(1, 19)]), [])

    def test_12_q078_one_null_price_shrinks_twenty_listed_to_nineteen_scored(self):
        self.assertEqual(native(78,
            products=q78_products(null_price=True),
            details=[(i, 10) for i in range(1, 19)]), [])
        # Conditional contract ambiguity: "at least 20 products" counts all
        # listings in the task, but supplier SQL counts only non-NULL price rows.

    def test_13_q078_uniform_price_gives_percent_rank_zero_to_every_product(self):
        self.assertEqual(native(78,
            products=q78_products(all_tied=True),
            details=[(i, 10) for i in range(1, 20)]), [])

    def test_14_q078_zero_sales_median_is_zero_so_no_below_median_candidates(self):
        self.assertEqual(native(78, products=q78_products()), [])

    def test_15_q078_null_subcategory_product_group_omitted(self):
        self.assertEqual(native(78,
            products=q78_products(null_subcat=True),
            details=[(i, 10) for i in range(1, 20)]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
