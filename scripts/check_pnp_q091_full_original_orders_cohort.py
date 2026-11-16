#!/usr/bin/env python3
"""Auditor-only PNP Q091 native PostgreSQL 16 / complete immutable Orders.csv differential.

Execute supplier-attributed SQL unchanged on transaction-local scratch tables.
Independently calculate the same explicit quarter-end maturity *key policy* in
Python, and separately assert the source's illustrative output contradiction.
No official grading, archived student completions, or mastery is inferred.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import unittest
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / "Source Materials/PrepNPlaced_SQL_100_v2"
QUESTION = BASE / ("12. Dates and Time/"
                   "P091. Cumulative value per customer by cohort (LTV curve).md")
KEY = SOURCE / "sql/all_100_solutions.sql"
LOADER = SOURCE / "data/load_dataset_v2.sql"
ORDERS = SOURCE / "data/Orders.csv"
PINS = {
    QUESTION: "cf11e56982938b3227f711e00534237f88d451aa",
    KEY: "7912c8e676621c513e0b635a40c6ee299404676e",
    LOADER: "3787743252d29268c67c491d6a2eb47c1757c35b",
    ORDERS: "307acc9ad2f85a79d7637a7958ffd62f2a8fa594",
}
COLS = ("OrderID", "CustomerID", "PaymentID", "OrderDate", "ShipperID",
        "Total_Order_Amount", "ShipDate", "DeliveryDate")
DDL = """CREATE TEMP TABLE Orders (
    OrderID integer PRIMARY KEY, CustomerID integer,
    OrderDate date, Total_Order_Amount numeric(12,2)
) ON COMMIT DROP"""


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def source_sql() -> str:
    text = KEY.read_text(encoding="utf-8-sig")
    match = re.search(r"(?ms)^-- Q91\. [^\n]*\n(.*?)(?=^-- Q92\.|\Z)", text)
    assert match, "Q091 original supplier SQL marker not found"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS") and sql.endswith(";"), "key source section drift"
    for token in ("DATE_TRUNC('quarter', fo.first_month)",
                  "generate_series(0, 12)", "fo.CustomerID = o.CustomerID",
                  "WHERE oo.month_offset <= 12",
                  "s.cohort_quarter + INTERVAL '2 months'",
                  "ORDER BY cv.cohort_quarter"):
        assert token in sql, token
    return sql


def source_rows() -> list[tuple[int, int | None, date | None, Decimal | None]]:
    with ORDERS.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        assert tuple(reader.fieldnames) == COLS, "Orders.csv header mismatch"
        rows = []
        for r in reader:
            rows.append((
                int(r["OrderID"]),
                int(r["CustomerID"]) if r["CustomerID"] else None,
                datetime.strptime(r["OrderDate"], "%d-%m-%Y").date()
                if r["OrderDate"] else None,
                Decimal(r["Total_Order_Amount"]) if r["Total_Order_Amount"] else None,
            ))
    assert len(rows) == 46438, "original order population drift"
    assert len({r[0] for r in rows}) == len(rows), "duplicate OrderID"
    return rows


def conn():
    return psycopg.connect(host=os.getenv("PGHOST", "127.0.0.1"),
                           port=os.getenv("PGPORT", "5432"),
                           dbname=os.getenv("PGDATABASE", "audit"),
                           user=os.getenv("PGUSER", "audit"),
                           password=os.getenv("PGPASSWORD", "audit"),
                           autocommit=True)


def native(rows: list[tuple]) -> list[tuple]:
    with conn() as db, db.transaction():
        db.execute(DDL)
        if rows:
            with db.cursor() as cursor:
                with cursor.copy("COPY Orders (OrderID, CustomerID, OrderDate, Total_Order_Amount) FROM STDIN") as out:
                    for row in rows:
                        out.write_row(row)
        return db.execute(source_sql()).fetchall()


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def plus_months(d: date, months: int) -> date:
    assert d.day == 1
    index = d.year * 12 + d.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def quarter_start(d: date) -> date:
    return date(d.year, ((d.month - 1) // 3) * 3 + 1, 1)


def independent_key_policy(rows: list[tuple]) -> list[tuple]:
    """Independent date/Decimal aggregation oracle for the *source-key policy*.

    This deliberately does not bless the supplied key as the intended answer:
    source sample maturity has separately documented contradictory cells.
    """
    dated = [r[2] for r in rows if r[2] is not None]
    if not dated:
        return []
    latest = max(dated)
    # Source DATE_TRUNC('month', MAX(OrderDate)+1) - INTERVAL '1 month':
    # latest calendar month counts only if the last observed day is its final day.
    last_full = month_start(latest) if (latest + timedelta(days=1)).month != latest.month else plus_months(month_start(latest), -1)

    first: dict[int, date] = {}
    for _oid, customer, day, _value in rows:
        if customer is None or day is None:
            continue
        if customer not in first or day < first[customer]:
            first[customer] = day
    counts = defaultdict(int)
    for day in first.values():
        counts[quarter_start(day)] += 1

    buckets = defaultdict(lambda: Decimal("0"))
    for _oid, customer, day, value in rows:
        if customer not in first or day is None or value is None:
            continue
        f = month_start(first[customer])
        offset = (day.year - f.year) * 12 + day.month - f.month
        if 0 <= offset <= 12:
            buckets[(quarter_start(f), offset)] += value

    result = []
    for cohort in sorted(counts):
        cumulative = Decimal("0")
        values = {}
        for offset in range(13):
            cumulative += buckets[(cohort, offset)]
            maturity = plus_months(cohort, 2 + offset) <= last_full
            if offset in (0, 3, 6, 12):
                values[offset] = (
                    (cumulative / Decimal(counts[cohort])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP)
                    if maturity else None
                )
        result.append((cohort, counts[cohort], *(values[o] for o in (0, 3, 6, 12))))
    return result


class Q091FullCommerceCohortReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, expected in PINS.items():
            assert blob_sha(path) == expected, ("immutable source drift", path)
        question = QUESTION.read_text(encoding="utf-8-sig")
        for text in ("# PNP Q091.", "NOT SOLVED YET",
                     "2025-01-05", "2026-01-31", "cohort has not yet",
                     "## My solution — SQLite\n\nPending",
                     "## Official solution\n\nPending"):
            assert text in question, ("source status/task drift", text)
        loader = LOADER.read_text(encoding="utf-8")
        for text in ("Total_Order_Amount NUMERIC(12,2)",
                     "TO_DATE(NULLIF(orderdate, ''), 'DD-MM-YYYY')"):
            assert text in loader, text
        cls.rows = source_rows()

    def test_01_original_source_identity_and_history_still_pending(self):
        self.assertEqual(len(PINS), 4)
        self.assertEqual(len(self.rows), 46438)

    def test_02_real_native_postgresql_16(self):
        with conn() as db:
            version = int(db.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= version < 170000, version)

    def test_03_original_four_row_source_illustration_conflict_reproduced(self):
        sample = [
            (1, 10, date(2025,1,5), Decimal("100")),
            (2, 10, date(2025,4,5), Decimal("50")),
            (3, 10, date(2026,1,31), Decimal("50")),
            (4, 20, date(2026,1,10), Decimal("80")),
        ]
        got = native(sample)
        self.assertEqual(got, independent_key_policy(sample))
        self.assertEqual(got, [
            (date(2025,1,1),1,Decimal("100"),Decimal("150"),Decimal("150"),None),
            (date(2026,1,1),1,None,None,None,None)])
        source_expected = [
            (date(2025,1,1),1,Decimal("100"),Decimal("150"),Decimal("150"),Decimal("200")),
            (date(2026,1,1),1,Decimal("80"),None,None,None)]
        differences = [(i,j) for i in range(2) for j in range(6)
                       if got[i][j] != source_expected[i][j]]
        self.assertEqual(differences, [(0,5),(1,2)])
        print("SOURCE CONTRACT CONFLICT: exactly two original example cells disagree with supplier SQL")

    def test_04_entire_original_46438_order_differential(self):
        actual = native(self.rows)
        expected = independent_key_policy(self.rows)
        self.assertEqual(actual, expected)
        self.assertGreater(len(actual), 1)
        self.assertEqual(sum(r[1] for r in actual),
                         len({r[1] for r in self.rows if r[1] is not None and r[2] is not None}))
        self.assertTrue(all(row[0].month in (1,4,7,10) for row in actual))
        print("SOURCE DATA MATCH: 46438 original orders, cohort rows",len(actual),
              "cohort customers",sum(r[1] for r in actual),
              "first cohort",actual[0][0],"last cohort",actual[-1][0])
        for row in actual:
            print("COHORT_AGGREGATE",row)

    def test_05_original_last_observed_month_not_automatically_complete(self):
        latest = max(r[2] for r in self.rows if r[2] is not None)
        self.assertEqual(latest, date(2025,12,28))
        last_full = plus_months(month_start(latest),-1)
        self.assertEqual(last_full,date(2025,11,1))
        actual = native(self.rows)
        self.assertEqual(actual,independent_key_policy(self.rows))
        latest_cohort = actual[-1]
        if latest_cohort[0] == date(2025,10,1):
            self.assertTrue(all(val is None for val in latest_cohort[2:]))
        print("MATURITY CAVEAT: max date",latest,"=> supplier last-full-month",last_full)

    def test_06_last_day_of_month_changes_maturity_not_sample_credit(self):
        early = [(1,10,date(2025,1,5),Decimal("100")),
                 (2,20,date(2026,3,15),Decimal("20"))]
        full = [(1,10,date(2025,1,5),Decimal("100")),
                (2,20,date(2026,3,31),Decimal("20"))]
        for data in (early,full):
            self.assertEqual(native(data),independent_key_policy(data))
        self.assertIsNone(native(early)[0][-1])
        self.assertEqual(native(full)[0][-1],Decimal("100.00"))

    def test_07_multiple_orders_same_month_signed_amounts_decimal_rounding(self):
        sample = [
            (1,11,date(2024,1,4),Decimal("10.01")),
            (2,11,date(2024,1,5),Decimal("-2.00")),
            (3,12,date(2024,2,1),Decimal("9.00")),
            (4,12,date(2024,2,8),Decimal("1.00")),
            (5,12,date(2025,6,30),Decimal("0.00"))]
        self.assertEqual(native(sample),independent_key_policy(sample))
        self.assertEqual(native(sample)[0][2],Decimal("9.01"))

    def test_08_null_amount_null_customer_null_date_and_empty_input(self):
        sample=[
            (1,11,date(2024,1,5),None),
            (2,11,date(2024,2,5),Decimal("7")),
            (3,None,date(2025,12,31),Decimal("200")),
            (4,12,None,Decimal("400")),
            (5,11,None,Decimal("300"))]
        self.assertEqual(native(sample),independent_key_policy(sample))
        self.assertEqual(native([]),[])
        self.assertEqual(independent_key_policy([]),[])

    def test_09_no_provider_grade_or_learner_solution_inferred(self):
        question = QUESTION.read_text(encoding="utf-8-sig")
        self.assertIn("## My solution — SQL Server\n\nPending",question)
        self.assertIn("## Official solution\n\nPending",question)


if __name__ == "__main__":
    unittest.main(verbosity=2)
