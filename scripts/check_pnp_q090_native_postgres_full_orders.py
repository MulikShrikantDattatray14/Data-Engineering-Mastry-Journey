#!/usr/bin/env python3
"""Independent original PNP Q090 supplier-key replay on all Commerce v2 Orders.

All SQL executes unchanged against transaction-scoped PostgreSQL 16 TEMP data.
Python reference independently calculates each null/distinct/recent ratio, using
the original loader's declared types and date interpretation. Source archives,
historical learner work and provider key are read only. No learner grades.
"""
import csv
import hashlib
import os
import re
import unittest
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SRC = BASE / "Source Materials/PrepNPlaced_SQL_100_v2"
QUESTION = BASE / ("14. Data Quality and Deduplication/"
                   "P090. Column-by-column completeness profile of Orders.md")
KEY = SRC / "sql/all_100_solutions.sql"
LOADER = SRC / "data/load_dataset_v2.sql"
CSV = SRC / "data/Orders.csv"
PINS = {
    QUESTION: "1fa536155bfc0115c796ae7c740d0b23dff851f7",
    KEY: "7912c8e676621c513e0b635a40c6ee299404676e",
    LOADER: "3787743252d29268c67c491d6a2eb47c1757c35b",
    CSV: "307acc9ad2f85a79d7637a7958ffd62f2a8fa594",
}
COLUMNS = ("OrderID", "CustomerID", "PaymentID", "OrderDate", "ShipperID",
           "Total_Order_Amount", "ShipDate", "DeliveryDate")
DATES = {"OrderDate", "ShipDate", "DeliveryDate"}
INTS = {"OrderID", "CustomerID", "PaymentID", "ShipperID"}
DDL = """CREATE TEMP TABLE Orders (
 OrderID integer PRIMARY KEY, CustomerID integer, PaymentID integer,
 OrderDate date, ShipperID integer, Total_Order_Amount numeric(12,2),
 ShipDate date, DeliveryDate date) ON COMMIT DROP"""


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def key_sql():
    source = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q90\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
    assert match, "Source Q090 SQL section absent"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS (") and sql.endswith(";"), "Unexpected Q090 key format"
    for term in ("CROSS JOIN LATERAL", "COUNT(DISTINCT u.column_value)",
                 "o.OrderDate > a.max_order_date - 30", "ORDER BY u.column_position"):
        assert term in sql, term
    for i, column in enumerate(COLUMNS, 1):
        assert f"({i}, '{column}'" in sql, column
    return sql


def cast(raw, column):
    if raw in ("", None):
        return None
    if column in DATES:
        return datetime.strptime(raw, "%d-%m-%Y").date()
    if column in INTS:
        return int(raw)
    return Decimal(raw)


def original_rows():
    assert blob(CSV) == PINS[CSV], "original Orders.csv changed"
    with CSV.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        assert tuple(reader.fieldnames) == COLUMNS, reader.fieldnames
        rows = [tuple(cast(r[c], c) for c in COLUMNS) for r in reader]
    assert len(rows) == 46438, len(rows)
    assert len({r[0] for r in rows}) == len(rows), "Original OrderID not unique"
    return rows


def connect():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "audit"),
        user=os.environ.get("PGUSER", "audit"),
        password=os.environ.get("PGPASSWORD", "audit"),
        autocommit=True)


def run_native(rows):
    with connect() as conn, conn.transaction():
        conn.execute(DDL)
        if rows:
            with conn.cursor() as cur:
                with cur.copy("COPY Orders (" + ", ".join(COLUMNS) +
                              ") FROM STDIN") as out:
                    for row in rows:
                        out.write_row(row)
        # Crucial: exact original supplier query: no fixes, translations or extra WHERE.
        return conn.execute(key_sql()).fetchall()


def percentage(numerator, denominator):
    if not denominator:
        return None
    return (Decimal(100) * Decimal(numerator) /
            Decimal(denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def independent_reference(rows):
    if not rows:
        return []  # Observed supplied SQL; NOT the task's eight-row empty-input contract.
    max_date = max((r[3] for r in rows if r[3] is not None), default=None)
    recent = [r for r in rows if max_date is not None and
              r[3] is not None and r[3] > max_date - timedelta(days=30)]
    output = []
    for i, name in enumerate(COLUMNS):
        values = [r[i] for r in rows]
        nulls = sum(v is None for v in values)
        recent_nulls = sum(r[i] is None for r in recent)
        distinct = len({v for v in values if v is not None})
        output.append((name, len(rows), nulls, percentage(nulls, len(rows)),
                       percentage(recent_nulls, len(recent)), distinct))
    return output


class Q090FullOriginalOrdersAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, sha in PINS.items():
            assert blob(path) == sha, "Source blob drift: " + str(path)
        original = QUESTION.read_text(encoding="utf-8")
        for phrase in ("# PNP Q090.", "NOT SOLVED YET", "## Schema",
                       "## Official solution\n\nPending",
                       "### Sample input and expected output"):
            assert phrase in original, phrase
        loader = LOADER.read_text(encoding="utf-8")
        for term in ("Total_Order_Amount NUMERIC(12,2)",
                     "TO_DATE(NULLIF(orderdate, ''), 'DD-MM-YYYY')",
                     "TO_DATE(NULLIF(shipdate, ''), 'DD-MM-YYYY')",
                     "TO_DATE(NULLIF(deliverydate, ''), 'DD-MM-YYYY')"):
            assert term in loader, term
        cls.full_rows = original_rows()

    def test_01_original_source_hashes_and_pending_state(self):
        self.assertEqual(len(PINS), 4)
        self.assertEqual(len(COLUMNS), 8)
        self.assertEqual(len(self.full_rows), 46438)

    def test_02_native_postgresql_16_engine(self):
        with connect() as conn:
            version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= version < 170000, version)

    def test_03_original_two_order_illustration(self):
        rows = [
            (1, 10, None, datetime(2026,1,1).date(), 30, Decimal("100"),
             datetime(2026,1,2).date(), datetime(2026,1,4).date()),
            (2, 10, 20, datetime(2026,1,31).date(), None, Decimal("200"), None, None)]
        got = run_native(rows)
        self.assertEqual(got, independent_reference(rows))
        self.assertEqual(got[2], ("PaymentID",2,1,Decimal("50.00"),Decimal("0.00"),1))
        self.assertEqual(got[6], ("ShipDate",2,1,Decimal("50.00"),Decimal("100.00"),1))

    def test_04_full_original_csv_exact_eight_column_results(self):
        expected = independent_reference(self.full_rows)
        actual = run_native(self.full_rows)
        self.assertEqual(len(actual), 8)
        self.assertEqual([r[0] for r in actual], list(COLUMNS))
        self.assertEqual(actual, expected)
        print("Q090 full 46,438-row immutable Orders.csv: all eight exact columns PASS")
        for row in actual:
            print("SOURCE_AGGREGATE", row[0], "total",row[1], "nulls",row[2],
                  "overall_pct",row[3], "recent_pct",row[4], "distinct",row[5])

    def test_05_full_original_30_day_anchor_independently_checked(self):
        dates = [r[3] for r in self.full_rows if r[3] is not None]
        anchor = max(dates)
        selected = [d for d in dates if d > anchor - timedelta(days=30)]
        self.assertGreater(len(selected), 0)
        self.assertTrue(all(d <= anchor for d in selected))
        self.assertTrue(all(d > anchor-timedelta(days=30) for d in selected))
        self.assertEqual(run_native(self.full_rows), independent_reference(self.full_rows))
        print("Q090 full source recent window: anchor",anchor,"recent dated orders",len(selected),
              "date-null orders",len(self.full_rows)-len(dates))

    def test_06_tie_date_boundary_and_null_values(self):
        rows = [
            (1,10,None,datetime(2026,1,1).date(),None,None,None,None),
            (2,10,20,datetime(2026,1,2).date(),None,Decimal("1.00"),None,None),
            (3,None,20,datetime(2026,1,31).date(),2,Decimal("1.0"),None,None),
            (4,None,None,None,2,Decimal("-5.00"),None,None)]
        got = run_native(rows)
        self.assertEqual(got, independent_reference(rows))
        self.assertEqual(got[5][-1],2)  # 1.00 / 1.0 collapse to one numeric DISTINCT
        self.assertEqual(got[2][4],Decimal("0.00"))

    def test_07_null_only_date_anchor_undefined_recent_ratio(self):
        rows = [(1,None,None,None,None,None,None,None)]
        got = run_native(rows)
        self.assertEqual(got,independent_reference(rows))
        self.assertTrue(all(r[4] is None for r in got))

    def test_08_known_empty_orders_contract_gap(self):
        actual=run_native([])
        self.assertEqual(actual,[])
        self.assertNotEqual(len(actual),8)
        print("KNOWN Q090 CONTRACT GAP: empty source returns zero rows; one per eight columns requested")

    def test_09_historical_learner_and_official_pending_not_promoted(self):
        content=QUESTION.read_text(encoding="utf-8")
        self.assertIn("## My solution — SQLite\n\nPending.",content)
        self.assertIn("## My solution — SQL Server\n\nPending.",content)
        self.assertIn("## Official solution\n\nPending",content)


if __name__=="__main__":
    unittest.main(verbosity=2)
