#!/usr/bin/env python3
"""Read-only source-pinned historical Q25 and pending Q26 Chinook SQL audit.

Q26 SQL is auditor-authored, NEVER a learner or official solution.
Fixture rows are disposable SQLite examples, not the original Chinook database.
"""
import hashlib
import re
import sqlite3
import unittest
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    '99. Reference Materials/Original Mastery Snapshot/'
    '1. SQL Mastery/1. SQL Mastry/'
    '1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy'
)
PINS = {
    25: ('25.Monthly revenue across the full history.md', 'f7f63f95b9d7ee390061f6d19477ee5e63b57e65'),
    26: ('26.2024 revenue, month by month, running.md', 'f9bf9cd89d177f42d31f812acb20f918c53bede6'),
}

def source(n):
    name, pin = PINS[n]
    raw = (BASE / name).read_bytes()
    actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert actual == pin, (name, 'original blob identity changed', actual, pin)
    return raw.decode('utf-8')

def archived_q25_sql():
    document = source(25)
    section = re.search(r'^## My solution — SQLite\s*\n(.*?)(?=^## |\Z)', document, re.M | re.S)
    assert section, 'missing archived Q25 learner SQL section'
    sql = re.search(r'```sql\s*\n(.*?)\n```', section.group(1), re.S)
    assert sql, 'missing archived Q25 SQLite query'
    return sql.group(1).strip()

# Explicit reviewer policy: 12 calendar months, zero fill, sum unrounded before YTD round.
# No SQL solution exists in original archived Q26; do NOT credit official/learner answer.
Q26_REVIEWER_SQL = """
WITH RECURSIVE months(Month) AS (
  SELECT '2024-01'
  UNION ALL
  SELECT strftime('%Y-%m', Month || '-01', '+1 month')
  FROM months WHERE Month < '2024-12'
), monthly AS (
  SELECT strftime('%Y-%m', InvoiceDate) AS Month, SUM(Total) AS Amount
  FROM Invoice
  WHERE InvoiceDate >= '2024-01-01' AND InvoiceDate < '2025-01-01'
  GROUP BY strftime('%Y-%m', InvoiceDate)
), calendar_totals AS (
  SELECT months.Month, COALESCE(monthly.Amount, 0.0) AS Amount
  FROM months LEFT JOIN monthly ON months.Month = monthly.Month
)
SELECT Month, ROUND(Amount, 2) AS Revenue,
  ROUND(SUM(Amount) OVER (
    ORDER BY Month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ), 2) AS CumulativeRevenue
FROM calendar_totals ORDER BY Month
"""

def fixture(rows):
    con = sqlite3.connect(':memory:')
    con.execute('CREATE TABLE Invoice (InvoiceId INTEGER, InvoiceDate TEXT, Total REAL)')
    con.executemany('INSERT INTO Invoice VALUES (?,?,?)', rows)
    return con

def review(rows):
    con = fixture(rows)
    try:
        return con.execute(Q26_REVIEWER_SQL).fetchall()
    finally:
        con.close()

def oracle(rows):
    """Independent invoice-level Decimal oracle for ordinary ISO timestamps."""
    amounts = {f'2024-{m:02d}': Decimal('0') for m in range(1, 13)}
    for _, stamp, total in rows:
        if stamp is None or total is None:
            continue
        day = datetime.fromisoformat(stamp)
        if day.year == 2024:
            amounts[day.strftime('%Y-%m')] += Decimal(str(total))
    accumulated = Decimal('0')
    expected = []
    for month, amount in amounts.items():
        accumulated += amount
        expected.append((month, amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                         accumulated.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)))
    return expected

class HistoricalQ25AndPendingQ26(unittest.TestCase):
    def assert_money_rows(self, got, expected):
        self.assertEqual(len(got), len(expected))
        for (m, a, c), (em, ea, ec) in zip(got, expected):
            self.assertEqual(m, em)
            self.assertAlmostEqual(a, float(ea), places=2)
            self.assertAlmostEqual(c, float(ec), places=2)

    def test_01_exact_original_blobs_and_evidence_tiers(self):
        prior, pending = source(25), source(26)
        self.assertIn('Solved (recorded): 2026-10-15', prior)
        self.assertTrue(archived_q25_sql().lower().startswith('select'))
        self.assertIn('NOT SOLVED YET', pending)
        self.assertIn('Expected output: `Month`, `Revenue`, `CumulativeRevenue` — 12 rows', pending)
        self.assertIn('The question image was supplied in the conversation but is not available', pending)
        self.assertIn('## My solution — SQLite\n\nPending', pending)
        self.assertIn('## My solution — SQL Server\n\nPending', pending)
        self.assertIn('## Official solution\n\nPending', pending)

    def test_02_saved_q25_sql_on_original_six_row_teaching_example(self):
        rows = [(1,'2023-01-10 10:00:00',10.25),(2,'2023-01-28 12:00:00',20.1),
                (3,'2023-02-05 09:00:00',5.0),(4,'2024-01-01 08:00:00',7.5),
                (5,'2024-01-20 14:00:00',2.5),(6,'2024-02-08 17:00:00',8.25)]
        con = fixture(rows)
        try:
            self.assertEqual(con.execute(archived_q25_sql()).fetchall(),
                             [('2023-01',30.35),('2023-02',5.0),('2024-01',10.0),('2024-02',8.25)])
        finally:
            con.close()
        self.assert_money_rows(review(rows), oracle(rows))

    def test_03_full_twelve_months_and_independent_decimal_oracle(self):
        rows = [(m,f'2024-{m:02d}-15 10:00:00',float(m)) for m in range(1,13)]
        self.assert_money_rows(review(rows), oracle(rows))
        self.assertEqual(review(rows)[-1], ('2024-12',12.0,78.0))

    def test_04_no_invoice_still_twelve_rows_under_reviewer_calendar_policy(self):
        self.assert_money_rows(review([]), oracle([]))
        self.assertEqual(review([])[-1], ('2024-12',0.0,0.0))
        con = fixture([])
        try:
            self.assertEqual(con.execute(archived_q25_sql()).fetchall(), [])
        finally:
            con.close()

    def test_05_absent_months_are_zero_filled_and_ytd_carried_forward(self):
        rows = [(1,'2024-01-12',5.5),(2,'2024-04-21',7.25)]
        self.assert_money_rows(review(rows), oracle(rows))
        got = review(rows)
        self.assertEqual(got[1], ('2024-02',0.0,5.5))
        self.assertEqual(got[3], ('2024-04',7.25,12.75))
        self.assertEqual(got[-1], ('2024-12',0.0,12.75))

    def test_06_half_open_year_boundaries_and_leap_day(self):
        rows = [(1,'2023-12-31 23:59:59',500),(2,'2024-01-01 00:00:00',1),
                (3,'2024-02-29 23:59:59',2),(4,'2024-12-31 23:59:59',3),
                (5,'2025-01-01 00:00:00',900)]
        self.assert_money_rows(review(rows), oracle(rows))
        self.assertEqual(review(rows)[-1], ('2024-12',3.0,6.0))

    def test_07_null_totals_and_missing_invoice_date(self):
        rows = [(1,'2024-01-02',None),(2,'2024-02-02',4),
                (3,'2024-02-03',None),(4,None,100)]
        self.assert_money_rows(review(rows), oracle(rows))
        self.assertEqual(review(rows)[0], ('2024-01',0.0,0.0))

    def test_08_rounding_per_month_differs_from_unrounded_ytd(self):
        rows = [(1,'2024-01-10',0.004),(2,'2024-02-10',0.004),
                (3,'2024-03-10',0.004)]
        got = review(rows)
        self.assert_money_rows(got, oracle(rows))
        self.assertEqual([r[1] for r in got[:3]], [0.0,0.0,0.0])
        self.assertEqual(got[2][2],0.01)
        self.assertNotEqual(got[2][2],round(sum(r[1] for r in got[:3]),2))

    def test_09_malformed_year_strings_silently_drop_calendar_join_amounts(self):
        rows = [(1,'2024-01-10',8),(2,'2024-13-01',50),
                (3,'2024-not-a-date',70)]
        self.assertEqual(review(rows)[-1], ('2024-12',0.0,8.0))
        con = fixture(rows)
        try:
            dropped = con.execute("""SELECT COUNT(*), SUM(Total) FROM Invoice
              WHERE InvoiceDate >= '2024-01-01' AND InvoiceDate < '2025-01-01'
              AND strftime('%Y-%m', InvoiceDate) IS NULL""").fetchone()
            self.assertEqual(dropped, (2,120.0))
        finally:
            con.close()

    def test_10_q25_saved_monthlies_match_q26_reviewer_monthlies_on_complete_year(self):
        rows = [(m,f'2024-{m:02d}-09',m*2.0) for m in range(1,13)]
        con = fixture(rows)
        try:
            q25 = con.execute(archived_q25_sql()).fetchall()
        finally:
            con.close()
        got = review(rows)
        self.assertEqual([(r[0],r[1]) for r in got],q25)
        self.assert_money_rows(got,oracle(rows))

if __name__ == '__main__':
    unittest.main(verbosity=2)
