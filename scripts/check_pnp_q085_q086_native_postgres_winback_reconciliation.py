#!/usr/bin/env python3
"""PNP Q085/Q086 immutable-source native PostgreSQL reviewer (NOT provider grading).

Runs the original supplied SQL unchanged on disposable synthetic tables.
Original PDF rendered parity, actual Commerce CSV results and learner mastery
are NOT established by these tests.
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
Q85 = BASE / "12. Dates and Time/P085. Win-back customers returning after 180+ days.md"
Q86 = BASE / "14. Data Quality and Deduplication/P086. Reconcile order headers with order lines.md"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
PINS = {
    Q85: "36e53c1398e4c533961c84b661fe501615a34033",
    Q86: "6ef60c84817d83962ef24d77f301b9ad8b962f93",
    KEY: "7912c8e676621c513e0b635a40c6ee299404676e",
}
SOURCE_STATUS_ORDER = [
    "Lines with NULL OrderID", "Lines without header", "Header without lines",
    "Header zero or NULL", "Exact match", "Discount 5%", "Discount 10%",
    "Discount 12%", "Discount 15%", "Other shortfall", "Header above lines",
]
SUPPLIER_STATUS_ORDER = [
    "Exact match", "Discount 5%", "Discount 10%", "Discount 12%",
    "Discount 15%", "Other shortfall", "Header above lines",
    "Header zero or NULL", "Header without lines", "Lines without header",
    "Lines with NULL OrderID",
]


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def get_sql(q):
    for path, sha in PINS.items():
        assert git_blob(path) == sha, "immutable original changed: " + str(path)
    for source in (Q85, Q86):
        statement = source.read_text(encoding="utf-8")
        for marker in ("NOT SOLVED YET", "## Schema", "## My solution — SQLite\n\nPending.",
                       "## My solution — SQL Server\n\nPending.",
                       "## Official solution\n\nPending"):
            assert marker in statement, (source.name, marker)
    key = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q" + str(q) + r"\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, "missing supplied Q" + str(q)
    sql = match.group(1).strip()
    assert sql.endswith(";")
    if q == 85:
        for token in ("LAG(o.OrderDate)", "ORDER BY o.OrderDate, o.OrderID",
                      ">= 180", "b.last_day - INTERVAL '1 year'"):
            assert token in sql, token
    else:
        for token in ("FULL OUTER JOIN", "STRING_AGG(DISTINCT cl.PaymentType",
                      "WHEN ABS(h.Total_Order_Amount - lt.line_list_value)",
                      "COUNT(cl.order_key)", "VALUES (1, 'Exact match')"):
            assert token in sql, token
    return sql


SQL85 = get_sql(85)
SQL86 = get_sql(86)


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True,
    )


def populate(conn, name, rows):
    if rows:
        with conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO " + name + " VALUES (" +
                ", ".join(["%s"] * len(rows[0])) + ")", rows)


def run85(orders=()):
    with connect() as conn:
        with conn.transaction():
            conn.execute("CREATE TEMP TABLE Orders (OrderID int, CustomerID int, "
                         "OrderDate date, Total_Order_Amount numeric(14,2)) ON COMMIT DROP")
            populate(conn, "Orders", orders)
            return conn.execute(SQL85).fetchall()


def run86(headers=(), lines=(), products=(), payments=()):
    with connect() as conn:
        with conn.transaction():
            conn.execute("CREATE TEMP TABLE Orders (OrderID int, PaymentID int, "
                         "Total_Order_Amount numeric(14,2)) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE OrderDetails (OrderDetailID int, OrderID int, "
                         "ProductID int, Quantity numeric) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE Products (ProductID int, Sale_Price numeric(14,2)) ON COMMIT DROP")
            conn.execute("CREATE TEMP TABLE Payments (PaymentID int, PaymentType text) ON COMMIT DROP")
            for name, rows in (("Orders", headers), ("OrderDetails", lines),
                               ("Products", products), ("Payments", payments)):
                populate(conn, name, rows)
            return conn.execute(SQL86).fetchall()


def grouped(result):
    return {r[0]: r for r in result}


class Q085OriginalWinBack(unittest.TestCase):
    def test_01_original_source_key_and_pending_learner_preserved(self):
        for path, expected in PINS.items():
            self.assertEqual(git_blob(path), expected)
        self.assertIn("customer 10 returned 181 days", Q85.read_text(encoding="utf-8"))

    def test_02_native_postgresql_16(self):
        with connect() as conn:
            major = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= major < 170000, major)

    def test_03_original_181_day_illustration(self):
        rows = [(1,10,"2025-01-01",100), (2,10,"2025-07-01",80),
                (3,20,"2025-06-01",50), (4,20,"2025-07-01",60)]
        self.assertEqual(run85(rows), [(10, __import__("datetime").date(2025,1,1),
                                       __import__("datetime").date(2025,7,1), 181, Decimal("80"))])

    def test_04_180_inclusive_179_excluded(self):
        rows = [(1,10,"2025-01-02",100), (2,10,"2025-07-01",80),
                (3,20,"2025-01-03",100), (4,20,"2025-07-01",80)]
        result = run85(rows)
        self.assertEqual([(r[0],r[3]) for r in result], [(10,180)])

    def test_05_previous_order_outside_reporting_window_still_used(self):
        rows = [(1,10,"2023-01-01",10), (2,10,"2025-06-30",20),
                (3,20,"2025-07-01",30)]
        self.assertEqual([(r[0],str(r[2])) for r in run85(rows)],
                         [(10,"2025-06-30")])

    def test_06_multiple_lapses_and_window_excludes_older_return(self):
        rows = [(1,10,"2024-01-01",10), (2,10,"2024-07-01",20),
                (3,10,"2025-01-01",30), (4,10,"2025-07-01",40)]
        self.assertEqual([(str(r[2]),r[3]) for r in run85(rows)],
                         [("2025-01-01",184), ("2025-07-01",181)])

    def test_07_same_day_orders_tie_broken_by_order_id(self):
        rows = [(1,10,"2024-01-01",10), (3,10,"2025-07-01",30),
                (2,10,"2025-07-01",20)]
        self.assertEqual([r[4] for r in run85(rows)], [Decimal("20")])

    def test_08_exact_twelve_month_cutoff_excludes_start_day(self):
        rows = [(1,10,"2024-01-01",10), (2,10,"2025-01-01",20),
                (3,20,"2024-01-01",10), (4,20,"2025-01-02",20),
                (5,30,"2026-01-01",30)]
        self.assertEqual([(r[0],str(r[2])) for r in run85(rows)],
                         [(20,"2025-01-02")])

    def test_09_null_customer_or_date_and_empty_input(self):
        self.assertEqual(run85(), [])
        self.assertEqual(run85([(1,None,"2024-01-01",10),
                                (2,None,"2025-07-01",10),
                                (3,10,None,10),
                                (4,10,"2025-07-01",10)]), [])


class Q086OriginalReconciliation(unittest.TestCase):
    def test_10_original_zero_rows_and_order_mismatch(self):
        result = run86()
        self.assertEqual([r[0] for r in result], SUPPLIER_STATUS_ORDER)
        self.assertNotEqual([r[0] for r in result], SOURCE_STATUS_ORDER)
        self.assertTrue(all(r[1:5] == (0,0,0,0) and r[5] is None for r in result))

    def test_11_source_sample_exact_match_but_row_position_differs(self):
        result = run86([(1,10,20)], [(1,1,101,2)],
                       [(101,10)], [(10,"Card")])
        self.assertEqual(grouped(result)["Exact match"],
                         ("Exact match",1,Decimal("20"),Decimal("20"),Decimal("0"),"Card"))
        self.assertEqual(result[0][0], "Exact match")
        self.assertNotEqual(result[0][0], SOURCE_STATUS_ORDER[0])

    def test_12_all_four_supplier_discount_buckets(self):
        headers = [(1,10,95),(2,10,90),(3,10,88),(4,10,85)]
        lines = [(i,i,101,1) for i in range(1,5)]
        results = grouped(run86(headers,lines,[(101,100)],[(10,"Card")]))
        for status in ("Discount 5%","Discount 10%","Discount 12%","Discount 15%"):
            self.assertEqual(results[status][1],1,status)

    def test_13_one_cent_inequality_is_labelled_exact(self):
        result = grouped(run86([(1,10,"19.99")],[(1,1,101,1)],[(101,20)],[(10,"Card")]))
        self.assertEqual(result["Exact match"][1],1)
        self.assertEqual(result["Exact match"][4],Decimal("0.01"))
        # Source says 'equals ... to the cent': 19.99 != 20.00; supplied <=0.01 tolerates it.

    def test_14_null_fk_and_orphan_line_statuses_count_differently(self):
        result = grouped(run86(lines=[(1,None,101,1),(2,999,101,1)],
                               products=[(101,20)]))
        self.assertEqual(result["Lines with NULL OrderID"][1:5],
                         (0,Decimal("0"),Decimal("20"),Decimal("20")))
        self.assertEqual(result["Lines without header"][1:5],
                         (1,Decimal("0"),Decimal("20"),Decimal("20")))

    def test_15_header_without_lines_and_negative_header(self):
        result = grouped(run86(headers=[(1,10,20),(2,10,-5),(3,10,0)],
                               lines=[(2,2,101,1),(3,3,101,1)],
                               products=[(101,20)],payments=[(10,"Card")]))
        self.assertEqual(result["Header without lines"][1],1)
        self.assertEqual(result["Header without lines"][4],Decimal("20"))
        self.assertEqual(result["Header zero or NULL"][1],2)
        self.assertEqual(result["Header zero or NULL"][4],Decimal("45"))

    def test_16_other_shortfall_header_above_and_unknown_product(self):
        result = grouped(run86(headers=[(1,10,16),(2,10,25),(3,10,20)],
                               lines=[(1,1,101,1),(2,2,101,1),(3,3,999,1)],
                               products=[(101,20)], payments=[(10,"Card")]))
        self.assertEqual(result["Other shortfall"][1],1)
        self.assertEqual(result["Header above lines"][1],2)
        # Missing Products match converts unknown line value to zero via COALESCE.


if __name__ == "__main__":
    unittest.main(verbosity=2)
